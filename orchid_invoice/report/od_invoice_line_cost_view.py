# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import fields, osv
class od_invoice_line_cost_view(osv.osv):
    _name = "od.invoice.line.cost.view"
    _description = "od.invoice.line.cost.view"
    _auto = False
    _rec_name = 'product_id'
    _columns = {
        'product_id':fields.many2one('product.product',string='Product'),
        'cost':fields.float('Cost'),
        'inv_id':fields.many2one('account.invoice',string='Invoice'),



    }



    _order = 'product_id desc'
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'od_invoice_line_cost_view')
        cr.execute("""
            create or replace view od_invoice_line_cost_view as (
                select ROW_NUMBER () OVER (ORDER BY inv. ID) AS ID,
                    inv.id as inv_id,
                    mvl.product_id as product_id,

CASE
WHEN (
(inv. TYPE) :: TEXT = 'out_invoice' :: TEXT
) THEN
SUM (mvl.debit)
WHEN (
(inv. TYPE) :: TEXT = 'out_refund' :: TEXT
) THEN
(
SUM (mvl.credit) * ((- 1)) :: NUMERIC
)
ELSE
(0) :: NUMERIC
END AS COST
                from
(
(
(
account_move_line mvl
JOIN account_account acc ON ((mvl.account_id = acc. ID))
)
JOIN account_account_type typ ON ((acc.user_type = typ. ID))
)
JOIN account_invoice inv ON ((inv.move_id = mvl.move_id))
)
WHERE

(typ.code) :: TEXT = 'expense' :: TEXT
AND inv.type in ('out_invoice','out_refund')
                group by
                    inv. TYPE,
                    inv.id,
                    mvl.product_id)
               """)


od_invoice_line_cost_view()































