# -*- coding: utf-8 -*-
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import models, fields, api, _

class hr_applicant(models.Model):
    _inherit = "hr.applicant"
    
    beta_join_id = fields.Many2one('od.beta.joining.form',string="Beta Joining Form")
    od_manager_id = fields.Many2one('hr.employee', string="Manager")
    od_father_name = fields.Char(string="Father Name")
    od_passport_no = fields.Char(string="Passport Number")
    od_nationality = fields.Many2one('res.country', string='Nationality')
    od_dob = fields.Date(string='Date of Birth')
    od_gender = fields.Selection([('male', 'Male'), ('female', 'Female')], 'Gender')
    od_marital = fields.Selection([('single', 'Single'), ('married', 'Married'),('widower', 'Widower'),('divorced', 'Divorced')], 'Martial Status')
    od_place_of_birth =fields.Char(string="Place of Birth")
    
    od_work_email = fields.Char(string='Work Email')
    od_place_of_birth =fields.Char(string="Place of Birth")
    od_manager_id = fields.Many2one('hr.employee', string='Manager')
    od_coach_id = fields.Many2one('hr.employee', string='Coach')
    od_joining_date = fields.Date(string='Joining Date', track_visibility='onchange')
    
    od_branch_id = fields.Many2one('od.cost.branch', string='Branch')
    od_tech_dept_id = fields.Many2one('od.cost.division', string='Technology Unit/Department')
    od_cost_centre_id = fields.Many2one('od.cost.centre', string='Cost Centre')
    od_pay_salary_during_annual_leave = fields.Boolean('Pay Salary During Annual Leave')
    
    od_type_id = fields.Many2one('hr.contract.type', string='Contract Type')
    od_mode_of_pay_id = fields.Many2one('od.mode.of.payment', string='Mode of Payment')
    od_total_wage = fields.Float(string="Total Wage")
    od_basic_wage = fields.Float(string="Basic Wage")
    od_allowance_rule_line_ids = fields.One2many('allowance.rule.line','applicant_id','Rule Lines')
    od_salary_struct = fields.Many2one('hr.payroll.structure', string='Salary Structure')
    od_analytic_account_id = fields.Many2one('account.analytic.account',string="Analytic Account")
    
    od_work_sched = fields.Many2one('resource.calendar', string='Working Schedule')
    od_manager1_id = fields.Many2one('res.users', string='First Approval Manager(Leaves)')
    od_manager2_id = fields.Many2one('res.users', string='Second Approval Manager(Leaves)')
    
    first_interview_date = fields.Datetime(string='Second Interview Date')
    second_interview_date = fields.Datetime(string='Second Interview Date')
    feedback1 = fields.Text(string='First Interview Feedback')
    feedback2 = fields.Text(string='Second Interview Feedback')

    
    def od_send_mail(self,template):
        ir_model_data = self.env['ir.model.data']
        email_obj = self.pool.get('email.template')
        saudi_comp =6
        user_company_id = self.env.user.company_id.id
        if user_company_id == saudi_comp:
            template = template +'_saudi'
        template_id = ir_model_data.get_object_reference('beta_customisation', template)[1]
        crm_id = self.id
        email_obj.send_mail(self.env.cr,self.env.uid,template_id,crm_id, force_send=True)
        return True
    
    @api.one
    def proceed_for_second_intrvw(self):
        pass
    
    @api.one
    def reject_by_1st_interviwer(self):
        pass
    
    @api.one
    def create_joining_form(self):
        """ Create an od.beta.joining.form from the hr.applicants """
        beta_joining_form = self.env['od.beta.joining.form']
        model_data = self.env['ir.model.data']
        act_window = self.env['ir.actions.act_window']
        emp_id = False
        for applicant in self:
            beta_join_id = beta_joining_form.create({'name': applicant.partner_name,
                                                     'personal_email': applicant.email_from,
                                                     'job_id': applicant.job_id and applicant.job_id.id or False,
                                                     'department_id': applicant.department_id and applicant.department_id.id or False,
                                                     'manager_id': applicant.manager_id and applicant.manager_id.id or False
                                                 })
            self.write({'beta_join_id': beta_join_id.id})
            self.od_send_mail('od_fill_detail_employee')
            return beta_join_id
        
class allowance_rule_line(models.Model):
    _inherit = 'allowance.rule.line'
    
    applicant_id = fields.Many2one('od.beta.joining.form', string='Applicant ID', ondelete='cascade')
    
    
    