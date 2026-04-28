# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import fields, osv
class od_payroll_transaction_analysis_view(osv.osv):
    _name = "od.payroll.transaction.analysis.view"
    _description = "od.payroll.transaction.analysis.view"
    _auto = False
    _rec_name = 'employee_id'
    _columns = {
        'employee_id':fields.many2one('hr.employee','Employee'),
        'date':fields.date('Date'),
        'period_id':fields.many2one('account.period','Period'),
        'description':fields.char('Description'),
        'product_id':fields.many2one('product.template','Payroll Item'),
        'transaction_note_id': fields.many2one('od.transaction.note','Transaction Note'),
        'allowance':fields.float('Allowance'),
        'deduction':fields.float('Deduction'),
        'state':fields.char('state')
        
        
    }


    def _select(self):
        select_str = """
              SELECT ROW_NUMBER () OVER (ORDER BY od_payroll_transactions_line.id ) AS id,
             od_payroll_transactions_line.employee_id as employee_id,
od_payroll_transactions.period_id as period_id,
od_payroll_transactions.date as date,
od_payroll_transactions.name as description,
od_payroll_transactions_line.product_id as product_id,
od_payroll_transactions_line.transaction_note_id as transaction_note_id,
od_payroll_transactions_line.allowance as allowance,
od_payroll_transactions_line.deduction as deduction,
od_payroll_transactions_line.state as state 
             
        """
        return select_str
    def _from(self):
        from_str = """
                od_payroll_transactions_line  
        """
        return from_str

    def _group_by(self):
        group_by_str = """
            GROUP BY od_payroll_transactions_line.id,
                    od_payroll_transactions_line.employee_id,
                   od_payroll_transactions.period_id,
                    od_payroll_transactions.name,
                    od_payroll_transactions_line.allowance,
                    od_payroll_transactions_line.product_id,
                    od_payroll_transactions_line.transaction_note_id,
                    od_payroll_transactions_line.state,
                    od_payroll_transactions_line.deduction,
                    od_payroll_transactions.date
                   
                    
        """
        return group_by_str


    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM  %s 
left outer join od_payroll_transactions 
on od_payroll_transactions.id = payroll_transactions_id
  %s
            )""" % (self._table, self._select(), self._from(), self._group_by()))








