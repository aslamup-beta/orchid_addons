import datetime
import math
import time
from operator import attrgetter

from openerp.exceptions import Warning
from openerp import tools
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import models, fields, api
from datetime import date, timedelta, datetime


class HrHolidaysWfh(models.Model):
    _name = "hr.holidays.wfh"
    _description = "Work From Home"
    _rec_name = 'employee_id'
    _order = "date_from asc"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    def _employee_get(self, cr, uid, context=None):
        emp_id = context.get('default_employee_id', False)
        if emp_id:
            return emp_id
        ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
        if ids:
            return ids[0]
        return False

    def _compute_number_of_days(self, cr, uid, ids, name, args, context=None):
        result = {}
        for hol in self.browse(cr, uid, ids, context=context):
            result[hol.id] = hol.number_of_days_temp
        return result

    def _get_can_reset(self, cr, uid, ids, name, arg, context=None):
        """User can reset a leave request if it is its own leave request or if
        he is an Hr Manager. """
        user = self.pool['res.users'].browse(cr, uid, uid, context=context)
        group_hr_manager_id = \
            self.pool.get('ir.model.data').get_object_reference(cr, uid, 'base', 'group_hr_manager')[
                1]
        if group_hr_manager_id in [g.id for g in user.groups_id]:
            return dict.fromkeys(ids, True)
        result = dict.fromkeys(ids, False)
        for holiday in self.browse(cr, uid, ids, context=context):
            if holiday.employee_id and holiday.employee_id.user_id and holiday.employee_id.user_id.id == uid:
                result[holiday.id] = True
        return result

    def _check_date(self, cr, uid, ids, context=None):
        for holiday in self.browse(cr, uid, ids, context=context):
            domain = [
                ('date_from', '<=', holiday.date_to),
                ('date_to', '>=', holiday.date_from),
                ('employee_id', '=', holiday.employee_id.id),
                ('id', '!=', holiday.id),
                ('state', 'not in', ['cancel', 'refuse']),
            ]
            nholidays = self.search_count(cr, uid, domain, context=context)
            if nholidays:
                return False
        return True

    _check_holidays = lambda self, cr, uid, ids, context=None: self.check_holidays(cr, uid, ids, context=context)

    state = fields.Selection(
        [('draft', 'To Submit'), ('waiting_approval', 'To Approve'), ('hr_approval', 'HR Approval'),
         ('confirmed', 'Confirmed'), ('refuse', 'Refused'), ('cancel', 'Cancelled')],
        'Status', readonly=True, track_visibility='onchange', copy=False)
    date_from = fields.Date('Start Date', readonly=True,
                            states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]},
                            select=True, copy=False, track_visibility='onchange')
    date_to = fields.Date('End Date', readonly=True,
                          states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]},
                          copy=False, track_visibility='onchange')
    name = fields.Text('Description')
    employee_id = fields.Many2one('hr.employee', "Employee", select=True, invisible=False, readonly=True,
                                  track_visibility='onchange',
                                  states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    manager_id = fields.Many2one('res.users', string="Direct Manager")
    number_of_days_temp = fields.Float('Allocation', readonly=True,
                                       states={'draft': [('readonly', False)],
                                               'confirm': [('readonly', False)]},
                                       copy=False)
    department_id = fields.Many2one('hr.department', string="Department", related="employee_id.department_id",
                                    readonly=True, store=True)
    user_id = fields.Many2one('res.users', string="User", related="employee_id.user_id", readonly=True)
    wfh_type = fields.Selection(
        [('wfh', 'Work From Home'), ('trip', 'Business Trip')],
        'Type', track_visibility='onchange', copy=False, default='wfh')
    number_of_days = fields.Float(string='Number of Days', readonly=True, store=True, related="number_of_days_temp")
    can_reset = fields.Boolean(string='Can Reset', readonly=True, store=True, compute='_get_can_reset')

    date_log_history_line = fields.One2many('date.log.wfh', 'wfh_id', strint="Date Log History",
                                            readonly=True, copy=False)

    def od_get_company_id(self):
        return self.env.user.company_id

    company_id = fields.Many2one('res.company', string='Company', default=od_get_company_id)
    _defaults = {
        'employee_id': _employee_get,
        'state': 'draft',
        'wfh_type': 'wfh',
        'user_id': lambda obj, cr, uid, context: uid,
    }
    _constraints = [
        (_check_date, 'You can not have 2 leaves that overlaps on same day!', ['date_from', 'date_to']),
    ]

    _sql_constraints = [
        ('date_check2', "CHECK (date_from <= date_to )", "The start date must be anterior to the end date."),
        ('date_check', "CHECK ( number_of_days_temp >= 0 )", "The number of days must be greater than 0."),
    ]

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        employee = self.employee_id or False
        if employee:
            self.manager_id = employee.sudo().parent_id and employee.sudo().parent_id.user_id and employee.sudo().parent_id.user_id.id or False

    # TODO: can be improved using resource calendar method
    def _get_number_of_days(self, date_from, date_to):
        """Returns a float equals to the timedelta between two dates given as string."""

        DATETIME_FORMAT = "%Y-%m-%d"
        from_dt = datetime.strptime(date_from, DATETIME_FORMAT)
        to_dt = datetime.strptime(date_to, DATETIME_FORMAT)
        timedelta = to_dt - from_dt
        diff_day = timedelta.days + float(timedelta.seconds) / 86400
        return diff_day

    def unlink(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.state not in ['draft', 'cancel']:
                raise osv.except_osv(_('Warning!'),
                                     _('You cannot delete a wfh which is in %s state.') % (rec.state))
        return super(HrHolidaysWfh, self).unlink(cr, uid, ids, context)

    def od1_send_mail(self, template):
        ir_model_data = self.env['ir.model.data']
        email_obj = self.pool.get('email.template')
        template_id = ir_model_data.get_object_reference('beta_customisation', template)[1]
        rec_id = self.id
        email_obj.send_mail(self.env.cr, self.env.uid, template_id, rec_id, force_send=True)

    def onchange_date_from(self, cr, uid, ids, date_to, date_from):
        """
        If there are no date set for date_to, automatically set one 8 hours later than
        the date_from.
        Also update the number_of_days.
        """

        DATETIME_FORMAT = "%Y-%m-%d"
        # date_to has to be greater than date_from
        if (date_from and date_to) and (date_from > date_to):
            raise osv.except_osv(_('Warning!'), _('The start date must be anterior to the end date.'))

        result = {'value': {}}

        # No date_to set so far: automatically compute one 8 hours later
        # if date_from and not date_to:
        #     date_to_with_delta = datetime.strptime(date_from,
        #                                            DATETIME_FORMAT) + timedelta(
        #         hours=8)
        #     result['value']['date_to'] = str(date_to_with_delta)

        # Compute and update the number of days
        if (date_to and date_from) and (date_from <= date_to):
            diff_day = self._get_number_of_days(date_from, date_to)
            result['value']['number_of_days_temp'] = round(math.floor(diff_day)) + 1
        else:
            result['value']['number_of_days_temp'] = 0

        return result

    def onchange_date_to(self, cr, uid, ids, date_to, date_from):
        """
        Update the number_of_days.
        """

        # date_to has to be greater than date_from
        if (date_from and date_to) and (date_from > date_to):
            raise osv.except_osv(_('Warning!'), _('The start date must be anterior to the end date.'))

        result = {'value': {}}

        # Compute and update the number of days
        if (date_to and date_from) and (date_from <= date_to):
            diff_day = self._get_number_of_days(date_from, date_to)
            result['value']['number_of_days_temp'] = round(math.floor(diff_day)) + 1
        else:
            result['value']['number_of_days_temp'] = 0

        return result

    def od_send_mail(self, template):
        ir_model_data = self.env['ir.model.data']
        email_obj = self.pool.get('email.template')
        if self.company_id.id == 6:
            template = template + '_saudi'
        template_id = ir_model_data.get_object_reference('beta_extended', template)[1]
        rec_id = self.id
        email_obj.send_mail(self.env.cr, self.env.uid, template_id, rec_id, force_send=True)
        return True

    def get_first_and_last_dates_of_year(self, start, end):
        # Get the current year
        start_date = datetime.strptime(start, "%Y-%m-%d")
        end_date = datetime.strptime(end, "%Y-%m-%d")
        start_year = start_date.year
        end_year = end_date.year
        # current_year = datetime.now().year

        if start_year != end_year:
            raise osv.except_osv(_('Warning!'), _('You are not allowed to overlap 2 years'))

        # Create datetime objects for the first and last days of the current year
        first_date = datetime(start_year, 1, 1)
        last_date = datetime(start_year, 12, 31)

        return first_date, last_date

    def check_same_month(self, start, end):
        start_date = datetime.strptime(start, "%Y-%m-%d")
        end_date = datetime.strptime(end, "%Y-%m-%d")
        start_month = start_date.month
        end_month = end_date.month
        result = True
        if start_month == end_month:
            result = True
        else:
            result = False
        return result

    @api.one
    def action_check_consicutive_week(self, limit, domain, start, end):
        start_date = datetime.strptime(start, "%Y-%m-%d")
        end_date = datetime.strptime(end, "%Y-%m-%d")
        three_days_ago_start = start_date - timedelta(days=3)
        three_days_after_end = end_date + timedelta(days=3)
        domain = [('employee_id', '=', self.employee_id.id), ('state', 'in', ['hr_approval', 'confirmed']),
                  ('date_to', '>=', three_days_ago_start), ('date_to', '<=', start_date)]

        before_wfhs = self.env['hr.holidays.wfh'].search(domain)
        no_of_days = 0
        if before_wfhs:
            for b_wfh in before_wfhs:
                no_of_days = no_of_days + b_wfh.number_of_days
        if (no_of_days + self.number_of_days) > limit.max_days:
            raise osv.except_osv(_('Warning!'),
                                 _('You are not allowed to take more than %s days WFH within any 2 consecutive weeks') % (
                                     limit.max_days))

        after_domain = [('employee_id', '=', self.employee_id.id), ('state', 'in', ['hr_approval', 'confirmed']),
                        ('date_from', '>=', end_date), ('date_from', '<=', three_days_after_end)]

        after_wfhs = self.env['hr.holidays.wfh'].search(after_domain)
        after_no_of_days = 0
        if after_wfhs:
            for a_wfh in after_wfhs:
                after_no_of_days = after_no_of_days + a_wfh.number_of_days
        if (after_no_of_days + self.number_of_days) > limit.max_days:
            raise osv.except_osv(_('Warning!'),
                                 _('You are not allowed to take more than %s days WFH within any 2 consecutive weeks') % (
                                     limit.max_days))
        # ddd
        return True

    def action_check_yearly_limit(self, limit, domain, start, end):
        first_day, last_day = self.get_first_and_last_dates_of_year(start, end)
        domain = [('employee_id', '=', self.employee_id.id), ('state', 'in', ['hr_approval', 'confirmed']),
                  ('date_from', '>=', first_day), ('date_to', '<=', last_day)]
        wfhs = self.env['hr.holidays.wfh'].search(domain)
        no_of_days = 0
        if wfhs:
            for wfh in wfhs:
                no_of_days = no_of_days + wfh.number_of_days
        if no_of_days > limit.yearly_limit:
            raise osv.except_osv(_('Warning!'),
                                 _('Your yearly work from home limit of %s days exceeded.') % (limit.yearly_limit))
        # ddd
        return True

    @api.one
    def action_check_monthly_limit(self, limit, domain, start, end):
        same_month = self.check_same_month(start, end)
        total_monthly = 0
        monthly_wfh_approved_1 = 0
        monthly_wfh_approved_2 = 0
        monthly_wfh_requested_1 = 0
        monthly_wfh_requested_2 = 0
        if same_month:
            monthly_wfh_approved_1 = self.get_monthly_wfh(domain, start)
            monthly_wfh_requested_1 = self.days_between_dates(start, end) + 1
            total_monthly = monthly_wfh_approved_1 + monthly_wfh_requested_1
            if total_monthly > limit.monthly_limit:
                raise osv.except_osv(_('Warning!'), _('Your monthly work from home limit of %s days exceeded.') % (
                    limit.monthly_limit))
        else:
            monthly_wfh_approved_1 = self.get_monthly_wfh(domain, start)
            first_day, last_day = self.get_first_and_last_day(start)
            last_day = last_day.strftime('%Y-%m-%d')  # Example format: '2024-09-11'
            monthly_wfh_requested_1 = self.days_between_dates(start, last_day) + 1
            total_monthly_1 = monthly_wfh_approved_1 + monthly_wfh_requested_1
            if total_monthly_1 > limit.monthly_limit:
                raise osv.except_osv(_('Warning!'), _('Your monthly work from home limit of %s days exceeded.') % (
                    limit.monthly_limit))
            monthly_wfh_approved_2 = self.get_monthly_wfh(domain, end)
            first_day, last_day = self.get_first_and_last_day(end)
            first_day = first_day.strftime('%Y-%m-%d')
            monthly_wfh_requested_2 = self.days_between_dates(first_day, end) + 1
            total_monthly_2 = monthly_wfh_approved_2 + monthly_wfh_requested_2
            if total_monthly_2 > limit.monthly_limit:
                raise osv.except_osv(_('Warning!'), _('Your monthly work from home limit of %s days exceeded.') % (
                    limit.monthly_limit))
        return True

    def get_monthly_wfh(self, domain, start):
        first_day, last_day = self.get_first_and_last_day(start)
        domain = [('employee_id', '=', self.employee_id.id), ('state', 'in', ['hr_approval', 'confirmed']), '|',
                  ('date_from', '>=', first_day), ('date_to', '<=', last_day)]
        wfhs = self.env['hr.holidays.wfh'].search(domain)
        no_of_days = 0
        if wfhs:
            for wfh in wfhs:
                start = datetime.strptime(wfh.date_from, '%Y-%m-%d')
                end = datetime.strptime(wfh.date_to, '%Y-%m-%d')
                if first_day <= start <= last_day or first_day <= end <= last_day:
                    same_month = self.check_same_month(wfh.date_from, wfh.date_to)
                    if same_month:
                        no_of_days = no_of_days + wfh.number_of_days
                    else:
                        days = 0
                        if wfh.date_from > first_day and first_day < wfh.date_to > last_day:
                            first_day = first_day.strftime('%Y-%m-%d')
                            days = self.days_between_dates(first_day, wfh.date_to) + 1
                        if wfh.date_to < last_day and first_day < wfh.date_from > last_day:
                            last_day = last_day.strftime('%Y-%m-%d')
                            days = self.days_between_dates(wfh.date_from, last_day) + 1
                        no_of_days = no_of_days + days
        monthly_wfh = no_of_days
        return monthly_wfh

    def days_between_dates(self, date_str1, date_str2):
        # Define the date format
        date_format = '%Y-%m-%d'

        # Parse the date strings into datetime objects
        date1 = datetime.strptime(date_str1, date_format)
        date2 = datetime.strptime(date_str2, date_format)

        # Calculate the difference between the dates
        delta = date2 - date1

        # Return the number of days
        return abs(delta.days)

    def get_first_and_last_day(self, date_str):
        # Parse the input date string into a datetime object
        date = datetime.strptime(date_str, '%Y-%m-%d')

        # Find the first day of the month
        first_day = date.replace(day=1)

        # Find the last day of the month
        # To find the last day, go to the first day of the next month and subtract one day
        next_month = first_day.replace(day=28) + timedelta(days=4)  # go to the next month
        last_day = next_month - timedelta(days=next_month.day)

        return first_day, last_day

    @api.one
    def action_submit(self):
        limit = self.env['wfh.days.limit'].search([('company_id', '=', self.company_id.id)], limit=1)

        domain = [('employee_id', '=', self.employee_id.id), ('state', 'in', ['hr_approval', 'confirmed'])]

        if limit:
            if self.number_of_days > limit.max_days:
                raise osv.except_osv(_('Warning!'),
                                     _('Your are only allowed to create %s no:of days in a single request') % (
                                         limit.max_days))

        wfh = self.env['hr.holidays.wfh'].search(domain)
        self.action_check_yearly_limit(limit, domain, self.date_from, self.date_to)
        self.action_check_monthly_limit(limit, domain, self.date_from, self.date_to)
        self.action_check_consicutive_week(limit, domain, self.date_from, self.date_to)
        # nnn

        self.date_log_history_line = [
            {'name': 'Work From Home Request Submitted', 'user_id': self.env.user.id, 'date': str(datetime.now())}]
        self.od_send_mail('od_wfh_approval_manager')
        return self.write({'state': 'waiting_approval'})

    @api.one
    def action_manager_approve(self):
        if self.employee_id.user_id.id == self.env.user.id:
            raise osv.except_osv(_('Warning!'), _('You are not allowed to Approve your own request'))
        self.date_log_history_line = [
            {'name': 'Work From Home Request Approved By Manager', 'user_id': self.env.user.id,
             'date': str(datetime.now())}]
        self.od_send_mail('od_wfh_approval_hr')
        return self.write({'state': 'hr_approval'})

    @api.one
    def action_hr_approve(self):
        self.date_log_history_line = [
            {'name': 'Work From Home Request Approved By HR', 'user_id': self.env.user.id,
             'date': str(datetime.now())}]
        self.od_send_mail('od_wfh_approved_employee')
        return self.write({'state': 'confirmed'})

    @api.one
    def action_refuse(self):
        self.date_log_history_line = [
            {'name': 'Work From Home Request Refused', 'user_id': self.env.user.id, 'date': str(datetime.now())}]
        self.od_send_mail('od_wfh_refused_employee')
        return self.write({'state': 'refuse'})

    @api.one
    def action_cancel(self):
        self.date_log_history_line = [
            {'name': 'Work From Home Request Cancelled', 'user_id': self.env.user.id, 'date': str(datetime.now())}]
        return self.write({'state': 'cancel'})

    @api.one
    def action_reset(self):
        self.date_log_history_line = [
            {'name': 'Work From Home Moved To Draft', 'user_id': self.env.user.id, 'date': str(datetime.now())}]
        return self.write({'state': 'draft'})


class DateLogWfh(models.Model):
    _name = 'date.log.wfh'

    def od_get_company_id(self):
        return self.env.user.company_id

    company_id = fields.Many2one('res.company', string='Company', default=od_get_company_id)
    wfh_id = fields.Many2one('hr.holidays.wfh', string="WFH")
    name = fields.Char(string='Name')
    user_id = fields.Many2one('res.users', string="User")
    date = fields.Datetime(string="Date")


class WfhDaysLimit(models.Model):
    _name = 'wfh.days.limit'
    _rec_name = 'company_id'

    def od_get_company_id(self):
        return self.env.user.company_id

    company_id = fields.Many2one('res.company', string='Company', default=od_get_company_id)
    monthly_limit = fields.Float('Monthly Limit', copy=False)
    yearly_limit = fields.Float('Yearly Limit', copy=False)
    max_days = fields.Float('Maximum No:of Days For Single Request', copy=False)
