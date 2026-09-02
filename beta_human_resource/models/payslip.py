# -*- coding: utf-8 -*-
from openerp import api, fields, models


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    ot_salary = fields.Float(
        string='OT Salary',
        compute='_compute_salary_totals',
        store=True,
        digits=(16, 2),
        help="Sum of payslip lines whose salary rule category code is 'OT'.",
    )
    normal_salary = fields.Float(
        string='Normal Salary',
        compute='_compute_salary_totals',
        store=True,
        digits=(16, 2),
        help="Sum of payslip lines whose salary rule category code is 'OTHPAY'.",
    )
    leave_salary = fields.Float(
        string='Leave Salary',
        compute='_compute_salary_totals',
        store=True,
        digits=(16, 2),
        help="Sum of payslip lines whose salary rule category code is 'GROSS'.",
    )
    deduction = fields.Float(
        string='Deduction',
        compute='_compute_salary_totals',
        store=True,
        digits=(16, 2),
        help="Sum of payslip lines whose salary rule category code is 'OTHDED'.",
    )
    total_salary = fields.Float(
        string='Total Salary',
        compute='_compute_salary_totals',
        store=True,
        digits=(16, 2),
        help="normal_salary + leave_salary + ot_salary + deduction",
    )

    @api.multi
    @api.depends(
        'line_ids',
        'line_ids.total',
        'line_ids.category_id',
        'line_ids.category_id.code',
    )
    def _compute_salary_totals(self):
        # Map category code -> field name to accumulate into
        code_field_map = {
            'OT': 'ot_salary',
            'OTHPAY': 'normal_salary',
            'GROSS': 'leave_salary',
            'DED': 'deduction',
        }

        for payslip in self:
            totals = {field_name: 0.0 for field_name in code_field_map.values()}

            for line in payslip.line_ids:
                code = line.category_id.code
                field_name = code_field_map.get(code)
                if field_name:
                    totals[field_name] += line.total

            payslip.ot_salary = round(totals['ot_salary'])
            payslip.normal_salary = round(totals['normal_salary'])
            payslip.leave_salary = round(totals['leave_salary'])
            payslip.deduction = round(totals['deduction'])
            payslip.total_salary = round((
                totals['normal_salary']
                + totals['leave_salary']
                + totals['ot_salary']
                - totals['deduction']
            ))