# -*- coding: utf-8 -*-

import itertools
from lxml import etree

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp

class account_invoice(models.Model):
    _inherit = "account.invoice"
    od_inter_exp_acc_id = fields.Many2one('account.account', string='Expence. Account', readonly=True, states={'draft': [('readonly', False)]},       help="The account used for write Expnse.")
    od_inter_inc_acc_id = fields.Many2one('account.account', string='Income. Account', readonly=True, states={'draft': [('readonly', False)]},       help="The account used for write Income.")
#     @api.model
#     def create(self, values):
#         if values.get('od_order_type_id'):
#             od_order_type_id = values.get('od_order_type_id')
#             if od_order_type_id:
#                 od_type = self.env['od.order.type'].browse(od_order_type_id)
#                 exp_accnt_id = od_type.expense_acc_id.id
#                 inc_accnt_id = od_type.income_acc_id.id
#                 values.update({'od_inter_inc_acc_id':inc_accnt_id,'od_inter_exp_acc_id':exp_accnt_id})
#         return super(account_invoice, self).create(values)
#     @api.multi
#     def write(self, values):
#         if values.get('od_order_type_id'):
#             od_order_type_id = values.get('od_order_type_id')
#             if od_order_type_id:
#                 od_type = self.env['od.order.type'].browse(od_order_type_id)
#                 exp_accnt_id = od_type.expense_acc_id.id
#                 inc_accnt_id = od_type.income_acc_id.id
#                 values.update({'od_inter_inc_acc_id':inc_accnt_id,'od_inter_exp_acc_id':exp_accnt_id})
#         return super(account_invoice, self).write(values)
class account_invoice_line(models.Model):
    _inherit = "account.invoice.line"
#    
#Override to update the intercompany sales(Interchange accounts)
    @api.model
    def move_line_get_item(self, line):
        account_id = line.account_id.id
        if line.invoice_id.type == 'out_invoice':
            account_id = line.invoice_id and line.invoice_id.od_inter_inc_acc_id and line.invoice_id.od_inter_inc_acc_id.id or line.account_id.id
        return {
            'type': 'src',
            'name': line.name.split('\n')[0][:64],
            'price_unit': line.price_unit,
            'quantity': line.quantity,
            'price': line.price_subtotal,
#            'account_id': line.account_id.id,
            'account_id': account_id,
            'product_id': line.product_id.id,
            'uos_id': line.uos_id.id,
            'account_analytic_id': line.account_analytic_id.id,
            'taxes': line.invoice_line_tax_id,
        }


