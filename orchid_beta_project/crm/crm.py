# -*- coding: utf-8 -*-
from openerp import models,fields,api,_
class crm_lead(models.Model):
    _inherit ="crm.lead"


    @api.multi
    def od_btn_open_timsheet_for_opp(self):

        task_pool = self.env['project.task']
        work_pool = self.env['project.task.work']
        lead_id = self.id
        task_search_dom = [('od_opp_id','=',lead_id)]
        task_ids = [task.id for task in task_pool.search(task_search_dom)]
        work_search_dom = [('task_id','in',task_ids)]
        all_timesheet_ids = [work.hr_analytic_timesheet_id for work in work_pool.search(work_search_dom)]
        timesheet_ids = []
        for timesheet in all_timesheet_ids:
            if timesheet:
                timesheet_ids.append(timesheet.id)
        domain = [('id','in',timesheet_ids)]
        return {
            'domain':domain,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'hr.analytic.timesheet',
            'type': 'ir.actions.act_window',
        }

    @api.one
    def od_get_timesheet_amount(self):
        task_pool = self.env['project.task']
        work_pool = self.env['project.task.work']
        lead_id = self.id
        task_search_dom = [('od_opp_id','=',lead_id)]
        task_ids = [task.id for task in task_pool.search(task_search_dom)]
        work_search_dom = [('task_id','in',task_ids)]
        all_timesheet_ids = [work.hr_analytic_timesheet_id for work in work_pool.search(work_search_dom)]
        timesheet_amounts = []
        for timesheet in all_timesheet_ids:
            if timesheet:
                timesheet_amounts.append(timesheet.normal_amount)
        amount = sum(timesheet_amounts)
        self.od_timesheet_amount = amount
    @api.multi
    def od_btn_open_account_move_lines(self):
        account_move_line = self.env['account.move.line']
        lead_id = self.id
        domain = [('od_opp_id','=',lead_id),('od_state','=','posted')]
        return {
            'domain':domain,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'type': 'ir.actions.act_window',
        }
    @api.multi
    def od_btn_open_account_move_lines_draft(self):
        account_move_line = self.env['account.move.line']
        lead_id = self.id
        domain = [('od_opp_id','=',lead_id),('od_state','!=','posted')]
        return {
            'domain':domain,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'type': 'ir.actions.act_window',
        }
    @api.one
    def od_get_lead_journal_amount_draft(self):
        account_move_line = self.env['account.move.line']
        lead_id = self.id
        domain = [('od_opp_id','=',lead_id),('od_state','!=','posted')]
        journal_lines = account_move_line.search(domain)
        amount = sum([mvl.debit for mvl in journal_lines])
        self.od_journal_amount_draft = amount

    @api.one
    def od_get_lead_journal_amount(self):
        account_move_line = self.env['account.move.line']
        lead_id = self.id
        company_id = self.company_id and self.company_id.id or False
        account_id = self.get_product_id_from_param('pre_op_account_id')
        if company_id ==6:
            account_id = self.get_product_id_from_param('pre_op_account_id_ksa')
        domain = [('account_id', '=', account_id),('od_opp_id','=',lead_id),('move_id.state', '<>', 'draft')]
        journal_lines = account_move_line.search(domain)
        amount = sum([mvl.debit for mvl in journal_lines])
        self.od_journal_amount = amount


    @api.multi
    def od_open_hr_expense_claim(self):
        hr_exp_line = self.env['hr.expense.line']
        lead_id = self.id
        domain = [('od_opp_id','=',lead_id),('od_state','not in',('draft','cancelled','confirm','second_approval'))]
        return {
            'domain':domain,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'hr.expense.line',
            'type': 'ir.actions.act_window',
        }
    @api.multi
    def od_open_hr_expense_claim_draft(self):
        hr_exp_line = self.env['hr.expense.line']
        lead_id = self.id
        domain = [('od_opp_id','=',lead_id),('od_state','in',('draft','cancelled','confirm','second_approval'))]
        return {
            'domain':domain,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'hr.expense.line',
            'type': 'ir.actions.act_window',
        }
    @api.one
    def od_get_hr_exp_claim_amount_draft(self):
        hr_exp_line = self.env['hr.expense.line']
        lead_id = self.id
        domain = [('od_opp_id','=',lead_id),('od_state','in',('draft','cancelled','confirm','second_approval'))]
        hr_exp_obj =hr_exp_line.search(domain)
        amount  = sum([hr.total_amount for hr in hr_exp_obj])
        self.od_hr_claim_amount_draft = amount
    @api.one
    def od_get_hr_exp_claim_amount(self):
        hr_exp_line = self.env['hr.expense.line']
        lead_id = self.id
        domain = [('od_opp_id','=',lead_id),('od_state','not in',('draft','cancelled','confirm','second_approval'))]
        hr_exp_obj =hr_exp_line.search(domain)
        amount  = sum([hr.total_amount for hr in hr_exp_obj])
        self.od_hr_claim_amount = amount
        
   
        
    od_timesheet_amount = fields.Float(string="Timesheet Amount",compute="od_get_timesheet_amount")
    od_hr_claim_amount = fields.Float(string="Hr Exp Claim Amount",compute="od_get_hr_exp_claim_amount")
    od_hr_claim_amount_draft = fields.Float(string="Hr Exp Claim Amount",compute="od_get_hr_exp_claim_amount_draft")
    od_journal_amount = fields.Float(string="Journal Amount",compute="od_get_lead_journal_amount")
    od_journal_amount_draft = fields.Float(string="Journal Amount",compute="od_get_lead_journal_amount_draft")
    kpi_considered = fields.Boolean(string="KPI Considered Net")
    kpi_considered_sec = fields.Boolean(string="KPI Considered Sec")
    
    