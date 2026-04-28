# -*- coding: utf-8 -*-
from openerp import models, fields, api
from pprint import pprint
from datetime import datetime
import openerp.addons.decimal_precision as dp



class opp_rev_rpt_wiz(models.TransientModel):
    _name = 'opp.rev.rpt.wiz'
    
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
    product_group_ids = fields.Many2many('od.product.group',string="Technolgoy Unit",domain=[('code','in',('1','2','3','4','Cloud','5'))])
    stage_ids = fields.Many2many('crm.case.stage',string="Opp Stage",domain=[('id','not in',(6,9,1,2))],default=get_stages)
#     stage = fields.Selection([(1,'Approved'),(4,'Design Ready'),(12,'Pipeline'),(5,'Commit'),(6,'Lost'),(8,'Cancelled')],string="Opp Stage")
    
    branch_ids= fields.Many2many('od.cost.branch',string="Branch")
    cost_centre_ids = fields.Many2many('od.cost.centre',string="Cost Center")
    division_ids = fields.Many2many('od.cost.division',string="Technology Unit")
    industry_ids= fields.Many2many('od.partner.industry',string="Industry")
    
    date_start = fields.Date(string="Expected Booking Date Start")
    date_end =fields.Date(string="Expected Booking Date End")
    
    
    lead_date_start = fields.Date(string="Opp Creation Date Start")
    lead_date_end =fields.Date(string="Opp Creation Date End")
    
    submit_to_cust_date_start = fields.Date(string="Submit To Customer Date Start")
    submit_to_cust_date_end =fields.Date(string="Submit To Customer Date End")

    
    wiz_line = fields.One2many('wiz.rev.rpt.data','wiz_id',string="Wiz Line")
    
    presale_ids = fields.Many2many('res.users','wiz_pres_sale_opp_x','wiz_id','user_id',string="Pre-Sale Engineer")
    sm_ids = fields.Many2many('res.users','wiz_sale_a','wiz_id','user_id',string="Customer AM")
    lead_am_ids = fields.Many2many('res.users','wiz_lead_a3','wiz_id','user_id',string="Lead AM", default = get_lead_am_ids)
    cust_ids = fields.Many2many('res.partner','wiz_sale_cust2','wiz_id','user_id',domain=[('is_company','=',True),('customer','=',True)],string="Customer")
    owner_ids = fields.Many2many('res.users','wiz_sale_b','wiz_id','user_id',string="Owner")
    sale_team_ids = fields.Many2many('crm.case.section',string="Sales Team")
    #cust_class_ids = fields.Many2many('od.partner.class','wiz_cust_class','wiz_id','cust_id',string="Customer Class")
    copy_cust_am = fields.Boolean(string="Lead AM")
    costsheet_id = fields.Many2one('od.cost.sheet', string="Cost Sheet")
    
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
#         product_group_id = self.product_group_id and self.product_group_id.id or False
        
        stage_id = self.stage_id and self.stage_id.id or False
        branch_id = self.branch_id and self.branch_id.id or False
       
        fm_view = "od_rev_opp_tree_view_1"
        product_group_ids = [pr.id for pr in self.product_group_ids]
        if product_group_ids:
            fm_view = "od_rev_opp_tree_view"
        created_by_ids = [pr.id for pr in self.created_by_ids]
        stage_ids = [pr.id for pr in self.stage_ids]
        branch_ids = [pr.id for pr in self.branch_ids]
        cost_centre_ids = [pr.id for pr in self.cost_centre_ids]
        division_ids = [pr.id for pr in self.division_ids]
        industry_ids = [pr.id for pr in self.industry_ids]
        sm_ids = [pr.id for pr in self.sm_ids]
        lead_am_ids = [pr.id for pr in self.lead_am_ids]
        costsheet_id = self.costsheet_id and self.costsheet_id.id or False
#         cust_class_ids = [pr.id for pr in self.cust_class_ids]
#         vals = dict([(1, 'a'), (2, 'b'),(3,'c')])
#         cust_class = [vals[k] for k in cust_class_ids]
        user_id = self.env.user.id
        emp_id = self.env['hr.employee'].search([('user_id','=',user_id)])
        if emp_id.job_id.id in (40,83,182):
            sm_ids = []
            lead_am_ids = [user_id]
            
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
        
        wiz_id = self.id
        company_id = self.company_id and self.company_id.id 
        domain = [('status','=','active')]
        domain2= []
        
#         if cust_class:
#             domain2 += [('od_partner_class', 'in',cust_class)]
        
        
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
        
            
        if pre_sale_team_ids:
            domain += [('pre_sales_engineer','in',pre_sale_team_ids)]
        
        if owner_ids:
            domain += [('reviewed_id','in',owner_ids)]
        
        if date_start:
            domain += [('op_expected_booking','>=',date_start)]
        if date_end:
            domain += [('op_expected_booking','<=',date_end)]
            
        if submit_to_cust_date_start:
            domain += [('submit_to_customer_date','>=',submit_to_cust_date_start)]
        if submit_to_cust_date_end:
            domain += [('submit_to_customer_date','<=',submit_to_cust_date_end)]
        if costsheet_id:
            domain += [('id','=',costsheet_id)]

            
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
            industry_id = sheet.sudo().od_customer_id and sheet.sudo().od_customer_id.od_industry_id and sheet.sudo().od_customer_id.od_industry_id.id
            company_id = sheet.company_id and sheet.company_id.id 
            branch_id = sheet.od_branch_id and sheet.od_branch_id.id
            sam_id = sheet.lead_id and sheet.lead_id.user_id and sheet.lead_id.user_id.id
            lead_am_id = sheet.lead_id and sheet.lead_id.od_lead_user_id and sheet.lead_id.od_lead_user_id.id
            pre_sales_engineer =sheet.pre_sales_engineer and sheet.pre_sales_engineer.id
            int_note = [pr.name for pr in sheet.lead_id.od_activity_lines1]
            last_up_dte = [pr.date for pr in sheet.lead_id.od_activity_lines1]
            rebate = sheet.prn_ven_reb_cost
            if not int_note:
                int_note = ['-']
            if not last_up_dte:
                last_up_dte = [sheet.write_date]
            if product_group_ids:
                fm_view = "od_rev_opp_tree_view"
                for line in sheet.summary_weight_line:
                    if product_group_ids:
                        if line.pdt_grp_id.id in product_group_ids:
                            result.append((0,0,{
                                'wiz_id':wiz_id,
                                'cost_sheet_id':sheet_id,
                                'expected_booking':expected_booking,
                                 'mp_sales':sheet.a_total_manpower_sale,
                                'opp_id':opp_id ,
                                'opp_create_date':opp_create_date,
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
                                'pre_sales_engineer':pre_sales_engineer,
                                'sm_io':int_note[0],
                                'lst_up_dte': last_up_dte[0],
                                'rebate_amnt':rebate,
                                'cs_state': sheet.state
                                }))
                    else:
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
                                'pre_sales_engineer':pre_sales_engineer,
                                'sm_io':int_note[0],
                                'lst_up_dte': last_up_dte[0],
                                'rebate_amnt':rebate,
                                'cs_state': sheet.state
                                }))
            else:
                fm_view = "od_rev_opp_tree_view_1"
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
                                 'sam_id':sam_id,
                                 'lead_am_id':lead_am_id,
                                'total_gp':sheet.sum_profit + sheet.a_total_manpower_cost + sheet.prn_ven_reb_cost,
                                'pre_sales_engineer':pre_sales_engineer,
                                'sm_io':int_note[0],
                                'lst_up_dte': last_up_dte[0],
                                'rebate_amnt':rebate,
                                'cs_state': sheet.state
                                }))
        
        self.wiz_line.unlink()
        self.write({'wiz_line':result})
        model_data = self.env['ir.model.data']
        tree_view = model_data.get_object_reference( 'orchid_cost_sheet', fm_view)
        return {
            'domain': [('wiz_id','=',wiz_id)],
            'name': 'Pipeline Report',
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(tree_view and tree_view[1] or False, 'tree')],
            'context':{'search_default_stage':1},
            'res_model': 'wiz.rev.rpt.data',
            'type': 'ir.actions.act_window',
        }
                        
        
        
        

class wiz_rev_rpt(models.TransientModel):
    _name = 'wiz.rev.rpt.data'
    wiz_id = fields.Many2one('opp.rev.rpt.wiz',string="Wizard")
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet')
    opp_id = fields.Many2one('crm.lead',string='Opportunity')
    opp_create_date = fields.Date(string="Opp Creation Date")
    partner_id = fields.Many2one('res.partner',string="Customer")
    industry_id = fields.Many2one('od.partner.industry',string="Industry")
    bdm_user_id = fields.Many2one('res.users',string="Lead/Opp Created By")
    expected_booking = fields.Date(string="Opp Expected Booking")
    stage_id = fields.Many2one('crm.case.stage',string="Opp Stage")
    pdt_grp_id = fields.Many2one('od.product.group',string='Technology Unit')
    total_sale = fields.Float(string="Sales",digits=dp.get_precision('Account'))
    disc = fields.Float(string="Disc %",digits=dp.get_precision('Account'))
    sale_aftr_disc = fields.Float(string="Sales After Disc",digits=dp.get_precision('Account'))
    total_cost = fields.Float(string="Cost",digits=dp.get_precision('Account'))
    profit = fields.Float(string="Profit",digits=dp.get_precision('Account'))
    manpower_cost = fields.Float(string="Manpower Cost",digits=dp.get_precision('Account'))
    returned_mp = fields.Float(string="Returned MP",digits=dp.get_precision('Account'))
    total_gp = fields.Float(string="Total GP",digits=dp.get_precision('Account'))
    mp_sales = fields.Float(string="MP Sales")
    branch_id =  fields.Many2one('od.cost.branch',string="Branch")
    sam_id = fields.Many2one('res.users',string="Customer AM")
    lead_am_id = fields.Many2one('res.users',string="Lead AM")
    pre_sales_engineer =fields.Many2one('res.users',string="Pre-Sales Engineer")
    company_id = fields.Many2one('res.company',string="Company")
    od_class = fields.Selection([('a', 'A'), ('b', 'B'), ('c', 'C') ,('r', 'R')],string="Class")
    sm_io = fields.Text(string="Internal Notes")
    lst_up_dte = fields.Datetime(string="Last Update Date")
    rebate_amnt =fields.Float(string="Rebate Amount",digits=dp.get_precision('Account'))
    cs_state = fields.Selection([('draft','Opportunity'),('design_ready','Design Ready'),('submitted','Pipeline'),('commit','Commit'),('returned_by_pmo','Returned By PMO'),
                              ('handover','Hand-Over'),('waiting_po','Waiting PO Locked'),('waiting_po_open','Waiting PO Open'),('returned_by_fin','Returned By Finance'),
                              ('change','Change'),('analytic_change','Redistribute Analytic'),('processed','Processed'),('pmo','Pending Approval'),
                              ('change_processed','Change Processed'),('waiting_po_processed','Waiting PO Processed'),('redistribution_processed','Redistribution Processed'),
                              ('modify','Modify'),('approved','Approved'),('done','Won'),('cancel','Cancelled')],string="Cost Sheet Stage")
    
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