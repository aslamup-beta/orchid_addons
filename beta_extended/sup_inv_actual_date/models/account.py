# -*- coding: utf-8 -*-

import itertools
from lxml import etree

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    actual_inv_date = fields.Date(string="Actual Invoice Date")

    @api.multi
    def invoice_validate(self):
        res = super(AccountInvoice, self).invoice_validate()
        for rec in self:
            if rec.type == 'in_invoice':
                if rec.move_id:
                    rec.move_id.write({
                        'actual_inv_date' : rec.actual_inv_date if rec.actual_inv_date else False,
                        'sup_inv_number' : rec.supplier_invoice_number,
                    })
        return res



class AccountMove(models.Model):
    _inherit = "account.move"

    actual_inv_date = fields.Date(string="Actual Invoice Date")
    sup_inv_number = fields.Char(string="Invoice Number")


