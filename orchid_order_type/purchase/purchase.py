# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
from openerp.tools.translate import _

class purchase_order(osv.osv):
    _inherit = 'purchase.order'
    
    
    def action_picking_create(self, cr, uid, ids, context=None):
        for order in self.browse(cr, uid, ids):
            order_type_id = order.od_order_type_id and order.od_order_type_id.id
            picking_vals = {
                'picking_type_id': order.picking_type_id.id,
                'partner_id': order.partner_id.id,
                'date': max([l.date_planned for l in order.order_line]),
                'origin': order.name,
                'od_order_type_id':order_type_id
            }
            picking_id = self.pool.get('stock.picking').create(cr, uid, picking_vals, context=context)
            self._create_stock_moves(cr, uid, order, order.order_line, picking_id, context=context)

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        if vals.get('name','/') == '/' and vals.get('od_order_type_id'):
            session = self.pool['od.order.type'].browse(cr, uid, vals['od_order_type_id'], context=context)
            vals['name'] = session.sequence_id._next()
        return super(purchase_order, self).create(cr,uid,vals,context=context)

    _columns = {
        'od_order_type_id': fields.many2one('od.order.type','Order Type',readonly=True,domain=[('type','=','po')], states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},)
    }
    def _prepare_invoice(self, cr, uid, order, line_ids, context=None):
        res = super(purchase_order,self)._prepare_invoice(cr, uid, order, line_ids, context=context)
        od_order_type_id = order.od_order_type_id and order.od_order_type_id.id
        journal_id = order.od_order_type_id and order.od_order_type_id.journal_id and order.od_order_type_id.journal_id.id
        if journal_id:
            res['journal_id'] = journal_id
        if od_order_type_id:
            res.update({'od_order_type_id':od_order_type_id})
        return res

    
    def _prepare_inv_line(self, cr, uid, account_id, order_line, context=None):
        """Collects require data from purchase order line that is used to create invoice line
        for that purchase order line
        :param account_id: Expense account of the product of PO line if any.
        :param browse_record order_line: Purchase order line browse record
        :return: Value for fields of invoice lines.
        :rtype: dict
        """
        stock_input = order_line.order_id and order_line.order_id.od_order_type_id and order_line.order_id.od_order_type_id.stock_input_account_id and order_line.order_id.od_order_type_id.stock_input_account_id.id
        if stock_input:
            account_id = stock_input  
        return {
            'name': order_line.name,
            'account_id': account_id,
            'price_unit': order_line.price_unit or 0.0,
            'quantity': order_line.product_qty,
            'product_id': order_line.product_id.id or False,
            'uos_id': order_line.product_uom.id or False,
            'invoice_line_tax_id': [(6, 0, [x.id for x in order_line.taxes_id])],
            'account_analytic_id': order_line.account_analytic_id.id or False,
            'purchase_line_id': order_line.id,
        }



#     def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
#         partner = self.pool.get('res.partner')
#         result = super(purchase_order,self).onchange_partner_id(cr, uid, ids, partner_id,context)
#         if partner_id:
#             od_po_order_type_id = partner.browse(cr,uid,partner_id,context).od_po_order_type_id.id or False
#             print "::::::",od_po_order_type_id
#             result['value']['od_order_type_id'] = od_po_order_type_id  
#         return result
    def onchange_partner_id(self, cr, uid, ids, part, context=None):
        result = super(purchase_order,self).onchange_partner_id(cr, uid, ids, part,context)
        if part:
            od_po_order_type_id = self.pool.get('res.partner').browse(cr,uid,part,context).od_po_order_type_id.id or False
            if od_po_order_type_id:
                result['value']['od_order_type_id'] = od_po_order_type_id
  
        return result
















    def _create_stock_moves(self, cr, uid, order, order_lines, picking_id=False, context=None):
        stock_move = self.pool.get('stock.move')
        todo_moves = []
        new_group = self.pool.get("procurement.group").create(cr, uid, {'name': order.name, 'partner_id': order.partner_id.id,'od_order_type_id': order.od_order_type_id and order.od_order_type_id.id or False}, context=context)

        for order_line in order_lines:
            if not order_line.product_id:
                continue

            if order_line.product_id.type in ('product', 'consu'):
                for vals in self._prepare_order_line_move(cr, uid, order, order_line, picking_id, new_group, context=context):
                    move = stock_move.create(cr, uid, vals, context=context)
                    todo_moves.append(move)

        todo_moves = stock_move.action_confirm(cr, uid, todo_moves)
        stock_move.force_assign(cr, uid, todo_moves)
