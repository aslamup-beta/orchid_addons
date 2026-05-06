# -*- coding: utf-8 -*-
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

from openerp import models, fields, api, _


class BetaJoiningForm(models.Model):
    _name = 'od.beta.joining.form'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Beta Joining Form"
    _order = 'id desc'

    def od_get_company_id(self):
        return self.env.user.company_id

    def od_get_struct_id(self):
        company_id = self.env.user.company_id.id or False
        if company_id == 6:
            salary_struct = 3
        else:
            salary_struct = 8
        return salary_struct

    def _get_work_hrs_id(self):
        company_id = self.env.user.company_id.id or False
        if company_id == 6:
            work_sched = 3
        else:
            work_sched = 1
        return work_sched

    name = fields.Char(string='Employee Name', track_visibility='onchange')
    state = fields.Selection(
        [('draft', 'Start'), ('employee', 'Waiting for Employee'), ('finance', 'Finance'), ('confirm', 'Confirmed'),
         ('cancel', 'Terminated')],
        string='State', readonly=True,
        track_visibility='always', copy=False, default='draft')
    work_email = fields.Char(string='Work Email')
    personal_email = fields.Char(string="Personal Email")
    mobile = fields.Char(string="Mobile No")
    #     father_name = fields.Char(string="Father Name")
    passport_no = fields.Char(string="Passport Number")

    place_of_birth = fields.Char(string="Place of Birth")
    department_id = fields.Many2one('hr.department', string='Department')
    job_id = fields.Many2one('hr.job', string='Job Title')
    sales_team_id = fields.Many2one('crm.case.section', string='Sales Team')
    manager_id = fields.Many2one('hr.employee', string='Manager')
    coach_id = fields.Many2one('hr.employee', string='Coach')
    nationality = fields.Many2one('res.country', string='Nationality')
    dob = fields.Date(string='Date of Birth')
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], 'Gender')
    martial = fields.Selection(
        [('single', 'Single'), ('married', 'Married'), ('widower', 'Widower'), ('divorced', 'Divorced')],
        'Marital Status')
    joining_date = fields.Date(string='Joining Date', track_visibility='onchange')
    branch_id = fields.Many2one('od.cost.branch', string='Branch')
    tech_dept_id = fields.Many2one('od.cost.division', string='Technology Unit/Department')
    cost_centre_id = fields.Many2one('od.cost.centre', string='Cost Centre')
    pay_salary_during_annual_leave = fields.Boolean('Pay Salary During Annual Leave', default=True)

    type_id = fields.Many2one('hr.contract.type', string='Contract Type')
    mode_of_pay_id = fields.Many2one('od.mode.of.payment', string='Mode of Payment')
    total_wage = fields.Float(string="Total Wage")
    basic_wage = fields.Float(string="Basic Wage")
    allowance_rule_line_ids = fields.One2many('allowance.rule.line', 'joining_id', 'Rule Lines')
    salary_struct = fields.Many2one('hr.payroll.structure', string='Salary Structure', default=od_get_struct_id)
    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account")

    work_sched = fields.Many2one('resource.calendar', string='Working Schedule', default=_get_work_hrs_id)
    employee_id = fields.Many2one('hr.employee', string="Employee")
    #     work_hrs = fields.Integer(string="Working Hours")
    #     schedule_pay = fields.Selection([
    #             ('monthly', 'Monthly'),
    #             ('quarterly', 'Quarterly'),
    #             ('semi-annually', 'Semi-annually'),
    #             ('annually', 'Annually'),
    #             ('weekly', 'Weekly'),
    #             ('bi-weekly', 'Bi-weekly'),
    #             ('bi-monthly', 'Bi-monthly'),
    #             ], 'Scheduled Pay', select=True, default="monthly")
    #     journal_id = fields.Many2one('account.journal', string='Salary Journal')
    manager1_id = fields.Many2one('res.users', string='First Approval Manager(Leaves)')
    manager2_id = fields.Many2one('res.users', string='Second Approval Manager(Leaves)')
    #     audit_temp_id = fields.Many2one('audit.template', string='Audit Template')
    document_line_ids = fields.One2many('od.hr.employee.document.line', 'joining_id', string='Document Lines')
    #     image = fields.Binary("Photo",
    #             help="This field holds the image used as photo for the employee, limited to 1024x1024px.")
    company_id = fields.Many2one('res.company', string='Company', default=od_get_company_id)

    # Address details
    street = fields.Char(string='Street')
    street2 = fields.Char(string='Street2')
    city = fields.Char(string='City')
    zip = fields.Char(string='Zip', size=24, change_default=True)
    state_id = fields.Many2one('res.country.state', string='State')
    country_id = fields.Many2one('res.country', string='Country')

    e_c1_name = fields.Char(string='Emergency Contact')
    e_c1_relationship = fields.Char(string='Relationship')
    e_c1_street = fields.Char(string='Street')
    e_c1_street2 = fields.Char(string='Street2')
    e_c1_city = fields.Char(string='City')
    e_c1_state_id = fields.Many2one('res.country.state', string='State')
    e_c1_country_id = fields.Many2one('res.country', string='Country')
    e_c1_ph1 = fields.Char(string='Mobile')
    e_c1_ph2 = fields.Char(string='Phone')

    # Outsource employee details
    customer_id = fields.Many2one('res.partner', 'Customer')
    so_id = fields.Many2one('sale.order', 'Sales Order')
    costsheet_id = fields.Many2one('od.cost.sheet', 'Cost Sheet')
    analytic_id = fields.Many2one('account.analytic.account', string="Analytic Account")
    proj_manager = fields.Many2one('res.users', 'Project Manager')
    sponsorship = fields.Many2one('res.partner', 'Sponsorship')
    join_date = fields.Date(string="Customer Joining Date")
    end_date = fields.Date(string="Customer Contract End Date")
    employee_end_date = fields.Date(string="Employee Contract End Date")

    # For Creation of Outsourced Employees
    @api.onchange('costsheet_id')
    def onchange_costsheet_id(self):
        costsheet_id = self.costsheet_id or False
        if costsheet_id:
            self.customer_id = costsheet_id.od_customer_id and costsheet_id.od_customer_id.id or False
            self.tech_unit = costsheet_id.od_division_id and costsheet_id.od_division_id.id or False
            self.proj_manager = costsheet_id.reviewed_id and costsheet_id.reviewed_id.id or False
            self.so_id = costsheet_id.od_mat_sale_id and costsheet_id.od_mat_sale_id.id or False

    def get_outsourced_emp_vals(self):
        vals = {'name': self.name,
                'profession_id': self.job_id and self.job_id.id or False,
                'customer_id': self.customer_id and self.customer_id.id or False,
                'so_id': self.so_id and self.so_id.id or False,
                'costsheet_id': self.costsheet_id and self.costsheet_id.id or False,
                'tech_unit': self.tech_dept_id and self.tech_dept_id.id or False,
                'proj_manager': self.proj_manager and self.proj_manager.id or False,
                'sponsorship': self.sponsorship and self.sponsorship.id or False,
                'join_date': self.join_date or False,
                'end_date': self.end_date or False,
                'employee_end_date': self.employee_end_date or False,
                'salary_proposed': self.total_wage or False,
                'personal_email': self.personal_email or False,
                'work_email': self.work_email or False,
                'mobile_phone': self.mobile or False,
                'image': self.image or False,
                'active': True
                }
        return vals

    @api.model
    def create_om_analytic_line(self, emp_id):
        analytic_id = self.analytic_id or False
        if analytic_id:
            line_vals = {'start_date': analytic_id.date_start, 'end_date': analytic_id.od_date_end_original,
                         'analytic_id': analytic_id.id, 'outsource_id': emp_id.id}
            self.env['od.outsource.analytics'].create(line_vals)
        return True

    @api.model
    def attach_out_doc_emp(self, emp_id):
        model = self.env['od.attachement']
        for doc_line in self.document_line_ids:
            attach_file = doc_line.attach_file or None
            model.create({'name': doc_line.document_referance,
                          'attach_file': attach_file,
                          'attach_fname': doc_line.attach_fname or False,
                          'model_name': 'outsource.employee',
                          'object_id': emp_id,
                          'issue_date': doc_line.issue_date,
                          'expiry_date': doc_line.expiry_date,
                          'type': 'binary'})
        return True

    @api.model
    def create_outsourced_employee(self):
        employee_pool = self.env['outsource.employee']
        vals = self.get_outsourced_emp_vals()
        emp_id = employee_pool.create(vals)
        self.attach_out_doc_emp(emp_id)
        self.create_om_analytic_line(emp_id)
        return emp_id

    # End and starting the code for Beta It Employee creation

    def get_emp_vals(self):
        company_id = self.env.user.company_id.id or False
        if company_id == 6:
            address_id = 6926
        else:
            address_id = 1
        vals = {'name': self.name,
                'address_id': address_id,
                'work_email': self.work_email or False,
                'department_id': self.department_id and self.department_id.id or False,
                'job_id': self.job_id and self.job_id.id or False,
                'audit_temp_id': self.job_id and self.job_id.audit_temp_id and self.job_id.audit_temp_id.id or False,
                'parent_id': self.manager_id and self.manager_id.id or False,
                'coach_id': self.coach_id and self.coach_id.id or False,
                'country_id': self.nationality and self.nationality.id or False,
                'birthday': self.dob or False,
                'marital': self.martial or False,
                'place_of_birth': self.place_of_birth or False,
                #                 'od_father': self.father_name or False,
                'passport_id': self.passport_no or False,
                'mobile_phone': self.mobile or False,
                'od_personal_email': self.personal_email or False,
                'gender': self.gender or False,
                'active': True,
                'od_joining_date': self.joining_date or False,
                'od_pay_salary_during_annual_leave': self.pay_salary_during_annual_leave or False,
                'od_branch_id': self.branch_id and self.branch_id.id or False,
                'od_division_id': self.tech_dept_id and self.tech_dept_id.id or False,
                'od_cost_centre_id': self.cost_centre_id and self.cost_centre_id.id or False,
                'od_based_on_basic': True,
                'od_first_manager_id': self.manager1_id and self.manager1_id.id or False,
                'od_second_manager_id': self.manager2_id and self.manager2_id.id or False,
                'image': self.image or False,
                'od_street': self.street or False,
                'od_street2': self.street2 or False,
                'od_city': self.city or False,
                'od_zip': self.zip or False,
                'od_state_id': self.state_id and self.state_id.id or False,
                'od_country_id': self.country_id and self.country_id.id or False,
                'od_e_c1_name': self.e_c1_name or False,
                'od_e_c1_relationship': self.e_c1_relationship or False,
                'od_e_c1_street': self.e_c1_street or False,
                'od_e_c1_street2': self.e_c1_street2 or False,
                'od_e_c1_city': self.e_c1_city or False,
                'od_e_c1_state_id': self.e_c1_state_id and self.e_c1_state_id.id or False,
                'od_e_c1_country_id': self.e_c1_country_id and self.e_c1_country_id.id or False,
                'od_e_c1_ph1': self.e_c1_ph1 or False,
                'od_e_c1_ph2': self.e_c1_ph2 or False,
                }
        return vals

    @api.model
    def create_employee(self):
        employee_pool = self.env['hr.employee']
        vals = self.get_emp_vals()
        emp_id = employee_pool.create(vals)
        return emp_id

    @api.model
    def create_contract(self, emp_id):
        contract_pool = self.env['hr.contract']
        date_start_dt = fields.Datetime.from_string(self.joining_date)
        company_id = self.env.user.company_id.id or False
        journal_id = False
        limited = False
        date_end = False
        work_hrs = 9.0
        if company_id == 6:
            dt1 = date_start_dt + relativedelta(months=3)
            journal_id = 58
            work_hrs = 8.0
        else:
            dt1 = date_start_dt + relativedelta(months=6)
            journal_id = 21
            work_hrs = 9.0
        country_id = self.nationality and self.nationality.id or False
        if company_id == 6 and country_id != 194:
            dt = date_start_dt + relativedelta(months=24)
            # DECREASE 1 DAY FROM END DATE AS PER KSA RULE
            dt = dt - relativedelta(days=1)
            date_end = fields.Datetime.to_string(dt)
            limited = True

        vals = {'name': self.name,
                'employee_id': emp_id.id,
                'job_id': self.job_id and self.job_id.id or False,
                'od_active': True,
                'type_id': self.type_id and self.type_id.id or False,
                'xo_mode_of_payment_id': self.mode_of_pay_id and self.mode_of_pay_id.id or False,
                'xo_total_wage': self.total_wage,
                'wage': self.basic_wage,
                'struct_id': self.salary_struct and self.salary_struct.id or False,
                'xo_allowance_rule_line_ids': [(0, 0, {'rule_type': x.rule_type.id, 'amt': x.amt}) for x in
                                               self.allowance_rule_line_ids],
                'trial_date_start': self.joining_date,
                'trial_date_end': fields.Datetime.to_string(dt1),
                'date_start': self.joining_date,
                'date_end': date_end,
                'od_limited': limited,
                'working_hours': self.work_sched and self.work_sched.id or False,
                'xo_working_hours': work_hrs,
                'schedule_pay': 'monthly',
                'journal_id': journal_id
                }

        contract_id = contract_pool.create(vals)
        return contract_id

    @api.model
    def create_user(self):
        user_pool = self.env['res.users']
        field_list = user_pool.fields_get_keys()
        default_vals = user_pool.default_get(field_list)  # This One need for default values needed for create user

        #         name_list = self.name.split()
        #         first_name = name_list[0] or ''
        #         last_name = name_list[-1] or ''
        groups = self.job_id and self.job_id.groups_id
        groups_ids = [group.id for group in groups]
        vals = {'name': self.name,
                'login': self.work_email,
                'email': self.work_email,
                'mobile': self.mobile,
                'image': self.image,
                'is_2fa_enable': True,
                'groups_id': [[6, False, groups_ids]]
                }
        default_vals.update(vals)
        user_id = user_pool.create(default_vals)
        partner_id = user_id.partner_id
        partner_id.write({'employee': True})
        # user_id.action_reset_password()
        #         user_id.write({'groups_id'})
        return user_id

    @api.model
    def action_create_emp_idp(self, emp_id):
        current_year = datetime.now().year
        idp_pool = self.env['employee.idp']
        vals = {
            'employee_id': emp_id.id,
            'idp_year': current_year,
        }
        default_vals.update(vals)
        emp_idp = idp_pool.create(vals)
        return emp_idp

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
    def send_to_employee(self):
        self.state = 'employee'
        self.od_send_mail('od_fill_detail_employee')
        return True

    @api.one
    @api.model
    def send_to_finance(self):
        self.od_send_mail('od_fill_detail_finance')
        self.state = 'finance'
        return True

    @api.one
    @api.model
    def send_hr_welcome_mail(self):
        self.od_send_mail('od_hr_welcome_mail')
        return True

    @api.model
    def attach_doc_emp(self, emp_id):
        for doc_line in self.document_line_ids:
            doc_line.write({
                'employee_id': emp_id.id
            })
        return True

    @api.one
    @api.model
    def confirm_emp(self):
        emp_id = self.create_employee()
        contract_id = self.create_contract(emp_id)
        user_id = self.create_user()
        emp_id.write({'user_id': user_id and user_id.id or False,
                      'address_home_id': user_id.partner_id and user_id.partner_id.id or False})
        self.state = 'confirm'
        self.employee_id = emp_id.id
        self.attach_doc_emp(emp_id)
        self.send_hr_welcome_mail()
        emp_id.audit_set_date()
        if emp_id and self.company_id == 6:
            self.action_create_emp_idp(emp_id)
        if emp_id.job_id.id in (40, 83, 182):
            self.sales_team_id.member_ids = [(4, user_id.id)]
        if emp_id.job_id.id == 161:
            self.create_outsourced_employee()
        return emp_id

    @api.one
    @api.model
    def cancel_emp(self):
        emp_rec = self.env['hr.employee'].search([('name', '=', self.name), ('active', '=', True)])
        emp_rec.write({'active': False})
        contract_rec = self.env['hr.contract'].search([('name', '=', self.name), ('od_active', '=', True)])
        contract_rec.write({'od_active': False})
        users_rec = self.env['res.users'].search([('login', '=', self.work_email), ('active', '=', True)])
        users_rec.write({'active': False})
        self.state = 'cancel'
        return True


class allowance_rule_line(models.Model):
    _inherit = 'allowance.rule.line'
    joining_id = fields.Many2one('od.beta.joining.form', string='Joining ID', ondelete='cascade')


# class hr_payroll_structure(models.Model):
#     _inherit = 'hr.payroll.structure'
#     joining_id = fields.Many2one('od.beta.joining.form', string='Joining ID', ondelete='cascade')

class hr_job(models.Model):
    _inherit = 'hr.job'
    audit_temp_id = fields.Many2one('audit.template', string='Audit Template')
    groups_id = fields.Many2many('res.groups', 'job_res_groups_users_rel', 'uid', 'gid', string='Groups')


class od_hr_employee_document_line(models.Model):
    _inherit = 'od.hr.employee.document.line'
    joining_id = fields.Many2one('od.beta.joining.form', string='Joining ID', ondelete='cascade')


class hr_employee(models.Model):
    _inherit = 'hr.employee'

    @api.one
    @api.depends('name')
    def _compute_cert_line_count(self):
        employee_id = self.id
        doc_ids = []
        document_ids = self.env['od.hr.employee.certificate.line'].search([('employee_id', '=', employee_id)])
        for obj in document_ids:
            doc_ids.append(obj.id)
        if doc_ids:
            self.od_cert_line_count = len(doc_ids)

    @api.one
    @api.depends('name')
    def _compute_appreciation_line_count(self):
        employee_id = self.id
        doc_ids = []
        document_ids = self.env['od.hr.employee.appreciation.line'].search([('employee_id', '=', employee_id)])
        for obj in document_ids:
            doc_ids.append(obj.id)
        if doc_ids:
            self.od_appreciation_line_count = len(doc_ids)

    def od_view_carrier_cert(self, cr, uid, ids, context=None):
        result = self._get_act_window_dict(cr, uid, ids, 'beta_customisation.action_od_hr_cert_lines_tree_view',
                                           context=context)
        return result

    def od_view_appreciation(self, cr, uid, ids, context=None):
        result = self._get_act_window_dict(cr, uid, ids, 'beta_customisation.action_od_hr_appreciation_lines_tree_view',
                                           context=context)
        return result

    od_cert_line_count = fields.Float(string='Count', compute='_compute_cert_line_count')
    od_appreciation_line_count = fields.Float(string='Count', compute='_compute_appreciation_line_count')
