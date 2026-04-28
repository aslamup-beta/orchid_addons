# -*- coding: utf-8 -*-
##############################################################################

from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
class account_entries_report(osv.osv):
    _inherit = "account.entries.report"
#    _description = "Journal Items Analysis"
#    _auto = False
#    _rec_name = 'date'
    _columns = {
        'od_cost_centre_id': fields.many2one('od.cost.centre','Cost Centre'),
        'od_product_brand_id': fields.many2one('od.product.brand','Brand'),
        'od_asset_id':fields.many2one('account.asset.asset','Asset'),
        'od_branch_id': fields.many2one('od.cost.branch','Branch'),
        'od_division_id': fields.many2one('od.cost.division','Division'),


    }

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
                l.debit-l.credit as balance,
                l.od_cost_centre_id as od_cost_centre_id,
                l.od_branch_id as od_branch_id,
                l.od_division_id as od_division_id,
                l.od_product_brand_id as od_product_brand_id,
                l.asset_id as od_asset_id
            from
                account_move_line l
                left join account_account a on (l.account_id = a.id)
                left join account_move am on (am.id=l.move_id)
                left join account_period p on (am.period_id=p.id)
                left join od_cost_centre cc on (l.od_cost_centre_id=cc.id)
                where l.state != 'draft' and a.active=True)
               """)
