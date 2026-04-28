# -*- coding: utf-8 -*-
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import models, fields, api, _
from __builtin__ import True, False
from pickle import FALSE
from openerp.exceptions import Warning


class BetaBankLoanClosing(models.Model):
    _name = 'od.beta.bank.loan.closing'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Bank Loan Closing Procedure"
    _order = 'create_date desc'
    
    def od_get_company_id(self):
        return self.env.user.company_id
    
    name = fields.Many2one('od.beta.bank.loan', string='Loan', domain=[('req_type','=','b'),('state','=','confirm')])
    link = fields.Char(string="Loan ERP Link")
    state = fields.Selection([('draft', 'Draft'), ('hr', 'HR Approval'),('finance', 'Finance Approval'),('confirm', 'Confirmed') ,('reject', 'Rejected')],
                                  string='State', readonly=True,
                                  track_visibility='always', copy=False,  default= 'draft')
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    #Loan Bank details
    close_date = fields.Date(string="Loan Closed Date")
    acc_name = fields.Char(string="Account Holder Name")
    bank_name = fields.Char(string="Loan Bank Name")
    l_iban = fields.Char(string="IBAN")
    h_approved_by = fields.Many2one('res.users', string='HR Approval By')
    h_appr_date = fields.Date(string='Date')
    f_approved_by = fields.Many2one('res.users', string='Finance Approval By')
    f_appr_date = fields.Date(string='Date')
    bank_contact_person = fields.Char(string="Bank Contact Person")
    phone = fields.Char(string="Phone Number")
    reference = fields.Char(string="Loan Ref No")
    remarks = fields.Text(string="Remarks")
    attach_file = fields.Binary('Attach Bank Clearance')
    attach_fname = fields.Char('File Name')
    number = fields.Char('Number')
    
    @api.onchange('name')
    def onchange_name(self):
        loan = self.name or False
        if loan:
            l_id = loan.id or False
            self.link= "https://erp.betait.net/web?#id="+str(l_id)+"&view_type=form&model=od.beta.bank.loan&menu_id=1186&action=1797"
            self.acc_name= loan.l_acc_name or False
            self.bank_name= loan.l_bank_name or False
            self.l_iban=  loan.l_iban or False
                        
    
    @api.model
    def create(self,vals):
        res = super(BetaBankLoanClosing, self).create(vals)
        if res.company_id.id == 6:
            res.number = self.env['ir.sequence'].get('od.bank.loan.closing') or '/'
        res.send_to_hr()
        return res
    
    @api.one
    def copy(self,defaults):
        res = super(BetaBankLoanClosing,self).copy(defaults)
        res.check_already_approved_loan()
        return res
        
    
    def od_send_mail(self,template):
        ir_model_data = self.env['ir.model.data']
        email_obj = self.pool.get('email.template')
        saudi_comp =6
        emp_company_id = self.company_id.id
        if emp_company_id == saudi_comp:
            template = template +'_saudi'
        template_id = ir_model_data.get_object_reference('beta_customisation', template)[1]
        crm_id = self.id
        email_obj.send_mail(self.env.cr, self.env.uid, template_id,crm_id)
        return True
    
    @api.one
    @api.model
    def send_to_hr(self):
        self.od_send_mail('od_loan_close_approval_hr')
        self.state = 'hr'
        return True
    
    @api.one
    @api.model
    def send_to_finance(self):
        if self.env.user.id == self.name.name.user_id.id:
            raise Warning("You cannot close your own loan request, Please Ask HR Team to do it..")
        if not self.attach_file:
            raise Warning("Please attach Clearance letter from Bank.!!!")
        self.h_approved_by = self.env.user.id
        self.h_appr_date = fields.Date.today()
        self.od_send_mail('od_loan_close_approval_finance')
        self.state = 'finance'
        return True
    
    def get_no_of_approved_loans(self):
        emp_rec = self.name and self.name.name or False
        emp_id = emp_rec.id
        rec = self.env['od.beta.bank.loan'].search([('name','=', emp_id),('req_type','=','b'),('state', '=', 'confirm')])
        return len(rec)

    
    @api.one
    @api.model
    def od_confirm(self):
        emp_rec = self.name and self.name.name or False
        self.f_approved_by = self.env.user.id
        self.f_appr_date = fields.Date.today()
        self.od_send_mail('od_loan_close_notify_employee')
        self.state = 'confirm'
        loan_count = self.get_no_of_approved_loans()
        #check if any other existing loan in system
        if loan_count == 1:
            emp_rec.write({'od_req_clearance' : False})
        self.name.write({'state' : 'close'})
        return True
    
    @api.one
    @api.model
    def reject_request(self):
        self.od_send_mail('od_loan_close_rejected_notify_employee')
        self.state = 'reject'
        return True
    
