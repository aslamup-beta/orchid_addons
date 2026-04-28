# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
from openerp.tools.translate import _

class generate_purchase_order(osv.osv_memory):
    _name = 'orchid_so2po.generate_purchase_order'
    _description = 'Generate Purchase Order'

    _columns = {
        'partner_id': fields.many2one('res.partner', 'Supplier', required=True, domain="[('supplier','=',True)]"),
        'pricelist_id': fields.many2one('product.pricelist', 'Purchase Pricelist', required=True, domain="[('type','=','purchase')]",
                        help="This pricelist will be used, instead of the default one, for purchases from the current partner",),
        'warehouse_id': fields.many2one('stock.warehouse', 'Warehouse', required=True,),
        'od_purchase_generate_line': fields.one2many('od.orchid_so2po.generate_purchase_order_line','purchase_generate_id','Purchase Generate Line'),
        'purchase_requsition_id': fields.many2one('purchase.requisition','Purchase Requsition'),
        'copy_desc':fields.boolean('Copy Description '),
    }

    def default_get(self, cr, uid, fields, context=None):
        res = super(generate_purchase_order, self).default_get(cr, uid, fields, context=context)
        if context is None:
            context = {}
        active_id = context and  context.get('active_id')
        vals = []
        if context.get('analytic',False):
            active_id = context.get('sale_id') 
        if active_id:
            sale_order_obj = self.pool.get('sale.order').browse(cr, uid, active_id, context=context)
            res.update({'purchase_requsition_id': sale_order_obj.od_purchase_requsition_id.id or False})
            for line in sale_order_obj.order_line:
                vals.append({'product_id':line.product_id.id,'name':line.name,'product_qty':line.product_uom_qty,'product_uom_id':line.product_uom.id})
            res.update({'od_purchase_generate_line': vals})
            if context.get('partner_id',False):
                partner_id = context.get('partner_id')
                planned_date = context.get('planned_date')
                res.update({'partner_id':partner_id})
        return res


    
    def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
        partner_obj = self.pool.get('res.partner')
        partner = partner_obj.browse(cr, uid, partner_id, context=context)
        if not partner:
            return {}
        if isinstance(partner, list):
            partner = partner[0]
        
        if partner.property_product_pricelist_purchase:
            return {'value': {'pricelist_id': partner.property_product_pricelist_purchase.id}}
        else:
            return {}
    
    def generate_purchase_order(self, cr, uid, ids, context=None):
        for wizard in self.browse(cr, uid, ids, context=context):
            sale_order_ids = [context['active_id']]
            if context.get('analytic'):
                sale_order_ids = [context.get('sale_id')]
            sale_obj = self.pool.get('sale.order')
            sale_obj.generate_purchase_order(cr, uid, sale_order_ids, wizard.partner_id.id, wizard.pricelist_id.id, 
                                             wizard.warehouse_id.id, wizard,wizard.copy_desc, context=context)
        return { 'type': 'ir.actions.act_window_close'}
        
generate_purchase_order()




class od_generate_purchase_order_line(osv.osv_memory):
    _name = 'od.orchid_so2po.generate_purchase_order_line'
    _description = 'Generate Purchase Order Line'

    _columns = {
        'purchase_generate_id': fields.many2one('orchid_so2po.generate_purchase_order','Purchase Generate',ondelete='cascade'),
        'product_id':fields.many2one('product.product',string='Product'),
        'name':fields.char('Description'),
        'product_uom_id':fields.many2one('product.uom',string='Unit',required="1"),
        'product_qty':fields.float('Qty'),
        'price':fields.float('Price'),
        'select':fields.boolean('Select')
    }
    _defaults = {
        'select': False,
    }

