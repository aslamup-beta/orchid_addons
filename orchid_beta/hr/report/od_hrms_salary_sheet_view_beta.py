# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import fields, osv
class od_hrms_salary_sheet_view_beta(osv.osv):
    _name = "od.hrms.salary.sheet.view.beta"
    _description = "od.hrms.salary.sheet.view.beta"
    _auto = False
    _rec_name = 'employee_id'
    _columns = {
        'employee_id':fields.many2one('hr.employee','Employee'),
        'address_id':fields.many2one('res.partner','Working Address'),
        'date_from':fields.date('Date From'),
        'date_to':fields.date('Date To'),
        'od_sponser_id':fields.many2one('hr.employee','Sponser'),
        'company_id':fields.many2one('res.company', 'Company', readonly=True),
        'od_cost_centre_id':fields.many2one('od.cost.centre','Cost Centre'),
        
#        'xo_total_wage':fields.float('Monthly Salary'),
        'daily_salary':fields.float('Daily Salary'),
        'net_salary':fields.float('Net Salary'),
        'loan_deduction':fields.float('Loan Deduction'),
        'period':fields.char('Period'),
        'cash':fields.float('Cash'),
        'period_id':fields.many2one('account.period','Account Period'),
        'xo_mode_of_payment_id':fields.many2one('od.mode.of.payment','Mode Of Payment'),
        'identification':fields.integer('Identification No'),
        'department_id':fields.many2one('hr.department','Department'),
        'basic':fields.float('Basic'),
        'house_allowance':fields.float('House Allowance'),
        'transport_allowance':fields.float('Transport Allowance'),
        'other_allowance':fields.float('Other Allowance'),
        'gross_salary':fields.float('Gross Salary'),
        'wps_beta_engineering':fields.float('WPS Beta Engineering'),
        'wps_beta_it':fields.float('WPS Beta IT'),
        'leave_deduction':fields.float('Leave Deduction'),
        'other_deduction':fields.float('Other Deduction'),
        'total_salary':fields.float('Total Salary'),
        'ot_allowance':fields.float('OT Allowance'),
        'other_payment':fields.float('Other Payment'),
        'days_in_month':fields.float('Days In Month'),
        'working_days':fields.float('Working Days'),
        'late_arival_deduction':fields.float('Late Arrival Deduction'),
        'leave_salary':fields.float('Leave Salary'),
        'unresume_ded':fields.float('Unresume Deduction'),
    }


    def _select(self):
        select_str = """
              SELECT ROW_NUMBER () OVER (ORDER BY hr_payslip.id ) AS id,
              hr_payslip.company_id as company_id,
             hr_payslip.employee_id AS employee_id,
             hr_employee.address_id as address_id,
            hr_employee.od_cost_centre_id,
            hr_employee.od_sponser_id,
             
             hr_payslip.date_from AS date_from,
             hr_payslip.date_to AS date_to,
             hr_employee.od_identification_no as identification,
             hr_employee.department_id as department_id,
             hr_contract.wage as basic,

(select allowance_rule_line.amt from allowance_rule_line where allowance_rule_line.contract_id = hr_contract.id and allowance_rule_line.code='HA') as house_allowance,

(select allowance_rule_line.amt from allowance_rule_line where allowance_rule_line.contract_id = hr_contract.id and allowance_rule_line.code='TA'                
) as transport_allowance,

(select allowance_rule_line.amt from allowance_rule_line where allowance_rule_line.contract_id = hr_contract.id and allowance_rule_line.code='OA'                
) AS other_allowance,
 (
        SELECT
                SUM (hr_payslip_line.total) AS SUM
        FROM
                hr_payslip_line
        WHERE
                (
                        (
                                hr_payslip_line.slip_id = hr_payslip. ID
                        )
                        AND (
                                hr_payslip_line.code in ('GRPI','GRBIT','GRBHO','BEINTR')
                        )
                )
) AS gross_salary,
 (
        SELECT
                SUM (hr_payslip_line.total)
        FROM
                hr_payslip_line
        WHERE                
                hr_payslip_line.slip_id = hr_payslip. ID
        AND 
                hr_payslip_line.code = 'LVSAL' 
) AS leave_salary,
  hr_payslip.xo_total_no_of_days as days_in_month,
        hr_payslip_worked_days.number_of_days as working_days,


        CASE
             WHEN 
        hr_payslip.xo_total_no_of_days > 0
          THEN        
                hr_contract.xo_total_wage / hr_payslip.xo_total_no_of_days        
             ELSE        
                hr_contract.xo_total_wage        
           END AS daily_salary, 

to_char(hr_payslip.date_from,
        'yyyy/mm'
) AS period,
 hr_payslip.xo_period_id AS period_id,
 hr_contract.xo_mode_of_payment_id,



(
        SELECT
                SUM (hr_payslip_line.total) 
        FROM
                hr_payslip_line
        WHERE                
                                hr_payslip_line.slip_id = hr_payslip. ID                        
        AND 
                          hr_payslip_line.code = 'OTHPAY' 
                        
                
) AS other_payment,
 (
        SELECT
                SUM (hr_payslip_line.total) 
        FROM
                hr_payslip_line
        WHERE                        
                                hr_payslip_line.slip_id = hr_payslip. ID
                AND 
                                hr_payslip_line.code = 'OTALW'                 
) AS ot_allowance,
 (
        SELECT
                SUM (hr_payslip_line.total) 
        FROM
                hr_payslip_line
        WHERE                        
                                hr_payslip_line.slip_id = hr_payslip. ID
                AND 
                                hr_payslip_line.code = 'TOT'                 
) AS total_salary,
(
        SELECT
             SUM (hr_payslip_line.total)
        FROM
                hr_payslip_line
        WHERE                        
                                hr_payslip_line.slip_id = hr_payslip. ID
                AND 
                                hr_payslip_line.code = 'UNRESUME'                 
) AS unresume_ded,
 (
        SELECT
                SUM (hr_payslip_line.total)
        FROM
                hr_payslip_line
        WHERE                
                                hr_payslip_line.slip_id = hr_payslip. ID
                AND 
                                hr_payslip_line.code= 'LOAN'
) AS loan_deduction,
(
        SELECT
                SUM (hr_payslip_line.total)
        FROM
                hr_payslip_line
        WHERE                        
                hr_payslip_line.slip_id = hr_payslip. ID
        AND 
                hr_payslip_line.code =  'LTARIV'
                      
) AS late_arival_deduction,
 (
        SELECT
                SUM (hr_payslip_line.total)
        FROM
                hr_payslip_line
        WHERE                        
                hr_payslip_line.slip_id = hr_payslip. ID
        AND 
                hr_payslip_line.code = 'OTHDED'                
) AS other_deduction,
 (
        SELECT
                SUM (hr_payslip_line.total)
        FROM
                hr_payslip_line
        WHERE                
                hr_payslip_line.slip_id = hr_payslip. ID
        AND 
                hr_payslip_line.code = 'LDED' 
) AS leave_deduction, 
 (
        SELECT
                SUM (hr_payslip_line.total)
        FROM
                hr_payslip_line
        WHERE        
                                hr_payslip_line.slip_id = hr_payslip. ID
                AND 
                hr_payslip_line.code= 'NET'
) AS net_salary,
 CASE
WHEN (
        hr_contract.xo_mode_of_payment_id = 1
) THEN
        (
                SELECT
                        SUM (hr_payslip_line.total)
                FROM
                        hr_payslip_line
                WHERE                                
                                        hr_payslip_line.slip_id = hr_payslip. ID
                AND 
                                        hr_payslip_line.code= 'NET'
        )
ELSE
        0
END AS cash,
 CASE
WHEN (
        hr_contract.xo_mode_of_payment_id = 2
) THEN
        (
                SELECT
                        SUM (hr_payslip_line.total)
                FROM
                        hr_payslip_line
                WHERE                        
                                        hr_payslip_line.slip_id = hr_payslip. ID
                        AND 
                                        hr_payslip_line.code = 'NET'                        
        )
ELSE
        0
END AS wps_beta_it,
 CASE
WHEN (
        hr_contract.xo_mode_of_payment_id = 3
) THEN
        (
                SELECT
                        SUM (hr_payslip_line.total)
                FROM
                        hr_payslip_line
                WHERE                        
                                        hr_payslip_line.slip_id = hr_payslip. ID
                AND 
                                        hr_payslip_line.code = 'NET'                        
        )
ELSE
        0
END AS wps_beta_engineering





             
        """
        return select_str
    def _from(self):
        from_str = """
                hr_payslip  

       
        """
        return from_str

    def _group_by(self):
        group_by_str = """
            GROUP BY         hr_payslip.ID,
        hr_payslip.employee_id,
        hr_payslip.date_from,
        hr_payslip.date_to,
        hr_contract.xo_total_wage,
        hr_contract.wage,
        hr_employee.od_cost_centre_id,
        hr_employee.od_sponser_id,
        hr_payslip.xo_total_no_of_days,
        hr_payslip_worked_days.number_of_days,
        hr_employee.address_id,
        hr_contract.xo_mode_of_payment_id,
        hr_payslip.xo_period_id,
        hr_employee.od_identification_no,
        hr_employee.department_id,
  hr_contract.id
                    
        """

  
        return group_by_str


    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM  %s 
  
                        JOIN hr_contract ON  hr_contract. ID = hr_payslip.contract_id                                
                        JOIN hr_employee ON  hr_employee. ID = hr_contract.employee_id                
                JOIN hr_payslip_worked_days 
            ON         hr_payslip_worked_days.payslip_id = hr_payslip. ID        AND 
                                                        hr_payslip_worked_days.code        = 'WORK100'  
  %s
            )""" % (self._table, self._select(), self._from(), self._group_by()))

























