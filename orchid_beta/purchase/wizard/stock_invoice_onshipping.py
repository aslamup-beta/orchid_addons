from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import datetime
class stock_invoice_onshipping(osv.osv_memory):
    _inherit = "stock.invoice.onshipping"
    def default_get(self, cr, uid, fields, context=None):
        res = super(stock_invoice_onshipping, self).default_get(cr, uid, fields, context=context)
        if context is None:
            context = {}
        active_id = context and  context.get('active_id')
        vals = []
        if active_id:
            stock_picking_obj = self.pool.get('stock.picking').browse(cr, uid, active_id, context=context)
            date = datetime.strptime(stock_picking_obj.date, '%Y-%m-%d %H:%M:%S') 
            date = date.strftime('%Y-%m-%d')
            res.update({'invoice_date': date})
        return res


    def create_invoice(self, cr, uid, ids, context=None):
        res = super(stock_invoice_onshipping,self).create_invoice(cr, uid, ids, context)
        data = self.browse(cr, uid, ids[0], context=context)
        active_id = context and  context.get('active_id')
        invoice_date = data.invoice_date
        if invoice_date:
            self.pool.get('account.invoice').write(cr,uid,[res[0]],{'date_invoice':invoice_date,'date_due':invoice_date})
        return res


