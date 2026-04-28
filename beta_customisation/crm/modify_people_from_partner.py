# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning
import re

class wiz_modify_contact(models.TransientModel):

    _name = 'wiz.modify.contact.part'
    
    def default_get(self, cr, uid, fields, context=None):
        """
        This function gets default values
        """
        res = super(wiz_modify_contact, self).default_get(cr, uid, fields, context=context)
        if context is None:
            context = {}
        part = self.pool.get('res.partner')
        parent_id = context and context.get('active_id', False) or False
        contact_ids = part.search(cr, uid, [('parent_id','=', parent_id)])
        contacts = part.browse(cr, uid, contact_ids)
        vals = []
        for contact in contacts:
            values = {'name': contact.name,
                      'od_active': True,
                      'partner_id': contact.id,
                      'function': contact.function,
                      'email': contact.email,
                      'mobile': contact.mobile,
                      'phone':contact.phone}
            vals.append(values)
        res['partner_id'] = parent_id
        res['wiz_line'] = [(0, 0, x ) for x in vals]
        return res
    
    def od_get_company_id(self):
        return self.env.user.company_id
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    wiz_line = fields.One2many('wiz.modify.contact.part.line','wiz_id',string="Contact details")
    partner_id  = fields.Many2one('res.partner',string="Customer")
             
    @api.one
    def modify_contact(self):
        part_obj = self.env['res.partner']
        for line in self.wiz_line:
            part_rec = part_obj.browse([line.partner_id and line.partner_id.id])    
            part_rec.write({'name':line.name, 
                            'function':line.function, 
                            'email': line.email, 
                            'mobile': line.mobile,
                            'phone':line.phone})
        return True
            
class wiz_modify_contact_line(models.TransientModel):
    _name = 'wiz.modify.contact.part.line'

    wiz_id = fields.Many2one('wiz.modify.contact.part',string="Wizard")
    name = fields.Char(string="Name")
    partner_id  = fields.Many2one('res.partner',string="Customer")
    od_active = fields.Boolean(string="Active")
    function = fields.Char(string="Job Position")
    email = fields.Char(string="Email")
    mobile = fields.Char(string="Mobile")
    phone = fields.Char(string="Phone")
    
class res_partner(models.Model):
    _inherit ='res.partner'
    
    @api.multi
    def modify_people_from_part(self):
        return {
              'name': _('Modify People'),
              'view_type': 'form',
              "view_mode": 'form',
              'res_model': 'wiz.modify.contact.part',
              'type': 'ir.actions.act_window',
              'target':'new',
              }
    
