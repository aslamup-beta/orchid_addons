# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import fields, osv
class od_account_move_line_debit(osv.osv):
    _name = "od.account.move.line.debit"
    _description = "od.account.move.line.debit"
    _auto = False
    _rec_name = 'code'
    _columns = {
        'account_id':fields.many2one('account.account', 'Account'),
        'partner_id':fields.many2one('res.partner','Partner'),
        'account_analytic_id':fields.many2one('account.analytic.account','Analytic Account'),
        'product_id':fields.many2one('product.product','Product'),
        'company_id': fields.many2one('res.company', 'Company'),
        'currency_id':fields.many2one('res.currency', 'Currency'),
        'amount_currency':fields.float('Amount Currency'),
        'account_type':fields.char('Account Type'),
        'debit':fields.float('Debit'),
        'code':fields.char('Code'),
        'move_id':fields.many2one('account.move','Journal Entry'),
        'journal_id':fields.many2one('account.journal', string='Journal'),
        'journal_type':fields.char('Journal Type')
    }
    def _select(self):
        select_str = """
              SELECT ROW_NUMBER () OVER (ORDER BY mvlne.id ) AS id,
             mvlne.move_id AS move_id,
             mvlne.account_id AS account_id,
             mvlne.partner_id AS partner_id,
             mvlne.journal_id as journal_id,
             mvlne.analytic_account_id AS account_analytic_id,
             mvlne.product_id AS product_id,
             mvlne.company_id as company_id,
             mvlne.currency_id as currency_id,
             mvlne.amount_currency as amount_currency,
             acc.type as account_type,
             typ.code as code,
             jnl.type as journal_type,
             mvlne.debit
             
        """
        return select_str
    def _from(self):
        from_str = """
                account_move_line mvlne 
        """
        return from_str

    def _group_by(self):
        group_by_str = """
            GROUP BY mvlne.move_id,
            mvlne.id,
            mvlne.account_id,
            mvlne.partner_id,
            mvlne.analytic_account_id,
            mvlne.product_id,
            mvlne.company_id,
            mvlne.currency_id,
            mvlne.amount_currency,
            acc.type,
            typ.code,
            jnl.type,
            mvlne.journal_id,
            mvlne.debit
        """
        return group_by_str


    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM  %s 
    INNER JOIN account_account acc ON ((acc."id" = mvlne.account_id))
    INNER JOIN account_account_type typ ON ((typ."id" = acc.user_type))
    INNER JOIN account_journal AS jnl ON jnl.id=mvlne.journal_id
  %s
            )""" % (self._table, self._select(), self._from(), self._group_by()))




