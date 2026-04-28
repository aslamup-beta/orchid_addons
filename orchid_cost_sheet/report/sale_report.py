# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import fields, osv
class sale_report(osv.osv):
    _inherit = "sale.report"

    _columns = {
        # 'order_id': fields.many2one('sale.order','Sale Order'),
        'od_cost' : fields.float('Total Cost'),
        'od_profit': fields.float('Profit'),
    }

    def _select(self):
        result = super(sale_report, self)._select()
        select_str = result + """,sum(l.product_uom_qty *cr.rate * l.purchase_price) as od_cost,
        (sum(l.product_uom_qty * cr.rate * l.price_unit * (100.0-l.discount) / 100.0) - sum(l.product_uom_qty * cr.rate * l.purchase_price) )as od_profit
                              """
        return select_str
