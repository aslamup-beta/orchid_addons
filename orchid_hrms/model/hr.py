# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
from openerp.tools.translate import _
import copy
import math
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning

import datetime
import dateutil.relativedelta
from datetime import date, timedelta
import itertools
from lxml import etree
import openerp.addons.decimal_precision as dp
import time
from openerp import workflow
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from openerp import SUPERUSER_ID




class hr_job(models.Model):
    _inherit = 'hr.job'
    od_notes = fields.Text(String='Description')

class hr_holidays(models.Model):
    _inherit = "hr.holidays"
    od_document_line = fields.One2many('od.holiday.document.line','holiday_id',string='Documents')
    od_leave_encashment = fields.Boolean('Leave Encashment',default=False)
    od_ticket_required = fields.Boolean('Ticket Required',default=False)


#    @api.multi
#    @api.one
#    @api.constrains('number_of_days_temp','holiday_status_id','od_leave_encashment','date_from')
#    def _check_constriant(self):
#        holiday_status_id = self.holiday_status_id and self.holiday_status_id.id
#        od_deny_back_dated_entry = self.holiday_status_id.od_deny_back_dated_entry
#        date_from = datetime.datetime.now().strftime('%Y-%m-%d 00:00:00')
#        print ">><<<<<<CCCCC",date_from

#        if holiday_status_id == 1 and not od_deny_back_dated_entry:
#            print "BBBBBBBBBBBB",
#            
#        

#            
#        return True



class hr_holidays_status(models.Model):
    _inherit = "hr.holidays.status"
    od_deny_back_dated_entry = fields.Boolean(string='Deny Back Dated Entry',default=False)



class od_holiday_document_line(models.Model):
    _name = "od.holiday.document.line"
    _description = "od.holiday.document.line"

    holiday_id = fields.Many2one('hr.holidays',string='Holiday')
    document_type_id = fields.Many2one('od.employee.document.type',string='Document Type',required=True)
    recieved = fields.Boolean(string='Return',default=False)
    recieved_date = fields.Date(string='Returned Date')
    issued_date = fields.Date(string='Issued Date')
    issued = fields.Boolean(string='Issued',default=False)



class hr_employee(models.Model):
    _inherit = 'hr.employee'


    @api.one
    @api.depends('name')
    def _compute_document_count(self):
        employee_id = self.id
        doc_ids = []
        document_ids = self.env['od.document.request'].search([('employee_id','=',employee_id)])
        for obj in document_ids:
            doc_ids.append(obj.id)
        if doc_ids:
            self.od_document_count = len(doc_ids)

    @api.one
    @api.depends('name')
    def _compute_document_line_count(self):
        employee_id = self.id
        doc_ids = []
        document_ids = self.env['od.hr.employee.document.line'].search([('employee_id','=',employee_id)])
        for obj in document_ids:
            doc_ids.append(obj.id)
        if doc_ids:
            self.od_document_line_count = len(doc_ids)



    def od_generate_gratuity_value(self,cr,uid,ids,context=None):
        experiance = 0
        experiance_days = 0
        one_day_wage =0
        gratuvity = 0
        for obj in self.browse(cr,uid,ids,context):
            employee_id = obj.id
            od_terminated = obj.od_terminated
            od_limited = False
            od_gratuity_date = obj.od_gratuity_date
            if not od_gratuity_date:
                raise Warning(_("pls provide date"))
            joining_date = str(datetime.datetime.strptime(str(obj.od_joining_date), "%Y-%m-%d"))
            od_gratuity_date = str(datetime.datetime.strptime(str(od_gratuity_date), "%Y-%m-%d")) 


#####unpaid leave calculation search crieteria joining date to gratuvity date

            parameter_obj = self.pool.get('ir.config_parameter')
            parameter_ids = parameter_obj.search(cr,uid,[('key', '=', 'def_unpaid_leave_id')])
            if not parameter_ids:
                raise osv.except_osv(_('Settings Warning!'),_('configure id for unpaid leaves def_unpaid_leave_id!'))
            parameter_data = parameter_obj.browse(cr,uid,parameter_ids)
            unpaid_le_id = int(parameter_data.value)




            unpaid_leave_ids = self.pool.get('hr.holidays').search(cr,uid,[('employee_id', '=', employee_id), ('holiday_status_id', '=', unpaid_le_id),('state', 'in', ('validate','od_resumption_to_approve','od_approved')),('date_from','<',str(od_gratuity_date)),('date_from','>',joining_date)])
            total_unpaid_leaves = 0
            if unpaid_leave_ids:
                for lv in unpaid_leave_ids:
                    for levs in self.pool.get('hr.holidays').browse(cr,uid,lv,context=context):
                        total_unpaid_leaves += levs.number_of_days_temp

##############------------un paid leaves finish here ##############
                
            contract_ids = self.pool.get('hr.contract').search(cr,uid,[('employee_id','=',employee_id),('od_active','=',True)])
            if contract_ids:
                contract_ids = contract_ids[0]
                contract_obj = self.pool.get('hr.contract').browse(cr,uid,contract_ids,context)
                od_limited = contract_obj.od_limited
                one_day_wage = float(contract_obj.wage * 12) / 365.00 
                max_gratuity = float(contract_obj.wage * 24)  
#                 one_day_wage = float((contract_obj.wage) / 30)
                


#                
                experiance = float(((datetime.datetime.strptime(od_gratuity_date, '%Y-%m-%d %H:%M:%S') -  datetime.datetime.strptime(joining_date, '%Y-%m-%d %H:%M:%S')).days) - total_unpaid_leaves) /365.00  #Experiance in year

                experiance_days = float(((datetime.datetime.strptime(od_gratuity_date, '%Y-%m-%d %H:%M:%S') -  datetime.datetime.strptime(joining_date, '%Y-%m-%d %H:%M:%S')).days) - total_unpaid_leaves)  #Experiance in days
            else:
                raise Warning(_("pls define active contract for the employee"))


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

                if gratuvity > max_gratuity:
                    gratuvity = max_gratuity

            self.pool.get('hr.employee').write(cr,uid,[obj.id],{'od_gratuity':gratuvity},context=context)

               
        return True


#old one 
#    def od_generate_gratuity_value(self,cr,uid,ids,context=None):
#        experiance = 0
#        experiance_days = 0
#        one_day_wage =0
#        for obj in self.browse(cr,uid,ids,context):
#            employee_id = obj.id
#            od_gratuity_date = obj.od_gratuity_date
#            if not od_gratuity_date:
#                raise Warning(_("pls provide date"))
#                
#            contract_ids = self.pool.get('hr.contract').search(cr,uid,[('employee_id','=',employee_id)])[0]
#            if contract_ids:
#                contract_obj = self.pool.get('hr.contract').browse(cr,uid,contract_ids,context)
#                one_day_wage = float(contract_obj.wage * 12) / 365.00
#                joining_date = str(datetime.datetime.strptime(str(contract_obj.date_start), "%Y-%m-%d")) 
#                current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#                od_gratuity_date = str(datetime.datetime.strptime(str(od_gratuity_date), "%Y-%m-%d"))
#                
#                experiance = float(((datetime.datetime.strptime(od_gratuity_date, '%Y-%m-%d %H:%M:%S') -  datetime.datetime.strptime(joining_date, '%Y-%m-%d %H:%M:%S')).days)) /365.00  #Experiance in year

#                experiance_days = float(((datetime.datetime.strptime(od_gratuity_date, '%Y-%m-%d %H:%M:%S') -  datetime.datetime.strptime(joining_date, '%Y-%m-%d %H:%M:%S')).days))  #Experiance in days
#            else:
#                raise Warning(_("pls define contract for the employee"))
##  

#            if experiance <1:
#                gratuvity = 0
#            if experiance >1 and experiance <3:
#                gratuvity = (((7 * one_day_wage)/365.0) * experiance_days)
#            
#            if experiance >3 and experiance <5:
#                gratuvity = (((14 * one_day_wage) / 365.0) * experiance_days)
#            if experiance ==5:
#                gratuvity = (((21 * one_day_wage) /365.0) * experiance_days)
#            if experiance >5:
#                extra_year = experiance - 5
#                extra_year_in_days = extra_year * 365
#                gratuvity = ((21 * one_day_wage)*5) + (((one_day_wage *30) /365) * extra_year_in_days)
#            self.pool.get('hr.employee').write(cr,uid,[obj.id],{'od_gratuity':gratuvity},context=context)

#               
#        return True

    def od_view_documents(self,cr,uid,ids,context=None):
        result = self._get_act_window_dict(cr, uid, ids,'orchid_hrms.action_od_hr_document_lines_tre_views',context=context)
        return result





    def _get_act_window_dict(self, cr, uid, ids, name, context=None):
        context['employee_id'] = ids[0]
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        result = mod_obj.xmlid_to_res_id(cr, uid, name, raise_if_not_found=True)

        result = act_obj.read(cr, uid, [result], context=context)[0]
        result['domain'] = [('employee_id','=',ids[0])]

        return result


    def action_open_document_request(self,cr,uid,ids,context=None):
        data = self.browse(cr,uid,ids)
        employee_id = data and data.id
        res = {
        'type': 'ir.actions.act_window',
        'view_mode': 'tree,form',
        'view_type': 'form',
        'res_model': 'od.document.request',
        'domain': [('employee_id', '=',employee_id)],
        'context':{'default_employee_id':employee_id}
        }
        print res
        return res


    
#    def od_generate_gratuity(self,cr,uid,ids,context=None):
#        for obj in self.browse(cr, uid, ids, context=context):
#            employee_id = obj.id
#            partner_id = obj.address_home_id and obj.address_home_id.id
#            if not partner_id:
#                raise osv.except_osv(_('Error!'), _('define Home Address First'))
#            account_move_line_obj = self.pool.get('account.move.line')
#            salary_rule_obj = self.pool.get('hr.salary.rule')
#            rule_ids =  salary_rule_obj.search(cr,uid,[('account_credit','!=',False)])
#            if not rule_ids:
#                raise osv.except_osv(_('Error!'), _('pls define salary rule'))
#            account_credit_ids = [x.account_credit.id for x in salary_rule_obj.browse(cr,uid,rule_ids) if x.account_credit and x.od_is_gratuity]
#            account_ids = list(set(account_credit_ids))
#            if not account_ids:
#                raise osv.except_osv(_('Error!'), _('pls define accounts in salary rule'))
#                   
#            move_ids = account_move_line_obj.search(cr,uid,[('partner_id','=',partner_id),('account_id','in',account_ids)])
#            if not move_ids:
#                raise osv.except_osv(_('Error!'), _('there is no accounting entries for the particular employee'))
#               
#            move_data = account_move_line_obj.browse(cr,uid,move_ids)
#            move_line_credit={}
#            move_line_debit={}
#            for line in move_data:
#                if not line.account_id:
#                    continue
#                if line.credit:
#                    move_line_credit[line.account_id.id] = (line.account_id.id not in move_line_credit) \
#                                                             and line.credit or (float(move_line_credit.get(line.account_id.id))+line.credit)

#                    self.pool.get('hr.employee').write(cr,uid,[obj.id],{'od_gratuity':move_line_credit[line.account_id.id]},context=context)
#                else:
#                    self.pool.get('hr.employee').write(cr,uid,[obj.id],{'od_gratuity':0.0},context=context)
#                    

#        return True


    def compute_leave_eligible_employee_master(self,cr,uid,ids,context=None):
        uid=SUPERUSER_ID
        employee_id = self.browse(cr,uid,ids[0],context) and self.browse(cr,uid,ids[0],context).id
        if not employee_id:
            raise osv.except_osv(_('Settings Warning!'),_('first create employee,then compute'))
            
        



        year_start_date = str(datetime.datetime.strptime(str(date(date.today().year, 1, 1)), "%Y-%m-%d")) 
        year_end_date = str(datetime.datetime.strptime(str(date(date.today().year+1, 01, 01)), "%Y-%m-%d"))
        date_from = datetime.datetime.now().strftime('%Y-%m-%d 00:00:00')

        if date_from:
            leave_request_date = str(date_from)
            leave_request_date = str(datetime.datetime.strptime(leave_request_date, '%Y-%m-%d %H:%M:%S') + timedelta(hours=4))

       #calculating allowed leave for particular employee at the date of requesting
        worked_days_in_the_current_year =0
        if date_from:
            worked_days_in_the_current_year = (datetime.datetime.strptime(year_end_date, '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(leave_request_date, '%Y-%m-%d %H:%M:%S')).days + 1
        parameter_obj = self.pool.get('ir.config_parameter')
        parameter_ids = parameter_obj.search(cr,uid,[('key', '=', 'def_leaves_year')])
        if not parameter_ids:
            raise osv.except_osv(_('Settings Warning!'),_('No allocated leave defined\nPlz config it in System Parameters with def_leaves_year!'))
        parameter_data = parameter_obj.browse(cr,uid,parameter_ids)
        allocated_leave = parameter_data.value
        leave_allowed_now = float(float(allocated_leave)/float(365)) * worked_days_in_the_current_year



        #calculating total allocated leave for the employee
        leaves =0
        no_of_pending_leaves = 0
        total_allocated_leave = 0
        leave_remaining = 0
        if date_from:
            allocated_ids = self.pool.get('hr.holidays').search(cr,uid,[('employee_id', '=', employee_id), ('holiday_status_id', '=', 1),('state', 'in', ('validate','od_resumption_to_approve','od_approved')),('date_from','=',False)])
            if allocated_ids:
                for obje in allocated_ids:
                    for alloc in self.pool.get('hr.holidays').browse(cr,uid,obje,context=context):
                        total_allocated_leave += alloc.number_of_days


        #calculating total leave taken the employee before the request date
        leave_taken_upto_current_date = 0
        if date_from:
            leave_ids_for_current_date = self.pool.get('hr.holidays').search(cr,uid,[('employee_id', '=', employee_id), ('holiday_status_id', '=', 1),('state', 'in', ('validate','od_resumption_to_approve','od_approved')),('date_from','<',leave_request_date)])
            if leave_ids_for_current_date:
                for lv in leave_ids_for_current_date:
                    for levs in self.pool.get('hr.holidays').browse(cr,uid,lv,context=context):
                        leave_taken_upto_current_date += levs.number_of_days_temp


        #currently how much leave pending
        no_of_pending_leaves = round((total_allocated_leave - leave_taken_upto_current_date),2)
        eligible_leave = no_of_pending_leaves - leave_allowed_now
        self.pool.get('hr.employee').write(cr,uid,ids[0],{'od_leave_eligible':eligible_leave},context=context)
        return True




    def od_generate_leave_salary(self,cr,uid,ids,context=None):
        for obj in self.browse(cr, uid, ids, context=context):
            od_leave_salary_date = obj.od_leave_salary_date
            employee_id = obj.id
            if not od_leave_salary_date:
                raise osv.except_osv(_('warning!'), _('pls provide date'))

            parameter_obj = self.pool.get('ir.config_parameter')
            parameter_ids = parameter_obj.search(cr,uid,[('key', '=', 'def_wrk_days_year')])
            if not parameter_ids:
                raise osv.except_osv(_('Settings Warning!'),_('pls config work days,def_wrk_days_year'))
            parameter_data = parameter_obj.browse(cr,uid,parameter_ids)
            working_days_year = parameter_data.value

            parameter_leaves_ids = parameter_obj.search(cr,uid,[('key', '=', 'def_leaves_year')])

            if not parameter_leaves_ids:
                raise osv.except_osv(_('Settings Warning!'),_('No allocated leave defined\nPlz config it in System Parameters with def_leaves_year!'))
            parameter_leave_data = parameter_obj.browse(cr,uid,parameter_leaves_ids)
            allocated_leave_year = parameter_leave_data.value

            od_leave_salary_date = str(datetime.datetime.strptime(od_leave_salary_date, '%Y-%m-%d')) 





            holiday_id = self.pool.get('hr.holidays').search(cr,uid,[('employee_id', '=', employee_id),('date_from','=',False),('state', 'in', ('validate','od_resumption_to_approve','od_approved')),('holiday_status_id', '=', 1)])
            allocated_leaves = 0
            if holiday_id:
                for obj in self.pool.get('hr.holidays').browse(cr,uid,holiday_id,context):
                    allocated_leaves += obj.number_of_days

            total_leave_taken_up_to_applying_date= 0
            holiday_leave_ids = self.pool.get('hr.holidays').search(cr,uid,[('employee_id', '=', employee_id),('date_from','<',od_leave_salary_date),('state', 'in', ('validate','od_resumption_to_approve','od_approved')),('holiday_status_id', '=', 1)])
        
            
            if holiday_leave_ids:
                for obj in self.pool.get('hr.holidays').browse(cr,uid,holiday_leave_ids,context):
                    total_leave_taken_up_to_applying_date += obj.number_of_days_temp
                    
                




            year_end_date = str(datetime.datetime.strptime(str(date(date.today().year, 12, 31)), "%Y-%m-%d"))
           
            worked_days_in_the_current_year = ((datetime.datetime.strptime(year_end_date, '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(od_leave_salary_date, '%Y-%m-%d %H:%M:%S')).days) +1
            pending_leves = round(((allocated_leaves - (worked_days_in_the_current_year*(float(float(allocated_leave_year)/float(365))))) - total_leave_taken_up_to_applying_date),2)
           








            contract_id = self.pool.get('hr.contract').search(cr,uid,[('employee_id', '=', employee_id)])
            if not contract_id:
                raise osv.except_osv(_('Settings Warning!'),_('No contracts for employee'))
             
            if contract_id:
                contract_id = contract_id[0]
                
                contact_obj = self.pool.get('hr.contract').browse(cr,uid,contract_id,context)
                total_wage_one_day = (contact_obj.xo_total_wage * 12) / int(working_days_year)
                leave_salary = pending_leves * total_wage_one_day
        self.pool.get('hr.employee').write(cr,uid,ids[0],{'od_leave_salary':leave_salary,'od_leaves':pending_leves},context=context)
#        self.pool.get('hr.employee').write(cr,uid,ids[0],{'od_leaves':pending_leves},context)
            

        return True



    def od_generate_airfare(self,cr,uid,ids,context=None):
        for obj in self.browse(cr, uid, ids, context=context):
            employee_id = obj.id
            partner_id = obj.address_home_id and obj.address_home_id.id
            if not partner_id:
                raise osv.except_osv(_('Error!'), _('define Home Address First'))
            account_move_line_obj = self.pool.get('account.move.line')
            salary_rule_obj = self.pool.get('hr.salary.rule')
            rule_ids =  salary_rule_obj.search(cr,uid,[('account_credit','!=',False)])
            if not rule_ids:
                raise osv.except_osv(_('Error!'), _('pls define salary rule'))
            account_credit_ids = [x.account_credit.id for x in salary_rule_obj.browse(cr,uid,rule_ids) if x.account_credit and x.od_is_airfare]
            account_ids = list(set(account_credit_ids))
            if not account_ids:
                raise osv.except_osv(_('Error!'), _('pls define accounts in salary rule'))
                   
            move_ids = account_move_line_obj.search(cr,uid,[('partner_id','=',partner_id),('account_id','in',account_ids)])
            if not move_ids:
                raise osv.except_osv(_('Error!'), _('there is no accounting entries for the particular employee'))
               
            move_data = account_move_line_obj.browse(cr,uid,move_ids)
            move_line_credit={}
            move_line_debit={}
            for line in move_data:
                if not line.account_id:
                    continue
                if line.credit:
                    move_line_credit[line.account_id.id] = (line.account_id.id not in move_line_credit) \
                                                             and line.credit or (float(move_line_credit.get(line.account_id.id))+line.credit)

                    self.pool.get('hr.employee').write(cr,uid,[obj.id],{'od_air_fare':move_line_credit[line.account_id.id]},context=context)
                else:
                    self.pool.get('hr.employee').write(cr,uid,[obj.id],{'od_air_fare':0.0},context=context)
                    

        return True

    od_sponser_id = fields.Many2one('res.partner', domain=[('is_company', '=', True)],string='Sponsor',)
    od_pay_salary_during_annual_leave = fields.Boolean(string='Pay Salary During Annual Leave',default=False)
    od_air_fare = fields.Float(string="Airfare",readonly="1")
    od_leave_salary = fields.Float(string="Leave Salary",readonly="1")
    od_gratuity = fields.Float(string="Gratuity",readonly="1")
    od_terminated = fields.Boolean(string="Terminated")
    od_leave_eligible = fields.Float(string="Leave Eligble",readonly="1")
    od_original_leave_eligible = fields.Float(string="Leave Eligble(Org Value)",readonly="1")
    od_air_route_id = fields.Many2one('od.employee.air.route', string=' Air Route',)
    od_air_route_code = fields.Char(string='Code',)  
    od_air_route_fare = fields.Char(string='Fare',) 
    od_eligibility_date = fields.Date('Eligibility date')
    od_dependents_line = fields.One2many('od.hr.employee.dependents.line', 'employee_id', string='Dependents Lines')
    od_relatives_line = fields.One2many('od.hr.employee.relatives.line', 'employee_id', string='Relatives Lines')
    od_education_line = fields.One2many('od.hr.employee.education.line', 'employee_id', string='Education Lines')
    od_launguage_line = fields.One2many('od.hr.employee.launguage.line', 'employee_id', string='Launguage Lines')
    od_facilitates_line = fields.One2many('od.hr.employee.facilitates.line', 'employee_id', string='Facilitates Lines')
    od_accomadtion_id = fields.Many2one('od.employee.accomadation', string='Accommodation',)
    od_transportation_id = fields.Many2one('od.employee.transportation', string='Transportation',)
    od_room_no = fields.Char(string='Room No')
    od_pickup_point = fields.Char(string='Pickup Point',) 
    od_land_mark = fields.Char(string='Land Mark',)
    od_beneficiary_line = fields.One2many('od.hr.employee.beneficiary.line', 'employee_id', string='Beneficiary Lines')
    od_leave_history_line = fields.One2many('hr.holidays', 'employee_id', string='History Lines')
    od_document_line = fields.One2many('od.hr.employee.document.line', 'employee_id', string='Document Lines')
    od_street = fields.Char(string='Street')
    od_street2 = fields.Char(string='Street2')
    od_city = fields.Char(string='City')
    od_zip = fields.Char(string='Zip',size=24,change_default=True)
    od_state_id = fields.Many2one('res.country.state',string='State')
    od_country_id = fields.Many2one('res.country',string='Country')
    od_leave_salary_date = fields.Date(string='Leave Salary')
    od_based_on_basic = fields.Boolean(string='Based on Basic')
#    leave_eligible = fields.float()
    od_gratuity_date = fields.Date(string='Gratuity')
    od_parent = fields.Char(string='Manager Name',related='parent_id.name', store=True, readonly=True) 
    od_manager_mail = fields.Char(string='Manager Mail',related='parent_id.work_email', store=True, readonly=True)
#    od_employee_type_id = fields.Many2one('od.employee.type',string='Employee Type')
    od_leaves = fields.Float(string='Leaves',readonly="1")
    od_joining_date = fields.Date(string='Joining Date')
    od_job_role_line = fields.One2many('od.hr.job.line','employee_id',string='Job History',copy=False)
    od_father = fields.Char(string="Father Name")
    od_e_c1_name = fields.Char(string='Emergency Contact')
    od_e_c1_relationship = fields.Char(string='Relationship')
    od_e_c1_street = fields.Char(string='Street')
    od_e_c1_street2 = fields.Char(string='Street2')

    od_e_c1_city = fields.Char(string='City')
    od_e_c1_state_id = fields.Many2one('res.country.state',string='State')

    od_e_c1_country_id = fields.Many2one('res.country',string='Country')

    od_e_c1_ph1 = fields.Char(string='Phone1')

    od_e_c1_ph2 = fields.Char(string='Phone2')



    od_e_c2_name = fields.Char(string='Emergency Contact')
    od_e_c2_relationship = fields.Char(string='Relationship')
    od_e_c2_street = fields.Char(string='Street')
    od_e_c2_street2 = fields.Char(string='Street2')

    od_e_c2_city = fields.Char(string='City')
    od_e_c2_state_id = fields.Many2one('res.country.state',string='State')

    od_e_c2_country_id = fields.Many2one('res.country',string='Country')

    od_e_c2_ph1 = fields.Char(string='Phone1')

    od_e_c2_ph2 = fields.Char(string='Phone2')

    od_mc_dr_name = fields.Char(string='Doctor')
    od_mc_street = fields.Char(string='Street')
    od_mc_street2 = fields.Char(string='Street2')

    od_mc_city = fields.Char(string='City')
    od_mc_state_id = fields.Many2one('res.country.state',string='State')

    od_mc_country_id = fields.Many2one('res.country',string='Country')

    od_mc_ph1 = fields.Char(string='Phone1')

    od_mc_ph2 = fields.Char(string='Phone2')
    od_mc_blood_group = fields.Char(string='Blood Group')
    od_mc_medical_conditions = fields.Char(string='Medical Conditions')
    od_mc_allergies = fields.Char(string='Allergies')
    od_mc_medications = fields.Char(string='Current Medications')
    od_personal_email = fields.Char(string='Personal Email')

    od_document_count = fields.Float(string='Count',
        compute='_compute_document_count')

    od_document_line_count = fields.Float(string='Count',
        compute='_compute_document_line_count')

    

class od_hr_job_line(models.Model):
    _name='od.hr.job.line'
    employee_id = fields.Many2one('hr.employee', string='Employee')
    date_from = fields.Date(String='Date From')
    date_to = fields.Date(String='Date To')
    job_id = fields.Many2one('hr.job',string='Job Title')
    name = fields.Text(string='Responsibility')

class od_hr_employee_dependents_line(models.Model):
    _name = 'od.hr.employee.dependents.line'
    _description = "od.hr.employee.dependents.line"
    employee_id = fields.Many2one('hr.employee', string='Employee')
    contacts = fields.Many2one('res.partner', string='Contacts',)
    od_benefits_ids = fields.Many2many('od.hr.employee.benefits','employee_id','benefits_id',string='Benefits')
    relation_id = fields.Many2one('od.employee.relation', string='Relation',)


class od_hr_employee_relatives_line(models.Model):
    _name = 'od.hr.employee.relatives.line'
    _description = "od.hr.employee.relatives.line"
    employee_id = fields.Many2one('hr.employee', string='Employee')
    contacts = fields.Many2one('res.partner', string='Contacts',)
    relation_id = fields.Many2one('od.employee.relation', string='Relation',)


class od_hr_employee_education_line(models.Model):
    _name = 'od.hr.employee.education.line'
    _description = "od.hr.employee.education.line"
    employee_id = fields.Many2one('hr.employee', string='Employee')
    academic_qualification_id = fields.Many2one('od.employee.academic.qualification', string='Academic Qualification',)
    instituite = fields.Char(string='Institute')
    year = fields.Date(string='Year')
    country_id = fields.Many2one('res.country',string='Country')
class od_hr_employee_launguage_line(models.Model):
    _name = 'od.hr.employee.launguage.line'
    _description = "od.hr.employee.launguage.line"
    employee_id = fields.Many2one('hr.employee', string='Employee')
    launguage_id = fields.Many2one('res.lang', string='Launguage')
    speak = fields.Boolean(string='Speak',default=False)
    writes = fields.Boolean(string='Write',default=False)
    reads = fields.Boolean(string='Read',default=False)
class od_hr_employee_beneficiary_line(models.Model):
    _name = 'od.hr.employee.beneficiary.line'
    _description = "od.hr.employee.beneficiary.line"
    employee_id = fields.Many2one('hr.employee', string='Employee')
    contacts = fields.Many2one('res.partner', string='Contacts',)
    relation_id = fields.Many2one('od.employee.relation', string='Relation',)

class od_hr_employee_facilitates_line(models.Model):
    _name = 'od.hr.employee.facilitates.line'
    _description = "od.hr.employee.facilitates.line"
    employee_id = fields.Many2one('hr.employee', string='Employee')
    entitlement_id = fields.Many2one('od.employee.entitelment', string='Entitlement')
    asset_id = fields.Many2one('account.asset.asset',string='Asset')
    ref = fields.Char(string='Reference')
    od_from_date = fields.Date(string='From Date')




class od_hr_employee_benefits(models.Model):
    _name = 'od.hr.employee.benefits'
    _description = "od.hr.employee.benefits"
    name = fields.Char(string='Name',required="1")
    remarks = fields.Text(string='Notes')








class od_hr_employee_document_line(models.Model):
    _name = 'od.hr.employee.document.line'
    _description = "od.hr.employee.document.line"
    employee_id = fields.Many2one('hr.employee', string='Employee')
    document_type_id = fields.Many2one('od.employee.document.type',string='Document Type',required=True)
    document_referance = fields.Char(string='Document Reference')
    attach_file = fields.Binary(string='Scanned Copy')
    issue_date = fields.Date(string='Issue Date')
    expiry_date = fields.Date(string='Expiry Date')
    attach_fname = fields.Char(string='Comp', size=32)

    def default_get(self, cr, uid, ids,context=None):
        res = super(od_hr_employee_document_line, self).default_get(cr, uid, ids, context=context)
        res.update({'employee_id': context.get('active_id', False)})
        return res


class od_employee_relation(models.Model):
    _name = 'od.employee.relation'
    _description = "od.employee.relation"
    name = fields.Char(string='Name',required="1")  
    notes = fields.Text('Remarks')  




class od_employee_type(models.Model):
    _name = 'od.employee.type'
    _description = "od.employee.type"
    name = fields.Char(string='Name',required="1")  
    notes = fields.Text('Remarks')  







class od_employee_air_route(models.Model):
    _name = 'od.employee.air.route'
    _description = "od.employee.air.route"
    name = fields.Char(string='Name',required="1") 
    notes = fields.Text('Remarks')
class od_employee_academic_qualification(models.Model):
    _name = 'od.employee.academic.qualification'
    _description = "od.employee.academic.qualification"
    name = fields.Char(string='Name',required="1") 
    notes = fields.Text('Remarks')
class od_employee_accomadation(models.Model):
    _name = 'od.employee.accomadation'
    _description = "od.employee.accomadation"
    name = fields.Char(string='Name',required="1") 
    notes = fields.Text('Remarks')   

class od_employee_transportation(models.Model):
    _name = 'od.employee.transportation'
    _description = "od.employee.transportation"
    name = fields.Char(string='Name',required="1") 
    notes = fields.Text('Remarks')

class od_employee_document_type(osv.osv):
    _name = 'od.employee.document.type'
    _description = "od.employee.document.type"
    name = fields.Char(string='Name',required=True,size=64)
    code = fields.Char(string='Code',size=32)
    description = fields.Text(string='Description')
    custodian = fields.Selection([
            ('employee','Employee'),
            ('company','Company'),
        ], string='Custodian', required="1", default='company')

class od_employee_entitelment(models.Model):
    _name = 'od.employee.entitelment'
    _description = "od.employee.entitelment"
    name = fields.Char(string='Name',required="1") 
    notes = fields.Text('Remarks')  


class od_document_request(models.Model):
    _name = 'od.document.request'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "od.document.request"
    def od_get_company_id(self):
        return self.env.user.company_id
    company_id = fields.Many2one('res.company', 'Company',default=od_get_company_id)
    employee_id = fields.Many2one('hr.employee', string='Employee',required="1",track_visibility='onchange')
    document_type_id = fields.Many2one('od.employee.document.type',string='Document Type',required=True,track_visibility='onchange')
    purpose = fields.Many2one('od.employee.purpose',string='Purpose',required=True,track_visibility='onchange')
    notes = fields.Text(string='Remarks')  
    is_issued = fields.Boolean(string='Issued',track_visibility='onchange')
    is_returned = fields.Boolean(string='Returned',track_visibility='onchange')
    return_date = fields.Date(string='Returned Date',track_visibility='onchange')
    issued_date = fields.Date(string='Issued Date',track_visibility='onchange')
    expected_date = fields.Date(string='Expected Return Date',track_visibility='onchange')

    department_id = fields.Many2one('hr.department', string='Department',related='employee_id.department_id', store=True, readonly=True) 
    job_id = fields.Many2one('hr.job', string='Job',related='employee_id.job_id', store=True, readonly=True)
    address_home_id = fields.Many2one('res.partner', string='Home Address',related='employee_id.address_home_id', store=True, readonly=True)
#    custodian = fields.Char(string='Custodian',related='document_type_id.custodian', store=True, readonly=True)
    custodian = fields.Selection([
            ('employee','Employee'),
            ('company','Company'),
        ], string='Custodian', related='document_type_id.custodian', store=True, readonly=True)


    state = fields.Selection([
            ('draft','To Submit'),
            ('refused','Refused'),
            ('to_approve','To Approve'),
            ('first_approval','First Approval'),
            ('approved','Approved'),
        ], string='Status', index=True, readonly=True, default='to_approve',
        track_visibility='onchange')
    document_attach_here_line = fields.One2many('od.document.request.attach.here.line','document_attach_here_line_id',string='Attach Here')


#    def action_approved(self,cr,uid,ids,context=None):
#        self.write(cr, uid,ids, {'state': 'approved'})
#        return True

    def unlink(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.state not in ['draft']:
                raise osv.except_osv(_('Invalid Action!'), _('Cannot delete  which is in state \'%s\'.') %(rec.state,))
        return super(od_document_request, self).unlink(cr, uid, ids, context=context)

    def action_refused(self,cr,uid,ids,context=None):
        self.write(cr, uid,ids, {'state': 'refused'})
        return True
    def reset_to_draft(self,cr,uid,ids,context=None):
        self.write(cr, uid,ids, {'state': 'draft'})
        return True
#    def action_confirm(self,cr,uid,ids,context=None):
#        self.write(cr, uid,ids, {'state': 'to_approve'})
#        return True

#    def first_approval(self,cr,uid,ids,context=None):
##        self.signal_workflow(cr, uid, ids, 'first_approval')
#        self.write(cr, uid,ids, {'state': 'first_approval'})
##        self.signal_workflow(cr, uid, ids, 'first_approval')
#        return True
        

class od_document_request_attach_here_line(models.Model):
    _name = 'od.document.request.attach.here.line'
    _description = "od.document.request.attach.here.line"
    name = fields.Char(string='Description')
    scanned_copy = fields.Binary(string='Scanned Copy')
    scanned_fname = fields.Char(string='Comp', size=32)
    reference = fields.Char(string='Reference')
    issue_date = fields.Date(string='Issue Date')
    expiry_date = fields.Date(string='Expiry Date')
    document_attach_here_line_id = fields.Many2one('od.document.request',string='Document')


class od_employee_purpose(models.Model):
    _name = 'od.employee.purpose'
    _description = "od.employee.purpose"
    name = fields.Char(string='Name',required="1") 
    notes = fields.Text('Remarks')  




class od_employee_joining(models.Model):
    _name = 'od.employee.joining'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "od.employee.joining"
    employee_id = fields.Many2one('hr.employee', string='Employee',required="1",track_visibility='onchange')
    department_id = fields.Many2one('hr.department', string='Department',related='employee_id.department_id', store=True, readonly=True,track_visibility='onchange') 
    job_id = fields.Many2one('hr.job', string='Job',related='employee_id.job_id', store=True, readonly=True,track_visibility='onchange')
    address_home_id = fields.Many2one('res.partner', string='Home Address',related='employee_id.address_home_id', store=True, readonly=True,track_visibility='onchange')
    parent_id = fields.Many2one('hr.employee', string='Manager',related='employee_id.parent_id', store=True, readonly=True,track_visibility='onchange')
    joining_date = fields.Date(string='Joining Date',required="1",track_visibility='onchange')
    joining_document_line = fields.One2many('od.employee.joining.document.line','joining_id',string='Documents',track_visibility='onchange')
    notes = fields.Text(string='Remarks')


class od_employee_joining_document_line(models.Model):
    _name = 'od.employee.joining.document.line'
    _description = "od.employee.joining.document.line"
    joining_id = fields.Many2one('od.employee.joining',string='Joining')
    document_type_id = fields.Many2one('od.employee.document.type',string='Document Type',required=True)
    recieved = fields.Boolean(string='Recieved',default=False)
    recieved_date = fields.Date(string='Recieved Date')






class hr_salary_rule(models.Model):
    _inherit = 'hr.salary.rule'
    od_is_gratuity = fields.Boolean('Gratuity',default=False)
    od_is_leave_salary = fields.Boolean('Leave Salary',default=False)
    od_is_airfare = fields.Boolean('Airfare',default=False)

