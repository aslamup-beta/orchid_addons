# -*- coding: utf-8 -*-
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import models, fields, api, _
from __builtin__ import True, False
from pickle import FALSE
from openerp.exceptions import Warning


class SalafLoanForm(models.Model):
    _name = 'beta.loan.salaf'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Beta IT Loan Assistance Program SALAF"
    _order = 'create_date desc'
    
    def od_get_company_id(self):
        return self.env.user.company_id
    
    def od_get_total_salary(self):
        emp_id = self.name
        if emp_id:
            res =self.env['hr.contract'].search([('od_active','=',True),('employee_id','=',emp_id.id)],limit=1)
            if self.name.active == False:
                res =self.env['hr.contract'].search([('employee_id','=',emp_id.id)], order='id desc')[0]
            self.monthly_salary = res.xo_total_wage
    
    @api.onchange('loan_amount')
    def onchange_loan_amount(self):
        res = 0.0
        if self.loan_amount:
            res = self.loan_amount/6
        self.monthly_instalment = res
        
    @api.onchange('start_date')
    def onchange_start_date(self):
        res = 0.0
        if self.start_date:
            date_start = self.start_date
            start_date_datetime = datetime.strptime(date_start, "%Y-%m-%d")
            res = start_date_datetime + relativedelta(months=6)
            self.end_date = res
        
    
    def default_loan_terms(self):
        res = """
        <h3>Loan Conditions:</h3>
        <p>1. The loan amount is up to one-month gross salary.</p>
        <p>2. The Loan shall be settled back within 6 months.</p>
        <p>3. The loan is applicable once every 12 months.</p>
        <p>4. Loan settlement will be through deduction from the monthly salary.</p>
        <p>5. Loan settlement will start from the next month after receiving the loan.</p>
        </br>
        <h3>General Terms:</h3>
        <p>1. The program is valid starting Jan 1, 2025, and it ends on Dec 31, 2025. It will be reviewed every year.</p>
        <p>2. In case the employee resigns or gets terminated, the remaining balance of the loan will be deducted from his end of service gratuity. If the end of service gratuity does not cover the remaining balance of the loan, the balance will be deducted from the notice period salary payments (distributed equally on the notice period months).</p>
        </br>
        <h3>Company Commitment:</h3>
        <p>1. Salary Deduction: The company will automatically deduct the specified amount for six months, provided that the deducted amount does not exceed 50% of the salary during the agreement period.</p>
        <p>2. Deduction Justification: The company will submit the deduction on a monthly basis through the Wage Protection System.</p>
        </br>
        <h3>Employee Commitment:</h3>
        <p>1. Request of Loan: The employee confirms the submission of this loan request for a period of six months, and the company theirs no responsibility.</p>
        <p>2. Acceptance of Deduction Justification: The employee must accept the deduction justification on a monthly basis through the Wage Protection System within three days.</p>
        </br>
        <h3>Mandatory Authorization:</h3>
        """

        return res
    
    name  = fields.Many2one('hr.employee', string='Name', track_visibility='onchange')
    state = fields.Selection([('draft', 'Draft'),('manager', 'Manager Approval'), ('hr', 'Pending HR Review'),('finance', 'Reviewed & Confirmed'),('confirm', 'Approved'), ('close', 'Loan Closed') ,('reject', 'Rejected')],
                                  string='State', readonly=True,
                                  track_visibility='always', copy=False,  default= 'draft')
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
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    
    loan_amount = fields.Integer(string="Loan Amount", track_visibility='always')
    monthly_instalment = fields.Float(string="Monthly Installment")
    repay_period = fields.Integer(string="Repayment Period (Months)", default = 6)
    reason = fields.Text(string="Reason")
    purpose = fields.Selection([('housing', 'Housing - سكن'),('education', 'Education - دفعة مدارس'), ('family', 'Family Residence - مقابل مالي لإقامة العائلة'),('travel', 'Travelling - سفر'),('car', 'Buying a car - شراء'), ('invest', 'Investment - استثمار') ,('others', 'Others')],
                                  string='Pupose of Loan', track_visibility='always', copy=False)
    other_purpose = fields.Char(string="Specify the other purpose")
    monthly_salary = fields.Float(string="Monthly Salary",compute='od_get_total_salary')
    joining_date =fields.Date(string="Joining Date",related="name.od_joining_date")
    start_date = fields.Date(string="Loan Start Date")
    end_date = fields.Date(string="Loan End Date")
    company_authorize = fields.Boolean(string="Authorization")
    accept_terms = fields.Boolean(string="Accept terms")

    
    h_approved_by = fields.Many2one('res.users', string='HR Review')
    h_review = fields.Char(string="HR Review")
    h_appr_date = fields.Date(string='Date')
    f_approved_by = fields.Many2one('res.users', string='Finance Approval')
    f_review = fields.Char(string="Finance Approval")
    f_appr_date = fields.Date(string='Date')
    loan_terms = fields.Html(string='Terms',default=default_loan_terms, readonly="1")
    
    @api.onchange('name')
    def onchange_name(self):
        employee = self.name or False
        if employee:
            self.department_id= employee.department_id and employee.department_id.id or False
            self.job_id= employee.job_id and employee.job_id.id or False
            self.branch_id= employee.od_branch_id and employee.od_branch_id.id or False
            self.manager_id=  employee.sudo().parent_id and employee.sudo().parent_id.user_id and employee.sudo().parent_id.user_id.id or False
            self.nationality= employee.country_id and employee.country_id.id or False
            self.passport_no = employee.passport_id or False
            self.lab_no = employee.otherid or False
            self.govt_id = employee.identification_id or False
            self.work_email = employee.work_email or False
            self.mobile = employee.mobile_phone or False
            #Staffno field
            self.emp_id = employee.od_identification_no or False
            if not (self.passport_no and self.govt_id and self.emp_id and self.lab_no):
                raise Warning("Kindly Contact HR team to update below all missing information in Employee profile before creating this document.\n  a)Government ID \n b)Staff No \n c)Passport No \n d)Labour Card No. ")
    
                
    def check_loan_conditions(self):
        emp_rec = self.name
        emp_id = emp_rec.id
        rec = self.search([('name','=', emp_id),('state', '=', 'confirm')])
        if len(rec) >= 1:
            raise Warning("You already have a loan approved in system. Please close the loan before proceeding with new")
        if self.loan_amount > self.monthly_salary:
            raise Warning("The loan amount is up to one-month gross salary. You cannot exceed more than %s"%self.monthly_salary)
        join_date = self.joining_date
        join_date_datetime = datetime.strptime(join_date, "%Y-%m-%d")
        res = join_date_datetime + relativedelta(months=3)
        date_start = self.start_date or False
        if date_start:
            start_date_datetime = datetime.strptime(date_start, "%Y-%m-%d")
            if res > start_date_datetime:
                raise Warning("You are only eligible to apply for Beta IT Loan Assistance Program (SALAF) after completing probation period.")

            
    
    @api.model
    def create(self,vals):
        res = super(SalafLoanForm, self).create(vals)
        res.check_loan_conditions()
        #res.send_to_hr()
        return res
    
    @api.one
    def copy(self,defaults):
        res = super(SalafLoanForm,self).copy(defaults)
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
        self.check_loan_conditions()
        self.od_send_mail('beta_salaf_loan_approval_hr')
        self.state = 'hr'
        return True
    
    @api.one
    @api.model
    def send_to_finance(self):
        self.check_loan_conditions()
        if self.env.user.id == self.name.user_id.id:
            raise Warning("You Cannot Approve your own loan request, Please Ask HR Team to do it..")
        self.h_approved_by = self.env.user.id
        self.h_review = 'Reviewed & Processed by HR Team'
        self.h_appr_date = fields.Date.today()
        self.od_send_mail('beta_salaf_loan_approval_finance')
        self.state = 'finance'
        return True
    
    @api.one
    @api.model
    def od_confirm(self):
        self.f_review = 'Approved'
        self.f_approved_by = self.env.user.id
        self.f_appr_date = fields.Date.today()
        self.od_send_mail('beta_salaf_loan_approved_notify_employee')
        self.state = 'confirm'
        return True
    
    @api.one
    @api.model
    def reject_request(self):
        if self.state == 'hr':
            self.h_review = 'Rejected by HR Team'
            self.h_appr_date = fields.Date.today()
        if self.state == 'finance':
            self.f_review = 'Rejected'
            self.f_appr_date = fields.Date.today()
        self.od_send_mail('beta_salaf_loan_rejected_notify_employee')
        self.state = 'reject'
        return True
