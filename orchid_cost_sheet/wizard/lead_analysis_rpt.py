# -*- coding: utf-8 -*-
from openerp import models, fields, api
from pprint import pprint
from datetime import datetime
import openerp.addons.decimal_precision as dp

class lead_analysis_rpt_wiz(models.TransientModel):
    _name = 'lead.analysis.rpt.wiz'
    
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
    stage_ids = fields.Many2many('crm.case.stage',string="Opp Stage",domain=[('id','!=',6)])    
    branch_ids= fields.Many2many('od.cost.branch',string="Branch")
    date_start = fields.Date(string="Expected Booking Date Start")
    date_end =fields.Date(string="Expected Booking Date End")
    lead_date_start = fields.Date(string="Created On Start")
    lead_date_end =fields.Date(string="Created On End")
    sm_ids = fields.Many2many('res.users','wiz_sale_a','wiz_id','user_id',string="Customer AM")
    lead_am_ids = fields.Many2many('res.users','wiz_lead_a5','wiz_id','user_id',string="Lead AM", default = get_lead_am_ids)
    cust_ids = fields.Many2many('res.partner','wiz_sale_cust3','wiz_id','user_id',domain=[('is_company','=',True),('customer','=',True)],string="Customer")
    wiz_line = fields.One2many('wiz.lead.analysis.data','wiz_id',string="Wiz Line")

    def od_get_company_id(self):
        return self.env.user.company_id
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    @api.multi 
    def export_rpt(self):
        created_by_ids = [pr.id for pr in self.created_by_ids]
        stage_ids = [pr.id for pr in self.stage_ids]
        branch_ids = [pr.id for pr in self.branch_ids]
        sm_ids = [pr.id for pr in self.sm_ids]
        lead_am_ids = [pr.id for pr in self.lead_am_ids]
        user_id = self.env.user.id
        emp_id = self.env['hr.employee'].search([('user_id','=',user_id)])
        if emp_id.job_id.id in (40,83):
            sm_ids = []
            lead_am_ids =[user_id]
        cust_ids = [pr.id for pr in self.cust_ids]
        
        date_start = self.date_start
        date_end =self.date_end
        lead_date_start = self.lead_date_start
        lead_date_end =self.lead_date_end 
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
            company_id = lead.company_id and lead.company_id.id 
            branch_id = lead.od_branch_id and lead.od_branch_id.id
            division_id = lead.od_division_id and lead.od_division_id.id
            sam_id = lead.user_id and lead.user_id.id
            lead_am_id = lead.od_lead_user_id and lead.od_lead_user_id.id or False

            type = lead.type 
            cost_sheet = self.env['od.cost.sheet'].search([('lead_id','=',lead.id),('status','=','active')],limit=1)
            sheet_id = cost_sheet and cost_sheet.id
            mp_sales = cost_sheet and cost_sheet.a_total_manpower_sale or 0.0
            returned_mp = cost_sheet and cost_sheet.returned_mp or 0.0
            rebate_amnt = cost_sheet and cost_sheet.prn_ven_reb_cost or 0.0
            int_note = [pr.name for pr in lead.od_activity_lines1]
            last_up_dte = [pr.date for pr in lead.od_activity_lines1]
            if not int_note:
                int_note = ['-']
            if not last_up_dte:
                last_up_dte = [lead.write_date]
            profit_mp =0.0
            if cost_sheet:
                profit_mp = cost_sheet.sum_profit + cost_sheet.a_total_manpower_cost + rebate_amnt
            result.append((0,0,{
                                'wiz_id':wiz_id,
                                'cost_sheet_id':sheet_id, 
                                 'expected_booking':expected_booking,
                                'opp_id':opp_id ,
                                'name':name,
                                'partner_id':partner_id,
                                'company_id':company_id,
                                'branch_id':branch_id,
                                'created_on':created_on,
                                'created_by_id':created_by_id,
                                'division_id':division_id,
                                'type':type,
                                'stage_id':stage_id,
                                'cs_sale':lead.od_costsheet_sale,
                                 'mp_sales':mp_sales,
                                 'returned_mp':returned_mp,
                                 'sam_id':sam_id,
                                 'lead_am_id':lead_am_id,
                                'profit_mp':profit_mp,
                                'rebate_amnt':rebate_amnt,
                                'sm_io':int_note[0],
                                'lst_up_dte': last_up_dte[0],
                                }))
        
        self.wiz_line.unlink()
        self.write({'wiz_line':result})
        return {
            'domain': [('wiz_id','=',wiz_id)],
            'name': 'Lead Analysis',
            'view_type': 'form',
            'view_mode': 'tree',
            'context':{'search_default_stage':1},
            'res_model': 'wiz.lead.analysis.data',
            'type': 'ir.actions.act_window',
        }
                        
        
        
        

class wiz_lead_analysis_rpt(models.TransientModel):
    _name = 'wiz.lead.analysis.data'
    wiz_id = fields.Many2one('lead.analysis.rpt.wiz',string="Wizard")
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Active Cost Sheet',)
    opp_id = fields.Many2one('crm.lead',string='Opportunity')
    name = fields.Char(string="Name")
    type = fields.Selection([('lead','Lead'),('opportunity','Opportunity')],string="Type")
    created_on = fields.Datetime(string="Created On")
    partner_id = fields.Many2one('res.partner',string="Customer")
    created_by_id = fields.Many2one('res.users',string="Lead/Opp Created By")
    expected_booking = fields.Date(string="Opp Expected Booking")
    submitted_on =fields.Date(string="Submitted To Customer")
    stage_id = fields.Many2one('crm.case.stage',string="Opp Stage")
    cs_sale = fields.Float(string="CS Sales",digits=dp.get_precision('Account'))
    profit_mp = fields.Float(string="Profit With MP",digits=dp.get_precision('Account'))
    returned_mp = fields.Float(string="Returned MP",digits=dp.get_precision('Account'))
    mp_sales = fields.Float(string="MP Sales")
    branch_id =  fields.Many2one('od.cost.branch',string="Branch")
    division_id =  fields.Many2one('od.cost.division',string="Technology Unit")
    sam_id = fields.Many2one('res.users',string="Customer AM")
    lead_am_id = fields.Many2one('res.users',string="Lead AM")
    company_id = fields.Many2one('res.company',string="Company")
    rebate_amnt =fields.Float(string="Rebate Amount",digits=dp.get_precision('Account'))
    sm_io = fields.Text(string="Internal Notes")
    lst_up_dte = fields.Datetime(string="Last Update Date")
    @api.multi
    def btn_open_opp(self):
        model_data = self.env['ir.model.data']
        form_view = model_data.get_object_reference('crm', 'crm_case_form_view_oppor')
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'crm.lead',
                'res_id':self.opp_id and self.opp_id.id or False,
                'views': [(form_view and form_view[1] or False, 'form')],
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

