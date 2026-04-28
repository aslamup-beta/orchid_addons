# -*- coding: utf-8 -*-
from openerp import models, fields, api
from pprint import pprint
from datetime import datetime
import openerp.addons.decimal_precision as dp


class fiscal_rpt_wiz(models.TransientModel):
    _name = 'fiscal.rev.rpt.wiz'
    
    branch_ids= fields.Many2many('od.cost.branch',string="Branch")
    cost_centre_ids = fields.Many2many('od.cost.centre',string="Cost Center")
    division_ids = fields.Many2many('od.cost.division',string="Technology Unit")
    
    date_start_from = fields.Date(string="Project Planned Starting Date From")
    date_start_to = fields.Date(string="Project Planned Starting Date To")
    
    date_end_from = fields.Date(string="PMO Expected Closing Date From")
    date_end_to = fields.Date(string="PMO Expected Closing Date To")
    
    closing_date_from = fields.Date(string="Project Actual Closing  From")
    closing_date_to = fields.Date(string="Project Actual Closing  To")
    
    partner_ids = fields.Many2many('res.partner',string="Customer")
    pm_ids = fields.Many2many('res.users','fisc_proj_wiz_pm','wiz_id','user_id',string="Project Manager")
    sam_ids = fields.Many2many('res.users','proj_wiz_sam','wiz_id','user_id',string="Sales Account Manager")
    sale_team_ids = fields.Many2many('crm.case.section',string="Sale Team")
    territory_ids = fields.Many2many('od.partner.territory',string="Territory")
    wiz_line = fields.One2many('fiscal.rev.rpt.data','wiz_id',string="Wiz Line")
    wip = fields.Boolean(string="Work In Progress")
    closed = fields.Boolean(string="Closed Projects")
    inactive = fields.Boolean(string="Inactive Projects")
    include_invoice = fields.Boolean(string="Include Customer Invoices?", default=True)
    def od_get_company_id(self):
        return self.env.user.company_id
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    
    def get_amc_vals(self):
        branch_ids = [pr.id for pr in self.branch_ids]
        cost_centre_ids = [pr.id for pr in self.cost_centre_ids]
        division_ids = [pr.id for pr in self.division_ids]
        pm_ids =[pr.id for pr in self.pm_ids]
        #For PM default filling their user_id in code
        user_id = self.env.user.id
        emp_id = self.env['hr.employee'].search([('user_id','=',user_id)])
        if emp_id.job_id.id in (30,80,43,85,166):
            pm_ids = [user_id]
        sam_ids =[pr.id for pr in self.sam_ids]
        sale_team_ids =[pr.id for pr in self.sale_team_ids]
        territory_ids =[pr.id for pr in self.territory_ids]
        partner_ids =[pr.id for pr in self.partner_ids]
        wiz_id = self.id
        wip = self.wip 
        closed = self.closed 
        inactive= self.inactive
            
        date_start_from = self.date_start_from
        date_start_to = self.date_start_to
        date_end_from = self.date_end_from
        date_end_to = self.date_end_to
        
        closing_date_from =self.closing_date_from
        closing_date_to =self.closing_date_to
        
        prj_states = []
        if wip:
            prj_states += ['active']
        if closed:
            prj_states += ['close']
        if inactive:
            prj_states += ['inactive']
            
        company_id = self.company_id and self.company_id.id 
        domain = [('od_type_of_project','in',('amc','o_m')),('state','!=','cancelled'),('type','!=','view'),('od_analytic_level','=','level_old')]
        if company_id:
            domain += [('company_id','=',company_id)]
        
        if partner_ids:
            domain += [('partner_id','in',partner_ids)]
        
        if prj_states:
            domain+=[('od_amc_status','in',prj_states)]
        if branch_ids:
            domain += [('od_branch_id','in',branch_ids)]
        if cost_centre_ids:
            domain += [('od_cost_centre_id','in',cost_centre_ids)]
        if division_ids:
            domain += [('od_division_id','in',division_ids)]
        
        if pm_ids:
            domain += [('od_amc_owner_id','in',pm_ids)]
        if sam_ids:
            domain += [('manager_id','in',sam_ids)]
        if sale_team_ids:
            domain += [('od_section_id','in',sale_team_ids)]
        if territory_ids:
            domain += [('od_territory_id','in',territory_ids)]
        
        
        if date_start_from:
            domain += [('od_amc_start','>=',date_start_from)]
        if date_start_to:
            domain += [('od_amc_start','<=',date_start_to)]
        
        if date_end_from:
            domain += [('od_amc_pmo_closing','>=',date_end_from)]
        
        if date_end_to:
            domain += [('od_amc_pmo_closing','<=',date_end_to)]
        
          
        if closing_date_from:
            domain += [('od_amc_closing','>=',closing_date_from)]
        
        if closing_date_to:
            domain += [('od_amc_closing','<=',closing_date_to)]
            
        domain2 = [('od_type_of_project','in',('amc','o_m')),('state','!=','cancelled'),('type','!=','view'),('od_analytic_level','!=','level_old')]
        if company_id:
            domain2 += [('company_id','=',company_id)]
        
        if partner_ids:
            domain2 += [('partner_id','in',partner_ids)]
        
        prj_states = []
        if wip:
            prj_states += ['open','pending','sign_off']
        if closed:
            prj_states += ['close']
        if inactive:
            prj_states += ['draft']
        
        if prj_states:
            domain2 +=[('state','in',prj_states)]
        if branch_ids:
            domain2 += [('od_branch_id','in',branch_ids)]
        if cost_centre_ids:
            domain2 += [('od_cost_centre_id','in',cost_centre_ids)]
        if division_ids:
            domain2 += [('od_division_id','in',division_ids)]
        
        if pm_ids:
            domain2 += [('od_owner_id','in',pm_ids)]
        if sam_ids:
            domain2 += [('manager_id','in',sam_ids)]
        if sale_team_ids:
            domain2 += [('od_section_id','in',sale_team_ids)]
        if territory_ids:
            domain2 += [('od_territory_id','in',territory_ids)]
        
        
        if date_end_from:
            domain2 += [('od_analytic_pmo_closing','>=',date_end_from)]
        
        if date_end_to:
            domain2 += [('od_analytic_pmo_closing','<=',date_end_to)]
        
          
        if closing_date_from:
            domain2 += [('od_closing_date','>=',closing_date_from)]
        
        if closing_date_to:
            domain2 += [('od_closing_date','<=',closing_date_to)]
    
        result =[]
       
        project_data = self.env['project.project'].search(domain) 
        
        for data in project_data:
            project_id = data.id
            sam_id = data.manager_id and data.manager_id.id
            pm_id = data.od_amc_owner_id and data.od_amc_owner_id.id 
            partner_id = data.partner_id and data.partner_id.id 
            company_id = data.company_id and data.company_id.id 
            branch_id = data.od_branch_id and data.od_branch_id.id
            od_cost_sheet_id = data.od_cost_sheet_id and data.od_cost_sheet_id.id
            approved_date =data.od_cost_sheet_id and data.od_cost_sheet_id.approved_date or False
            po_status = data.od_cost_sheet_id and data.od_cost_sheet_id and data.od_cost_sheet_id.po_status
            pstatus = data.od_amc_status 
            if pstatus =='active':
                pstatus ='Open'
            elif pstatus =='close':
                pstatus = 'Closed'
            else:
                pstatus ='Inactive'
            contract_status = data.state 
            contract_start_date = data.date_start
            contract_end_date = data.date 
            closing_date = data.od_amc_closing
            result.append((0,0,{
                              'approved_date':approved_date,
                                'wiz_id':wiz_id,
                                'cost_sheet_id':od_cost_sheet_id, 
                                'sam_id':sam_id ,
                                'partner_id':partner_id,
                                'company_id':company_id,
                                'branch_id':branch_id,
                                'pm_id':pm_id,
                                'project_id':project_id,
                                'analytic_account_id':data.analytic_account_id and data.analytic_account_id.id,
                                'original_sale':data.od_amc_original_sale,
                                'original_cost':data.od_amc_original_cost,
                                'original_profit':data.od_amc_original_profit,
                                'amended_sale':data.od_amc_amend_sale,
                                'amended_cost':data.od_amc_amend_cost,
                                'amended_profit':data.od_amc_amend_cost,
                                'amended_proft':data.od_amc_amend_cost,
                                'amended_mp':0.0,
                                'invoiced_amnt':data.get_invoice_untaxed_amount(),
                                'wip':data.od_actual_cost,
#                                 'estimated_cost':data.od_amc_amend_cost,
                                'collected_amount':data.get_invoice_amt(),
                                
                                'actual_sale':data.od_amc_sale,
                                'actual_cost':data.od_amc_cost,
                                'actual_profit':data.od_amc_profit,
                                'actual_mp':0.0,
                                'rebate_amnt':0.0,
                                'status':pstatus,
                                'date_start':data.od_amc_start,
                                'date_end':data.od_analytic_pmo_closing, 
                                'po_status':po_status,
                                 'contract_status':contract_status,
                                'contract_start_date':contract_start_date,
                                'contract_end_date':contract_end_date,
                                'closing_date':closing_date,
                                 'project_type':'amc' 
                                }))
        
        
              
        project_data2 = self.env['project.project'].search(domain2) 
        
        for data in project_data2:
            project_id = data.id
            sam_id = data.manager_id and data.manager_id.id
            pm_id = data.od_owner_id and data.od_owner_id.id 
            partner_id = data.partner_id and data.partner_id.id 
            company_id = data.company_id and data.company_id.id 
            branch_id = data.od_branch_id and data.od_branch_id.id
            od_cost_sheet_id = data.od_cost_sheet_id and data.od_cost_sheet_id.id
            approved_date =data.od_cost_sheet_id and data.od_cost_sheet_id.approved_date or False
            po_status = data.od_cost_sheet_id and data.od_cost_sheet_id and data.od_cost_sheet_id.po_status
            pstatus = data.state 
            if pstatus in ('open','pending','sign_off'):
                pstatus ='Open'
            elif pstatus =='close':
                pstatus = 'Closed'
            else:
                pstatus ='Inactive'
            contract_status = data.state 
            contract_start_date = data.date_start
            contract_end_date = data.date 
            closing_date = data.od_closing_date
            if self.include_invoice:
                sale = data.od_amended_sale_price
                cost = data.od_amended_sale_cost
                profit = sale -cost
                result.append((0,0,{
                                      'approved_date':approved_date,
                                    'wiz_id':wiz_id,
                                    'cost_sheet_id':od_cost_sheet_id, 
                                    'sam_id':sam_id ,
                                    'partner_id':partner_id,
                                    'company_id':company_id,
                                    'branch_id':branch_id,
                                    'pm_id':pm_id,
                                    'project_id':project_id,
                                    'analytic_account_id':data.analytic_account_id and data.analytic_account_id.id,
                                    'original_sale':data.od_original_sale_price,
                                    'original_cost':data.od_original_sale_cost,
                                    'original_profit':data.od_original_sale_profit,
                                    'amended_sale':sale,
                                    'amended_cost':cost,
                                    'amended_profit':data.od_amended_profit + data.od_rebate,
                                    'amended_prof':profit + data.od_rebate,
                                    'amended_mp':data.od_amended_profit - profit ,
                                    'invoiced_amnt':data.get_invoice_untaxed_amount(),
                                    'wip':data.od_actual_cost,
    #                                 'estimated_profit':data.od_amended_cost_rg,
                                    'collected_amount':data.get_invoice_amt(),
                                    
                                    'actual_sale':data.od_actual_sale,
                                    'actual_cost':data.od_actual_cost,
                                    'actual_profit':data.od_actual_prof,
                                    'actual_mp':data.od_timesheet_amount2,
                                    'rebate_amnt':data.od_rebate,
                                    'status':pstatus,
                                    'date_start':data.date_start,
                                    'date_end':data.od_analytic_pmo_closing, 
                                    'po_status':po_status,
                                    'contract_status':contract_status,
                                    'contract_start_date':contract_start_date,
                                    'contract_end_date':contract_end_date,
                                    'closing_date':closing_date,
                                     'project_type':'amc'
                                    }))
            
            else:
                sale = data.od_amended_sale_price
                cost = data.od_amended_sale_cost
                profit = sale -cost
                result.append((0,0,{
                                      'approved_date':approved_date,
                                    'wiz_id':wiz_id,
                                    'cost_sheet_id':od_cost_sheet_id, 
                                    'sam_id':sam_id ,
                                    'partner_id':partner_id,
                                    'company_id':company_id,
                                    'branch_id':branch_id,
                                    'pm_id':pm_id,
                                    'project_id':project_id,
                                    'analytic_account_id':data.analytic_account_id and data.analytic_account_id.id,
                                    'original_sale':data.od_original_sale_price,
                                    'original_cost':data.od_original_sale_cost,
                                    'original_profit':data.od_original_sale_profit,
                                     'amended_sale':sale,
                                    'amended_cost':cost,
                                    'amended_profit':data.od_amended_profit + data.od_rebate,
                                    'amended_prof':profit + data.od_rebate,
                                    'amended_mp':data.od_amended_profit - profit ,
#                                     'invoiced_amnt':data.od_amnt_invoiced - data.od_cust_refund_amt,
                                    'wip':data.od_actual_cost,
    #                                 'estimated_profit':data.od_amended_cost_rg,
#                                     'collected_amount':data.get_invoice_amt(),
                                    
                                    'actual_sale':data.od_actual_sale,
                                    'actual_cost':data.od_actual_cost,
                                    'actual_profit':data.od_actual_prof,
                                    'actual_mp':data.od_timesheet_amount2,
                                    'rebate_amnt':data.od_rebate,
                                    'status':pstatus,
                                    'date_start':data.date_start,
                                    'date_end':data.od_analytic_pmo_closing, 
                                    'po_status':po_status,
                                    'contract_status':contract_status,
                                    'contract_start_date':contract_start_date,
                                    'contract_end_date':contract_end_date,
                                    'closing_date':closing_date,
                                     'project_type':'amc'
                                    }))
                
                
        return result
    
    
    def get_project_vals(self):
        branch_ids = [pr.id for pr in self.branch_ids]
        cost_centre_ids = [pr.id for pr in self.cost_centre_ids]
        division_ids = [pr.id for pr in self.division_ids]
        pm_ids =[pr.id for pr in self.pm_ids]
        #For PM default filling their user_id in code
        user_id = self.env.user.id
        emp_id = self.env['hr.employee'].search([('user_id','=',user_id)])
        if emp_id.job_id.id in (30,80,43,85,166):
            pm_ids = [user_id]
        sam_ids =[pr.id for pr in self.sam_ids]
        sale_team_ids =[pr.id for pr in self.sale_team_ids]
        territory_ids =[pr.id for pr in self.territory_ids]
        partner_ids =[pr.id for pr in self.partner_ids]
        wiz_id = self.id
        wip = self.wip 
        closed = self.closed 
        inactive= self.inactive
        
       
        date_end_from = self.date_end_from
        date_end_to = self.date_end_to
        
        closing_date_from =self.closing_date_from
        closing_date_to =self.closing_date_to
        
        
        prj_states = []
        if wip:
            prj_states += ['active']
        if closed:
            prj_states += ['close']
        if inactive:
            prj_states += ['inactive']
        
        #Added training proj also as per request of elayyan on 11/feb/19 by Aslam     
        company_id = self.company_id and self.company_id.id 
        domain = [('od_type_of_project','in',('credit','sup','imp','sup_imp','cust_trn')),('state','!=','cancelled'),('type','!=','view'),('od_analytic_level','=','level_old')]
        if company_id:
            domain += [('company_id','=',company_id)]
        if partner_ids:
            domain += [('partner_id','in',partner_ids)]
        
        if prj_states:
            domain+=[('od_project_status','in',prj_states)]
        if branch_ids:
            domain += [('od_branch_id','in',branch_ids)]
        if cost_centre_ids:
            domain += [('od_cost_centre_id','in',cost_centre_ids)]
        if division_ids:
            domain += [('od_division_id','in',division_ids)]
        
        if pm_ids:
            domain += [('od_project_owner_id','in',pm_ids)]
        if sam_ids:
            domain += [('manager_id','in',sam_ids)]
        if sale_team_ids:
            domain += [('od_section_id','in',sale_team_ids)]
        if territory_ids:
            domain += [('od_territory_id','in',territory_ids)]
            
        
        
        if date_end_from:
            domain += [('od_project_pmo_closing','>=',date_end_from)]
        
        if date_end_to:
            domain += [('od_project_pmo_closing','<=',date_end_to)]
            
        if closing_date_from:
            domain += [('od_project_closing','>=',closing_date_from)]
        
        if closing_date_to:
            domain += [('od_project_closing','<=',closing_date_to)]
        
            
        
        
        #Added training proj also as per request of elayyan on 11/feb/19 by Aslam
        domain2 = [('od_type_of_project','in',('credit','sup','imp','sup_imp','cust_trn')),('state','!=','cancelled'),('type','!=','view'),('od_analytic_level','!=','level_old')]
        
        if company_id:
            domain2 += [('company_id','=',company_id)]
        if partner_ids:
            domain2 += [('partner_id','in',partner_ids)]
        
        prj_states = []
        if wip:
            prj_states += ['open','pending','sign_off']
        if closed:
            prj_states += ['close']
        if inactive:
            prj_states += ['draft']
        
        
        
        if prj_states:
            domain2 +=[('state','in',prj_states)]
        if branch_ids:
            domain2 += [('od_branch_id','in',branch_ids)]
        if cost_centre_ids:
            domain2 += [('od_cost_centre_id','in',cost_centre_ids)]
        if division_ids:
            domain2 += [('od_division_id','in',division_ids)]
        
        if pm_ids:
            domain2 += [('od_owner_id','in',pm_ids)]
        if sam_ids:
            domain2 += [('manager_id','in',sam_ids)]
        if sale_team_ids:
            domain2 += [('od_section_id','in',sale_team_ids)]
        if territory_ids:
            domain2 += [('od_territory_id','in',territory_ids)]
            
        
        
        if date_end_from:
            domain2 += [('od_analytic_pmo_closing','>=',date_end_from)]
        
        if date_end_to:
            domain2 += [('od_analytic_pmo_closing','<=',date_end_to)]
            
        if closing_date_from:
            domain2 += [('od_closing_date','>=',closing_date_from)]
        
        if closing_date_to:
            domain2 += [('od_closing_date','<=',closing_date_to)]
        
         
        result =[]
        project_data = self.env['project.project'].search(domain)
        for data in project_data:
            project_id = data.id
            sam_id = data.manager_id and data.manager_id.id
            pm_id = data.od_project_owner_id and data.od_project_owner_id.id 
            partner_id = data.partner_id and data.partner_id.id 
            company_id = data.company_id and data.company_id.id 
            branch_id = data.od_branch_id and data.od_branch_id.id
            od_cost_sheet_id = data.od_cost_sheet_id and data.od_cost_sheet_id.id
            approved_date =data.od_cost_sheet_id and data.od_cost_sheet_id.approved_date or False
            po_status = data.od_cost_sheet_id and data.od_cost_sheet_id and data.od_cost_sheet_id.po_status
            pstatus = data.od_project_status 
            if pstatus =='active':
                pstatus ='Open'
            elif pstatus =='close':
                pstatus = 'Closed'
            else:
                pstatus ='Inactive'
            
            contract_status = data.state 
            contract_start_date = data.date_start
            contract_end_date = data.date 
            closing_date = data.od_project_closing
            result.append((0,0,{
                               'approved_date':approved_date,
                                'wiz_id':wiz_id,
                                'cost_sheet_id':od_cost_sheet_id, 
                                'sam_id':sam_id ,
                                'partner_id':partner_id,
                                'company_id':company_id,
                                'branch_id':branch_id,
                                'pm_id':pm_id,
                                'project_id':project_id,
                                'analytic_account_id':data.analytic_account_id and data.analytic_account_id.id,
                                'original_sale':data.od_project_original_sale,
                                'original_cost':data.od_project_original_cost,
                                'original_profit':data.od_project_original_profit,
                                'amended_sale':data.od_project_amend_sale,
                                'amended_cost':data.od_project_amend_cost,
                                'amended_profit':data.od_project_amend_profit + data.od_rebate,
                                'amended_prof':data.od_project_amend_profit + data.od_rebate,
                                'amended_mp':0.0,
                                'wip':data.od_project_cost,
#                                 'estimated_profit':data.od_project_amend_sale - data.od_project_amend_profit,
                                'collected_amount':data.get_invoice_amt(),
                                'invoiced_amnt':data.get_invoice_untaxed_amount(),
                                'actual_sale':data.od_project_sale,
                                'actual_cost':data.od_project_cost,
                                'actual_profit':data.od_project_profit,
                                'actual_mp':0.0,
                                'rebate_amnt':0.0,
                                'status':pstatus,
                                'date_start':data.od_project_start,
                                'date_end':data.od_analytic_pmo_closing, 
                                'po_status':po_status,
                                'contract_status':contract_status,
                                'contract_start_date':contract_start_date,
                                'contract_end_date':contract_end_date,
                                'closing_date':closing_date,
                                 'project_type':'project' 
                                }))
        
        
        
        project_data2 = self.env['project.project'].search(domain2)
        for data in project_data2:
            project_id = data.id
            sam_id = data.manager_id and data.manager_id.id
            pm_id = data.od_owner_id and data.od_owner_id.id 
            partner_id = data.partner_id and data.partner_id.id 
            company_id = data.company_id and data.company_id.id 
            branch_id = data.od_branch_id and data.od_branch_id.id
            od_cost_sheet_id = data.od_cost_sheet_id and data.od_cost_sheet_id.id
            approved_date =data.od_cost_sheet_id and data.od_cost_sheet_id.approved_date or False
            po_status = data.od_cost_sheet_id and data.od_cost_sheet_id and data.od_cost_sheet_id.po_status
            pstatus = data.state 
            if pstatus in ('open','pending','sign_off'):
                pstatus ='Open'
            elif pstatus =='close':
                pstatus = 'Closed'
            else:
                pstatus ='Inactive'
            contract_status = data.state 
            contract_start_date = data.date_start
            contract_end_date = data.date 
            closing_date = data.od_closing_date
            if self.include_invoice:
                
                sale = data.od_amended_sale_price
                cost = data.od_amended_sale_cost
                profit = sale -cost
                result.append((0,0,{
                                     'approved_date':approved_date,
                                    'wiz_id':wiz_id,
                                    'cost_sheet_id':od_cost_sheet_id, 
                                    'sam_id':sam_id ,
                                    'partner_id':partner_id,
                                    'company_id':company_id,
                                    'branch_id':branch_id,
                                    'pm_id':pm_id,
                                    'project_id':project_id,
                                    'analytic_account_id':data.analytic_account_id and data.analytic_account_id.id,
                                    'original_sale':data.od_original_sale_price,
                                    'original_cost':data.od_original_sale_cost,
                                    'original_profit':data.od_original_sale_profit,
                                    'amended_sale':sale,
                                    'amended_cost':cost,
                                    'amended_profit':data.od_amended_profit + data.od_rebate,
                                    'amended_prof':profit + data.od_rebate,
                                    'amended_mp':data.od_amended_profit - profit ,
                                    'invoiced_amnt':data.get_invoice_untaxed_amount(),
                                    'wip':data.od_actual_cost,
    #                                 'estimated_profit':data.od_amended_sale_price -data.od_amended_profit,
                                     'collected_amount':data.get_invoice_amt(),
                                    
                                    'actual_sale':data.od_actual_sale,
                                    'actual_cost':data.od_actual_cost,
                                    'actual_profit':data.od_actual_prof,
                                    'actual_mp':data.od_timesheet_amount2,
                                    'rebate_amnt':data.od_rebate,
                                    'status':pstatus,
                                    'date_start':data.date_start,
                                    'date_end':data.od_analytic_pmo_closing, 
                                    'po_status':po_status,
                                    'contract_status':contract_status,
                                    'contract_start_date':contract_start_date,
                                    'contract_end_date':contract_end_date,
                                    'closing_date':closing_date,
                                     'project_type':'project'
                                    }))
            
            
            else:
                      
                sale = data.od_amended_sale_price
                cost = data.od_amended_sale_cost
                profit = sale -cost
                result.append((0,0,{
                                     'approved_date':approved_date,
                                    'wiz_id':wiz_id,
                                    'cost_sheet_id':od_cost_sheet_id, 
                                    'sam_id':sam_id ,
                                    'partner_id':partner_id,
                                    'company_id':company_id,
                                    'branch_id':branch_id,
                                    'pm_id':pm_id,
                                    'project_id':project_id,
                                    'analytic_account_id':data.analytic_account_id and data.analytic_account_id.id,
                                    'original_sale':data.od_original_sale_price,
                                    'original_cost':data.od_original_sale_cost,
                                    'original_profit':data.od_original_sale_profit,
                                    'amended_sale':sale,
                                    'amended_cost':cost,
                                    'amended_profit':data.od_amended_profit + data.od_rebate,
                                    'amended_prof':profit + data.od_rebate,
                                    'amended_mp':data.od_amended_profit - profit ,
#                                     'invoiced_amnt':data.od_amnt_invoiced - data.od_cust_refund_amt,
                                    'wip':data.od_actual_cost,
    #                                 'estimated_profit':data.od_amended_sale_price -data.od_amended_profit,
#                                      'collected_amount':data.get_invoice_amt(),
                                    
                                    'actual_sale':data.od_actual_sale,
                                    'actual_cost':data.od_actual_cost,
                                    'actual_profit':data.od_actual_prof,
                                    'actual_mp':data.od_timesheet_amount2,
                                    'rebate_amnt':data.od_rebate,
                                    'status':pstatus,
                                    'date_start':data.date_start,
                                    'date_end':data.od_analytic_pmo_closing, 
                                    'po_status':po_status,
                                    'contract_status':contract_status,
                                    'contract_start_date':contract_start_date,
                                    'contract_end_date':contract_end_date,
                                    'closing_date':closing_date,
                                     'project_type':'project'
                                    }))
                    
        
        return result
    
    
    @api.multi
    def export_rpt(self):
        project_vals = self.get_project_vals()
        amc_vals = self.get_amc_vals()
        result = project_vals + amc_vals
        self.wiz_line.unlink()
        self.write({'wiz_line':result})
        del(result)
        
        model_data = self.env['ir.model.data']
        
        vw ='no_inv_od_fiscal_rev_data_tree_view'
        closed = self.closed
        if closed:
            vw ='no_inv_od_fiscal_rev_data_closed_tree_view'
        
        if self.include_invoice:
            vw ='od_fiscal_rev_data_tree_view'
            closed = self.closed
            if closed:
                vw ='od_fiscal_rev_data_closed_tree_view'
        tree_view = model_data.get_object_reference( 'orchid_beta_project', vw)
        
        
        
        return {
            'domain': [('wiz_id','=',self.id)],
            'name': 'Revenue Report',
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(tree_view and tree_view[1] or False, 'tree')],
            'context':{'search_default_status':1},
            'res_model': 'fiscal.rev.rpt.data',
            'type': 'ir.actions.act_window',
        }
        

class fiscal_rev_rpt_data(models.TransientModel):
    _name = 'fiscal.rev.rpt.data'
    wiz_id = fields.Many2one('fiscal.rev.rpt.wiz',string="Wizard")
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet')
    approved_date = fields.Date(string="Approved Date")
    partner_id = fields.Many2one('res.partner',string="Customer")
    company_id = fields.Many2one('res.company',string="Company")
    branch_id = fields.Many2one('od.cost.branch',string="Branch")
    project_id = fields.Many2one('project.project',string='Project')
    analytic_account_id = fields.Many2one('account.analytic.account',string='Analytic Account')
    sam_id = fields.Many2one('res.users',string="Sale Account Manager")
    pm_id = fields.Many2one('res.users',string="Project Manager")
    original_sale = fields.Float(string="Original Sale",digits=dp.get_precision('Account'))
    original_cost = fields.Float(string="Original Cost",digits=dp.get_precision('Account'))
    original_profit = fields.Float(string="Original Profit",digits=dp.get_precision('Account'))
   
    amended_sale = fields.Float(string="Amended Sale",digits=dp.get_precision('Account'))
    amended_cost = fields.Float(string="Amended Cost",digits=dp.get_precision('Account'))
    amended_profit = fields.Float(string="Estimated Profit",digits=dp.get_precision('Account'))
    amended_mp = fields.Float(string="Returned MP")
    amended_prof =fields.Float(string="Profit Without MP")
    
    wip = fields.Float(string="WIP",digits=dp.get_precision('Account'))
    estimated_profit = fields.Float(string="Estimated Cost",digits=dp.get_precision('Account'))
    collected_amount = fields.Float(string="Collected Amount",digits=dp.get_precision('Account'))
   
    actual_sale = fields.Float(string="Actual Sale",digits=dp.get_precision('Account'))
    actual_cost = fields.Float(string="Actual Cost",digits=dp.get_precision('Account'))
    actual_profit = fields.Float(string="Actual Profit",digits=dp.get_precision('Account'))
    actual_mp = fields.Float(string="Actual Manpower",digits=dp.get_precision('Account'))
    date_start = fields.Date(string="Planned Date Start")
    date_end = fields.Date(string="PMO Expected Closing Date")
    closing_date = fields.Date(string="Actual Closing Date")
    contract_status = fields.Selection([('template','Template'),('draft','New'),('open','In Progress'),('pending','To Renew'),('close','Closed'),('sign_off','Sign Off'),('cancelled','Cancelled'),('cancel','Cancelled(Component)')],string="Contract Status")
    contract_start_date =  fields.Date(string="Contract Start Date")
    contract_end_date =  fields.Date(string="Contract End Date")
    project_type = fields.Selection([('amc','AMC'),('project','Project')],string="Type")
    status = fields.Selection([('Open','Open'),('Inactive','Inactive'),('Closed','Closed')],string="Status")
    po_status = fields.Selection([('waiting_po','Waiting P.O'),('special_approval','Special Approval From GM'),('available','Available'),('credit','Customer Credit')],'Customer PO Status')
    invoiced_amnt =fields.Float(string="Invoiced Amount",digits=dp.get_precision('Account'))
    rebate_amnt =fields.Float(string="Rebate Amount",digits=dp.get_precision('Account'))
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