# -*- coding: utf-8 -*-
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.exceptions import Warning
from openerp.tools import amount_to_text_en
from openerp import models, fields, api, _


class EndofContract(models.Model):
    _name = 'end.of.contract'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Beta End of Contract"
    _rec_name = 'employee_id'
    _order = 'id desc'

    def od_get_company_id(self):
        return self.env.user.company_id

    def days_between(self, d1, d2):
        d1 = datetime.strptime(d1, "%Y-%m-%d")
        d2 = datetime.strptime(d2, "%Y-%m-%d")
        return abs((d2 - d1).days) + 1

    def leave_days(self, d2):
        d2 = datetime.strptime(d2, "%Y-%m-%d")
        joining_date = self.joining_date or False
        last_day = self.last_day_date or False
        days_of_service = self.days_between(joining_date, last_day)
        if days_of_service < 365.0:
            d1 = datetime.strptime(joining_date, "%Y-%m-%d")
        else:
            d1 = d2.replace(month=1, day=1)
        return abs((d2 - d1).days) + 1

    def is_same_year(self, date1, date2):
        """
        Check if two dates are in the same year
        :param date1: First date string in 'YYYY-MM-DD' format
        :param date2: Second date string in 'YYYY-MM-DD' format
        :return: True if same year, False otherwise
        """
        if not date1 or not date2:
            return False

        # Parse dates
        date1_obj = datetime.strptime(date1, '%Y-%m-%d')
        date2_obj = datetime.strptime(date2, '%Y-%m-%d')

        # Compare years
        return date1_obj.year == date2_obj.year

    def get_number_of_working_days_in_same_year(self, joining_day, last_day):
        first_date = joining_day
        number_of_working_days_in_current_year = self.days_between(first_date, last_day)
        return number_of_working_days_in_current_year

    def get_number_of_working_days_in_current_year(self, last_day):
        start_date = datetime.strptime(last_day, "%Y-%m-%d")
        start_year = start_date.year
        d1 = datetime(start_year, 1, 1)
        first_date = d1.strftime("%Y-%m-%d")
        number_of_working_days_in_current_year = self.days_between(first_date, last_day)
        return number_of_working_days_in_current_year

    def get_leave_taken_in_final_year(self, employee_id, last_day):
        start_date = datetime.strptime(last_day, "%Y-%m-%d")
        start_year = start_date.year
        d1 = datetime(start_year, 1, 1)
        first_date = d1.strftime("%Y-%m-%d")
        leaves = self.env['hr.holidays'].search([
            ('holiday_status_id', '=', 1),
            ('employee_id', '=', employee_id),
            ('state', 'not in', ('draft', 'cancel', 'refuse')),
            ('date_from', '>=', first_date),  # Leaves starting on or after start_date
            ('date_to', '<=', last_day),  # Leaves ending on or before last_day
        ])
        days = 0
        for obj in leaves:
            days += obj.od_number_of_days
        # number_of_working_days_in_current_year = self.days_between(first_date, last_day)
        return days

    def _get_pending_leave(self):
        print("_get_pending_leave")
        service = self.years_of_service
        employee_id = self.employee_id and self.employee_id.id
        if self.company_id.id == 6:
            if self.create_date < '2025-08-01':
                last_day = self.last_day_date or False
                if last_day:
                    leave_avail = self.leave_days(last_day)
                    leave_taken = self.employee_id.od_legal_leave
                    days = 0.0
                    if service < 1.0:
                        leaves = self.env['hr.holidays'].search(
                            [('holiday_status_id', '=', 1), ('employee_id', '=', employee_id),
                             ('state', 'not in', ('draft', 'cancel', 'refuse'))])
                        print("leaves 11111111111", leaves)
                        for obj in leaves:
                            days += obj.od_number_of_days
                            leave_taken = days
                    leave_pending_days = leave_avail - leave_taken
                    leave_tot = (leave_pending_days * 30) / 365.0
                    leave_pending = leave_tot - leave_taken
                    contract_ob = self._get_contract_obj()
                    full_salary = contract_ob.xo_total_wage
                    day_wage = full_salary / 30.0
                    leave_salary = leave_pending * day_wage
                    self.leave_pending = leave_pending
                    self.leave_salary_amount = leave_salary
            else:
                same_year = False
                last_day = self.last_day_date or False
                joining_day = self.joining_date or False
                if last_day:
                    leave_taken = self.get_leave_taken_in_final_year(employee_id, last_day)
                    # print("leave_taken_test", leave_taken_test)
                    # leave_taken = self.employee_id.od_legal_leave
                    days = 0.0
                    if service < 1.0:
                        leaves = self.env['hr.holidays'].search(
                            [('holiday_status_id', '=', 1), ('employee_id', '=', employee_id),
                             ('state', 'not in', ('draft', 'cancel', 'refuse'))])
                        for obj in leaves:
                            days += obj.od_number_of_days
                            leave_taken = days
                    same_year = self.is_same_year(joining_day, last_day)
                    if same_year:
                        number_of_working_days_in_current_year = self.get_number_of_working_days_in_same_year(
                            joining_day, last_day)
                    else:
                        number_of_working_days_in_current_year = self.get_number_of_working_days_in_current_year(
                            last_day)
                    leave_pending = (30.0 / 365.0 * number_of_working_days_in_current_year) - leave_taken
                    #                 if service < 1.0:
                    #                     leave_pending = (24.0/365.0* number_of_working_days_in_current_year) - leave_taken
                    rounded_leave_pending = round(leave_pending, 2)
                    contract_ob = self._get_contract_obj()
                    leave_salary = rounded_leave_pending * (contract_ob.xo_total_wage / 30.0)
                    self.leave_pending = leave_pending
                    self.leave_salary_amount = leave_salary


        else:
            last_day = self.last_day_date or False
            if last_day:
                leave_avail = self.leave_days(last_day)
                leave_taken = self.get_leave_taken_in_final_year(employee_id, last_day)
                days = 0.0
                if service < 1.0:
                    leaves = self.env['hr.holidays'].search(
                        [('holiday_status_id', '=', 1), ('employee_id', '=', employee_id),
                         ('state', 'not in', ('draft', 'cancel', 'refuse'))])
                    for obj in leaves:
                        days += obj.od_number_of_days
                        leave_taken = days
                leave_pending_days = leave_avail - leave_taken
                leave_tot = (leave_pending_days * 30) / 365.0
                if service < 1.0:
                    leave_tot = (leave_pending_days * 24) / 365.0
                leave_pending = leave_tot - leave_taken
                contract_ob = self._get_contract_obj()
                basic = contract_ob.wage
                day_wage = basic / 30.0
                leave_salary = leave_pending * day_wage
                self.leave_pending = leave_pending
                self.leave_salary_amount = leave_salary

    def _get_allowances(self):
        contract = self._get_contract_obj()
        result = 0.0
        for line in contract.xo_allowance_rule_line_ids:
            if line.code == 'OA':
                result += line.amt
            if line.code == 'ALW':
                result += line.amt
            if line.code == 'HA':
                result += line.amt
            if line.code == 'KSA_HA':
                result += line.amt
            if line.code == 'KSA_TA':
                result += line.amt

        return result

    def _get_pending_salary(self):
        contract_ob = self._get_contract_obj()
        full_salary = contract_ob.wage + self._get_allowances()
        day_wage = full_salary / 30.0
        start_date = self.date_start
        has_pending_salary = self.has_pending_salary
        end_date = self.date_end
        if has_pending_salary and start_date and end_date:
            days = self.days_between(start_date, end_date)
            if days == 31:
                days = 30
            self.pending_salary = days * day_wage or 0.0
        else:
            self.pending_salary = 0.0

    @api.one
    def _compute_unpaid_leaves(self):
        joining_date = self.joining_date
        last_day = self.last_day_date
        employee_id = self.employee_id and self.employee_id.id
        days = 0.0
        leaves = self.env['hr.holidays'].search(
            [('od_start', '>', joining_date), ('od_end', '<', last_day), ('holiday_status_id', '=', 4),
             ('employee_id', '=', employee_id), ('state', 'not in', ('draft', 'cancel', 'refuse'))])
        for obj in leaves:
            days += obj.od_number_of_days
        if days:
            self.unpaid_days = days

    @api.one
    def _compute_years(self):
        joining_date = self.joining_date
        last_day = self.last_day_date
        if joining_date and last_day:
            days = self.days_between(joining_date, last_day)
            years = days / 365.2425
            self.years_of_service = years

    @api.one
    def _compute_final_years(self):
        unpaid_days = self.unpaid_days
        unpaid_in_years = unpaid_days / 365.2425
        years = self.years_of_service - unpaid_in_years
        self.final_years_of_service = years

    def _get_contract_obj(self):
        employee_id = self.employee_id and self.employee_id.id or False
        res = self.env['hr.contract'].search([('od_active', '=', True), ('employee_id', '=', employee_id)], limit=1)
        if self.employee_id.active == False:
            res = self.env['hr.contract'].search([('employee_id', '=', employee_id)], order='id desc')[0]
        return res

    def od_get_total_salary(self, emp_id):
        res = self.env['hr.contract'].search([('od_active', '=', True), ('employee_id', '=', emp_id)], limit=1)
        if self.employee_id.active == False:
            res = self.env['hr.contract'].search([('employee_id', '=', emp_id)], order='id desc')[0]
            print res, "c" * 88
        total = 0.0
        salary = 0.0
        company_id = self.env.user.company_id.id
        # if company_id == 6:
        total = res.xo_total_wage
        kpi = 0
        if res.xo_allowance_rule_line_ids:
            for rule in res.xo_allowance_rule_line_ids:
                if rule.code == 'KPI':
                    kpi = rule.amt
        salary = total - kpi
        # if company_id == 1:
        #     salary = res.wage
        return salary

    def _get_gratuvity(self):
        emp_id = self.employee_id and self.employee_id.id or False
        if self.company_id.id == 6:
            #             contract_ob = self._get_contract_obj()
            #             monthly_salary = contract_ob.xo_total_wage
            monthly_salary = self.od_get_total_salary(emp_id)
            service = self.final_years_of_service
            res = 0.0
            if 1 <= service < 5:
                res = (monthly_salary / 2) * service
            if service >= 5:
                up_to_5 = (monthly_salary / 2) * 5
                after_5_service = service - 5.0
                after_5 = monthly_salary * after_5_service
                res = up_to_5 + after_5
            self.gratuvity = res
        else:
            contract_ob = self._get_contract_obj()
            basic_salary = contract_ob.wage
            day_wage = (basic_salary / 30.0)
            service = self.final_years_of_service
            service = round(service, 2)
            res = 0.0
            if 0.5 <= service < 5:
                res = 21 * service * day_wage
            if service >= 5:
                up_to_5 = 21 * day_wage * 5
                after_5_service = service - 5.0
                after_5_grat = 30.0 * day_wage * after_5_service
                res = up_to_5 + after_5_grat
            self.gratuvity = res

    def _get_final(self):
        leave_salary_amt = self.leave_salary_amount
        pending_salary = self.pending_salary
        if self.is_manual_leave_salary_amount:
            leave_salary_amt = self.man_leave_salary_amount
        if self.is_manual_pending_salary:
            pending_salary = self.man_pending_salary
        res = self.gratuvity + leave_salary_amt + pending_salary + self.other_payment - self.other_deduction
        self.final_settlement = res

    def _get_amount_to_pay(self):
        final_amount = self.final_settlement
        gratuity = self.gratuvity
        service = self.final_years_of_service
        employee = self.employee_id
        leave_salary_amt = self.leave_salary_amount
        pending_salary = self.pending_salary
        if self.is_manual_leave_salary_amount:
            leave_salary_amt = self.man_leave_salary_amount
        if self.is_manual_pending_salary:
            pending_salary = self.man_pending_salary
        remaining_amt = leave_salary_amt + pending_salary + self.other_payment - self.other_deduction
        if self.company_id.id == 6:
            if service < 2.0:
                self.amount_to_pay = gratuity + remaining_amt
                self.final_grat = gratuity
            if service >= 2.0:
                self.amount_to_pay = gratuity + remaining_amt
                self.final_grat = gratuity
            if employee.gender == 'female':
                if employee.od_mrg_date:
                    res = self.check_six_months_conditions()
                    if res:
                        self.amount_to_pay = gratuity + remaining_amt
                        self.final_grat = gratuity
                if employee.od_child_birth_date:
                    res = self.check_three_months_conditions()
                    if res:
                        self.amount_to_pay = gratuity + remaining_amt
                        self.final_grat = gratuity
        else:
            self.amount_to_pay = gratuity + remaining_amt
            self.final_grat = gratuity

    employee_id = fields.Many2one('hr.employee', string='Name of Employee', track_visibility='onchange')
    # state = fields.Selection([('draft', 'Start'), ('approval1', 'Direct Manager'), ('approval4', 'IT Approval'),
    #                           ('notify_bank', 'Waiting to Notify Bank'), ('approval2', 'Finance Approval'),
    #                           ('approval3', 'GM Approval'), ('approval5', 'HR Approval'), ('confirm', 'Confirmed'),
    #                           ('sent_clearance', 'Clearance Send to Bank'), ('cancel', 'Refused')],
    #                          string='State', readonly=True,
    #                          track_visibility='always', copy=False, default='draft')
    state = fields.Selection(
        [('draft', 'Start'), ('approval1', 'Direct Manager'), ('notify_bank', 'Waiting to Notify Bank'),
         ('approval2', 'Finance Approval'), ('approval3', 'GM Approval'), ('approval5', 'HR Approval'),
         ('approval4', 'IT Approval'), ('cs_approval', 'Cyber Security Approval'), ('confirm', 'Confirmed'),
         ('sent_clearance', 'Clearance Send to Bank'), ('cancel', 'Refused')],
        string='State', readonly=True,
        track_visibility='always', copy=False, default='draft')
    department_id = fields.Many2one('hr.department', string='Department')
    job_id = fields.Many2one('hr.job', string='Job Title')
    last_day_date = fields.Date(string='Last Day At Work', track_visibility='onchange', copy=False)
    term_date = fields.Date(string='End of Contract Date', copy=False)
    branch_id = fields.Many2one('od.cost.branch', string='Branch')
    tech_dept_id = fields.Many2one('od.cost.division', string='Technology Unit/Department')
    manager1_id = fields.Many2one('res.users', string='First Approval Manager')
    manager2_id = fields.Many2one('res.users', string='Second Approval Manager')
    company_id = fields.Many2one('res.company', string='Company', default=od_get_company_id)
    reason = fields.Text("Reason for End of Contract")
    notes = fields.Text("Notes")

    joining_date = fields.Date(string="Joining Date", related="employee_id.od_joining_date")
    basic_salary = fields.Float(string="Basic Salary")
    allowance = fields.Float(string="Allowance")
    full_salary = fields.Float(string="Full Salary")
    years_of_service = fields.Float(string="Years Of Service", compute='_compute_years')
    unpaid_days = fields.Float(string="Unpaid Leaves(Days)", compute='_compute_unpaid_leaves')
    final_years_of_service = fields.Float(string="Final Years Of Service", compute='_compute_final_years')
    gratuvity = fields.Float(string="Gratuity Amount", compute='_get_gratuvity')
    leave_pending = fields.Float(string="No of Leave Pending", compute='_get_pending_leave')
    leave_salary_amount = fields.Float(string="Leave Salary Amount", compute='_get_pending_leave')
    is_manual_leave_salary_amount = fields.Boolean(string="Manually Enter Leave Salary Amount?")
    man_leave_salary_amount = fields.Float(string="Leave Salary Amount(Manual)")
    final_settlement = fields.Float(string="Final Settlement", compute='_get_final')
    has_pending_salary = fields.Boolean(string="Pending Salary")
    date_start = fields.Date(string='Start Date')
    date_end = fields.Date(string='End Date')
    pending_salary = fields.Float(string="Pending Salary Amount", compute='_get_pending_salary')
    is_manual_pending_salary = fields.Boolean(string="Manually Enter Pending Salary Amount?")
    man_pending_salary = fields.Float(string="Pending Salary Amount(Manual)")
    other_payment = fields.Float(string="Other Payment")
    other_deduction = fields.Float(string="Other Deduction")
    amount_to_pay = fields.Float(string="Amount to be Paid", compute='_get_amount_to_pay')
    final_grat = fields.Float(string="Final Gratuity", compute='_get_amount_to_pay')
    force_majure = fields.Boolean(string="Leaves the work due to a force majeure?")
    account_move_id = fields.Many2one('account.move', string='Ledger Posting')

    staff_no = fields.Integer(string="Staff No")
    profession = fields.Char(string="Profession")
    overtime_hrs = fields.Float(string="Overtime Hours")
    bank_clearnce = fields.Selection([('yes', 'YES'), ('no', 'NO')], string="Bank Clearance Letter")
    l_bank_id = fields.Many2one('beta.loan.bank', string='Loan Bank')
    it_approved_by = fields.Many2one('res.users', string='IT DEPT Manager')
    it_approved_date = fields.Datetime(string="Approval Date")
    om_approved_by = fields.Many2one('res.users', string='OPERATION MANAGER')
    om_approved_date = fields.Datetime(string="Approval Date")
    sales_approved_by = fields.Many2one('res.users', string='SALES DEPT')
    sales_approved_date = fields.Datetime(string="Approval Date")
    approved_by = fields.Many2one('res.users', string='DIRECT MANAGER')
    approved_date = fields.Datetime(string="Approval Date")
    fin_approved_by = fields.Many2one('res.users', string='FINANCE MANAGER')
    fin_approved_date = fields.Datetime(string="Approval Date")
    gm_approved_by = fields.Many2one('res.users', string='GENERAL MANAGER')
    gm_approved_date = fields.Datetime(string="Approval Date")
    hr_approved_by = fields.Many2one('res.users', string='HR MANAGER')
    hr_approved_date = fields.Datetime(string="Approval Date")
    bank_email = fields.Char(string="Bank Email")
    notified_bank = fields.Boolean(string="Notified Bank")
    clearance_sent_to_bank = fields.Boolean(string="Clearance Sent to bank")
    clearance_sent_to_bank = fields.Boolean(string="Clearance Sent to bank")
    cs_approved_by = fields.Many2one('res.users', string='Cyber Security Manager')
    cs_approved_date = fields.Datetime(string="Approval Date")
    cs_feedback_1 = fields.Selection([('confirmed', 'Confirmed'), ('not_confirmed', 'Not Confirmed')],
                                     string="CS Feedback 1")
    cs_feedback_2 = fields.Selection([('confirmed', 'Confirmed'), ('not_confirmed', 'Not Confirmed')],
                                     string="CS Feedback 2")
    cs_feedback_3 = fields.Selection([('confirmed', 'Confirmed'), ('not_confirmed', 'Not Confirmed')],
                                     string="CS Feedback 3")
    cs_feedback_4 = fields.Selection([('confirmed', 'Confirmed'), ('not_confirmed', 'Not Confirmed')],
                                     string="CS Feedback 4")
    cs_feedback_5 = fields.Selection([('confirmed', 'Confirmed'), ('not_confirmed', 'Not Confirmed')],
                                     string="CS Feedback 5")

    def _get_clearence_status(self, employee):
        if employee:
            bank_clearnce = employee.od_req_clearance
            if bank_clearnce:
                res = "yes"
            else:
                res = "no"
        return res

    def _get_clearence_bank_email(self, employee):
        loan_bank_email = ''
        if employee:
            rec = self.env['od.beta.bank.loan'].search(
                [('name', '=', employee.name), ('req_type', '=', 'b'), ('state', '=', 'confirm')])
            if len(rec) >= 1 and employee.od_req_clearance:
                loan_bank_email = rec.l_bank_id.bank_email
        return loan_bank_email

    def _get_clearence_bank(self, employee):
        loan_bank = False
        if employee:
            rec = self.env['od.beta.bank.loan'].search(
                [('name', '=', employee.name), ('req_type', '=', 'b'), ('state', '=', 'confirm')])
            if len(rec) >= 1 and employee.od_req_clearance:
                loan_bank = rec.l_bank_id.id
        return loan_bank

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        employee = self.employee_id or False
        if employee:
            self.department_id = employee.department_id and employee.department_id.id or False
            self.job_id = employee.job_id and employee.job_id.id or False
            self.branch_id = employee.od_branch_id and employee.od_branch_id.id or False
            self.tech_dept_id = employee.od_division_id and employee.od_division_id.id or False
            self.manager1_id = employee.sudo().parent_id and employee.sudo().parent_id.user_id and employee.sudo().parent_id.user_id.id or False
            self.manager2_id = employee.od_branch_id and employee.od_branch_id.manager_user_id and employee.od_branch_id.manager_user_id.id or False
            self.staff_no = employee.od_identification_no or False
            contract_ob = self._get_contract_obj()
            self.basic_salary = contract_ob.wage
            self.allowance = self._get_allowances()
            self.bank_clearnce = self._get_clearence_status(employee)
            self.bank_email = self._get_clearence_bank_email(employee)
            self.l_bank_id = self._get_clearence_bank(employee)

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
    def submit(self):
        self.approved_by = self.env.user.id
        self.approved_date = fields.Date.today()
        if self.company_id.id == 6:
            if self.employee_id.od_req_clearance:
                self.od_send_mail('eoc_notification_to_hr_finance_to_notify_bank')
                self.state = 'notify_bank'
            else:
                self.od_send_mail('od_eoc_notification_to_finance')
                self.state = 'approval2'
        else:
            # self.od_send_mail('od_terminate_notification_to_hr_finance')
            self.state = 'approval2'

        return True

    @api.one
    @api.model
    def action_send_it_approval_mail(self):
        print("action_send_it_approval_mail")
        self.od_send_mail('od_eoc_approval_it')
        return True

    @api.model
    def create(self, vals):
        res = super(EndofContract, self).create(vals)
        res.submit()
        return res

    @api.one
    @api.model
    def finance_approval(self):
        if self.employee_id.od_req_clearance:
            raise Warning("This Employee requires a Clearance certificate before you do Approval")
        self.fin_approved_by = self.env.user.id
        self.fin_approved_date = fields.Date.today()
        if self.company_id.id == 6:
            self.od_send_mail('od_eoc_approval2')
        self.state = 'approval3'
        return True

    @api.one
    @api.model
    def it_approval(self):
        self.od_send_mail('od_eoc_approval_cs')
        self.state = 'cs_approval'
        self.it_approved_by = self.env.user.id
        self.it_approved_date = fields.Date.today()
        return True

    @api.one
    @api.model
    def action_return(self):
        # self.od_send_mail('od_resignation_approval1')
        self.state = 'approval4'
        return True

    @api.one
    @api.model
    def action_cs_approval(self):
        if not self.cs_feedback_1 or not self.cs_feedback_2 or not self.cs_feedback_3 or not self.cs_feedback_4 or not self.cs_feedback_5:
            raise Warning("You Cannot Approve without filling the cyber security clearance tab")
        if self.env.user.id == self.employee_id.user_id.id:
            raise Warning("You Cannot Approve your own Resignation, Please Ask IT Team to do it..")
        if self.cs_feedback_1 == 'not_confirmed':
            raise Warning("Please confirm Email Address Disabled?")
        if self.cs_feedback_2 == 'not_confirmed':
            raise Warning("Please confirm Azure Active Directory User Disabled?")
        if self.cs_feedback_3 == 'not_confirmed':
            raise Warning("Please confirm Laptop Formatted (Sanitized)?")
        if self.cs_feedback_4 == 'not_confirmed':
            raise Warning("Please confirm Physical Access Revoked?")
        if self.cs_feedback_5 == 'not_confirmed':
            raise Warning("Please confirm Lab Access Revoked")
        # if self.employee_id.od_req_clearance and self.company_id.id == 6:
        #     self.od_send_mail('od_notification_to_hr_finance_to_notify_bank')
        #     self.state = 'notify_bank'
        # else:
        # self.od_send_mail('od_notification_to_hr_finance')
        self.state = 'confirm'
        self.cs_approved_by = self.env.user.id
        self.cs_approved_date = fields.Date.today()
        return True

    @api.one
    @api.model
    def action_notify_bank(self):
        if self.employee_id.od_req_clearance and self.company_id.id == 6:
            self.od_send_mail('od_notify_bank_eoc')
            self.state = 'approval2'
            self.notified_bank = True
            self.employee_id.write({'od_req_clearance': False})
        return True

    @api.one
    @api.model
    def skip_notify_bank(self):
        self.od_send_mail('od_eoc_notification_to_finance')
        self.state = 'approval2'

    @api.one
    @api.model
    def second_approval(self):
        if self.company_id.id == 6:
            self.od_send_mail('od_eoc_notification_to_hr')
        self.state = 'approval5'
        self.gm_approved_by = self.env.user.id
        self.gm_approved_date = fields.Date.today()
        return True

    @api.one
    @api.model
    def hr_approval(self):
        if self.env.user.id == self.employee_id.user_id.id:
            raise Warning("You Cannot Approve your own End of Contract, Please Ask your HR Manager to do it..")
        self.employee_id.write({'od_end_contract': True, 'od_last_day': self.last_day_date})
        if self.company_id.id == 6:
            self.state = 'approval4'
        else:
            self.state = 'confirm'
        self.hr_approved_by = self.env.user.id
        self.hr_approved_date = fields.Date.today()
        return True

    def sent_clearance_to_bank(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.notified_bank and rec.company_id.id == 6:
                # create a wizard and auto pop up below template. ask team to attach proper documents..
                # self.od_send_mail('od_sent_clearance_to_bank')
                ir_model_data = self.pool.get('ir.model.data')
                template_id = ir_model_data.get_object_reference(cr, uid, 'beta_customisation',
                                                                 'od_sent_clearance_to_bank_eoc_saudi')[1]
                try:
                    compose_form_id = \
                        ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
                except ValueError:
                    compose_form_id = False
                ctx = dict(context)
                ctx.update({
                    'default_model': 'end.of.contract',
                    'default_res_id': ids[0],
                    'default_use_template': bool(template_id),
                    'default_template_id': template_id,
                    'default_composition_mode': 'comment',
                    'bank_clearance_sent': True
                })
                return {
                    'name': _('Compose Email'),
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'mail.compose.message',
                    'views': [(compose_form_id, 'form')],
                    'view_id': compose_form_id,
                    'target': 'new',
                    'context': ctx,
                }

    @api.one
    @api.model
    def refuse(self):
        self.state = 'cancel'
        return True

    @api.one
    @api.model
    def unlink(self):
        for rec in self:
            if rec.state not in ('draft', 'cancel'):
                raise Warning(_('You cannot delete a termination form which is not draft or refused.'))
        return super(EndofContract, self).unlink()

    @api.multi
    def amount_to_text_eng(self, amount, currency):
        convert_amount_in_words = amount_to_text_en.amount_to_text(amount, lang='en', currency=currency)
        company_id = self.company_id and self.company_id.id
        if company_id == 6:
            convert_amount_in_words = convert_amount_in_words.replace('Cent', 'Halala')
        else:
            convert_amount_in_words = convert_amount_in_words.replace('Cent', 'Fill')
        return convert_amount_in_words

    @api.one
    @api.model
    def generate_gratuity_accounting_entry(self):
        period_obj = self.env['account.period']
        move_obj = self.env['account.move']
        date = fields.Date.today()
        period_ids = period_obj.find(date).id
        ref = self.employee_id.name + " End of Service"
        partner_id = self.employee_id.address_home_id and self.employee_id.address_home_id.id or False
        branch_id = self.employee_id.od_branch_id and self.employee_id.od_branch_id.id or False
        cost_centre_id = self.employee_id.od_cost_centre_id and self.employee_id.od_cost_centre_id.id or False

        total_amount_to_pay = self.amount_to_pay
        leave_salary_amt = self.leave_salary_amount
        pending_salary = self.pending_salary
        if self.is_manual_pending_salary:
            pending_salary = self.man_pending_salary
        if self.is_manual_leave_salary_amount:
            leave_salary_amt = self.man_leave_salary_amount
        other_pay = self.other_payment
        other_deduct = self.other_deduction
        remaining_amt = leave_salary_amt + pending_salary + other_pay - other_deduct
        gratuity = total_amount_to_pay - remaining_amt

        # Accounts IDS in ERP KSA
        journal_id = 41
        move_lines = []
        if leave_salary_amt:
            debit_account = 5440
            d_vals1 = {
                'name': 'LEAVE CLEARANCE',
                'period_id': period_ids,
                'journal_id': journal_id,
                'date': date,
                'account_id': debit_account,
                'credit': 0.0,
                'quantity': 1,
                'debit': abs(leave_salary_amt),
                'partner_id': partner_id,
                'od_branch_id': branch_id,
                'od_cost_centre_id': cost_centre_id
            }
            move_lines.append([0, 0, d_vals1])

        if gratuity:
            debit_account = 5735
            d_vals2 = {
                'name': 'GRATUITY CLEARANCE',
                'period_id': period_ids,
                'journal_id': journal_id,
                'date': date,
                'account_id': debit_account,
                'credit': 0.0,
                'quantity': 1,
                'debit': abs(gratuity),
                'partner_id': partner_id,
                'od_branch_id': branch_id,
                'od_cost_centre_id': cost_centre_id
            }
            move_lines.append([0, 0, d_vals2])
        if pending_salary:
            debit_account = 5434
            d_vals3 = {
                'name': 'SALARY EXPENSE',
                'period_id': period_ids,
                'journal_id': journal_id,
                'date': date,
                'account_id': debit_account,
                'credit': 0.0,
                'quantity': 1,
                'debit': abs(pending_salary),
                'partner_id': partner_id,
                'od_branch_id': branch_id,
                'od_cost_centre_id': cost_centre_id
            }
            move_lines.append([0, 0, d_vals3])
        if other_pay:
            debit_account = 5265
            d_vals4 = {
                'name': 'OTHER PAYMENT',
                'period_id': period_ids,
                'journal_id': journal_id,
                'date': date,
                'account_id': debit_account,
                'credit': 0.0,
                'quantity': 1,
                'debit': abs(other_pay),
                'partner_id': partner_id,
                'od_branch_id': branch_id,
                'od_cost_centre_id': cost_centre_id
            }
            move_lines.append([0, 0, d_vals4])
        if other_deduct:
            credit_account = 5265
            c_vals1 = {
                'name': 'OTHER DEDUCTION',
                'period_id': period_ids,
                'journal_id': journal_id,
                'date': date,
                'account_id': credit_account,
                'quantity': 1,
                'debit': 0.0,
                'credit': abs(other_deduct),
                'partner_id': partner_id,
                'od_branch_id': branch_id,
                'od_cost_centre_id': cost_centre_id
            }
            move_lines.append([0, 0, c_vals1])

        if total_amount_to_pay:
            credit_account = 5265
            c_vals2 = {
                'name': 'FINAL CLEARANCE PAY',
                'period_id': period_ids,
                'journal_id': journal_id,
                'date': date,
                'account_id': credit_account,
                'quantity': 1,
                'debit': 0.0,
                'credit': abs(total_amount_to_pay),
                'partner_id': partner_id,
                'od_branch_id': branch_id,
                'od_cost_centre_id': cost_centre_id
            }
            move_lines.append([0, 0, c_vals2])
            move_lines.reverse()
        move_vals = {

            'date': date,
            'ref': ref,
            'period_id': period_ids,
            'journal_id': journal_id,
            'line_id': move_lines
        }
        move_id = move_obj.create(move_vals).id
        self.account_move_id = move_id
        return True


class mail_compose_message(models.Model):
    _inherit = 'mail.compose.message'

    @api.multi
    def send_mail(self):
        context = self._context
        if context.get('default_model') == 'end.of.contract' and \
                context.get('default_res_id') and context.get('bank_clearance_sent'):
            rec = self.env['end.of.contract'].browse(context['default_res_id'])
            rec.write({'clearance_sent_to_bank': True, 'state': 'sent_clearance'})
        return super(mail_compose_message, self).send_mail()
