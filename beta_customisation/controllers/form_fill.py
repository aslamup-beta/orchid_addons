# -*- coding: utf-8 -*-
import base64
import logging

from openerp import SUPERUSER_ID
from openerp import http
from openerp.http import request

_logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------
# Each entry: key = form field name, type_id = od.hr.employee.document.type id.
# key == 'image' is the employee photo (stored on the joining form itself).
# !! Fill in every type_id that is None (see your document type records). !!
# Entries with type_id None are skipped (a warning is logged).

SAUDI_COMPANY_ID = 6
FULL_ADDRESS_FIELD = 'short_addr'  # where the single "full address" is stored

SAUDI_DOCS = [
    {'key': 'passport', 'label': 'Passport', 'icon': 'fa-book',
     'hint': 'Clear scan of the photo page', 'required': True, 'type_id': 2},
    {'key': 'iqama', 'label': 'ID / Iqama', 'icon': 'fa-id-card-o',
     'hint': 'Front and back', 'required': True, 'type_id': 7},
    {'key': 'iban', 'label': 'Bank IBAN Certificate', 'icon': 'fa-university',
     'hint': 'Issued by your bank', 'required': True, 'type_id': 41},
    {'key': 'education', 'label': 'Educational Certificates', 'icon': 'fa-graduation-cap',
     'hint': 'Highest qualification', 'required': True, 'type_id': 4},
    {'key': 'national_address', 'label': 'National Address', 'icon': 'fa-map-marker',
     'hint': 'Short address certificate', 'required': True, 'type_id': 42},
    {'key': 'sce', 'label': 'Saudi Council of Engineers Membership', 'icon': 'fa-certificate',
     'hint': 'If applicable', 'required': False, 'type_id': 8},
    {'key': 'eng_cert', 'label': 'Engineering Certificate', 'icon': 'fa-cogs',
     'hint': 'If applicable', 'required': False, 'type_id': 51},
    {'key': 'image', 'label': 'Personal Photo (Passport Size)', 'icon': 'fa-camera',
     'hint': 'Passport-size, less than 30 KB', 'required': True, 'type_id': None,
     'max_kb': 30, 'accept': 'image/*'},
]

# Company 1 and every other company
DEFAULT_DOCS = [
    {'key': 'passport', 'label': 'Upload your Passport Copy', 'icon': 'fa-book',
     'hint': '', 'required': True, 'type_id': 2},
    {'key': 'education', 'label': 'Upload your Educational Certificate', 'icon': 'fa-graduation-cap',
     'hint': '', 'required': True, 'type_id': 4},
    {'key': 'local_id', 'label': 'Local ID (if any)', 'icon': 'fa-id-card-o',
     'hint': 'Optional', 'required': False, 'type_id': 5},
    {'key': 'image', 'label': 'Upload your Photo', 'icon': 'fa-camera',
     'hint': 'Less than 30 KB', 'required': True, 'type_id': None,
     'max_kb': 30, 'accept': 'image/*'},
]

M2O_FIELDS = ['nationality', 'state_id', 'country_id', 'e_c1_state_id', 'e_c1_country_id']
CHAR_FIELDS = ['name', 'dob', 'gender', 'passport_no', 'place_of_birth', 'martial',
               'mobile', 'street', 'street2', 'city', 'zip',
               'e_c1_name', 'e_c1_relationship', 'e_c1_street', 'e_c1_street2',
               'e_c1_city', 'e_c1_ph1', 'e_c1_ph2', 'short_addr']


def get_documents(company_id):
    return SAUDI_DOCS if company_id == SAUDI_COMPANY_ID else DEFAULT_DOCS


def to_int(val):
    try:
        return int(val) or False
    except (TypeError, ValueError):
        return False


def read_upload(storage):
    """Return (data, filename) for a werkzeug FileStorage, or (None, None) if empty."""
    if storage is None or not getattr(storage, 'filename', None):
        return None, None
    data = storage.read()
    if not data:
        return None, None
    return base64.encodestring(data), storage.filename


class BetaJoin(http.Controller):

    @http.route('/beta_join/<model("od.beta.joining.form"):join_id>', type='http',
                auth="public", website=True)
    def beta_join_form(self, join_id):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        orm_country = registry.get('res.country')
        orm_state = registry.get('res.country.state')
        country_ids = orm_country.search(cr, SUPERUSER_ID, [], context=context)
        countries = orm_country.browse(cr, SUPERUSER_ID, country_ids, context)
        state_ids = orm_state.search(cr, SUPERUSER_ID, [], context=context)
        states = orm_state.browse(cr, SUPERUSER_ID, state_ids, context)

        joinee = registry.get('od.beta.joining.form').browse(cr, SUPERUSER_ID, join_id.id, context)
        company_id = joinee.company_id.id

        error = {}
        default = {}
        if 'website_hr_recruitment_error' in request.session:
            error = request.session.pop('consyshr_error')
            default = request.session.pop('consyshr_default')
        return request.render("beta_customisation.employee_join_form", {
            'joinee': join_id,
            'company_id': company_id,
            'is_saudi': company_id == SAUDI_COMPANY_ID,
            'documents': get_documents(company_id),
            'error': error,
            'default': default,
            'countries': countries,
            'states': states,
        })

    @http.route('/beta_join/thankyou', methods=['POST'], type='http', auth="public", website=True)
    def jobs_thankyou(self, **post):
        env = request.env(user=SUPERUSER_ID)
        join_id = to_int(post.get('join_id'))
        rec = env['od.beta.joining.form'].browse(join_id)
        company_id = rec.company_id.id

        value = {}
        for f in CHAR_FIELDS:
            value[f] = post.get(f)
        for f in M2O_FIELDS:
            value[f] = to_int(post.get(f))

        # Company 6: one single full-address field
        if company_id == SAUDI_COMPANY_ID:
            value[FULL_ADDRESS_FIELD] = post.get('full_address')

        rec.write(value)

        # Replace previously uploaded documents
        rec.document_line_ids.unlink()

        for doc in get_documents(company_id):
            data, fname = read_upload(post.get(doc['key']))
            if not data:
                continue
            if doc['key'] == 'image':
                rec.write({'image': data})
                continue
            if not doc.get('type_id'):
                _logger.warning("beta_join: no document type configured for '%s' "
                                "- upload skipped", doc['key'])
                continue
            env['od.hr.employee.document.line'].create({
                'document_type_id': doc['type_id'],
                'joining_id': join_id,
                'attach_file': data,
                'attach_fname': fname,
            })

        rec.send_to_finance()
        return request.render("beta_customisation.beta_thankyou", {})
