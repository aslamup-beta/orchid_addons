# -*- coding: utf-8 -*-
from openerp import models, fields, api
from pprint import pprint
from datetime import datetime
import openerp.addons.decimal_precision as dp


class customer_statement(models.TransientModel):
    _inherit = 'cust.statement.rpt.wiz'

    def get_new_data(self):
        partner_id = self.partner_id.id
        invoice_ids = self.env['account.invoice'].search(
            [('state', 'in', ('open', 'accept')), ('type', '=', 'out_invoice'), ('partner_id', '=', partner_id),
             ('account_id.type', '=', 'receivable')])
        move_ids = []
        payment_move_ids = []
        result = []
        for inv in invoice_ids:
            due = inv.amount_total
            bal = inv.residual
            paid = due - bal
            move_ids.append(inv.move_id.id)
            if paid:
                payment_move_ids += [pay.id for pay in inv.payment_ids]
            currency = inv.currency_id
            company_currency = inv.company_id.currency_id
            if currency != company_currency:
                due = currency.compute(due, company_currency, round=False)
                bal = currency.compute(bal, company_currency, round=False)
                paid = currency.compute(paid, company_currency, round=False)
            age = (datetime.strptime(datetime.strftime(datetime.now(), '%Y-%m-%d'), '%Y-%m-%d') - datetime.strptime(
                inv.move_id.date, '%Y-%m-%d')).days
            result.append((0, 0, {
                'date': inv.move_id.date,
                'beta_ref': inv.number,
                'part_ref': inv.bt_po_ref or "/",
                'due': due,
                'paid': paid,
                'bal': bal,
                'age': age,
                'remark': inv.od_remarks[:20] if inv.od_remarks else "",
                'move_id': inv.move_id.id
            }))
        due_moves = self._mv_lines_get(partner_id, move_ids, payment_move_ids)
        for mvl in due_moves:
            age = (datetime.strptime(datetime.strftime(datetime.now(), '%Y-%m-%d'), '%Y-%m-%d') - datetime.strptime(
                mvl.move_id.date, '%Y-%m-%d')).days
            result.append((0, 0, {
                'date': mvl.date,
                'beta_ref': mvl.invoice.number,
                'part_ref': mvl.invoice.bt_po_ref or "/",
                'due': mvl.debit,
                'age': age,
                'paid': mvl.credit,
                'bal': mvl.debit - mvl.credit,
                'remark': mvl.invoice.od_remarks[:20] if mvl.invoice.od_remarks else "",
                'move_id': mvl.move_id.id

            }))
        return result

    @api.multi
    def new_print_directly(self):
        data = self.get_new_data()
        partner_id = self.partner_id.id
        rpt_pool = self.env['od.cust.statement.rpt.data']
        currency_id = self.partner_id.company_id.currency_id.id
        company_id = self.partner_id.company_id.id
        vals = {
            'name': "Customer Statement Report",
            'partner_id': partner_id,
            'line_ids': data,
            'currency_id': currency_id,
            'company_id': company_id,
        }
        bucket_vals = self.get_bucket_vals(partner_id)
        vals.update(bucket_vals)

        rpt = rpt_pool.create(vals)
        rpt_id = rpt.id
        ctx = self.env.context
        cr = self.env.cr
        uid = self.env.uid
        return self.pool['report'].get_action(cr, uid, [rpt_id], 'report.od_new_cust_statement', context=ctx)


class customer_statement_rpt_data(models.TransientModel):
    _inherit = 'od.cust.statement.rpt.data'

    company_id = fields.Many2one('res.company', string="Company")
