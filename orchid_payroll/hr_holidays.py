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
from datetime import date
import dateutil.relativedelta 
import math




class hr_holidays(osv.osv):
    _inherit = "hr.holidays"
    
    def _od_check_leaves(self, cr, uid, ids, context=None):
        for wiz in self.browse(cr, uid, ids, context=context):
            if not wiz.number_of_days_temp:
                print wiz.number_of_days_temp,"o"*88
                return False
        return True

    _constraints = [
        (_od_check_leaves, 'Check Number Of Leave', ['number_of_days_temp']),
    ]




    def holidays_confirm(self, cr, uid, ids, context=None):
        
        for record in self.browse(cr, SUPERUSER_ID, ids, context=context):
            if record.employee_id and record.employee_id.parent_id and record.employee_id.parent_id.user_id:
                self.message_subscribe_users(cr, SUPERUSER_ID, [record.id], user_ids=[record.employee_id.parent_id.user_id.id], context=context)
        return self.write(cr, uid, ids, {'state': 'confirm'})



    def create(self, cr, uid, vals, context=None):
        vals['od_leave_eligible'] = vals.get('od_leave_eligible_invisible')

        vals['od_total_leave_taken'] = vals.get('od_total_leave_taken_invisible')
        vals['od_leave_sal'] = vals.get('od_leave_sal_invisible')
        employee_id = vals.get('employee_id',False)
        emp_obj = self.pool.get('hr.employee').browse(cr,uid,employee_id)
        emp_comp_id  = emp_obj.company_id and emp_obj.company_id.id
        if vals.get('od_leave_encashment') ==True:
            return super(hr_holidays, self).create(cr, uid, vals, context=context)
            

        friday = 0
        sat = 0
        public_holidays = 0
        if not vals:
            vals={}
        if vals.get('type') == 'add':
            return super(hr_holidays, self).create(cr, uid, vals, context=context)
        leave_type_obj = self.pool.get('hr.holidays.status').browse(cr,uid,vals['holiday_status_id'],context)
        if leave_type_obj.od_skip_holidays and leave_type_obj.od_skip_weekends:
            parameter_obj = self.pool.get('ir.config_parameter')
            parameter_ids = parameter_obj.search(cr,uid,[('key', '=', 'def_weekend_days')])
            if not parameter_ids:
                raise osv.except_osv(_('Settings Warning!'),_('pls config holidays,def_weekend_days'))
            parameter_data = parameter_obj.browse(cr,uid,parameter_ids)
            if vals.get('date_from') and vals.get('date_to') and vals.get('number_of_days_temp'):

                od_tmp_days = vals.get('number_of_days_temp') < 1 and 1 or vals.get('number_of_days_temp')
                for i in range(0,int(od_tmp_days)):
                    leave_days_date_time = datetime.strptime(vals.get('date_from'),"%Y-%m-%d %H:%M:%S") + timedelta(days=i)
                    leave_days_date = (leave_days_date_time).strftime('%Y-%m-%d')
                    current_year = (leave_days_date_time).strftime('%Y')
                    public_holidays_id = self.pool.get('od.hr.holidays.public').search(cr,uid,[('year','=',current_year)])
                    public_holiday_obj = self.pool.get('od.hr.holidays.public').browse(cr,uid,public_holidays_id,context)
                    pub_hod_comp_id = public_holiday_obj.company_id and public_holiday_obj.company_id.id
                    for holidays in public_holiday_obj.line_ids:
                        if emp_comp_id:
                            if emp_comp_id == pub_hod_comp_id:
                                if leave_days_date == holidays.date and holidays.variable:
                                    public_holidays +=1 
                        else:
                            if leave_days_date == holidays.date and holidays.variable:
                                public_holidays +=1 

                    if (leave_days_date_time.strftime("%A") == (parameter_data.value).split(',')[0]):
                        friday+=1
                    if (leave_days_date_time.strftime("%A") == (parameter_data.value).split(',')[1]):
                        sat = sat + 1

                total_week_leaves_in_leave = friday + sat + public_holidays
                vals['number_of_days_temp'] = vals.get('number_of_days_temp') - total_week_leaves_in_leave




        elif leave_type_obj.od_skip_holidays and not leave_type_obj.od_skip_weekends:
            parameter_obj = self.pool.get('ir.config_parameter')
            parameter_ids = parameter_obj.search(cr,uid,[('key', '=', 'def_weekend_days')])
            if not parameter_ids:
                raise osv.except_osv(_('Settings Warning!'),_('pls config holidays,def_weekend_days'))
            parameter_data = parameter_obj.browse(cr,uid,parameter_ids)
            if vals.get('date_from') and vals.get('date_to') and vals.get('number_of_days_temp'):

                od_tmp_days = vals.get('number_of_days_temp') < 1 and 1 or vals.get('number_of_days_temp')
                for i in range(0,int(od_tmp_days)):
                    leave_days_date_time = datetime.strptime(vals.get('date_from'),"%Y-%m-%d %H:%M:%S") + timedelta(days=i)
                    leave_days_date = (leave_days_date_time).strftime('%Y-%m-%d')
                    current_year = (leave_days_date_time).strftime('%Y')
                    public_holidays_id = self.pool.get('od.hr.holidays.public').search(cr,uid,[('year','=',current_year)])
                    public_holiday_obj = self.pool.get('od.hr.holidays.public').browse(cr,uid,public_holidays_id,context)
                    for holidays in public_holiday_obj.line_ids:
                        if leave_days_date == holidays.date and holidays.variable:
                            public_holidays +=1 

                    if (leave_days_date_time.strftime("%A") == (parameter_data.value).split(',')[0]):
                        friday+=1
                    if (leave_days_date_time.strftime("%A") == (parameter_data.value).split(',')[1]):
                        sat = sat + 1

                total_week_leaves_in_leave = public_holidays
                vals['number_of_days_temp'] = vals.get('number_of_days_temp') - total_week_leaves_in_leave




        elif not leave_type_obj.od_skip_holidays and leave_type_obj.od_skip_weekends:
            parameter_obj = self.pool.get('ir.config_parameter')
            parameter_ids = parameter_obj.search(cr,uid,[('key', '=', 'def_weekend_days')])
            if not parameter_ids:
                raise osv.except_osv(_('Settings Warning!'),_('pls config holidays,def_weekend_days'))
            parameter_data = parameter_obj.browse(cr,uid,parameter_ids)
            if vals.get('date_from') and vals.get('date_to') and vals.get('number_of_days_temp'):

                od_tmp_days = vals.get('number_of_days_temp') < 1 and 1 or vals.get('number_of_days_temp')
                for i in range(0,od_tmp_days):
                    leave_days_date_time = datetime.strptime(vals.get('date_from'),"%Y-%m-%d %H:%M:%S") + timedelta(days=i)
                    leave_days_date = (leave_days_date_time).strftime('%Y-%m-%d')
                    current_year = (leave_days_date_time).strftime('%Y')
                    public_holidays_id = self.pool.get('od.hr.holidays.public').search(cr,uid,[('year','=',current_year)])
                    public_holiday_obj = self.pool.get('od.hr.holidays.public').browse(cr,uid,public_holidays_id,context)
                    for holidays in public_holiday_obj.line_ids:
                        if leave_days_date == holidays.date and holidays.variable:
                            public_holidays +=1 

                    if (leave_days_date_time.strftime("%A") == (parameter_data.value).split(',')[0]):
                        friday+=1
                    if (leave_days_date_time.strftime("%A") == (parameter_data.value).split(',')[1]):
                        sat = sat + 1

                total_week_leaves_in_leave = friday + sat
                vals['number_of_days_temp'] = vals.get('number_of_days_temp') - total_week_leaves_in_leave




        else:
            vals['number_of_days_temp'] = vals.get('number_of_days_temp') 


        return super(hr_holidays, self).create(cr, uid, vals, context=context)



#    def write(self, cr, uid, ids, vals, context=None):
#        obj = self.browse(cr,uid,ids[0],context)
#        od_leave_eligible = obj.od_leave_eligible
#        od_total_leave_taken = obj.od_total_leave_taken
#        print "-----------------------",vals.get('od_leave_eligible_invisible')

#        print ">>>>>>>>>>XXXXXXXXXXXX**************",od_leave_eligible
#        print "*******************",od_total_leave_taken

#        vals['od_leave_eligible'] = od_leave_eligible

#        vals['od_total_leave_taken'] = od_total_leave_taken
#        
#        

#        return super(hr_holidays, self).write(cr, uid, ids, vals, context=context)


    def onchange_employee(self, cr, uid, ids, employee_id):
        result = {'value': {'department_id': False}}
        if employee_id:
            employee = self.pool.get('hr.employee').browse(cr, uid, employee_id)
            result['value'] = {'department_id': employee.department_id.id}
            result['value'].update({'holiday_status_id':False})
        return result

    def onchange_date_from(self, cr, uid, ids, date_to, date_from):
        result = super(hr_holidays,self).onchange_date_from(cr, uid, ids, date_to, date_from)  
        result['value'].update({'holiday_status_id':False}) 

        return result
    def onchange_date_to(self, cr, uid, ids, date_to, date_from):
        result = super(hr_holidays,self).onchange_date_to(cr, uid, ids, date_to, date_from)  
        result['value'].update({'holiday_status_id':False}) 

        return result





    def write(self, cr, uid, ids, vals, context=None):

        if vals.get('od_leave_eligible_invisible') or vals.get('od_total_leave_taken_invisible') or vals.get('od_leave_sal_invisible'):

            vals['od_leave_eligible'] = vals.get('od_leave_eligible_invisible')

            vals['od_total_leave_taken'] = vals.get('od_total_leave_taken_invisible')

            vals['od_leave_sal'] = vals.get('od_leave_sal_invisible')
        if vals.get('od_leave_encashment') ==True:
            return super(hr_holidays, self).create(cr, uid, vals, context=context)


        if not vals:
            vals={}
        if vals.get('type') == 'add':
            return super(hr_holidays, self).write(cr, uid, ids, vals, context=context)
        if vals.get('date_from') or vals.get('date_to') or vals.get('holiday_status_id') or vals.get('number_of_days_temp'):
            leave_obj = self.pool.get('hr.holidays').browse(cr,uid,ids[0],context)
            date_from = vals.get('date_from') or leave_obj.date_from
            date_to = vals.get('date_to') or leave_obj.date_to 
            diff = (datetime.strptime(date_to, '%Y-%m-%d %H:%M:%S') -  datetime.strptime(date_from, '%Y-%m-%d %H:%M:%S')).days +1
            if diff < 0:
                raise osv.except_osv(_('Settings Warning!'),_('pls check the dates'))


            friday = 0
            sat = 0
            public_holidays = 0
            
            
            
            holiday_status_id = vals.get('holiday_status_id') or leave_obj.holiday_status_id.id
            leave_type_obj = self.pool.get('hr.holidays.status').browse(cr,uid,holiday_status_id,context)
            if leave_type_obj.od_skip_holidays and leave_type_obj.od_skip_weekends:
                parameter_obj = self.pool.get('ir.config_parameter')
                parameter_ids = parameter_obj.search(cr,uid,[('key', '=', 'def_weekend_days')])
                if not parameter_ids:
                    raise osv.except_osv(_('Settings Warning!'),_('pls config holidays,def_weekend_days'))
                parameter_data = parameter_obj.browse(cr,uid,parameter_ids)

                for i in range(0,diff):
                    leave_days_date_time = datetime.strptime(date_from,"%Y-%m-%d %H:%M:%S") + timedelta(days=i)
                    leave_days_date = (leave_days_date_time).strftime('%Y-%m-%d')
                    current_year = (leave_days_date_time).strftime('%Y')
                    public_holidays_id = self.pool.get('od.hr.holidays.public').search(cr,uid,[('year','=',current_year)])
                    public_holiday_obj = self.pool.get('od.hr.holidays.public').browse(cr,uid,public_holidays_id,context)
                    


                    for holidays in public_holiday_obj.line_ids:
                        if leave_days_date == holidays.date and holidays.variable:
                            public_holidays +=1 

                    if (leave_days_date_time.strftime("%A") == (parameter_data.value).split(',')[0]):
                        friday+=1
                    if (leave_days_date_time.strftime("%A") == (parameter_data.value).split(',')[1]):
                        sat = sat + 1

                total_week_leaves_in_leave = friday + sat + public_holidays
                vals['number_of_days_temp'] = diff - total_week_leaves_in_leave





            elif leave_type_obj.od_skip_holidays and not leave_type_obj.od_skip_weekends:
                parameter_obj = self.pool.get('ir.config_parameter')
                parameter_ids = parameter_obj.search(cr,uid,[('key', '=', 'def_weekend_days')])
                if not parameter_ids:
                    raise osv.except_osv(_('Settings Warning!'),_('pls config holidays,def_weekend_days'))
                parameter_data = parameter_obj.browse(cr,uid,parameter_ids)

                for i in range(0,diff):
                    leave_days_date_time = datetime.strptime(date_from,"%Y-%m-%d %H:%M:%S") + timedelta(days=i)
                    leave_days_date = (leave_days_date_time).strftime('%Y-%m-%d')
                    current_year = (leave_days_date_time).strftime('%Y')
                    public_holidays_id = self.pool.get('od.hr.holidays.public').search(cr,uid,[('year','=',current_year)])
                    public_holiday_obj = self.pool.get('od.hr.holidays.public').browse(cr,uid,public_holidays_id,context)
                    


                    for holidays in public_holiday_obj.line_ids:
                        if leave_days_date == holidays.date and holidays.variable:
                            public_holidays +=1 

                    if (leave_days_date_time.strftime("%A") == (parameter_data.value).split(',')[0]):
                        friday+=1
                    if (leave_days_date_time.strftime("%A") == (parameter_data.value).split(',')[1]):
                        sat = sat + 1

                total_week_leaves_in_leave = public_holidays
                vals['number_of_days_temp'] = diff - total_week_leaves_in_leave




            elif not leave_type_obj.od_skip_holidays and leave_type_obj.od_skip_weekends:
                parameter_obj = self.pool.get('ir.config_parameter')
                parameter_ids = parameter_obj.search(cr,uid,[('key', '=', 'def_weekend_days')])
                if not parameter_ids:
                    raise osv.except_osv(_('Settings Warning!'),_('pls config holidays,def_weekend_days'))
                parameter_data = parameter_obj.browse(cr,uid,parameter_ids)

                for i in range(0,diff):
                    leave_days_date_time = datetime.strptime(date_from,"%Y-%m-%d %H:%M:%S") + timedelta(days=i)
                    leave_days_date = (leave_days_date_time).strftime('%Y-%m-%d')
                    current_year = (leave_days_date_time).strftime('%Y')
                    public_holidays_id = self.pool.get('od.hr.holidays.public').search(cr,uid,[('year','=',current_year)])
                    public_holiday_obj = self.pool.get('od.hr.holidays.public').browse(cr,uid,public_holidays_id,context)
                    


                    for holidays in public_holiday_obj.line_ids:
                        if leave_days_date == holidays.date and holidays.variable:
                            public_holidays +=1 

                    if (leave_days_date_time.strftime("%A") == (parameter_data.value).split(',')[0]):
                        friday+=1
                    if (leave_days_date_time.strftime("%A") == (parameter_data.value).split(',')[1]):
                        sat = sat + 1


                total_week_leaves_in_leave = friday + sat
                vals['number_of_days_temp'] = diff - total_week_leaves_in_leave





















            else:
                vals['number_of_days_temp'] = diff 
                
        return super(hr_holidays, self).write(cr, uid, ids, vals, context=context)



#     def od_onchange_holiday_status_id(self, cr, uid, ids, holiday_status_id, employee_id, date_from=False, context=None): 
# 
#         year_start_date = str(datetime.strptime(str(date(date.today().year, 1, 1)), "%Y-%m-%d")) 
#         year_end_date = str(datetime.strptime(str(date(date.today().year+1, 01, 01)), "%Y-%m-%d"))
# 
#         if date_from:
#             leave_request_date = str(date_from)
#             leave_request_date = str(datetime.strptime(leave_request_date, '%Y-%m-%d %H:%M:%S') + timedelta(hours=4))
# 
#        #calculating allowed leave for particular employee at the date of requesting
#         worked_days_in_the_current_year =0
#         if date_from:
#             worked_days_in_the_current_year = (datetime.strptime(year_end_date, '%Y-%m-%d %H:%M:%S') - datetime.strptime(leave_request_date, '%Y-%m-%d %H:%M:%S')).days + 1
#         parameter_obj = self.pool.get('ir.config_parameter')
#         parameter_ids = parameter_obj.search(cr,uid,[('key', '=', 'def_leaves_year')])
#         if not parameter_ids:
#             raise osv.except_osv(_('Settings Warning!'),_('No allocated leave defined\nPlz config it in System Parameters with def_leaves_year!'))
#         parameter_data = parameter_obj.browse(cr,uid,parameter_ids)
#         allocated_leave = parameter_data.value
#         leave_allowed_now = float(float(allocated_leave)/float(365)) * worked_days_in_the_current_year
# 
# 
# 
#         #calculating total allocated leave for the employee
#         leaves =0
#         no_of_pending_leaves = 0
#         total_allocated_leave = 0
#         leave_remaining = 0
#         if date_from:
#             allocated_ids = self.search(cr,uid,[('employee_id', '=', employee_id), ('holiday_status_id', '=', holiday_status_id),('state', 'in', ('validate','od_resumption_to_approve','od_approved')),('date_from','=',False)])
#             if allocated_ids:
#                 for obje in allocated_ids:
#                     for alloc in self.browse(cr,uid,obje,context=context):
#                         total_allocated_leave += alloc.number_of_days
# 
# 
#         #calculating total leave taken the employee before the request date
#         leave_taken_upto_current_date = 0
#         if date_from:
#             leave_ids_for_current_date = self.search(cr,uid,[('employee_id', '=', employee_id), ('holiday_status_id', '=', holiday_status_id),('state', 'in', ('validate','od_resumption_to_approve','od_approved')),('date_from','<',leave_request_date)])
#             if leave_ids_for_current_date:
#                 for lv in leave_ids_for_current_date:
#                     for levs in self.browse(cr,uid,lv,context=context):
#                         leave_taken_upto_current_date += levs.number_of_days_temp
# 
# 
#         #currently how much leave pending
#         no_of_pending_leaves = round((total_allocated_leave - leave_taken_upto_current_date),2)
#         eligible_leave = no_of_pending_leaves - leave_allowed_now
#                     
#             
#      
#         res = {'value':{'od_total_leave_taken':(leave_taken_upto_current_date),'od_leave_eligible':eligible_leave,'od_leave_encashment':False}}
#         
#         return res


#    def _od_get_total_leave(self, cr, uid, ids, field_name, arg, context=None): 
#        res ={} 

#        year_start_date = str(datetime.strptime(str(date(date.today().year, 1, 1)), "%Y-%m-%d")) 
#        year_end_date = str(datetime.strptime(str(date(date.today().year, 12, 31)), "%Y-%m-%d"))
#        for li in self.browse(cr, uid, ids, context): 
#            employee_id = li.employee_id and li.employee_id.id
#            holiday_status_id = li.holiday_status_id and li.holiday_status_id.id
#            total_no_of_leave = 0
#            number_of_days_temp = li.number_of_days_temp
#            if employee_id:
#                leave_ids = self.search(cr,uid,[('employee_id', '=', employee_id), ('holiday_status_id', '=', 2),('date_from','>=',year_start_date),('date_from','<=',year_end_date)])
#            
#                if leave_ids:
#                    for obj in leave_ids:
#                        for leave in self.browse(cr,uid,obj,context=context):
#                            if leave.number_of_days <0:
#                                total_no_of_leave+=leave.number_of_days
#            
#            res[li.id] = (-1 * total_no_of_leave) - number_of_days_temp
#        return res 


    def _od_get_year(self, cr, uid, ids, field_name, arg, context=None): 
        res ={} 
        year = 0

        for li in self.browse(cr, uid, ids, context): 
        
            
            if li.date_from:
                date_from = str(li.date_from)
                year = int(date_from.split('-')[0])
            
            res[li.id] = year
        return res 

    def _od_get_month(self, cr, uid, ids, field_name, arg, context=None): 
        res ={} 
        month = 0

        for li in self.browse(cr, uid, ids, context): 
            
            if li.date_from:
                date_from = str(li.date_from)
                month = int(date_from.split('-')[1])
            
            res[li.id] = month
        return res 




    def _od_get_day(self, cr, uid, ids, field_name, arg, context=None): 
        res ={} 
        day = 0

        for li in self.browse(cr, uid, ids, context): 
            
            if li.date_from:
                date_from = str(li.date_from)
                day_time = str(date_from.split('-')[2])
                day = int(day_time.split()[0])
            
            res[li.id] = day
        return res 






    def od_compute_leave_encashment(self,cr,uid,ids,context=None):

        parameter_obj = self.pool.get('ir.config_parameter')
        parameter_ids = parameter_obj.search(cr,uid,[('key', '=', 'def_wrk_days_year')])
        if not parameter_ids:
            raise osv.except_osv(_('Settings Warning!'),_('pls config work days,def_wrk_days_year'))
        parameter_data = parameter_obj.browse(cr,uid,parameter_ids)
        working_days_year = float(parameter_data.value) or 1
        encashment_amt = 0
        holiday_obj = self.browse(cr,uid,ids[0],context)
        number_of_days_temp = holiday_obj.number_of_days_temp
        if holiday_obj.holiday_type == 'category':
            raise osv.except_osv(_('Settings Warning!'),_('computation is possible only mode of type By Employee!!'))
        employee_id = holiday_obj.employee_id.id
        hr_contract_ids = self.pool.get('hr.contract').search(cr,uid,[('employee_id','=',employee_id)])
        if hr_contract_ids:
            hr_contract_id = hr_contract_ids[0]
            hr_contract_obj = self.pool.get('hr.contract').browse(cr,uid,hr_contract_id,context)
            basis_for_oneday = (hr_contract_obj.wage*12)/working_days_year
            encashment_amt = round((basis_for_oneday * number_of_days_temp),2)
        self.pool.get('hr.holidays').write(cr,uid,ids[0],{'od_leave_encahment_amount':encashment_amt},context=context)
        return True
        
    

#    def _od_leave_eligible(self, cr, uid, ids, field_name, arg, context=None): 
#        res ={} 

#        year_start_date = str(datetime.strptime(str(date(date.today().year, 1, 1)), "%Y-%m-%d")) 
#        year_end_date = str(datetime.strptime(str(date(date.today().year+1, 01, 01)), "%Y-%m-%d"))
#        print "::::::::::",ids
#        for eo in self.browse(cr, uid, ids, context): 
#            employee_id = eo.employee_id and eo.employee_id.id
#            holiday_status_id = eo.holiday_status_id and eo.holiday_status_id.id
#            leave_request_date = eo.date_from
#            if leave_request_date:
#                leave_request_date = datetime.strptime(leave_request_date, '%Y-%m-%d %H:%M:%S') + timedelta(hours=4)
#            current_value_of_leave = eo.number_of_days_temp
#            if leave_request_date:
#                worked_days_in_the_current_year = ((datetime.strptime(year_end_date, '%Y-%m-%d %H:%M:%S') - leave_request_date).days) +1
#                parameter_obj = self.pool.get('ir.config_parameter')
#                parameter_ids = parameter_obj.search(cr,uid,[('key', '=', 'def_leaves_year')])
#                if not parameter_ids:
#                    raise osv.except_osv(_('Settings Warning!'),_('No allocated leave defined\nPlz config it in System Parameters with def_leaves_year!'))
#                parameter_data = parameter_obj.browse(cr,uid,parameter_ids)
#                allocated_leave = parameter_data.value
#                print "LLLLLLLLL",allocated_leave
#                print "FFFFFFFFFF",float(allocated_leave)/365
#                print "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFf",worked_days_in_the_current_year
#                leave_allowed_now = (worked_days_in_the_current_year*(float(allocated_leave)/float(365)))

##(worked_days_in_the_current_year*(float(float(allocated_leave)/float(365))))

##(worked_days_in_the_current_year*(float(float(allocated_leave)/float(365))))
#                print "DDDDDDDDDDDDDD",leave_allowed_now

#                no_of_pending_leaves = 0
#                leaves=0
#                total_allocated_leave = 0
#                leave_remaining = 0
#                allocated_ids = self.search(cr,uid,[('employee_id', '=', employee_id), ('holiday_status_id', '=', holiday_status_id)])
#                if allocated_ids:
#                    for obje in allocated_ids:
#                        for alloc in self.browse(cr,uid,obje,context=context):
#                            total_allocated_leave += alloc.number_of_days_temp
#                            leave_remaining +=float(alloc.number_of_days)
#                            

#                            
#                            if alloc.number_of_days_temp >0:
#                            
#                                no_of_pending_leaves= (no_of_pending_leaves + float(alloc.number_of_days_temp))

#                leaves = (total_allocated_leave - leave_remaining) - current_value_of_leave
#                print "LLLLLLLLLL",leaves
#                eligible_leave = float(no_of_pending_leaves - leave_allowed_now) - float(leaves)
#                print "IIIIIIIIIIIIIII",eligible_leave
#                res[eo.id] = eligible_leave
#            else:
#                res[eo.id] = 0
#                
#        return res

    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id

    _columns = {
        'company_id': fields.many2one('res.company','Company'),
        'od_resumption_date':fields.date('Resumption Date'),
        'state': fields.selection([('draft', 'To Submit'), ('cancel', 'Cancelled'),('confirm', 'To Approve'), ('refuse', 'Refused'), ('validate1', 'Second Approval'), ('validate', 'Leave Approved'),('od_resumption_to_approve','Resumption To Approve'),('od_approved','Resumption Approved'),('validate2','Third Approval')],
            'Status', readonly=True, track_visibility='onchange', copy=False,
            ), 
#        'od_total_leave_taken':fields.function(_od_get_total_leave,string='Total Leave Taken',type='integer'),
#        'od_leave_eligible':fields.function(_od_leave_eligible,string='Leave Eligibile',type='float',store=True),

        'od_total_leave_taken':fields.integer('Total Leave Taken'),
        'od_leave_eligible':fields.float('Leave Eligibile', digits_compute=dp.get_precision('Account')),
        'od_leave_encahment_amount':fields.float(string='Encashment Amt',readonly="1"),


        'od_year':fields.function(_od_get_year,string='Year',type='integer',store=True),
        'od_month':fields.function(_od_get_month,string='Month',type='integer',store=True),
        'od_day':fields.function(_od_get_day,string='Day',type='integer',store=True),
        'od_total_leave_taken_invisible':fields.integer('Total Leave Taken in'),
        'od_leave_eligible_invisible':fields.float('Leave Eligibile in', digits_compute=dp.get_precision('Account')),
        'od_leave_sal':fields.float('Leave Salary', digits_compute=dp.get_precision('Account')),
        'od_leave_sal_invisible':fields.float('Leave Salary', digits_compute=dp.get_precision('Account')),
       
    }
    _defaults ={
                'company_id': _get_default_company,
                }



class hr_employee(osv.osv):
    _inherit = "hr.employee"

    def _od_airfare_count(self, cr, uid, ids, field_name, arg, context=None):
        res ={}
        for obj in self.browse(cr, uid, ids, context):
            arifare_ids = self.pool.get('od.airfare.encashments').search(cr, uid, [('employee_id', '=', obj.id)])
            if arifare_ids:
                res[obj.id] = len(arifare_ids)
        return res

    _columns = {
        'od_identification_no':fields.integer('Identification No'),
        'od_airfare_count':fields.function(_od_airfare_count,string='Count',type='integer'),
        
           
    }



#    def _get_act_window_dict(self, cr, uid, ids, name, context=None):
#        mod_obj = self.pool.get('ir.model.data')
#        act_obj = self.pool.get('ir.actions.act_window')
#        result = mod_obj.xmlid_to_res_id(cr, uid, name, raise_if_not_found=True)
#        obj = self.browse(cr,uid,ids,context)
#        result['domain'] = [('employee_id','=',obj.id)]
#        result['context'] = {'default_employee_id':obj.id}
#        print ">>>>>>>>>>>>>>>>>>>>>>>>",res

#        return result
#    
#    def action_open_airfare(self, cr, uid, ids, context=None):
#        result = self._get_act_window_dict(cr, uid, ids,'orchid_payroll.action_od_airfare_encashments_master',context=context)
#        return result

    def action_open_airfare(self,cr,uid,ids,context=None):
        data = self.browse(cr,uid,ids)
        employee_id = data and data.id
        res = {
        'type': 'ir.actions.act_window',
        'view_mode': 'tree,form',
        'view_type': 'form',
        'res_model': 'od.airfare.encashments',
        'domain': [('employee_id', '=',employee_id)],
        'context':{'default_employee_id':employee_id}
        }
        return res









class hr_holidays_status(osv.osv):
    _inherit = "hr.holidays.status"
    _columns = {
        'od_skip_holidays':fields.boolean('Skip Public Holidays'),

        'od_skip_weekends':fields.boolean('Skip Week Ends'),
        'od_tripple_validation':fields.boolean(string="Triple Validation")

           
    }
    
