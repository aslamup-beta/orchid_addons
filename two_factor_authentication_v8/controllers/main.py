# -*- coding: utf-8 -*-
from openerp import http
import logging
_logger = logging.getLogger(__name__)
from openerp.http import request
import werkzeug
#import simplejson
import requests
from openerp.addons.web.controllers.main import  ensure_db #db_monodb, set_cookie_and_redirect, login_and_redirect
#from odoo import registry as registry_get
from openerp import api, http, SUPERUSER_ID, _
import openerp.addons.web.controllers.main as main
import openerp
import hmac, base64, struct, hashlib, time
import ast

class Home(main.Home):
    
    @http.route('/web/login', type='http', auth="none", sitemap=False)
    def web_login(self, redirect=None, **kw):
        ensure_db()
        copy_kw = kw.copy()
        
        request.params['login_success'] = False
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return http.redirect_with_hash(redirect)
        if not request.uid:
            request.uid = openerp.SUPERUSER_ID
        values = request.params.copy()
        try:
            values['databases'] = http.db_list()
        except openerp.exceptions.AccessDenied:
            values['databases'] = None
        if request.httprequest.method == 'POST':
            old_uid = request.uid
            uid = request.session.authenticate(request.session.db, request.params['login'], request.params['password'])
            
            if uid is not False:
                """check if user enable two fector authentication and if yes then redirect 2FA page with credential """
                user = http.request.env['res.users'].sudo().browse(uid)
                if user.is_2fa_enable:
                    request.session.logout(keep_db=True)
                    request.session.update({'temp_data': {'login' : request.params['login'], 'password': request.params['password']}})
                    response = request.render('two_factor_authentication_v8.two_factor_auth',  {'data': copy_kw, 'redirect': redirect})
                    return response                
                else:
                    login_response = super(Home, self).web_login(redirect=None, kw=copy_kw)
                    return login_response
                request.params['login_success'] = True
                if not redirect:
                    redirect = '/web'
                return http.redirect_with_hash(self._login_redirect(uid, redirect=redirect))
            request.uid = old_uid
            values['error'] = _("Wrong login/password")
        response =  request.render('web.login', values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response
    
    
    
    @http.route('/web/login/auth', auth="none", type='http', csrf=False)
    def two_factor_authentication(self, redirect=None, **kw):
        login_data = request.session.get('temp_data')
        uid = False
        if login_data:
            login = login_data.get('login')
            password = login_data.get('password')
#         if not login_data or login or password:
#             return werkzeug.utils.redirect('/web/login')

            uid = request.session.authenticate(request.session.db, login, password)
        if not uid:
            request.session.logout(keep_db=True)
            return http.redirect_with_hash('/web/login')
        
        """ Generate TOTP code using user's secret key"""
        user = http.request.env['res.users'].browse(uid)
        secret_key = user.secret_key.replace(" ", "")
        key = base64.b32decode(secret_key, True)
        msg = struct.pack(">Q", int(time.time())//30)
        
        h = hmac.new(key, msg, hashlib.sha1).digest()
        o = ord(h[19]) & 15
        code = (struct.unpack(">I", h[o:o+4])[0] & 0x7fffffff) % 1000000
        code = str(code)
        #add zero prefix if code is less then 6 digit
        if len(code) < 6:
            code = code.rjust(6, '0')
#             
        copy_kw = kw.copy()
        if str(kw.get('2fa_code')) != code:
#             
#             request.session.logout(keep_db=True)
#             request.session['temp_data'] = False
#             request.session.pop('temp_data' or None)
            request.session.logout(keep_db=True)
            request.session.update({'temp_data': {'login' : login, 'password': password}})
            return request.render('two_factor_authentication_v8.two_factor_auth',  {'data': copy_kw, 'redirect': redirect, 'wrong_code': "Wrong Authentication Code!!!"})
            

        request.session['temp_data'] = False
        request.session.pop('temp_data' or None)
        #TODO: remove temp data from session after 2fa done.

        if not redirect:
            redirect = '/web'
        return http.redirect_with_hash(redirect)
