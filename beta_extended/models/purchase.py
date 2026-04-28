# -*- coding: utf-8 -*-

import itertools
from lxml import etree

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp
from openerp.tools import amount_to_text_en
# from . import amount_to_ar
from pprint import pprint
from openerp import tools
from itertools import groupby


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    print_with_stamp = fields.Boolean("Print With Stamp")

    @api.multi
    def amount_to_text_en(self, amount, currency, check):
        convert_amount_in_words = amount_to_text_en.amount_to_text(amount, lang='en', currency=currency)
        company_id = self.company_id and self.company_id.id
        if check == 'USD':
            print("@@@@@")
            convert_amount_in_words = convert_amount_in_words.replace('USD', 'Dollars')
            convert_amount_in_words = convert_amount_in_words.replace('Cents', 'Cents')
        elif check == 'SAR':
            convert_amount_in_words = convert_amount_in_words.replace('Cent', 'Halala')
            convert_amount_in_words = convert_amount_in_words.replace('SAR', 'Riyal')
        else:
            convert_amount_in_words = convert_amount_in_words.replace('Cents', 'Fills')
            convert_amount_in_words = convert_amount_in_words.replace('AED', 'Dirhams')

        return convert_amount_in_words

    def action_picking_create(self, cr, uid, ids, context=None):
        print("action_picking_create")
        res = super(PurchaseOrder, self).action_picking_create(cr, uid, ids, context=context)
        print("res.................sssssssssssss", res)
        purchase = self.browse(cr, uid, ids[0], context)
        picking = self.pool.get('stock.picking').browse(cr, uid, res, context=context)
        print("picking", picking)
        print("purchase.od_customer_id", purchase.od_customer_id)
        if picking:
            if purchase.od_customer_id:
                picking.write({'od_customer_id': purchase.od_customer_id.id})
        # gggg
        return res
