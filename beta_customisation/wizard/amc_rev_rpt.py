# -*- coding: utf-8 -*-
from openerp import models, fields, api
from pprint import pprint
from datetime import datetime
import openerp.addons.decimal_precision as dp


class amc_rev_rpt_wiz(models.TransientModel):
    _name = 'amc.rev.rpt.wiz'
    
    branch_ids= fields.Many2many('od.cost.branch',string="Branch")
    approved_date_from = fields.Date(string="Project Approved Date From")
    approved_date_to = fields.Date(string="Project Approved Date To")
    wiz_line = fields.One2many('amc.rev.rpt.data','amc_wiz_id',string="Wiz Line")

    def od_get_company_id(self):
        return self.env.user.company_id
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    
    def get_amc_vals(self):
        branch_ids = [pr.id for pr in self.branch_ids]
        wiz_id = self.id
        date_start_from = self.approved_date_from
        date_start_to = self.approved_date_to 
        company_id = self.company_id and self.company_id.id
        domain = [('od_type_of_project','=','amc'),('type','!=','view'),('od_analytic_level','=','level_old')]
        if company_id:
            domain += [('company_id','=',company_id)]
        if branch_ids:
            domain += [('od_branch_id','in',branch_ids)]
        if date_start_from:
            domain += [('fin_approved_date','>=',date_start_from)]
        if date_start_to:
            domain += [('fin_approved_date','<=',date_start_to)]
    
        domain2 = [('od_type_of_project','=','amc'),('type','!=','view'),('od_analytic_level','!=','level_old')]
        if company_id:
            domain2 += [('company_id','=',company_id)]
        
        if branch_ids:
            domain2 += [('od_branch_id','in',branch_ids)]
        
        if date_start_from:
            domain2 += [('fin_approved_date','>=',date_start_from)]
        if date_start_to:
            domain2 += [('fin_approved_date','<=',date_start_to)]
            
        result =[]
       
        project_data = self.env['project.project'].search(domain) 
        
        for data in project_data:
            project_id = data.id
            partner_id = data.partner_id and data.partner_id.id 
            company_id = data.company_id and data.company_id.id 
            branch_id = data.od_branch_id and data.od_branch_id.id
            od_cost_sheet_id = data.od_cost_sheet_id and data.od_cost_sheet_id.id
            approved_date =data.od_cost_sheet_id and data.od_cost_sheet_id.approved_date or False
            contract_status = data.state
            result.append((0,0,{
                              'approved_date':approved_date,
                                'amc_wiz_id':wiz_id,
                                'cost_sheet_id':od_cost_sheet_id, 
                                'partner_id':partner_id,
                                'company_id':company_id,
                                'branch_id':branch_id,
                                'project_id':project_id,
                                'analytic_account_id':data.analytic_account_id and data.analytic_account_id.id,
                                'amended_sale':data.od_amc_amend_sale,
                                'amended_cost':data.od_amc_amend_cost,
                                'amended_profit':data.od_amc_amend_profit,
                                'actual_profit': data.od_amc_profit,
                                'contract_status': contract_status
                                                                }))
        
        
              
        project_data2 = self.env['project.project'].search(domain2) 
        
        for data in project_data2:
            project_id = data.id
            partner_id = data.partner_id and data.partner_id.id 
            company_id = data.company_id and data.company_id.id 
            branch_id = data.od_branch_id and data.od_branch_id.id
            od_cost_sheet_id = data.od_cost_sheet_id and data.od_cost_sheet_id.id
            approved_date =data.od_cost_sheet_id and data.od_cost_sheet_id.approved_date or False
            contract_status = data.state 
            sale = data.od_amended_sale_price
            cost = data.od_amended_sale_cost
            profit = sale - cost
            result.append((0,0,{
                            'approved_date':approved_date,
                            'amc_wiz_id':wiz_id,
                            'cost_sheet_id':od_cost_sheet_id, 
                            'partner_id':partner_id,
                            'company_id':company_id,
                            'branch_id':branch_id,
                            'project_id':project_id,
                            'analytic_account_id':data.analytic_account_id and data.analytic_account_id.id,
                            'amended_sale':sale,
                            'amended_cost':cost,
                            'amended_profit':data.od_amended_profit,
                            'actual_profit': sale - data.od_actual_cost,
                            'contract_status': contract_status
                                                                }))
                
                
        return result
    

    @api.multi
    def export_rpt(self):
        amc_vals = self.get_amc_vals()
        self.wiz_line.unlink()
        self.write({'wiz_line':amc_vals})
        del(amc_vals)
        model_data = self.env['ir.model.data']
        vw ='od_amc_rev_data_tree_view'
        tree_view = model_data.get_object_reference('beta_customisation', vw)
        return {
            'domain': [('amc_wiz_id','=',self.id)],
            'name': 'Revenue Report',
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(tree_view and tree_view[1] or False, 'tree')],
            'context':{'search_default_year':1},
            'res_model': 'amc.rev.rpt.data',
            'type': 'ir.actions.act_window',
        }
        

class amc_rev_rpt_data(models.TransientModel):
    _name = 'amc.rev.rpt.data'
    amc_wiz_id = fields.Many2one('amc.rev.rpt.wiz',string="Wizard")
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet')
    approved_date = fields.Date(string="Approved Date")
    partner_id = fields.Many2one('res.partner',string="Customer")
    company_id = fields.Many2one('res.company',string="Company")
    branch_id = fields.Many2one('od.cost.branch',string="Branch")
    project_id = fields.Many2one('project.project',string='Project')
    analytic_account_id = fields.Many2one('account.analytic.account',string='Analytic Account')
       
    amended_sale = fields.Float(string="Amended Sale",digits=dp.get_precision('Account'))
    amended_cost = fields.Float(string="Amended Cost",digits=dp.get_precision('Account'))
    amended_profit = fields.Float(string="Estimated Profit",digits=dp.get_precision('Account'))
    actual_profit = fields.Float(string="Actual Profit",digits=dp.get_precision('Account'))
    contract_status = fields.Selection([('template','Template'),('draft','New'),('open','In Progress'),('pending','To Renew'),('close','Closed'),('sign_off','Sign Off'),('cancelled','Cancelled'),('cancel','Cancelled(Component)')],string="Contract Status")

    
    
    @api.multi
    def btn_open_project(self):
       
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'project.project',
                'res_id':self.project_id and self.project_id.id or False,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }
    
    @api.multi
    def btn_open_analytic(self):
       
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.analytic.account',
                'res_id':self.analytic_account_id and self.analytic_account_id.id or False,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }
    @api.multi
    def btn_open_cost(self):
       
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'od.cost.sheet',
                'res_id':self.cost_sheet_id and self.cost_sheet_id.id or False,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }