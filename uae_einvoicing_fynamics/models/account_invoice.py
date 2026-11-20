# -*- coding: utf-8 -*-
import json

from openerp import models, fields, api
from openerp.exceptions import Warning

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    fynamics_status = fields.Selection([
        ('not_submitted', 'Not Submitted'),
        ('queued', 'Queued'),
        ('success', 'Success'),
        ('failure', 'Failure'),
        ('error', 'Error'),
    ], default='not_submitted', readonly=True,copy=False)
    fynamics_uuid = fields.Char(readonly=True, copy=False)
    fynamics_message = fields.Text(readonly=True, copy=False)
    fynamics_error = fields.Text(readonly=True, copy=False)
    fynamics_json = fields.Text(readonly=True, copy=False)
    fynamics_warning = fields.Text(readonly=True, copy=False)
    fynamics_print_url = fields.Char(string='Invoice PDF', readonly=True, copy=False)
    fynamics_compliance_url = fields.Char(string='Compliance Files', readonly=True, copy=False)
    fynamics_submission_date = fields.Datetime(readonly=True, copy=False)
    fynamics_last_status_check = fields.Datetime(readonly=True, copy=False)
    fynamics_retry_count = fields.Integer(default=0, readonly=True, copy=False)

    fynamics_transaction_type_code = fields.Selection([
        ('00000000', 'Default (Standard domestic B2B)'),
        ('10000000', 'Free Trade Zone transaction'),
        ('01000000', 'Deemed Supply'),
        ('00100000', 'Profit Margin Scheme'),
        ('00010000', 'Summary Invoice'),
        ('00001000', 'Continuous Supply'),
        ('00000100', 'Disclosed Agent Billing'),
        ('00000010', 'E-commerce'),
        ('00000001', 'Exports'),
        ('00000011', 'E-commerce + Exports'),
    ], string='Transaction Type', default='00000000',
        help='8 flag bits: Free Trade Zone, Deemed Supply, Profit Margin, Summary Invoice, '
             'Continuous Supply, Disclosed Agent Billing, E-commerce, Exports. '
             'Multiple flags are allowed (e.g. 00000011).')
    fynamics_invoice_type_code = fields.Selection([
        ('380', 'Commercial Invoice'),
        ('381', 'Credit Note'),
        ('81', 'Credit Note (Out of Scope)'),
        ('389', 'Self-Billed Invoice'),
        ('261', 'Self-Billed Credit Note'),
        ('480', 'Invoice Out of Scope of Tax'),
    ], string='Invoice Type', default='380',
        help='381, 81 and 261 must include BillingReference.ID (the original invoice).')
    fynamics_payment_means_code = fields.Selection([
        ('1', 'Instrument not defined'),
        ('10', 'In cash'),
        ('20', 'Cheque'),
        ('30', 'Credit transfer'),
        ('42', 'Payment to bank account'),
        ('48', 'Bank card'),
        ('49', 'Direct debit'),
        ('55', 'Direct Debit (payer authorises debit)'),
        ('57', 'Standing agreement'),
        ('58', 'SEPA credit transfer (not applicable to UAE)'),
        ('59', 'SEPA direct debit (not applicable to UAE)'),
        ('68', 'Online payment service'),
        ('97', 'Clearing between partners'),
    ], string='Payment Method', default='42')
    fynamics_credit_note_reason_code = fields.Selection([
        ('DL8.61.1.A', 'Supply was cancelled'),
        ('DL8.61.1.B', 'Tax treatment changed (nature of supply changed)'),
        ('DL8.61.1.C', 'Consideration altered (e.g. bad debt relief)'),
        ('DL8.61.1.D', 'Goods/services returned, consideration returned'),
        ('DL8.61.1.E', 'Tax charged or tax treatment applied in error'),
        ('VD', 'VD - Volume discount'),
    ], string='Credit Note Reason Code',
        help='Only for customer refunds. All codes except VD need the original invoice.')

    @api.multi
    def _get_fynamics_config(self):
        """Fynamics configuration of the invoice's branch (od_branch_id)."""
        self.ensure_one()
        branch = self.od_branch_id
        if not branch:
            raise Warning('Select a Branch on the invoice before sending to Fynamics.')
        if not branch.fynamics_enabled:
            raise Warning('UAE E-Invoicing is not enabled for branch %s.' % branch.display_name)
        if not (branch.fynamics_client_id and branch.fynamics_client_secret):
            raise Warning('Fynamics credentials are missing for branch %s.' % branch.display_name)
        return branch

    @api.multi
    def action_submit_to_fynamics(self):
        from ..services.fynamics_api import FynamicsAPI
        from ..services.invoice_json import build_invoice_json

        for invoice in self:
            if invoice.state != 'open':
                raise Warning('Only validated/open invoices can be submitted to Fynamics.')
            if invoice.fynamics_status in ('queued', 'success'):
                raise Warning('Invoice %s is already submitted to Fynamics.' % invoice.number)

            config = invoice._get_fynamics_config()
            payload = None  # <-- NEW line
            try:
                payload = build_invoice_json(invoice)
                api = FynamicsAPI(config)
                result = api.submit_invoice_json(invoice, payload)
                uuid = result.get('uuid')
                if not uuid:
                    # Fynamics refused the invoice, e.g. {"message": "...", "success": 0}      # <-- NEW comment
                    raise Exception(result.get('message') or json.dumps(result))
                invoice.write({
                    'fynamics_status': 'queued',
                    'fynamics_uuid': uuid,
                    'fynamics_message': result.get('message') or '',
                    'fynamics_error': False,
                    'fynamics_json': json.dumps(payload, indent=2, default=str),
                    'fynamics_submission_date': fields.Datetime.now(),
                    'fynamics_retry_count': 0,
                })
            except Exception as e:
                # keep the failure on the record (API log is kept separately)
                invoice.write({
                    'fynamics_status': 'error',
                    'fynamics_error': getattr(e, 'value', None) or str(e),
                    'fynamics_retry_count': invoice.fynamics_retry_count + 1,
                    'fynamics_json': payload and json.dumps(payload, indent=2, default=str) or False
                })
        return True

    @api.multi
    def action_check_fynamics_status(self):
        from ..services.fynamics_api import FynamicsAPI
        for invoice in self:
            if not invoice.fynamics_uuid:
                raise Warning('No Fynamics UUID exists for this invoice.')
            config = invoice._get_fynamics_config()
            result = FynamicsAPI(config).get_document_status(invoice, invoice.fynamics_uuid)
            if result.get('success') == 0 and not result.get('documentStatus'):
                # unknown UUID: {"success": 0, "message": "Invoice not found ..."}
                invoice.write({
                    'fynamics_status': 'error',
                    'fynamics_error': result.get('message') or 'Document not found at Fynamics.',
                    'fynamics_last_status_check': fields.Datetime.now(),
                })
                continue
            status = result.get('documentStatus')   # SUCCESS / FAILED / QUEUED
            if status == 'SUCCESS':
                new_status = 'success'
            elif status == 'FAILED':
                new_status = 'failure'
            else:
                new_status = 'queued'

            errors = []
            warnings = []
            for key in ('from_c2', 'from_c3', 'to_c2', 'to_c3', 'to_c5'):
                section = result.get(key) or {}
                # validationResults are non-blocking findings; only treat them as
                # errors when the document did not succeed.
                for item in section.get('validationResults', []) or []:
                    text = item.get('text')
                    if not text:
                        continue
                    line = '[%s] %s' % (item.get('flag') or 'info', text)
                    if new_status != 'success' and str(item.get('flag')).lower() == 'error':
                        errors.append(line)
                    else:
                        warnings.append(line)
                for item in section.get('transmissionErrors', []) or []:
                    msg = '%s: %s' % (item.get('errorCode', ''), item.get('errorMessage', ''))
                    errors.append('%s - %s' % (key, msg.strip(': ')))
                if section.get('isTransmissionError') and not section.get('transmissionErrors'):
                    errors.append('%s: transmission error' % key)

            invoice.write({
                'fynamics_status': new_status,
                'fynamics_error': '\n'.join(errors) if errors else False,
                'fynamics_warning': '\n'.join(warnings) if warnings else False,
                'fynamics_message': result.get('message') or '',
                'fynamics_print_url': result.get('print_url') or invoice.fynamics_print_url,
                'fynamics_compliance_url': result.get('compliance_url') or invoice.fynamics_compliance_url,
                'fynamics_last_status_check': fields.Datetime.now(),
            })
        return True

    @api.multi
    def action_view_fynamics_logs(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Fynamics API Logs',
            'res_model': 'fynamics.api.log',
            'view_mode': 'tree,form',
            'domain': [('invoice_id', '=', self.id)],
            'context': {'default_invoice_id': self.id},
        }

    @api.multi
    def invoice_validate(self):
        # res = super(AccountMove, self).invoice_validate(cr, uid, ids, context=context)
        res = super(AccountInvoice, self).invoice_validate()
        for line in self:
            if line.company_id.id == 1 and line.type in ('out_invoice','out_refund'):
                if not line.od_branch_id:
                    raise Warning('Branch Field is mandatory for E-Invoicing')
        return res

    @api.model
    def _prepare_refund(self, invoice, date=None, period_id=None, description=None, journal_id=None):
        res = super(AccountInvoice, self)._prepare_refund(invoice, date=date, period_id=period_id,
                                                          description=description, journal_id=journal_id)
        res['fynamics_invoice_type_code'] = '381'
        return res

    @api.multi
    def action_cancel(self):
        for invoice in self:
            if invoice.fynamics_status == 'success':
                raise Warning(
                    'Invoice %s is already accepted by Fynamics / FTA and cannot be '
                    'cancelled. Issue a Credit Note instead.' % (invoice.number or ''))
        return super(AccountInvoice, self).action_cancel()