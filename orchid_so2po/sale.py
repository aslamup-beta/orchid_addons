# -*- coding: utf-8 -*-

import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.exceptions import Warning

class sale_order(osv.osv):
    _name = 'sale.order'
    _inherit = 'sale.order'

    _columns = {
        'od_purchase_requsition_id': fields.many2one('purchase.requisition','Purchase Requsition'),
    }
    
    def generate_purchase_order(self, cr, uid, ids, supplier_id, pricelist_id, warehouse_id, wizard,copy_desc, context=None):
        purchase_obj = self.pool.get('purchase.order')
        purchase_line_obj = self.pool.get('purchase.order.line')
        warehouse_obj = self.pool.get('stock.warehouse')
        purchase_requsition_obj = self.pool.get('purchase.requisition')
        purchase_requsition_line_obj = self.pool.get('purchase.requisition.line')
        warehouse = warehouse_obj.browse(cr, uid, warehouse_id, context=context)
        if not warehouse:
            return False
        if isinstance(warehouse, list):
            warehouse = warehouse[0]
        self_order = self.browse(cr,uid,ids,context=context)[0]
        date_order = self_order and self_order.date_order
        sale_order = self_order and self_order.name
        purchase_requsition_id = wizard.purchase_requsition_id and wizard.purchase_requsition_id.id
        if not purchase_requsition_id:
            for order in self.browse(cr, uid, ids, context=context):
                vals = {}
                line_vals = {}
                vals['origin'] = order.name
#                sale_order = order.name
                vals['exclusive'] = 'multiple'
#                date_order = order.date_order
                purchase_requsition_id = purchase_requsition_obj.create(cr, uid, vals, context=context)
                
               
                for line in order.order_line:
                    line_vals['product_id'] = line.product_id and line.product_id.id
                    line_vals['product_qty'] = line.product_uom_qty
                    line_vals['requisition_id'] = purchase_requsition_id
                    purchase_requsition_line_obj.create(cr, uid, line_vals, context=context)
            self.write(cr,uid,ids,{'od_purchase_requsition_id':purchase_requsition_id}) 

        purchase_line_vals = {}
        for purchase in wizard:
            vals = purchase_obj.onchange_partner_id(cr, uid, [], supplier_id)['value']
            currency_id= self.pool.get('product.pricelist').browse(cr, uid, purchase.pricelist_id.id, context=context).currency_id.id
            picking_type_id = purchase_obj._get_picking_in(cr,uid,context=context)
            onchange_pick_type = purchase_obj.onchange_picking_type_id(cr,uid,[],picking_type_id,context)['value']
            vals.update(onchange_pick_type)
            vals['origin'] = sale_order
            vals['partner_id'] = purchase.partner_id.id
            vals['pricelist_id'] = purchase.pricelist_id.id
            vals['currency_id'] = currency_id
            vals['warehouse_id'] = purchase.warehouse_id.id
            vals['picking_type_id'] = picking_type_id
            vals['requisition_id'] = purchase_requsition_id
            vals['date_order'] = date_order
            purchase_id = purchase_obj.create(cr, uid, vals, context=context)
            for ob in wizard.od_purchase_generate_line:

                purchase_line_vals = purchase_line_obj.onchange_product_id(cr, uid, ids, pricelist_id, ob.product_id.id,
                                                ob.product_qty, ob.product_uom_id.id, supplier_id,context=context)['value']
                
                product_id  = ob.product_id and ob.product_id.id
                purchase_line_vals['product_id'] = product_id
                if not (product_id or copy_desc):
                    raise Warning('Either You should Tick Copy Description or You should Select Product in Product Line')
                if not purchase_line_vals.get('price_unit', False):
                    purchase_line_vals['price_unit'] = ob.price
                purchase_line_vals['product_uom'] = ob.product_uom_id.id
                purchase_line_vals['product_uom_qty'] = ob.product_qty
                purchase_line_vals['order_id'] = purchase_id
                if not (ob.product_id and ob.product_id.id):
                    purchase_line_vals['date_planned'] = date_order
                    purchase_line_vals['od_gross'] = ob.price
                if copy_desc:
                    purchase_line_vals['name'] = ob.name
                   
                purchase_line_obj.create(cr, uid, purchase_line_vals, context=context)
                
                
        
        return True

sale_order()

