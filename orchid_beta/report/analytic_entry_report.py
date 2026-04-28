# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import fields,osv

class analytic_entries_report(osv.osv):
    _inherit = "analytic.entries.report"
    _columns = {
    'state': fields.selection([('template', 'Template'),
                               ('draft','New'),
                               ('open','In Progress'),
                               ('pending','To Renew'),
                               ('close','Closed'),
                               ('cancelled', 'Cancelled')],
                              'Status'),
    'user_type':fields.many2one('account.account.type',string="Account Type")
    }
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'analytic_entries_report')
        cr.execute("""
            create or replace view analytic_entries_report as (
                 select
                     min(a.id) as id,
                     count(distinct a.id) as nbr,
                     a.date as date,
                     a.user_id as user_id,
                     analytic.state as state,
                     a.name as name,
                     analytic.partner_id as partner_id,
                     a.company_id as company_id,
                     a.currency_id as currency_id,
                     a.account_id as account_id,
                     a.general_account_id as general_account_id,
                     a.journal_id as journal_id,
                     a.move_id as move_id,
                     a.product_id as product_id,
                     a.product_uom_id as product_uom_id,
                     acc.user_type as user_type,
                     sum(a.amount) as amount,
                     sum(a.unit_amount) as unit_amount
                 from
                     account_analytic_line a
                     left join account_analytic_account analytic on (analytic.id = a.account_id)
                     left join account_account acc on (acc.id = a.general_account_id)
                 group by
                     a.date, a.user_id,a.name,analytic.partner_id,a.company_id,a.currency_id,
                     a.account_id,a.general_account_id,a.journal_id,
                     analytic.state,acc.user_type,
                     a.move_id,a.product_id,a.product_uom_id
            )
        """)
