# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import fields, osv
class sale_report(osv.osv):
    _inherit = "sale.report"
    _columns = {
        'od_order_type_id': fields.many2one('od.order.type','Sale Type',readonly=True),
    }
    def _select(self):
        result = super(sale_report, self)._select()
        select_str = result + """, s.od_order_type_id
                              """
        return select_str

    def _group_by(self):
        result = super(sale_report,self)._group_by()
        group_by_str = result + """,s.od_order_type_id

                                """
        return group_by_str
            
