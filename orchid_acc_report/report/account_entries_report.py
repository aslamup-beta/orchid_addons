# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import fields, osv
class account_entries_report(osv.osv):
    _inherit = "account.entries.report"
    _columns = {
        'move_id':fields.many2one('account.move', 'Move'),
    }
    
#                l.od_cost_centre_id as od_cost_centre_id,
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'account_entries_report')
        cr.execute("""
            create or replace view account_entries_report as (
                 select l.id as id,
                am.date as date,

                am.id as move_id,

                l.date_maturity as date_maturity,
                l.date_created as date_created,
                am.ref as ref,
                am.state as move_state,
                l.state as move_line_state,
                l.reconcile_id as reconcile_id,
                to_char(am.date, 'YYYY') as year,
                to_char(am.date, 'MM') as month,
                to_char(am.date, 'YYYY-MM-DD') as day,
                l.partner_id as partner_id,
                l.product_id as product_id,
                l.product_uom_id as product_uom_id,
                am.company_id as company_id,
                am.journal_id as journal_id,
                p.fiscalyear_id as fiscalyear_id,
                am.period_id as period_id,
                l.account_id as account_id,
                l.analytic_account_id as analytic_account_id,
                a.type as type,
                a.user_type as user_type,
                1 as nbr,


                (CASE WHEN (l.credit > 0) 
    		     THEN (l.quantity*-1)
                 ELSE (l.quantity)
    	        END)
        		AS quantity,

                l.currency_id as currency_id,
                l.amount_currency as amount_currency,
                l.debit as debit,
                l.credit as credit,
                coalesce(l.debit, 0.0) - coalesce(l.credit, 0.0) as balance

            from
                account_move_line l
                left join account_account a on (l.account_id = a.id)
                left join account_move am on (am.id=l.move_id)
                left join account_period p on (am.period_id=p.id)
                where l.state != 'draft')
               """)




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
