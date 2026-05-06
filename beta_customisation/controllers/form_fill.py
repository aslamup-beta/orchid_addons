# -*- coding: utf-8 -*-
import base64

from openerp import SUPERUSER_ID
from openerp import http
from openerp.tools.translate import _
from openerp.http import request
from openerp.addons.website.models.website import slug
from openerp import api

class BetaJoin(http.Controller):
    @http.route('/beta_join/<model("od.beta.joining.form"):join_id>', type='http', auth="public", website=True)
    def beta_join_form(self, join_id):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        orm_country = registry.get('res.country')
        orm_state = registry.get('res.country.state')
        country_ids = orm_country.search(cr, SUPERUSER_ID, [], context=context)
        countries = orm_country.browse(cr, SUPERUSER_ID, country_ids, context)
        state_ids = orm_state.search(cr, SUPERUSER_ID, [], context=context)
        states = orm_state.browse(cr, SUPERUSER_ID, state_ids, context)
        
        error = {}
        default = {}
        if 'website_hr_recruitment_error' in request.session:
            error = request.session.pop('consyshr_error')
            default = request.session.pop('consyshr_default')
        return request.render("beta_customisation.employee_join_form", {
            'joinee': join_id,
            'error':error,
            'default':default,
            'countries': countries,
            'states': states
        
        })

    @http.route('/beta_join/thankyou', methods=['POST'], type='http', auth="public", website=True)
    def jobs_thankyou(self, **post):
        error = {}
        for field_name in ["name"]:
            if not post.get(field_name):
                error[field_name] = 'missing'

        env = request.env(user=SUPERUSER_ID)
        value = {
        }
        for f in ['name', 'dob','age','gender', 'passport_no', 'place_of_birth', 'martial', 'mobile', 'nationality', 'mobile', 
                  'street', 'street2','city', 'zip','state_id','country_id',
                  'e_c1_name','e_c1_relationship', 'e_c1_street','e_c1_street2','e_c1_city', 'e_c1_state_id', 'e_c1_country_id', 'e_c1_ph1','e_c1_ph2']:
            value[f] = post.get(f)
        for f in ['join_id']:
            join_id = int(post.get(f) or False)
            emp_join_form_rec = env['od.beta.joining.form'].browse(join_id)
        # Retro-compatibility for saas-3. "phone" field should be replace by "partner_phone" in the template in trunk.
#         value['partner_phone'] = post.pop('phone', False)

        emp_join_id = emp_join_form_rec.write(value)
        if emp_join_form_rec.company_id.id == 6:
            local = 7
        else:
            local = 5
        
        if post['image']:    
            emp_join_form_rec.write({'image': base64.encodestring(post['image'].read())})
        
        emp_join_form_rec.document_line_ids.unlink()
        if post['passport']:
            attachment_value = {
                'document_type_id': 2,
                'joining_id': join_id,
                'attach_file': base64.encodestring(post['passport'].read()),
                'attach_fname': post['passport'].filename,
            }
            
            env['od.hr.employee.document.line'].create(attachment_value)
        
        if post['education']:
            attachment_value = {
                'document_type_id': 4,
                'joining_id': join_id,
                'attach_file': base64.encodestring(post['education'].read()),
                'attach_fname': post['education'].filename,
            }
            env['od.hr.employee.document.line'].create(attachment_value)
        if post['local_id']:
            attachment_value = {
                'document_type_id': local,
                'joining_id': join_id,
                'attach_file': base64.encodestring(post['local_id'].read()),
                'attach_fname': post['local_id'].filename,
            }
            env['od.hr.employee.document.line'].create(attachment_value)
        emp_join_form_rec.send_to_finance()
        return request.render("beta_customisation.beta_thankyou", {})

# vim :et:
