# -*- coding: utf-8 -*-
import time
from lxml import etree
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp.tools import float_compare
from openerp.report import report_sxw
import openerp
class account_voucher(osv.osv):
    _inherit = "account.voucher"
    _columns = {
        'od_advance_payment': fields.boolean('Advance Payment', help="Check this if you want to input an Adv.payment on the prepayment accounts."),
        'od_purchase_order_id': fields.many2one('purchase.order', 'Purchase Order'),
        'od_sale_order_id':fields.many2one('sale.order', 'Sale Order')
    }
    _defaults = {
        'od_advance_payment': False,
    }




    def account_move_get(self, cr, uid, voucher_id, context=None):


        voucher = self.pool.get('account.voucher').browse(cr,uid,voucher_id,context)

        move = super(account_voucher,self).account_move_get(cr, uid, voucher_id, context=context)
        if voucher.od_advance_payment:
            if voucher.od_purchase_order_id:
                move['ref'] = "Advance:" + voucher.od_purchase_order_id.name or '/' 
            elif voucher.od_sale_order_id:
                move['ref'] = "Advance:" + voucher.od_sale_order_id.name or '/' 
            else:   
                move['ref'] = "Advance"
        return move



