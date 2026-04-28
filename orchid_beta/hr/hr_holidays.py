# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
from openerp.tools.translate import _
import copy
import math
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
import dateutil.relativedelta
import itertools
from lxml import etree
import openerp.addons.decimal_precision as dp
import time
from openerp import workflow
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from openerp import SUPERUSER_ID
from datetime import datetime,date
from datetime import timedelta
from datetime import date
import dateutil.relativedelta
from openerp.exceptions import Warning
from pprint import pprint
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
class hr_holidays(models.Model):
    _inherit = "hr.holidays"
    @api.model 
    def create(self ,vals):
        holiday_status_id = vals.get('holiday_status_id',False)
        if holiday_status_id and holiday_status_id !=5:
            date_from = vals.get('date_from')
            date_to = vals.get('date_to')
            date_from_split = date_from.split(' ')
            date_to_split = date_to.split(' ')
            if date_from_split and date_from_split[0]:
                date_from_new = date_from_split[0] + ' 03:00:00'
                vals['date_from'] = date_from_new
            if date_to_split and date_to_split[0]:
                date_to_new = date_to_split[0] + ' 15:00:00'
                vals['date_to'] = date_to_new


        return super(hr_holidays,self).create(vals)
    def get_time_diff(self,start_time,complete_time):
        start_time = datetime.strptime(start_time, DEFAULT_SERVER_DATETIME_FORMAT)
        complete_time = datetime.strptime(complete_time, DEFAULT_SERVER_DATETIME_FORMAT)
        diff = (complete_time -start_time)
        days = diff.days * 24
        seconds = diff.seconds
        hour= days + float(seconds)/3600
        return hour
    @api.one
    @api.depends('date_from','date_to')
    def od_compute_hours(self):
        date_from = self.date_from
        date_to = self.date_to
        if date_from and date_to:
            hour = self.get_time_diff(date_from,date_to)
            self.od_hour = hour
    od_remark = fields.Text(string="Remarks")
    od_hour = fields.Float(string="Hours",compute="od_compute_hours")
    od_exit_visa = fields.Selection([('not_required','Not Required'),('single','Single'),('multiple','Multiple')],string="Exit Re-Entry Visa",default="not_required")
    
    def od_send_mail_for_validation(self):
        email_obj = self.pool.get('email.template')
        saudi_comp =6
        emp_company_id = self.company_id.id
        template_id = 35
        if emp_company_id == saudi_comp:
            template_id = 78
        leave_id = self.id
        email_obj.send_mail(self.env.cr, self.env.uid, template_id,leave_id)
        return True
    
    @api.multi
    def od_check_access_approval(self):
        employee = self.employee_id
        leave_type = self.holiday_status_id and self.holiday_status_id or False
        uid = self._uid
        related_user_id = employee.user_id and employee.user_id.id
        first_user_id = employee.od_first_manager_id and employee.od_first_manager_id.id
        first_user_id_list = [first_user_id,2501,101,12]
        if not related_user_id:
            raise Warning("Related User Not Set In Employee Profile")
        manager_id  = employee.parent_id and employee.parent_id.id or False
        if uid == related_user_id:
            return False
        if uid not in first_user_id_list:
            raise Warning("You are not allowed to do the first approval for this employee, Please ask %s to do this." % employee.od_first_manager_id.name)
        if leave_type != 5:
            self.od_send_mail_for_validation()
        return True



    @api.multi
    @api.one
    @api.constrains('number_of_days_temp','holiday_status_id','employee_id','date_from','od_leave_eligible','od_leave_encashment','date_to', 'od_hour')
    def _check_constriant(self):
        company_id = self.company_id and self.company_id.id or False
        to_date = str(datetime.strptime(self.date_to, '%Y-%m-%d %H:%M:%S') + timedelta(hours=4))
        f_date = str(datetime.strptime(self.date_from, '%Y-%m-%d %H:%M:%S') + timedelta(hours=4))
        year_start_date = str(datetime.strptime(str(date(date.today().year, 1, 1)), "%Y-%m-%d"))
        year_end_date = str(datetime.strptime(str(date(date.today().year+1, 01, 01)), "%Y-%m-%d"))
        x_start_from = self.date_from[:4] + '-'+'01'+'-'+'01'
        x_end_to = self.date_from[:4] + '-'+'12'+'-'+'31'
        to_date = to_date[:10]
        f_date = f_date[:10]
        if to_date > x_end_to or to_date < x_start_from:
            raise Warning(_("You cannot have one leave over different years.Kindly apply for 2 different leaves for each year"))
  
        
        od_leave_encashment = self.od_leave_encashment
        holiday_status_id = self.holiday_status_id and self.holiday_status_id.id

        parameter_obj = self.env['ir.config_parameter']
        parameter_ids = parameter_obj.search([('key', '=', 'def_short_leave')])
        if not parameter_ids:
            raise Warning(_("create short leave in parameter with key def_short_leave"))

        x_id = parameter_ids.od_model_id and parameter_ids.od_model_id.id
        if holiday_status_id == x_id:
            if to_date != f_date:
                raise Warning(_("Leave Start Date and End Date must be same"))
            if self.od_hour > 4:
                raise Warning(_("Short leaves cannot extend more than 4 hours !!"))
                

        number_of_days_temp = self.number_of_days_temp
        leave_request_date = str(self.date_from)
        od_leave_eligible = self.od_leave_eligible
        leave_request_date = datetime.strptime(leave_request_date[:10],"%Y-%m-%d")
        employee_id = self.employee_id and self.employee_id.id
        leave_taken_upto_current_date = 0
        if holiday_status_id ==1:

##committed as per firos(proof:#BETA  @RM  While leave applaying legal leave  need to change validation as  "Leave eligible days <= Requested days')
#            legal_leave_ids = self.env['hr.holidays'].search([('employee_id', '=', employee_id), ('holiday_status_id', '=', holiday_status_id),('state', 'in', ('validate','od_resumption_to_approve','od_approved')),('date_from','<',str(leave_request_date)),('date_from','>',year_start_date)])
#            for obj in legal_leave_ids:
#                leave_taken_upto_current_date += obj.number_of_days_temp
#            if leave_taken_upto_current_date + number_of_days_temp > od_leave_eligible:
#                raise Warning(_("leave not eligible"))

            if not od_leave_encashment and number_of_days_temp > od_leave_eligible:
                raise Warning(_("Leave not eligible for requested number of days. Kindly take email approval from your manager for this leave and contact administrator"))
            od_joining_date = self.env['hr.employee'].browse(employee_id).od_joining_date or False
            total_days = 0
            od_joining_date = datetime.strptime(od_joining_date, "%Y-%m-%d")
            total_days = (datetime.strptime(str(leave_request_date), '%Y-%m-%d %H:%M:%S') - datetime.strptime(str(od_joining_date), '%Y-%m-%d %H:%M:%S')).days


            parameter_obj = self.env['ir.config_parameter']
            parameter_ids = parameter_obj.search([('key', '=', 'def_wrk_days_year')])
            if not parameter_ids:
                raise osv.except_osv(_('Settings Warning!'),_('def_wrk_days_year configure in parameter setting'))
            wrking_days = float(parameter_obj.value)



            if not od_leave_encashment and total_days < wrking_days:
                raise osv.except_osv(_('Settings Warning!'),_('not eligible for leave'))
            #Added on 20Jul2023 by Aslam as requested by Elayyan and KSA HR
            if not od_leave_encashment:
                create_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                create_date = datetime.strptime(create_date, '%Y-%m-%d %H:%M:%S')
                if self.date_from:
                    date_from =datetime.strptime(self.date_from, '%Y-%m-%d %H:%M:%S')
                    delta = date_from - create_date
                    no_of_days = self.number_of_days_temp
                    if no_of_days > 7 and delta.days < 10 and company_id == 6 and not self.env.user.id in (2501,154):
                        raise Warning('Your leave cannot be submitted. Legal leave longer than 7 days must be submitted 10 days in advance.')
                    
                
        if holiday_status_id == 2:
            sick_leave_ids = self.env['hr.holidays'].search([('employee_id', '=', employee_id), ('holiday_status_id', '=', holiday_status_id),('state', 'not in', ('cancel','refuse')),('date_from','<',str(leave_request_date)),('date_from','>',year_start_date)])
            leave_sick_taken_upto_current_date = 0
            for obj in sick_leave_ids:
                leave_sick_taken_upto_current_date += obj.number_of_days_temp
            if leave_sick_taken_upto_current_date + number_of_days_temp > 90:
                raise Warning(_("sick leave cannot apply more than 90 days"))

        return True
