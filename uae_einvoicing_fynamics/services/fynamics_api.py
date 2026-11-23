# -*- coding: utf-8 -*-
"""Fynamics API client: authenticate, submit invoice, get document status.

`branch` is the od.cost.branch record that holds the fynamics_* settings.
"""
import base64
import json
import os
from datetime import datetime, timedelta

import requests

from openerp import fields
from openerp.exceptions import Warning

# Trusted certificate list. Old versions of `requests` carry an outdated built-in list,
# so we point it at the system list (Ubuntu). If the file is missing, use the default.
CA_BUNDLE = '/etc/ssl/certs/ca-certificates.crt'
if not os.path.exists(CA_BUNDLE):
    CA_BUNDLE = True


class FynamicsAPI(object):

    def __init__(self, branch):
        self.branch = branch

    # ------------------------------------------------------------ helpers
    def _url(self, path):
        base = (self.branch.fynamics_base_url or '').rstrip('/')
        if not base:
            raise Warning('Fynamics Base URL is not configured.')
        return base + '/' + path.lstrip('/')

    def _log(self, name, url, request_body, response_body, http_status,
             status, invoice=None, uuid=None):
        """Write one line in the API log (secrets are never passed in here)."""
        self.branch.env['fynamics.api.log'].sudo().create({
            'name': name,
            'operation': name,
            'endpoint': url,
            'request_body': request_body,
            'response_body': response_body,
            'http_status': http_status,
            'status': status,
            'error_message': response_body if status == 'error' else False,
            'invoice_id': invoice and invoice.id or False,
            'uuid': uuid,
        })

    @staticmethod
    def _token_expiry(token_data):
        """Expiry as a UTC datetime. Uses accessTokenExpire (Unix seconds) when Fynamics
        sends it, otherwise the "exp" value inside the JWT access token itself."""
        expire = token_data.get('accessTokenExpire')
        if not expire:
            payload = str(token_data['accessToken'].split('.')[1])
            payload += '=' * (-len(payload) % 4)
            expire = json.loads(base64.urlsafe_b64decode(payload))['exp']
        return datetime.utcfromtimestamp(int(expire))

    # ------------------------------------------------------------ authentication
    def authenticate(self, force=False):
        """Return a valid access token. Reuses the saved one until it expires."""
        branch = self.branch
        if not force and branch.fynamics_access_token and branch.fynamics_token_expires_at:
            expires = fields.Datetime.from_string(branch.fynamics_token_expires_at)
            if expires - timedelta(seconds=60) > datetime.utcnow():
                return branch.fynamics_access_token

        if not (branch.fynamics_client_id and branch.fynamics_client_secret):
            raise Warning('Fynamics Client ID / Secret are not configured.')

        url = self._url(branch.fynamics_token_path)
        form = {'grant_type': 'client_credentials'}
        if branch.fynamics_scope:
            form['scope'] = branch.fynamics_scope
        try:
            # requests turns the (id, secret) pair into "Authorization: Basic <base64>"
            r = requests.post(url, data=form, timeout=branch.fynamics_timeout or 60,
                              verify=CA_BUNDLE,
                              auth=(branch.fynamics_client_id, branch.fynamics_client_secret))
        except requests.RequestException as e:
            self._log('authenticate', url, json.dumps(form), str(e), 0, 'error')
            raise Warning('Fynamics authentication connection error: %s' % e)

        try:
            data = r.json()
        except ValueError:
            data = {}
        token_data = data.get('data') or {}
        token = token_data.get('accessToken')
        if r.status_code != 200 or not token:
            self._log('authenticate', url, json.dumps(form), r.text, r.status_code, 'error')
            raise Warning('Fynamics authentication failed (HTTP %s): %s' %
                          (r.status_code, r.text[:500]))

        expires = self._token_expiry(token_data)
        branch.sudo().write({
            'fynamics_access_token': token,
            'fynamics_token_expires_at': fields.Datetime.to_string(expires),
        })
        # the token itself is never stored in the log
        self._log('authenticate', url, json.dumps(form),
                  json.dumps({'success': data.get('success'), 'accessToken': '***'}),
                  200, 'success')
        return token

    # ------------------------------------------------------------ generic call
    def _request(self, name, method, path, invoice=None, retry_auth=True, **kwargs):
        url = self._url(path)
        headers = dict(kwargs.pop('headers', {}))
        headers['Authorization'] = 'Bearer %s' % self.authenticate()
        body = kwargs.get('data')
        try:
            r = requests.request(method, url, headers=headers,
                                 timeout=self.branch.fynamics_timeout or 60,
                                 verify=CA_BUNDLE, **kwargs)
        except requests.RequestException as e:
            self._log(name, url, body, str(e), 0, 'error', invoice)
            raise Warning('Fynamics connection error: %s' % e)

        if r.status_code == 401 and retry_auth:
            # token was rejected: get a new one and try once more
            self.authenticate(force=True)
            return self._request(name, method, path, invoice, False, **kwargs)

        try:
            data = r.json()
        except ValueError:
            data = {}
        ok = 200 <= r.status_code < 300
        self._log(name, url, body, r.text, r.status_code,
                  'success' if ok else 'error', invoice, data.get('uuid'))
        if not ok:
            raise Warning('Fynamics %s failed (HTTP %s): %s' %
                          (name, r.status_code, r.text[:1000]))
        return data

    # ------------------------------------------------------------ business calls
    def submit_invoice_json(self, invoice, payload):
        """POST the invoice JSON. Response: {"uuid": ..., "message": ...}."""
        return self._request('submit_invoice', 'POST', self.branch.fynamics_submit_path,
                             invoice=invoice, data=json.dumps(payload, default=str),
                             headers={'Content-Type': 'application/json'})

    def get_document_status(self, invoice, uuid):
        path = self.branch.fynamics_status_path.replace('{uuid}', uuid)
        return self._request('check_status', 'GET', path, invoice=invoice)