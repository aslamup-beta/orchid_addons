# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
class purchase_order(models.Model):
    _inherit = 'purchase.order'
    
    @api.one
    @api.depends('amount_total','order_line')
    def _compute_forgin_curr_amt(self):
        user_currency_id = self.env.user.company_id.currency_id
        from_currency = self.currency_id.with_context(date=self.date_order)
        self.od_amount_in_local_currency = from_currency and from_currency.compute(self.amount_total,user_currency_id) or self.amount_total
        
    od_amount_in_local_currency = fields.Float(string='Local Currency', digits=dp.get_precision('Account'),
        compute='_compute_forgin_curr_amt', store=True,
        help="Forgin Curr amount.")