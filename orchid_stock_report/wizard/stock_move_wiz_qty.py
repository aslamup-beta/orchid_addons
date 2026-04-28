# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import fields, osv
from openerp.exceptions import Warning
class od_stock_move_wiz_qty(osv.osv_memory):
    _name='od.stock.move.wiz.qty'
    _columns = {
                'product_id':fields.many2one('product.product','Product'),
                'location_id': fields.many2one('stock.location', 'Warehouse',domain=[('usage','=','view'),('location_id','=',1)]),
                'date_from' : fields.date('From Date'),
                'date_to' : fields.date('To Date'),
                'refresh':fields.boolean('Refresh Data')
                }
    _defaults = {
        'date_from': fields.date.context_today,
        'date_to': fields.date.context_today,
    }



    def open_quant(self,cr,uid,ids,context=None):
        stock_history = self.pool.get('od.stock.history.qty')
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, context=context)[0]
        product_id = data['product_id'] and data['product_id'][0]
        location_id = data['location_id'] and data['location_id'][0]
        date_from = data['date_from'] or False
        date_to = data['date_to'] or False
        refresh = data['refresh']


        stock_history.od_refresh_data(cr)
        domain = []
        if product_id:
            domain.append(('product_id', '=', product_id))
        if location_id:
            domain.append(('warehouse_id','=',location_id))
        if date_from:
            domain.append(('date','>=',date_from))
        if date_to:
            domain.append(('date','<=',date_to))
        ctx ={'search_default_warehouse':1}
        ctx.update(context)
        res = {
            'view_type': 'form',
            'view_mode': 'tree,graph',
            'res_model': 'od.stock.history.qty',
            'type': 'ir.actions.act_window',
            'context':ctx
        }

        if not domain:
            return res


        res['domain'] = domain
        return res



    def pre_print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        return data

    def build_filter(self,cr,uid,ids,context=None):
        data = self.read(cr, uid, ids,['product_id','location_id','date_from','date_to'])[0]
        return data

    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = self.build_filter(cr,uid,ids,context=context)

        return self.pool['report'].get_action(cr, uid, [], 'orchid_stock_report.report_stock_move_analysis', data=data, context=context)
