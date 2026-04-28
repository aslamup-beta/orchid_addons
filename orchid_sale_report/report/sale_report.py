# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import fields, osv
class sale_report(osv.osv):
    _inherit = "sale.report"

    _columns = {
        'order_id': fields.many2one('sale.order','Sale Order'),
        'requested_date':fields.datetime('Requested Date')
    }

    def _select(self):
        result = super(sale_report, self)._select()
        select_str = result + """,l.order_id as order_id,s.requested_date as requested_date
                              """
        return select_str


    def _group_by(self):

        result = super(sale_report, self)._group_by()

        group_by_str = result + """,s.requested_date"""

        return group_by_str

