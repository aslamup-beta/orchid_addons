# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning
import re

class wiz_add_contact(models.TransientModel):

    _name = 'wiz.add.contact.part'
    
    def default_get(self, cr, uid, fields, context=None):
        """
        This function gets default values
        """
        res = super(wiz_add_contact, self).default_get(cr, uid, fields, context=context)
        if context is None:
            context = {}
        record_id = context and context.get('active_id', False) or False
#         lead = self.pool.get('crm.lead')
        part = self.pool.get('res.partner')
#         lead_obj = lead.browse(cr, uid, [record_id])
        parent_id = record_id
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
    wiz_line = fields.One2many('wiz.add.contact.part.line','wiz_id')
    partner_id  = fields.Many2one('res.partner',string="Customer")
    already_added_contacts = fields.Many2many('res.partner', 'res_partner_contact1_rel','contact_id1','partner_id1','Already Added Contacts')
    
                
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
    _name = 'wiz.add.contact.part.line'
    
    @api.one
    def check_email_exists_already(self,email):
        context = self._context
        active_id = context.get('active_id')
#         lead = self.env['crm.lead']
#         lead_obj = lead.browse(active_id)
#         parent_id = lead_obj.partner_id and lead_obj.partner_id.id
        part_obj = self.env['res.partner']
        contact_ids = part_obj.search([('parent_id','=', active_id)])
        for contact in contact_ids:
            if contact.email == email:
                raise Warning("A Contact with email id %s already exists"%email)
        return True
    
    @api.model
    def check_email(self,email,name):
        regex = '^[a-zA-Z0-9]+[\._-]?[a-zA-Z0-9]+[@]\w+[.]\w{2,10}$'
        regex1 = '^[a-zA-Z0-9]+[\._-]?[a-zA-Z0-9]+[@]\w+[\._-]\w+[.]\w{2,10}$'
        regex2 = '^[a-zA-Z0-9]+[\._-]?[a-zA-Z0-9]+[\._-]?[a-zA-Z0-9]+[@]\w+[\._-]\w+[.]\w{2,10}$'
        regex3 = '^[a-zA-Z0-9]+[\._-]?[a-zA-Z0-9]+[\._-]?[a-zA-Z0-9]+[@]\w+[.]\w{2,10}$'
        regex4 = '^[a-zA-Z0-9]+[\._-]?[a-zA-Z0-9]+[\._-]?[a-zA-Z0-9]+[@]\w+[\._-]\w+[\._-]\w+[.]\w{2,10}$'
        if(re.search(regex,email)):
            return True
        elif (re.search(regex1,email)):
            return True
        elif (re.search(regex2,email)):
            return True
        elif (re.search(regex3,email)):
            return True
        elif (re.search(regex4,email)):
            return True
        else:
            raise Warning("Please Enter a valid Email for %s"%name)
        
    @api.onchange('email')
    def onchange_email(self):
        email = self.email
        if email:
            name = self.name
            self.check_email(email,name)
    
    wiz_id = fields.Many2one('wiz.add.contact.part',string="Wizard")
    name = fields.Char(string="Name")
    partner_id  = fields.Many2one('res.partner',string="Customer")
    function = fields.Char(string="Job Position")
    phone = fields.Char(string="Phone")
    mobile = fields.Char(string="Mobile")
    email = fields.Char(string="Email")
    
# class wiz_move_contact(models.TransientModel):
# 
#     _name = 'wiz.move.contact.part'
#     
#     def default_get(self, cr, uid, fields, context=None):
#         """
#         This function gets default values
#         """
#         res = super(wiz_move_contact, self).default_get(cr, uid, fields, context=context)
#         print res,"z"*88
#         print self,"f"*88
#         if context is None:
#             context = {}
#         record_id = context and context.get('active_id', False) or False
# #         lead = self.pool.get('crm.lead')
#         part = self.pool.get('res.partner')
# #         lead_obj = lead.browse(cr, uid, [record_id])
#         parent_id = record_id
#         part_obj = part.browse(cr, uid, [parent_id])
#         contact_ids = part_obj.search([('parent_id','=', parent_id)])
#         contact_list = []
#         for line in contact_ids:
#             contact_list.append(line.id)
#             vals = {'wiz_id': self.id,
#                     'actual_partner_id': line.id,
#                     'name': line.name,
#                     'function': line.function,
#                     'phone': line.phone,
#                     'email': line.email,
#                     'mobile': line.mobile}
#             part_line_obj = self.pool.get('wiz.move.contact.part.line')
#             part_line_obj.create(cr, uid, vals)
#         res['already_added_contacts'] = [[6,0,contact_list]]
#         res['partner_id'] = parent_id
#         return res
#     
#     def od_get_company_id(self):
#         return self.env.user.company_id
#     company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
#     partner_id  = fields.Many2one('res.partner',string="Customer")
#     already_added_contacts = fields.Many2many('res.partner', 'res_partner_contact2_rel','contact_id2','partner_id2','Contacts')
#     wiz_line = fields.One2many('wiz.move.contact.part.line','wiz_id')
#                 
#     @api.one
#     def move_contact(self):
#         part_obj = self.env['res.partner']
#         for line in self.already_added_contacts:
#             line_company = line.parent_id and line.parent_id.id
#             parent_company = self.partner_id.id
#             print line_company, parent_company, "C"*88
#             if line_company != parent_company :
#                 line.write({'active':False})
#                 part_obj.create({'name':line.name,
#                              'function':line.function,
#                              'phone':line.phone,
#                              'mobile':line.mobile,
#                             'parent_id': line.parent_id and line.parent_id.id,
#                             'email':line.email,
#                             'customer':True,
#                             'use_parent_address':True,
#                             'type':'contact' })
#         return True
#     
#     
# class wiz_move_contact_line(models.TransientModel):
#     _name = 'wiz.move.contact.part.line'
#     
#     wiz_id = fields.Many2one('wiz.move.contact.part',string="Wizard")
#     name = fields.Char(string="Name")
#     actual_partner_id  = fields.Many2one('res.partner',string="Customer")
#     function = fields.Char(string="Job Position")
#     phone = fields.Char(string="Phone")
#     mobile = fields.Char(string="Mobile")
#     email = fields.Char(string="Email")
    
    
class res_partner(models.Model):
    _inherit ='res.partner'
    
    @api.multi
    def add_people_from_part(self):
        return {
              'name': _('Add People'),
              'view_type': 'form',
              "view_mode": 'form',
              'res_model': 'wiz.add.contact.part',
              'type': 'ir.actions.act_window',
              'target':'new',
              }
    inactive_child_ids = fields.One2many('res.partner','parent_id',string='Inactive Contacts',domain=[('is_company', '=', False), ('active', '=', False)])    
#     @api.multi
#     def move_people_from_part(self):
#         return {
#               'name': _('Move People'),
#               'view_type': 'form',
#               "view_mode": 'form',
#               'res_model': 'wiz.move.contact.part',
#               'type': 'ir.actions.act_window',
#               'target':'new',
#               }

    @api.onchange('user_id')
    def onchange_user_id(self):
            if self.user_id:
                team_obj = self.env['crm.case.section']
                sales_team = team_obj.search([
                    '|',
                    ('user_id', '=', self.user_id.id),
                    ('member_ids', 'in', [self.user_id.id])
                ], order="id desc", limit=1)
                if sales_team:
                    self.section_id = sales_team.id
                else:
                    self.section_id = False
            else:
                self.section_id = False