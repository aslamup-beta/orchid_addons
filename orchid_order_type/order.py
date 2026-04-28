# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
from openerp.tools.translate import _

class od_order_type(osv.osv):
    _name = "od.order.type"
    _description = "Order Type"
    _columns = {
        'name': fields.char('Name',required=True),
        'sequence_id': fields.many2one('ir.sequence',string='Sequence',copy=False),
        'type': fields.selection([('so', 'Sale Order'),('po', 'Purchase Order')],'Type', required=True,copy=False),
        'picking_type_id':fields.many2one('stock.picking.type','Picking Type'),
        'company_id':fields.many2one('res.company', 'Company', required=True, readonly=True),
        'expense_acc_id': fields.property(type='many2one',relation='account.account',string="Expense Account" ,domain="[('type', '=', 'other'),('company_id','=',company_id)]",),
        'income_acc_id': fields.property(type='many2one',relation='account.account',string="Income Account", domain="[('type', '=', 'other'),('company_id','=',company_id)]",),
        'journal_id':fields.many2one('account.journal', 'Journal',required="1"),
        'sample':fields.boolean('No Invoice'),
        'stock_journal_id':fields.many2one('account.journal','Stock Journal'),
        'stock_input_account_id':fields.many2one('account.account','Stock Input Account'),
        'stock_output_account_id':fields.many2one('account.account','Stock Output Account'),
        'stock_valuation_account_id':fields.many2one('account.account','Stock Valuation Account'),
    }
    def create(self, cr, uid, values, context=None):
        ir_sequence = self.pool.get('ir.sequence')
        values['sequence_id'] = ir_sequence.create(cr, uid, {
            'name': 'SO-%s' % values['name'],
            'padding': 4,
            'prefix': "%s/"  % values['name'],
            'code': "od.order.type",
            'company_id': values.get('company_id', False),
        }, context=context)
        return super(od_order_type, self).create(cr, uid, values, context=context)

    def unlink(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.sequence_id:
                obj.sequence_id.unlink()
        return super(od_order_type, self).unlink(cr, uid, ids, context=context)

    _defaults = {
        'company_id': lambda self,cr,uid,c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
    }


class procurement_order(osv.osv):
    _inherit = 'procurement.order'
    
    def _run_move_create(self, cr, uid, procurement, context=None):
        vals = super(procurement_order, self)._run_move_create(cr, uid, procurement, context=context)


#        print "#############@@@@@@@@@@@@@@%%%%%%%%%%%%%^^^^^^^^^^^^^^^^^&&&&&&&&&&&&",procurement.od_order_type_id
#        new_vals={
#            'od_order_type_id': procurement.od_order_type_id and procurement.od_order_type_id.id or False,
#        }
##        vals.update(new_vals)
        return vals


class res_partner(osv.osv):
    _inherit = 'res.partner'

    _columns = {
        'od_so_order_type_id': fields.many2one('od.order.type','Sale Type',domain=[('type','=','so')]),
        'od_po_order_type_id': fields.many2one('od.order.type','Purchase Type',domain=[('type','=','po')])

    }

class stock_invoice_onshipping(osv.osv_memory):
    _inherit = "stock.invoice.onshipping"
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(stock_invoice_onshipping, self).default_get(cr, uid, fields, context=context)
        res_ids = context and context.get('active_ids', [])
        pick_obj = self.pool.get('stock.picking')
        pickings = pick_obj.browse(cr, uid, res_ids, context=context)
        od_type_ids = list(set([p.od_order_type_id for p in pickings ]))
        od_type = len(od_type_ids) == 1 and od_type_ids[0] and od_type_ids[0]
        if od_type:
            journal_id = od_type.journal_id and od_type.journal_id.id
            res['journal_id'] = journal_id
        return res


