# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import fields, osv
class od_hrms_provision_beta(osv.osv):
    _name = "od.hrms.provision.beta"
    _description = "od.hrms.provision.beta"
    _auto = False
    _rec_name = 'employee_id'
    _columns = {
        'employee_id':fields.many2one('hr.employee','Employee'),

        'address_id':fields.many2one('res.partner','Working Address'),

        'date_from':fields.date('Date From'),

        'date_to':fields.date('Date To'),

        'identification':fields.integer('Identification No'),

        'department_id':fields.many2one('hr.department','Department'),
        'gross_salary':fields.float('Gross Salary'),

        'basic':fields.float('Basic'),
        'days_in_month':fields.float('Days In Month'),
        'working_days':fields.float('Working Days'),
        'period':fields.char('Period'),
        'leave_provision':fields.float('Leave Provision'),
        'gratuvity_provision':fields.float('Gratuity Provision'),
        'other_allowance':fields.float('Other Allowance'),
        'total_gratuvity_provision':fields.float('Total Gratuity Provision'),
        'od_joining_date':fields.date('Joining Date'),
       



    }


    def _select(self):
        select_str = """
SELECT
        ROW_NUMBER () OVER (ORDER BY hr_payslip. ID) AS ID,
        hr_payslip.employee_id AS employee_id,
        hr_employee.address_id AS address_id,
        hr_payslip.date_from AS date_from,
        hr_payslip.date_to AS date_to,
        hr_employee.od_identification_no AS identification,
        hr_employee.od_joining_date,
        hr_employee.department_id AS department_id,
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
   allowance_rule_line.amt
  FROM
   allowance_rule_line
  WHERE
   (
    (
     allowance_rule_line.contract_id = hr_contract. ID
    )
    AND (
     (allowance_rule_line.code) :: TEXT = 'OA' :: TEXT
    )
   )
 ) AS other_allowance,
        hr_contract.wage AS basic,
        hr_payslip.xo_total_no_of_days AS days_in_month,
        hr_payslip_worked_days.number_of_days AS working_days,
        to_char(
                hr_payslip.date_from,
                'yyyy/mm'
        ) AS period,
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
     hr_payslip_line.code in ('LVEPROV','LVEPR')
    )
   )
 ) AS leave_provision,
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
     hr_payslip_line.code  in ('GRTPROV','GRTPR')
    )
   )
 ) AS gratuvity_provision,
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
     (hr_payslip_line.code) :: TEXT = 'TOTGRV' :: TEXT
    )
   )
 ) AS total_gratuvity_provision






             
        """
        return select_str
    def _from(self):
        from_str = """
                hr_payslip  

       
        """
        return from_str

    def _group_by(self):
        group_by_str = """
            GROUP BY  hr_payslip. ID,
        hr_payslip.employee_id,
        hr_payslip.date_from,
        hr_payslip.date_to,
        hr_contract.xo_total_wage,
        hr_contract.wage,
        hr_payslip.xo_total_no_of_days,
        hr_payslip_worked_days.number_of_days,
        hr_employee.address_id,
        hr_payslip.xo_period_id,
        hr_employee.od_identification_no,
        hr_employee.department_id,
        hr_employee.od_joining_date,
        hr_contract. ID
                    
        """

  
        return group_by_str


    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM  %s 
  
JOIN hr_contract ON hr_contract. ID = hr_payslip.contract_id
JOIN hr_employee ON hr_employee. ID = hr_contract.employee_id
JOIN hr_payslip_worked_days ON hr_payslip_worked_days.payslip_id = hr_payslip. ID
AND hr_payslip_worked_days.code = 'WORK100'
  %s
            )""" % (self._table, self._select(), self._from(), self._group_by()))

























