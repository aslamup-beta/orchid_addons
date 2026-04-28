# -*- coding: utf-8 -*-
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.exceptions import Warning

from openerp import models, fields, api, _
 
class BetaNamedAccounts(models.Model):
    _name = 'named.accounts'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Beta Named Accounts"
    _rec_name = 'branch_id'
    
    def od_get_company_id(self):
        return self.env.user.company_id
    
    name = fields.Char(string="Name")
    branch_id = fields.Many2one('od.cost.branch', string='Branch')
    named_accounts_lines = fields.One2many('named.accounts.line', 'named_account_id', 'Named Accounts Line')
    submit= fields.Boolean(string="Submit")
    approval= fields.Boolean(string="Approval")
    change1 = fields.Boolean(string="Changed")
    approval_state = fields.Selection([('pending', 'Pending Approval'), ('change', 'Change Request'), ('approved', 'Approved'), ('approve_change', 'Pending Change Approval')], track_visibility='always')
    new_added_named_account_ids = fields.Many2many('res.partner','rel_new_named_partner_accounts','branch_id','partner_id',string="New Added Named Accounts",domain=[('is_company','=',True),('customer','=',True),('named_account','=',False)])
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    select_all = fields.Boolean(string="Select ALL")
    
    _sql_constraints = [
                        ('branch_id_uniq', 'unique(branch_id)', 'Branch once created. You can update the existing record instead of creating new !!'),
                        ]
    
    def od_send_mail(self,template):
        ir_model_data = self.env['ir.model.data']
        email_obj = self.pool.get('email.template')
        if self.company_id.id == 6:
            template = template +'_saudi'
        template_id = ir_model_data.get_object_reference('beta_customisation', template)[1]
        rec_id = self.id
        email_obj.send_mail(self.env.cr,self.env.uid,template_id,rec_id, force_send=True)
        return True
    
    @api.onchange('select_all')
    def onchange_select_all(self):
        if self.select_all:
            for x in self.named_accounts_lines:
                x.remove = True
        else:
            for x in self.named_accounts_lines:
                x.remove = False
    
    
    
    @api.multi
    def update_branch_approval_state(self, branch, state):
        branch.write({'approval_state': state})
    
    @api.one 
    def btn_submit(self):
        branch = self.branch_id
        if not self.new_added_named_account_ids:
            raise Warning("At least one Account should be added before submitting for CEO Approval")
        self.write({'submit':True, 'approval_state':'pending'})
        self.update_branch_approval_state(branch, state='pending')
        self.od_send_mail('od_branch_named_account_submit_mail1')
        
    @api.one 
    def btn_submit_change(self):
        branch = self.branch_id
        if not self.new_added_named_account_ids:
            raise Warning("At least one Account should be added before submitting for CEO Approval")
        self.write({'submit':True, 'approval_state':'approve_change'})
        self.update_branch_approval_state(branch, state='pending')
        self.od_send_mail('od_branch_named_account_change_submit_mail1')
    
    @api.multi
    def update_branch_data(self, branch, named_accounts_lines):
        for line in branch.named_account_ids:
            branch.write({'named_account_ids': [(3, line.id)]})
        for line in named_accounts_lines:
            branch.write({'named_account_ids': [(4, line.account_id.id)]})
            
    @api.one
    def btn_approval(self):
        branch = self.branch_id
        for line in self.new_added_named_account_ids:
            self.named_accounts_lines.create({'account_id': line.id, 'user_id':line.user_id.id })
            self.write({'new_added_named_account_ids': [(3, line.id)]})
        for line in self.named_accounts_lines:
            if not line.remove:
                line.account_id.write({'named_account':True})
            else:
                line.account_id.write({'named_account':False})
                line.unlink()
        
        self.write({'approval':True, 'approval_state':'approved'})
        self.update_branch_data(branch, self.named_accounts_lines)
        self.update_branch_approval_state(branch, state='approved')
        self.od_send_mail('od_branch_named_account_approved_mail1')
        
    @api.one 
    def btn_approve_change(self):
        branch = self.branch_id
        for line in self.new_added_named_account_ids:
            self.named_accounts_lines.create({'named_account_id': self.id,'account_id': line.id, 'user_id':line.user_id.id })
            self.write({'new_added_named_account_ids': [(3, line.id)]})
        for line in self.named_accounts_lines:
            if not line.remove:
                line.account_id.write({'named_account':True})
            else:
                line.account_id.write({'named_account':False})
                line.unlink()
                
        self.write({'approval':True, 'approval_state':'approved'})
        self.update_branch_data(branch, self.named_accounts_lines)
        self.update_branch_approval_state(branch, state='approved')
        self.od_send_mail('od_branch_named_account_approved_mail1')

    @api.one 
    def btn_change(self):
        branch = self.branch_id
        self.write({'submit':False,'approval':False,'change1':True, 'approval_state':'change'})
        self.update_branch_approval_state(branch, state='change')
        self.od_send_mail('od_branch_named_account_change_mail1')
    
class BetaNamedAccountsLine(models.Model):
    _name = 'named.accounts.line'
    
    account_id = fields.Many2one('res.partner',string="Account Name",domain=[('is_company','=',True),('customer','=',True)])
    user_id = fields.Many2one('res.users',string='Sales Person')
    remove= fields.Boolean(string="Remove Account")
    named_account_id = fields.Many2one('named.accounts')
    od_part_class = fields.Selection([('a', 'A'), ('b', 'B'), ('c', 'C'), ('r', 'R')], string="Class")
    
    @api.onchange('account_id')
    def onchange_account_id(self):
        account_id = self.account_id or False
        if account_id:
            self.user_id= account_id.user_id and account_id.user_id.id or False
    
    