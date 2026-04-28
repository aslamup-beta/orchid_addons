# -*- coding: utf-8 -*-
from datetime import datetime,date
from datetime import timedelta
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import openerp.addons.decimal_precision as dp
from openerp import workflow
from openerp import SUPERUSER_ID
import string
from datetime import date
import dateutil.relativedelta 

class hr_payslip_run(osv.osv):
    _inherit = 'hr.payslip.run'


    def unlink(self, cr, uid, ids, context=None):
        for payslip_batch in self.browse(cr, uid, ids, context=context):
            if payslip_batch.state != 'draft':
                raise osv.except_osv(_('Warning!'),_('You cannot delete a payslip which is not in draft state'))
            payslips = self.pool.get('hr.payslip').search(cr,uid,[('payslip_run_id', '=', payslip_batch.id)])
            self.pool.get('hr.payslip').unlink(cr,uid,payslips,context)
        return super(hr_payslip_run, self).unlink(cr, uid, ids, context)



class hr_employee(osv.osv):
    _inherit = "hr.employee"
    _columns ={
                'od_leave_history_line':fields.one2many('hr.holidays', 'employee_id', string='History Lines',domain=[('od_year','not in',('2011','2012','2013','2014'))])
               }
   
    
    def od_generate_gratuity_value(self,cr,uid,ids,context=None):
        experiance = 0
        experiance_days = 0
        one_day_wage =0
        gratuvity = 0
        
        parameter_obj = self.pool.get('ir.config_parameter')
#company parameter
        company_param_id = parameter_obj.search(cr,uid,[('key', '=', 'od_beta_saudi_co')])
        if not company_param_id:
            raise osv.except_osv(_('Settings Warning!'),_('No Company Parameter Not defined\nconfig it in System Parameters with od_beta_saudi_co!'))
        company_param =parameter_obj.browse(cr,uid,company_param_id)
        saudi_company_id = company_param.od_model_id and company_param.od_model_id.id or False
        for obj in self.browse(cr,uid,ids,context):
            employee_id = obj.id
            emp_comp_id = obj.company_id and obj.company_id
            od_terminated = obj.od_terminated
            od_limited = False
            od_gratuity_date = obj.od_gratuity_date
            if not od_gratuity_date:
                raise Warning(_("pls provide date"))
            joining_date = str(datetime.strptime(str(obj.od_joining_date), "%Y-%m-%d"))
            od_gratuity_date = str(datetime.strptime(str(od_gratuity_date), "%Y-%m-%d")) 


#####unpaid leave calculation search crieteria joining date to gratuvity date
            unpaid_leave_ids = self.pool.get('hr.holidays').search(cr,uid,[('employee_id', '=', employee_id), ('holiday_status_id', '=', 4),('state', 'not in', ('cancel','refuse')),('date_from','<',str(od_gratuity_date)),('date_from','>',joining_date)])
            total_unpaid_leaves = 0
            if unpaid_leave_ids:
                for lv in unpaid_leave_ids:
                    for levs in self.pool.get('hr.holidays').browse(cr,uid,lv,context=context):
                        total_unpaid_leaves += levs.number_of_days_temp

#############------------un paid leaves finish here ##############
                
            contract_ids = self.pool.get('hr.contract').search(cr,uid,[('employee_id','=',employee_id),('od_active','=',True)])
            if contract_ids:
                contract_ids = contract_ids[0]
                contract_obj = self.pool.get('hr.contract').browse(cr,uid,contract_ids,context)
                od_limited = contract_obj.od_limited
#    old            one_day_wage = float(contract_obj.wage * 12) / 365.00  contract.wage/ 30 
                one_day_wage = float((contract_obj.wage) / 30)
                


#                
                experiance = float(((datetime.strptime(od_gratuity_date, '%Y-%m-%d %H:%M:%S') -  datetime.strptime(joining_date, '%Y-%m-%d %H:%M:%S')).days) - total_unpaid_leaves) /365.00  #Experiance in year

                experiance_days = float(((datetime.strptime(od_gratuity_date, '%Y-%m-%d %H:%M:%S') -  datetime.strptime(joining_date, '%Y-%m-%d %H:%M:%S')).days) - total_unpaid_leaves)  #Experiance in days
            else:
                raise Warning(_("pls define active contract for the employee"))

            if emp_comp_id == saudi_company_id:
##################################################case1
                if od_limited and od_terminated ==False:
                    if experiance <5:
                        gratuvity = 0
                    if experiance >5:
                        extra_year = experiance - 5
                        extra_year_in_days = extra_year * 365
                        gratuvity = ((21 * one_day_wage)*5) + (((one_day_wage *30) /365) * extra_year_in_days)
    
    
    #########################################################case2
    
                if od_limited and od_terminated:
                    if experiance <1:
                        gratuvity = 0
    
                    if experiance >1 and experiance <5:
                        gratuvity = (((21 * one_day_wage)/365.0) * experiance_days)
    
                    if experiance >5:
                        extra_year = experiance - 5
                        extra_year_in_days = extra_year * 365
                        gratuvity = ((21 * one_day_wage)*5) + (((one_day_wage *30) /365) * extra_year_in_days)
    
    #############################################################case3
    
                if od_limited==False and od_terminated ==False:
                    if experiance <1:
                        gratuvity = 0
    
                    if experiance >1 and experiance <3:
                        gratuvity = (((7 * one_day_wage)/365.0) * experiance_days)
    
                    if experiance >3 and experiance <5:
                        gratuvity = (((14 * one_day_wage)/365.0) * experiance_days)
    
                    if experiance >5:
                        extra_year = experiance - 5
                        extra_year_in_days = extra_year * 365
                        gratuvity = ((21 * one_day_wage)*5) + (((one_day_wage *30) /365) * extra_year_in_days)
    
    
    ##################################################################case4
    
    
    
    
                if od_limited==False and od_terminated:
                    if experiance <1:
                        gratuvity = 0
    
                    if experiance >1 and experiance <5:
                        gratuvity = (((21 * one_day_wage)/365.0) * experiance_days)
    
                    
    
                    if experiance >5:
                        extra_year = experiance - 5
                        extra_year_in_days = extra_year * 365
                        gratuvity = ((21 * one_day_wage)*5) + (((one_day_wage *30) /365) * extra_year_in_days)


            else:
                if (not od_terminated) and experiance<2:
                    gratuvity = 0
                if experiance >=2 and experiance <5 and not od_terminated:
                    gratuvity = (((5 * one_day_wage)/365.0) * experiance_days)
                if experiance >=5 and experiance <10 and not od_terminated:
                    extra_year = experiance - 5
                    extra_year_in_days = extra_year * 365
                    gratuvity = ((10 * one_day_wage)*5) + (((one_day_wage *20) /365) * extra_year_in_days)
                if (not od_terminated) and experiance>=10:
                    extra_year = experiance - 5
                    extra_year_in_days = extra_year * 365
                    gratuvity = ((15 * one_day_wage)*5) + (((one_day_wage *30) /365) * extra_year_in_days)
                if od_terminated and experiance<5:  
                    gratuvity = (((15 * one_day_wage)/365.0) * experiance_days)
                if experiance >=5  and od_terminated:
                    extra_year = experiance - 5
                    extra_year_in_days = extra_year * 365
                    gratuvity = ((15 * one_day_wage)*5) + (((one_day_wage *30) /365) * extra_year_in_days)
            
            self.pool.get('hr.employee').write(cr,uid,[obj.id],{'od_gratuity':gratuvity},context=context)

               
        return True




    def od_generate_leave_salary(self,cr,uid,ids,context=None):
#        date_from = datetime.now().strftime('%Y-%m-%d 00:00:00')
        le = 0
        leav = 0
        od_total_leave_eligible = 0
        
        emp_obj = self.browse(cr,uid,ids)
        emp_comp_id  = emp_obj.company_id and emp_obj.company_id.id
        
        parameter_obj = self.pool.get('ir.config_parameter')
        #company parameter
        company_param_id = parameter_obj.search(cr,uid,[('key', '=', 'od_beta_saudi_co')])
        if not company_param_id:
            raise osv.except_osv(_('Settings Warning!'),_('No Company Parameter Not defined\nconfig it in System Parameters with od_beta_saudi_co!'))
        company_param =parameter_obj.browse(cr,uid,company_param_id)
        saudi_company_id = company_param.od_model_id and company_param.od_model_id.id or False
        
        year_start_date = str(datetime.strptime(str(date(date.today().year, 1, 1)), "%Y-%m-%d")) 
        year_end_date = str(datetime.strptime(str(date(date.today().year+1, 01, 01)), "%Y-%m-%d"))
        od_joining_date = ''
        leave_request_date = ''   
        employee_id = self.browse(cr,uid,ids[0],context) and self.browse(cr,uid,ids[0],context).id  
        
        od_based_on_basic = self.browse(cr,uid,ids[0],context).od_based_on_basic
#        leave_request_date = str(datetime.strptime(str(date_from), '%Y-%m-%d %H:%M:%S'))
        for obj in self.browse(cr,uid,ids,context):
            od_joining_date = obj.od_joining_date
            leave_request_date = obj.od_leave_salary_date
        if not leave_request_date:
            raise osv.except_osv(_('warning!'), _('pls provide leave requested date'))
        leave_request_date = str(datetime.strptime(leave_request_date, '%Y-%m-%d'))
        if not od_joining_date:
            raise osv.except_osv(_('Settings Warning!'),_('joining_date not provided'))
        od_joining_date = datetime.strptime(od_joining_date, "%Y-%m-%d")
#total days
        total_days = (datetime.strptime(str(leave_request_date), '%Y-%m-%d %H:%M:%S') - datetime.strptime(str(od_joining_date), '%Y-%m-%d %H:%M:%S')).days 
# total_unpaid_leaves 

        leave_unpaid_ids = self.pool.get('hr.holidays').search(cr,uid,[('employee_id', '=', employee_id), ('holiday_status_id', '=', 4),('state', 'not in', ('cancel','refuse'))])   
        total_unpaid_leaves = 0
        if leave_unpaid_ids:
            for obje in leave_unpaid_ids:
                for alloc in self.pool.get('hr.holidays').browse(cr,uid,obje,context=context):
                        total_unpaid_leaves += alloc.number_of_days
#total_worked_days
        total_worked_days = total_days + total_unpaid_leaves

#allowed leave taking from parameter
#        parameter_obj = self.pool.get('ir.config_parameter')
#        parameter_ids = parameter_obj.search(cr,uid,[('key', '=', 'def_leaves_year')])
#        if not parameter_ids:
#            raise osv.except_osv(_('Settings Warning!'),_('No allocated leave defined\nconfig it in System Parameters with def_leaves_year!'))
#        parameter_data = parameter_obj.browse(cr,uid,parameter_ids)
#        allocated_leave = parameter_data.value
#taking number of working days in parameter values

        parameter_obj = self.pool.get('ir.config_parameter')
        parameter_ids = parameter_obj.search(cr,uid,[('key', '=', 'def_wrk_days_year')])
        if not parameter_ids:
            raise osv.except_osv(_('Settings Warning!'),_('config work days,def_wrk_days_year'))
        parameter_data = parameter_obj.browse(cr,uid,parameter_ids)
        working_days_year = float(parameter_data.value)









#calculating leave_allowed_now
#        leave_allowed_now = float(float(allocated_leave)/float(working_days_year)) * total_worked_days

#calculating current year legal leaves taken
        legal_leaves_current_year_ids = self.pool.get('hr.holidays').search(cr,uid,[('employee_id', '=', employee_id), ('holiday_status_id', '=', 1),('state', 'not in', ('cancel','refuse'))]) 
        total_legal_leaves_in_current_year =0
        if legal_leaves_current_year_ids:
            for objec in legal_leaves_current_year_ids:
                for allocs in self.pool.get('hr.holidays').browse(cr,uid,objec,context=context):
                        total_legal_leaves_in_current_year += allocs.number_of_days


#calculating the no_of_pending_leaves(original value)     
#        no_of_pending_leaves = round((leave_allowed_now + total_legal_leaves_in_current_year),2)
#        print ">>>>>>>>>>>>>>>>>-----------------------------------------------no_of_pending_leaves",no_of_pending_leaves
        
        contract_id = self.pool.get('hr.contract').search(cr,uid,[('employee_id', '=', employee_id),('od_active','=',True)])
        if not contract_id:
            raise osv.except_osv(_('Settings Warning!'),_('employee have no active contract'))
            
        if contract_id:
            contract_id = contract_id[0]
        contract_obj = self.pool.get('hr.contract').browse(cr,uid,contract_id,context)
        type_id = contract_obj.type_id and contract_obj.type_id.id

#        leave_taken_upto_current_date = 0
#        leave_ids_for_current_date = self.pool.get('hr.holidays').search(cr,uid,[('employee_id', '=', employee_id), ('holiday_status_id', '=', 1),('state', 'in', ('validate','od_resumption_to_approve','od_approved')),('date_from','<',str(leave_request_date)),('date_from','>',year_start_date)])
#        if leave_ids_for_current_date:
#            for lv in leave_ids_for_current_date:
#                for levs in self.pool.get('hr.holidays').browse(cr,uid,lv,context=context):
#                    leave_taken_upto_current_date += levs.number_of_days_temp
#        print "LLLLLLLLLLLLLLLLLLL",leave_taken_upto_current_date
#        print "?????????????????????????????????????????????????????????????????",contract_obj.wage
#        print "?????????????????????????????????????????????????????????????????",contract_obj.xo_total_wage
#        if od_based_on_basic:
#            leav = no_of_pending_leaves * contract_obj.wage
#        else:
#            leav = no_of_pending_leaves * contract_obj.xo_total_wage
            
        
            
            
        
#        self.pool.get('hr.employee').write(cr,uid,ids[0],{'od_original_leave_eligible':no_of_pending_leaves},context=context)
        if not (total_days < working_days_year):
        


#  TL= { [(Joining Date   - Given Date)- total unpaid Leave]* (LE/365)] - (Leagel leave till Given Date { State Not in (Cancel, reject) } 



       
            if type_id == 4:
                if emp_comp_id == saudi_company_id:
                    od_total_leave_eligible = (total_worked_days * float(float(21)/float(365)))
                else:   
                    od_total_leave_eligible = (total_worked_days * float(float(60)/float(365)))
                no_of_pending_leaves = od_total_leave_eligible + total_legal_leaves_in_current_year

#                if le < no_of_pending_leaves:
#                    no_of_pending_leaves = le
                
#                le = 60-leave_taken_upto_current_date
#                if le < no_of_pending_leaves:
#                    no_of_pending_leaves = le
#                    
#                else:
#                    no_of_pending_leaves = no_of_pending_leaves
                    
                    
                
            if type_id == 5:
                no_of_pending_leaves = 0
            if type_id not in (4,5):
                od_total_leave_eligible = (total_worked_days * float(float(30)/float(365)))
                no_of_pending_leaves = od_total_leave_eligible + total_legal_leaves_in_current_year






#                print "::::::::::::::::::::::::::::::::::::::::::::::::::::haioooooooooooooooooooo11111111111111111"
#                le = 30-leave_taken_upto_current_date
#                if le < no_of_pending_leaves:
#                    no_of_pending_leaves = le
#                    
#                else:
#                    no_of_pending_leaves = no_of_pending_leaves
            if od_based_on_basic:
                leav = no_of_pending_leaves * ((contract_obj.wage * 12)/365)
            else:
                leav = no_of_pending_leaves * ((contract_obj.xo_total_wage * 12)/365)
           
            
            self.pool.get('hr.employee').write(cr,uid,ids[0],{'od_leaves':no_of_pending_leaves,'od_leave_salary':leav},context=context)
        else:  
            if od_based_on_basic:
                leav = no_of_pending_leaves * ((contract_obj.wage * 12)/365)
            else:
                leav = no_of_pending_leaves * ((contract_obj.xo_total_wage * 12)/365)

            self.pool.get('hr.employee').write(cr,uid,ids[0],{'od_leaves':0,'od_leave_salary':leav},context=context)
            
        return True




    def compute_leave_eligible_employee_master(self,cr,uid,ids,context=None):
#dates
        date_from = datetime.now().strftime('%Y-%m-%d 00:00:00')
        le = 0
        parameter_obj = self.pool.get('ir.config_parameter')
        emp_obj = self.browse(cr,uid,ids)
        emp_comp_id  = emp_obj.company_id and emp_obj.company_id.id
        year_start_date = str(datetime.strptime(str(date(date.today().year, 1, 1)), "%Y-%m-%d")) 
        year_end_date = str(datetime.strptime(str(date(date.today().year+1, 01, 01)), "%Y-%m-%d"))
        od_joining_date = ''   
        employee_id = self.browse(cr,uid,ids[0],context) and self.browse(cr,uid,ids[0],context).id  
        leave_request_date = str(datetime.strptime(str(date_from), '%Y-%m-%d %H:%M:%S'))
        
        #company parameter
        company_param_id = parameter_obj.search(cr,uid,[('key', '=', 'od_beta_saudi_co')])
        if not company_param_id:
            raise osv.except_osv(_('Settings Warning!'),_('No Company Parameter Not defined\nconfig it in System Parameters with od_beta_saudi_co!'))
        company_param =parameter_obj.browse(cr,uid,company_param_id)
        saudi_company_id = company_param.od_model_id and company_param.od_model_id.id or False
        
        
        contract_id = self.pool.get('hr.contract').search(cr,uid,[('employee_id', '=', employee_id),('od_active','=',True)])
        if not contract_id:
            raise osv.except_osv(_('Settings Warning!'),_('employee have no active contract'))
            
        if contract_id:
            contract_id = contract_id[0]
        contract_obj = self.pool.get('hr.contract').browse(cr,uid,contract_id,context)
        type_id = contract_obj.type_id and contract_obj.type_id.id
        
        
        
        for obj in self.browse(cr,uid,ids,context):
            od_joining_date = obj.od_joining_date
        if not od_joining_date:
            raise osv.except_osv(_('Settings Warning!'),_('joining_date not provided'))
        od_joining_date = datetime.strptime(od_joining_date, "%Y-%m-%d")
#total days
        total_days = (datetime.strptime(str(leave_request_date), '%Y-%m-%d %H:%M:%S') - datetime.strptime(str(od_joining_date), '%Y-%m-%d %H:%M:%S')).days 
# total_unpaid_leaves 

        leave_unpaid_ids = self.pool.get('hr.holidays').search(cr,uid,[('employee_id', '=', employee_id), ('holiday_status_id', '=', 4),('state', 'not in', ('cancel','refuse'))])   
        total_unpaid_leaves = 0
        if leave_unpaid_ids:
            for obje in leave_unpaid_ids:
                for alloc in self.pool.get('hr.holidays').browse(cr,uid,obje,context=context):
                        total_unpaid_leaves += alloc.number_of_days
#total_worked_days
        total_worked_days = total_days + total_unpaid_leaves

#allowed leave taking from parameter
        
        parameter_ids = parameter_obj.search(cr,uid,[('key', '=', 'def_leaves_year')])
        if not parameter_ids:
            raise osv.except_osv(_('Settings Warning!'),_('No allocated leave defined\nconfig it in System Parameters with def_leaves_year!'))
        parameter_data = parameter_obj.browse(cr,uid,parameter_ids)
        allocated_leave = parameter_data.value
        if emp_comp_id == saudi_company_id and type_id ==  4:
            parameter_ids = parameter_obj.search(cr,uid,[('key', '=', 'def_leaves_year_saudi_labour')])
            if not parameter_ids:
                raise osv.except_osv(_('Settings Warning!'),_('No allocated leave defined\nconfig it in System Parameters with def_leaves_year_saudi_labour!'))
            parameter_data = parameter_obj.browse(cr,uid,parameter_ids)
            allocated_leave = parameter_data.value
#taking number of working days in parameter values

        parameter_obj = self.pool.get('ir.config_parameter')
        parameter_ids = parameter_obj.search(cr,uid,[('key', '=', 'def_wrk_days_year')])
        if not parameter_ids:
            raise osv.except_osv(_('Settings Warning!'),_('config work days,def_wrk_days_year'))
        parameter_data = parameter_obj.browse(cr,uid,parameter_ids)
        working_days_year = float(parameter_data.value)









#calculating leave_allowed_now
        leave_allowed_now = float(float(allocated_leave)/float(working_days_year)) * total_worked_days
       
#calculating current year legal leaves taken
        legal_leaves_current_year_ids = self.pool.get('hr.holidays').search(cr,uid,[('employee_id', '=', employee_id), ('holiday_status_id', '=', 1),('state', 'not in', ('cancel','refuse'))]) 
        total_legal_leaves_in_current_year =0
        if legal_leaves_current_year_ids:
            for objec in legal_leaves_current_year_ids:
                for allocs in self.pool.get('hr.holidays').browse(cr,uid,objec,context=context):
                        total_legal_leaves_in_current_year += allocs.number_of_days


#calculating the no_of_pending_leaves(original value)     
        no_of_pending_leaves = round((leave_allowed_now + total_legal_leaves_in_current_year),2)
        
        leave_taken_upto_current_date = 0
        
        old_str =leave_request_date[5:10]
        leave_request_date = string.replace(leave_request_date, old_str, '12-31')
      
       
        leave_ids_for_current_date = self.pool.get('hr.holidays').search(cr,uid,[('employee_id', '=', employee_id), ('holiday_status_id', '=', 1),('state', 'not in', ('cancel','refuse')),('date_from','<',str(leave_request_date)),('date_from','>',year_start_date)])
        if leave_ids_for_current_date:
            for lv in leave_ids_for_current_date:
                for levs in self.pool.get('hr.holidays').browse(cr,uid,lv,context=context):
                    leave_taken_upto_current_date += levs.number_of_days_temp
        
      
            
        
#         self.pool.get('hr.employee').write(cr,uid,ids[0],{'od_original_leave_eligible':no_of_pending_leaves},context=context)
        if not (total_days < working_days_year):
        
            if type_id == 4:
                
                if emp_comp_id == saudi_company_id:
                    le = 30-leave_taken_upto_current_date
                else:
                    le = 60-leave_taken_upto_current_date
                if le < no_of_pending_leaves:
                    no_of_pending_leaves = le
                    
                else:
                    no_of_pending_leaves = no_of_pending_leaves
                    
                    
                
            if type_id == 5:
                no_of_pending_leaves = 0
            if type_id not in (4,5):
                le = 30-leave_taken_upto_current_date
                if le < no_of_pending_leaves:
                    no_of_pending_leaves = le
                    
                else:
                    no_of_pending_leaves = no_of_pending_leaves
           
            raise osv.except_osv(_('Leave Eligible'),_('Eligible Leave are : ' + str(no_of_pending_leaves) ))
#             self.pool.get('hr.employee').write(cr,uid,ids[0],{'od_leave_eligible':no_of_pending_leaves},context=context)
        else:  
            raise osv.except_osv(_('Leave Eligible'),_('Eligible Leave are : 0'  ))
#             self.pool.get('hr.employee').write(cr,uid,ids[0],{'od_leave_eligible':0},context=context)
            
        return True


class hr_holidays(osv.osv):
    _inherit = "hr.holidays"


    def od_onchange_holiday_status_id(self, cr, uid, ids, holiday_status_id, employee_id, date_from=False, context=None): 
        year_start_date = str(datetime.strptime(str(date(date.today().year, 1, 1)), "%Y-%m-%d"))
        if date_from:
            year = datetime.strptime(date_from,'%Y-%m-%d %H:%M:%S').year
            year_start_date = str(datetime.strptime(str(date(year, 1, 1)), "%Y-%m-%d"))
#         year_end_date = str(datetime.strptime(str(date(date.today().year+1, 01, 01)), "%Y-%m-%d"))
        employee_ids = self.pool.get('hr.employee').search(cr,uid,[('id','=',employee_id)])
        
        emp_obj = self.pool.get('hr.employee').browse(cr,uid,employee_id)
        emp_comp_id  = emp_obj.company_id and emp_obj.company_id.id 
        parameter_obj = self.pool.get('ir.config_parameter')
#company parameter
        company_param_id = parameter_obj.search(cr,uid,[('key', '=', 'od_beta_saudi_co')])
        if not company_param_id:
            raise osv.except_osv(_('Settings Warning!'),_('No Company Parameter Not defined\nconfig it in System Parameters with od_beta_saudi_co!'))
        company_param =parameter_obj.browse(cr,uid,company_param_id)
        saudi_company_id = company_param.od_model_id and company_param.od_model_id.id or False
        #parameter saudi work days
        parameter_ids = parameter_obj.search(cr,uid,[('key', '=', 'def_leaves_year_saudi_labour')])
        if not parameter_ids:
            raise osv.except_osv(_('Settings Warning!'),_('config work days,def_leaves_year_saudi_labour'))
        parameter_data = parameter_obj.browse(cr,uid,parameter_ids)
        saudi_parameter_work_days = float(parameter_data.value)
        
        contract_id = self.pool.get('hr.contract').search(cr,uid,[('employee_id', '=', employee_id),('od_active','=',True)])
        if not contract_id:
            raise osv.except_osv(_('Settings Warning!'),_('employee have no active contract'))
        if contract_id:
            contract_id = contract_id[0]
        type_id = self.pool.get('hr.contract').browse(cr,uid,contract_id,context).type_id and self.pool.get('hr.contract').browse(cr,uid,contract_id,context).type_id.id
        
        res = {}
        le = 0
        if employee_ids:
            employee_ids = employee_ids[0]
        od_joining_date = self.pool.get('hr.employee').browse(cr,uid,employee_ids,context).od_joining_date or False
        if not od_joining_date:
            raise osv.except_osv(_('Settings Warning!'),_('joining_date not provided'))
        od_joining_date = datetime.strptime(od_joining_date, "%Y-%m-%d")
        
            
        leave_request_date = ''  
        total_days = 0 
        if date_from:
            leave_request_date = str(date_from)
            leave_request_date = datetime.strptime(leave_request_date[:10],"%Y-%m-%d")
#            leave_request_date = leave_request_date.strftime('%Y-%m-%d') 
            total_days = (datetime.strptime(str(leave_request_date), '%Y-%m-%d %H:%M:%S') - datetime.strptime(str(od_joining_date), '%Y-%m-%d %H:%M:%S')).days 
# total_unpaid_leaves 

        leave_unpaid_ids = self.pool.get('hr.holidays').search(cr,uid,[('employee_id', '=', employee_id), ('holiday_status_id', '=', 4),('state', 'not in', ('cancel','refuse'))])   
        total_unpaid_leaves = 0
        if leave_unpaid_ids:
            for obje in leave_unpaid_ids:
                for alloc in self.pool.get('hr.holidays').browse(cr,uid,obje,context=context):
                        total_unpaid_leaves += alloc.number_of_days
#total_worked_days
        total_worked_days = total_days + total_unpaid_leaves

#allowed leave taking from parameter
        parameter_obj = self.pool.get('ir.config_parameter')
        parameter_ids = parameter_obj.search(cr,uid,[('key', '=', 'def_leaves_year')])
        if not parameter_ids:
            raise osv.except_osv(_('Settings Warning!'),_('No allocated leave defined\nconfig it in System Parameters with def_leaves_year!'))
        parameter_data = parameter_obj.browse(cr,uid,parameter_ids)
        allocated_leave = parameter_data.value
        if emp_comp_id == saudi_company_id and type_id == 4:
            allocated_leave = saudi_parameter_work_days
#taking number of working days in parameter values

        parameter_obj = self.pool.get('ir.config_parameter')
        parameter_ids = parameter_obj.search(cr,uid,[('key', '=', 'def_wrk_days_year')])
        if not parameter_ids:
            raise osv.except_osv(_('Settings Warning!'),_('config work days,def_wrk_days_year'))
        parameter_data = parameter_obj.browse(cr,uid,parameter_ids)
        working_days_year = float(parameter_data.value)

#calculating leave_allowed_now, if employee completes 1 year he will be allowed 30 days at starting of next year itself
        if total_days > working_days_year:
            leave_allowed_now = float(allocated_leave)
        else:
            leave_allowed_now = float(float(allocated_leave)/float(working_days_year)) * total_worked_days
 
#total leave taken in the applying year
        leave_taken_upto_current_date = 0
        if date_from:
            leave_request_date = str(leave_request_date)
            old_str = str(leave_request_date[5:10])
            leave_request_date = string.replace(leave_request_date, old_str, '12-31')
            current_leave_id =ids and ids[0]
            leave_ids_for_current_date = self.search(cr,uid,[('employee_id', '=', employee_id),('id','!=',current_leave_id), ('holiday_status_id', '=', holiday_status_id),('state', 'not in', ('cancel','refuse')),('date_from','<',str(leave_request_date)),('date_from','>',year_start_date)])
            if leave_ids_for_current_date:
                for lv in leave_ids_for_current_date:
                    for levs in self.browse(cr,uid,lv,context=context):
                        leave_taken_upto_current_date += levs.number_of_days_temp
                        
        #calculating the no_of_pending_leaves(original value)     
        no_of_pending_leaves = round((leave_allowed_now - leave_taken_upto_current_date),2)
        
        if not (total_days < working_days_year):
            if type_id == 4:
                if emp_comp_id == saudi_company_id:
                    le = 30-leave_taken_upto_current_date
                else:
                    le = 60-leave_taken_upto_current_date
                if le < no_of_pending_leaves:
                    no_of_pending_leaves = le
                    
                else:
                    no_of_pending_leaves = no_of_pending_leaves 
                    
            if type_id == 5:
                no_of_pending_leaves = 0
            if type_id not in (4,5):
                le = 30-leave_taken_upto_current_date
                if le < no_of_pending_leaves:
                    no_of_pending_leaves = le
                    
                else:
                    no_of_pending_leaves = no_of_pending_leaves
     
            res = {'value':{'od_leave_eligible':no_of_pending_leaves,'od_leave_encashment':False,'od_total_leave_taken':leave_taken_upto_current_date,'od_leave_eligible_invisible':no_of_pending_leaves,'od_total_leave_taken_invisible':(leave_taken_upto_current_date)}}
        else:
            
            res = {'value':{'od_leave_eligible':0,'od_leave_encashment':False,'od_total_leave_taken':leave_taken_upto_current_date,'od_leave_eligible_invisible':no_of_pending_leaves,'od_total_leave_taken_invisible':(leave_taken_upto_current_date)}}
        return res
