# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import fields, osv
from openerp.exceptions import Warning
from datetime import date
from dateutil.relativedelta import relativedelta

class od_stock_move_wiz(osv.osv_memory):
    _name='od.stock.move.wiz'
    _columns = {
                'product_id':fields.many2one('product.product','Product'),
                'location_id': fields.many2one('stock.location', 'Warehouse',domain=[('usage','=','view'),('location_id','=',1)]),
                'date_from' : fields.date('From Date', required="1"),
                'date_to' : fields.date('To Date', required="1"),
                'refresh':fields.boolean('Refresh Data'),
                'move_type':fields.selection([('purchase','Purchase'),('purchase_return','Purchase Return'),('sale','Sale'),('sale_return','Sale Return'),('internal','Internal Transfer'),
                ('inventory_loss','Inventory Loss'),('inventory_add','Inventory Add'),('others','Others')],string="Type")
                }
    _defaults = {
#        'date_from': date.today() - relativedelta(months=+12),
        'date_from': fields.date.context_today,
        'date_to': fields.date.context_today,
    }

#lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'procurement.order', context=c)

    def get_cost_method(self,cr,uid,ids,context=None):
        parameter_obj = self.pool.get('ir.config_parameter')
        parameter_ids = parameter_obj.search(cr,1,[('key', '=', 'cost_method')])
        if not parameter_ids:
            raise Warning("Cost Method Not Defined on Key cost_method")
        cost_method  = parameter_obj.browse(cr,uid,parameter_ids).value
        return cost_method
    def open_quant(self,cr,uid,ids,context=None):
        stock_history = self.pool.get('od.stock.history')
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, context=context)[0]
        product_id = data['product_id'] and data['product_id'][0]
        location_id = data['location_id'] and data['location_id'][0]
        date_from = data['date_from'] or False
        date_to = data['date_to'] or False
        refresh = data['refresh']
        move_type = data['move_type']
        cost_method = self.get_cost_method(cr,uid,ids,context=context)
        stock_history.od_refresh_data(cr,cost_method)


        domain = []
        if move_type:
            domain.append(('move_type','=',move_type))
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
            'res_model': 'od.stock.history',
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
