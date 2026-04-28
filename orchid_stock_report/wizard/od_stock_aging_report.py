# -*- coding: utf-8 -*-
##############################################################################

import time
from openerp.tools.translate import _
from openerp.osv import orm, fields
import logging
_logger = logging.getLogger(__name__)

class od_stock_aging_report_wizard(orm.TransientModel):
    _name = "od.stock.aging.report.wizard"
    _description = "Stock Aging Report Wizard"

    _columns = {
        'product_id': fields.many2one('product.product',string='Product'),
        'location_id': fields.many2one('stock.location',string='Location'),
        'categ_id': fields.many2one('product.category',string='Product Category'),
        'detail' : fields.boolean('Detail'),
        'age': fields.float('Age(Days)'),
        'stock_list':fields.boolean('Stock List Only')
    }

    def pre_print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        return data

    def build_filter(self,cr,uid,ids,context=None):
        data = self.read(cr, uid, ids,['product_id','location_id','categ_id','age','detail'])[0]
        return data

    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = self.build_filter(cr,uid,ids,context=context)

        if context.get('xls_export'):
            return {'type': 'ir.actions.report.xml',
                    'report_name': 'stock_aging_xls',
                    'datas': data}

        for val in self.browse(cr,uid,ids):
            if val.detail:
                return self.pool['report'].get_action(cr, uid, [], 'orchid_stock_report.report_stock_aging_detail', data=data, context=context)
            if val.stock_list:
                return self.pool['report'].get_action(cr, uid, [], 'orchid_stock_report.report_stock_list', data=data, context=context)
        return self.pool['report'].get_action(cr, uid, [], 'orchid_stock_report.report_stock_aging', data=data, context=context)

    def xls_export(self, cr, uid, ids, context=None):
        return self.print_report(cr, uid, ids, context=context)

od_stock_aging_report_wizard()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
