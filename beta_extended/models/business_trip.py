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


class HrBusinessTrip(models.Model):
    _name = "hr.business.trip"
    _description = "Business Trip"
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
        [('draft', 'To Submit'), ('confirm', 'To Approve'),
         ('validate', 'Approved'), ('refuse', 'Refused'), ('cancel', 'Cancelled')],
        'Status', readonly=True, track_visibility='onchange', copy=False)
    date_from = fields.Date('Start Date', readonly=True, track_visibility='onchange',
                            states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]},
                            select=True, copy=False)
    date_to = fields.Date('End Date', readonly=True, track_visibility='onchange',
                          states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]},
                          copy=False)
    name = fields.Text('Description')
    trip_location = fields.Char('Trip Location', track_visibility='onchange')
    employee_id = fields.Many2one('hr.employee', "Employee", select=True, invisible=False, readonly=True, track_visibility='onchange',
                                  states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    manager_id = fields.Many2one('res.users', string="Direct Manager")
    number_of_days_temp = fields.Float('Allocation', copy=False)
    department_id = fields.Many2one('hr.department', string="Department", related="employee_id.department_id",
                                    readonly=True, store=True)
    user_id = fields.Many2one('res.users', string="User", related="employee_id.user_id", readonly=True)
    wfh_type = fields.Selection(
        [('wfh', 'Work From Home'), ('trip', 'Business Trip')],
        'Type', track_visibility='onchange', copy=False, default='trip')
    number_of_days = fields.Float(string='Number of Days', readonly=True, store=True, related="number_of_days_temp")
    can_reset = fields.Boolean(string='Can Reset', readonly=True, store=True, compute='_get_can_reset')
    date_log_history_line = fields.One2many('date.log.business.trip', 'wfh_id', strint="Date Log History",
                                            readonly=True, copy=False)

    def od_get_company_id(self):
        return self.env.user.company_id

    company_id = fields.Many2one('res.company', string='Company', default=od_get_company_id)
    _defaults = {
        'employee_id': _employee_get,
        'state': 'draft',
        'wfh_type': 'trip',
        'user_id': lambda obj, cr, uid, context: uid,
    }
    _constraints = [
        (_check_date, 'You can not have 2 leaves that overlaps on same day!', ['date_from', 'date_to']),
    ]

    _sql_constraints = [
        ('date_check2', "CHECK (date_from <= date_to )", "The start date must be anterior to the end date."),
        ('date_check', "CHECK ( number_of_days_temp >= 0 )", "The number of days must be greater than 0."),
    ]

    # TODO: can be improved using resource calendar method
    def _get_number_of_days(self, date_from, date_to):
        """Returns a float equals to the timedelta between two dates given as string."""

        DATETIME_FORMAT = "%Y-%m-%d"
        from_dt = datetime.strptime(date_from, DATETIME_FORMAT)
        to_dt = datetime.strptime(date_to, DATETIME_FORMAT)
        timedelta = to_dt - from_dt
        diff_day = timedelta.days + float(timedelta.seconds) / 86400
        return diff_day

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        employee = self.employee_id or False
        if employee:
            self.manager_id = employee.sudo().parent_id and employee.sudo().parent_id.user_id and employee.sudo().parent_id.user_id.id or False

    def unlink(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.state not in ['draft', 'cancel']:
                raise osv.except_osv(_('Warning!'),
                                     _('You cannot delete a business trip which is in %s state.') % (rec.state))
        return super(HrBusinessTrip, self).unlink(cr, uid, ids, context)

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

    @api.one
    def action_confirm(self):
        self.date_log_history_line = [
            {'name': 'Business Trip Request Submitted', 'user_id': self.env.user.id, 'date': str(datetime.now())}]
        self.od_send_mail('od_buisness_trip_approval_manager')
        return self.write({'state': 'confirm'})

    @api.one
    def action_approve(self):
        if self.employee_id.user_id.id == self.env.user.id:
            raise osv.except_osv(_('Warning!'), _('You are not allowed to Approve your own request'))
        self.date_log_history_line = [
            {'name': 'Business Trip Request Approved', 'user_id': self.env.user.id, 'date': str(datetime.now())}]
        self.od_send_mail('od_buisness_trip_approved_employee')
        return self.write({'state': 'validate'})

    @api.one
    def action_refuse(self):
        self.date_log_history_line = [
            {'name': 'Business Trip Request Refused', 'user_id': self.env.user.id, 'date': str(datetime.now())}]
        self.od_send_mail('od_buisness_trip_refused_employee')
        return self.write({'state': 'refuse'})

    @api.one
    def action_cancel(self):
        self.date_log_history_line = [
            {'name': 'Business Trip Request Cancelled', 'user_id': self.env.user.id, 'date': str(datetime.now())}]
        return self.write({'state': 'cancel'})

    @api.one
    def action_reset(self):
        self.date_log_history_line = [
            {'name': 'Business Trip Moved To Draft', 'user_id': self.env.user.id, 'date': str(datetime.now())}]
        return self.write({'state': 'draft'})


class DateLogWfh(models.Model):
    _name = 'date.log.business.trip'

    def od_get_company_id(self):
        return self.env.user.company_id

    company_id = fields.Many2one('res.company', string='Company', default=od_get_company_id)
    wfh_id = fields.Many2one('hr.business.trip', string="WFH")
    name = fields.Char(string='Name')
    user_id = fields.Many2one('res.users', string="User")
    date = fields.Datetime(string="Date")
