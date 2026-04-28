# -*- coding: utf-8 -*-
import time
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

from openerp import models, fields, api, _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from openerp.osv import osv


class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    # @api.one
    # @api.depends('company_id', 'holiday_status_id')
    # def _compute_vac_terms(self):
    #     print("_compute_vac_terms")
    #     print("self.company_id", self.company_id)
    #     print("self.holiday_status_id", self.holiday_status_id)
    #     if self.company_id.id == 6 and self.holiday_status_id:
    #         print("!!!!!!!!!!!!!!!!!!!!!!!")
    #         self.vac_terms = self.holiday_status_id.vac_terms
    #         print("@@@@@@@@@@@@@@@@@@@")
    #         self.vac_terms_ar = self.holiday_status_id.vac_terms_ar

    @api.one
    def write(self, vals):
        print("vals", vals)
        current_state = self.state
        if vals.get('od_resumption_date') and current_state == 'validate':
            self.sudo().write({'state': 'od_resumption_to_approve'})
            # self.state = 'od_resumption_to_approve'
            self.sudo().signal_workflow('resumption_to_approve')
        result = super(HrHolidays, self).write(vals)
        current_company = self.company_id
        print("self", self)
        print("current_company", current_company)
        res = self
        if vals.get('holiday_status_id') or vals.get('od_start') or vals.get('od_end'):
            if not res.ignore_exception:
                self.action_check_consicutive_week(res)
                if res.holiday_status_id.id == 2:
                    self.action_check_sick_leave(res)
                if res.company_id.id == 6:
                    self.action_check_unpaid_leaves(res)
                    if res.holiday_status_id.id == 8:
                        self.action_check_death_leave(res)
                    if res.holiday_status_id.id == 9:
                        self.action_check_marriage_leave(res)
                    if res.holiday_status_id.id == 14:
                        self.action_check_maternity_leave(res)
                    if res.holiday_status_id.id == 11:
                        self.action_check_newborn_leave(res)
                    if res.holiday_status_id.id == 7:
                        self.action_check_haj_leave(res)
                if res.company_id.id == 1:
                    self.action_check_probation_period(res)

        return result

    @api.one
    @api.depends('date_from', 'date_to')
    def od_compute_hours(self):
        date_from = self.date_from
        date_to = self.date_to
        if date_from and date_to:
            hour = self.get_time_diff(date_from, date_to)
            self.od_hour = hour

    od_remark = fields.Text(string="Remarks")
    od_hour = fields.Float(string="Hours", compute="od_compute_hours")

    @api.one
    @api.depends('od_start', 'od_end', 'holiday_status_id')
    def _get_number_of_days(self):
        holiday_status_id = self.holiday_status_id and self.holiday_status_id.id
        od_start = self.od_start
        od_end = self.od_end

        # For short leaves we set number of days default to 1
        if holiday_status_id == 5:
            self.number_of_days_temp = 1.0

        if od_end:
            start = datetime.strptime(od_start, DEFAULT_SERVER_DATE_FORMAT)
            end = datetime.strptime(od_end, DEFAULT_SERVER_DATE_FORMAT)
            if holiday_status_id == 5:
                self.od_number_of_days = 1
            else:
                no_of_days = (end - start).days + 1
                self.od_number_of_days = no_of_days

    @api.onchange('od_start', 'od_end')
    def onchange_start_end(self):
        print("%%%%%%%%%%%%%%%%%%%%%%%%")
        holiday_status_id = self.holiday_status_id and self.holiday_status_id.id
        od_start = self.od_start
        od_end = self.od_end

        if self.od_start:
            start = od_start + ' 03:00:00'
            self.date_from = start

        if self.od_end:
            end = od_end + ' 12:30:00'
            self.date_to = end

            start = datetime.strptime(od_start, DEFAULT_SERVER_DATE_FORMAT)
            end = datetime.strptime(od_end, DEFAULT_SERVER_DATE_FORMAT)
            if holiday_status_id == 5:
                self.number_of_days_temp = 1.0
            else:
                no_of_days = (end - start).days + 1
                self.number_of_days_temp = no_of_days

    od_start = fields.Date(string="Date Start")
    od_end = fields.Date(string="Date End")
    od_number_of_days = fields.Float(string="Number of Days", compute=_get_number_of_days)
    allow_resumption = fields.Boolean(string="Allow Resumption")
    ignore_exception = fields.Boolean(string="Ignore Exception")
    vac_terms = fields.Text('Vacation Terms', related="holiday_status_id.vac_terms")
    vac_terms_ar = fields.Text('Vacation Terms Arabic', related="holiday_status_id.vac_terms_ar")

    def onchange_holiday_status_id(self, cr, uid, ids, holiday_status_id=False, context=None):
        res = {}
        print("onchange_holiday_status_id")
        print("holiday_status_id", holiday_status_id)
        # if holiday_status_id:
        #     employee_pool = self.pool.get('hr.employee')
        #     emp_obj = employee_pool.browse(cr,uid,manager_id)
        #     email = emp_obj.work_email
        #     res['value'] = {'email': email}
        return res

    # @api.one
    # @api.onchange('holiday_status_id')
    # def onchange_holiday_status_id_check(self):
    #     print("onchange_holiday_status_id_check")
    #     holiday_status_id = self.holiday_status_id and self.holiday_status_id.id
    #     if self.company_id and self.company_id.id == 6:
    #         if holiday_status_id in [4,13]:
    #             raise Warning("This Leave Type Must be Applied through the HR Team. Send email to the HR team at hr.ksa@betait.net")

    # @api.one
    def action_check_consicutive_week(self, res):
        if res.holiday_status_id.id == 1:
            start_date = datetime.strptime(res.od_start, "%Y-%m-%d")
            three_days_before_start_date = start_date - timedelta(days=3)
            start_weekday = three_days_before_start_date.weekday()
            # start_weekday = (start_weekday + 1) % 7
            end_date = datetime.strptime(res.od_end, "%Y-%m-%d")
            three_days_after_end_date = end_date + timedelta(days=3)
            end_weekday = three_days_after_end_date.weekday()
            # end_weekday = (end_weekday + 1) % 7
            if res.company_id.id == 1:
                if start_weekday == 4:
                    date_string = three_days_before_start_date.strftime("%Y-%m-%d")
                    domain = [('employee_id', '=', res.employee_id.id), ('state', 'not in', ['cancel', 'refuse']),
                              ('od_end', '=', date_string)]

                    leaves = self.env['hr.holidays'].search(domain)
                    if leaves:
                        raise osv.except_osv(_('Warning!'),
                                             _('Applying for a second leave immediately following an existing leave to avoid weekends is not permitted. You may be required to extend your current leave instead.'))
                if end_weekday == 0:
                    end_date_string = three_days_after_end_date.strftime("%Y-%m-%d")
                    domain = [('employee_id', '=', res.employee_id.id), ('state', 'not in', ['cancel', 'refuse']),
                              ('od_start', '=', end_date_string)]

                    leaves = self.env['hr.holidays'].search(domain)
                    if leaves:
                        raise osv.except_osv(_('Warning!'),
                                             _('Applying for a leave preceding to an existing leave to avoid weekends is not permitted. You may be required to extend your existing leave instead.'))

            if res.company_id.id == 6:
                if start_weekday == 3:
                    date_string = three_days_before_start_date.strftime("%Y-%m-%d")
                    domain = [('employee_id', '=', res.employee_id.id), ('state', 'not in', ['cancel', 'refuse']),
                              ('od_end', '=', date_string)]

                    leaves = self.env['hr.holidays'].search(domain)
                    if leaves:
                        raise osv.except_osv(_('Warning!'),
                                             _('Applying for a second leave immediately following an existing leave to avoid weekends is not permitted. You may be required to extend your current leave instead.'))
                if end_weekday == 6:
                    date_string = three_days_after_end_date.strftime("%Y-%m-%d")
                    domain = [('employee_id', '=', res.employee_id.id), ('state', 'not in', ['cancel', 'refuse']),
                              ('od_start', '=', date_string)]

                    leaves = self.env['hr.holidays'].search(domain)
                    if leaves:
                        raise osv.except_osv(_('Warning!'),
                                             _('Applying for a leave preceding to an existing leave to avoid weekends is not permitted. You may be required to extend your existing leave instead.'))

    def action_check_probation_period(self, res):
        if res.holiday_status_id.id in [1, 2]:
            start_date = datetime.strptime(res.od_start, "%Y-%m-%d")
            joining_date = res.employee_id and res.employee_id.od_joining_date or False
            joining_date = datetime.strptime(joining_date, "%Y-%m-%d")
            six_month = (joining_date + timedelta(6 * 365 / 12))
            if start_date < six_month:
                raise osv.except_osv(_('Warning!'),
                                     _('Your are not allowed to apply for paid / sick  leave because you have not completed six months of employment from your joining date. Kindly contact HR admin for more info.'))

    def action_check_unpaid_leaves(self, res):
        if self.env.user.id not in [154, 2501,268]:
            if res.holiday_status_id.id in [4, 13]:
                raise osv.except_osv(_('Warning!'),
                                     _('This Leave Type Must be Applied through the HR Team. Please send email to the HR team at hr.ksa@betait.net'))

    def action_check_sick_leave(self, res):
        year_start_date = str(datetime.strptime(str(date(date.today().year, 1, 1)), "%Y-%m-%d"))
        year_end_date = str(datetime.strptime(str(date(date.today().year + 1, 01, 01)), "%Y-%m-%d"))
        domain = [('employee_id', '=', res.employee_id.id), ('state', 'not in', ['cancel', 'refuse']),
                  ('holiday_status_id', '=', 2), ('od_start', '>', year_start_date), ('od_end', '<', year_end_date)]
        leaves = self.env['hr.holidays'].search(domain)
        print("leaves", leaves)
        sick_leave_taken = 0

        if leaves:
            for leave in leaves:
                sick_leave_taken = sick_leave_taken + leave.od_number_of_days
        if res.company_id.id == 6:
            if sick_leave_taken > 30:
                raise osv.except_osv(_('Warning!'),
                                     _('You have exceeded your annual sick leave limit. Please consult with the HR team for further assistance.'))
        if res.company_id.id == 1:
            if sick_leave_taken > 15:
                raise osv.except_osv(_('Warning!'),
                                     _('You have exceeded your annual sick leave limit. Please consult with the HR team for further assistance.'))

    def action_check_death_leave(self, res):
        year_start_date = str(datetime.strptime(str(date(date.today().year, 1, 1)), "%Y-%m-%d"))
        year_end_date = str(datetime.strptime(str(date(date.today().year + 1, 01, 01)), "%Y-%m-%d"))
        domain = [('employee_id', '=', res.employee_id.id), ('state', 'not in', ['cancel', 'refuse']),
                  ('holiday_status_id', '=', 8), ('od_start', '>', year_start_date), ('od_end', '<', year_end_date)]
        leaves = self.env['hr.holidays'].search(domain)
        print("leaves", leaves)
        death_leave_taken = 0
        if leaves:
            for leave in leaves:
                death_leave_taken = death_leave_taken + leave.od_number_of_days
        if death_leave_taken > 5:
            raise osv.except_osv(_('Warning!'),
                                 _('Leave is not eligible for the requested number of days for this leave type. Please reach out to the HR team for more help.'))

    def action_check_marriage_leave(self, res):
        year_start_date = str(datetime.strptime(str(date(date.today().year, 1, 1)), "%Y-%m-%d"))
        year_end_date = str(datetime.strptime(str(date(date.today().year + 1, 01, 01)), "%Y-%m-%d"))
        domain = [('employee_id', '=', res.employee_id.id), ('state', 'not in', ['cancel', 'refuse']),
                  ('holiday_status_id', '=', 9), ('od_start', '>', year_start_date), ('od_end', '<', year_end_date)]
        leaves = self.env['hr.holidays'].search(domain)
        print("leaves", leaves)
        marriage_leave_taken = 0
        if leaves:
            for leave in leaves:
                marriage_leave_taken = marriage_leave_taken + leave.od_number_of_days
        if marriage_leave_taken > 5:
            raise osv.except_osv(_('Warning!'),
                                 _('Leave is not eligible for the requested number of days for this leave type. Please reach out to the HR team for more help.'))

    def action_check_maternity_leave(self, res):
        year_start_date = str(datetime.strptime(str(date(date.today().year, 1, 1)), "%Y-%m-%d"))
        year_end_date = str(datetime.strptime(str(date(date.today().year + 1, 01, 01)), "%Y-%m-%d"))
        domain = [('employee_id', '=', res.employee_id.id), ('state', 'not in', ['cancel', 'refuse']),
                  ('holiday_status_id', '=', 14), ('od_start', '>', year_start_date), ('od_end', '<', year_end_date)]
        leaves = self.env['hr.holidays'].search(domain)
        print("leaves", leaves)
        maternity_leave_taken = 0
        if leaves:
            for leave in leaves:
                maternity_leave_taken = maternity_leave_taken + leave.od_number_of_days
        if maternity_leave_taken > 70:
            raise osv.except_osv(_('Warning!'),
                                 _('Leave is not eligible for the requested number of days for this leave type. Please reach out to the HR team for more help.'))

    def action_check_newborn_leave(self, res):
        print("action_check_newborn_leave")
        year_start_date = str(datetime.strptime(str(date(date.today().year, 1, 1)), "%Y-%m-%d"))
        year_end_date = str(datetime.strptime(str(date(date.today().year + 1, 01, 01)), "%Y-%m-%d"))
        domain = [('employee_id', '=', res.employee_id.id), ('state', 'not in', ['cancel', 'refuse']),
                  ('holiday_status_id', '=', 11), ('od_start', '>', year_start_date), ('od_end', '<', year_end_date)]
        leaves = self.env['hr.holidays'].search(domain)
        print("leaves", leaves)
        newborn_leave_taken = 0
        if leaves:
            for leave in leaves:
                newborn_leave_taken = newborn_leave_taken + leave.od_number_of_days
        print("newborn_leave_taken", newborn_leave_taken)
        if newborn_leave_taken > 3:
            raise osv.except_osv(_('Warning!'),
                                 _('Leave is not eligible for the requested number of days for this leave type. Please reach out to the HR team for more help.'))

    def action_check_haj_leave(self, res):
        domain = [('employee_id', '=', res.employee_id.id), ('state', 'not in', ['cancel', 'refuse']),
                  ('holiday_status_id', '=', 7)]
        leaves = self.env['hr.holidays'].search(domain)
        print("leaves", leaves)
        haj_leave_taken = 0
        if leaves:
            for leave in leaves:
                haj_leave_taken = haj_leave_taken + leave.od_number_of_days
        if haj_leave_taken > 10:
            raise osv.except_osv(_('Warning!'),
                                 _('Leave is not eligible for the requested number of days for this leave type. Please reach out to the HR team for more help.'))

    @api.model
    def create(self, vals):
        res = super(HrHolidays, self).create(vals)
        if not res.ignore_exception:
            self.action_check_consicutive_week(res)
            if res.holiday_status_id.id == 2:
                self.action_check_sick_leave(res)
            if res.company_id.id == 6:
                self.action_check_unpaid_leaves(res)
                if res.holiday_status_id.id == 8:
                    self.action_check_death_leave(res)
                if res.holiday_status_id.id == 9:
                    self.action_check_marriage_leave(res)
                if res.holiday_status_id.id == 14:
                    self.action_check_maternity_leave(res)
                if res.holiday_status_id.id == 11:
                    self.action_check_newborn_leave(res)
                if res.holiday_status_id.id == 7:
                    self.action_check_haj_leave(res)
            if res.company_id.id == 1:
                self.action_check_probation_period(res)
        return res


class HrHolidayStatus(models.Model):
    _inherit = 'hr.holidays.status'

    def od_get_company_id(self):
        return self.env.user.company_id

    company_id = fields.Many2one('res.company', string='Company', default=od_get_company_id)
    vac_terms = fields.Text('Vacation Terms')
    vac_terms_ar = fields.Text('Vacation Terms Arabic')
