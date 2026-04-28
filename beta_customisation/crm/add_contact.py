# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning

class wiz_add_contact(models.TransientModel):

    _name = 'wiz.add.contact'
    
    def default_get(self, cr, uid, fields, context=None):
        """
        This function gets default values
        """
        res = super(wiz_add_contact, self).default_get(cr, uid, fields, context=context)
        if context is None:
            context = {}
        record_id = context and context.get('active_id', False) or False
        lead = self.pool.get('crm.lead')
        part = self.pool.get('res.partner')
        lead_obj = lead.browse(cr, uid, [record_id])
        parent_id = lead_obj.partner_id and lead_obj.partner_id.id
        part_obj = part.browse(cr, uid, [parent_id])
        contact_ids = part_obj.search([('parent_id','=', parent_id)])
        contact_list = []
        for line in contact_ids:
            contact_list.append(line.id)
        res['already_added_contacts'] = [[6,0,contact_list]]
        res['partner_id'] = parent_id
        return res
    
    def od_get_company_id(self):
        return self.env.user.company_id
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    wiz_line = fields.One2many('wiz.add.contact.line','wiz_id')
    partner_id  = fields.Many2one('res.partner',string="Customer")
    already_added_contacts = fields.Many2many('res.partner', 'res_partner_contact_rel','contact_id','partner_id','Already Added Contacts')
    
                
    @api.one
    def update_contact(self):
        part_obj = self.env['res.partner']
        for line in self.wiz_line:
            email = line.email
            line.check_email_exists_already(email)
            part_obj.create({'name':line.name,
                         'function':line.function,
                         'phone':line.phone,
                         'mobile':line.mobile,
                        'parent_id': line.partner_id and line.partner_id.id,
                        'email':line.email,
                        'customer':True,
                        'use_parent_address':True,
                        'type':'contact' })
        return True
            
class wiz_add_contact_line(models.TransientModel):
    _name = 'wiz.add.contact.line'
    
    @api.one
    def check_email_exists_already(self,email):
        context = self._context
        active_id = context.get('active_id')
        lead = self.env['crm.lead']
        lead_obj = lead.browse(active_id)
        parent_id = lead_obj.partner_id and lead_obj.partner_id.id
        part_obj = self.env['res.partner']
        contact_ids = part_obj.search([('parent_id','=', parent_id)])
        for contact in contact_ids:
            if contact.email == email:
                raise Warning("A Contact with email id %s already exists"%email)
        return True
    
    wiz_id = fields.Many2one('wiz.add.contact',string="Wizard")
    name = fields.Char(string="Name")
    partner_id  = fields.Many2one('res.partner',string="Customer")
    function = fields.Char(string="Job Position")
    phone = fields.Char(string="Phone")
    mobile = fields.Char(string="Mobile")
    email = fields.Char(string="Email")
    
class wiz_lead_cancel(models.TransientModel):

    _name = 'wiz.mark.lead.cancel'
    
    sm_io1 = fields.Text(string="Why Lost?")
    sm_io2 = fields.Text(string="What we should/shouldn’t do to avoid losing it?")
    
    @api.one
    def send_cancel_req(self):
        context = self._context
        active_id = context.get('active_id')
        lead = self.env['crm.lead']
        lead_obj = lead.browse(active_id)
        lead_obj.write({'od_approval_state': 'request_cancel', 'sm_io1': self.sm_io1, 'sm_io2':self.sm_io2})
        lead_obj.od1_send_mail('crm_cancel_request_email_template')
        
class wiz_lead_lost(models.TransientModel):

    _name = 'wiz.mark.lead.lost'
    
    sm_io1 = fields.Text(string="Why Lost?")
    sm_io2 = fields.Text(string="What we should/shouldn’t do to avoid losing it?")
    
    @api.one
    def send_lost_req(self):
        context = self._context
        active_id = context.get('active_id')
        lead = self.env['crm.lead']
        lead_obj = lead.browse(active_id)
        lead_obj.write({'od_approval_state': 'request_cancel', 'sm_io1': self.sm_io1, 'sm_io2':self.sm_io2})
        lead_obj.od1_send_mail('crm_lost_request_email_template')
        
    
class crm_lead(models.Model):
    _inherit ='crm.lead'
    
    @api.multi
    def add_people_from_lead(self):
        return {
              'name': _('Add People'),
              'view_type': 'form',
              "view_mode": 'form',
              'res_model': 'wiz.add.contact',
              'type': 'ir.actions.act_window',
              'target':'new',
              }
        
    @api.multi
    def request_lead_cancellation(self):
        return {
              'name': _('Mark Cancel'),
              'view_type': 'form',
              "view_mode": 'form',
              'res_model': 'wiz.mark.lead.cancel',
              'type': 'ir.actions.act_window',
              'target':'new',
              }
        
    @api.multi
    def request_mark_lead_lost(self):
        return {
              'name': _('Mark Lost'),
              'view_type': 'form',
              "view_mode": 'form',
              'res_model': 'wiz.mark.lead.lost',
              'type': 'ir.actions.act_window',
              'target':'new',
              }
    
    
    