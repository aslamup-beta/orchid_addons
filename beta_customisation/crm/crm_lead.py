# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2013 Camptocamp (<http://www.camptocamp.com>)
#    Authors: Ferdinand Gasauer, Joel Grand-Guillaume
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
##############################################################################
import datetime
from openerp.osv import fields, osv
from openerp import models, api, _
from datetime import date
from openerp.exceptions import Warning
from openerp import SUPERUSER_ID
import time
import calendar
from dateutil.relativedelta import relativedelta
from __builtin__ import True


class hr_employee(osv.osv):
    _inherit = 'hr.employee'
    
    _columns = {
        'od_last_day':fields.date(string='Last Day At Work'),
        'od_resigned' :fields.boolean(string="Resigned"),
        'od_mrg_date': fields.date(string='Date of Marriage'),
        'od_child_birth_date': fields.date(string='Birth Date of Last Child'),
        'od_req_clearance': fields.boolean(string="Clearance Letter Required ?"),
        'od_end_contract': fields.boolean(string="End of Contract ?")
    }
    
    def run_employee_documents_expiry_reminder(self, cr, uid, context=None):
        context = dict(context or {})
        hr_pool = self.pool['hr.employee']
        doc_pool = self.pool['od.hr.employee.document.line']
        today = datetime.date.today()
        emp_ids=hr_pool.search(cr,uid,[('active', '=', True),('company_id', '=', 1)],context=context)
        if emp_ids:
            for emp_id in emp_ids:
                emp = hr_pool.browse(cr,uid,emp_id,context=context)
                # if emp.company_id.id == 6:
                #     temp_id = 353
                #     no_of_days = 30
                # else:
                temp_id = 337
                no_of_days = 15
                document_ids = doc_pool.search(cr, uid, [('employee_id','=',emp_id)],context=context)
                emp_docs = doc_pool.browse(cr, uid, document_ids,context=context)
                for doc in emp_docs:
                    expiry_date = doc.expiry_date
                    context['doc_name'] = doc.document_type_id.name
                    context['expiry_date'] = expiry_date
                    if expiry_date:
                        expiry_date1 = datetime.datetime.strptime(expiry_date,'%Y-%m-%d').date()
                        expiry_date_bf_1mnth = expiry_date1 - relativedelta(days=no_of_days)
                        if expiry_date_bf_1mnth == today:
                            self.pool.get('email.template').send_mail(cr, uid, temp_id, emp_id, force_send=True, context=context)
                            
    def run_employee_documents_expiry_reminder_60_days(self, cr, uid, context=None):
        context = dict(context or {})
        template_id = self.pool['email.template'].browse(cr,uid,354)[0]
        hr_pool = self.pool['hr.employee']
        doc_pool = self.pool['od.hr.employee.document.line']
        today = datetime.date.today()
        emp_ids=hr_pool.search(cr,uid,[('active', '=', True),('company_id', '=', 6)],context=context)
        if emp_ids:
            for emp_id in emp_ids:
                document_ids = doc_pool.search(cr, uid, [('employee_id','=',emp_id)],context=context)
                emp_docs = doc_pool.browse(cr, uid, document_ids,context=context)
                for doc in emp_docs:
                    expiry_date = doc.expiry_date
                    context['doc_name'] = doc.document_type_id.name
                    context['expiry_date'] = expiry_date
                    if expiry_date:
                        expiry_date1 = datetime.datetime.strptime(expiry_date,'%Y-%m-%d').date()
                        expiry_date_bf_2mnth = expiry_date1 - relativedelta(days=60)
                        if expiry_date_bf_2mnth == today:
                            self.pool.get('email.template').send_mail(cr, uid, template_id.id, emp_id, force_send=True, context=context)
                            
    
    def run_employee_bday_reminder(self, cr, uid, context=None):
        hr_pool = self.pool['hr.employee']
        today = datetime.date.today()
        emp_ids=hr_pool.search(cr,uid,[('active', '=', True)],context=context)
        if emp_ids:
            for emp_id in emp_ids:
                emp_rec=hr_pool.browse(cr,uid,emp_id)
                template_id = self.pool['email.template'].browse(cr,uid,139)[0]
                if emp_rec.company_id.id == 6:
                    template_id = self.pool['email.template'].browse(cr,uid,335)[0]
                birthday_date =emp_rec.birthday and datetime.datetime.strptime(emp_rec.birthday,'%Y-%m-%d')
                if birthday_date and birthday_date.month==today.month and  birthday_date.day == today.day:
                    self.pool.get('email.template').send_mail(cr, uid, template_id.id, emp_id, force_send=True, context=context)
        return True
    
    def run_ksa_employee_bday_reminder_to_hr_two_days(self, cr, uid, context=None):
        hr_pool = self.pool['hr.employee']
        today = datetime.date.today()
        emp_ids=hr_pool.search(cr,uid,[('active', '=', True),('company_id','=',6)],context=context)
        if emp_ids:
            for emp_id in emp_ids:
                emp_rec=hr_pool.browse(cr,uid,emp_id)
                template_id = self.pool['email.template'].browse(cr,uid,336)[0]
                birthday_date =emp_rec.birthday and datetime.datetime.strptime(emp_rec.birthday,'%Y-%m-%d')
                if birthday_date:
                    birthday_date_bf_2day = birthday_date - relativedelta(days=2)
                if birthday_date_bf_2day and birthday_date_bf_2day.month==today.month and  birthday_date_bf_2day.day == today.day:
                    self.pool.get('email.template').send_mail(cr, uid, template_id.id, emp_id, force_send=True, context=context)
        return True



    def action_it_approval(self, cr, uid, context=None):
        print("$$$$$$$$$$$$$$$$$")
        hr_pool = self.pool['hr.employee']
        resign_pool = self.pool['od.beta.resign.form']
        term_pool = self.pool['od.beta.terminate.form']
        eoc_pool = self.pool['end.of.contract']
        idp_pool = self.pool['employee.idp']
        today = datetime.date.today()
        emp_ids=hr_pool.search(cr,uid,['&',('od_last_day', '<=', today),('active', '=', True)],context=context)
        print("emp_ids",emp_ids)
        if emp_ids:
            for emp_id in emp_ids:
                emp_rec=hr_pool.browse(cr,uid,emp_id)
                if emp_rec.company_id.id == 6:
                    print("emp_rec.od_resigned", emp_rec.od_resigned)
                    if emp_rec.od_resigned:
                        resign_id = resign_pool.search(cr, uid, [('employee_id','=',emp_rec.id),('state','=','approval4')], order='id desc',context=context)
                        print("resign_id", resign_id)
                        if resign_id:
                            resign_id = resign_id[0]
                            resign_rec = resign_pool.browse(cr,uid,resign_id)
                            resign_rec.action_send_it_approval_mail()
                    if emp_rec.od_terminated:
                        term_id = term_pool.search(cr, uid, [('employee_id','=',emp_rec.id),('state','=','approval4')], order='id desc',context=context)
                        if term_id:
                            term_id = term_id[0]
                            term_rec = term_pool.browse(cr,uid,term_id)
                            term_rec.action_send_it_approval_mail()
                    if emp_rec.od_end_contract:
                        eoc_id = eoc_pool.search(cr, uid, [('employee_id','=',emp_rec.id),('state','=','approval4')], order='id desc',context=context)
                        if eoc_id:
                            eoc_id = eoc_id[0]
                            eoc_rec = eoc_pool.browse(cr,uid,eoc_id)
                            eoc_rec.action_send_it_approval_mail()
    
    
    
    def deactivate_users(self, cr, uid, context=None):
        hr_pool = self.pool['hr.employee']
        resign_pool = self.pool['od.beta.resign.form']
        term_pool = self.pool['od.beta.terminate.form']
        eoc_pool = self.pool['end.of.contract']
        idp_pool = self.pool['employee.idp']
        today = datetime.date.today()
        emp_ids=hr_pool.search(cr,uid,['&',('od_last_day', '<=', today),('active', '=', True)],context=context)
        if emp_ids:
            for emp_id in emp_ids:
                emp_rec=hr_pool.browse(cr,uid,emp_id)
                emp_rec.user_id.write({'active':False})
                emp_rec.address_home_id.write({'active':False})
                contract_id= self.pool['hr.contract'].search(cr, uid, [('employee_id','=',emp_rec.id),('od_active','=',True)],context=context)
                contract_rec = self.pool['hr.contract'].browse(cr,uid,contract_id)
                contract_rec.write({'od_active': False})
                emp_rec.write({'active': False})
                emp_idp_ids = idp_pool.search(cr, uid, [('employee_id', '=', emp_rec.id),
                                                                        ('active', '=', True)])
                if emp_idp_ids:
                    print("emp_idp_ids", emp_idp_ids)
                    for idp in emp_idp_ids:
                        idp_rec = idp_pool.browse(cr, uid, idp)
                        idp_rec.write({'active': False})
                if emp_rec.company_id.id ==6 and emp_rec.od_resigned:
                    resign_id = resign_pool.search(cr, uid, [('employee_id','=',emp_rec.id),('state','in',['confirm', 'sent_clearance'])], order='id desc',context=context)[0]
                    if resign_id:
                        resign_rec = resign_pool.browse(cr,uid,resign_id)
                        resign_rec.generate_gratuity_accounting_entry()
                if emp_rec.company_id.id ==6 and emp_rec.od_terminated:
                    term_id = term_pool.search(cr, uid, [('employee_id','=',emp_rec.id),('state','in',['confirm', 'sent_clearance'])], order='id desc',context=context)[0]
                    if term_id:
                        term_rec = term_pool.browse(cr,uid,term_id)
                        term_rec.generate_gratuity_accounting_entry()
                if emp_rec.company_id.id ==6 and emp_rec.od_end_contract:
                    eoc_id = eoc_pool.search(cr, uid, [('employee_id','=',emp_rec.id),('state','in',['confirm', 'sent_clearance'])], order='id desc',context=context)[0]
                    if eoc_id:
                        eoc_rec = eoc_pool.browse(cr,uid,eoc_id)
                        eoc_rec.generate_gratuity_accounting_entry()
                    
        return True
    
    def emp_contract_expiry_reminder(self, cr, uid, context=None):
        hr_pool = self.pool['hr.employee']
        today = datetime.date.today()
        context = dict(context or {})
        emp_ids= hr_pool.search(cr,uid,[('od_joining_date','>=','01-Jan-19')],context=context)
        emp_recs= hr_pool.browse(cr,uid,emp_ids,context=context)
        template = 'od_probation_period_end_date'
        template_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'beta_customisation', template)[1]
        for emp in emp_recs:
            emp_join_date = datetime.datetime.strptime(emp.od_joining_date, "%Y-%m-%d").date()
            if emp.company_id.id == 6:
                dt = emp_join_date + relativedelta(months=2)
            else:
                dt = emp_join_date + relativedelta(months=5)
            contract_id= self.pool['hr.contract'].search(cr, uid, [('employee_id','=',emp.id),('od_active','=',True)],context=context)
            contract_rec = self.pool['hr.contract'].browse(cr,uid,contract_id)
            context['trail_end_date'] = contract_rec.trial_date_end
            if dt == today:
                self.pool.get('email.template').send_mail(cr, uid, template_id, emp.id, force_send=False, context=context)
        return True
    
    def emp_legal_leaves_reminder(self, cr, uid, context=None):
        hr_pool = self.pool['hr.employee']
        emp_ids= hr_pool.search(cr,uid,[('company_id','=',1)],context=context)
#         emp_ids = [426]
        emp_recs= hr_pool.browse(cr,uid,emp_ids,context=context)
        import datetime
        today = datetime.date.today()
        context = dict(context or {})
        for emp in emp_recs:
            template = 'od_pending_legal_leaves'
            # if emp.company_id.id == 6:
            #     template = template + '_saudi'
            template_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'beta_customisation', template)[1]
            from datetime import datetime
            od_joining_date = datetime.strptime(emp.od_joining_date, "%Y-%m-%d")
            od_today = str(datetime.strptime(str(today), '%Y-%m-%d'))
            total_days = (datetime.strptime(str(od_today), '%Y-%m-%d %H:%M:%S') - datetime.strptime(str(od_joining_date), '%Y-%m-%d %H:%M:%S')).days
            from datetime import date
            start_date = date(date.today().year, 1, 1)
            end_date = date(date.today().year, 12, 31)
            holi = self.pool['hr.holidays']
            holi_ids =holi.search(cr, uid, [('employee_id','=',emp.id), ('od_start','>=',start_date),('od_end','<=',end_date),('state','not in',('draft','cancel','refuse')),('holiday_status_id','=',1)])
            holi_recs = holi.browse(cr, uid, holi_ids)
            days =sum([a.number_of_days_temp for a in holi_recs])
            pending_days = 30 - days
            context['pending_days'] = pending_days
            if pending_days >=1 and total_days >=365:
                self.pool.get('email.template').send_mail(cr, uid, template_id, emp.id, force_send=False, context=context)
        return True
    
    #Below 4 functions added for Auto generation of gratuity monthly as JV
    def get_active_contract(self,cr, uid, emp, context=None):
        employee_id = emp.id
        res =self.pool['hr.contract'].search(cr, uid, [('od_active','=',True),('employee_id','=',employee_id)],limit=1)
        res1 = self.pool['hr.contract'].browse(cr, uid, res, context=context)
        if emp.active == False:
            res =self.pool['hr.contract'].search(cr, uid, [('employee_id','=',employee_id)], order='id desc')[0]   
            res1 = self.pool['hr.contract'].browse(cr, uid, res, context=context) 
        return res1
    
    def compute_total_wage_without_kpi(self, cr, uid, contract_rec, context=None):
        allowances = 0.0
        basic = contract_rec.wage
        for line in contract_rec.xo_allowance_rule_line_ids:
            if line.code=='OA':
                allowances+=line.amt
            if line.code=='ALW':
                allowances+=line.amt
        if allowances:
            wage= allowances + basic
        else:
            wage = basic
        return wage
    
    def days_between(self,cr, uid, d1, d2,context=None ):
        from datetime import datetime
        d1 = datetime.strptime(d1, "%Y-%m-%d")
        d2 = datetime.strptime(d2, "%Y-%m-%d")
        return abs((d2 - d1).days)+1
    
    def _compute_years(self, cr, uid,  joining_date, context=None):
        from datetime import datetime
        last_day = datetime.today().strftime('%Y-%m-%d')
        if last_day:
            if joining_date and last_day:
                days = self.days_between(cr, uid, joining_date, last_day, context=context)
                years = days/365.2425
                return years
    
    def create_provision_for_leave_gratuity(self, cr, uid, context=None):
        from datetime import datetime
        period_obj = self.pool['account.period']
        move_obj = self.pool['account.move']
        emp_ids= self.search(cr, uid, [('company_id','=',6), ('id','!=',329)], context=context)
        emp_recs= self.browse(cr, uid, emp_ids, context=context)
        total_grat = 0.0
        journal_id = 41
        move_lines =[]
        credit_acc_id = 5735
        debit_acc_id = 5440
        date = datetime.today().strftime('%Y-%m-%d')
        period_ids = period_obj.find(cr, uid, date)[0]
        period_name = self.pool['account.period'].browse(cr, uid, [period_ids])
        current_month = period_name.name
        for emp in emp_recs:
            partner_id = emp.address_home_id.id
            branch_id = emp.od_branch_id.id
            cost_centre_id = emp.od_cost_centre_id.id
            contract_rec = self.get_active_contract(cr, uid, emp, context=context)
            total_wage = self.compute_total_wage_without_kpi(cr, uid, contract_rec, context=context)
            joining_date = emp.od_joining_date
            work_period = self._compute_years(cr, uid,  joining_date, context=context)
            import datetime
            now = datetime.datetime.now()
            current_month_days = calendar.monthrange(now.year, now.month)[1]
            if current_month_days == 31.0:
                days = 31.0
            else:
                days = 30.0
            if work_period <= 5:
                val = (total_wage/2.0)*(days/365.0)
            else:
                val = (total_wage)*(days/365.0)
            total_grat += val
            d_vals1={
                    'name': 'L&G EXPENSE - ' + current_month,
                    'period_id': period_ids ,
                    'account_id': debit_acc_id,
                    'credit': 0.0,
                    'quantity': 1,
                    'debit': abs(val),
                    'partner_id': partner_id,
                    'od_branch_id': branch_id,
                    'od_cost_centre_id': cost_centre_id
                }
            move_lines.append([0,0,d_vals1])
        c_vals1={
                'name': 'L&G EXPENSE - ' + current_month,
                'period_id': period_ids ,
                'account_id': credit_acc_id,
                'quantity': 1,
                'debit': 0.0,
                'credit': abs(total_grat),
                'partner_id': False
            }
        move_lines.append([0,0,c_vals1])
        move_vals = {

                'date': date,
                'ref': 'L&G EXPENSE',
                'period_id': period_ids ,
                'journal_id': journal_id,
                'line_id':move_lines
                }
        move_id = move_obj.create(cr, uid,move_vals, context=context)
        return True
                
    
class hr_contract(osv.osv):
    _inherit = 'hr.contract'
    
    def emp_contract_end_date_reminder(self, cr, uid, context=None):
        today = date.today()
        context = dict(context or {})
        template = 'od_contract_end_date'
        template_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'beta_customisation', template)[1]
        contract_ids= self.pool['hr.contract'].search(cr, uid, [('employee_id.company_id','=',6),('od_active','=',True),('od_limited','=',True)],context=context)
        for contract in self.browse(cr,uid,contract_ids):
            contract_end_date = contract.date_end
#             today = datetime.datetime.strptime(today, "%Y-%m-%d").date()
            date_after_90_days = today + relativedelta(months=3)
            if contract_end_date == str(date_after_90_days):
                self.pool.get('email.template').send_mail(cr, uid, template_id, contract.id, force_send=False, context=context)
        return True
    
    def emp_contract_end_date_reminder_60_days(self, cr, uid, context=None):
        today = date.today()
        context = dict(context or {})
        template_id = 351
        contract_ids= self.pool['hr.contract'].search(cr, uid, [('employee_id.company_id','=',6),('od_active','=',True),('od_limited','=',True)],context=context)
        for contract in self.browse(cr,uid,contract_ids):
            contract_end_date = contract.date_end
#             today = datetime.datetime.strptime(today, "%Y-%m-%d").date()
            date_after_60_days = today + relativedelta(months=2)
            if contract_end_date == str(date_after_60_days):
                self.pool.get('email.template').send_mail(cr, uid, template_id, contract.id, force_send=False, context=context)
        return True
    
    def emp_contract_end_date_reminder_same_day(self, cr, uid, context=None):
        today = date.today()
        context = dict(context or {})
        template_id = 352
        contract_ids= self.pool['hr.contract'].search(cr, uid, [('employee_id.company_id','=',6),('od_active','=',True),('od_limited','=',True)],context=context)
        for contract in self.browse(cr,uid,contract_ids):
            contract_end_date = contract.date_end
#             today = datetime.datetime.strptime(today, "%Y-%m-%d").date()
            if contract_end_date == str(today):
                self.pool.get('email.template').send_mail(cr, uid, template_id, contract.id, force_send=False, context=context)
        return True
    
class hr_holidays(osv.osv):
    _inherit = 'hr.holidays'
    
    def emp_duty_resumption_reminder(self, cr, uid, context=None):
        today = date.today()
        context = dict(context or {})
        leaves= self.pool['hr.holidays'].search(cr, uid, [('od_start','>','01-Jan-21'),('holiday_status_id.id','=',1),('state','=','validate')],context=context)
        for leave in self.browse(cr,uid,leaves):
            leave_end_date = leave.od_end
            company_id = leave.employee_id.company_id.id
            template_id = 76
            if company_id == 6:
                template_id = 77
            leave_end_date = datetime.datetime.strptime(leave_end_date, "%Y-%m-%d").date()
            date_after_1_day = leave_end_date + relativedelta(days=1)
            if today == date_after_1_day:
                leave.write({'allow_resumption': True})
                self.pool.get('email.template').send_mail(cr, uid, template_id, leave.id, force_send=False, context=context)
        return True
    
class account_analytic_account(osv.osv):
    _inherit = 'account.analytic.account'
    
    def planned_invoice_date_reminder(self, cr, uid, context=None):
        template = 'od_planned_a0_invoice_reminder_email_template'
        ir_model_data = self.pool.get('ir.model.data')
        analytic_obj = self.pool.get('account.analytic.account')
        user_obj = self.pool.get('res.users')
        company_id = user_obj.browse(cr, uid, uid, context=context).company_id.id
        if company_id == 6:
            template = template +'_saudi'
        template_id = ir_model_data.get_object_reference(cr,uid,'beta_customisation', template)[1]
        open_a0s  = analytic_obj.search(cr, uid, [('state','=','open'), ('od_type_of_project','=','parent_level0'), ('od_analytic_level','=','level0'), ('fin_approved_date','>=', '03-Mar-20 23:00:00')])
        for analytic_id in open_a0s:
            analytic_account=analytic_obj.browse(cr,uid,analytic_id)
            today = datetime.date.today()
            company_id = analytic_account.company_id and analytic_account.company_id.id or False
            if company_id == 6:
                template = template +'_saudi'
            for inv_line in analytic_account.prj_inv_sch_line:
                invoice_id = inv_line.invoice_id and inv_line.invoice_id.id or False
                if not invoice_id:
                    planned_date = inv_line.date
                    check_date = today + relativedelta(days=7)
                    target_date = check_date.strftime('%Y-%m-%d')
                    if target_date == planned_date:
                        self.pool.get('email.template').send_mail(cr, uid, template_id, analytic_id, force_send=True, context=context)
        return True
    
    #Added by aslam as requested by sami for reminding finance about this finance date from ao planning
    def finance_invoice_date_reminder(self, cr, uid, context=None):
        template = 'od_finance_a0_invoice_reminder_email_template'
        ir_model_data = self.pool.get('ir.model.data')
        analytic_obj = self.pool.get('account.analytic.account')
        user_obj = self.pool.get('res.users')
        company_id = user_obj.browse(cr, uid, uid, context=context).company_id.id
        template_id = ir_model_data.get_object_reference(cr,uid,'beta_customisation', template)[1]
        open_a0s  = analytic_obj.search(cr, uid, [('od_type_of_project','=','parent_level0'), ('od_analytic_level','=','level0'), ('fin_approved_date','>=', '03-Mar-20 23:00:00')])
        for analytic_id in open_a0s:
            analytic_account=analytic_obj.browse(cr,uid,analytic_id)
            today = datetime.date.today()
            company_id = analytic_account.company_id and analytic_account.company_id.id or False
            if company_id == 6:
                template = template +'_saudi'
            for inv_line in analytic_account.prj_inv_sch_line:
                inv_fin_date = inv_line.finance_date or False
                if inv_fin_date:
                    finance_date = inv_line.finance_date
                    check_date = today + relativedelta(days=7)
                    target_date = check_date.strftime('%Y-%m-%d')
                    if target_date == finance_date:
                        self.pool.get('email.template').send_mail(cr, uid, template_id, analytic_id, force_send=True, context=context)
        return True
    
    def auto_closing_a0_analytic(self, cr, uid, context=None):
        analytic_obj = self.pool.get('account.analytic.account')
        open_a0s  = analytic_obj.search(cr, uid, [('state','=','open'), ('od_type_of_project','=','parent_level0'), ('od_analytic_level','=','level0')])
        analytic_accounts=analytic_obj.browse(cr,uid,open_a0s)
        all_closed = []
        for analytic in analytic_accounts:
            for child_acc in analytic.od_child_data:
                if child_acc.od_type_of_project not in ('amc_view', 'o_m_view'):
                    if child_acc.state == 'close':
                        all_closed.append("Y")
                    else:
                        all_closed.append("N")
            
            for child_acc in analytic.od_grandchild_data:
                if child_acc.state == 'close':
                    all_closed.append("Y")
                else:
                    all_closed.append("N")
                    
            if not 'N' in all_closed:
                analytic.set_close()
                for child_acc in analytic.od_child_data:
                    if child_acc.od_type_of_project in ('amc_view', 'o_m_view'):
                        child_acc.set_close()
                all_closed =  []
            else:
                all_closed =  []
            
        return True   

class crm_lead(osv.osv):
    _inherit = "crm.lead"
    
    
    def cron_od_lead_weekly_reminder(self, cr, uid, context=None):
        context = dict(context or {})
        remind = []

        def fill_remind( domain):
            base_domain = []
            base_domain.extend(domain)
            cost_sheet_ids = self.search(cr, uid, base_domain, context=context)
            
            for lead in self.browse(cr,uid,cost_sheet_ids,context=context):
                if lead.stage_id.id == 9 :
                    val = {'name':lead.name,
                           'branch':lead.od_branch_id and lead.od_branch_id.name or '',
                           'customer':lead.partner_id and lead.partner_id.name or '',
                           'hyper_link': 'https://erp.betait.net/web?#id=%d&view_type=form&model=crm.lead&menu_id=136&action=143' % (lead.id)
                        }
#                    br_email = lead.od_branch_id and lead.od_branch_id.email
#                     if br_email:
#                         branch_managers.append(br_email)
                    remind.append(val)
        
        company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        hr_pool = self.pool.get('hr.employee')
        emp_ids = hr_pool.search(cr, SUPERUSER_ID,  [('job_id', 'in', (40, 83))], context=context)
        user_ids = []
        for emp_id in emp_ids:
            employee = hr_pool.browse(cr,SUPERUSER_ID,emp_id)
            user_ids.append(employee.user_id.id)
        for lead_user_id in user_ids:
            remind = []
            branch_managers =[]
            fill_remind([('type','=','lead'),('od_lead_user_id','=',lead_user_id)])
            template = 'od_lead_weekly_cron_email_template'
            if company_id == 6:
                template = template + '_saudi'
            template_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'beta_customisation', template)[1]
            branch_managers = list(set(branch_managers))
            br_emails = ','.join(branch_managers)
            context['branch_managers'] = br_emails
            related_employee_id = hr_pool.search(cr, SUPERUSER_ID,  [('user_id', '=', lead_user_id)], context=context)
            related_employee = hr_pool.browse(cr,SUPERUSER_ID,related_employee_id)
            manager_email = related_employee.parent_id.user_id.email
            context['manager'] = manager_email
            context['lead_am'] = related_employee.user_id.email
            context['lead_am_name'] = related_employee.user_id.name
            context['subject'] = "Update Your Open Leads"
            context['title'] = "We would like to remind you that below leads are still Open. Kindly Update them."
            remind = sorted(remind, key=lambda k: k['branch']) 
            context['data'] = remind
            if remind:
                self.pool.get('email.template').send_mail(cr, uid, template_id, uid, force_send=True, context=context)
        return True
    
    def ksa_portal_submission_datetime_reminder(self, cr, uid, context=None):
        today = date.today()
        context = dict(context or {})
        template_id = 355
        lead_ids= self.search(cr, uid, [('stage_id', 'in', (1,4,12,5,14))],context=context)
        for opp in self.browse(cr,uid,lead_ids):
            portal_date = opp.portal_date
            if portal_date:
                date_after_2_days = today + relativedelta(days=2)
                if portal_date[:10] == str(date_after_2_days):
                    self.pool.get('email.template').send_mail(cr, uid, template_id, opp.id, force_send=False, context=context)
        return True
    
    def create(self, cr, uid, vals, context=None):
        res = super(crm_lead, self).create(cr, uid, vals, context=context)
        context = dict(context or {})
        mod_obj = self.pool.get('ir.model.data')
        email_obj = self.pool.get('email.template')
        template = 'beta_lead_assigned_template'
        template_id = mod_obj.get_object_reference(cr, uid, 'beta_customisation', template)[1]
        lead = self.browse(cr, uid, res, context=context)
        lead_id = lead.id
        lead_user = lead.od_lead_user_id and lead.od_lead_user_id.id or False
        customer_am = lead.user_id and lead.user_id.id or False
        if lead.od_partner_class in ('a','b') and uid != customer_am and uid not in (1,5,6,8,2137,101,154,268,2429,134,2663,2441,2536,2537):
            raise Warning("Opportunities under A and B accounts should not be opened except by the assigned Sales Account Manager.")
        if lead.type == 'lead' and uid != lead_user:
            email_obj.send_mail(cr,uid,template_id,lead_id, force_send=True)
        return res

    
    #Added by Aslam on 22 Dec 2019 for canceling all related cost sheets when opportunity is marked as lost.
    def case_mark_lost(self, cr, uid, ids, context=None):
        for lead in self.browse(cr, uid, ids, context=context):
            lead.write({'od_approval_state':'cancelled'})
            cost_sheet_ids = self.pool['od.cost.sheet'].search(cr, uid, [('lead_id','=',lead.id)], context=context)
            for sheet_id in cost_sheet_ids:
                sheet_rec = self.pool['od.cost.sheet'].browse(cr,uid,sheet_id)
                sheet_rec.write({'state':'cancel'})
        return super(crm_lead, self).case_mark_lost(cr, uid, ids, context=context)
    
    
    def action_schedule_meeting_lead(self, cr, uid, ids, context=None):
        """
        Open meeting's calendar view to schedule meeting on current lead.
        :return dict: dictionary value for created Meeting view
        """
        lead = self.browse(cr, uid, ids[0], context)
        res = self.pool.get('ir.actions.act_window').for_xml_id(cr, uid, 'calendar', 'action_calendar_event', context)
        partner_ids = [self.pool['res.users'].browse(cr, uid, uid, context=context).partner_id.id]
        if lead.partner_id:
            partner_ids.append(lead.partner_id.id)
        res['context'] = {
            'search_default_lead_id': lead.type == 'lead' and lead.id or False,
            'default_lead_id': lead.type == 'lead' and lead.id or False,
            'default_partner_id': lead.partner_id and lead.partner_id.id or False,
            'default_partner_ids': partner_ids,
            'default_section_id': lead.section_id and lead.section_id.id or False,
            'default_name': lead.name,
        }
        return res
    
    def _meeting_count_lead(self, cr, uid, ids, field_name, arg, context=None):
        Event = self.pool['calendar.event']
        return {
            lead_id: Event.search_count(cr,uid, [('lead_id', '=', lead_id)], context=context)
            for lead_id in ids
        }
    @api.one
    @api.depends('user_id')    
    def _compute_cust_user_id(self):
        self.user_id_dummy = self.user_id and self.user_id.id or False
        
    _columns = {
        'meeting_count_lead': fields.function(_meeting_count_lead, string='# Meetings', type='integer'),
        'other_division_ids': fields.many2many('od.cost.division', 'crm_lead_cost_division', 'lead_id', 'division_id', 'Other Technology Unit', \
             help="Other technology units associated with this opportunity"),
        'other_presale_ids':fields.many2many('res.users', 'crm_lead_res_users1', 'lead_id', 'user_id', 'Supporting PreSales', \
             help="Other Pre Sales Engineers associated with this opportunity"),
        'od_cs_presale_id': fields.many2one('res.users', 'CS Solution Architect', select=True, track_visibility='onchange',
                                             help=" CS Solution Architect handling"),
        'od_an_presale_id': fields.many2one('res.users', 'AN Solution Architect', select=True,
                                            track_visibility='onchange',
                                            help=" AN Solution Architect handling"),
        'od_dc_presale_id': fields.many2one('res.users', 'DC Solution Architect', select=True,
                                            track_visibility='onchange',
                                            help=" DC Solution Architect handling"),
        'od_is_presale_id': fields.many2one('res.users', 'InfoSec Solution Architect', select=True,
                                            track_visibility='onchange',
                                            help=" InfoSec Solution Architect handling"),
        'od_approved_date': fields.date(string="Opp. Approval Date"),
        'od_approved_by': fields.many2one('res.users', 'Opp. Approved by', select=True,help="Opp. Approved by"),
        'od_lead_user_id': fields.many2one('res.users', 'Lead AM', select=True,help="Lead Account Manager"),

        'support_presales_emails': fields.char(string="Support presales emails"),
        'user_id_dummy' : fields.many2one('res.users', compute='_compute_cust_user_id', string="Customer AM"),
        'od_partner_class' : fields.selection([('a', 'A'), ('b', 'B'), ('c', 'C'), ('r', 'R')],string="Class",related='partner_id.od_class',store=True)

    }

class calendar_event(osv.osv):
    """ Model for Calendar Event """
    _inherit = 'calendar.event'
        
    _columns = {
        'lead_id': fields.many2one('crm.lead', 'Lead', domain="[('type', '=', 'lead')]"),
    }
    
    def create(self, cr, uid, vals, context=None):
        res = super(calendar_event, self).create(cr, uid, vals, context=context)
        obj = self.browse(cr, uid, res, context=context)
        if obj.lead_id:
            self.pool.get('crm.lead').log_meeting(cr, uid, [obj.lead_id.id], obj.name, obj.start, obj.duration, context=context)
        return res
    
    
class crm_lead2opportunity_partner(osv.osv_memory):
    _inherit = 'crm.lead2opportunity.partner'
    
    def default_get(self, cr, uid, fields, context=None):
        res = super(crm_lead2opportunity_partner, self).default_get(cr, uid, fields, context=context)
        if context.get('active_id'):
            if 'name' in fields:
                res.update({'name' : 'convert'})
            if 'opportunity_ids' in fields:
                res.update({'opportunity_ids': []})
        return res

    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: