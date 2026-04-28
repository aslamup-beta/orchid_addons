# -*- coding: utf-8 -*-
from openerp import models, fields, api
from pprint import pprint
from datetime import datetime
import openerp.addons.decimal_precision as dp


class supply_chain_wiz(models.TransientModel):
    _name = 'supply.chain.rpt.wiz'
    
    branch_ids= fields.Many2many('od.cost.branch','supply_wiz_branch','wiz_id','branch_id',string="Branch")
    date_start = fields.Date(string="Original Date End From")
    date_end = fields.Date(string="Original Date End To")
    pmo_exp_date_start = fields.Date(string="PMO Expected Date From")
    pmo_exp_date_end = fields.Date(string="PMO Expected Date To")
    actual_closing_from = fields.Date(string="Actual Closing From")
    actual_closing_to = fields.Date(string="Actual Closing To")
    partner_ids = fields.Many2many('res.partner','supply_partner_rel','wiz_id','partner_id',string="Customer")
    pm_ids = fields.Many2many('res.users','supply_wiz_pm','wiz_id','user_id',string="Project Manager")
    sam_ids = fields.Many2many('res.users','supply_wiz_sam','wiz_id','user_id',string="Sales Account Manager")
    analytic_ids = fields.Many2many('account.analytic.account','supply_wiz_analytic','wiz_id','analytic_id',string="Analytic Account")
    wiz_line = fields.One2many('supply.chain.rpt.data','wiz_id',string="Wiz Line")
    def od_get_company_id(self):
        return self.env.user.company_id
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    
    
    
    def get_submission_date(self,aa):
        date_list = []
        costsheet_id = aa.od_cost_sheet_id  and aa.od_cost_sheet_id.id or False 
        date_log_history = self.env['od.date.log.history']
        date_logs = date_log_history.search([('cost_sheet_id','=',costsheet_id),('name','in',('Submitted Date','Submit To Customer'))])
        for line in date_logs:
            date_list.append(line.date)
        sorted_dates = sorted(date_list)
        first_date = sorted_dates and sorted_dates[0] or False
        last_date = sorted_dates and sorted_dates[-1] or False
        if not date_list:
            first_date,last_date = aa.od_cost_sheet_id.submit_to_customer_date or '',aa.od_cost_sheet_id.submit_to_customer_date or ''
        return first_date,last_date
    
    def get_po_dates(self,aa):
        date_list = []
        po_pool = self.env['purchase.order']
        po_ids = po_pool.search([('project_id','=',aa.id),('state','!=','cancel')])
        for line in po_ids:
            date_list.append(line.date_order)
        sorted_dates = sorted(date_list)
        first_date = sorted_dates and sorted_dates[0] or False
        last_date = sorted_dates and sorted_dates[-1] or False
        return first_date,last_date
    
    def get_pick_in_dates(self,aa):
        date_list = []
        picking = self.env['stock.picking']
        picking_ids = picking.search([('picking_type_code','=','incoming'),('od_analytic_id','=',aa.id),('state','!=','cancel')]) 
        for line in picking_ids:
            date_list.append(line.date_done)
        
        sorted_dates = sorted(date_list)
        first_date = sorted_dates and sorted_dates[0] or False
        last_date = sorted_dates and sorted_dates[-1] or False
        return first_date,last_date
    
    def get_pick_out_dates(self,aa):
        date_list = []
        picking = self.env['stock.picking']
        picking_ids = picking.search([('picking_type_code','=','outgoing'),('od_analytic_id','=',aa.id),('state','!=','cancel')]) 
        for line in picking_ids:
            date_list.append(line.date_done)
        
        sorted_dates = sorted(date_list)
        first_date = sorted_dates and sorted_dates[0] or False
        last_date = sorted_dates and sorted_dates[-1] or False
        return first_date,last_date
            
            
            
    
    def get_vals(self):
        branch_ids = [pr.id for pr in self.branch_ids]
        pm_ids =[pr.id for pr in self.pm_ids]
        sam_ids =[pr.id for pr in self.sam_ids]
        partner_ids =[pr.id for pr in self.partner_ids]
        a_ids =[pr.id for pr in self.analytic_ids]
        company_id = self.company_id and self.company_id.id
        date_start = self.date_start 
        date_end = self.date_end
        pmo_exp_date_start = self.pmo_exp_date_start 
        pmo_exp_date_end = self.pmo_exp_date_end
        actual_closing_start = self.actual_closing_from 
        actual_closing_end = self.actual_closing_to
        
        domain = [('od_type_of_project','in',('credit','sup','imp','sup_imp')),('state','!=','cancelled'),('type','!=','view')]
        if company_id:
            domain += [('company_id','=',company_id)]
        
        if partner_ids:
            domain += [('partner_id','in',partner_ids)]
        
       
        if branch_ids:
            domain += [('od_branch_id','in',branch_ids)]
        
        if a_ids:
            domain += [('id','in',a_ids)]
        
        if pm_ids:
            domain += [('od_amc_owner_id','in',pm_ids)]
        if sam_ids:
            domain += [('manager_id','in',sam_ids)]
       
        
        if date_start:
            domain += [('od_date_end_original','>=',date_start)]
        if date_end:
            domain += [('od_date_end_original','<=',date_end)]
            
        if pmo_exp_date_start:
            domain += [('od_analytic_pmo_closing','>=',pmo_exp_date_start)]
        if pmo_exp_date_end:
            domain += [('od_analytic_pmo_closing','<=',pmo_exp_date_end)]
            
        if actual_closing_start:
            domain += [('od_closing_date','>=',actual_closing_start)]
        if actual_closing_end:
            domain += [('od_closing_date','<=',actual_closing_end)]
        
        
        analytic_pool = self.env['account.analytic.account'] 
        analytic_ids = analytic_pool.search(domain)
        result  =[]
        for aa in analytic_ids:
            analytic_id  = aa.id
            sub_f,sub_l = self.get_submission_date(aa)
            po_date_f,po_date_s = self.get_po_dates(aa)
            pickin_date_f,pickin_date_s = self.get_pick_in_dates(aa)
            pickout_date_f,pickout_date_s = self.get_pick_out_dates(aa)
            if aa.od_cost_sheet_id.state != 'cancel':
                result.append((0,0,{
                    'analytic_id':analytic_id,
                    'cost_sheet_id':aa.od_cost_sheet_id and aa.od_cost_sheet_id.id or False,
                    'partner_id':aa.partner_id and aa.partner_id.id or False,
                    'sam_id':aa.manager_id and aa.manager_id.id or False,
                    'pm_id':aa.od_owner_id and aa.od_owner_id.id or False,
                    'branch_id':aa.od_branch_id and aa.od_branch_id.id or False,
                    'opp_id':aa.lead_id and aa.lead_id.id or False,
                    'lead_created_date': aa.lead_id and aa.lead_id.create_date or False,
                    'opp_date': aa.lead_id and aa.lead_id.od_req_on_7 or False,
                    'sub_date_first':sub_f,
                    'sub_date_second':sub_l,
                    'ho_date':aa.od_cost_sheet_id and aa.od_cost_sheet_id.handover_date or False,
                    'processing_date':aa.od_cost_sheet_id and aa.od_cost_sheet_id.processed_date or False,
                    'pmo_date':aa.od_cost_sheet_id and aa.od_cost_sheet_id.pmo_date or False,
                    'approve_date':aa.od_cost_sheet_id and aa.od_cost_sheet_id.approved_date or False,
                    'cust_po_status':aa.od_cost_sheet_id and aa.od_cost_sheet_id.po_status or False,
                    'cust_po_date':aa.od_cost_sheet_id and aa.od_cost_sheet_id.po_date or False,
                    'original_date_end':aa.od_date_end_original or False,
                    'pmo_closing':aa.od_analytic_pmo_closing or False,
                    'actual_closing':aa.od_closing_date or False,
                    'po_first_date':po_date_f,
                    'po_last_date':po_date_s,
                    'pick_in_first_date':pickin_date_f,
                    'pick_in_last_date':pickin_date_s,
                    'pick_out_first_date':pickout_date_f,
                    'pick_out_last_date':pickout_date_s,
                    }))
        return result
 
    @api.multi 
    def export_rpt(self):
        result = self.get_vals()
        self.wiz_line.unlink()
        self.write({'wiz_line':result})
        return {
            'domain': [('wiz_id','=',self.id)],
            'name': 'Supply Chain',
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'supply.chain.rpt.data',
            'type': 'ir.actions.act_window',
        }
    
class supply_chain_rpt_data(models.TransientModel):
    _name = 'supply.chain.rpt.data'
    wiz_id = fields.Many2one('supply.chain.rpt.wiz',string="Wizard")
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet')
    company_id = fields.Many2one('res.company',string="Company")
    partner_id = fields.Many2one('res.partner',string="Customer")
    branch_id = fields.Many2one('od.cost.branch',string="Branch")
    sam_id = fields.Many2one('res.users',string="Sale Account Manager")
    pm_id = fields.Many2one('res.users',string="Project Manager")
    in_status = fields.Selection([('pending','Pending')],string="Material In")
    out_status = fields.Selection([('pending','Pending')],string="Material Out")
    opp_id = fields.Many2one('crm.lead',string='Opportunity')
    analytic_id = fields.Many2one('account.analytic.account',string='Analytic Account')
    lead_created_date = fields.Date(string="Lead Created On")
    opp_date = fields.Date(string="Financial Proposal Required On")
    sub_date_first = fields.Date(string="Cost Sheet First Submit Date")
    sub_date_second = fields.Date(string="Cost Sheet Last Submit Date")
    ho_date = fields.Date(string="Sales Handover Date")
    processing_date = fields.Date(string="Projects Processing Date")
    pmo_date = fields.Date(string="PMO Director Approval Date")
    approve_date = fields.Date(string="Finance Approval Date")
    original_date_end = fields.Date(string="Original Closing Date")
    pmo_closing = fields.Date(string="Expected Closing")
    actual_closing = fields.Date(string="Actual Closing Date")
    po_first_date = fields.Date(string="First Supplier PO Date")
    po_last_date = fields.Date(string="Last Supplier PO Date")
    pick_in_first_date = fields.Date(string="First Material Received On")
    pick_in_last_date = fields.Date(string="Last Material Received On")
    pick_out_first_date = fields.Date(string="First Material Delivered On")
    pick_out_last_date = fields.Date(string="Last Material Delivered On")
    cust_po_status = fields.Selection([('waiting_po','Waiting P.O'),('special_approval','Special Approval From GM'),('available','Available'),('credit','Customer Credit')],'Customer PO Status')
    cust_po_date = fields.Date(string="Customer PO Date")
    
    @api.multi
    def btn_open_analytic(self):
       
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.analytic.account',
                'res_id': self.analytic_id and self.analytic_id.id or False,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }
    
    
    @api.multi
    def btn_open_po(self):
       
        return {
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'purchase.order',
                'domain':[('project_id','=',self.analytic_id.id),('state','!=','cancel')],
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
    
