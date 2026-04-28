# -*- coding: utf-8 -*-
import time
from openerp import models, fields, api

from pprint import pprint
from datetime import datetime
import openerp.addons.decimal_precision as dp

class pre_operation_rpt(models.TransientModel):
    _name = 'pre.oprn.rpt.wiz'
    
    def _get_fiscalyear(self):
        now = time.strftime('%Y-%m-%d')
        company_id = self.env.user.company_id.id
        domain = [('company_id', '=', company_id), ('date_start', '<', now), ('date_stop', '>', now)]
        fiscalyears = self.env['account.fiscalyear'].search(domain, limit=1)
        return fiscalyears and fiscalyears[0] or False
    
    def _get_pre_oprn_acc_id(self):
        company_id = self.env.user.company_id.id
        if company_id==6:
            return 6567
        if company_id==1:
            return 2135
    
    account_id = fields.Many2one('account.account',string="Account", default=_get_pre_oprn_acc_id, readonly="1")
    fiscal_year = fields.Many2one('account.fiscalyear',string="Fiscal Year", default=_get_fiscalyear)
    branch_ids= fields.Many2many('od.cost.branch',string="Branch")
    cost_centre_ids = fields.Many2many('od.cost.centre',string="Cost Center")
    division_ids = fields.Many2many('od.cost.division',string="Technology Unit")
    journal_ids = fields.Many2many('account.journal',string="Journals")
    opp_stage_ids = fields.Many2many('crm.case.stage',string="Opportunity Stage",domain=[('id','!=',6)])
    sam_ids = fields.Many2many('res.users',string="Sale Account Managers")
    opp_ids = fields.Many2many('crm.lead',string="Opportunity")
    select_won_opp = fields.Boolean("Won Opportunities")
    select_won_opp = fields.Boolean("Won Opportunities")
    detail = fields.Boolean("Detailed Report")
    wiz_line = fields.One2many('pre.oprn.rpt.data.line','org_wiz_id',string="Wiz Line")
    
    def od_get_company_id(self):
        return self.env.user.company_id
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    
    def od_get_period_ids(self):
        fiscal_year = self.fiscal_year.id
        company_id = self.env.user.company_id.id
        period_ids = self.env['account.period'].search([('company_id', '=', company_id), ('fiscalyear_id', '=', fiscal_year)])
        return period_ids
    
    def _mv_lines_get(self, account_id):
        moveline_obj = self.env['account.move.line']
        period_ids = [x.id for x in self.od_get_period_ids()]
        
        branch_ids = [pr.id for pr in self.branch_ids]
        cost_centre_ids = [pr.id for pr in self.cost_centre_ids]
        division_ids = [pr.id for pr in self.division_ids]
        journal_ids = [pr.id for pr in self.journal_ids]
        opp_stage_ids = [pr.id for pr in self.opp_stage_ids]
        sam_ids = [pr.id for pr in self.sam_ids]
        opp_ids = [pr.id for pr in self.opp_ids]
        
        if self.select_won_opp:
            fiscal_year = self.fiscal_year
            domain1 = [('status','=','active'),('state','in',('approved','done','modify','change','analytic_change','change_processed','redistribution_processed'))]
            domain1 += [('approved_date','>=',fiscal_year.date_start),('approved_date','<=',fiscal_year.date_stop)]
            cost_sheet_data = self.env['od.cost.sheet'].search(domain1)
            for costsheet in cost_sheet_data:
                opp_ids.append(costsheet.lead_id.id)
            
        
        domain = [('account_id', 'in', account_id),
                    ('account_id.type', '=', 'other',),
                    ('move_id.state', '<>', 'draft'),
                    ('move_id.date', '>=', '01-Jan-19'),
                    ('move_id.journal_id', 'not in', (6,29))
                    ]
        
        if branch_ids:
            domain += [('od_branch_id','in',branch_ids)]
        if cost_centre_ids:
            domain += [('od_cost_centre_id','in',cost_centre_ids)]
        if division_ids:
            domain += [('od_division_id','in',division_ids)]
        if journal_ids:
            domain += [('move_id.journal_id','in',journal_ids)]
        if opp_stage_ids:
            domain += [('od_opp_id.stage_id','in',opp_stage_ids)]
        if sam_ids:
            domain += [('od_opp_id.user_id', 'in', sam_ids)]
        if opp_ids:
            domain += [('od_opp_id', 'in', opp_ids)]
        
        
        
        
            
            
        movelines = moveline_obj.search(domain)
        return movelines

    def get_detailed_data(self):
        #account_id = self.account_id.id
        
        company_id = self.env.user.company_id.id
        if company_id==6:
            account_id =  [6567]
        if company_id==1:
            account_id =  [2135,6632]
        
        result  = []
        moves = self._mv_lines_get(account_id)
        for mvl in moves:
            age = (datetime.strptime(datetime.strftime(datetime.now(), '%Y-%m-%d'),'%Y-%m-%d') - datetime.strptime(mvl.move_id.date, '%Y-%m-%d')).days
            result.append((0,0,{
                'date':mvl.date,
                'beta_ref':mvl.ref,
                'part_ref':mvl.name or "/",
                'due':mvl.debit,
                'age':age,
                'paid':mvl.credit,
                'bal': mvl.debit - mvl.credit,
                'move_id': mvl.move_id.id,
                'opp_id': mvl.od_opp_id and mvl.od_opp_id.id or False,
                'partner_id':mvl.partner_id and mvl.partner_id.id or False,
                'cust_id': mvl.od_opp_id and mvl.od_opp_id.partner_id.id or False,
                'jrnl_id':mvl.move_id.journal_id.id,
                'opp_stage_id': mvl.od_opp_id and mvl.od_opp_id.stage_id.id or False,
                'od_branch_id': mvl.od_opp_id and mvl.od_opp_id.od_branch_id and mvl.od_opp_id.od_branch_id.id or False,
                'sam_id': mvl.od_opp_id and mvl.od_opp_id.user_id.id or False,
                
                }))
        return result
    
    def sum_grouped_moves(self,result):
        for vals in result:
            debit =sum(vals['due'])
            credit =sum(vals['paid'])
            bal = sum(vals['bal'])
            vals.pop('line_rec')
            vals.update({'due': debit, 'paid': credit, 'bal': bal})
        return result
    
    def de_duplicate_moves(self, moves):
        res = []
        for line in moves:
            res.append({'line_rec': line, 'opp_id': line.od_opp_id and line.od_opp_id.id or False})
        result = []
        for item in res :
            check = False
            for r_item in result :
                if item['opp_id'] == r_item['opp_id'] :
                    check = True
                    debit = r_item['due']
                    debit.append(item['line_rec'].debit)
                    credit = r_item['paid']
                    credit.append(item['line_rec'].credit)
                    bal = r_item['bal']
                    bal.append(item['line_rec'].debit - item['line_rec'].credit)

            if check == False:
                mvl = item['line_rec']
                if mvl.od_opp_id.od_approved_date:
                    age = (datetime.strptime(datetime.strftime(datetime.now(), '%Y-%m-%d'),'%Y-%m-%d') - datetime.strptime(mvl.od_opp_id.od_approved_date, '%Y-%m-%d')).days
                else:
                    age = (datetime.strptime(datetime.strftime(datetime.now(), '%Y-%m-%d'),'%Y-%m-%d') - datetime.strptime(mvl.move_id.date, '%Y-%m-%d')).days
                item['date'] = mvl.od_opp_id.od_approved_date if mvl.od_opp_id.od_approved_date else mvl.move_id.date
                item['opp_id'] = mvl.od_opp_id and mvl.od_opp_id.id or False
                item['opp_name'] = mvl.od_opp_id and mvl.od_opp_id.name or False
                item['opp_stage_id'] = mvl.od_opp_id and mvl.od_opp_id.stage_id.id or False
                item['od_branch_id'] = mvl.od_opp_id and mvl.od_opp_id.od_branch_id and mvl.od_opp_id.od_branch_id.id or False
                item['cust_id'] = mvl.od_opp_id and mvl.od_opp_id.partner_id.id or False
                item['age'] = age
                item['sam_id'] = mvl.od_opp_id and mvl.od_opp_id.user_id.id or False
                item['due'] = [item['line_rec'].debit]
                item['paid'] = [item['line_rec'].credit]
                item['bal'] = [item['line_rec'].debit - item['line_rec'].credit]
                
                result.append(item)
        
        result = self.sum_grouped_moves(result)
        return result
        

    def get_data(self):
        #account_id = self.account_id.id
        company_id = self.env.user.company_id.id
        if company_id==6:
            account_id =  [6567]
        if company_id==1:
            account_id =  [2135,6632]
        result  = []
        moves = self._mv_lines_get(account_id)
        moves1 = self.de_duplicate_moves(moves)
        for mvl in moves1:
            if not 0.0 <= abs(mvl.get('bal',0.0)) < 0.01 :
                result.append((0,0,mvl))
        return result

    
    @api.multi
    def print_directly(self):
        if self.detail:
            data = self.get_detailed_data()
            rpt_temp = 'report.od_pre_oprn_rpt'
        else:
            data = self.get_data()
            rpt_temp = 'report.od_pre_oprn_anal_rpt1'
        account_id = self.account_id.id
        rpt_pool = self.env['pre.oprn.rpt.data']
        currency_id = self.env.user.company_id.currency_id.id
        vals = {
            'name': "Pre Operation Analysis Report",
            'account_id':account_id,
            'line_ids':data,
            'currency_id':currency_id,
            }
        
        rpt =rpt_pool.create(vals)
        rpt_id =rpt.id
        ctx = self.env.context
        cr = self.env.cr
        uid = self.env.uid
        return self.pool['report'].get_action(cr, uid, [rpt_id], rpt_temp , context=ctx)
    
    @api.multi
    def export_rpt(self):
        model_data = self.env['ir.model.data']
        if self.detail:
            result = self.get_detailed_data()
            vw = 'tree_view_pre_oprn_analysis_rpt2'
        else:
            result = self.get_data()
            vw = 'tree_view_pre_oprn_analysis_rpt1'
#         result = self.get_data()
            
        tree_view = model_data.get_object_reference( 'beta_customisation', vw)
        self.wiz_line.unlink()
        self.write({'wiz_line':result})
        del(result)
        return {
            'domain': [('org_wiz_id','=',self.id)],
            'name': 'Pre-Oprn Analysis Report',
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(tree_view and tree_view[1] or False, 'tree')],
            'res_model': 'pre.oprn.rpt.data.line',
            'type': 'ir.actions.act_window',
        }


      
class pre_oprn_rpt_data(models.TransientModel):
    _name = 'pre.oprn.rpt.data'
    
    def od_get_currency(self):
        return self.env.uid.company_id.currency_id
    
    def _get_today_date(self):
        return datetime.today().strftime('%d-%b-%y')
    
    name = fields.Char()
    account_id = fields.Many2one('account.account',string="Account", )
    line_ids = fields.One2many('pre.oprn.rpt.data.line','wiz_id',string="Wiz Line",readonly=True)
    currency_id = fields.Many2one('res.currency',string='Currency') 
    date = fields.Date(default=_get_today_date)
    
    total = fields.Float(string="Total")
    
class pre_oprn_rpt_data_line(models.TransientModel):
    _name = 'pre.oprn.rpt.data.line'
    _order = 'date'
    
    def od_get_company_id(self):
        return self.env.user.company_id
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)

    
    wiz_id = fields.Many2one('pre.oprn.rpt.data',string="Wizard data")
    org_wiz_id = fields.Many2one('pre.oprn.rpt.wiz',string="Wizard")
    s_no = fields.Integer(string="S N")
    date = fields.Date(string='Date')
    opp_name = fields.Char(string="Opportunity Name")
    beta_ref = fields.Char(string="Beta IT Reference")
    part_ref = fields.Char(string="Partner Reference")
    age = fields.Integer(string="Age(Days)")
    due = fields.Float(string="Debit", digits=(16,2))
    paid = fields.Float(string="Credit", digits=(16,2))
    bal = fields.Float(string="Balance",digits=(16,2))
    move_id = fields.Many2one('account.move', string="Move")
    opp_id = fields.Many2one('crm.lead', string="Opportunity")
    opp_stage_id = fields.Many2one('crm.case.stage', string='Status')
    partner_id = fields.Many2one('res.partner', string="Partner")
    cust_id = fields.Many2one('res.partner', string="Customer")
    jrnl_id = fields.Many2one('account.journal', string="JRNL")
    od_branch_id = fields.Many2one('od.cost.branch', string="Branch")
    sam_id = fields.Many2one('res.users', string="SAM")
    
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
    def btn_open_move(self):
       
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.move',
                'res_id':self.move_id and self.move_id.id or False,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }
    
