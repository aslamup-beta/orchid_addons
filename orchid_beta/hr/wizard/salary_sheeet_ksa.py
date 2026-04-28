# -*- coding: utf-8 -*-


from openerp.osv import fields,osv
from openerp import tools


class ksa_salary_sheet_wiz(osv.osv_memory):
    _name ='ksa.salary.sheet.wiz'
    
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id
    _columns = {
         'company_id': fields.many2one('res.company','Company',required=True),
        'period_id':fields.many2one('account.period', string="Period",required=True),
     
        }
    _defaults ={
    'company_id': _get_default_company,
        }
    def export_rpt(self,cr,uid,ids,context=None):
        tools.sql.drop_view_if_exists(cr, 'od_hrms_salary_sheet_view_beta')
        company_id = self.browse(cr,uid,ids).company_id and self.browse(cr,uid,ids).company_id.id
        period_id =self.browse(cr,uid,ids).period_id and self.browse(cr,uid,ids).period_id.id
        where ="where hr_payslip.xo_period_id=%s"%period_id
        
        query = ''' 
        
        '''
        
       
        cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM  %s 
  
                        JOIN hr_contract ON  hr_contract. ID = hr_payslip.contract_id                                
                        JOIN hr_employee ON  hr_employee. ID = hr_contract.employee_id                
                JOIN hr_payslip_worked_days 
            ON         hr_payslip_worked_days.payslip_id = hr_payslip. ID        AND 
                                                        hr_payslip_worked_days.code        = 'WORK100'  
                                                        %s
  %s
            )""" % ('od_hrms_salary_sheet_view_beta', self._select(), self._from(),where, self._group_by()))
        
#         cr.execute(query)
        return {
            
            'name': 'KSA Salary Sheet Report',
            'view_type': 'form',
            'view_mode': 'tree,graph',
            'res_model': 'od.hrms.salary.sheet.view.beta',
            'type': 'ir.actions.act_window',
#             'context':{'search_default_brand':1,'search_default_po':1}
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

