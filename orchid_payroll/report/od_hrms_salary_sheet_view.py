# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import fields, osv
class od_hrms_salary_sheet_view(osv.osv):
    _name = "od.hrms.salary.sheet.view"
    _description = "od.hrms.salary.sheet.view"
    _auto = False
    _rec_name = 'employee_id'
    _columns = {
        'employee_id':fields.many2one('hr.employee','Employee'),
        'date_from':fields.date('Date From'),
        'date_to':fields.date('Date To'),
        'xo_total_wage':fields.float('Monthly Salary'),
        'daily_salary':fields.float('Daily Salary'),
        'number_of_days':fields.integer('Number Of Days'),
        'gross':fields.float('Gross'),
        'allowance':fields.float('Allowance'),
        'net_salary':fields.float('Net Salary'),
        'loan':fields.float('Loan'),
        'arrears':fields.float('Arrears'),
        'advance_salary':fields.float('Advance Salary'),
        'advance_salary_deduction':fields.float('Advance Salary Deduction'),
        'personal_expence_deduction':fields.float('Personal Expence Deduction'),
        'blackberry':fields.float('Blackberry'),
        'cost_center':fields.char('Cost Center'),
        'period':fields.char('Period'),
        'wps_obs':fields.float('WPS_OBS'),
        'wps_auto':fields.float('WPS_Auto'),
        'wps_kartell':fields.float('WPS_Kartell'),
        'cash':fields.float('Cash'),
        'telegraphic_transfer':fields.float('Telegraphic Transfer'),
        'period_id':fields.many2one('account.period','Account Period'),
        'xo_mode_of_payment_id':fields.many2one('od.mode.of.payment','Mode Of Payment'),
        'identification':fields.integer('Identification No'),
        'department_id':fields.many2one('hr.department'),
        
        
    }


    def _select(self):
        select_str = """
              SELECT ROW_NUMBER () OVER (ORDER BY hr_payslip.id ) AS id,
             hr_payslip.employee_id AS employee_id,
             hr_payslip.date_from AS date_from,
             hr_payslip.date_to AS date_to,
             hr_employee.od_identification_no as identification,
             hr_employee.department_id as department_id,
             hr_contract.xo_total_wage as xo_total_wage,
             CASE
                WHEN hr_payslip.xo_total_no_of_days > 0 THEN
                    (hr_contract.xo_total_wage/hr_payslip.xo_total_no_of_days)
               ELSE
                    (hr_contract.xo_total_wage/1)
               END 
                    AS daily_salary,
             hr_payslip_worked_days.number_of_days as number_of_days,
             (select name from account_analytic_account where account_analytic_account.id=hr_contract.analytic_account_id) as cost_center,
             to_char(date_from,'yyyy/mm') as period,
            hr_payslip.xo_period_id as period_id,
            hr_contract.xo_mode_of_payment_id as xo_mode_of_payment_id,
(select sum (total) from hr_payslip_line where hr_payslip_line.slip_id=hr_payslip.id and code = 'GROSS') as gross,
(select sum (total) from hr_payslip_line where hr_payslip_line.slip_id=hr_payslip.id and code = 'SPALLOW') as allowance,
(select sum (total) from hr_payslip_line where hr_payslip_line.slip_id=hr_payslip.id and code = 'NET') as net_salary,
(select sum (total) from hr_payslip_line where hr_payslip_line.slip_id=hr_payslip.id and code = 'LOAN') as loan,
(select sum (total) from hr_payslip_line where hr_payslip_line.slip_id=hr_payslip.id and code = 'ARR') as arrears,
(select sum (total) from hr_payslip_line where hr_payslip_line.slip_id=hr_payslip.id and code = 'ADVSAL') as advance_salary,
(select sum (total) from hr_payslip_line where hr_payslip_line.slip_id=hr_payslip.id and code = 'ADVSALDED') as Advance_Salary_Deduction,
(select sum (total) from hr_payslip_line where hr_payslip_line.slip_id=hr_payslip.id and code = 'PEREXPDED') as Personal_Expence_Deduction,
(select sum (total) from hr_payslip_line where hr_payslip_line.slip_id=hr_payslip.id and code = 'BBERY') as Blackberry,
case when  hr_contract.xo_mode_of_payment_id= 1 then
  (select sum (total) from hr_payslip_line where hr_payslip_line.slip_id=hr_payslip.id and code = 'NET') 
else 0 end as WPS_OBS,
case when hr_contract.xo_mode_of_payment_id= 2 then
  (select sum (total) from hr_payslip_line where hr_payslip_line.slip_id=hr_payslip.id and code = 'NET') 
else 0 end as WPS_Auto,
case when hr_contract.xo_mode_of_payment_id= 3 then
  (select sum (total) from hr_payslip_line where hr_payslip_line.slip_id=hr_payslip.id and code = 'NET') 
else 0 end as WPS_Kartell,
case when hr_contract.xo_mode_of_payment_id= 4 then
  (select sum (total) from hr_payslip_line where hr_payslip_line.slip_id=hr_payslip.id and code = 'NET') 
else 0 end as Telegraphic_Transfer,
case when hr_contract.xo_mode_of_payment_id= 5 then
  (select sum (total) from hr_payslip_line where hr_payslip_line.slip_id=hr_payslip.id and code = 'NET') 
else 0 end as Cash 
             
        """
        return select_str
    def _from(self):
        from_str = """
                hr_payslip  
        """
        return from_str

    def _group_by(self):
        group_by_str = """
            GROUP BY hr_payslip.id,
                    hr_payslip.employee_id,
                   hr_payslip.date_from,
                    hr_payslip.date_to,
                    hr_contract.xo_total_wage,
                    hr_payslip.xo_total_no_of_days,
                    hr_payslip_worked_days.number_of_days,
                    hr_contract.analytic_account_id,
                    hr_contract.xo_mode_of_payment_id,
                    hr_payslip.xo_period_id,
                    hr_employee.od_identification_no,
                    hr_employee.department_id
                    
        """
        return group_by_str


    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM  %s 
join hr_contract on hr_contract.id=hr_payslip.contract_id
join hr_employee on hr_employee.id = hr_contract.employee_id 
join hr_payslip_worked_days on hr_payslip_worked_days.payslip_id =hr_payslip.id and hr_payslip_worked_days.code = 'WORK100'
  %s
            )""" % (self._table, self._select(), self._from(), self._group_by()))


