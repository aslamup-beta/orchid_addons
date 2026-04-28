# -*- coding: utf-8 -*-
from openerp import models, fields, api
from pprint import pprint
from datetime import datetime
import openerp.addons.decimal_precision as dp

class sla_perfomance_rpt_wiz(models.TransientModel):
    _name = 'sla.perf.rpt.wiz'
    
    wiz_line = fields.One2many('wiz.sla.perf.data','wiz_id',string="Wiz Line")
    
    project_ids = fields.Many2many('project.project','wiz_proj_x','wiz_id','user_id',string="Projects",domain=[('od_type_of_project','=','amc')])    
    
    def od_get_company_id(self):
        return self.env.user.company_id
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    
    @api.multi 
    def export_rpt(self):
        wiz_id = self.id
        model_data = self.env['ir.model.data']
        tree_view = model_data.get_object_reference( 'beta_customisation', 'od_sla_perf_tree_view')
        
        project_ids = [pr.id for pr in self.project_ids]
         
        wiz_id = self.id
        company_id = self.company_id and self.company_id.id 
        domain =[('state','=','done')]
        if company_id:
            domain += [('company_id','=',company_id)]
        if project_ids:
            domain += [('od_project_id2','in',project_ids)]
            
        helpdesk_data = self.env['crm.helpdesk'].search(domain) 
        result =[]
        for data in helpdesk_data:
            
            name = data.name 
            created_on = data.create_date
            close_date = data.close_date 
            responsible = data.user_id and data.user_id.id
            customer = data.od_organization_id and data.od_organization_id.id
            sla_status = data.od_closing_status
            actual_time = data.actual_time
            resol_time =data.sla_resol_time
            result.append((0,0,{
                                'wiz_id':wiz_id,
                                'name':name,
                                'create_date': created_on,
                                'close_date': close_date,
                                'responsible':responsible,
                                'customer': customer,
                                'od_closing_status': sla_status,
                                'resol_time':resol_time,
                                'actual_time':actual_time
                                }))
        
        self.wiz_line.unlink()
        self.write({'wiz_line':result})
        
        return {
            'domain': [('wiz_id','=',wiz_id)],
            'name': 'SLA Performance Report',
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(tree_view and tree_view[1] or False, 'tree')],
            'res_model': 'wiz.sla.perf.data',
            'context':{'search_default_close':1},
            'type': 'ir.actions.act_window',
        }

                        
class sla_perfomance_data_wiz(models.TransientModel):
    _name = 'wiz.sla.perf.data'
    
    wiz_id = fields.Many2one('sla.perf.rpt.wiz',string="Wizard")
    name = fields.Char('Name')
    created_on = fields.Date(string="Creation Date")
    close_date = fields.Date(string="Close Date")
    customer = fields.Many2one('res.partner',string="Customer")
    responsible = fields.Many2one('res.users',string="Responsible")
    od_closing_status = fields.Selection([('ok','OK'),('not_ok','Not OK'),('not_available','Not Available')],string="SLA Status")
    actual_time = fields.Float(string="Actual Time")
    resol_time = fields.Float(string="Resolution Time")

    