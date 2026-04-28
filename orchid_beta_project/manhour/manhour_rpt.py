# -*- coding: utf-8 -*-
from openerp import models, fields, api
from pprint import pprint
from datetime import datetime
import openerp.addons.decimal_precision as dp


class manhour_rpt_wiz(models.TransientModel):
    _name = 'manhour.rpt.wiz'
    
    
    
    
     
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
    pm_ids = fields.Many2many('res.users','proj_man_wiz_pm','wiz_id','user_id',string="Project Manager")
    sam_ids = fields.Many2many('res.users','proj_man_wiz_sam','wiz_id','user_id',string="Sales Account Manager")
    sale_team_ids = fields.Many2many('crm.case.section',string="Sale Team")
    territory_ids = fields.Many2many('od.partner.territory',string="Territory")
   
    project_ids = fields.Many2many('project.project','proj_wiz_man_sam','wiz_id','project',string="Project")
    cost_sheet_ids = fields.Many2many('od.cost.sheet','cost_wiz_man','wiz_id','cost_sheet_id',string="Costsheets",domain=[('state','=','done')])
    approved_date_from = fields.Date(string="Costsheet Approved Date From")
    approved_date_to = fields.Date(string="Costsheet Approved Date To")
    wip = fields.Boolean(string="Work In Progress")
    closed = fields.Boolean(string="Closed Projects")
    
    wiz_line = fields.One2many('manhour.rpt.data','wiz_id',string="Wiz Line")
    
    def od_get_company_id(self):
        return self.env.user.company_id
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    
    def get_work_hour(self,analytic_id):
        timesheet_pool = self.env['hr.analytic.timesheet']
        timesheet_ids = timesheet_pool.search([('account_id','=',analytic_id)])
        work_hour = sum([sheet.unit_amount for sheet in timesheet_ids])
        return work_hour
    
    def get_no_of_l2(self,sheet):
        sheet_id = sheet.id
        project_pool = self.env['project.project']
        project_ids = project_pool.search([('od_cost_sheet_id','=',sheet_id),('od_type_of_project','=','amc'),('state','!=','cancelled'),('type','!=','view')])
        return len(project_ids)
    
    def get_vals(self):
        branch_ids = [pr.id for pr in self.branch_ids]
        cost_centre_ids = [pr.id for pr in self.cost_centre_ids]
        division_ids = [pr.id for pr in self.division_ids]
        pm_ids =[pr.id for pr in self.pm_ids]
        sam_ids =[pr.id for pr in self.sam_ids]
        sale_team_ids =[pr.id for pr in self.sale_team_ids]
        territory_ids =[pr.id for pr in self.territory_ids]
        partner_ids =[pr.id for pr in self.partner_ids]
        project_ids = [pr.id for pr in self.project_ids]
        cost_sheet_ids = [pr.id for pr in self.cost_sheet_ids]
        wiz_id = self.id
        wip = self.wip 
        closed = self.closed 
#         inactive= self.inactive
        
       
        date_end_from = self.date_end_from
        date_end_to = self.date_end_to
        
        closing_date_from =self.closing_date_from
        closing_date_to =self.closing_date_to
        
        approved_date_from = self.approved_date_from 
        approved_date_to = self.approved_date_to
        
        company_id = self.company_id and self.company_id.id 
        
        domain = []
        domain+=[('company_id','=',company_id)]
        if approved_date_from:
            
            domain+=[('approved_date','>=',approved_date_from)]
        if approved_date_to:
            domain+=[('approved_date','<=',approved_date_to)]
        if approved_date_from or approved_date_to:
            costsheet_data = self.env['od.cost.sheet'].search(domain)
            
            cost_sheet_ids2 = [cs.id for cs in costsheet_data]
            cost_sheet_ids += cost_sheet_ids2
        
        if cost_sheet_ids:
            project_data = self.env['project.project'].search([('od_cost_sheet_id','in',cost_sheet_ids)])
            project_ids =[pr.id for pr in project_data]
        
        nominal_value =350.0
        if company_id ==6:
            nominal_value =250.0
            
            
        
        domain2 = [('od_type_of_project','in',('imp','sup_imp','amc')),('state','!=','cancelled'),('type','!=','view')]
        
        
        if project_ids:
            domain2 += [('id','in',project_ids)]
        if company_id:
            domain2 += [('company_id','=',company_id)]
        if partner_ids:
            domain2 += [('partner_id','in',partner_ids)]
        
        prj_states = []
        if wip:
            prj_states += ['open','pending']
        if closed:
            prj_states += ['close']
#         if inactive:
#             prj_states += ['draft']
        
        
        
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
        
        
        project_data2 = self.env['project.project'].search(domain2)
        for data in project_data2:
            project_id = data.id
           
            od_cost_sheet_id = data.od_cost_sheet_id and data.od_cost_sheet_id.id
            ret_mp = data.od_cost_sheet_id and data.od_cost_sheet_id.returned_mp or 0.0
            
            pstatus = data.state
            analytic_id =data.analytic_account_id and data.analytic_account_id.id 
            
            type_of_project = data.od_type_of_project
            if type_of_project in ['imp','sup_imp']:
                ret_mp = data.od_cost_sheet_id and data.od_cost_sheet_id.a_bim_cost or 0.0
            if type_of_project == 'amc':
                ret_mp = data.od_cost_sheet_id and data.od_cost_sheet_id.a_bmn_cost or 0.0
                no_of_l2 = self.get_no_of_l2(data.od_cost_sheet_id)
                if no_of_l2  :
                    ret_mp = ret_mp/no_of_l2 
            
            work_hour = self.get_work_hour(analytic_id)
            cst_hour = ret_mp/nominal_value
            
            sam_id = data.manager_id and data.manager_id.id
            pm_id = data.od_owner_id and data.od_owner_id.id 
            partner_id = data.partner_id and data.partner_id.id 
            company_id = data.company_id and data.company_id.id 
            branch_id = data.od_branch_id and data.od_branch_id.id
            od_cost_sheet_id = data.od_cost_sheet_id and data.od_cost_sheet_id.id
            approved_date =data.od_cost_sheet_id and data.od_cost_sheet_id.approved_date or False
            
            
            if pstatus in ('open','pending'):
                pstatus ='Open'
            elif pstatus =='close':
                pstatus = 'Closed'
            else:
                pstatus ='Inactive'
           
            result.append((0,0,{
                               
                                'cost_sheet_id':od_cost_sheet_id, 
                             
                                'project_id':project_id,
                                'analytic_account_id':data.analytic_account_id and data.analytic_account_id.id,
                               'cst_manhour':cst_hour,
                               'work_manhour':work_hour,
                               'sam_id':sam_id ,
                                'partner_id':partner_id,
                               'approved_date':approved_date,
                                'branch_id':branch_id,
                                'pm_id':pm_id,
                                 'date_start':data.date_start,
                                'date_end':data.od_analytic_pmo_closing, 
                                 'contract_status':data.state ,
                                  'closing_date':data.od_closing_date,
                                }))
        return result
    
    
    @api.multi 
    def export_rpt(self):
       
        result = self.get_vals()
        self.wiz_line.unlink()
        self.write({'wiz_line':result})
        return {
            'domain': [('wiz_id','=',self.id)],
            'name': 'Man-hour Report',
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'manhour.rpt.data',
            'type': 'ir.actions.act_window',
        }
    
class manhour_rpt_data(models.TransientModel):
    _name = 'manhour.rpt.data'
    wiz_id = fields.Many2one('manhour.rpt.wiz',string="Wizard")
    
    project_id = fields.Many2one('project.project',string='Project')
    cost_sheet_id = fields.Many2one('od.cost.sheet',string="Costsheet")
    cst_manhour= fields.Float(string="Costsheet Manhour")
    work_manhour = fields.Float("Worked Hours")
    
    approved_date = fields.Date(string="Approved Date")
    partner_id = fields.Many2one('res.partner',string="Customer")
    branch_id = fields.Many2one('od.cost.branch',string="Branch")
    sam_id = fields.Many2one('res.users',string="Sale Account Manager")
    pm_id = fields.Many2one('res.users',string="Project Manager")
    contract_status = fields.Selection([('template','Template'),('draft','New'),('open','In Progress'),('pending','To Renew'),('close','Closed'),('sign_off','Sign Off'),('cancelled','Cancelled'),('cancel','Cancelled(Component)')],string="Contract Status")
    closing_date = fields.Date(string="Actual Closing Date")
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
    def btn_open_cost(self):
       
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'od.cost.sheet',
                'res_id':self.cost_sheet_id and self.cost_sheet_id.id or False,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }
    