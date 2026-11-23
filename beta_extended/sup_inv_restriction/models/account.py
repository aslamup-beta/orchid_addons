# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import Warning


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def invoice_validate(self):
        for rec in self:
            if not (rec.purchase_id and rec.type == 'in_invoice'):
                continue

            po = rec.purchase_id
            inv_currency = rec.currency_id
            conv_date = rec.date_invoice or fields.Date.context_today(rec)

            # PO amount converted to the invoice currency (e.g. AED -> SAR)
            po_amount = po.amount_total
            if po.currency_id and po.currency_id != inv_currency:
                po_amount = po.currency_id.with_context(date=conv_date).compute(
                    po_amount, inv_currency)

            sup_invs = self.search([
                ('type', 'in', ['in_invoice', 'in_refund']),
                ('state', '!=', 'cancel'),
            ]).filtered(lambda i: i.purchase_id.id == po.id)

            total_amount = 0.0
            for inv in sup_invs:
                amount = inv.amount_untaxed
                if inv.currency_id != inv_currency:
                    amount = inv.currency_id.with_context(
                        date=inv.date_invoice or conv_date
                    ).compute(amount, inv_currency)

                if inv.type == 'in_invoice':
                    total_amount += amount
                else:  # in_refund
                    total_amount -= amount

            if (total_amount - po_amount) >= 1:
                raise Warning(_(
                    "The total sum of all supplier invoices (%.2f %s) should not "
                    "exceed the corresponding purchase order (%.2f %s)."
                ) % (total_amount, inv_currency.name, po_amount, inv_currency.name))

        return super(AccountInvoice, self).invoice_validate()