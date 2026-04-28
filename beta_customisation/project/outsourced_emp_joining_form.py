# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning
from datetime import date, timedelta,datetime

class outsource_employee_join_form(models.Model):
    _name = "outsource.employee.join.form"
    _description = "Outsource Employee Joining Form"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    
    def od_get_company_id(self):
        return self.env.user.company_id
    
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
    
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    name = fields.Char(string="Employee Name")
    profession_id = fields.Many2one('hr.job', 'Profession')
    customer_id = fields.Many2one('res.partner', 'Customer')
    so_id = fields.Many2one('sale.order', 'Sales Order')
    analytic_id = fields.Many2one('account.analytic.account',string="Analytic Account")
    costsheet_id = fields.Many2one('od.cost.sheet', 'Cost Sheet')
    tech_unit = fields.Many2one('od.cost.division', 'Technology Unit')
    proj_manager = fields.Many2one('res.users', 'Project Manager')
    sponsorship = fields.Many2one('res.partner', 'Sponsorship')
    join_date = fields.Date(string="Customer Joining Date")
    end_date = fields.Date(string="Customer Contract End Date")
    employee_end_date = fields.Date(string="Employee Contract End Date")
    salary_proposed = fields.Float('Monthly Salary', help="Salary Proposed by the Organisation")
    personal_email = fields.Char('Personal Email', size=128, help="Personal Email of the outsourced emloyee")
    work_email = fields.Char('Work Email', size=128, help="Work Email of the outsourced emloyee")
    description = fields.Text(string="Additional Notes")
    mobile_phone = fields.Char(string="Mobile")
    od_document_line_ids = fields.One2many('od.hr.employee.document.line', 'outsource_joining_id', string='Document Lines')
    state = fields.Selection([('draft', 'Start'), ('finance', 'HR'),('confirm', 'Confirmed'), ('cancel', 'Cancelled')],
                                  string='State', readonly=True,
                                  track_visibility='always', copy=False,  default= 'draft')
    
    @api.onchange('costsheet_id')
    def onchange_costsheet_id(self):
        costsheet_id = self.costsheet_id or False
        if costsheet_id:
            self.customer_id= costsheet_id.od_customer_id and costsheet_id.od_customer_id.id or False
            self.tech_unit= costsheet_id.od_division_id and costsheet_id.od_division_id.id or False
            self.proj_manager = costsheet_id.reviewed_id and costsheet_id.reviewed_id.id or False
            self.so_id = costsheet_id.od_mat_sale_id and costsheet_id.od_mat_sale_id.id or False
    
    def get_emp_vals(self):
        vals = { 'name' : self.name,
                'profession_id': self.profession_id and self.profession_id.id or False,
                'customer_id': self.customer_id and self.customer_id.id or False,
                'so_id': self.so_id and self.so_id.id or False,
                'costsheet_id':self.costsheet_id and self.costsheet_id.id or False,
                'tech_unit': self.tech_unit and self.tech_unit.id or False,
                'proj_manager': self.proj_manager and self.proj_manager.id or False,
                'sponsorship': self.sponsorship and self.sponsorship.id or False,
                'join_date': self.join_date or False,
                'end_date': self.end_date or False,
                'employee_end_date': self.employee_end_date or False,
                'salary_proposed': self.salary_proposed or False,
                'personal_email': self.personal_email or False,
                'work_email': self.work_email or False,
                'description': self.description or False,
                'mobile_phone': self.mobile_phone or False,
                'image': self.image or False,
                'active': True
            }
        return vals
    
    @api.model
    def create_om_analytics(self,emp_id):
        analytic_id = self.analytic_id
        line_vals={'start_date':analytic_id.date_start,'end_date':analytic_id.od_date_end_original,'analytic_id':analytic_id.id,'outsource_id':emp_id.id}
        self.env['od.outsource.analytics'].create(line_vals)
        return True

    
    @api.model
    def attach_doc_emp(self, emp_id):
        model = self.env['od.attachement']
        for doc_line in self.od_document_line_ids:
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
    def create_employee(self):
        employee_pool = self.env['outsource.employee']
        vals = self.get_emp_vals()
        emp_id = employee_pool.create(vals)
        self.attach_doc_emp(emp_id)
        self.create_om_analytics(emp_id)
        return emp_id
    
    @api.one
    @api.model
    def send_to_finance(self):
        self.od_send_mail('od_approve_outsource_mail_finance')
        self.state = 'finance'
        return True
    
    @api.one
    @api.model
    def confirm_out_emp(self):
        emp_id = self.create_employee()
        self.state = 'confirm'
        self.od_send_mail('od_approved_outsource_mail_project')
        return emp_id
        
    @api.one
    @api.model
    def cancel_form(self):
        self.state = 'cancel'
        return True
    
    
    
class od_hr_employee_document_line(models.Model):
        
    _inherit = 'od.hr.employee.document.line'
    outsource_joining_id = fields.Many2one('od.beta.joining.form', string='Outsource Joining ID', ondelete='cascade')
    
    