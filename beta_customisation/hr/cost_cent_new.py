# -*- coding: utf-8 -*-
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import models, fields, api, _
from openerp.exceptions import Warning
import re

class res_partner(models.Model):
    _inherit = 'res.partner'
    
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
        if not self.is_company and email:
            name = self.name
            self.check_email(email,name)
            
    
    @api.one
    def _compute_parent_supplier(self):
        if self.parent_id and self.parent_id.supplier:
            self.parent_supplier = True
        if self.parent_id and self.parent_id.od_class:
            self.parent_class = self.parent_id.od_class
        if self.parent_id and self.parent_id.user_id:
            self.parent_sam = self.parent_id.user_id.id
        if self.parent_id and self.parent_id.od_territory_id:
            self.parent_territory = self.parent_id.od_territory_id.id
        if self.parent_id and self.parent_id.od_industry_id:
            self.parent_industry = self.parent_id.od_industry_id.id
        
        
        
    named_account = fields.Boolean(string="Named Account")
    od_class = fields.Selection([('a', 'A'), ('b', 'B'), ('c', 'C'), ('r', 'R')], string="Class", default="c")
    parent_supplier = fields.Boolean(compute='_compute_parent_supplier', string="Supplier")
    parent_class = fields.Selection([('a', 'A'), ('b', 'B'), ('c', 'C'), ('r', 'R')],compute='_compute_parent_supplier', string="Class")
    parent_sam = fields.Many2one('res.users',compute='_compute_parent_supplier', string="SAM")
    parent_territory = fields.Many2one('od.partner.territory',compute='_compute_parent_supplier', string="Terrirtoy")
    parent_industry = fields.Many2one('od.partner.industry',compute='_compute_parent_supplier', string="Industry")
    od_building_no = fields.Char(string="Building No.")
    od_additional_no = fields.Char(string="Additional No.")
    od_other_buyer_id = fields.Char(string="Other Buyer ID")
    od_cr_no = fields.Char(string="Commercial Register")
    district = fields.Char(string='District')
    buyer_identification = fields.Selection([('NAT', 'National ID'), ('IQA', 'Iqama Number'),
                                             ('PAS', 'Passport ID'),
                                             ('CRN', 'Commercial Registration number'),
                                             ('MOM', 'Momra license'), ('MLS', 'MLSD license'),
                                             ('SAG', 'Sagia license'), ('GCC', 'GCC ID'),
                                             ('OTH', 'Other OD'),
                                             ('TIN', 'Tax Identification Number'), ('700', '700 Number')],
                                            string="Buyer Identification",
                                            help="|) In case multiple IDs exist then one of the above must be entered,"
                                                 "||) In case of tax invoice, "
                                                 "      1) Not mandatory for export invoices.")
    
    @api.one
    def write(self, vals):
        user_id = vals.get('user_id', False)
        partner_id = self.id
        if user_id:
            lead_pool= self.env['crm.lead']
            opps = lead_pool.search([('partner_id','=',partner_id),('stage_id','in',[1,12,5,4,14])])
            leads = lead_pool.search([('partner_id','=',partner_id),('type','=','lead')])
            lead_ids = opps + leads
            for lead in lead_ids:
                lead.write({'user_id': user_id,
                            })
            
            partners = self.search([('parent_id','=',partner_id),('is_company','=',False)])
            for child in partners:
                child.write({'user_id': user_id,
                            })
                
        hr_pool = self.env['hr.employee']
        emp_ids = hr_pool.sudo().search([('job_id', 'in', (40, 83))])
        user_ids = [2390,134]
        for emp_id in emp_ids:
            user_ids.append(emp_id.user_id.id)  
        if self._uid in user_ids and vals.get('od_industry_id'):
                    raise Warning("You Cannot Change Industry,Please Discard..")
        if self._uid in user_ids and vals.get('od_territory_id'):
                raise Warning("You Cannot Change Territory,Please Discard..")
        if self._uid in user_ids and vals.get('od_class'):
                raise Warning("You Cannot Change Class,Please Discard..")
#         if self._uid in user_ids and vals.get('vat'):
#                 raise Warning("You Cannot Change TRN,Please Discard..")
        if self._uid in user_ids and vals.get('name'):
            if self.is_company == True:
                raise Warning("You Cannot Change Organization name, Please Discard..")
        email = vals.get('email')
        name = vals.get('name') or self.name
        if email and not self.is_company:
            self.check_email(email,name)
            
        return super(res_partner, self).write(vals)

    @api.model
    def create(self, vals):
        res = super(res_partner, self).create(vals)
        email = vals.get('email')
        name = vals.get('name')
        if vals.get('is_company') == True:
            hr_pool = self.env['hr.employee']
            emp_ids = hr_pool.sudo().search([('job_id', 'in', (40, 83))])
            user_ids = [2390,134]
            for emp_id in emp_ids:
                user_ids.append(emp_id.user_id.id)
            if self._uid in user_ids:
                raise Warning("You are not allowed to Create an Organization, Please Discard..")
        if email and not self.is_company:
            self.check_email(email,name)
        return res
    
    @api.multi
    def btn_open_partner(self):
       
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'res.partner',
                'res_id':self.id,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }
        
    @api.multi
    def btn_open_parent(self):
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'res.partner',
                'res_id':self.parent_id and self.parent_id.id,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }
    
class od_cost_branch(models.Model):
    _inherit = "od.cost.branch"
    named_account_ids = fields.Many2many('res.partner','rel_named_partner_accounts','branch_id','partner_id',string="Named Accounts",domain=[('is_company','=',True),('customer','=',True)])
    submit= fields.Boolean(string="Submit")
    approval= fields.Boolean(string="Approval")
    approval_state = fields.Selection([('pending', 'Pending Approval'), ('approved', 'Approved'), ('change', 'Change Request'), ('approve_change', 'Pending Change Approval')])
    
    enable_gp_approval = fields.Boolean(string="Enable GP Approval Workflow")
    range_ch =fields.Float(string="Range No")
    range_fr_1 = fields.Float(string="Range 1")
    range_fr_2 = fields.Float(string="Range 1")
    range_fr_3 = fields.Float(string="Range 1")
    range_fr_4 = fields.Float(string="Range 1")
    
    range_to_1 = fields.Float(string="Range 1")
    range_to_2 = fields.Float(string="Range 1")
    range_to_3 = fields.Float(string="Range 1")
    range_to_4 = fields.Float(string="Range 1")
    
    user_id_1 = fields.Many2one('res.users',"Approve Manager 2")
    user_id_2 = fields.Many2one('res.users',"Approve Manager 2")
    user_id_3 = fields.Many2one('res.users',"Approve Manager 3")
    user_id_4 = fields.Many2one('res.users',"Approve Manager 4")
    
    enab_1= fields.Boolean(string="Enable 1")
    enab_2= fields.Boolean(string="Enable 2")
    enab_3= fields.Boolean(string="Enable 3")
    enab_4= fields.Boolean(string="Enable 4")
    
    def od_send_mail(self,template):
        ir_model_data = self.env['ir.model.data']
        email_obj = self.pool.get('email.template')
        if self.company_id.id == 6:
            template = template +'_saudi'
        template_id = ir_model_data.get_object_reference('beta_customisation', template)[1]
        rec_id = self.id
        email_obj.send_mail(self.env.cr,self.env.uid,template_id,rec_id, force_send=True)
        return True
    
    @api.one 
    def btn_submit(self):
        if not self.named_account_ids:
            raise Warning("At least one Account should be added before submitting for CEO Approval")
        self.write({'submit':True, 'approval_state':'pending'})
        self.od_send_mail('od_branch_named_account_submit_mail')
        
    @api.one 
    def btn_submit_change(self):
        if not self.named_account_ids:
            raise Warning("At least one Account should be added before submitting for CEO Approval")
        self.write({'submit':True, 'approval_state':'approve_change'})
        self.od_send_mail('od_branch_named_account_change_submit_mail')

    
    @api.one
    def btn_approval(self):
        for part in self.named_account_ids:
            part.write({'named_account':True})
        self.write({'approval':True, 'approval_state':'approved'})
        self.od_send_mail('od_branch_named_account_approved_mail')
        
    @api.one 
    def btn_approve_change(self):
        for part in self.named_account_ids:
            part.write({'named_account':True})
        self.write({'approval':True, 'approval_state':'approved'})
        self.od_send_mail('od_branch_named_account_approved_mail')

    
    @api.one 
    def btn_change(self):
        for part in self.named_account_ids:
            part.write({'named_account':False})
        self.write({'submit':False,'approval':False,'approval_state':'change'})
        self.od_send_mail('od_branch_named_account_change_mail')