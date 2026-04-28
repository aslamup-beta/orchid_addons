# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import fields, osv
class od_overtime_analysis_beta(osv.osv):
    _name = "od.overtime.analysis.beta"
    _description = "od.overtime.analysis.beta"
    _auto = False
    _rec_name = 'employee_id'
    _columns = {
        'employee_id':fields.many2one('hr.employee','Employee'),
        'hour':fields.float('Hour'),
        'period_id':fields.many2one('account.period','Period'),
        'state':fields.char('State'),
        'date':fields.date('Date'),
        'narration':fields.text('Narration'),
        'xo_working_hours':fields.float('Working Hours'),
        'xo_total_wage':fields.float('Total Wage'),
        'name':fields.char('Name'),
        'over_time_type_id':fields.many2one('hr.salary.rule','Overtime Type'),
        'ot_allowance':fields.float('Allowance')


    }


    def _select(self):
        select_str = """
              SELECT ROW_NUMBER () OVER (ORDER BY od_hr_over_time_line.id ) AS id,
od_hr_over_time_line.hour as hour,
od_hr_over_time_line.employee_id as employee_id,
od_hr_over_time.period_id as period_id,
od_hr_over_time.state as state,

od_hr_over_time.date as date,
od_hr_over_time.narration as narration,
hr_contract.xo_working_hours as xo_working_hours,
hr_contract.xo_total_wage as xo_total_wage,
od_hr_over_time.name as name,
CASE
WHEN 
        od_hr_over_time_line.code = 'OHOT'
 THEN
         (((xo_total_wage/EXTRACT(DAY FROM account_period.date_stop))/xo_working_hours) * 2.5)*hour
WHEN 
        od_hr_over_time_line.code = 'NIOT'
 THEN
   (((xo_total_wage/EXTRACT(DAY FROM account_period.date_stop))/xo_working_hours) * 2.5)*hour

WHEN 
        od_hr_over_time_line.code = 'HOT'
 THEN         
(((xo_total_wage/EXTRACT(DAY FROM account_period.date_stop))/xo_working_hours) * 1.5)*hour
        
ELSE
  (((xo_total_wage/EXTRACT(DAY FROM account_period.date_stop))/xo_working_hours) * 1.25)*hour
        
END AS ot_allowance,
od_hr_over_time_line.over_time_type as over_time_type_id
        """
        return select_str
    def _from(self):
        from_str = """
                od_hr_over_time_line  

       
        """
        return from_str

    def _group_by(self):
        group_by_str = """
            GROUP BY od_hr_over_time_line.id,
od_hr_over_time_line.hour,
od_hr_over_time_line.employee_id,
od_hr_over_time.period_id,
od_hr_over_time.state,

od_hr_over_time.date,
od_hr_over_time.narration,
hr_contract.xo_working_hours,
hr_contract.xo_total_wage,
od_hr_over_time.name,
account_period.date_stop,


        

od_hr_over_time_line.over_time_type
                    
        """

  
        return group_by_str


    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM  %s 
  

LEFT OUTER JOIN od_hr_over_time ON od_hr_over_time_line.hr_over_time_id = od_hr_over_time.id
LEFT OUTER JOIN hr_contract ON od_hr_over_time_line.employee_id = hr_contract.employee_id 
LEFT OUTER JOIN account_period on account_period.id = od_hr_over_time.period_id
and hr_contract.od_active = 't' 
  %s
            )""" % (self._table, self._select(), self._from(), self._group_by()))




