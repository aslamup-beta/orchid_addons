# -*- coding: utf-8 -*-
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

from openerp import models, fields, api, _
 
class BetaRoleChangeForm(models.Model):
    _name = 'od.beta.role.change.form'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Beta RoleChange Form"
    _rec_name = 'employee_id'
    
    def od_get_company_id(self):
        return self.env.user.company_id
    
    employee_id  = fields.Many2one('hr.employee', string='Name of Employee', track_visibility='onchange')
    state = fields.Selection([('draft', 'Start'),('approval1', 'First Approval'),('confirm', 'Confirmed'), ('cancel', 'Refused')],
                                  string='State', readonly=True,
                                  track_visibility='always', copy=False,  default= 'draft')
    department_id = fields.Many2one('hr.department', string='Department') 
    job_id = fields.Many2one('hr.job', string='Job Title')
#     last_day_date = fields.Date(string='Last Day At Work', track_visibility='onchange',copy=False)
    branch_id = fields.Many2one('od.cost.branch', string='Branch')
    parent_id = fields.Many2one('hr.employee', string='Manager')
    coach_id = fields.Many2one('hr.employee', string='Coach')
    tech_dept_id = fields.Many2one('od.cost.division', string='Technology Unit')
    cost_centre_id = fields.Many2one('od.cost.centre', string='Cost Centre')
    manager1_id = fields.Many2one('res.users', string='First Approval Manager')
    manager2_id = fields.Many2one('res.users', string='Second Approval Manager')
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    
    #New fields for the new roles
    n_department_id = fields.Many2one('hr.department', string='Department')
    n_job_id = fields.Many2one('hr.job', string='Job Title')
    n_branch_id = fields.Many2one('od.cost.branch', string='Branch')
    n_parent_id = fields.Many2one('hr.employee', string='Manager')
    n_coach_id = fields.Many2one('hr.employee', string='Coach')
    n_tech_dept_id = fields.Many2one('od.cost.division', string='Technology Unit')
    n_cost_centre_id = fields.Many2one('od.cost.centre', string='Cost Centre')
    n_manager1_id = fields.Many2one('res.users', string='First Approval Manager')
    n_manager2_id = fields.Many2one('res.users', string='Second Approval Manager')
    notes = fields.Text("Notes")
    
    @api.onchange('employee_id')
    def onchange_employee_id(self):
        employee = self.employee_id or False
        if employee:
            self.department_id= employee.department_id and employee.department_id.id or False
            self.job_id= employee.job_id and employee.job_id.id or False
            self.branch_id= employee.od_branch_id and employee.od_branch_id.id or False
            self.tech_dept_id= employee.od_division_id and employee.od_division_id.id or False
            self.cost_centre_id = employee.od_cost_centre_id and employee.od_cost_centre_id.id or False
            self.parent_id = employee.parent_id and employee.parent_id.id or False
            self.coach_id = employee.coach_id and employee.coach_id.id or False
            self.manager1_id=  employee.od_first_manager_id and employee.od_first_manager_id.id or False
            self.manager2_id= employee.od_second_manager_id and employee.od_second_manager_id.id or False
        
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
    def submit(self):
        self.od_send_mail('od_role_change_approval')
        self.state = 'approval1'
        return True
    
    @api.model
    def create(self,vals):
        res = super(BetaRoleChangeForm, self).create(vals)
        res.submit()
        return res
    
    @api.one
    @api.model
    def first_approval(self):
        employee = self.employee_id or False
        if self.n_department_id:
            employee.write({'department_id': self.n_department_id.id})
        if self.n_job_id:
            employee.write({'job_id': self.n_job_id.id})
        if self.n_branch_id:
            employee.write({'od_branch_id':self.n_branch_id.id})
        if self.n_tech_dept_id:
            employee.write({'od_division_id': self.n_tech_dept_id.id})
        if self.n_cost_centre_id :
            employee.write({'od_cost_centre_id': self.n_cost_centre_id.id})
        if self.n_parent_id :
            employee.write({'parent_id': self.n_parent_id.id})
        if self.n_coach_id:
            employee.write({'coach_id': self.n_coach_id.id})
        if self.n_manager1_id:
            employee.write({'od_first_manager_id': self.n_manager1_id.id})
        if self.n_manager2_id:
            employee.write({'od_second_manager_id': self.n_manager2_id.id})
        self.od_send_mail('od_role_change_notify_all')
        self.state = 'confirm'
        return True
    
    @api.one
    @api.model
    def refuse(self):
        self.state = 'cancel'
        return True
    