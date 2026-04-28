# -*- coding: utf-8 -*-
##############################################################################

from openerp import tools
from openerp.osv import fields,osv
from openerp.tools.translate import _
from dateutil.relativedelta import relativedelta
from datetime import datetime



class od_quant_new_wiz(osv.osv_memory):

    _name = 'od.quant.new.wiz'
    _description = 'Orchid Report Enquiry wizard'
    _columns = {
        'product_id':fields.many2one('product.product', 'Product'),
        'product_categ_id': fields.many2one('product.category', 'Product Category'),
        'location_id':fields.many2one('stock.location', 'Location'),
        'od_pdt_group_id':fields.many2one('od.product.group','Group'),
        'od_pdt_sub_group_id':fields.many2one('od.product.sub.group','Sub Group'),
        'od_pdt_brand_id':fields.many2one('od.product.brand','Brand'),
        'od_pdt_classification_id':fields.many2one('od.product.classification','Classification'),
        'lot_id':fields.many2one('stock.production.lot','Lot'),
        'negative_move':fields.boolean('Negative Move'),
        'usage': fields.selection([
                        ('supplier', 'Supplier Location'),
                        ('view', 'View'),
                        ('internal', 'Internal Location'),
                        ('customer', 'Customer Location'),
                        ('inventory', 'Inventory'),
                        ('procurement', 'Procurement'),
                        ('production', 'Production'),
                        ('transit', 'Transit Location')],
                'Location Type')
    }
    _defaults = {
                 'usage':'internal'
                 }
    def open_quant(self,cr,uid,ids,context=None):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, context=context)[0]
        domain = []
        product_id = data['product_id']
        if product_id:
            domain.append(('product_id','=',product_id[0]))
        product_categ_id = data['product_categ_id']
        if product_categ_id:
            domain.append(('product_categ_id','=',product_categ_id[0]))
        location_id = data['location_id']
        if location_id:
            domain.append(('location_id','=',location_id[0]))
        od_pdt_group_id = data['od_pdt_group_id']
        if od_pdt_group_id:
            domain.append(('od_pdt_group_id','=',od_pdt_group_id[0]))
        od_pdt_sub_group_id = data['od_pdt_sub_group_id']
        if od_pdt_sub_group_id:
            domain.append(('od_pdt_sub_group_id','=',od_pdt_sub_group_id[0]))
        od_pdt_brand_id = data['od_pdt_brand_id']
        if od_pdt_brand_id:
            domain.append(('od_pdt_brand_id','=',od_pdt_brand_id[0]))
        lot_id = data['lot_id']
        if lot_id:
            domain.append(('lot_id','=',lot_id[0]))
        negative_move = data['negative_move']
        if negative_move:
            domain.append(('negative_move_id','!=',False))
        usage = data['usage']
        if usage:
            domain.append(('usage','=',usage))
        if context.get('cost'):
            return {
                'domain': domain,
                'view_type': 'form',
                'view_mode': 'graph,tree,form',
                'res_model': 'od.stock.quant.report',
                'type': 'ir.actions.act_window',
            }
        else:
            return {
                'domain': domain,
                'view_type': 'form',
                'view_mode': 'graph,tree,form',
                'res_model': 'od.stock.quant.report.no.cost',
                'type': 'ir.actions.act_window',
            }

#With Cost
class od_stock_quant_report(osv.osv):
    _name = "od.stock.quant.report"
    _description = "Stock Quants Report"
    _auto = False
    _columns = {
        'location_id':fields.many2one('stock.location', 'Location', readonly=True),
        'qty':fields.float('Quantity',readonly=True),
        'in_date':fields.datetime('incoming Date',readonly=True),
        'product_id':fields.many2one('product.product','Product',readonly=True),
        'product_categ_id': fields.many2one('product.category', 'Product Category', readonly=True),
        'od_pdt_group_id':fields.many2one('od.product.group','Group',readonly=True),
        'od_pdt_sub_group_id':fields.many2one('od.product.sub.group','Sub Group',readonly=True),
        'od_pdt_brand_id':fields.many2one('od.product.brand','Brand',readonly=True),
        'od_pdt_classification_id':fields.many2one('od.product.classification','Classification',readonly=True),
        'lot_id':fields.many2one('stock.production.lot','Lot',readonly=True),
        'cost':fields.float('Cost',readonly=True),
        'value':fields.float('Value',readonly=True),
        'list_price':fields.float('Public Price',readonly=True),
        'negative_move_id':fields.many2one('stock.move','Negative Move',readonly=True),
        'usage': fields.selection([
                        ('supplier', 'Supplier Location'),
                        ('view', 'View'),
                        ('internal', 'Internal Location'),
                        ('customer', 'Customer Location'),
                        ('inventory', 'Inventory'),
                        ('procurement', 'Procurement'),
                        ('production', 'Production'),
                        ('transit', 'Transit Location')],
                'Location Type', readonly=True)
    }
    _rec_name = 'location_id'
    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'od_stock_quant_report')
        cr.execute("""
            create or replace view od_stock_quant_report as (
                select  ROW_NUMBER () OVER (ORDER BY qnt.id ) AS id,
                qnt.product_id,
qnt.location_id,
qnt.qty,
qnt.cost as cost,
coalesce((qnt.qty * qnt.cost),0) as value,
coalesce (pdtt.list_price, 0) as list_price,
qnt.lot_id,
qnt.negative_move_id,
qnt.in_date,
pdtt.categ_id AS product_categ_id,
pdtt.od_pdt_group_id,
pdtt.od_pdt_sub_group_id,
pdtt.od_pdt_brand_id,
pdtt.od_pdt_classification_id,
loc.usage
from stock_quant qnt
LEFT JOIN product_product pdt ON (qnt.product_id =  pdt.id)
LEFT JOIN product_template pdtt ON (pdt.product_tmpl_id =  pdtt.id)
LEFT JOIN stock_location loc ON (qnt.location_id = loc.id)

)
        """)


#With out Cost
class od_stock_quant_report_no_cost(osv.osv):
    _name = "od.stock.quant.report.no.cost"
    _description = "Stock Quants Report"
    _auto = False
    _columns = {
        'location_id':fields.many2one('stock.location', 'Location', readonly=True),
        'qty':fields.float('Quantity',readonly=True),
        'in_date':fields.datetime('incoming Date',readonly=True),
        'product_id':fields.many2one('product.product','Product',readonly=True),
        'product_categ_id': fields.many2one('product.category', 'Product Category', readonly=True),
        'od_pdt_group_id':fields.many2one('od.product.group','Group',readonly=True),
        'od_pdt_sub_group_id':fields.many2one('od.product.sub.group','Sub Group',readonly=True),
        'od_pdt_brand_id':fields.many2one('od.product.brand','Brand',readonly=True),
        'od_pdt_classification_id':fields.many2one('od.product.classification','Classification',readonly=True),
        'lot_id':fields.many2one('stock.production.lot','Lot',readonly=True),
        'negative_move_id':fields.many2one('stock.move','Negative Move',readonly=True),
        'usage': fields.selection([
                        ('supplier', 'Supplier Location'),
                        ('view', 'View'),
                        ('internal', 'Internal Location'),
                        ('customer', 'Customer Location'),
                        ('inventory', 'Inventory'),
                        ('procurement', 'Procurement'),
                        ('production', 'Production'),
                        ('transit', 'Transit Location')],
                'Location Type', readonly=True)
    }
    _rec_name = 'location_id'
    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'od_stock_quant_report_no_cost')
        cr.execute("""
            create or replace view od_stock_quant_report_no_cost as (
                select  ROW_NUMBER () OVER (ORDER BY qnt.id ) AS id,
                qnt.product_id,
qnt.location_id,
qnt.qty,
qnt.lot_id,
qnt.negative_move_id,
qnt.in_date,
pdtt.categ_id AS product_categ_id,
pdtt.od_pdt_group_id,
pdtt.od_pdt_sub_group_id,
pdtt.od_pdt_brand_id,
pdtt.od_pdt_classification_id,
loc.usage
from stock_quant qnt
LEFT JOIN product_product pdt ON (qnt.product_id =  pdt.id)
LEFT JOIN product_template pdtt ON (pdt.product_tmpl_id =  pdtt.id)
LEFT JOIN stock_location loc ON (qnt.location_id = loc.id)

)
        """)
