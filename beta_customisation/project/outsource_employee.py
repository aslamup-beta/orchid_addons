# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning
from datetime import date, timedelta,datetime

class outsource_employee(models.Model):
    _name = "outsource.employee"
    _description = "Outsource Employee"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    
    def od_get_company_id(self):
        return self.env.user.company_id
    
    @api.one
    def _od_attachement_count(self):
        for obj in self:
            attachement_ids = self.env['od.attachement'].search([('model_name', '=', self._name),('object_id','=',obj.id)])
            if attachement_ids:
                self.od_attachement_count = len(attachement_ids)
    
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    name = fields.Char(string="Employee Name")
    profession_id = fields.Many2one('hr.job', 'Profession')
    customer_id = fields.Many2one('res.partner', 'Customer')
    so_id = fields.Many2one('sale.order', 'Sales Order')
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
    od_attachement_count = fields.Integer(string="Attachement Count",compute="_od_attachement_count")
    active = fields.Boolean(string="Active")
    om_analytic_line = fields.One2many('od.outsource.analytics','outsource_id',string='OM Analytic Lines',copy=False)
    
    def od_open_attachement(self,cr,uid,ids,context=None):

        model_name=self._name
        object_id = ids[0]
        domain = [('model_name','=',model_name),('object_id','=',object_id)]
        ctx = {'default_model_name':model_name,'default_object_id':object_id}
        return {
            'domain': domain,
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'od.attachement',
            'type': 'ir.actions.act_window',
            'context':ctx
                }
    
class od_outsource_analytics(models.Model):
    _name = 'od.outsource.analytics'
    
    outsource_id = fields.Many2one('outsource.employee',string='Cost Sheet')
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    analytic_id = fields.Many2one('account.analytic.account',string="Analytic Account")
    state = fields.Selection(string ='State', related='analytic_id.state')
    so_id = fields.Many2one('sale.order',string="Sales Order")

    
    
    