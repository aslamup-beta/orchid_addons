# -*- coding: utf-8 -*-

import itertools
from lxml import etree

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def invoice_validate(self):
        for rec in self:
            if rec.purchase_id and rec.type == 'in_invoice':
                sup_invs = self.env['account.invoice'].search(
                    [('type', 'in', ['in_invoice', 'in_refund']),('state', '!=', 'cancel')])
                po_sup_inv_list = []
                total_amount = 0
                for inv in sup_invs:
                    if inv.purchase_id.id == rec.purchase_id.id:
                        po_sup_inv_list.append(inv)
                        if inv.type == 'in_invoice':
                            total_amount = total_amount + inv.amount_untaxed
                        if inv.type == 'in_refund':
                            total_amount = total_amount - inv.amount_untaxed
                        # total_amount = total_amount + inv.amount_total
                if total_amount > rec.purchase_id.amount_total:
                    if (total_amount-rec.purchase_id.amount_total) >= 1:
                        raise Warning(
                        "The total sum of all supplier invoices should not exceed the corresponding purchase order.")
        return super(AccountInvoice, self).invoice_validate()
