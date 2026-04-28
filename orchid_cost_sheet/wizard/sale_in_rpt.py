# -*- coding: utf-8 -*-
from openerp import models, fields, api
from pprint import pprint
from datetime import datetime
import openerp.addons.decimal_precision as dp
from openerp.exceptions import except_orm, Warning, RedirectWarning


class opp_rev_sale_in_wiz(models.TransientModel):
    _name = 'opp.sale.in.rpt.wiz'
    
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
    
    def get_product_grp(self):
        result =[]
        company_id = self.env.user.company_id.id
        if company_id ==6:
            result =[(6,0,[1,2,3,21])]
        return result
    created_by_ids = fields.Many2many('res.users',string="Created By")
#     product_group_ids = fields.Many2many('od.product.group',string="Technology Unit",domain=[('code','in',('1','2','3','4'))],default=get_product_grp)
    
    product_group_ids = fields.Many2many('od.product.group',string="Technology Unit",domain=[('code','in',('1','2','3','4','Cloud','5'))])
    
    
    branch_ids= fields.Many2many('od.cost.branch',string="Branch")
    cost_centre_ids = fields.Many2many('od.cost.centre',string="Cost Center")
    division_ids = fields.Many2many('od.cost.division',string="Technology Unit")
    industry_ids= fields.Many2many('od.partner.industry',string="Industry")
    
    date_start = fields.Date(string="Approved Date Start")
    date_end =fields.Date(string="Approved Date End")
    
    lead_date_start = fields.Date(string="Opp Creation Date Start")
    lead_date_end =fields.Date(string="Opp Creation Date End")
    
    submit_to_cust_date_start = fields.Date(string="Submit To Customer Date Start")
    submit_to_cust_date_end =fields.Date(string="Submit To Customer Date End")

    
    sm_ids = fields.Many2many('res.users','wiz_sale_x','wiz_id','user_id',string="Customer AM")
    lead_am_ids = fields.Many2many('res.users','wiz_lead_a1','wiz_id','user_id',string="Lead AM", default = get_lead_am_ids)

    cust_ids = fields.Many2many('res.partner','wiz_sale_cust5','wiz_id','user_id',domain=[('is_company','=',True),('customer','=',True)],string="Customer")
    owner_ids = fields.Many2many('res.users','wiz_sale_y','wiz_id','user_id',string="Owner")
    sale_team_ids = fields.Many2many('crm.case.section',string="Sales Team")
    presale_ids = fields.Many2many('res.users','wiz_pres_sale_sale_x','wiz_id','user_id',string="Pre-Sale Engineer")
    costsheet_id = fields.Many2one('od.cost.sheet', string="Cost Sheet")
    
    wiz_line = fields.One2many('wiz.sale.in.data','wiz_id',string="Wiz Line")
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
    def export_rpt(self):
       
        
        product_group_ids = [pr.id for pr in self.product_group_ids]
        fm_view = "od_rev_sale_in_tree_view_1"
        if product_group_ids:
            fm_view = "od_rev_sale_in_tree_view"
        
        created_by_ids = [pr.id for pr in self.created_by_ids]
        
        branch_ids = [pr.id for pr in self.branch_ids]
        cost_centre_ids = [pr.id for pr in self.cost_centre_ids]
        division_ids = [pr.id for pr in self.division_ids]
        industry_ids = [pr.id for pr in self.industry_ids]
        sm_ids = [pr.id for pr in self.sm_ids]
        lead_am_ids = [pr.id for pr in self.lead_am_ids]
        #For SAM default filling their user_id in code
        user_id = self.env.user.id
        emp_id = self.env['hr.employee'].search([('user_id','=',user_id)])
        if emp_id.job_id.id in (40,83,182):
            sm_ids = []
            lead_am_ids = [user_id]
#             if emp_id.id == 604:
#                 lead_am_ids = [user_id, 2446, 2511, 2507, 2583]
        if emp_id.id == 604:
            sm_ids = [pr.id for pr in self.sm_ids]
            lead_am_ids = [pr.id for pr in self.lead_am_ids]
        if emp_id.id == 373:
            sm_ids = [pr.id for pr in self.sm_ids]
            lead_am_ids = [pr.id for pr in self.lead_am_ids]    
                    
        cust_ids = [pr.id for pr in self.cust_ids]
        if industry_ids:
            customers = self.env['res.partner'].search([('is_company','=',True),('customer','=',True)])
            cust_ids = [pr.id for pr in customers if pr.od_industry_id.id in industry_ids ]
            
        
        owner_ids = [pr.id for pr in self.owner_ids]
        sale_team_ids = [pr.id for pr in self.sale_team_ids]
        pre_sale_team_ids = [pr.id for pr in self.presale_ids]
        
        date_start = self.date_start
        date_end =self.date_end
        
        lead_date_start = self.lead_date_start
        lead_date_end =self.lead_date_end
        submit_to_cust_date_start = self.submit_to_cust_date_start
        submit_to_cust_date_end = self.submit_to_cust_date_end
        costsheet_id = self.costsheet_id and self.costsheet_id.id or False

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
        
            
        if pre_sale_team_ids:
            domain += [('pre_sales_engineer','in',pre_sale_team_ids)]
        
        if sale_team_ids:
            domain += [('sale_team_id','in',sale_team_ids)]
        
        if owner_ids:
            domain += [('reviewed_id','in',owner_ids)]
        
        
        if date_start:
            domain += [('approved_date','>=',date_start)]
        if date_end:
            domain += [('approved_date','<=',date_end)]
            
        if submit_to_cust_date_start:
            domain += [('submit_to_customer_date','>=',submit_to_cust_date_start)]
        if submit_to_cust_date_end:
            domain += [('submit_to_customer_date','<=',submit_to_cust_date_end)]
        if costsheet_id:
            domain += [('id','=',costsheet_id)]
            
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
            industry_id = sheet.sudo().od_customer_id and sheet.sudo().od_customer_id.od_industry_id and sheet.sudo().od_customer_id.od_industry_id.id
            company_id = sheet.company_id and sheet.company_id.id 
            branch_id = sheet.od_branch_id and sheet.od_branch_id.id
            sam_id = sheet.sales_acc_manager and sheet.sales_acc_manager.id
            lead_am_id = sheet.lead_id and sheet.lead_id.od_lead_user_id and sheet.lead_id.od_lead_user_id.id
            po_status = sheet.po_status
            pre_sales_engineer =sheet.pre_sales_engineer and sheet.pre_sales_engineer.id
            rebate = sheet.prn_ven_reb_cost
            if product_group_ids:
                
                for line in sheet.summary_weight_line:
                    
                    if product_group_ids:
                        if line.pdt_grp_id.id in product_group_ids:
                            prdct_grp_id = line.pdt_grp_id.id
                            org_pdt_sale = self.env['od.cost.original.summary.group.weight'].search([('cost_sheet_id','=',sheet_id),('pdt_grp_id','=',prdct_grp_id)],limit=1)
                            if org_pdt_sale:
                                original_gp = org_pdt_sale.total_gp
                            else:
                                original_gp = 0.0
                            result.append((0,0,{
                                'wiz_id':wiz_id,
                                'cost_sheet_id':sheet_id, 
                                'opp_id':opp_id ,
                                'opp_create_date':opp_create_date,
                                'original_gp':original_gp,
                                'partner_id':partner_id,
                                'od_class':od_class,
                                'company_id':company_id,
                                'branch_id':branch_id,
                                'industry_id':industry_id,
                                'bdm_user_id':bdm_user_id ,
                                'date':date,
                                'stage_id':stage_id,
                                'pdt_grp_id':line.pdt_grp_id and line.pdt_grp_id.id,
                                'total_sale':line.total_sale,
                                'disc':line.disc,
                                'sale_aftr_disc':line.sale_aftr_disc,
                                'total_cost':line.total_cost,
                                'profit':line.profit,
                                'manpower_cost':line.manpower_cost,
                                'mp_sales':line.manpower_sale,
                                'sam_id':sam_id,
                                'lead_am_id':lead_am_id,
                                'total_gp':line.total_gp,
                                'po_status':po_status,
                                'pre_sales_engineer':pre_sales_engineer,
                                'rebate_amnt':rebate
                                }))
                    else:
                        result.append((0,0,{
                                'wiz_id':wiz_id,
                                'cost_sheet_id':sheet_id, 
                                'opp_id':opp_id ,
                                'opp_create_date':opp_create_date,
                                'partner_id':partner_id,
                                'od_class':od_class,
                                'company_id':company_id,
                                'branch_id':branch_id,
                                'industry_id':industry_id,
                                'bdm_user_id':bdm_user_id,
                                'date':date,
                                'stage_id':stage_id,
                                'pdt_grp_id':line.pdt_grp_id and line.pdt_grp_id.id,
                                'total_sale':line.total_sale,
                                'disc':line.disc,
                                'sale_aftr_disc':line.sale_aftr_disc,
                                'total_cost':line.total_cost,
                                'profit':line.profit,
                                'manpower_cost':line.manpower_cost,
                                 'mp_sales':sheet.a_total_manpower_sale,
                                 'sam_id':sam_id,
                                 'lead_am_id':lead_am_id,
                                'total_gp':line.total_gp,
                                 'po_status':po_status,
                                  'pre_sales_engineer':pre_sales_engineer,
                                  'rebate_amnt':rebate
                                }))
            else:
                original_gp = sum([cs.od_original_profit for cs in sheet.sale_order_original_line if cs.project_id.od_type_of_project not in ('amc_view','o_m_view')]) + sheet.original_mp
            


                result.append((0,0,{
                                'wiz_id':wiz_id,
                                'cost_sheet_id':sheet_id, 
                                'opp_id':opp_id ,
                                'opp_create_date':opp_create_date,
                                'partner_id':partner_id,
                                'od_class':od_class,
                                'company_id':company_id,
                                'branch_id':branch_id,
                                'industry_id':industry_id,
                                'bdm_user_id':bdm_user_id,
                                'date':date,
                                'stage_id':stage_id,
                                'pdt_grp_id':False,
                                'total_sale':sheet.sum_tot_sale,
                                'disc':abs(sheet.special_discount),
                                'sale_aftr_disc':sheet.sum_total_sale,
                                'total_cost':sheet.sum_tot_cost,
                                'profit':sheet.sum_profit,
                                'manpower_cost':sheet.a_total_manpower_cost,
                                 'mp_sales':sheet.a_total_manpower_sale,
                                 'returned_mp':sheet.returned_mp,
                                 'original_gp':original_gp + sheet.prn_ven_reb_cost,
                                 'sam_id':sam_id,
                                 'lead_am_id':lead_am_id,
                                'total_gp':sheet.total_gp + sheet.prn_ven_reb_cost,
                                 'po_status':po_status,
                                 'day_rule':sheet.sales_kpi,
                                 'over_rule':sheet.over_rule,
                                  'pre_sales_engineer':pre_sales_engineer,
                                  'rebate_amnt':rebate
                                }))
                        
        self.wiz_line.unlink()
        self.write({'wiz_line':result})
        model_data = self.env['ir.model.data']
        tree_view = model_data.get_object_reference( 'orchid_cost_sheet', fm_view)
        return {
            'domain': [('wiz_id','=',wiz_id)],
            'name': 'Sale In Report',
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(tree_view and tree_view[1] or False, 'tree')],
            'res_model': 'wiz.sale.in.data',
            'type': 'ir.actions.act_window',
        }
        
        
                        
        
        
        

class wiz_sale_in_rpt(models.TransientModel):
    _name = 'wiz.sale.in.data'
    wiz_id = fields.Many2one('opp.sale.in.rpt.wiz',string="Wizard")
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet')
    partner_id = fields.Many2one('res.partner',string="Customer")
    od_class = fields.Selection([('a', 'A'), ('b', 'B'), ('c', 'C') ,('r', 'R')],string="Class")
    company_id = fields.Many2one('res.company',string="Company")
    branch_id = fields.Many2one('od.cost.branch',string="Branch")
    industry_id = fields.Many2one('od.partner.industry',string="Industry")
    opp_id = fields.Many2one('crm.lead',string='Opportunity')
    opp_create_date = fields.Date(string="Opp Creation Date")
    bdm_user_id = fields.Many2one('res.users',string="Lead/Opp Created By")
    date = fields.Datetime(string="Approved Date")
    stage_id = fields.Many2one('crm.case.stage',string="Opp Stage")
    pdt_grp_id = fields.Many2one('od.product.group',string='Technology Unit')
    total_sale = fields.Float(string="Sales",digits=dp.get_precision('Account'))
    disc = fields.Float(string="Special Discount",digits=dp.get_precision('Account'))
    sale_aftr_disc = fields.Float(string="Sales After Disc",digits=dp.get_precision('Account'))
    total_cost = fields.Float(string="Cost",digits=dp.get_precision('Account'))
    profit = fields.Float(string="Profit",digits=dp.get_precision('Account'))
    manpower_cost = fields.Float(string="Manpower Cost",digits=dp.get_precision('Account'))
    total_gp = fields.Float(string="Total GP",digits=dp.get_precision('Account'))
    original_gp = fields.Float(string="Original GP",digits=dp.get_precision('Account'))
    returned_mp = fields.Float(string="Returned MP",digits=dp.get_precision('Account'))
    mp_sales = fields.Float(string="MP Sales")
    sam_id = fields.Many2one('res.users',string="Customer AM")
    lead_am_id = fields.Many2one('res.users',string="Lead AM")
    pre_sales_engineer =fields.Many2one('res.users',string="Pre-Sales Engineer")
    po_status = fields.Selection([('waiting_po','Waiting P.O'),('special_approval','Special Approval From GM'),('available','Available'),('credit','Customer Credit')],'Customer PO Status')
    day_rule = fields.Selection([('ok','OK'),('not_ok','Not OK'),('not_available','Not Available')],string="3-Day Rule")
    over_rule = fields.Selection([('over_rule','Over Ruled By GM')],string="Over Rule")
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