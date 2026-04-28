# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
from openerp.tools.translate import _

class sale_order(osv.osv):
    _inherit = 'sale.order'

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        if vals.get('name','/') == '/' and vals.get('od_order_type_id'):
            session = self.pool['od.order.type'].browse(cr, uid, vals['od_order_type_id'], context=context)
            vals['name'] = session.sequence_id._next()
        return super(sale_order, self).create(cr,uid,vals,context=context)

    _columns = {
        'od_order_type_id': fields.many2one('od.order.type','Type',readonly=True,domain=[('type','=','so')], states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},required=True)
    }
    def onchange_partner_id(self, cr, uid, ids, part, context=None):
        result = super(sale_order,self).onchange_partner_id(cr, uid, ids, part,context)
        if part:
            od_so_order_type_id = self.pool.get('res.partner').browse(cr,uid,part,context).od_so_order_type_id.id or False
            if od_so_order_type_id:
                result['value']['od_order_type_id'] = od_so_order_type_id
  
        return result
    
    

    def _prepare_procurement_group(self, cr, uid, order, context=None):
        if order.od_order_type_id:
            return {'name': order.name, 'partner_id': order.partner_shipping_id.id,'od_order_type_id':order.od_order_type_id and order.od_order_type_id.id,'od_analytic_id':order.project_id and order.project_id.id}
        return {'name': order.name, 'partner_id': order.partner_shipping_id.id}
    
    def _prepare_invoice(self, cr, uid, order, lines, context=None):
        invoice_vals = super(sale_order,self)._prepare_invoice(cr, uid, order, lines, context=context)
        od_order_type_id = order.od_order_type_id.id
        journal_id = order.od_order_type_id and order.od_order_type_id.journal_id and order.od_order_type_id.journal_id.id
        if journal_id:
            invoice_vals['journal_id'] = journal_id
        invoice_vals.update({'od_order_type_id':od_order_type_id})
        return invoice_vals
