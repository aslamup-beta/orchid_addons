#-*- coding:utf-8 -*-
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
from datetime import timedelta
from openerp import SUPERUSER_ID
import math

#import time
class hr_evaluation_interview(osv.Model):
    _inherit = 'hr.evaluation.interview'
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id
    _columns ={
               'company_id': fields.many2one('res.company','Company'),
               }
    _defaults ={
                'company_id': _get_default_company,
                }

class hr_evaluation(osv.Model):
    _inherit = "hr_evaluation.evaluation"
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id
    _columns ={
               'company_id': fields.many2one('res.company','Company'),
               }
    _defaults ={
                'company_id': _get_default_company,
                }
class hr_salary_rule_category(osv.osv):
    _inherit = 'hr.salary.rule.category'
    _columns = {
        'code':fields.char('Code', size=64, required=True, readonly=False),
    }
    _sql_constraints = [
            ('code_uniq', 'unique(code)', 'Code already exist !\n It should be Unique'),
        ]

class hr_salary_rule(osv.osv):
    _inherit = 'hr.salary.rule'
    _columns = {
        'code':fields.char('Code', size=64, required=True, help="The code of salary rules can be used as reference in computation of other rules. In that case, it is case sensitive."),
    }
    _sql_constraints = [
            ('code_uniq', 'unique(code)', 'Code already exist !\n It should be Unique'),
        ]

class hr_contract(osv.osv):
    _inherit = 'hr.contract'
    
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id

    # def onchange_xo_total_wage(self, cr,uid,ids,wage,xo_total_wage, struct_id,context=None):
    #     sal_rul_obj= self.pool.get('hr.salary.rule')
    #     sal_rule_ids = sal_rul_obj.search(cr, uid,[('code', '=','BASIC')], context=context)
    #     basic=0.0
    #     if not sal_rule_ids:
    #         raise osv.except_osv(_('Error!'),_("You need one salery Rule with code 'BASIC'"))
    #     if sal_rule_ids:
    #         sal_rec = sal_rul_obj.browse(cr, uid, sal_rule_ids,context=context)[0]
    #         basic = sal_rec.amount_percentage or 0.0
    #         basic = basic/100
    #     return {'value':{'wage':xo_total_wage*basic}}
    _columns = {
        'company_id': fields.many2one('res.company','Company'),
        'od_active':fields.boolean('Active'),
        'od_limited':fields.boolean('Limited'),
        'xo_total_wage': fields.float('Total Wage', digits=(16,2), required=True, help="Total Salary of the employee"),
        'wage': fields.float('Basic Wage', digits=(16,2), required=True, help="Basic Salary of the employee"),
        'xo_working_hours': fields.float('Working Hours'),
        'xo_hourly_rate': fields.float('Hourly Rate',digits=(16,2), help="Hourly Rate"),
        'xo_tm_required': fields.boolean('Timesheet Required'),
        'xo_allowance_rule_line_ids': fields.one2many('allowance.rule.line','contract_id','Rule Lines'),
        'xo_routing_code':fields.char('Routing Code'),
        'xo_mode_of_payment_id':fields.many2one('od.mode.of.payment',string='Mode Of Payment')

    }
    _defaults ={
                'company_id': _get_default_company,
                }



#Link Salary RUles to the Contract
class allowance_rule_line(osv.osv):
    _name = 'allowance.rule.line'
    _description = 'Contract Allowance Rule Line'


    def onchange_rule_type(self, cr, uid, ids,rule_type, context=None):
        res = {}
        if not rule_type:
            return res
        rule_obj=self.pool.get('hr.salary.rule').browse(cr, uid, rule_type,context)
        res = {'value':{'code':rule_obj.code or ''}}
        return res

    def _get_code(self, cr, uid, ids, field_name, arg=None, context=None):
        res ={}
        for rec in self.browse(cr, uid, ids, context):
            res[rec.id] = rec.rule_type.code or ''
        return res

    _columns = {
        'contract_id': fields.many2one('hr.contract','Contract ID',ondelete='cascade'),
        'rule_type' : fields.many2one('hr.salary.rule','Allowance Rule',help="this will get popullated based on the category Code in Salary Rule(code with ALW and DED must needed)"),
        'code': fields.function(_get_code, string='Code', type='char', size=10,store=True),
        #'code': fields.char('Code'),
        'amt': fields.float('Amount'),
    }

class hr_expense_expense(osv.osv):
    _inherit = 'hr.expense.expense'

    def expense_confirm(self, cr, uid, ids, context=None):
        proj_ids = []
        for expense in self.browse(cr, SUPERUSER_ID, ids):
            if expense.employee_id and expense.employee_id.parent_id.user_id:
                self.message_subscribe_users(cr, uid, [expense.id], user_ids=[expense.employee_id.parent_id.user_id.id])
            if expense.od_expense_type == 'opportunity':
                for line in expense.line_ids:
                    if not line.od_opp_id:
                        raise osv.except_osv(_('Error!'),_("You need to link your expense line to related Opportunity"))
            if expense.od_expense_type == 'project':
                if expense.sudo().employee_id.user_id.id == expense.od_prj_mngr.id and expense.company_id.id==6:
                    raise osv.except_osv(_('Error!'),_("Project Manager should be your Direct Manager in this Case."))
                for line in expense.line_ids:
                    if not line.analytic_account:
                        raise osv.except_osv(_('Error!'),_("You need to link your expense line to related Analytic Account"))
                    proj_ids.append(line.analytic_account.id)
                if len(set(proj_ids)) != 1:
                    raise osv.except_osv(_('Error!'),_("Expenses related to multiple projects should be submitted separately."))
                
                
        return self.write(cr, uid, ids, {'state': 'confirm', 'date_confirm': time.strftime('%Y-%m-%d'), 'date_log_history_line': [(0,0,{'name':'Expense Submitted for Approval','user_id': uid, 'date':str(datetime.now())})]},context=context)
    

class hr_payslip(osv.osv):
    _inherit = 'hr.payslip'
    #function overloaded for the front end date difference python code addition
    def get_payslip_lines(self, cr, uid, contract_ids, payslip_id, context):
        def _sum_salary_rule_category(localdict, category, amount):
            if category.parent_id:
                localdict = _sum_salary_rule_category(localdict, category.parent_id, amount)
            localdict['categories'].dict[category.code] = category.code in localdict['categories'].dict and localdict['categories'].dict[category.code] + amount or amount
            return localdict

        class BrowsableObject(object):
            def __init__(self, pool, cr, uid, employee_id, dict):
                self.pool = pool
                self.cr = cr
                self.uid = uid
                self.employee_id = employee_id
                self.dict = dict

            def __getattr__(self, attr):
                return attr in self.dict and self.dict.__getitem__(attr) or 0.0

        class InputLine(BrowsableObject):
            """a class that will be used into the python code, mainly for usability purposes"""
            def sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = datetime.now().strftime('%Y-%m-%d')
                result = 0.0
                self.cr.execute("SELECT sum(amount) as sum\
                            FROM hr_payslip as hp, hr_payslip_input as pi \
                            WHERE hp.employee_id = %s AND hp.state = 'done' \
                            AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pi.payslip_id AND pi.code = %s",
                           (self.employee_id, from_date, to_date, code))
                res = self.cr.fetchone()[0]
                return res or 0.0

        class WorkedDays(BrowsableObject):
            """a class that will be used into the python code, mainly for usability purposes"""
            def _sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = datetime.now().strftime('%Y-%m-%d')
                result = 0.0
                self.cr.execute("SELECT sum(number_of_days) as number_of_days, sum(number_of_hours) as number_of_hours\
                            FROM hr_payslip as hp, hr_payslip_worked_days as pi \
                            WHERE hp.employee_id = %s AND hp.state = 'done'\
                            AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pi.payslip_id AND pi.code = %s",
                           (self.employee_id, from_date, to_date, code))
                return self.cr.fetchone()

            def sum(self, code, from_date, to_date=None):
                res = self._sum(code, from_date, to_date)
                return res and res[0] or 0.0

            def sum_hours(self, code, from_date, to_date=None):
                res = self._sum(code, from_date, to_date)
                return res and res[1] or 0.0

        class Payslips(BrowsableObject):
            """a class that will be used into the python code, mainly for usability purposes"""

            def sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = datetime.now().strftime('%Y-%m-%d')
                self.cr.execute("SELECT sum(case when hp.credit_note = False then (pl.total) else (-pl.total) end)\
                            FROM hr_payslip as hp, hr_payslip_line as pl \
                            WHERE hp.employee_id = %s AND hp.state = 'done' \
                            AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pl.slip_id AND pl.code = %s",
                            (self.employee_id, from_date, to_date, code))
                res = self.cr.fetchone()
                return res and res[0] or 0.0
            #our function
            def days_between(self,date_from,date_to=None):
                if date_to is None:
                    date_to = datetime.now().strftime('%Y-%m-%d')
                start_date = datetime.strptime(date_from,"%Y-%m-%d")
                end_date = datetime.strptime(date_to,"%Y-%m-%d")
                od_nb_of_days = (end_date - start_date).days + 1
                return od_nb_of_days

        #we keep a dict with the result because a value can be overwritten by another rule with the same code
        result_dict = {}
        rules = {}
        categories_dict = {}
        blacklist = []
        payslip_obj = self.pool.get('hr.payslip')
        inputs_obj = self.pool.get('hr.payslip.worked_days')
        obj_rule = self.pool.get('hr.salary.rule')
        payslip = payslip_obj.browse(cr, uid, payslip_id, context=context)
        worked_days = {}
        for worked_days_line in payslip.worked_days_line_ids:
            worked_days[worked_days_line.code] = worked_days_line
        inputs = {}
        for input_line in payslip.input_line_ids:
            inputs[input_line.code] = input_line

        categories_obj = BrowsableObject(self.pool, cr, uid, payslip.employee_id.id, categories_dict)
        input_obj = InputLine(self.pool, cr, uid, payslip.employee_id.id, inputs)
        worked_days_obj = WorkedDays(self.pool, cr, uid, payslip.employee_id.id, worked_days)
        payslip_obj = Payslips(self.pool, cr, uid, payslip.employee_id.id, payslip)
        rules_obj = BrowsableObject(self.pool, cr, uid, payslip.employee_id.id, rules)

        baselocaldict = {'categories': categories_obj, 'rules': rules_obj, 'payslip': payslip_obj, 'worked_days': worked_days_obj, 'inputs': input_obj}
        #get the ids of the structures on the contracts and their parent id as well
        structure_ids = self.pool.get('hr.contract').get_all_structures(cr, uid, contract_ids, context=context)
        #get the rules of the structure and thier children
        rule_ids = self.pool.get('hr.payroll.structure').get_all_rules(cr, uid, structure_ids, context=context)
        #run the rules by sequence
        sorted_rule_ids = [id for id, sequence in sorted(rule_ids, key=lambda x:x[1])]

        for contract in self.pool.get('hr.contract').browse(cr, uid, contract_ids, context=context):
            employee = contract.employee_id
            localdict = dict(baselocaldict, employee=employee, contract=contract)
            for rule in obj_rule.browse(cr, uid, sorted_rule_ids, context=context):
                key = rule.code + '-' + str(contract.id)
                localdict['result'] = None
                localdict['result_qty'] = 1.0
                localdict['result_rate'] = 100
                #check if the rule can be applied
                if obj_rule.satisfy_condition(cr, uid, rule.id, localdict, context=context) and rule.id not in blacklist:
                    #compute the amount of the rule
                    amount, qty, rate = obj_rule.compute_rule(cr, uid, rule.id, localdict, context=context)
                    #check if there is already a rule computed with that code
                    previous_amount = rule.code in localdict and localdict[rule.code] or 0.0
                    #set/overwrite the amount computed for this rule in the localdict
                    tot_rule = amount * qty * rate / 100.0
                    localdict[rule.code] = tot_rule
                    rules[rule.code] = rule
                    #sum the amount for its salary category
                    localdict = _sum_salary_rule_category(localdict, rule.category_id, tot_rule - previous_amount)
                    #create/overwrite the rule in the temporary results
                    result_dict[key] = {
                        'salary_rule_id': rule.id,
                        'contract_id': contract.id,
                        'name': rule.name,
                        'code': rule.code,
                        'category_id': rule.category_id.id,
                        'sequence': rule.sequence,
                        'appears_on_payslip': rule.appears_on_payslip,
                        'condition_select': rule.condition_select,
                        'condition_python': rule.condition_python,
                        'condition_range': rule.condition_range,
                        'condition_range_min': rule.condition_range_min,
                        'condition_range_max': rule.condition_range_max,
                        'amount_select': rule.amount_select,
                        'amount_fix': rule.amount_fix,
                        'amount_python_compute': rule.amount_python_compute,
                        'amount_percentage': rule.amount_percentage,
                        'amount_percentage_base': rule.amount_percentage_base,
                        'register_id': rule.register_id.id,
                        'amount': amount,
                        'employee_id': contract.employee_id.id,
                        'quantity': qty,
                        'rate': rate,
                    }
                else:
                    #blacklist this rule and its children
                    blacklist += [id for id, seq in self.pool.get('hr.salary.rule')._recursive_search_of_rules(cr, uid, [rule], context=context)]

        result = [value for code, value in result_dict.items()]
        return result
    
    def strip_date(self, date):
        if len(date)>10:
            return date[:10]
        else:
            return date
    
    def get_last_legal_leave(self, cr, uid, employee_id, date_from, date_to, context=None):
        current_day = datetime.now().strftime('%Y-%m-%d')
        if current_day < date_to:
            # Not considering legal leave ending today
            date_to = datetime.now() - timedelta(days=1)
            date_to = date_to.strftime('%Y-%m-%d')
        holiday_ids = self.pool.get('hr.holidays').search(cr, uid, [('state','in',('validate', 'od_resumption_to_approve', 'od_approved')),('holiday_status_id','=',1),('employee_id','=',employee_id),('date_to','<=',date_to)],order="date_to desc",limit=1)        
        holiday_id = holiday_ids and holiday_ids[0] or False
        print holiday_id,"5"*88
        return  holiday_id
        
    def check_resumed(self, cr, uid, employee_id, last_legal_leave_id,date_from, date_to, context=None):
        holi_pool =self.pool.get('hr.holidays') 
        holi_obj = holi_pool.browse(cr,uid,last_legal_leave_id)
        state = holi_obj.state 
        return state in ('od_resumption_to_approve', 'od_approved')
    
    def od_days_between(self,d1, d2):
        d1 = self.strip_date(d1)
        d2 = self.strip_date(d2)
        from datetime import datetime
        d1 = datetime.strptime(d1, "%Y-%m-%d")
        d2 = datetime.strptime(d2, "%Y-%m-%d")
        return abs((d2 - d1).days)
    
    def od_days_between_1(self,d1, d2):
        d1 = self.strip_date(d1)
        d2 = self.strip_date(d2)
        from datetime import datetime
        d1 = datetime.strptime(d1, "%Y-%m-%d")
        d2 = datetime.strptime(d2, "%Y-%m-%d")
        return abs((d2 - d1).days)+1
    def od_get_holi(self,cr,uid,last_legal_leave_id,context=None):
        holi_pool =self.pool.get('hr.holidays')
        holi_obj = holi_pool.browse(cr,uid,last_legal_leave_id)
        return holi_obj
    
    def od_get_unresume_diff(self,cr, uid, holi_obj,date_from, date_to, context=None):
        leave_end_date = holi_obj.date_to
        unresume_diff = self.od_days_between_1(leave_end_date, date_to)
        return unresume_diff
    
    def get_unresumed_days(self, cr, uid, employee_id, date, context=None):
        unresumed_days = 0
        period_pool = self.pool.get('account.period')
        search_periods = period_pool.find(cr, uid, date, context=context) 
        od_period_id = search_periods[0]
        date_from = self.pool.get('account.period').browse(cr,uid,od_period_id,context).date_start
        date_to = self.pool.get('account.period').browse(cr,uid,od_period_id,context).date_stop
        
        last_legal_leave_id= self.get_last_legal_leave(cr, uid, employee_id,date_from, date_to, context)
        if last_legal_leave_id:
            check_resumed = self.check_resumed(cr, uid, employee_id,last_legal_leave_id, date_from, date_to, context)
            if check_resumed:
                
                holi_obj = self.od_get_holi(cr, uid, last_legal_leave_id, context)
                leave_end_date = holi_obj.date_to
                if date_from <= leave_end_date <= date_to:
                    resumption_date = holi_obj.od_resumption_date
                    days = self.od_days_between(leave_end_date, resumption_date)
                    if days:
                        days = days-1
                        unresumed_days = days
            else:
                holi_obj = self.od_get_holi(cr, uid, last_legal_leave_id, context)
                leave_end_date = holi_obj.date_to
                if date_from <= leave_end_date <= date_to:
                    unresume_diff = self.od_get_unresume_diff(cr, uid, holi_obj,date_from, date_to, context)
                    unresumed_days = unresume_diff -1
                else:
                    #this case must be, previous month legal leave not resumed, so we will deduct whole working days of this month, until they resume their previous legal leave
                    unresume_diff = self.od_days_between_1(date_from, date_to)
                    unresumed_days = unresume_diff
        
        return unresumed_days
        

    def get_worked_day_lines(self, cr, uid, contract_ids, date_from, date_to, context=None):
        period_pool = self.pool.get('account.period')
        search_periods = period_pool.find(cr, uid, date_to, context=context) 
        od_period_id = search_periods[0]
        od_start_date = self.pool.get('account.period').browse(cr,uid,od_period_id,context).date_start
        od_stop_date = self.pool.get('account.period').browse(cr,uid,od_period_id,context).date_stop
        parameter_obj = self.pool.get('ir.config_parameter')
        parameter_ids = parameter_obj.search(cr,uid,[('key', '=', 'od_def_leave_cut_off_days')])
        if not parameter_ids:
            raise osv.except_osv(_('Settings Warning!'),_('no cut off days\nPlz config it in System Parameters with od_def_leave_cut_off_days!'))
        parameter_data = parameter_obj.browse(cr,uid,parameter_ids)
        cut_days = int(parameter_data.value) or 0
        prev_month_cut_day = cut_days + 1

        date_f = self.pool.get('account.period').browse(cr,uid,od_period_id,context).date_stop
            
        new_end_date = date_f[:8] + str(cut_days)
        fist_day_of_current_date = date_f[:8] + str(1)
        xx = datetime.strptime(fist_day_of_current_date,"%Y-%m-%d") - timedelta(days=1)
        ss = xx.strftime('%Y-%m-%d')
        prev_date = ss[:8] + str(prev_month_cut_day)
        prev_date = prev_date + " 00:00:00"
        new_end_date = new_end_date + " 00:00:00"
        od_day_from = datetime.strptime(od_start_date,"%Y-%m-%d")
        od_day_to = datetime.strptime(od_stop_date,"%Y-%m-%d")
        if cut_days ==0:
            prev_date = od_day_from
            new_end_date = od_day_to

        od_nb_of_days = (od_day_to - od_day_from).days + 1
        """
        @param contract_ids: list of contract id
        @return: returns a list of dict containing the input that should be applied for the given contract between date_from and date_to
        """
        def was_on_leave(employee_id, datetime_day, context=None):
            res = False
            day = datetime_day.strftime("%Y-%m-%d")
            holiday_ids = self.pool.get('hr.holidays').search(cr, uid, [('state','in',('validate', 'od_resumption_to_approve', 'od_approved')),('employee_id','=',employee_id),('type','=','remove'),('date_from','<=',day),('date_to','>=',day)])
            if holiday_ids:
                res = self.pool.get('hr.holidays').browse(cr, uid, holiday_ids, context=context)[0].holiday_status_id.name
            return res

        res = []

        for contract in self.pool.get('hr.contract').browse(cr, uid, contract_ids, context=context):
            contract_start_date = contract.date_start
            if not contract.working_hours:
                #fill only if the contract as a working schedule linked
                continue
            attendances = {
                 'name': _("Normal Working Days paid at 100%"),
                 'sequence': 1,
                 'code': 'WORK100',
                 'number_of_days': 0.0,
                 'number_of_hours': 0.0,
                 'contract_id': contract.id,
            }
            
            
            leaves = {}
            day_from = datetime.strptime(date_from,"%Y-%m-%d")

            day_to = datetime.strptime(date_to,"%Y-%m-%d")
            nb_of_days = (day_to - day_from).days + 1
            working_hours_on_day = 0.0
            for day in range(0, nb_of_days):
                working_hours_on_day = self.pool.get('resource.calendar').working_hours_on_day(cr, uid, contract.working_hours, day_from + timedelta(days=day), context)
                if working_hours_on_day:
                    #the employee had to work
                    leave_type = was_on_leave(contract.employee_id.id, day_from + timedelta(days=day),context=context)
                    code = leave_type
                    if code and 'Unpaid' in code:
                        code = 'Unpaid'
                    if leave_type:
                        #if he was on leave, fill the leaves dict
                        if leave_type in leaves:
                            leaves[leave_type]['number_of_days'] += 1.0
                            leaves[leave_type]['number_of_hours'] += working_hours_on_day
                        else:
                            leaves[leave_type] = {
                                'name': leave_type,
                                'sequence': 5,
                                'code': code,
                                'number_of_days': 1.0,
                                'number_of_hours': working_hours_on_day,
                                'contract_id': contract.id,
                            }
                    else:
                        #add the input vals to tmp (increment if existing)
                        attendances['number_of_days'] += 1.0
                        attendances['number_of_hours'] += working_hours_on_day
                        
            unresumed_dict = {
                'name': _("Unresumed Days"),
                 'sequence': 1,
                 'code': 'UNRESUME',
                 'number_of_days': 0.0,
                 'number_of_hours': 0.0,
                 'contract_id': contract.id,
                }
            unresumed_days = self.get_unresumed_days(cr, uid, contract.employee_id.id, date_to, context)
            if unresumed_days:
                unresumed_dict['number_of_days'] = unresumed_days
                unresumed_dict['number_of_hours'] = unresumed_days*working_hours_on_day
                current_working_days = attendances['number_of_days'] - unresumed_days
                attendances['number_of_days'] = current_working_days
                attendances['number_of_hours'] = current_working_days*working_hours_on_day
                
            leaves = [value for key,value in leaves.items()]
            
            res += [attendances] + leaves
            if unresumed_days:
                res += [unresumed_dict]
                
            
        return res
#Orchid Start
#Check if have approved timelines for the employee
#Commented by Aslam
#             if contract.xo_tm_required:
#                 sheet_validate_obj = self.pool.get('hr_timesheet_sheet.sheet')
#                 sheet_ids = sheet_validate_obj.search(cr, uid,[('employee_id','=',contract.employee_id.id),('date_from','>=',prev_date),('date_to','<=',date_to),('state','=','done')])
#                 if sheet_ids:
#                     hours = sheet_validate_obj.browse(cr, uid, sheet_ids,context)[0]
#                     res[0]['number_of_hours'] = hours.total_timesheet
# 
# 
#         qry = "SELECT id from hr_holidays where state in ('validate','od_resumption_to_approve','od_approved') and date_to >='"+str(prev_date)+"' and date_to <='"+str(new_end_date)+"' and number_of_days_temp - floor(number_of_days_temp) >0 and employee_id ='"+str(contract.employee_id.id)+"';"
#         idss = cr.execute(qry)
#         holiday_ids = cr.fetchall()
#         holiday_ids_repeat_ids = []
#         total_holidays = 0
#         for res_values in res:
#             for holi in holiday_ids:
#                 holiday_ids_repeat_ids.append(holi[0])
#                 holiday_obj = self.pool.get('hr.holidays').browse(cr,uid,holi[0],context)
#                 leave_type = holiday_obj.holiday_status_id and holiday_obj.holiday_status_id.name
#                 number_of_days_temp = holiday_obj.number_of_days_temp
#                 total_holidays = total_holidays + number_of_days_temp
#                 
#     
#                 number_of_days_temp_int = math.floor(number_of_days_temp)
#                 if res_values['code'] == 'WORK100':
#                     res_values['number_of_days'] = res_values['number_of_days'] + (number_of_days_temp - number_of_days_temp_int)
# 
#                 if res_values['code'] == leave_type:
#                     if number_of_days_temp < 1:
#             
#                         res_values['number_of_days'] = res_values['number_of_days'] -1 + (number_of_days_temp - number_of_days_temp_int)
# 
#                     else:
#                         res_values['number_of_days'] = res_values['number_of_days']  - (number_of_days_temp - number_of_days_temp_int)
#             res_values['number_of_hours'] =  res_values['number_of_days'] * working_hours_on_day          

        



#old function before half day leave calculation
#    def get_worked_day_lines(self, cr, uid, contract_ids, date_from, date_to, context=None):
#        period_pool = self.pool.get('account.period')
#        search_periods = period_pool.find(cr, uid, date_to, context=context) 
#        od_period_id = search_periods[0]
#        od_start_date = self.pool.get('account.period').browse(cr,uid,od_period_id,context).date_start
#        od_stop_date = self.pool.get('account.period').browse(cr,uid,od_period_id,context).date_stop

#        od_day_from = datetime.strptime(od_start_date,"%Y-%m-%d")
#        od_day_to = datetime.strptime(od_stop_date,"%Y-%m-%d")
#        od_nb_of_days = (od_day_to - od_day_from).days + 1
#        """
#        @param contract_ids: list of contract id
#        @return: returns a list of dict containing the input that should be applied for the given contract between date_from and date_to
#        """
#        def was_on_leave(employee_id, datetime_day, context=None):
#            res = False
#            day = datetime_day.strftime("%Y-%m-%d")
#            holiday_ids = self.pool.get('hr.holidays').search(cr, uid, [('state','=','validate'),('employee_id','=',employee_id),('type','=','remove'),('date_from','<=',day),('date_to','>=',day)])
#            if holiday_ids:
#                res = self.pool.get('hr.holidays').browse(cr, uid, holiday_ids, context=context)[0].holiday_status_id.name
#            return res

#        res = []

#        for contract in self.pool.get('hr.contract').browse(cr, uid, contract_ids, context=context):
#            contract_start_date = contract.date_start
#            if not contract.working_hours:
#                #fill only if the contract as a working schedule linked
#                continue
#            attendances = {
#                 'name': _("Normal Working Days paid at 100%"),
#                 'sequence': 1,
#                 'code': 'WORK100',
#                 'number_of_days': 0.0,
#                 'number_of_hours': 0.0,
#                 'contract_id': contract.id,
#            }
#            leaves = {}
#            day_from = datetime.strptime(date_from,"%Y-%m-%d")

#            day_to = datetime.strptime(date_to,"%Y-%m-%d")
#            nb_of_days = (day_to - day_from).days + 1
#            for day in range(0, nb_of_days):
#                working_hours_on_day = self.pool.get('resource.calendar').working_hours_on_day(cr, uid, contract.working_hours, day_from + timedelta(days=day), context)
#                if working_hours_on_day:
#                    #the employee had to work
#                    leave_type = was_on_leave(contract.employee_id.id, day_from + timedelta(days=day),context=context)
#                    if leave_type:
#                        #if he was on leave, fill the leaves dict
#                        if leave_type in leaves:
#                            leaves[leave_type]['number_of_days'] += 1.0
#                            leaves[leave_type]['number_of_hours'] += working_hours_on_day
#                        else:
#                            leaves[leave_type] = {
#                                'name': leave_type,
#                                'sequence': 5,
#                                'code': leave_type,
#                                'number_of_days': 1.0,
#                                'number_of_hours': working_hours_on_day,
#                                'contract_id': contract.id,
#                            }
#                    else:
#                        #add the input vals to tmp (increment if existing)
#                        attendances['number_of_days'] += 1.0
#                        attendances['number_of_hours'] += working_hours_on_day
#            leaves = [value for key,value in leaves.items()]
#            
#            res += [attendances] + leaves
##Orchid Start
##Check if have approved timelines for the employee
#            if contract.xo_tm_required:
#                sheet_validate_obj = self.pool.get('hr_timesheet_sheet.sheet')
#                sheet_ids = sheet_validate_obj.search(cr, uid,[('employee_id','=',contract.employee_id.id),('date_from','>=',date_from),('date_to','<=',date_to),('state','=','done')])
#                if sheet_ids:
#                    hours = sheet_validate_obj.browse(cr, uid, sheet_ids,context)[0]
#                    res[0]['number_of_hours'] = hours.total_timesheet
#        return res















    def default_get(self, cr, uid, ids, context=None):
        res = super(hr_payslip, self).default_get(cr, uid, ids, context=context)
        vals = []
        if ids:
            parameter_obj = self.pool.get('ir.config_parameter')
            parameter_ids = parameter_obj.search(cr,uid,[('key', '=', 'od_def_leave_cut_off_days')])
            if not parameter_ids:
                raise osv.except_osv(_('Settings Warning!'),_('no cut off days\nPlz config it in System Parameters with od_def_leave_cut_off_days!'))
            parameter_data = parameter_obj.browse(cr,uid,parameter_ids)
            cut_days = int(parameter_data.value) or 0




            res.update({'od_cut_days': cut_days})
        return res








    def process_sheet(self, cr, uid, ids, context=None):
        move_pool = self.pool.get('account.move')
        period_pool = self.pool.get('account.period')
        #timenow = time.strftime('%Y-%m-%d')
        for slip in self.browse(cr, uid, ids, context=context):
            line_ids = []
            debit_sum = 0.0
            credit_sum = 0.0
            if not slip.period_id:
                ctx = dict(context or {}, account_period_prefer_normal=True)
                search_periods = period_pool.find(cr, uid, slip.date_to, context=ctx)
                period_id = search_periods[0]
            else:
                period_id = slip.period_id.id

            period_end_date = period_pool.browse(cr, uid, period_id,context=context)
            timenow = period_end_date.date_stop # the time is changed to the end date of the period to post the entry
            default_partner_id = slip.employee_id.address_home_id.id
            if not default_partner_id:
                raise osv.except_osv(_('Error!'),_("You need to set Home Address for Employee(%s)")%(slip.employee_id.name))
            name = _('Payslip of %s') % (slip.employee_id.name)
            move = {
                'narration': name,
                'date': timenow,
                'ref': slip.number,
                'journal_id': slip.journal_id.id,
                'period_id': period_id,
            }
            for line in slip.details_by_salary_rule_category:
                amt = slip.credit_note and -line.total or line.total
                partner_id = line.salary_rule_id.register_id.partner_id and line.salary_rule_id.register_id.partner_id.id or default_partner_id
                debit_account_id = line.salary_rule_id.account_debit.id
                credit_account_id = line.salary_rule_id.account_credit.id

                if debit_account_id:

                    debit_line = (0, 0, {
                    'name': line.name,
                    'date': timenow,
                   # 'partner_id': (line.salary_rule_id.register_id.partner_id or line.salary_rule_id.account_debit.type in ('receivable', 'payable')) and partner_id or False,
                    'partner_id': partner_id or False,
                    'account_id': debit_account_id,
                    'journal_id': slip.journal_id.id,
                    'period_id': period_id,
                    'debit': amt > 0.0 and amt or 0.0,
                    'credit': amt < 0.0 and -amt or 0.0,
                    'analytic_account_id': line.salary_rule_id.analytic_account_id and line.salary_rule_id.analytic_account_id.id or False,
                    'tax_code_id': line.salary_rule_id.account_tax_id and line.salary_rule_id.account_tax_id.id or False,
                    'tax_amount': line.salary_rule_id.account_tax_id and amt or 0.0,
                })
                    line_ids.append(debit_line)
                    debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']

                if credit_account_id:

                    credit_line = (0, 0, {
                    'name': line.name,
                    'date': timenow,
                    #'partner_id': (line.salary_rule_id.register_id.partner_id or line.salary_rule_id.account_credit.type in ('receivable', 'payable')) and partner_id or False,
                    'partner_id': partner_id or False,
                    'account_id': credit_account_id,
                    'journal_id': slip.journal_id.id,
                    'period_id': period_id,
                    'debit': amt < 0.0 and -amt or 0.0,
                    'credit': amt > 0.0 and amt or 0.0,
                    'analytic_account_id': line.salary_rule_id.analytic_account_id and line.salary_rule_id.analytic_account_id.id or False,
                    'tax_code_id': line.salary_rule_id.account_tax_id and line.salary_rule_id.account_tax_id.id or False,
                    'tax_amount': line.salary_rule_id.account_tax_id and amt or 0.0,
                })
                    line_ids.append(credit_line)
                    credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']

            if debit_sum > credit_sum:
                acc_id = slip.journal_id.default_credit_account_id.id
                if not acc_id:
                    raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Credit Account!')%(slip.journal_id.name))
                adjust_credit = (0, 0, {
                    'name': _('Adjustment Entry'),
                    'date': timenow,
                    'partner_id': False,
                    'account_id': acc_id,
                    'journal_id': slip.journal_id.id,
                    'period_id': period_id,
                    'debit': 0.0,
                    'credit': debit_sum - credit_sum,
                })
                line_ids.append(adjust_credit)

            elif debit_sum < credit_sum:
                acc_id = slip.journal_id.default_debit_account_id.id
                if not acc_id:
                    raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Debit Account!')%(slip.journal_id.name))
                adjust_debit = (0, 0, {
                    'name': _('Adjustment Entry'),
                    'date': timenow,
                    'partner_id': False,
                    'account_id': acc_id,
                    'journal_id': slip.journal_id.id,
                    'period_id': period_id,
                    'debit': credit_sum - debit_sum,
                    'credit': 0.0,
                })
                line_ids.append(adjust_debit)
            move.update({'line_id': line_ids})
            move_id = move_pool.create(cr, uid, move, context=context)
            self.write(cr, uid, [slip.id], {'move_id': move_id, 'period_id' : period_id}, context=context)
            if slip.journal_id.entry_posted:
                move_pool.post(cr, uid, [move_id], context=context)
        return self.write(cr, uid, ids, {'paid': True, 'state': 'done'}, context=context)


    def onchange_payslip_period(self, cr, uid, ids,employee_id, period_id, od_cut_days,context=None):
        
        if not employee_id or not period_id:
            return {}
        if od_cut_days < 0:
            raise osv.except_osv(_('Error!'),_('cut off days should not less than zero'))
        if od_cut_days == 0:   
            period_obj=self.pool.get('account.period').browse(cr, uid, period_id,context)
            period_start_date = period_obj.date_start #Start date in Period
            period_end_date = period_obj.date_stop  # end date of period

            contract_obj=self.pool.get('hr.contract')
            emp_obj=self.pool.get('hr.employee').browse(cr, uid, employee_id,context)

            contract_ids = contract_obj.search(cr, uid,[('employee_id','=',employee_id),('od_active','=',True)])
            if not contract_ids:
                contract_ids = contract_obj.search(cr, uid, [('employee_id', '=', employee_id), ('od_active', '=', False)], limit=1)
            #Commented by aslam to fix opening older payslips for deactivated employees
            # if len(contract_ids) >1 or not contract_ids:
            #     raise osv.except_osv(_('Error!'),_('Find NO/Multiple Active Contract For the Employee: (%s), Plz check the contract')%(emp_obj.name))
            contract_rec = contract_obj.browse(cr, uid, contract_ids,context)[0]
            contract_date_start = contract_rec.date_start # start date in Contract
            contract_date_end = contract_rec.date_end or period_end_date #end Date in Contract


            date_from = period_start_date
            date_to = period_end_date

            if contract_date_start > period_start_date:
                date_from = contract_date_start

            if contract_date_end < period_end_date:
                date_to = contract_date_end
            
            day_from = datetime.strptime(period_start_date,"%Y-%m-%d") 
            day_to = datetime.strptime(period_end_date,"%Y-%m-%d")
            nb_of_days_inperiod = (day_to - day_from).days + 1

            new_format = "%d-%m-%Y"
        
            d1= datetime.strptime(date_from,"%Y-%m-%d")
            d2= datetime.strptime(date_to,"%Y-%m-%d")

            msg='Pay slip from '+ d1.strftime(new_format)+' to '+d2.strftime(new_format)
            if date_from > date_to :
                msg = 'Contract Period Not Valid'
            return {'value':{'xo_total_no_of_days':nb_of_days_inperiod,'date_from':date_from,'date_to':date_to,'xo_msg':msg}}
        if od_cut_days > 0:
            if not employee_id or not period_id:
                return {}
            period_obj=self.pool.get('account.period').browse(cr, uid, period_id,context)

            date_f = period_obj.date_start
            
            new_end_date = date_f[:8] + str(od_cut_days)
            fist_day_of_current_date = date_f[:8] + str(1)
            xx = datetime.strptime(fist_day_of_current_date,"%Y-%m-%d") - timedelta(days=1)
            ss = xx.strftime('%Y-%m-%d')
            prev_date = ss[:8] + str(od_cut_days+1) 





            contract_obj=self.pool.get('hr.contract')
            emp_obj=self.pool.get('hr.employee').browse(cr, uid, employee_id,context)

            contract_ids = contract_obj.search(cr, uid,[('employee_id','=',employee_id),('od_active','=',True)])
            if len(contract_ids) >1 or not contract_ids:
                raise osv.except_osv(_('Error!'),_('Find NO/Multiple Active Contract For the Employee: (%s), Plz check the contract')%(emp_obj.name))
            contract_rec = contract_obj.browse(cr, uid, contract_ids,context)[0]
            contract_date_start = contract_rec.date_start # start date in Contract
            contract_date_end = contract_rec.date_end or new_end_date #end Date in Contract


            date_from = prev_date
            date_to = new_end_date

            if contract_date_start > prev_date:
                date_from = contract_date_start

            if contract_date_end < new_end_date:
                date_to = contract_date_end

            day_from = datetime.strptime(prev_date,"%Y-%m-%d") 
            day_to = datetime.strptime(new_end_date,"%Y-%m-%d")
            nb_of_days_inperiod = (day_to - day_from).days + 1
            new_format = "%d-%m-%Y"
        
            d1= datetime.strptime(date_from,"%Y-%m-%d")
            d2= datetime.strptime(date_to,"%Y-%m-%d")

            msg='Pay slip from '+ d1.strftime(new_format)+' to '+d2.strftime(new_format)
            if date_from > date_to :
                msg = 'Contract Period Not Valid'
            return {'value':{'xo_total_no_of_days':nb_of_days_inperiod,'date_from':date_from,'date_to':date_to,'xo_msg':msg}}

    def _get_msg(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for payslip in self.browse(cr, uid, ids, context=context):
            data= self.onchange_payslip_period(cr, uid, ids,payslip.employee_id.id,payslip.xo_period_id.id,0,context=context)
            if data.get('value'):
                res[payslip.id] = data['value']['xo_msg']
        return res

    def _od_generate_ot_details(self, cr, uid, ids, context=None):
        
        for payslip in self.browse(cr, uid, ids, context=context):
            employee_id = payslip.employee_id and payslip.employee_id.id 
            xo_period_id = payslip.xo_period_id and payslip.xo_period_id.id
            hr_over_time_line_obj = self.pool.get('od.hr.over.time.line')
            hr_over_time_line_ids = hr_over_time_line_obj.search(cr, uid, [('employee_id', '=', employee_id),('period_id','=',xo_period_id)])
            existing_hr_over_time_line_ids = hr_over_time_line_obj.search(cr, uid, [('payslip_id', '=', ids[0])])
            if existing_hr_over_time_line_ids:
                hr_over_time_line_obj.write(cr, uid,existing_hr_over_time_line_ids,{'payslip_id': ''},context=context)
            if hr_over_time_line_ids:
                hr_over_time_line_obj.write(cr, uid, hr_over_time_line_ids, {'payslip_id': ids[0]}, context=context)
        return True 
#For generating Loan Details in Employee Payslip Form
    def _od_generate_loan_details(self, cr, uid, ids, context=None):
        for payslip in self.browse(cr, uid, ids, context=context):
            employee_id = payslip.employee_id and payslip.employee_id.id 
            period_pool = self.pool.get('account.period')
            xo_period_id = payslip.xo_period_id and payslip.xo_period_id.id
            xo_period_data = period_pool.browse(cr, uid, xo_period_id, context=context)
            hr_loan_info_line_obj = self.pool.get('od.hr.loan.info.line')
            hr_loan_info_line_ids = hr_loan_info_line_obj.search(cr, uid, [('employee_id', '=', employee_id),('state','=','accepted')])

            if hr_loan_info_line_ids:
                for loan_info in hr_loan_info_line_obj.browse(cr, uid, hr_loan_info_line_ids, context=context):
                    date_value = loan_info.date_value
                    if date_value:
                        period_from_date_value = payslip.period_id
                        period_from_date_value = period_from_date_value.with_context().find(date_value)[:1]
                        if xo_period_id == period_from_date_value.id:
                            hr_loan_info_line_obj.write(cr, uid, loan_info.id, {'payslip_loan_id': ids[0]}, context=context)
        return True 



    def _od_generate_allowance_deduction_details(self, cr, uid, ids, context=None):
        for payslip in self.browse(cr, uid, ids, context=context):
            employee_id = payslip.employee_id and payslip.employee_id.id 
            xo_period_id = payslip.xo_period_id and payslip.xo_period_id.id
            payroll_transaction_line_obj = self.pool.get('od.payroll.transactions.line')
            payroll_transaction_line_ids = payroll_transaction_line_obj.search(cr, uid, [('employee_id', '=', employee_id),('state','=','accepted'),('period_id','=',xo_period_id)])
            payslip.od_hr_expense_loan_id.unlink()
            if payroll_transaction_line_ids:
                for obj in payroll_transaction_line_obj.browse(cr, uid, payroll_transaction_line_ids, context=context):
                    amount = 0
                    if not obj.product_id:
                        raise osv.except_osv(_('Settings Warning!'),_('put payroll item in payroll transaction line'))
                    rule_ids = self.pool.get('hr.salary.rule').search(cr,uid,[('od_product_id','=',obj.product_id.id)])
                    if not rule_ids:
                        raise osv.except_osv(_('Settings Warning!'),_('no salary rule defined for the particular payroll item'))
                    rule_id = rule_ids[0]
                    deduction = obj.deduction
                    allowance = obj.allowance
                    if deduction > 0:
                        amount = deduction
                    else:
                        amount = allowance
                    self.pool.get('od.hr.loan.info.line').create(cr,uid,{'amount':amount,'employee_id':employee_id,'rule_id':rule_id,'payslip_loan_id':payslip.id})
                         
     
        return True



   
    def compute_sheet(self, cr, uid, ids, context=None): 
        slip_line_pool = self.pool.get('hr.payslip.line')
        sequence_obj = self.pool.get('ir.sequence')
        self._od_generate_ot_details(cr, uid, ids,context=context)#calling _od_generate_ot_details
        self._od_generate_loan_details(cr, uid, ids,context=context)#calling _od_generate_loan_details
        self._od_generate_allowance_deduction_details(cr, uid, ids,context=context)#calling 
        for payslip in self.browse(cr, uid, ids, context=context):
            number = payslip.number or sequence_obj.get(cr, uid, 'salary.slip')
            #delete old payslip lines
            old_slipline_ids = slip_line_pool.search(cr, uid, [('slip_id', '=', payslip.id)], context=context)
#            old_slipline_ids
            if old_slipline_ids:
                slip_line_pool.unlink(cr, uid, old_slipline_ids, context=context)
            if payslip.contract_id:
                #set the list of contract for which the rules have to be applied
                contract_ids = [payslip.contract_id.id]
            else:
                #if we don't give the contract, then the rules to apply should be for all current contracts of the employee
                contract_ids = self.get_contract(cr, uid, payslip.employee_id, payslip.date_from, payslip.date_to, context=context)
            lines = [(0,0,line) for line in self.pool.get('hr.payslip').get_payslip_lines(cr, uid, contract_ids, payslip.id, context=context)]
            self.write(cr, uid, [payslip.id], {'line_ids': lines, 'number': number,}, context=context)
        return True


    _columns = {
        'xo_total_no_of_days': fields.integer('Total Number Of Days for payslip month'),
        'xo_period_id': fields.many2one('account.period', 'Payslip Period',states={'draft': [('readonly', False)]}, readonly=True, domain=[('state','<>','done'),('special','=',False)]),
        'xo_msg' : fields.function(_get_msg,string='Message',type='char'),

        'od_hr_over_time_line_id': fields.one2many('od.hr.over.time.line','payslip_id','Hr Over Time Line'),
        'od_hr_expense_loan_id': fields.one2many('od.hr.loan.info.line','payslip_loan_id','Hr Expense Loan Line'),
        'xo_mode_of_payment_id': fields.related('contract_id', 'xo_mode_of_payment_id',store=True,string='Mode Of Payment', type='many2one', relation='od.mode.of.payment'),
        'od_cut_days':fields.integer('Cut Off Days')
    }

class hr_payslip_run(osv.osv):
    _inherit = 'hr.payslip.run'
    
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id
    def onchange_xo_period(self, cr, uid, ids,xo_period_id,context=None):
        if xo_period_id:
            period_obj=self.pool.get('account.period').browse(cr, uid, xo_period_id,context)
            period_start_date = period_obj.date_start #Start date in Period
            period_end_date = period_obj.date_stop  # end date of period
            day_from = datetime.strptime(period_start_date,"%Y-%m-%d") 
            day_to = datetime.strptime(period_end_date,"%Y-%m-%d")
            nb_of_days_inperiod = (day_to - day_from).days + 1

            return {'value':{'date_start':period_start_date ,'date_end':period_end_date,'xo_total_no_of_days':nb_of_days_inperiod}}

            
        return {} 

    def default_get(self, cr, uid, ids, context=None):
        res = super(hr_payslip_run, self).default_get(cr, uid, ids, context=context)
        vals = []
        if ids:
            parameter_obj = self.pool.get('ir.config_parameter')
            parameter_ids = parameter_obj.search(cr,uid,[('key', '=', 'od_def_leave_cut_off_days')])
            if not parameter_ids:
                raise osv.except_osv(_('Settings Warning!'),_('no cut off days\nPlz config it in System Parameters with od_def_leave_cut_off_days!'))
            parameter_data = parameter_obj.browse(cr,uid,parameter_ids)
            cut_days = int(parameter_data.value) or 0




            res.update({'od_cut_days': cut_days})
        return res
    _columns = {
        'company_id': fields.many2one('res.company','Company'),
        'xo_period_id': fields.many2one('account.period', 'Payslip Period', domain=[('state','<>','done'),('special','=',False)]),
        'xo_total_no_of_days': fields.integer('Total Number Of Days for payslip month'),
        'od_cut_days':fields.integer('Cut Off Days')
    }
    _defaults ={
                'company_id': _get_default_company,
                }



