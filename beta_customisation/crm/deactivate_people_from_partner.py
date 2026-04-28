# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning
import re

class wiz_remove_contact(models.TransientModel):

    _name = 'wiz.remove.contact.part'
    
    def default_get(self, cr, uid, fields, context=None):
        """
        This function gets default values
        """
        res = super(wiz_remove_contact, self).default_get(cr, uid, fields, context=context)
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
                      'partner_id': contact.id}
            vals.append(values)
        res['partner_id'] = parent_id
        res['wiz_line'] = [(0, 0, x ) for x in vals]
        return res
    
    
#     @api.multi
#     def od_load_contacts(self):
#         context = self.env.context
#         record_id = context and context.get('active_id', False) or False
#         wiz_line = self.env['wiz.remove.contact.part.line']
#         part = self.env['res.partner']
#         parent_id = record_id
#         contact_ids = part.search([('parent_id','=', parent_id)])
#         for part_obj in contact_ids:
#             wiz_line.create({'wiz_id': self.id,
#                                       'name': part_obj.name,
#                                       'od_active': True,
#                                       'partner_id': part_obj.id
#                                       })
#         return {
#                 'context': context,
#                 'view_type': 'form',
#                 'view_mode': 'form',
#                 'res_model': 'wiz.remove.contact.part',
#                 'res_id': self.id,
#                 'view_id': False,
#                 'type': 'ir.actions.act_window',
#                 'target': 'new',
#                 }
    
    def od_get_company_id(self):
        return self.env.user.company_id
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    wiz_line = fields.One2many('wiz.remove.contact.part.line','wiz_id')
    partner_id  = fields.Many2one('res.partner',string="Customer")
             
    @api.one
    def deactivate_contact(self):
        part_obj = self.env['res.partner']
        for line in self.wiz_line:
            if not line.od_active:
                part_rec = part_obj.browse([line.partner_id and line.partner_id.id])    
                part_rec.write({'active':False})
        return True
            
class wiz_remove_contact_line(models.TransientModel):
    _name = 'wiz.remove.contact.part.line'

    wiz_id = fields.Many2one('wiz.remove.contact.part',string="Wizard")
    name = fields.Char(string="Name")
    partner_id  = fields.Many2one('res.partner',string="Customer")
    od_active = fields.Boolean(string="Active")
    
class res_partner(models.Model):
    _inherit ='res.partner'
    
    @api.multi
    def deactivate_people_from_part(self):
        return {
              'name': _('Deactivate People'),
              'view_type': 'form',
              "view_mode": 'form',
              'res_model': 'wiz.remove.contact.part',
              'type': 'ir.actions.act_window',
              'target':'new',
              }
    
