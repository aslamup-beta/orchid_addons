# -*- coding: utf-8 -*-
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import models, fields, api, _
from __builtin__ import True, False
from pickle import FALSE
from openerp.exceptions import Warning


class BetaLoanBank(models.Model):
    _name = 'beta.loan.bank'
    _description = "Loan Bank"

    name = fields.Char(string='Name')
    name_ar = fields.Char(string='Name (Arabic)')
    bank_email = fields.Char(string='Bank Email')


class BetaBankLoanForm(models.Model):
    _name = 'od.beta.bank.loan'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Bank Loan Internal Procedure"
    _order = 'create_date desc'

    def od_get_company_id(self):
        return self.env.user.company_id

    name = fields.Many2one('hr.employee', string='Name', track_visibility='onchange')
    state = fields.Selection(
        [('draft', 'Draft'), ('manager', 'Manager Approval'), ('hr', 'HR Approval'), ('finance', 'Finance Approval'),
         ('confirm', 'Confirmed'), ('close', 'Loan Closed'), ('reject', 'Rejected')],
        string='State', readonly=True,
        track_visibility='always', copy=False, default='draft')
    work_email = fields.Char(string='Work Email')
    mobile = fields.Char(string="Mobile No")
    govt_id = fields.Char(string="Government ID")
    emp_id = fields.Char(string="Staff No.")
    passport_no = fields.Char(string="Passport No.")
    lab_no = fields.Char(string="Labour Card No.")

    department_id = fields.Many2one('hr.department', string='Department')
    job_id = fields.Many2one('hr.job', string='Job Title')
    nationality = fields.Many2one('res.country', string='Nationality')
    branch_id = fields.Many2one('od.cost.branch', string='Branch')
    manager_id = fields.Many2one('res.users', string='Direct Manager')
    company_id = fields.Many2one('res.company', string='Company', default=od_get_company_id)

    # Loan Bank details
    is_loan_req = fields.Boolean(string="Is Loan Document required?", track_visibility='onchange', default=False)
    date = fields.Date(string="From Date")
    l_acc_name = fields.Char(string="Account Holder Name")
    l_bank_id = fields.Many2one('beta.loan.bank', string='Bank')
    l_bank_name = fields.Char(string="Bank Name")
    l_bank_name_ar = fields.Char(string="Bank Name(Arabic)")
    l_account_number = fields.Char(string="Account number")
    l_swift_code = fields.Char(string="Swift Code")
    l_iban = fields.Char(string="IBAN")
    req_type = fields.Selection([('a', 'Change Bank Details Only'), ('b', 'Change Bank Details With Loan Documents')],
                                string='Type of Request', track_visibility='always')

    # Salary Transfer details
    is_sal_trn_req = fields.Boolean(string="Is Salary Transfer required?", track_visibility='onchange', default=False)
    n_acc_name = fields.Char(string="Account Holder Name")
    n_bank_name = fields.Char(string="Bank Name")
    n_account_number = fields.Char(string="Account number")
    n_swift_code = fields.Char(string="Swift Code")
    n_iban = fields.Char(string="IBAN")

    o_acc_name = fields.Char(string="Account Holder Name")
    o_bank_name = fields.Char(string="Bank Name")
    o_account_number = fields.Char(string="Account number")
    o_swift_code = fields.Char(string="Swift Code")
    o_iban = fields.Char(string="IBAN")

    # Address details
    street = fields.Char(string='Street')
    street2 = fields.Char(string='Street2')
    city = fields.Char(string='City')
    zip = fields.Char(string='Zip', size=24, change_default=True)
    state_id = fields.Many2one('res.country.state', string='State')
    country_id = fields.Many2one('res.country', string='Country')

    # commitment details
    m_form_cmd_id = fields.Many2one('od.loan.comment', string='Comments')
    m_bank_cmd_id = fields.Many2one('od.loan.comment', string='Comments')
    m_salary_cmd_id = fields.Many2one('od.loan.comment', string='Comments')
    m_eos_cmd_id = fields.Many2one('od.loan.comment', string='Comments')

    h_form_cmd_id = fields.Many2one('od.loan.comment', string='Comments')
    h_bank_cmd_id = fields.Many2one('od.loan.comment', string='Comments')
    h_salary_cmd_id = fields.Many2one('od.loan.comment', string='Comments')
    h_eos_cmd_id = fields.Many2one('od.loan.comment', string='Comments')
    h_ongoing_loan_cmd_id = fields.Many2one('od.bankloan.comment', string='Comments')
    h_clearance_cmd_id = fields.Many2one('od.bankloan.comment', string='Comments')

    f_form_cmd_id = fields.Many2one('od.loan.comment', string='Comments')
    f_bank_cmd_id = fields.Many2one('od.loan.comment', string='Comments')
    f_salary_cmd_id = fields.Many2one('od.loan.comment', string='Comments')
    f_eos_cmd_id = fields.Many2one('od.loan.comment', string='Comments')
    f_ongoing_loan_cmd_id = fields.Many2one('od.loan.comment', string='Comments')
    f_clearance_cmd_id = fields.Many2one('od.loan.comment', string='Comments')

    m_approved_by = fields.Many2one('res.users', string='Manager Approval By')
    m_appr_date = fields.Date(string='Date')
    h_approved_by = fields.Many2one('res.users', string='HR Approval By')
    h_appr_date = fields.Date(string='Date')
    f_approved_by = fields.Many2one('res.users', string='Finance Approval By')
    f_appr_date = fields.Date(string='Date')

    @api.onchange('name')
    def onchange_name(self):
        employee = self.name or False
        if employee:
            self.department_id = employee.department_id and employee.department_id.id or False
            self.job_id = employee.job_id and employee.job_id.id or False
            self.branch_id = employee.od_branch_id and employee.od_branch_id.id or False
            self.manager_id = employee.sudo().parent_id and employee.sudo().parent_id.user_id and employee.sudo().parent_id.user_id.id or False
            self.nationality = employee.country_id and employee.country_id.id or False
            self.passport_no = employee.passport_id or False
            self.lab_no = employee.otherid or False
            self.govt_id = employee.identification_id or False
            self.work_email = employee.work_email or False
            self.mobile = employee.mobile_phone or False
            # Staffno field
            self.emp_id = employee.od_identification_no or False
            if not (self.passport_no and self.govt_id and self.emp_id and self.lab_no):
                raise Warning(
                    "Kindly Contact HR team to update below all missing information in Employee profile before creating this document.\n  a)Government ID \n b)Staff No \n c)Passport No \n d)Labour Card No. ")

    @api.onchange('req_type')
    def onchange_req_type(self):
        req_type = self.req_type
        if req_type:
            if req_type == 'a':
                self.is_sal_trn_req = True
                self.is_loan_req = False
            else:
                self.is_sal_trn_req = True
                self.is_loan_req = True

    @api.onchange('l_bank_id')
    def onchange_l_bank_id(self):
        bank = self.l_bank_id
        if bank:
            self.l_bank_name = bank.name
            self.l_bank_name_ar = bank.name_ar

    def check_already_approved_loan(self):
        emp_rec = self.name
        emp_id = emp_rec.id
        rec = self.search([('name', '=', emp_id), ('req_type', '=', 'b'), ('state', '=', 'confirm')])
        if len(rec) >= 1 and emp_rec.od_req_clearance:
            raise Warning(
                "You already have a loan approved in system. Please provide confirmation letter from the bank to HR that you finished the loan.")

    @api.model
    def create(self, vals):
        res = super(BetaBankLoanForm, self).create(vals)
        res.check_already_approved_loan()
        res.send_to_hr()
        return res

    @api.one
    def copy(self, defaults):
        res = super(BetaBankLoanForm, self).copy(defaults)
        res.check_already_approved_loan()
        return res

    def od_send_mail(self, template):
        ir_model_data = self.env['ir.model.data']
        email_obj = self.pool.get('email.template')
        saudi_comp = 6
        emp_company_id = self.company_id.id
        if emp_company_id == saudi_comp:
            template = template + '_saudi'
        template_id = ir_model_data.get_object_reference('beta_customisation', template)[1]
        crm_id = self.id
        email_obj.send_mail(self.env.cr, self.env.uid, template_id, crm_id)
        return True

    @api.one
    @api.model
    def send_to_manager(self):
        self.state = 'manager'
        self.od_send_mail('od_loan_form_approval_manager')
        return True

    def check_m_feedback_done(self):
        if not self.m_form_cmd_id:
            raise Warning("Form Details Comment Needed")
        if not self.m_bank_cmd_id:
            raise Warning("Loan Bank Details Comment Needed")
        if not self.m_salary_cmd_id:
            raise Warning("Salary Transfer Details Comment Needed")

    def check_h_feedback_done(self):
        if not self.h_form_cmd_id:
            raise Warning("Form Details Comment Needed")
        if not self.h_bank_cmd_id:
            raise Warning("Loan Bank Details Comment Needed")
        if not self.h_salary_cmd_id:
            raise Warning("Salary Transfer Details Comment Needed")
        if not self.h_eos_cmd_id:
            raise Warning("End of Service Transfer conditions Comment Needed")
        if not self.h_ongoing_loan_cmd_id:
            raise Warning("Loan with other Banks Comment Needed")
        if self.h_ongoing_loan_cmd_id == 1 and not self.h_clearance_cmd_id:
            raise Warning("Clearance from other Banks Comment Needed")

    def check_f_feedback_done(self):
        if not self.f_form_cmd_id:
            raise Warning("Form Details Comment Needed")
        if not self.f_bank_cmd_id:
            raise Warning("Loan Bank Details Comment Needed")
        if not self.f_salary_cmd_id:
            raise Warning("Salary Transfer Comment Needed")
        if not self.f_eos_cmd_id:
            raise Warning("End of Service Transfer conditions Comment Needed")
        if not self.f_ongoing_loan_cmd_id:
            raise Warning("Loan with other Banks Comment Needed")
        if self.h_ongoing_loan_cmd_id.id == 1 and not self.h_clearance_cmd_id:
            raise Warning("Clearance from other Banks Comment Needed")

    @api.one
    @api.model
    def send_to_hr(self):
        # self.check_m_feedback_done()
        self.m_approved_by = self.env.user.id
        self.m_appr_date = fields.Date.today()
        if not self.is_loan_req:
            self.od_send_mail('od_loan_form_approval_hr')
        else:
            self.od_send_mail('od_loan_form2_approval_hr')
        self.state = 'hr'
        return True

    @api.one
    @api.model
    def send_to_finance(self):
        if self.env.user.id == self.name.user_id.id:
            raise Warning("You Cannot Approve your own Salary Transfer request, Please Ask HR Team to do it..")
        if self.h_ongoing_loan_cmd_id.id == 1 and self.h_clearance_cmd_id.id == 2:
            raise Warning("Clearance required from old Bank. Please Reject the Application !!!")
        self.check_h_feedback_done()
        self.h_approved_by = self.env.user.id
        self.h_appr_date = fields.Date.today()
        if not self.is_loan_req:
            self.od_send_mail('od_loan_form_approval_finance')
        else:
            self.od_send_mail('od_loan_form2_approval_finance')
        self.state = 'finance'
        return True

    @api.one
    @api.model
    def od_confirm(self):
        self.check_f_feedback_done()
        self.f_approved_by = self.env.user.id
        self.f_appr_date = fields.Date.today()
        self.od_send_mail('od_loan_form_approved_notify_employee')
        self.state = 'confirm'
        if self.req_type == 'b':
            employee = self.name
            employee.write({'od_req_clearance': True})
        return True

    @api.one
    @api.model
    def reject_request(self):
        self.od_send_mail('od_loan_form_rejected_notify_employee')
        self.state = 'reject'
        return True


class od_loan_comment(models.Model):
    _name = 'od.loan.comment'
    name = fields.Char('Comments')


class od_bankloan_comment(models.Model):
    _name = 'od.bankloan.comment'
    name = fields.Char('Comments')
