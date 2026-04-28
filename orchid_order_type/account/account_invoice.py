# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.tools.translate import _

class account_invoice(models.Model):
    _inherit = 'account.invoice'
    od_order_type_id = fields.Many2one('od.order.type','Type', readonly=True, states={'draft': [('readonly', False)]})
    @api.model
    def line_get_convert(self, line, part, date):
        res = super(account_invoice,self).line_get_convert(line,part,date)
        account_id = res['account_id']
        product_id = res.get('product_id',False)
        product_pool = self.env['product.product']
        order_type = self.od_order_type_id and self.od_order_type_id
        if product_id and order_type:
            product_obj = product_pool.browse(product_id)
            stock_output_acc = product_obj.property_stock_account_output and product_obj.property_stock_account_output.id or False
            if not stock_output_acc:
                stock_output_acc = product_obj.categ_id.property_stock_account_output_categ and product_obj.categ_id.property_stock_account_output_categ.id or False
            if account_id == stock_output_acc:
                stock_output = order_type.stock_output_account_id and order_type.stock_output_account_id.id
                if stock_output:
                    res['account_id'] = stock_output
        return res
    @api.onchange('od_order_type_id')
    def onchange_order_type_id(self):
        if self.od_order_type_id:
            income_acc_id = self.od_order_type_id and self.od_order_type_id.income_acc_id and self.od_order_type_id.income_acc_id.id
            expense_acc_id = self.od_order_type_id and self.od_order_type_id.expense_acc_id and self.od_order_type_id.expense_acc_id.id
            journal_id = self.od_order_type_id and self.od_order_type_id.journal_id and self.od_order_type_id.journal_id.id
            self.od_inter_inc_acc_id = income_acc_id
            self.od_inter_exp_acc_id = expense_acc_id
            self.journal_id = journal_id
