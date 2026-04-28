# -*- coding: utf-8 -*-
from openerp import models, fields, api
from pprint import pprint
from datetime import datetime
import openerp.addons.decimal_precision as dp
from openerp.exceptions import Warning

class opp_rev_brand_rpt_wiz(models.TransientModel):
    _name = 'opp.rev.brand.rpt.wiz'
    
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
    
    @api.model
    def get_stages(self):
        return self.env['crm.case.stage'].search([('id', 'in', (4,5,12,14))]).ids
    
    bdm_id = fields.Many2one('res.users',string="BDM")
#     product_group_id = fields.Many2one('od.product.group',string="Technolgoy Unit",domain=[('code','in',('1','2','3','4'))])
    stage_id = fields.Many2one('crm.case.stage',string="Opp Stage")
    branch_id = fields.Many2one('od.cost.branch',string="Branch")
    cost_centre_id = fields.Many2one('od.cost.centre',string="Cost Center")
    division_id = fields.Many2one('od.cost.division',string="Technology Unit")
    
    created_by_ids = fields.Many2many('res.users',string="Created By")
#     product_group_ids = fields.Many2many('od.product.group',string="Technolgoy Unit",domain=[('code','in',('1','2','3','4'))],default=[(6,0,[1,2,3,21])])
    product_brand_ids = fields.Many2many('od.product.brand',string="Product Brand")
    stage_ids = fields.Many2many('crm.case.stage',string="Opp Stage",domain=[('id','not in',(6,9,1,2))], default=get_stages)
#     stage = fields.Selection([(1,'Approved'),(4,'Design Ready'),(12,'Pipeline'),(5,'Commit'),(6,'Lost'),(8,'Cancelled')],string="Opp Stage")
    
    branch_ids= fields.Many2many('od.cost.branch',string="Branch")
    cost_centre_ids = fields.Many2many('od.cost.centre',string="Cost Center")
    division_ids = fields.Many2many('od.cost.division',string="Technology Unit")
    
    date_start = fields.Date(string="Expected Booking Date Start")
    date_end =fields.Date(string="Expected Booking Date End")
    
    
    lead_date_start = fields.Date(string="Opp Creation Date Start")
    lead_date_end =fields.Date(string="Opp Creation Date End")
    
    wiz_line = fields.One2many('wiz.rev.brand.rpt.data','wiz_id',string="Wiz Line")
    
     
    sm_ids = fields.Many2many('res.users','wiz_sale_a','wiz_id','user_id',string="Customer AM")
    lead_am_ids = fields.Many2many('res.users','wiz_lead_a4','wiz_id','user_id',string="Lead AM", default = get_lead_am_ids)
    cust_ids = fields.Many2many('res.partner','wiz_sale_cust4','wiz_id','user_id',domain=[('is_company','=',True),('customer','=',True)],string="Customer")
    owner_ids = fields.Many2many('res.users','wiz_sale_b','wiz_id','user_id',string="Owner")
    sale_team_ids = fields.Many2many('crm.case.section',string="Sales Team")
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
                'res_model': 'opp.rev.brand.rpt.wiz',
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
                'res_model': 'opp.rev.brand.rpt.wiz',
                'res_id': self.id,
                'view_id': False,
                'type': 'ir.actions.act_window',
                'target': 'new',
                }
    
    @api.multi 
    def export_rpt(self):
        if not self.product_brand_ids:
            raise Warning("Please Select Product Brands")
        
        stage_id = self.stage_id and self.stage_id.id or False
        branch_id = self.branch_id and self.branch_id.id or False
       
        fm_view = "od_rev_opp_tree_view_1"
        product_brand_ids = [pr.id for pr in self.product_brand_ids]
#         if product_group_ids:
#             fm_view = "od_rev_opp_tree_view"
        created_by_ids = [pr.id for pr in self.created_by_ids]
        stage_ids = [pr.id for pr in self.stage_ids]
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
        domain = [('status','=','active')]
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
        if stage_ids:
            domain += [('op_stage_id','in',stage_ids)]
        if not stage_ids:
            domain += [('op_stage_id','!=',6)]
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
            domain += [('op_expected_booking','>=',date_start)]
        if date_end:
            domain += [('op_expected_booking','<=',date_end)]
            
        cost_sheet_data = self.env['od.cost.sheet'].search(domain)
        result =[]
        for sheet in cost_sheet_data:
            sheet_id = sheet.id
            opp_id = sheet.lead_id and sheet.lead_id.id 
            opp_create_date = sheet.lead_id and sheet.lead_id.create_date
            date = sheet.approved_date
            expected_booking = sheet.lead_id and sheet.lead_id.date_action 
            stage_id = sheet.op_stage_id and sheet.op_stage_id.id
            bdm_user_id = sheet.lead_created_by and sheet.lead_created_by.id
            partner_id = sheet.sudo().od_customer_id and sheet.sudo().od_customer_id.id
            od_class = sheet.sudo().od_customer_id and sheet.sudo().od_customer_id.od_class
            company_id = sheet.company_id and sheet.company_id.id 
            branch_id = sheet.od_branch_id and sheet.od_branch_id.id
            sam_id = sheet.lead_id and sheet.lead_id.user_id and sheet.lead_id.user_id.id
            lead_am_id = sheet.lead_id and sheet.lead_id.od_lead_user_id and sheet.lead_id.od_lead_user_id.id
            int_note = [pr.name for pr in sheet.lead_id.od_activity_lines1]
            last_up_dte = [pr.date for pr in sheet.lead_id.od_activity_lines1]
            rebate = sheet.prn_ven_reb_cost
            if not int_note:
                int_note = ['-']
            if not last_up_dte:
                last_up_dte = [sheet.write_date]
            if product_brand_ids:
                fm_view = "od_rev_opp_tree_view"
                for line in sheet.mat_brand_weight_line:
                    if line.manufacture_id.id in product_brand_ids:
                        result.append((0,0,{
                                'wiz_id':wiz_id,
                                'cost_sheet_id':sheet_id,
                                'expected_booking':expected_booking,
                                'opp_id':opp_id ,
                                'opp_create_date':opp_create_date,
                                'partner_id':partner_id,
                                'od_class':od_class,
                                'company_id':company_id,
                                'branch_id':branch_id,
                                'bdm_user_id':bdm_user_id ,
                                'date':date,
                                'stage_id':stage_id,
                                'product_brand_id':line.manufacture_id and line.manufacture_id.id,
                                'total_sale':line.total_sale,
                                'sale_aftr_disc': line.total_sale_after_disc,
                                'total_cost':line.total_cost,
                                'profit':line.profit,
                                'sam_id':sam_id,
                                'lead_am_id':lead_am_id,
                                'sm_io':int_note[0],
                                'lst_up_dte': last_up_dte[0],
                                'rebate_amnt':rebate
                                }))
             
        self.wiz_line.unlink()
        self.write({'wiz_line':result})
#         model_data = self.env['ir.model.data']
#         tree_view = model_data.get_object_reference( 'orchid_cost_sheet', fm_view)
        return {
            'domain': [('wiz_id','=',wiz_id)],
            'name': 'Pipeline Brand Report',
            'view_type': 'form',
            'view_mode': 'tree',
#             'views': [(tree_view and tree_view[1] or False, 'tree')],
            'res_model': 'wiz.rev.brand.rpt.data',
            'type': 'ir.actions.act_window',
        }
                        
        
        
        

class wiz_rev_brand_rpt(models.TransientModel):
    _name = 'wiz.rev.brand.rpt.data'
    wiz_id = fields.Many2one('opp.rev.brand.rpt.wiz',string="Wizard")
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet')
    opp_id = fields.Many2one('crm.lead',string='Opportunity')
    opp_create_date = fields.Date(string="Opp Creation Date")
    partner_id = fields.Many2one('res.partner',string="Customer")
    bdm_user_id = fields.Many2one('res.users',string="Lead/Opp Created By")
    expected_booking = fields.Date(string="Opp Expected Booking")
    stage_id = fields.Many2one('crm.case.stage',string="Opp Stage")
    product_brand_id = fields.Many2one('od.product.brand',string='Product Brand')
    total_sale = fields.Float(string="Sales",digits=dp.get_precision('Account'))
    disc = fields.Float(string="Disc %",digits=dp.get_precision('Account'))
    sale_aftr_disc = fields.Float(string="Sales After Disc",digits=dp.get_precision('Account'))
    total_cost = fields.Float(string="Cost",digits=dp.get_precision('Account'))
    profit = fields.Float(string="Profit",digits=dp.get_precision('Account'))
    manpower_cost = fields.Float(string="Manpower Cost",digits=dp.get_precision('Account'))
    total_gp = fields.Float(string="Total GP",digits=dp.get_precision('Account'))
    mp_sales = fields.Float(string="MP Sales")
    branch_id =  fields.Many2one('od.cost.branch',string="Branch")
    sam_id = fields.Many2one('res.users',string="Customer AM")
    lead_am_id = fields.Many2one('res.users',string="Lead AM")
    company_id = fields.Many2one('res.company',string="Company")
    od_class = fields.Selection([('a', 'A'), ('b', 'B'), ('c', 'C'), ('r', 'R')],string="Class")
    sm_io = fields.Text(string="Internal Notes")
    lst_up_dte = fields.Datetime(string="Last Update Date")
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