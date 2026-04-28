# -*- coding: utf-8 -*-
{
    "name" : "Orchid HRMS",
    "version" : "0.1",
    "author": "OrchidERP",
    "category" : "Accounting & Finance",
    "description": """OrchidERP for Payroll
        This module help you to know the basic Salary of the employee
        by giving the total of the month """,
    "website": ["http://www.orchiderp.com"],
    "depends": ['hr_evaluation','hr_contract','hr_payroll','hr_payroll_account','hr_timesheet_sheet','hr_holidays','product','hr_expense'],
    "data" : [
#'security/ir.model.access.csv',
                'hr_salary_rule_view.xml',
                'hr_payroll_view.xml',
                'od_hr_over_time_view.xml',
                'od_hr_loans_view.xml',
                'od_transaction_note_view.xml',
                'od_hr_over_time_seq.xml',
                'od_hr_duty_resumption_view.xml',
                'od_payroll_transactions_view.xml',
                'od_hr_duty_resumption_approval_view.xml',
                'od_final_settlement_view.xml',
                'od_final_settlement_type_master_view.xml',
                'od_mode_of_payment_view.xml',
                'hr_holidays_view.xml',
                'hr_employee_view.xml',
                'od_airfare_encashments_view.xml',
                'od_airfare_encashments_approval_view.xml',
#                'hr_payslip_view.xml',
                'hr_holidys_status_view.xml',
                'hr_public_holidays_view.xml',
                'report/salary_register.xml',
                'product_view.xml',
                'wizard/hr_payroll_payslips_by_employees_view.xml',
                'report/od_hrms_salary_sheet_view.xml',
                'report/od_payroll_transaction_analysis_view.xml'
                
            ],
    'css': ['static/src/css/hr.css'],
}
