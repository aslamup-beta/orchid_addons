# -*- coding: utf-8 -*-
from openerp import models, fields, api
from pprint import pprint
from datetime import datetime
import openerp.addons.decimal_precision as dp
from openerp.exceptions import Warning

class opp_rev_sale_in_brand_wiz(models.TransientModel):
    _name = 'opp.sale.in.brand.rpt.wiz'
    
    @api.model
    def get_lead_am_ids(self):
        user_ids = []
        hr_pool = self.env['hr.employee']
        if self.env.user.id == 134:
            emp_ids = hr_pool.search([('od_branch_id', '=', 6),('job_id', 'in', (140,182,83,104))])
            for employee in emp_ids:
                user_ids.append(employee.user_id.id)
        if self.env.user.id == 2429:
            emp_ids = hr_pool.search([('od_branch_id', '=', 4),('parent_id', '=', 594),('job_id', 'in', (182,83))])
            user_ids = [2429]
            for employee in emp_ids:
                user_ids.append(employee.user_id.id)
        if self.env.user.id == 2663:
            emp_ids = hr_pool.search([('od_branch_id', '=', 4),('parent_id', '=', 828),('job_id', 'in', (182,83))])
            user_ids = [2663]
            for employee in emp_ids:
                user_ids.append(employee.user_id.id)
        if self.env.user.id == 2441:
            emp_ids = hr_pool.search([('od_branch_id', '=', 4),('parent_id', '=', 611),('job_id', 'in', (182,83))])
            user_ids = [2441]
            for employee in emp_ids:
                user_ids.append(employee.user_id.id)
        if self.env.user.id == 2536:
            emp_ids = hr_pool.search([('od_branch_id', '=', 4),('parent_id', '=', 703),('job_id', 'in', (182,83))])
            user_ids = [2536]
            for employee in emp_ids:
                user_ids.append(employee.user_id.id)
        if self.env.user.id == 2434:
            emp_ids = hr_pool.search([('coach_id', '=', 604),('job_id', '=', 40)])
            user_ids = [2434]
            for employee in emp_ids:
                user_ids.append(employee.user_id.id)
        if self.env.user.id == 2186:
            emp_ids = hr_pool.search([('coach_id', '=', 373),('job_id', '=', 40)])
            user_ids = [2186]
            for employee in emp_ids:
                user_ids.append(employee.user_id.id)
        return user_ids
    

    created_by_ids = fields.Many2many('res.users',string="Created By")
#     product_group_ids = fields.Many2many('od.product.group',string="Technology Unit",domain=[('code','in',('1','2','3','4'))],default=get_product_grp)
    
#     product_brand_ids = fields.Many2many('od.product.brand',string="Product Brand",required=True)
    created_by_ids = fields.Many2many('res.users',string="Created By")    
    product_brand_ids = fields.Many2many('od.product.brand',string="Product Brand")

    
    
    branch_ids= fields.Many2many('od.cost.branch',string="Branch")
    cost_centre_ids = fields.Many2many('od.cost.centre',string="Cost Center")
    division_ids = fields.Many2many('od.cost.division',string="Technology Unit")
    
    date_start = fields.Date(string="Approved Date Start")
    date_end =fields.Date(string="Approved Date End")
    
    lead_date_start = fields.Date(string="Opp Creation Date Start")
    lead_date_end =fields.Date(string="Opp Creation Date End")
    
    sm_ids = fields.Many2many('res.users','wiz_sale_brand_x','wiz_id','user_id',string="Customer AM")
    lead_am_ids = fields.Many2many('res.users','wiz_lead_a2','wiz_id','user_id',string="Lead AM", default = get_lead_am_ids)
    cust_ids = fields.Many2many('res.partner','wiz_sale_cust1','wiz_id','user_id',domain=[('is_company','=',True),('customer','=',True)],string="Customer")
    owner_ids = fields.Many2many('res.users','wiz_sale_brand_y','wiz_id','user_id',string="Owner")
    sale_team_ids = fields.Many2many('crm.case.section',string="Sales Team")
    
    wiz_line = fields.One2many('wiz.sale.in.brand.data','wiz_id',string="Wiz Line")
    
    copy_cust_am = fields.Boolean(string="Lead AM")
    
#     @api.onchange('sm_ids','copy_cust_am')
#     def onchange_copy_cust_am(self):
#         if self.copy_cust_am:
#             p_ids = [pr.id for pr in self.sm_ids]
#             self.lead_am_ids = [(6,0,p_ids)]
#         else:
#             self.lead_am_ids = [(6,0,[])]
    
    def od_get_company_id(self):
        return self.env.user.company_id
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    
    @api.multi
    def od_load_brands(self):
        prod_brands = self.env['od.product.brand'].search([])
        brand_ids = [brand.id for brand in prod_brands]
        self.product_brand_ids = [[6,False,brand_ids]]
        return {
                'context': self.env.context,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'opp.sale.in.brand.rpt.wiz',
                'res_id': self.id,
                'view_id': False,
                'type': 'ir.actions.act_window',
                'target': 'new',
                }
        
    @api.multi
    def od_clear_brands(self):
        self.product_brand_ids = [[6,False,[]]]
        return {
                'context': self.env.context,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'opp.sale.in.brand.rpt.wiz',
                'res_id': self.id,
                'view_id': False,
                'type': 'ir.actions.act_window',
                'target': 'new',
                }
                                                
    
    @api.multi 
    def export_rpt(self):
        if not self.product_brand_ids:
            raise Warning("Please Select Product Brands")  
        
        brand_ids = [pr.id for pr in self.product_brand_ids]
        fm_view = "od_rev_sale_in_tree_view_1"
        
        
        created_by_ids = [pr.id for pr in self.created_by_ids]
        
        branch_ids = [pr.id for pr in self.branch_ids]
        cost_centre_ids = [pr.id for pr in self.cost_centre_ids]
        division_ids = [pr.id for pr in self.division_ids]
        sm_ids = [pr.id for pr in self.sm_ids]
        lead_am_ids = [pr.id for pr in self.lead_am_ids]
        user_id = self.env.user.id
        emp_id = self.env['hr.employee'].search([('user_id','=',user_id)])
        if emp_id.job_id.id in (40,83):
            sm_ids = []
            lead_am_ids = [user_id]
            
        if emp_id.id == 604:
            sm_ids = [pr.id for pr in self.sm_ids]
            lead_am_ids = [pr.id for pr in self.lead_am_ids]
        
        cust_ids = [pr.id for pr in self.cust_ids]
        owner_ids = [pr.id for pr in self.owner_ids]
        sale_team_ids = [pr.id for pr in self.sale_team_ids]
        
        
        date_start = self.date_start
        date_end =self.date_end 
        
        lead_date_start = self.lead_date_start
        lead_date_end =self.lead_date_end 
        wiz_id = self.id
        company_id = self.company_id and self.company_id.id 
        domain = [('status','=','active'),('state','in',('approved','done','modify','change','analytic_change','change_processed','redistribution_processed'))]
        domain2= []
        
        
        if lead_date_start:
            domain2 += [('create_date','>=',lead_date_start)]
        if lead_date_end:
            domain2 += [('create_date','<=',lead_date_end)]
        
        if domain2:
            lead_data =self.env['crm.lead'].search(domain2)
            lead_ids = [ld.id for ld in lead_data]
            domain += [('lead_id','in',lead_ids)] 
        
        if company_id:
            domain += [('company_id','=',company_id)]
        if created_by_ids:
            domain += [('lead_created_by','in',created_by_ids)]
        
        if branch_ids:
            domain += [('od_branch_id','in',branch_ids)]
        if cost_centre_ids:
            domain += [('od_cost_centre_id','in',cost_centre_ids)]
        if division_ids:
            domain += [('od_division_id','in',division_ids)]
            
        if sm_ids:
            domain += [('sales_acc_manager','in',sm_ids)]
            
        if lead_am_ids:
            domain += [('lead_acc_manager', 'in',lead_am_ids)]
            
        if cust_ids:
            domain += [('od_customer_id','in',cust_ids)]
        
        if sale_team_ids:
            domain += [('sale_team_id','in',sale_team_ids)]
        
        if owner_ids:
            domain += [('reviewed_id','in',owner_ids)]
        
        
        if date_start:
            domain += [('approved_date','>=',date_start)]
        if date_end:
            domain += [('approved_date','<=',date_end)]
            
        cost_sheet_data = self.env['od.cost.sheet'].search(domain) 
        result =[]
        analytic_pool = self.env['account.analytic.account']
        for sheet in cost_sheet_data:
            sheet_id = sheet.id
            analytic = analytic_pool.search([('od_cost_sheet_id','=',sheet_id)],limit=1)
            analytic_state = analytic and analytic.state
            if analytic_state =='cancelled':
                continue
            opp_id = sheet.lead_id and sheet.lead_id.id 
            opp_create_date = sheet.lead_id and sheet.lead_id.create_date
            date = sheet.approved_date 
            stage_id = sheet.op_stage_id and sheet.op_stage_id.id
            bdm_user_id = sheet.lead_created_by and sheet.lead_created_by.id
            partner_id = sheet.sudo().od_customer_id and sheet.sudo().od_customer_id.id
            od_class = sheet.sudo().od_customer_id and sheet.sudo().od_customer_id.od_class
            company_id = sheet.company_id and sheet.company_id.id 
            branch_id = sheet.od_branch_id and sheet.od_branch_id.id
            sam_id = sheet.sales_acc_manager and sheet.sales_acc_manager.id
            lead_am_id = sheet.lead_id and sheet.lead_id.od_lead_user_id and sheet.lead_id.od_lead_user_id.id
            po_status = sheet.po_status
            rebate = sheet.prn_ven_reb_cost
            if brand_ids:
                for line in sheet.mat_brand_weight_line:
                    if line.manufacture_id.id in brand_ids:
                            result.append((0,0,{
                                'wiz_id':wiz_id,
                                'cost_sheet_id':sheet_id, 
                                'opp_id':opp_id ,
                                'opp_create_date':opp_create_date,
                                'partner_id':partner_id,
                                'od_class':od_class,
                                'company_id':company_id,
                                'branch_id':branch_id,
                                'bdm_user_id':bdm_user_id ,
                                'date':date,
                                'stage_id':stage_id,
                                'brand_id':line.manufacture_id and line.manufacture_id.id,
                                'total_sale':line.total_sale,
                                'sale_aftr_disc': line.total_sale_after_disc,
                                'sup_cost':line.sup_cost,
                                'total_cost':line.total_cost,
                                'profit':line.profit,
                                'sam_id':sam_id,
                               'lead_am_id':lead_am_id,
                                'po_status':po_status,
                                'rebate_amnt':rebate
                                }))
                    
            
                        
        self.wiz_line.unlink()
        self.write({'wiz_line':result})
        model_data = self.env['ir.model.data']
#         tree_view = model_data.get_object_reference( 'orchid_cost_sheet', fm_view)
        return {
            'domain': [('wiz_id','=',wiz_id)],
            'name': 'Brand Sale In Report',
            'view_type': 'form',
            'view_mode': 'tree',
#             'views': [(tree_view and tree_view[1] or False, 'tree')],
            'res_model': 'wiz.sale.in.brand.data',
            'type': 'ir.actions.act_window',
        }
        
        
         

class wiz_sale_in_brand_rpt(models.TransientModel):
    _name = 'wiz.sale.in.brand.data'
    
    wiz_id = fields.Many2one('opp.sale.in.brand.rpt.wiz',string="Wizard")
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet')
    partner_id = fields.Many2one('res.partner',string="Customer")
    od_class = fields.Selection([('a', 'A'), ('b', 'B'), ('c', 'C') ,('r', 'R')],string="Class")
    company_id = fields.Many2one('res.company',string="Company")
    branch_id = fields.Many2one('od.cost.branch',string="Branch")
    opp_id = fields.Many2one('crm.lead',string='Opportunity')
    opp_create_date = fields.Date(string="Opp Creation Date")
    bdm_user_id = fields.Many2one('res.users',string="Lead/Opp Created By")
    date = fields.Datetime(string="Approved Date")
    stage_id = fields.Many2one('crm.case.stage',string="Opp Stage")
    brand_id = fields.Many2one('od.product.brand',string='Brand')
    total_sale = fields.Float(string="Sales",digits=dp.get_precision('Account'))
    sale_aftr_disc = fields.Float(string="Sales After Discount",digits=dp.get_precision('Account'))
    sup_cost = fields.Float(string="Supplier Discounted Price",digits=dp.get_precision('Account'))
    total_cost = fields.Float(string="Total Cost",digits=dp.get_precision('Account'))
    profit = fields.Float(string="Profit",digits=dp.get_precision('Account'))
    total_gp = fields.Float(string="Total GP",digits=dp.get_precision('Account'))
    original_gp = fields.Float(string="Original GP",digits=dp.get_precision('Account'))
    sam_id = fields.Many2one('res.users',string="Customer AM")
    lead_am_id = fields.Many2one('res.users',string="Lead AM")
    po_status = fields.Selection([('waiting_po','Waiting P.O'),('special_approval','Special Approval From GM'),('available','Available'),('credit','Customer Credit')],'Customer PO Status')
    day_rule = fields.Selection([('ok','OK'),('not_ok','Not OK'),('not_available','Not Available')],string="3-Day Rule")
    rebate_amnt =fields.Float(string="Rebate Amount",digits=dp.get_precision('Account'))
    
    @api.multi
    def btn_open_opp(self):
       
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'crm.lead',
                'res_id':self.opp_id and self.opp_id.id or False,
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