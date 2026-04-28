# -*- coding: utf-8 -*-
from openerp import models, fields, api
from pprint import pprint
from datetime import datetime
import openerp.addons.decimal_precision as dp


class sales_commit_wiz(models.TransientModel):
    _name = 'sales.commit.rpt.wiz'
    
    sam_ids = fields.Many2many('res.users','supply_wiz_sam_rel_vfs','wiz_id','user_id',string="Sales Account Manager")
    wiz_line = fields.One2many('sales.commit.rpt.data','wiz_id',string="Wiz Line")
    def od_get_company_id(self):
        return self.env.user.company_id
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    
    
    
    def get_vals(self):
        result = []
        commit_line = self.env['commit.gp.sample.line']
        user_ids =[pr.id for pr in self.sam_ids]
        company_id = self.company_id.id
        sample_obj = self.env['audit.sample']
        sample_dat  = sample_obj.search([('company_id','=',company_id)])
        sample_ids = [ss.id for ss in sample_dat]
        domain = [('sample_id','in',sample_ids)]
        if user_ids:
            domain +=[('user_id','in',user_ids)]
        commit_lines = commit_line.search(domain)
        
        for line in commit_lines:
            user_id = line.user_id and line.user_id.id 
            if not user_id:
                user_id = line.sample_id and line.sample_id.employee_id and line.sample_id.employee_id.user_id and line.sample_id.employee_id.user_id.id or False
            result.append((0,0,{
                    'sam_id':user_id, 
                    'gp':line.gp,
                    'od_cost_sheet_id':line.cost_sheet_id and line.cost_sheet_id.id or False,
#                     'opp_id':line.cost_sheet_id and line.cost_sheet_id.lead_id and line.cost_sheet_id.lead_id.id or False,
                    'stage_id':line.cost_sheet_id and line.cost_sheet_id.lead_id and line.cost_sheet_id.lead_id.stage_id and line.cost_sheet_id.lead_id.stage_id.id or False,
                    'partner_id':line.cost_sheet_id and line.cost_sheet_id.od_customer_id and line.cost_sheet_id.od_customer_id.id or False,
                    'aud_date_start':line.sample_id and line.sample_id.date_start or False,
                    'aud_date_end':line.sample_id and line.sample_id.date_end or False
                    
                    
                    }))
        return result
 
    @api.multi 
    def export_rpt(self):
        result = self.get_vals()
        self.wiz_line.unlink()
        self.write({'wiz_line':result})
        return {
            'domain': [('wiz_id','=',self.id)],
            'name': 'Sales Commit Report',
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'sales.commit.rpt.data',
            'type': 'ir.actions.act_window',
            'context':{'search_default_audit_end':1,'search_default_sam':1,}
        }
    
class sales_commit_rpt_data(models.TransientModel):
    _name = 'sales.commit.rpt.data'
    wiz_id = fields.Many2one('sales.commit.rpt.wiz',string="Wizard")
    company_id = fields.Many2one('res.company',string="Company")
    sam_id = fields.Many2one('res.users',string="Sale Account Manager")
    opp_id = fields.Many2one('crm.lead',string='Opportunity')
    partner_id = fields.Many2one('res.partner',string="Customer")
    stage_id = fields.Many2one('crm.case.stage',string="Current Stage")
    gp = fields.Float(string='GP')
    od_cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet')
    aud_date_start = fields.Date(string="Audit Date Start")
    aud_date_end = fields.Date(string="Audit Date End")
    

    
