# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
class stock_move(osv.osv):
    _inherit = "stock.move"
    def _get_price_unit_invoice(self, cr, uid, move_line, type, context=None):
        price = super(stock_move,self)._get_price_unit_invoice(cr, uid, move_line, type, context=None)
        if move_line.so_line_id:
            price = move_line.so_line_id.price_unit
        return price
