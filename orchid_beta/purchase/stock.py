from openerp.osv import fields, osv
from openerp.tools.translate import _

class stock_picking(osv.osv):
    _inherit = 'stock.picking'
    def _get_invoice_vals(self, cr, uid, key, inv_type, journal_id, move, context=None):
        result = super(stock_picking,self)._get_invoice_vals(cr, uid, key, inv_type, journal_id, move, context)
        result['od_discount'] = move.purchase_line_id and move.purchase_line_id.order_id and  move.purchase_line_id.order_id.od_discount
        return result

