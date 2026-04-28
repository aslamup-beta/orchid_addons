# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2013 Camptocamp (<http://www.camptocamp.com>)
#    Authors: Ferdinand Gasauer, Joel Grand-Guillaume
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
##############################################################################

from openerp import models, fields, api
from openerp.tools.translate import _
from openerp.exceptions import Warning
from datetime import datetime

class customer_visit_report(models.Model):
    _name ='customer.visit.report'
    _description = "Customer Visit Report"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'id desc'
    
    def od_get_company_id(self):
        return self.env.user.company_id
    
    name = fields.Char('Description')
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    employee_id = fields.Many2one('hr.employee','Requested by')
    manager_id = fields.Many2one('res.users','Approval Manager')
    visit_line_ids = fields.One2many('customer.visit.log.line','approval_form_id', "Customer Visit Logs" )
    state = fields.Selection([('draft','Draft'),('approval1','Pending Approval'),('done','Approved'),('reject','Rejected')],string="Status", default="draft")
    
    @api.onchange('employee_id')
    def onchange_employee_id(self):
        employee = self.employee_id or False
        if employee:
            self.manager_id= employee.sudo().parent_id and employee.sudo().parent_id.user_id and employee.sudo().parent_id.user_id.id or False
    
    def od1_send_mail(self,template):
        ir_model_data = self.env['ir.model.data']
        email_obj = self.pool.get('email.template')
        template_id = ir_model_data.get_object_reference('beta_customisation', template)[1]
        rec_id = self.id
        email_obj.send_mail(self.env.cr,self.env.uid,template_id,rec_id, force_send=True)
    
    @api.one
    def submit_to_manager(self):
        if len(self.visit_line_ids.ids) < 1 :
            raise Warning("At least 1 line needed to submit")
        self.write({'state':'approval1'})
        self.od1_send_mail('send_mail_customer_visit_approval')
    
    @api.one
    def btn_done(self):
        if self.env.user.id == self.employee_id.user_id.id:
            raise Warning("You Cannot Approve Customer visits, Please Ask your Manager to do it..")
        for line in self.visit_line_ids:
            line.write({'status':'done'})
        self.write({'state':'done'})
    
    @api.one
    def btn_reject(self):
        self.write({'state':'reject'})
    
class customer_visit_log_line(models.Model):
    _name ='customer.visit.log.line'
    _order = 'date desc'
    
    def od_get_company_id(self):
        return self.env.user.company_id

    approval_form_id = fields.Many2one('customer.visit.report','Approval Form', ondelete="cascade")
    assigned_id = fields.Many2one('res.users', 'Solutions Architect')
    sam = fields.Many2one('res.users', 'Sales Account Manager')
    partner_id = fields.Many2one('res.partner', 'Customer')
    date = fields.Date(string="Date of Visit")
    visit_type = fields.Selection([('on_site','On-Site'),('online','Online')],string="Visit Type")
    activity_type = fields.Selection([('a','Presentation'),('b','POC'),('c','Technical Workshop'),('d','Proposal Discussion'),('e','Site Survey'),('f','Writing RFP'),('g','General Discussion')],string="Activity Type")
    business_req = fields.Selection([('yes','Yes'),('no','No')],string="Business Requirement?")
    notes = fields.Text(string="SA Feedback")
    status = fields.Selection([('draft','Draft'),('done','Approved'),('reject','Rejected')],string="Status", default="draft")
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)        
            
    
    