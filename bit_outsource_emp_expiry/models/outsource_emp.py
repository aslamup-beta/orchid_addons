from openerp import models, fields, api, _
import datetime
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta


class OutsourceEmployee(models.Model):
    _inherit = 'outsource.employee'

    @api.model
    def run_outsource_emp_expiry_reminder_90_days(self):
        print("run_outsource_emp_expiry_reminder_90_days")
        template1 = self.env.ref(
            'bit_outsource_emp_expiry.email_template_customer_end_date_reminder_90',
            raise_if_not_found=False
        )
        template2 = self.env.ref(
            'bit_outsource_emp_expiry.email_template_employee_end_date_reminder_90',
            raise_if_not_found=False
        )
        template3 = self.env.ref(
            'bit_outsource_emp_expiry.email_template_customer_end_date_reminder_120',
            raise_if_not_found=False
        )
        template4 = self.env.ref(
            'bit_outsource_emp_expiry.email_template_employee_end_date_reminder_120',
            raise_if_not_found=False
        )
        # today = fields.Date.to_date(fields.Date.context_today(self))
        # target_date = today + timedelta(days=90)
        # print("target_date", target_date)
        today = datetime.date.today()
        domain = [
            ('active', '=', True), ('company_id', '=', 6)
        ]

        employees = self.search(domain)
        if employees:
            for emp in employees:
                if emp.end_date:
                    end_date = datetime.datetime.strptime(emp.end_date, '%Y-%m-%d').date()
                    end_date_bf_90_days = end_date - relativedelta(days=90)
                    if end_date_bf_90_days == today:
                        template1.send_mail(emp.id, force_send=True)
                    end_date_bf_120_days = end_date - relativedelta(days=120)
                    if end_date_bf_120_days == today:
                        template3.send_mail(emp.id, force_send=True)
                    employee_end_date = datetime.datetime.strptime(emp.employee_end_date, '%Y-%m-%d').date()
                    employee_end_date_90_days = employee_end_date - relativedelta(days=90)
                    if employee_end_date_90_days == today:
                        template2.send_mail(emp.id, force_send=True)
                    employee_end_date_120_days = employee_end_date - relativedelta(days=120)
                    if employee_end_date_120_days == today:
                        template4.send_mail(emp.id, force_send=True)
