#-*- coding:utf-8 -*-
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import datetime
from datetime import timedelta
from openerp import SUPERUSER_ID
import math
class hr_payslip_run(osv.osv):
    _inherit = 'hr.payslip.run'

    def unlink(self, cr, uid, ids, context=None): 
        pat_batch_obj = self.browse(cr,uid,ids,context)
        if pat_batch_obj.state != 'draft':
            raise osv.except_osv(_('Invalid Action!'), _('You cannot Delete it,it is not in draft state')) 
        unlink_ids = []   
        for line in pat_batch_obj.slip_ids:
            if line.state == 'draft':
                unlink_ids.append(line.id)
                
        if unlink_ids:
            self.pool.get('hr.payslip').unlink(cr, uid, unlink_ids,context)
            
   
        return osv.osv.unlink(self, cr, uid, ids, context=context)



class hr_payslip(osv.osv):
    _inherit = 'hr.payslip'



    def _od_generate_late_hour_details(self, cr, uid, ids, context=None):
        
        for payslip in self.browse(cr, uid, ids, context=context):
            considering_ids = []
            details = {}
            hour = 0
            employee_id = payslip.employee_id and payslip.employee_id.id 
            
            xo_period_id = payslip.xo_period_id and payslip.xo_period_id.id
            hr_over_time_line_obj = self.pool.get('od.late.hour.line')
            hr_over_time_line_ids = hr_over_time_line_obj.search(cr, uid, [('employee_id', '=', employee_id),('period_id','=',xo_period_id)])
            if hr_over_time_line_ids:
                for late_id in hr_over_time_line_ids:
                    lateline_obj = self.pool.get('od.late.hour.line').browse(cr,uid,late_id,context)
                    if lateline_obj.hr_late_hour_id.state == 'approved':
                        considering_ids.append(lateline_obj.id)
                        details[lateline_obj.employee_id.id] = (lateline_obj.employee_id.id not in details) \
                                                             and lateline_obj.late_hour or (float(details.get(lateline_obj.employee_id.id))+lateline_obj.late_hour)
                        
                        
            if details:
                for value in details:
                    hour = details[employee_id]


            
            existing_hr_over_time_line_ids = hr_over_time_line_obj.search(cr, uid, [('payslip_id', '=', ids[0])])
            if existing_hr_over_time_line_ids:
                hr_over_time_line_obj.write(cr, uid,existing_hr_over_time_line_ids,{'payslip_id': False},context=context)
            parameter_obj = self.pool.get('ir.config_parameter')
            late_hour_rule = parameter_obj.search(cr,uid,[('key', '=', 'def_late_hour_rule')])
            if not late_hour_rule:
                raise osv.except_osv(_('Settings Warning!'),_('No salary rule defined for late hours\nset in System Parameters with def_late_hour_rule!'))
            company_param =parameter_obj.browse(cr,uid,late_hour_rule)
            rule_id = company_param.od_model_id and company_param.od_model_id.id or False

            if hour > 0:
                self.pool.get('od.late.hour.line').create(cr,uid,{'payslip_id':ids[0],'late_hour':hour,'late_time_type':rule_id,'employee_id':employee_id})
                
#            if hr_over_time_line_ids:
#                hr_over_time_line_obj.write(cr, uid, hr_over_time_line_ids, {'payslip_id': ids[0]}, context=context)
        return True 

    def _od_generate_ot_details(self, cr, uid, ids, context=None):
        
        for payslip in self.browse(cr, uid, ids, context=context):
            considering_ids = []
            employee_id = payslip.employee_id and payslip.employee_id.id 
            xo_period_id = payslip.xo_period_id and payslip.xo_period_id.id
            hr_over_time_line_obj = self.pool.get('od.hr.over.time.line')
            hr_over_time_line_ids = hr_over_time_line_obj.search(cr, uid, [('employee_id', '=', employee_id),('period_id','=',xo_period_id)])
            if hr_over_time_line_ids:
                for ot_id in hr_over_time_line_ids:
                    ot_line_obj = self.pool.get('od.hr.over.time.line').browse(cr,uid,ot_id,context)
                    if ot_line_obj.hr_over_time_id.state == 'confirm':
                        considering_ids.append(ot_line_obj.id)


            existing_hr_over_time_line_ids = hr_over_time_line_obj.search(cr, uid, [('payslip_id', '=', ids[0])])
            if existing_hr_over_time_line_ids:
                hr_over_time_line_obj.write(cr, uid,existing_hr_over_time_line_ids,{'payslip_id': False},context=context)
            if considering_ids:
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
            print employee_id,xo_period_id
            payroll_transaction_line_ids = payroll_transaction_line_obj.search(cr, uid, [('employee_id', '=', employee_id),('state','=','accepted'),('period_id','=',xo_period_id)])
            print payroll_transaction_line_ids
            payslip.od_hr_expense_loan_id.unlink()
            if payroll_transaction_line_ids:
                for obj in payroll_transaction_line_obj.browse(cr, uid, payroll_transaction_line_ids, context=context):
                    amount = 0
                    if not obj.product_id:
                        raise osv.except_osv(_('Settings Warning!'),_('put payroll item in payroll transaction line'))
                    rule_ids = self.pool.get('hr.salary.rule').search(cr,uid,[('od_product_id','=',obj.product_id.id)])
                    
                    if not rule_ids:
                        raise osv.except_osv(_('Settings Warning!'),_('no salary rule defined for the particular payroll item by the product  %s'%str(obj.product_id.name)))
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
        self._od_generate_late_hour_details(cr, uid, ids,context=context)#calling
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

        'od_hr_late_time_line': fields.one2many('od.late.hour.line','payslip_id','Hr Late Time Line'),
    }


