from openerp import models, fields, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
import calendar

class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'
    
    def od_get_period_id(self, start_date, end_date):
        company_id = self.env.user.company_id.id
        period_id = self.env['account.period'].search([('company_id', '=', company_id), ('date_start', '=', start_date),('date_stop', '=', end_date)]).id
        return period_id
    
    def od_get_journal_id(self):
        company_id = self.env.user.company_id.id
        if company_id == 6:
            journal_id = 58
        if company_id == 1:
            journal_id = 21
        return journal_id
    
    @api.model
    def _cron_generate_batches_generate_payslips(self):
        print "x"*88
        payslip_employee_pool = self.env['hr.payslip.employees']
        today = datetime.today()
        start_date = datetime(today.year, today.month, 1)
        if today.month == 12:
            next_month = 1
            year = today.year + 1
        else:
            next_month = today.month + 1
            year = today.year
        next_month_start_day = datetime(year, next_month, 1)
        end_date = next_month_start_day - relativedelta(days=1)
        batch_name = 'Staff Salary for ' + calendar.month_name[today.month] + ' - ' + str(today.year)
        period_id = self.od_get_period_id(start_date, end_date)
        journal_id = self.od_get_journal_id()
        payslip_batch_vals = {
            'xo_period_id': period_id,
            'journal_id': journal_id,
            'name': batch_name
            }
        payslip_batch = self.create(payslip_batch_vals)
        employee_objs = self.env['hr.employee'].search([])
        employee_ids = []
        for employee in employee_objs:
            employee_ids.append(employee.id)
        ctx = dict(self.env.context) or {}
        ctx.update({
            'active_model': 'hr.payslip.run', 
            'journal_id': payslip_batch.journal_id and payslip_batch.journal_id.id,
            'active_ids': [payslip_batch.id],
            'active_id': payslip_batch.id
            })
        payslip_employee_obj = payslip_employee_pool.with_context(ctx).create({'employee_ids': [(6, 0, employee_ids)]})
        payslip_employee_obj.compute_sheet()
        
