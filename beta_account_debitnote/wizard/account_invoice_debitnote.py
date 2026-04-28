# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class AccountInvoiceDebitnote(models.TransientModel):
    """Debit Notes"""

    _name = 'account.invoice.debitnote'
    _description = "Debit Note"

    description = fields.Char(
        string='Reason',
        required=True,
    )
    date_invoice = fields.Date(
        string='Debit Note Date',
        default=fields.Date.context_today,
        required=True,
    )
    date = fields.Date(string='Accounting Date')
    filter_debit = fields.Selection(
        [('debit', 'Create a draft debit note')],
        string='Debit Method',
        default='debit',
        required=True,
    )

    @api.multi
    def compute_debitnote(self):
        inv_obj = self.env['account.invoice']
        context = dict(self._context or {})
        xml_id = False
        for form in self:
            created_inv = []
            date = False
            description = False
            for inv in inv_obj.browse(context.get('active_ids')):
                if inv.state in ['draft', 'cancel']:
                    raise ValidationError(_("""Cannot create debit note for
                                           draft/cancel invoice."""))

                date = form.date or False
                description = form.description or inv.name
                debitnote = inv.debitnote(form.date_invoice,
                                          date,
                                          description,
                                          inv.journal_id.id)
                created_inv.append(debitnote.id)

        xml_id = (inv.type == 'out_invoice') and 'action_invoice_tree1' or\
                 (inv.type == 'in_invoice') and 'action_invoice_tree4'
        result = self.env.ref('account.' + xml_id)
        result = result.read()[0]
        result['domain'] = [('id', 'in', created_inv)]
        return result

    @api.multi
    def invoice_debitnote(self):
        for invoice in self:
            return invoice.compute_debitnote()
