from openerp import api, fields, models, exceptions
from decimal import Decimal
import uuid


class AccountMoveLine(models.Model):
    _inherit = "account.invoice.line"

    # BR-KSA-DEC-01 for BT-138 only
#     @api.onchange('discount')
#     def zatca_onchange_discount(self):
#         for res in self:
#             res.discount = 100 if res.discount > 100 else (0 if res.discount < 0 else res.discount)

    #BR-KSA-F-04
#     @api.onchange('quantity')
#     def zatca_BR_KSA_F_04(self):
#         self.quantity = 0 if self.quantity < 0 else self.quantity
#         self.price_unit = abs(self.price_unit)

    @api.onchange('invoice_line_tax_id')
    def onchange_tax_ids(self):
        if self.env.user.company_id.is_zatca and len(self.invoice_line_tax_id.ids) > 1:
            raise exceptions.ValidationError("Only 1 tax can be applied per line.")