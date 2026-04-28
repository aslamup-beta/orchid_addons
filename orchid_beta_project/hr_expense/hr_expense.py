# -*- coding: utf-8 -*-
from openerp import models,fields,api,_
from datetime import date, timedelta,datetime
from openerp.exceptions import Warning


class hr_expense_expense(models.Model):
    _inherit ="hr.expense.expense"

    od_payment_status = fields.Selection([('paid','Paid Fully'),('paid_partial','Paid Partially')],string="Interim Payment Status",copy=False)
    od_payment_datetime = fields.Datetime(string="Interim Payment Date",copy=False)
    od_paid_amount = fields.Float(string="Interim Paid Amount",copy=False)
    od_expense_type = fields.Selection([('general','General'),('opportunity','Opportunity'),('project','Project')],string="Expense Type")
    od_prj_mngr = fields.Many2one('res.users', string='Project Manager')
    date_log_history_line = fields.One2many('od.date.log.expense','expense_id',strint="Date Log History",readonly=True,copy=False)

    #this is done only for ksa
    def create_accounting_entry(self):
        period_obj = self.env['account.period']
        move_obj = self.env['account.move']
        date = fields.Date.today()
        period_ids = period_obj.find(date).id
        ref = self.name
        partner_id =self.employee_id.address_home_id and self.employee_id.address_home_id.id or False
        branch_id = self.employee_id.od_branch_id and self.employee_id.od_branch_id.id or False
        cost_centre_id = self.employee_id.od_cost_centre_id and self.employee_id.od_cost_centre_id.id or False
        amount = self.amount
        
        #Expenses Accounts IDS in ERP KSA
        journal_id = 41
        credit_account = 5265
        if self.od_expense_type == 'general':
            debit_account = 5445
        if self.od_expense_type == 'opportunity':
            debit_account = 6567
        if self.od_expense_type == 'project':
            debit_account = 5732
        
        move_lines =[]
        vals1={
                'name': ref.split('\n')[0][:64],
                'period_id': period_ids ,
                'journal_id': journal_id,
                'date': date,
                'account_id': credit_account,
                'quantity': 1,
                'debit': 0.0,
                'credit': abs(amount),
                'partner_id':partner_id,
                'od_branch_id': branch_id,
                'od_cost_centre_id': cost_centre_id
            }
        move_lines.append([0,0,vals1])
        for line in self.line_ids:
            vals2={
                    'name': line.name.split('\n')[0][:64],
                    'period_id': period_ids ,
                    'journal_id': journal_id,
                    'date': date,
                    'account_id': debit_account,
                    'credit': 0.0,
                    'quantity': 1,
                    'od_opp_id':line.od_opp_id and line.od_opp_id.id or False,
                    'debit': abs(line.total_amount,),
                    'analytic_account_id': line.analytic_account and line.analytic_account.id or False,
                    'partner_id': False,
                    'od_branch_id': branch_id
                }
            move_lines.append([0,0,vals2])
        move_vals = {

                'date': date,
                'ref': ref,
                'period_id': period_ids ,
                'journal_id': journal_id,
                'line_id':move_lines
                }
        move_id = move_obj.create(move_vals).id
        self.account_move_id = move_id
        return True
    
    def expense_accept(self):
        if self.company_id.id ==6:
            if self.env.user.id not in (154,2283,2535,2626):
                raise Warning("Second Approval should be done through Finance Dept. as this action creates an Accounting Entry.")
            self.create_accounting_entry()
        self.date_log_history_line = [{'name':'Expense Validated (Second Approval)','user_id': self.env.user.id, 'date':str(datetime.now())}]
        return super(hr_expense_expense, self).expense_accept()
    
    def expense_canceled(self):
        self.date_log_history_line = [{'name':'Expense Refused','user_id': self.env.user.id, 'date':str(datetime.now())}]
        return super(hr_expense_expense, self).expense_canceled()
    
    def expense_validated(self):
            approval_manager = [135,2137]
            project_manager = self.od_prj_mngr.id
            approval_manager.append(project_manager)
            if self.env.user.id == self.sudo().employee_id.user_id.id:
                raise Warning("You cannot Approve your own expenses. Kindly contact your Manager")
            if self.od_expense_type == 'project' and self.company_id.id ==6:
                if self.env.user.id not in approval_manager:
                    raise Warning("Project Expenses Should be Approved by PMO department, Kindly discard")
            
            self.date_log_history_line = [{'name':'Expense Approved (First Approval)','user_id': self.env.user.id, 'date':str(datetime.now())}]

    
class od_date_log_expense(models.Model):
    _name = 'od.date.log.expense'
    expense_id =fields.Many2one('hr.expense.expense', string="Expense ID")
    name = fields.Char(string='Name')
    user_id = fields.Many2one('res.users', string="User")
    date = fields.Datetime(string="Date")
    
    
    