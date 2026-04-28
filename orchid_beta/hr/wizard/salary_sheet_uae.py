# -*- coding: utf-8 -*-


from openerp.osv import fields, osv
from openerp import tools
from datetime import datetime, timedelta, date
import os
import csv
import tempfile
import base64
import csv, cStringIO
from PIL import Image
from openerp.exceptions import Warning


class uae_salary_sheet_wiz(osv.osv_memory):
    _name = 'uae.salary.sheet.wiz'

    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id

    _columns = {
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'period_id': fields.many2one('account.period', string="Period", required=True),
        'branch_ids': fields.many2many('od.cost.branch', string="Branch"),
        'export_file': fields.binary(string="File"),
        'export_name': fields.char(string="Export File Name"),
    }
    _defaults = {
        'company_id': _get_default_company,
    }

    # @api.multi
    def btn_export_excel(self, cr, uid, ids, context=None):
        wizard_pool = self.pool['uae.salary.sheet.wiz']
        # context = self._context
        # sheet_id = context.get('sheet_id')
        file_path = tempfile.gettempdir() + '/' + 'data.csv'
        line_data = []
        rpt_temp = 'report.od_uae_salary_rpt'
        rpt_pool = self.pool['uae.salary.rpt.data']
        rpt_line_pool = self.pool['uae.salary.rpt.data.line']
        company_id = self.browse(cr, uid, ids).company_id and self.browse(cr, uid, ids).company_id.id
        tools.sql.drop_view_if_exists(cr, 'od_hrms_salary_sheet_view_uae')
        company_id = self.browse(cr, uid, ids).company_id and self.browse(cr, uid, ids).company_id.id
        period_id = self.browse(cr, uid, ids).period_id and self.browse(cr, uid, ids).period_id.id
        branch_ids = self.browse(cr, uid, ids).branch_ids and self.browse(cr, uid, ids).branch_ids.ids
        if not branch_ids:
            branch_ids = self.pool['od.cost.branch'].search(cr, uid, [])
        # hhh
        start_date = self.browse(cr, uid, ids).period_id.date_start
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
        month = start_date_obj.strftime("%B-%Y")
        today = date.today()
        today_date_str = today.strftime("%Y-%m-%d")
        where = "where hr_payslip.xo_period_id=%s" % period_id

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
                            )""" % ('od_hrms_salary_sheet_view_uae', self._select(), self._from(), where,
                                    self._group_by()))

        # sheet_lines = cr.dictfetchall()
        sheet_lines = self.pool['od.hrms.salary.sheet.view.uae'].search(cr, uid, [], context=context,
                                                                        order='identification')
        vals = {
            'name': "Salary Sheet",
            'sheet_line': line_data,
            'month': month,
            # 'currency_id': currency_id,
            'company_id': company_id,
        }
        rpt = rpt_pool.create(cr, uid, vals)
        rpt_id = rpt
        sheet_ids = self.pool['od.hrms.salary.sheet.view.uae'].browse(cr, uid, sheet_lines)
        unpaid_leaves = 0
        total_net_salary = 0
        total_ot_salary = 0
        total_salary = 0
        no_of_recs = 0
        for sheet in self.pool['od.hrms.salary.sheet.view.uae'].browse(cr, uid, sheet_lines):
            unpaid_leaves = 0
            print("sheet.employee_id.id", sheet.employee_id.id)
            unpaid_leaves = self._compute_unpaid_leaves(cr, uid, ids, sheet, context=None)
            print("unpaid_leaves", unpaid_leaves)
            if sheet.employee_id.od_branch_id.id in branch_ids:
                line_vals = {
                    'Employee Detail Record': 'EDR',
                    'Id Number': sheet.employee_id.otherid,
                    'Staff No': sheet.identification,
                    'Employee Name': sheet.employee_id.user_id.name,
                    'Routing Code': sheet.employee_id.bank_account_id.bank_bic,
                    'IBAN': sheet.employee_id.bank_account_id.acc_number,
                    'Start Date': sheet.date_from,
                    'End Date': sheet.date_to,
                    'No:of Days': sheet.days_in_month,
                    'Net Salary': round(sheet.net_salary - sheet.ot_allowance),
                    'Overtime': round(sheet.ot_allowance),
                    'Unpaid Leaves': unpaid_leaves,
                }
                line_data.append(line_vals)
                total_net_salary +=  round(sheet.net_salary - sheet.ot_allowance)
                total_ot_salary +=  round(sheet.ot_allowance)
                no_of_recs +=  1

        ctx = context
        print("line_data", line_data)
        total_salary = total_net_salary + total_ot_salary
        last_line_vals = {
            'Employee Detail Record': 'SDR',
            'Id Number': '0000000860470',
            'Staff No': '',
            'Employee Name': '',
            'Routing Code': '600310101',
            'IBAN': today_date_str,
            'Start Date': '09:00',
            'End Date': self.browse(cr, uid, ids).period_id.name,
            'No:of Days': no_of_recs,
            'Net Salary': total_salary,
            'Overtime': 'AED',
            'Unpaid Leaves': 'AE770030010143406020001',
        }
        last_line_list = []
        last_line_list.append(last_line_vals)
        keys = ['Employee Detail Record','Id Number', 'Staff No', 'Employee Name', 'Routing Code', 'IBAN', 'Start Date', 'End Date','No:of Days',
                'Net Salary', 'Overtime', 'Unpaid Leaves']
        with open(file_path, 'wb') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(line_data)
            dict_writer.writerows(last_line_list)
        file = open(file_path, 'rb')
        out = file.read()
        file.close()
        # self.write({'export_file': base64.b64encode(out), 'export_name': 'Export.csv'})
        self.write(cr, uid, ids, {'export_file': base64.b64encode(out), 'export_name': 'Export.csv'})
        print("self.browse(cr, uid, ids)", self.browse(cr, uid, ids).id)
        res_id = self.browse(cr, uid, ids).id
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'uae.salary.sheet.wiz',
            'res_id': res_id,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def _compute_unpaid_leaves(self, cr, uid, ids, sheet_id, context=None):
        days = 0.0
        year_start_date = (date(date.today().year, 1, 1)).strftime("%Y-%m-%d")
        year_end_date = (date(date.today().year, 12, 1)).strftime("%Y-%m-%d")
        if sheet_id:
            month_start_date = sheet_id.date_from
            month_end_date = sheet_id.date_to
            days = 0.0
            leaves = self.pool['hr.holidays'].search(cr, uid, [('holiday_status_id', '=', 4),
                                                               ('employee_id', '=', sheet_id.employee_id.id),
                                                               ('state', 'in', ('validate','od_resumption_to_approve','od_approved')),
                                                               ('od_start', '>', year_start_date),
                                                               ('od_end', '<', year_end_date)])
            for leave in self.pool['hr.holidays'].browse(cr, uid, leaves):
                month_end_date = sheet_id.date_to
                if isinstance(month_end_date, date):
                    month_end_date = month_end_date.strftime("%Y-%m-%d")
                if leave.od_start >= month_start_date and leave.od_end <= month_end_date:
                    days += leave.od_number_of_days
                else:
                    if month_start_date <= leave.od_end <= month_end_date:
                        date_start = datetime.strptime(month_start_date, "%Y-%m-%d").date()
                        month_end_date = datetime.strptime(leave.od_end, "%Y-%m-%d").date()

                        days += (month_end_date - date_start).days + 1
                    if month_start_date <= leave.od_start <= month_end_date:
                        date_start = datetime.strptime(leave.od_start, "%Y-%m-%d").date()
                        month_end_date = datetime.strptime(month_end_date, "%Y-%m-%d").date()

                        days += (month_end_date - date_start).days + 1

        return days

    def print_rpt(self, cr, uid, ids, context=None):
        print("print_rpt")
        line_data = []
        rpt_temp = 'report.od_uae_salary_rpt'
        rpt_pool = self.pool['uae.salary.rpt.data']
        rpt_line_pool = self.pool['uae.salary.rpt.data.line']
        company_id = self.browse(cr, uid, ids).company_id and self.browse(cr, uid, ids).company_id.id
        tools.sql.drop_view_if_exists(cr, 'od_hrms_salary_sheet_view_uae')
        company_id = self.browse(cr, uid, ids).company_id and self.browse(cr, uid, ids).company_id.id
        period_id = self.browse(cr, uid, ids).period_id and self.browse(cr, uid, ids).period_id.id
        branch_ids = self.browse(cr, uid, ids).branch_ids and self.browse(cr, uid, ids).branch_ids.ids
        if not branch_ids:
            branch_ids = self.pool['od.cost.branch'].search(cr, uid, [])
        # hhh
        start_date = self.browse(cr, uid, ids).period_id.date_start
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
        month = start_date_obj.strftime("%B-%Y")
        where = "where hr_payslip.xo_period_id=%s" % period_id

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
                    )""" % ('od_hrms_salary_sheet_view_uae', self._select(), self._from(), where, self._group_by()))

        # sheet_lines = cr.dictfetchall()
        sheet_lines = self.pool['od.hrms.salary.sheet.view.uae'].search(cr, uid, [], context=context,
                                                                        order='identification')
        vals = {
            'name': "Salary Sheet",
            'sheet_line': line_data,
            'month': month,
            # 'currency_id': currency_id,
            'company_id': company_id,
        }
        rpt = rpt_pool.create(cr, uid, vals)
        rpt_id = rpt
        sheet_ids = self.pool['od.hrms.salary.sheet.view.uae'].browse(cr, uid, sheet_lines)
        for sheet in self.pool['od.hrms.salary.sheet.view.uae'].browse(cr, uid, sheet_lines):
            # sheet = self.pool['od.hrms.salary.sheet.view.uae'].browse(cr, uid, line)
            print("sheet.employee_id.od_branch_id", sheet.employee_id.od_branch_id)
            if sheet.employee_id.od_branch_id.id in branch_ids:
                line_vals = {
                    'employee_id': sheet.employee_id.id,
                    'address_id': sheet.address_id.id,
                    'sheet_id': rpt_id,
                    'date_from': sheet.date_from,
                    'date_to': sheet.date_to,
                    'identification': sheet.identification,
                    'od_cost_centre_id': sheet.od_cost_centre_id.id,
                    'basic': round(sheet.basic),
                    'house_allowance': round(sheet.house_allowance),
                    'transport_allowance': round(sheet.transport_allowance),
                    'other_allowance': round(sheet.other_allowance),
                    'other_payment': round(sheet.other_payment),
                    'ot_allowance': round(sheet.ot_allowance),
                    'total_salary': round(sheet.gross_salary) + round(sheet.other_payment) + round(sheet.ot_allowance),
                    'loan_deduction': round(sheet.loan_deduction),
                    'other_deduction': round(sheet.other_deduction) + round(sheet.leave_deduction) + round(sheet.unresume_ded),
                    'net_salary': round(sheet.net_salary),
                }
                line_rec = rpt_line_pool.create(cr, uid, line_vals)
                # hhhh
                # line_data.append((0, 0, {
                #     'employee_id': sheet.employee_id.id,
                #     'address_id': sheet.address_id.id,
                #     'date_from': sheet.date_from,
                #     'date_to': sheet.date_to,
                #     'identification': sheet.identification,
                #     'od_cost_centre_id': sheet.od_cost_centre_id.id,
                #     'basic': sheet.basic,
                #     'house_allowance': sheet.house_allowance,
                #     'transport_allowance': sheet.transport_allowance,
                #     'other_allowance': sheet.other_allowance,
                #     'other_payment': sheet.other_payment,
                #     'ot_allowance': sheet.ot_allowance,
                #     'total_salary': sheet.total_salary,
                #     'loan_deduction': sheet.loan_deduction,
                #     'other_deduction': sheet.other_deduction,
                #     'net_salary': sheet.net_salary,
                # }))

        ctx = context
        # vals = {
        #     'name': "Salary Sheet",
        #     'sheet_line': line_data,
        #     # 'date': self.date,
        #     # 'currency_id': currency_id,
        #     'company_id': company_id,
        # }
        # rpt = rpt_pool.create(cr, uid, vals)
        # print("rpt", rpt, type(rpt))
        # rpt_id = rpt
        # cr = self.env.cr
        # uid = self.env.uid
        return self.pool['report'].get_action(cr, uid, [rpt_id], rpt_temp, context=ctx)

    def export_rpt(self, cr, uid, ids, context=None):
        tools.sql.drop_view_if_exists(cr, 'od_hrms_salary_sheet_view_uae')
        company_id = self.browse(cr, uid, ids).company_id and self.browse(cr, uid, ids).company_id.id
        period_id = self.browse(cr, uid, ids).period_id and self.browse(cr, uid, ids).period_id.id
        where = "where hr_payslip.xo_period_id=%s" % period_id

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
            )""" % ('od_hrms_salary_sheet_view_uae', self._select(), self._from(), where, self._group_by()))

        #         cr.execute(query)
        return {

            'name': 'Uae Salary Sheet Report',
            'view_type': 'form',
            'view_mode': 'tree,graph',
            'res_model': 'od.hrms.salary.sheet.view.uae',
            'type': 'ir.actions.act_window',
            #             'context':{'search_default_brand':1,'search_default_po':1}
        }

    def _select(self):
        select_str = """
              SELECT ROW_NUMBER () OVER (ORDER BY hr_payslip.id ) AS id,
             hr_payslip.employee_id AS employee_id,
             hr_employee.address_id as address_id,
            hr_employee.od_cost_centre_id,
            hr_employee.od_sponser_id,
             hr_payslip.company_id as company_id,
             hr_payslip.date_from AS date_from,
             hr_payslip.date_to AS date_to,
             hr_employee.od_identification_no as identification,
             hr_employee.department_id as department_id,
             hr_employee.od_cost_centre_id as cost_centre_id,
             hr_employee.od_branch_id as branch_id,
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
                                hr_payslip_line.code in ('UAE_GRBIT')
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
                          hr_payslip_line.code = 'UAE_OTHPAY' 
                        
                
) AS other_payment,
 (
        SELECT
                SUM (hr_payslip_line.total) 
        FROM
                hr_payslip_line
        WHERE                        
                                hr_payslip_line.slip_id = hr_payslip. ID
                AND 
                                hr_payslip_line.code in ('UAE_HOT','UAE_NOT','UAE_FOT','UAE_OOT')           
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
                                hr_payslip_line.code = 'UAE_UNRESUME'                 
) AS unresume_ded,
 (
        SELECT
                SUM (hr_payslip_line.total)
        FROM
                hr_payslip_line
        WHERE                
                                hr_payslip_line.slip_id = hr_payslip. ID
                AND 
                                hr_payslip_line.code= 'UAE_LOAN'
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
                hr_payslip_line.code = 'UAE_OTHDED'                
) AS other_deduction,
 (
        SELECT
                SUM (hr_payslip_line.total)
        FROM
                hr_payslip_line
        WHERE                
                hr_payslip_line.slip_id = hr_payslip. ID
        AND 
                hr_payslip_line.code = 'UAE_UNPAID' 
) AS leave_deduction, 
 (
        SELECT
                SUM (hr_payslip_line.total)
        FROM
                hr_payslip_line
        WHERE        
                                hr_payslip_line.slip_id = hr_payslip. ID
                AND 
                hr_payslip_line.code= 'UAE_NET'
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
                                        hr_payslip_line.code= 'UAE_NET'
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
                                        hr_payslip_line.code = 'UAE_NET'                        
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
                                        hr_payslip_line.code = 'UAE_NET'                        
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
        hr_employee.od_branch_id,
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


class uae_salary_rpt_data(osv.osv_memory):
    _name = 'uae.salary.rpt.data'

    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id

    _columns = {
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'currency_id': fields.many2one('res.currency', 'Currency'),
        'date_today': fields.date('Date Today'),
        'name': fields.char('Name'),
        'month': fields.char('Month'),
        'sheet_line': fields.one2many('uae.salary.rpt.data.line', 'sheet_id', 'Salary Sheet Lines'),

    }
    _defaults = {
        'company_id': _get_default_company,
        'date_today': fields.date.context_today,
    }


class uae_salary_rpt_data_line(osv.osv_memory):
    _name = "uae.salary.rpt.data.line"

    _columns = {
        'employee_id': fields.many2one('hr.employee', 'Employee'),
        'address_id': fields.many2one('res.partner', 'Working Address'),
        'sheet_id': fields.many2one('uae.salary.rpt.data', 'Sheet Data'),
        'date_from': fields.date('Date From'),
        'date_to': fields.date('Date To'),
        'od_sponser_id': fields.many2one('hr.employee', 'Sponser'),
        'company_id': fields.many2one('res.company', 'Company', readonly=True),
        'od_cost_centre_id': fields.many2one('od.cost.centre', 'Cost Centre'),
        #        'xo_total_wage':fields.float('Monthly Salary'),
        'daily_salary': fields.float('Daily Salary'),
        'net_salary': fields.float('Net Salary'),
        'loan_deduction': fields.float('Loan Deduction'),
        'period': fields.char('Period'),
        'cash': fields.float('Cash'),
        'period_id': fields.many2one('account.period', 'Account Period'),
        'xo_mode_of_payment_id': fields.many2one('od.mode.of.payment', 'Mode Of Payment'),
        'identification': fields.integer('Identification No'),
        'department_id': fields.many2one('hr.department', 'Department'),
        'cost_centre_id': fields.many2one('od.cost.centre', 'Cost Centre'),
        'branch_id': fields.many2one('od.cost.branch', 'Branch'),
        'basic': fields.float('Basic'),
        'house_allowance': fields.float('House Allowance'),
        'transport_allowance': fields.float('Transport Allowance'),
        'other_allowance': fields.float('Other Allowance'),
        'gross_salary': fields.float('Gross Salary'),
        'wps_beta_engineering': fields.float('WPS Beta Engineering'),
        'wps_beta_it': fields.float('WPS Beta IT'),
        'leave_deduction': fields.float('Leave Deduction'),
        'other_deduction': fields.float('Other Deduction'),
        'total_salary': fields.float('Total Salary'),
        'ot_allowance': fields.float('OT Allowance'),
        'other_payment': fields.float('Other Payment'),
        'days_in_month': fields.float('Days In Month'),
        'working_days': fields.float('Working Days'),
        'late_arival_deduction': fields.float('Late Arrival Deduction'),
        'leave_salary': fields.float('Leave Salary'),
        'unresume_ded': fields.float('Unresume Deduction'),
    }
