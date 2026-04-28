# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from datetime import datetime


class hr_employee(models.Model):
    _inherit = "hr.employee"

    @api.one
    @api.depends('name')
    def _compute_document_count2(self):
        employee_id = self.id
        doc_ids = []
        current_year = datetime.now().year
        document_ids = self.env['od.document.request'].search(
            [('employee_id', '=', employee_id), ('is_issued', '=', False), ('state', '!=', 'refused')])
        for obj in document_ids:
            if obj.od_year == current_year:
                doc_ids.append(obj.id)
        if doc_ids:
            self.od_document_count2 = len(doc_ids)

    def od_action_open_document_request(self, cr, uid, ids, context=None):
        data = self.browse(cr, uid, ids)
        employee_id = data and data.id
        model_data = self.pool.get('ir.model.data')
        tree_view = model_data.get_object_reference(cr, uid, 'orchid_beta', 'od_document_request_approval_beta_tree')
        form_view = model_data.get_object_reference(cr, uid, 'orchid_beta', 'od_document_request_approval_beta_form')
        doc_ids = []
        current_year = datetime.now().year
        doc_pool = self.pool.get('od.document.request')
        document_ids = doc_pool.search(cr, uid, [('employee_id', '=', employee_id)])
        for obj in doc_pool.browse(cr, uid, document_ids):
            if obj.od_year == current_year:
                doc_ids.append(obj.id)
        domain = [('id', 'in', doc_ids)]
        res = {
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'views': [(tree_view and tree_view[1] or False, 'tree'), (form_view and form_view[1] or False, 'form')],
            'view_type': 'form',
            'res_model': 'od.document.request',
            'domain': domain,
            'context': {'default_employee_id': employee_id}
        }

        return res

    @api.one
    def od_comp_short_leave(self):
        holidays_pool = self.env['hr.holidays']
        employee_id = self.id
        current_year = datetime.now().year
        base_dom = [('employee_id', '=', employee_id), ('od_year', '=', current_year), ('holiday_status_id', '=', 5),
                    ('state', 'not in', ('draft', 'confirm', 'cancel', 'refuse', 'validate1'))]
        holidays = holidays_pool.search(base_dom)
        short_leaves = 0.0
        for holiday in holidays:
            short_leaves += holiday.od_hour
        self.od_short_leave = short_leaves

    @api.multi
    def od_btn_open_short_leaves(self):
        holidays_pool = self.env['hr.holidays']
        employee_id = self.id
        current_year = datetime.now().year
        base_dom = [('employee_id', '=', employee_id), ('od_year', '=', current_year), ('holiday_status_id', '=', 5)]
        holidays = holidays_pool.search(base_dom)
        holiday_ids = [holi.id for holi in holidays]
        domain = [('id', 'in', holiday_ids)]
        ctx = {'default_employee_id': employee_id, 'default_holiday_status_id': 5, }
        return {
            'domain': domain,
            'context': ctx,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'hr.holidays',
            'type': 'ir.actions.act_window',
        }

    @api.one
    def od_comp_legal_leave(self):
        holidays_pool = self.env['hr.holidays']
        employee_id = self.id
        current_year = datetime.now().year
        base_dom = [('employee_id', '=', employee_id), ('od_year', '=', current_year), ('holiday_status_id', '=', 1),
                    ('state', 'not in', ('draft', 'confirm', 'cancel', 'refuse', 'validate1'))]
        holidays = holidays_pool.search(base_dom)
        leaves = 0.0
        for holiday in holidays:
            leaves += abs(holiday.number_of_days)
        self.od_legal_leave = leaves

    @api.multi
    def od_btn_open_legal_leaves(self):
        holidays_pool = self.env['hr.holidays']
        employee_id = self.id
        current_year = datetime.now().year
        base_dom = [('employee_id', '=', employee_id), ('od_year', '=', current_year), ('holiday_status_id', '=', 1)]
        holidays = holidays_pool.search(base_dom)
        holiday_ids = [holi.id for holi in holidays]
        domain = [('id', 'in', holiday_ids)]
        ctx = {'default_employee_id': employee_id, 'default_holiday_status_id': 1, }
        return {
            'domain': domain,
            'context': ctx,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'hr.holidays',
            'type': 'ir.actions.act_window',
        }

    @api.one
    def od_comp_sick_leave(self):
        holidays_pool = self.env['hr.holidays']
        employee_id = self.id
        current_year = datetime.now().year
        base_dom = [('employee_id', '=', employee_id), ('od_year', '=', current_year), ('holiday_status_id', '=', 2),
                    ('state', 'not in', ('draft', 'confirm', 'cancel', 'refuse', 'validate1'))]
        holidays = holidays_pool.search(base_dom)
        leaves = 0.0
        for holiday in holidays:
            leaves += abs(holiday.number_of_days)
        self.od_sick_leave = leaves

    @api.multi
    def od_btn_open_sick_leaves(self):
        holidays_pool = self.env['hr.holidays']
        employee_id = self.id
        current_year = datetime.now().year
        base_dom = [('employee_id', '=', employee_id), ('od_year', '=', current_year), ('holiday_status_id', '=', 2)]
        holidays = holidays_pool.search(base_dom)
        holiday_ids = [holi.id for holi in holidays]
        domain = [('id', 'in', holiday_ids)]
        ctx = {'default_employee_id': employee_id, 'default_holiday_status_id': 2, }
        return {
            'domain': domain,
            'context': ctx,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'hr.holidays',
            'type': 'ir.actions.act_window',
        }

    @api.one
    def od_comp_unpaid_leave(self):
        holidays_pool = self.env['hr.holidays']
        employee_id = self.id
        current_year = datetime.now().year
        base_dom = [('employee_id', '=', employee_id), ('od_year', '=', current_year), ('holiday_status_id', '=', 4),
                    ('state', 'not in', ('draft', 'confirm', 'cancel', 'refuse', 'validate1'))]
        holidays = holidays_pool.search(base_dom)
        leaves = 0.0
        for holiday in holidays:
            leaves += abs(holiday.number_of_days)
        self.od_unpaid_leave = leaves

    @api.multi
    def od_btn_open_unpaid_leaves(self):
        holidays_pool = self.env['hr.holidays']
        employee_id = self.id
        current_year = datetime.now().year
        base_dom = [('employee_id', '=', employee_id), ('od_year', '=', current_year), ('holiday_status_id', '=', 4)]
        holidays = holidays_pool.search(base_dom)
        holiday_ids = [holi.id for holi in holidays]
        domain = [('id', 'in', holiday_ids)]
        ctx = {'default_employee_id': employee_id, 'default_holiday_status_id': 4, }
        return {
            'domain': domain,
            'context': ctx,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'hr.holidays',
            'type': 'ir.actions.act_window',
        }

    @api.one
    def od_compute_claim_amount(self):
        hr_exp_pool = self.env['hr.expense.expense']
        employee_id = self.id
        expense_pool = self.env['hr.expense.expense']
        expenses = expense_pool.search([('employee_id', '=', employee_id), ('state', 'in', ('accepted', 'done'))])
        amount = sum([exp.amount for exp in expenses if exp.od_payment_status != 'paid'])
        self.od_exp_claim_amount = amount
        # cr = self.env.cr
        # query = """
        #     select sum(amount)
        #     from hr_expense_expense where employee_id = %s and state = 'accepted' and od_payment_status != 'paid_fully'
        #  """
        # cr.execute(query,tuple(emp_ids))
        # amount =cr.fetchall()

    @api.multi
    def od_btn_open_expense_claim(self):

        employee_id = self.id
        expense_pool = self.env['hr.expense.expense']
        expenses = expense_pool.search([('employee_id', '=', employee_id)])
        exp_ids = []
        current_year = datetime.now().year
        for exp in expenses:
            if exp.od_year == current_year:
                exp_ids.append(exp.id)
        domain = [('id', 'in', exp_ids)]
        ctx = {'default_employee_id': employee_id}
        return {
            'domain': domain,
            'context': ctx,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'hr.expense.expense',
            'type': 'ir.actions.act_window',
        }

    od_exp_claim_amount = fields.Float(string="Expense Claim", compute="od_compute_claim_amount")
    od_document_count2 = fields.Float(string='Count', compute='_compute_document_count2')
    od_short_leave = fields.Float(string="Short Leaves", compute="od_comp_short_leave")
    od_legal_leave = fields.Float(string="Legal Leaves", compute="od_comp_legal_leave")
    od_unpaid_leave = fields.Float(string="Unpaid Leaves", compute="od_comp_unpaid_leave")
    od_sick_leave = fields.Float(string="Sick Leaves", compute="od_comp_sick_leave")


class HrContract(models.Model):
    _inherit = "hr.contract"

    od_allowance = fields.Float(string="Allowances", compute="_compute_od_allowance", strore=True,default=0.0)
    xo_total_wage = fields.Float(string="Total", compute="_compute_xo_total_wage", strore=True, default=0.0)

    @api.depends('xo_allowance_rule_line_ids', 'xo_allowance_rule_line_ids.amt')
    def _compute_od_allowance(self):
        total_allowance_amt = 0
        for rec in self:
            if rec.xo_allowance_rule_line_ids:
                total_allowance_amt = sum([line.amt for line in rec.xo_allowance_rule_line_ids])
            rec.od_allowance = total_allowance_amt

    @api.depends('od_allowance', 'wage','xo_allowance_rule_line_ids')
    def _compute_xo_total_wage(self):
        for rec in self:
            od_allowance = rec.od_allowance or 0.0
            wage = rec.wage or 0.0
            rec.xo_total_wage = od_allowance + wage
