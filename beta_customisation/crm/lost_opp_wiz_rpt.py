# -*- coding: utf-8 -*-
from openerp import models, fields, api
from pprint import pprint
from datetime import datetime
import openerp.addons.decimal_precision as dp

class opp_lost_rpt_wiz(models.TransientModel):
    _name = 'opp.lost.rpt.wiz'
    
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
        return self.env['crm.case.stage'].search([('id', 'in', (7, 8, 13))]).ids
    
    wiz_line = fields.One2many('wiz.opp.lost.data','wiz_id',string="Wiz Line")
    created_by_ids = fields.Many2many('res.users',string="Created By")
    stage_ids = fields.Many2many('crm.case.stage',string="Opp Stage",domain=[('id','in',(7,8,13))], default=get_stages)
    branch_ids= fields.Many2many('od.cost.branch',string="Branch")    
    
    date_start = fields.Date(string="Expected Booking Date Start")
    date_end =fields.Date(string="Expected Booking Date End")
    
    lead_date_start = fields.Date(string="Opp Creation Date Start")
    lead_date_end =fields.Date(string="Opp Creation Date End")
    
    lost_date_start = fields.Date(string="Lost Date Start")
    lost_date_end =fields.Date(string="Lost Date End")
    
    presale_ids = fields.Many2many('res.users','wiz_pres_sale_hjk_opp_x','wiz_id','user_id',string="Pre-Sale Engineer")
    sm_ids = fields.Many2many('res.users','wiz_sale_jhk_a','wiz_id','user_id',string="Sales Account Manager")
    lead_am_ids = fields.Many2many('res.users','wiz_lead_a6','wiz_id','user_id',string="Lead AM", default = get_lead_am_ids)

    cust_ids = fields.Many2many('res.partner','wiz_sale_cust6','wiz_id','user_id',domain=[('is_company','=',True),('customer','=',True)],string="Customer")
    sale_team_ids = fields.Many2many('crm.case.section',string="Sales Team")
    
    def od_get_company_id(self):
        return self.env.user.company_id
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    
    def calculate_preopr_cost(self, lead):
        pre_op_cost =0.0
        company_id = self.company_id and self.company_id.id or False
        account_id_dxb = lead.get_product_id_from_param('pre_op_account_id')
        account_id = [6632] + [account_id_dxb]
        if company_id ==6:
            account_id = [lead.get_product_id_from_param('pre_op_account_id_ksa')]
        moveline_obj = self.env['account.move.line']
        movelines = moveline_obj.search([('od_opp_id', '=', lead.id),
                                            ('move_id.state', '<>', 'draft'), 
                                            ('account_id', 'in', account_id)])  
        if movelines:
            pre_op_cost = sum([line.debit for line in movelines])
        return pre_op_cost
    
    @api.multi 
    def export_rpt(self):
        wiz_id = self.id
        model_data = self.env['ir.model.data']
        tree_view = model_data.get_object_reference( 'beta_customisation', 'od_lost_opp_tree_view')
        
        created_by_ids = [pr.id for pr in self.created_by_ids]
        stage_ids = [pr.id for pr in self.stage_ids]
        branch_ids = [pr.id for pr in self.branch_ids]
        sm_ids = [pr.id for pr in self.sm_ids]
        lead_am_ids = [pr.id for pr in self.lead_am_ids]
        user_id = self.env.user.id
        emp_id = self.env['hr.employee'].search([('user_id','=',user_id)])
        if emp_id.job_id.id in (40,83):
            sm_ids = [user_id]
        
        if emp_id.id == 604:
            sm_ids = [pr.id for pr in self.sm_ids]
            lead_am_ids = [pr.id for pr in self.lead_am_ids]
        
        if emp_id.id == 373:
            sm_ids = [pr.id for pr in self.sm_ids]
            lead_am_ids = [pr.id for pr in self.lead_am_ids]
        
        cust_ids = [pr.id for pr in self.cust_ids]
        date_start = self.date_start
        date_end =self.date_end
        lead_date_start = self.lead_date_start
        lead_date_end =self.lead_date_end
        
        lost_date_start = self.lost_date_start
        lost_date_end =self.lost_date_end
         
        wiz_id = self.id
        company_id = self.company_id and self.company_id.id 
        domain =[]
        if company_id:
            domain += [('company_id','=',company_id)]
        if created_by_ids:
            domain += [('create_uid','in',created_by_ids)]
        if stage_ids:
            domain += [('stage_id','in',stage_ids)]
       
        if branch_ids:
            domain += [('od_branch_id','in',branch_ids)]
       
                    
        if sm_ids:
            domain += [('user_id','in',sm_ids)]
            
        if lead_am_ids:
            domain += [('od_lead_user_id', 'in',lead_am_ids)]
            
        if cust_ids:
            domain += [('partner_id','in',cust_ids)]
        
        if date_start:
            domain += [('date_action','>=',date_start)]
        if date_end:
            domain += [('date_action','<=',date_end)]
        
        if lead_date_start:
            domain += [('create_date','>=',lead_date_start)]
        if lead_date_end:
            domain += [('create_date','<=',lead_date_end)]
            
        
        if lost_date_start:
            domain += [('lost_date','>=',lost_date_start)]
        if lost_date_end:
            domain += [('lost_date','<=',lost_date_end)]
            
        lead_data = self.env['crm.lead'].search(domain) 
        result =[]
        for lead in lead_data:
            
            opp_id = lead.id
            name = lead.name 
            created_on = lead.create_date
            created_by_id = lead.create_uid and lead.create_uid.id 
            expected_booking = lead.date_action 
            stage_id = lead.stage_id and lead.stage_id.id 
            partner_id = lead.partner_id and lead.partner_id.id
            od_class = lead.partner_id and lead.partner_id.od_class 
            company_id = lead.company_id and lead.company_id.id 
            branch_id = lead.od_branch_id and lead.od_branch_id.id
            division_id = lead.od_division_id and lead.od_division_id.id
            sam_id = lead.user_id and lead.user_id.id
            lead_am_id = lead.od_lead_user_id and lead.od_lead_user_id.id or False
            type = lead.type 
            cost_sheet = self.env['od.cost.sheet'].search([('lead_id','=',lead.id),('status','=','active')],limit=1)
            sheet_id = cost_sheet and cost_sheet.id
            mp_sales = cost_sheet and cost_sheet.a_total_manpower_sale or 0.0
            rebate = cost_sheet and cost_sheet.prn_ven_reb_cost or 0.0
            returned_mp = cost_sheet and cost_sheet.returned_mp or 0.0
            cs_sale = cost_sheet and cost_sheet.sum_total_sale or 0.0
            pre_oprn_amt = self.calculate_preopr_cost(lead)
            profit_mp =0.0
            if cost_sheet:
                profit_mp = cost_sheet.total_gp + rebate
            result.append((0,0,{
                                'wiz_id':wiz_id,
                                'cost_sheet_id':sheet_id, 
                                 'expected_booking':expected_booking,
                                'opp_id':opp_id ,
                                'name':name,
                                'partner_id':partner_id,
                                'company_id':company_id,
                                'branch_id':branch_id,
                                'od_class':od_class,
                                'opp_create_date':created_on,
                                'create_user_id':created_by_id,
                                'division_id':division_id,
                                'lost_date':lead.lost_date,
                                'type':type,
                                'stage_id':stage_id,
                                'sale_aftr_disc':cs_sale,
                                 'mp_sales':mp_sales,
                                 'sam_id':sam_id,
                                 'lead_am_id':lead_am_id,
                                'pre_sales_engineer': cost_sheet.prepared_by and cost_sheet.prepared_by.id or False,
                                'profit':profit_mp,
                                'sm_io1' :lead.sm_io1,
                                'sm_io2':lead.sm_io2,
                                'tum_io1':lead.tum_io1,
                                'tum_io2':lead.tum_io2,
                                'returned_mp':returned_mp,
                                'rebate_amnt':rebate,
                                'pre_oprn_amt': pre_oprn_amt
                                
                                }))
        
        self.wiz_line.unlink()
        self.write({'wiz_line':result})
        
        return {
            'domain': [('wiz_id','=',wiz_id)],
            'name': 'Lost/Cancelled Opportunities Report',
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(tree_view and tree_view[1] or False, 'tree')],
            'res_model': 'wiz.opp.lost.data',
            'type': 'ir.actions.act_window',
        }

                        
class opp_lost_rpt(models.TransientModel):
    _name = 'wiz.opp.lost.data'
    
    wiz_id = fields.Many2one('opp.lost.rpt.wiz',string="Wizard")
    opp_create_date = fields.Date(string="Opp Creation Date")
    expected_booking = fields.Date(string="Opp Expected Booking")
    lost_date = fields.Date(string="Lost Date")
    branch_id =  fields.Many2one('od.cost.branch',string="Branch")
    pdt_grp_id = fields.Many2one('od.product.group',string='Technology Unit')
    partner_id = fields.Many2one('res.partner',string="Customer")
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet')
    opp_id = fields.Many2one('crm.lead',string='Opportunity')
    create_user_id = fields.Many2one('res.users',string="Lead/Opp Created By")
    sam_id = fields.Many2one('res.users',string="Customer AM")
    lead_am_id = fields.Many2one('res.users',string="Lead AM")
    pre_sales_engineer =fields.Many2one('res.users',string="Pre-Sales Engineer")
    sale_aftr_disc = fields.Float(string="Sales",digits=dp.get_precision('Account'))
    profit = fields.Float(string="Profit with MP",digits=dp.get_precision('Account'))
    mp_sales = fields.Float(string="MP Sales")
    returned_mp = fields.Float(string="Returned MP")
    rebate_amnt = fields.Float(string="Rebate Amount")
    company_id = fields.Many2one('res.company',string="Company")
    sm_io1 = fields.Text(string="GM/Sales Manager Input")
    sm_io2 = fields.Text(string="GM/Sales Manager Input")
    tum_io1 = fields.Text(string="Technology Unit Manager Input")
    tum_io2 = fields.Text(string="Technology Unit Manager Input")
    pre_oprn_amt = fields.Float(string="Pre-Operation Cost")
    od_class = fields.Selection([('a', 'A'), ('b', 'B'), ('c', 'C') ,('r', 'R')],string="Class")
    
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
    