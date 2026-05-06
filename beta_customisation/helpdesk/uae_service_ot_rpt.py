# -*- coding: utf-8 -*-
from openerp import models, fields, api
from pprint import pprint
from datetime import datetime
import openerp.addons.decimal_precision as dp

class uae_service_team_ot_rpt(models.TransientModel):
    _name = 'uae.ot.rpt.wiz'
    
    @api.model
    def get_technicians(self):
        emp_rel = self.env['hr.employee'].search([('job_id','=',44)])
        emp_ids = []
        for emp_id in emp_rel:
            emp_ids.append(emp_id.user_id.id)
        return self.env['res.users'].search([('id', 'in', emp_ids)]).ids
    
    wiz_line = fields.One2many('uae.ot.rpt.data','wiz_id',string="Wiz Line")
    
    date_start = fields.Date(string="Tickets From")
    date_end =fields.Date(string="Tickets To")
    user_ids = fields.Many2many('res.users',string="Technicians",default=get_technicians)
    
    def od_get_company_id(self):
        return self.env.user.company_id
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    
    @api.multi 
    def export_rpt(self):
        model_data = self.env['ir.model.data']
        tree_view = model_data.get_object_reference( 'beta_customisation', 'od_service_team_ot_tree_view')
        
        user_ids = [pr.id for pr in self.user_ids]
        date_start = self.date_start
        date_end =self.date_end
        
        wiz_id = self.id
        company_id = self.company_id and self.company_id.id 
        domain =[('od_stage','=','done')]
        if company_id:
            domain += [('company_id','=',company_id)]
        if user_ids:
            domain += [('user_id','in',user_ids)]
        if date_start:
            domain += [('date_start','>=',date_start)]
        if date_end:
            domain += [('date_end','<=',date_end)]
            
        result =[]
        for user in user_ids:
            
            task_data = self.env['project.task'].search(domain)
            normal_ot = 0.0 
            friday_ot= 0.0
            overnight_ot = 0.0 
            holiday_ot = 0.0
            emp_rel = self.env['hr.employee'].search([('user_id','=',user)])
            staff_no = emp_rel.od_identification_no
            contract = self.env['hr.contract'].search([('employee_id','=',emp_rel.id),('od_active','=',True)])
            hourly_rate = (contract.wage/30)/8 or 0.0
            for data in task_data:
                if data.user_id.id == user:
                    normal_ot += data.od_normal_ot
                    friday_ot += data.od_friday_ot
                    overnight_ot += data.od_overnight_ot
                    holiday_ot += data.od_holiday_ot
            total_hrs = normal_ot + friday_ot + overnight_ot + holiday_ot
            total_amt = (1.25 * hourly_rate *normal_ot) + (1.50 * hourly_rate *friday_ot) + (1.50 * hourly_rate *overnight_ot) + (1.50 * hourly_rate *holiday_ot)
            result.append((0,0,{
                    'wiz_id':wiz_id,
                    'name':user,
                    'staff_no': staff_no,
                    'normal_ot': normal_ot,
                    'friday_ot':friday_ot,
                    'overnight_ot': overnight_ot,
                    'holiday_ot': holiday_ot,
                    'total_hrs':total_hrs,
                    'total_amt':total_amt
                    }))
        
        self.wiz_line.unlink()
        self.write({'wiz_line':result})
        
        return {
            'domain': [('wiz_id','=',wiz_id)],
            'name': 'UAE Service Team OT Report',
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(tree_view and tree_view[1] or False, 'tree')],
            'res_model': 'uae.ot.rpt.data',
            'type': 'ir.actions.act_window',
        }

                        
class uae_service_team_ot_rpt_data_wiz(models.TransientModel):
    _name = 'uae.ot.rpt.data'
    
    wiz_id = fields.Many2one('uae.ot.rpt.wiz',string="Wizard")
    staff_no = fields.Char('Staff#')
    name = fields.Many2one('res.users',string="Name")
    normal_ot = fields.Float(string="Normal OT")
    friday_ot = fields.Float(string="Sunday OT")
    overnight_ot = fields.Float(string="Overnight OT")
    holiday_ot = fields.Float(string="Holiday OT")
    total_hrs = fields.Float(string="Total Hours")
    total_amt = fields.Float(string="Total Amount")

    