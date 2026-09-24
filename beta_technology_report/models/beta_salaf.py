from openerp import models, fields, api, exceptions
from datetime import datetime
from dateutil.relativedelta import relativedelta
import calendar


class BetaLoanSalaf(models.Model):
    _inherit = 'beta.loan.salaf'

    installment_line_ids = fields.One2many(
        'beta.loan.salaf.installment', 'loan_id', string='Installments')

    @api.multi
    def action_generate_installments(self):
        self.ensure_one()
        Installment = self.env['beta.loan.salaf.installment']

        if not self.start_date:
            raise exceptions.Warning('Please set the Loan Start Date first.')
        if not self.repay_period:
            raise exceptions.Warning('Please set the Repayment Period first.')

        # wipe existing lines so the button can be used to regenerate
        if self.installment_line_ids:
            self.installment_line_ids.unlink()

        start = datetime.strptime(self.start_date, '%Y-%m-%d')
        # first instalment = last day of the month AFTER the start month
        current = start + relativedelta(months=1)

        for i in range(1, int(self.repay_period) + 1):
            last_day = calendar.monthrange(current.year, current.month)[1]
            inst_date = current.replace(day=last_day)
            Installment.create({
                'loan_id': self.id,
                's_no': i,
                'date': inst_date.strftime('%Y-%m-%d'),
                'amount': self.monthly_instalment,
                'paid': False,
            })
            current += relativedelta(months=1)

        return True


class BetaLoanSalafInstalment(models.Model):
    _name = 'beta.loan.salaf.installment'
    _order = 's_no'

    loan_id = fields.Many2one(
        'beta.loan.salaf', string='Loan', ondelete='cascade', required=True)
    s_no = fields.Integer(string='S.No')
    date = fields.Date(string='Date')
    amount = fields.Float(string='Amount')
    paid = fields.Boolean(string='Paid')