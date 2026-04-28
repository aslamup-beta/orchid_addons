# -*- coding: utf-8 -*-
from openerp import models, fields, api
from pprint import pprint
from datetime import datetime
import openerp.addons.decimal_precision as dp


class pmo_analytic_rpt(models.TransientModel):
    _name = 'pmo.anal.rpt.wiz'
    
#     branch_ids= fields.Many2many('od.cost.branch',string="Branch")
#     cost_centre_ids = fields.Many2many('od.cost.centre',string="Cost Center")
#     division_ids = fields.Many2many('od.cost.division',string="Technology Unit")
    
    date_start_from = fields.Date(string="Analytic Starting Date From")
    date_start_to = fields.Date(string="Analytic Starting Date To")
        
    closing_date_from = fields.Date(string="Analytic Closing Date From")
    closing_date_to = fields.Date(string="Analytic Closing Date To")
    
    prj_status = fields.Selection([('open','Open'),('closed','Closed (Excluding fully collected from Customer and fully paid to Supplier)')],'Project Status')
    wiz_line = fields.One2many('pmo.anal.rpt.data','wiz_id',string="Wiz Line")
    
    def od_get_company_id(self):
        return self.env.user.company_id
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    
    
    
    @api.multi
    def export_rpt(self):
        result  = []
        company_id = self.company_id and self.company_id.id 
        domain = [('company_id','=',company_id)]
        date_start_from = self.date_start_from 
        date_start_to = self.date_start_to 
        closing_date_from = self.closing_date_from 
        closing_date_to = self.closing_date_to
        if date_start_from:
            domain += [('date_start','>=',date_start_from)]
        
        if date_start_to:
            domain += [('date_start','<=',date_start_to)]
            
        if closing_date_from:
            domain += [('od_closing_date','>=',closing_date_from)]
        
        if closing_date_to:
            domain += [('od_closing_date','<=',closing_date_to)]
        
        analytic_ob=self.env['account.analytic.account'].search(domain)
        analytic_ids = [ob.id for ob in analytic_ob]
        audit_temp_id=14
        if company_id ==6:
            audit_temp_id =9
        
            
        
        sample_id = self.env['audit.sample'].search([('aud_temp_id','=',audit_temp_id)])
        samp_id =sample_id[-1].id
        obj_model = 'pmo.closed.project.sample'
        if self.prj_status =='open':
            obj_model = 'pmo.open.project.sample'
        datas = self.env[obj_model].search([('sample_id','=',samp_id),('analytic_id','in',analytic_ids)])
        for dat in datas:
            result.append((0,0,{
                'analytic_id':dat.analytic_id and dat.analytic_id.id or False,
                'paid':dat.paid,
                'manpower_cost':dat.manpower_cost,
                'general_cost':dat.general_cost,
                'collected':dat.collected,
                'project_value':dat.project_value,
                'inv_amount':dat.inv_amount,
                
                }))
        self.wiz_line.unlink()
        self.write({'wiz_line':result})
        del(result)
        return {
            'domain': [('wiz_id','=',self.id)],
            'name': 'Revenue Report',
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'pmo.anal.rpt.data',
            'type': 'ir.actions.act_window',
        }
        

class pmo_analytic_rpt_data(models.TransientModel):
    _name = 'pmo.anal.rpt.data'
    wiz_id = fields.Many2one('pmo.anal.rpt.wiz',string="Wizard")
    analytic_id = fields.Many2one('account.analytic.account',string="Analytic/Project")
    paid = fields.Float(string="Paid to Supplier")
    manpower_cost = fields.Float(string="Manpower Cost")
    general_cost =fields.Float(string="General Cost")
    collected = fields.Float(string="Collected From Customer")
    project_value = fields.Float(string="Project Value")
    inv_amount = fields.Float(string="Invoice Value")

    
    @api.multi
    def btn_open_analytic(self):
       
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.analytic.account',
                'res_id':self.analytic_id and self.analytic_id.id or False,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }
