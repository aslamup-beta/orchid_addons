# -*- coding: utf-8 -*-
from openerp import models, fields, api
from pprint import pprint
from datetime import datetime
import openerp.addons.decimal_precision as dp


class amc_inv_sch_wiz(models.TransientModel):
    _name = 'amc.inv.sch.wiz'
    
    
    
   
    branch_ids= fields.Many2many('od.cost.branch',string="Branch")
    partner_ids = fields.Many2many('res.partner','x_partner_amc_inv_sch','wiz_id','partner_id',string="Customer")
    pm_ids = fields.Many2many('res.users','proj_wiz_pm_amc_inv_sch','wiz_id','user_id',string="Service Desk Engineer")
    analytic_account_ids = fields.Many2many('account.analytic.account',string="Analytic Accounts")
    
    planning_date_from = fields.Date(string="Invoice Planning Date From")
    planning_date_to = fields.Date(string="Invoice Planning Date To")
    
     
    pmo_planning_date_from = fields.Date(string="PMO Expected Invoice Date From")
    pmo_planning_date_to = fields.Date(string="PMO Expected Invoice Date To")
    
    accept_date_from = fields.Date(string="Invoice Customer Accept Date From")
    accept_date_to = fields.Date(string="Invoice Customer Accept Date To")
    
    
    wiz_line = fields.One2many('wiz.amc.inv.sch.data','wiz_id',string="Wiz Line")
   
    
    def od_get_company_id(self):
        return self.env.user.company_id
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    @api.multi 
    def export_rpt(self):
        
        
        branch_ids = [pr.id for pr in self.branch_ids]
        pm_ids =[pr.id for pr in self.pm_ids]
        partner_ids =[pr.id for pr in self.partner_ids]
        analytic_ids =[pr.id for pr in self.analytic_account_ids]
        wiz_id = self.id
       
        
        planning_date_from = self.planning_date_from
        planning_date_to = self.planning_date_to
        
         
        pmo_planning_date_from = self.pmo_planning_date_from
        pmo_planning_date_to = self.pmo_planning_date_to
        
        accept_date_from = self.accept_date_from
        accept_date_to = self.accept_date_to
        
            
        company_id = self.company_id and self.company_id.id 
        domain = [('od_type_of_project','in',('amc','o_m'))]
        domain2=[]
        if company_id:
            domain += [('company_id','=',company_id)]
        if partner_ids:
            domain += [('partner_id','in',partner_ids)]
       
        if branch_ids:
            domain += [('od_branch_id','in',branch_ids)]
        
        
        if pm_ids:
            domain += [('od_owner_id','in',pm_ids)]
        
        if analytic_ids:
            domain +=[('id','in',analytic_ids)]
        
        
        analytic_pool = self.env['account.analytic.account']
        
        an_ids = analytic_pool.search(domain)
        an_ac_ids = [an.id for an in an_ids] 
        
        
        domain2 +=[('analytic_id','in',an_ac_ids)]
        
        if planning_date_from:
            domain2 += [('date','>=',planning_date_from)]
        if planning_date_to:
            domain2 += [('date','<=',planning_date_to)]
        
            
        if pmo_planning_date_from:
            domain2 += [('pmo_date','>=',pmo_planning_date_from)]
        if pmo_planning_date_to:
            domain2 += [('pmo_date','<=',pmo_planning_date_to)]
        
        if accept_date_from:
            domain2 += [('cust_date','>=',accept_date_from)]
        
        if accept_date_to:
            domain2 += [('cust_date','<=',accept_date_to)]
        sch_data = self.env['od.amc.invoice.schedule'].search(domain2) 
        result =[]
        for data in sch_data:
            an_id = data.analytic_id and data.analytic_id.id 
            pm_id = data.analytic_id and data.analytic_id.od_owner_id and data.analytic_id.od_owner_id.id
            partner_id = data.analytic_id and data.analytic_id.partner_id and data.analytic_id.partner_id.id 
            company_id = data.analytic_id and  data.analytic_id.company_id and data.analytic_id.company_id.id 
            branch_id = data.analytic_id.od_branch_id and data.analytic_id.od_branch_id.id
            od_cost_sheet_id = data.analytic_id.od_cost_sheet_id and data.analytic_id.od_cost_sheet_id.id
            result.append((0,0,{
                                'wiz_id':wiz_id,
                                'cost_sheet_id':od_cost_sheet_id, 
                                'partner_id':partner_id,
                                'company_id':company_id,
                                'branch_id':branch_id,
                                'pm_id':pm_id,
                                'analytic_id':an_id,
                                'name':data.name,
                                'planned_date':data.date,
                                'planned_amount':data.amount,
                                'invoice_id':data.invoice_id and data.invoice_id.id,
                                'invoice_amount':data.invoice_amount,
                                'invoice_status':data.invoice_status,
                                'date_invoice':data.date_invoice,
                                'cust_date':data.cust_date,
                                
                                }))
                        
        self.wiz_line.unlink()
        self.write({'wiz_line':result})
        return {
            'domain': [('wiz_id','=',wiz_id)],
            'name': 'SLA Invoice Schedule Report',
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'wiz.amc.inv.sch.data',
            'type': 'ir.actions.act_window',
        }
                        
        
        
        

class wiz_amc_rpt_data(models.TransientModel):
    _name = 'wiz.amc.inv.sch.data'
    wiz_id = fields.Many2one('amc.inv.sch.wiz',string="Wizard")
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet')
    partner_id = fields.Many2one('res.partner',string="Customer")
    company_id = fields.Many2one('res.company',string="Company")
    branch_id = fields.Many2one('od.cost.branch',string="Branch")
    analytic_id = fields.Many2one('account.analytic.account',string='Account')
    pm_id = fields.Many2one('res.users',string="Service Desk Engineer")
    invoice_status = fields.Selection([('draft','Draft'),('proforma','Pro-forma'),('proforma2','Pro-forma'),('open','Open'),('accept','Accepted By Customer'),('paid','Paid'),('cancel','Cancelled')],string="Invoice Status")
    name =fields.Char(string="Name")
    planned_date = fields.Date(string="Planned Date")
    planned_amount = fields.Float(strig="Planned Amount")
    invoice_id = fields.Many2one('account.invoice',string="Invoice")
    invoice_amount = fields.Float(string="Invoice Amount")
    date_invoice = fields.Date(string="Invoice Date")
    cust_date = fields.Date(string="Customer Accepted Date")
    
    
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