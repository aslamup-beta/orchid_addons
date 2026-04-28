# -*- coding: utf-8 -*-
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import models, fields, api, _
from __builtin__ import True, False
from pickle import FALSE
from openerp.exceptions import Warning


class HrSalaryProfile(models.Model):
    _name = 'hr.salary.profile'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Salary Profile Form for Employees"
    _order = 'create_date desc'
    
    def od_get_company_id(self):
        return self.env.user.company_id
    
    name  = fields.Many2one('hr.employee', string='Name', track_visibility='onchange')
    date = fields.Date(string="Date", default=fields.Date.today())
    state = fields.Selection([('draft', 'Draft'),('valid', 'Validated'), ('cancel', 'Cancelled')],
                                  string='State', readonly=True,
                                  track_visibility='always', copy=False,  default= 'draft')
    name_of_bank = fields.Char(string="Name of Bank")
    nationality = fields.Many2one('res.country', string='Nationality')
    govt_id = fields.Char(string="Government ID No:")
    staff_id = fields.Char(string="Staff ID")
    join_date = fields.Date(string="Date of Joining")
    job_id = fields.Many2one('hr.job', string='Job Title')    
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    basic_salary = fields.Float(string="Basic Salary")
    allowance = fields.Float(string="Allowance")
    housing_allowance = fields.Float(string="Housing Allowance")
    transport_allowance = fields.Float(string="Transportation Allowance")
    total_salary =fields.Float(string="Total Salary")
    passport_no = fields.Char(string="Passport No:")
    ref_to = fields.Char(string="Make Reference To (English)", default = "To Whom It May Concern")
    ref_to_ar = fields.Char(string="Make Reference To (Arabic)", default = "من يهمه الأمر")
    phrase = fields.Text(string="Phrase (Arabic)", default = "نشهد نحن / شركة دار بيتا لتكنولوجيا المعلومات بأن الموظف المذكور بياناته لا يزال يعمل لدينا وتحت كفالتنا حتى تاريخه، وقد أعطي هذا الخطاب بناء على طلبه دون أدنى مسؤولية على الشركة")
    phrase_en = fields.Text(string="Phrase (English)", default = "We hereby confirm that the employee mentioned in this letter is still employed with us as of the present date. This letter is issued based on his request, and the company bears no responsibility in this regard.")
    print_type = fields.Selection([('en', 'English'),('ar', 'Arabic'), ('both', 'Both English and Arabic')], string='Type', default= 'both')
    
    def _get_contract_obj(self):
        employee_id = self.name and self.name.id or False
        res =self.env['hr.contract'].search([('od_active','=',True),('employee_id','=',employee_id)],limit=1)
        if self.name and self.name.active == False:
            res =self.env['hr.contract'].search([('employee_id','=',employee_id)], order='id desc')[0]
        return res
    
    def _get_allowances(self):
        contract = self._get_contract_obj()
        result = 0.0
        for line in contract.xo_allowance_rule_line_ids:
            if line.code=='OA':
                result += line.amt
            if line.code=='ALW':
                result += line.amt
        return result

    def _get_house_allowances(self):
        contract = self._get_contract_obj()
        result = 0.0
        for line in contract.xo_allowance_rule_line_ids:
            if line.code=='KSA_HA':
                result += line.amt
            if line.code=='HA':
                result += line.amt
        return result

    def _get_transport_allowances(self):
        contract = self._get_contract_obj()
        result = 0.0
        for line in contract.xo_allowance_rule_line_ids:
            if line.code=='KSA_TA':
                result += line.amt
        return result
        
        
    
    @api.onchange('name')
    def onchange_name(self):
        contract_obj = self._get_contract_obj()
        employee = self.name or False
        if employee:
            self.job_id= employee.job_id and employee.job_id.id or False
            self.nationality= employee.country_id and employee.country_id.id or False
            self.govt_id = employee.identification_id or False
            self.staff_id = employee.od_identification_no or False
            self.join_date = employee.od_joining_date or False
            self.allowance = self._get_allowances()
            self.housing_allowance = self._get_house_allowances()
            self.transport_allowance = self._get_transport_allowances()
            self.basic_salary = contract_obj.wage
            self.total_salary = contract_obj.wage + self._get_allowances() + self._get_house_allowances() + self._get_transport_allowances()
            self.passport_no = employee.passport_id or False
            if not (self.staff_id and self.govt_id and self.passport_no):
                raise Warning("Dear HR Team, Kindly update below missing information in Employee profile before creating this document.\n  a)Government ID \n b)Staff No \n b)Passport No")
    
    
    @api.one
    @api.model
    def validate(self):
        self.state = 'valid'
        return True
    
    @api.one
    @api.model
    def cancel(self):
        self.state = 'cancel'
        return True
    
