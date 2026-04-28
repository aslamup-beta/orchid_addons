# -*- coding: utf-8 -*-
import time
from openerp import models, fields, api
from pprint import pprint
from datetime import datetime, timedelta, date
import openerp.addons.decimal_precision as dp


class gratuity_rpt(models.TransientModel):
    _name = 'gratuity.rpt.wiz'

    emp_ids = fields.Many2many('hr.employee', string="Employee List")
    branch_ids = fields.Many2many('od.cost.branch', string="Branch")
    date = fields.Date(string="Gratuity Calculation Date")
    wiz_line = fields.One2many('gratuity.rpt.data.line', 'org_wiz_id', string="Wiz Line")

    def od_get_company_id(self):
        return self.env.user.company_id

    company_id = fields.Many2one('res.company', string='Company', default=od_get_company_id)

    def days_between(self, d1, d2):
        d1 = datetime.strptime(d1, "%Y-%m-%d")
        d2 = datetime.strptime(d2, "%Y-%m-%d")
        return abs((d2 - d1).days) + 1

    def od_get_basic_salary(self, emp_id):
        contract_ob = self._get_contract_obj(emp_id)
        basic_salary = contract_ob.wage
        return basic_salary

    def od_get_total_salary(self, emp_id):
        res = self.env['hr.contract'].search([('od_active', '=', True), ('employee_id', '=', emp_id.id)], limit=1)
        total = 0
        salary = 0
        company_id = self.env.user.company_id.id
        # if company_id == 6:
        total = res.xo_total_wage
        kpi = 0
        if res.xo_allowance_rule_line_ids:
            for rule in res.xo_allowance_rule_line_ids:
                if rule.code == 'KPI':
                    kpi = rule.amt
        salary = total - kpi
        # if company_id == 1:
        #     salary = res.wage
        return salary

    def _compute_unpaid_leaves(self, emp_id):
        last_day = self.date or False
        if last_day:
            joining_date = emp_id.od_joining_date
            days = 0.0
            leaves = self.env['hr.holidays'].search(
                [('od_start', '>', joining_date), ('od_end', '<', last_day), ('holiday_status_id', '=', 4),
                 ('employee_id', '=', emp_id.id), ('state', 'not in', ('draft', 'cancel', 'refuse'))])
            for obj in leaves:
                days += obj.od_number_of_days
            if days:
                return days

    def _compute_years(self, emp_id):
        total_days_in_a_year = 365.0
        if self.company_id.id == 6:
            total_days_in_a_year = 365.2425
        last_day = self.date
        if last_day:
            joining_date = emp_id.od_joining_date
            last_day = self.date
            if joining_date and last_day:
                days = self.days_between(joining_date, last_day)
                years = days / total_days_in_a_year
                return years

    def _compute_days(self, emp_id):
        last_day = self.date
        if last_day:
            joining_date = emp_id.od_joining_date
            last_day = self.date
            if joining_date and last_day:
                days = self.days_between(joining_date, last_day)
                return days

    def _compute_final_years(self, emp_id):
        total_days_in_a_year = 365.0
        if self.company_id.id == 6:
            total_days_in_a_year = 365.2425
        unpaid_days = self._compute_unpaid_leaves(emp_id) or False
        unpaid_in_years = unpaid_days / total_days_in_a_year
        years_of_service = self._compute_years(emp_id)
        years = years_of_service - unpaid_in_years
        return years

    def _compute_total_days(self, emp_id):
        unpaid_days = self._compute_unpaid_leaves(emp_id) or False
        years_of_service_in_days = self._compute_days(emp_id)
        total_days = years_of_service_in_days - unpaid_days
        return total_days

    def _get_contract_obj(self, emp_id):
        employee_id = emp_id and emp_id.id or False
        res = self.env['hr.contract'].search([('od_active', '=', True), ('employee_id', '=', employee_id)], limit=1)
        if emp_id and emp_id.active == False:
            res = self.env['hr.contract'].search([('employee_id', '=', employee_id)], order='id desc')[0]
        return res

    def od_get_accumulated_bal_of_grat(self, emp_id):
        company_id = self.env.user.company_id.id
        res = 0.0
        if company_id == 6:
            monthly_salary = self.od_get_total_salary(emp_id)
            service = self._compute_final_years(emp_id)
            res = 0.0
            if service < 5:
                res = (monthly_salary / 2.0) * service
            if service >= 5:
                up_to_5 = (monthly_salary / 2.0) * 5.0
                after_5_service = service - 5.0
                after_5 = monthly_salary * after_5_service
                res = up_to_5 + after_5
        if company_id == 1:
            contract_ob = self._get_contract_obj(emp_id)
            basic_salary = contract_ob.wage
            day_wage = (basic_salary / 30.0)
            service = self._compute_final_years(emp_id)
            service_days = self._compute_total_days(emp_id)
            print("service_days", service_days)
            service = round(service, 2)
            res = 0.0
            if service < 5:
                res = 21 * (service_days / 365.0) * day_wage
            if service >= 5:
                up_to_5 = 21 * day_wage * (1825 / 365.0)
                # after_5_service = service - 5.0
                after_5_service = service_days - 1825
                after_5_grat = 30.0 * day_wage * (after_5_service / 365.0)
                res = up_to_5 + after_5_grat
        return res

    def od_get_accumulated_bal_of_last_month(self, emp_id):
        company_id = self.env.user.company_id.id
        res = 0.0
        if company_id == 6:
            monthly_salary = self.od_get_total_salary(emp_id)
            service = self._compute_final_years_last_month(emp_id)
            res = 0.0
            if service < 5:
                res = (monthly_salary / 2.0) * service
            if service >= 5:
                up_to_5 = (monthly_salary / 2.0) * 5.0
                after_5_service = service - 5.0
                after_5 = monthly_salary * after_5_service
                res = up_to_5 + after_5
        if company_id == 1:
            contract_ob = self._get_contract_obj(emp_id)
            basic_salary = contract_ob.wage
            day_wage = (basic_salary / 30.0)
            service = self._compute_final_years_last_month(emp_id)
            service_days = self._compute_total_days_last_month(emp_id)
            service = round(service, 2)
            res = 0.0
            if service < 5:
                res = 21 * (service_days / 365.0) * day_wage
            if service >= 5:
                up_to_5 = 21 * day_wage * (1825 / 365.0)
                # after_5_service = service - 5.0
                after_5_service = service_days - 1825
                after_5_grat = 30.0 * day_wage * (after_5_service / 365.0)
                res = up_to_5 + after_5_grat
        return res

    def _compute_unpaid_leaves_last_month(self, emp_id):
        last_day = self.date or False
        last_day = datetime.strptime(self.date, "%Y-%m-%d")
        # today = datetime.date.today()
        first = last_day.replace(day=1)
        last_month = first - timedelta(days=1)
        last_month = last_month.strftime("%Y-%m-%d")
        print("last_month", last_month)

        # jjj
        if last_day:
            joining_date = emp_id.od_joining_date
            days = 0.0
            leaves = self.env['hr.holidays'].search(
                [('od_start', '>', joining_date), ('od_end', '<', last_month), ('holiday_status_id', '=', 4),
                 ('employee_id', '=', emp_id.id), ('state', 'not in', ('draft', 'cancel', 'refuse'))])
            for obj in leaves:
                days += obj.od_number_of_days
            if days:
                return days

    def _compute_years_last_month(self, emp_id):
        total_days_in_a_year = 365.0
        if self.company_id.id == 6:
            total_days_in_a_year = 365.2425
        last_day = self.date
        last_day = self.date or False
        last_day = datetime.strptime(self.date, "%Y-%m-%d")
        # today = datetime.date.today()
        first = last_day.replace(day=1)
        last_month = first - timedelta(days=1)
        print(last_month.strftime("%Y-%m-%d"))
        if last_month:
            joining_date = emp_id.od_joining_date
            last_day = last_month.strftime("%Y-%m-%d")
            if joining_date and last_day:
                days = self.days_between(joining_date, last_day)
                years = days / total_days_in_a_year
                return years

    def _compute_days_last_month(self, emp_id):
        last_day = self.date
        last_day = self.date or False
        last_day = datetime.strptime(self.date, "%Y-%m-%d")
        # today = datetime.date.today()
        first = last_day.replace(day=1)
        last_month = first - timedelta(days=1)
        print(last_month.strftime("%Y-%m-%d"))
        if last_month:
            joining_date = emp_id.od_joining_date
            last_day = last_month.strftime("%Y-%m-%d")
            if joining_date and last_day:
                days = self.days_between(joining_date, last_day)
                return days

    def _compute_final_years_last_month(self, emp_id):
        total_days_in_a_year = 365.0
        if self.company_id.id == 6:
            total_days_in_a_year = 365.2425
        unpaid_days = self._compute_unpaid_leaves_last_month(emp_id) or False
        unpaid_in_years = unpaid_days / total_days_in_a_year
        years_of_service = self._compute_years_last_month(emp_id)
        years = years_of_service - unpaid_in_years
        return years

    def _compute_total_days_last_month(self, emp_id):
        unpaid_days = self._compute_unpaid_leaves_last_month(emp_id) or False
        years_of_service_in_days = self._compute_days_last_month(emp_id)
        total_days = years_of_service_in_days - unpaid_days
        return total_days

    def _get_employee_list(self):
        emp_list = []
        emp_obj = self.env['hr.employee']
        emp_ids = [pr.id for pr in self.emp_ids]
        branch_obj = self.env['od.cost.branch']
        branch_ids = [branch.id for branch in self.branch_ids]
        company_id = self.env.user.company_id.id
        domain = [('company_id', '=', company_id), ('active', '=', True), ('od_joining_date', '<=', self.date),
                  ('country_id', '!=', 2)]
        if emp_ids:
            domain += [('id', 'in', emp_ids)]
        if branch_ids:
            domain += [('od_branch_id', 'in', branch_ids)]
        active_amp_list = emp_obj.search(domain, order='od_identification_no')
        non_active_domain = [('company_id', '=', company_id), ('active', '=', False),
                             ('od_joining_date', '<=', self.date),
                             ('country_id', '!=', 2), ('od_last_day', '!=', False),
                             ('od_last_day', '!=', None),('od_last_day', '>=', self.date)]
        non_active_amp_list = emp_obj.search(non_active_domain, order='od_identification_no')
        emp_list = active_amp_list + non_active_amp_list
        return emp_list


    def is_same_year(self, date1, date2):
        """
        Check if two dates are in the same year
        :param date1: First date string in 'YYYY-MM-DD' format
        :param date2: Second date string in 'YYYY-MM-DD' format
        :return: True if same year, False otherwise
        """
        if not date1 or not date2:
            return False

        # Parse dates
        date1_obj = datetime.strptime(date1, '%Y-%m-%d')
        date2_obj = datetime.strptime(date2, '%Y-%m-%d')

        # Compare years
        return date1_obj.year == date2_obj.year


    def od_get_leave_days(self, emp_id):
        joining_day = emp_id.od_joining_date or False
        leave_days = 0
        total_days_in_a_year = 365.0
        if self.company_id.id == 6:
            total_days_in_a_year = 365.2425
        last_day = self.date
        last_day = self.date or False
        same_year = self.is_same_year(joining_day, last_day)
        last_day = datetime.strptime(self.date, "%Y-%m-%d")
        joining_date = datetime.strptime(joining_day, "%Y-%m-%d")
        month = 1
        eligible_leaves = 0
        if same_year:
            month = month + (last_day.month - joining_date.month)
            eligible_leaves = 2.5 * month
        else:
            eligible_leaves = 2.5 * last_day.month

        current_year = last_day.year
        start_date = date(current_year, 1, 1)
        end_date = date(current_year, 12, 31)
        start_date = start_date.strftime("%Y-%m-%d")
        end_date = end_date.strftime("%Y-%m-%d")
        leaves = self.env['hr.holidays'].search(
            [('od_start', '>=', start_date), ('od_end', '<=', end_date), ('holiday_status_id', 'in', (1,12)),
             ('employee_id', '=', emp_id.id), ('state', 'not in', ('draft', 'cancel', 'refuse'))])
        leave_taken = 0
        for leave in leaves:
            leave_taken = leave_taken + leave.od_number_of_days
        leave_days = eligible_leaves - leave_taken
        if current_year == 2025:
            if emp_id.id in [764, 763]:
                leave_days = leave_days + 19.07
            if emp_id.id == 765:
                leave_days = leave_days + 19.64
            if emp_id.id == 768:
                leave_days = leave_days + 17.34
            if emp_id.id == 773:
                leave_days = leave_days + 14.88
            if emp_id.id == 782:
                leave_days = leave_days + 11.01
            if emp_id.id == 784:
                leave_days = leave_days + 9.29
            if emp_id.id == 788:
                leave_days = leave_days + 8.63
            if emp_id.id == 789:
                leave_days = leave_days + 8.38
            if emp_id.id == 479:
                leave_days = leave_days + 6.41
            if emp_id.id == 795:
                leave_days = leave_days + 2.22
        return leave_days

    def od_get_gratuity_days(self, emp_id):
        print("od_get_gratuity_days")
        company_id = self.env.user.company_id.id
        res = 0.0
        if company_id == 1:
            service = self._compute_final_years(emp_id)
            service = round(service, 2)
            res = 0.0
            if service < 5:
                res = 21 * service
            if service >= 5:
                up_to_5 = 21 * 5
                after_5_service = service - 5.0
                after_5_grat = 30.0 * after_5_service
                res = up_to_5 + after_5_grat
        return res

    def get_detailed_data(self):
        result = []
        ctx = self.env.context
        cr = self.env.cr
        uid = self.env.uid
        emp_list = self._get_employee_list()
        for emp in emp_list:
            bal = self.od_get_accumulated_bal_of_grat(emp)
            # prec = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
            # bal = round(bal, prec)
            bal_last_month = self.od_get_accumulated_bal_of_last_month(emp)
            result.append((0, 0, {
                'emp_name': emp.name,
                'join_date': emp.od_joining_date,
                'staff_id': emp.od_identification_no,
                'od_cost_centre_id': emp.od_cost_centre_id.id,
                'bal': round(bal),
                'this_month_bal': round(bal - bal_last_month),
                'total_salary': self.od_get_total_salary(emp),
                'leave_days': self.od_get_leave_days(emp),
                'gratuity_days': self.od_get_gratuity_days(emp),
                'basic_salary': self.od_get_basic_salary(emp),
            }))
        return result

    @api.multi
    def print_directly(self):
        data = self.get_detailed_data()
        rpt_temp = 'report.od_gratuity_rpt'
        rpt_pool = self.env['gratuity.rpt.data']
        currency_id = self.env.user.company_id.currency_id.id
        vals = {
            'name': "Gratuity Report",
            'line_ids': data,
            'date': self.date,
            'currency_id': currency_id,
            'company_id': self.env.user.company_id.id,
        }
        rpt = rpt_pool.create(vals)
        rpt_id = rpt.id
        ctx = self.env.context
        cr = self.env.cr
        uid = self.env.uid
        return self.pool['report'].get_action(cr, uid, [rpt_id], rpt_temp, context=ctx)

    @api.multi
    def export_rpt(self):
        model_data = self.env['ir.model.data']
        result = self.get_detailed_data()
        vw = 'tree_view_gratuity_rpt'
        tree_view = model_data.get_object_reference('beta_customisation', vw)
        self.wiz_line.unlink()
        self.write({'wiz_line': result})
        del (result)
        return {
            'domain': [('org_wiz_id', '=', self.id)],
            'name': 'Gratuity Report',
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(tree_view and tree_view[1] or False, 'tree')],
            'res_model': 'gratuity.rpt.data.line',
            'type': 'ir.actions.act_window',
        }


class gratuity_rpt_data(models.TransientModel):
    _name = 'gratuity.rpt.data'

    def _get_today_date(self):
        return datetime.today().strftime('%d-%b-%y')

    line_ids = fields.One2many('gratuity.rpt.data.line', 'wiz_id', string="Wiz Line", readonly=True)
    date = fields.Date(string="Gratuity Calculation Date")
    date_today = fields.Date(default=_get_today_date)
    currency_id = fields.Many2one('res.currency', string='Currency')

    def od_get_company_id(self):
        return self.env.user.company_id

    company_id = fields.Many2one('res.company', string='Company', default=od_get_company_id)


class gratuity_rpt_data_line(models.TransientModel):
    _name = 'gratuity.rpt.data.line'

    def od_get_company_id(self):
        return self.env.user.company_id

    company_id = fields.Many2one('res.company', string='Company', default=od_get_company_id)

    wiz_id = fields.Many2one('gratuity.rpt.data', string="Wizard data")
    org_wiz_id = fields.Many2one('gratuity.rpt.wiz', string="Wizard")
    od_cost_centre_id = fields.Many2one('od.cost.centre', string="Department")
    emp_name = fields.Char(string="Employee Name")
    join_date = fields.Date(string='Joining Date')
    leave_days = fields.Float(string="Leave Days", digits=(16, 2))
    gratuity_days = fields.Float(string="Gratuity Days", digits=(16, 2))
    total_salary = fields.Float(string="Total Salary", digits=(16, 2))
    basic_salary = fields.Float(string="Basic Salary", digits=(16, 2))
    bal = fields.Float(string="Accumulated balance for Gratuity", digits=(16, 2))
    this_month_bal = fields.Float(string="This Month", digits=(16, 2))
    staff_id = fields.Integer(string="Staff ID")
