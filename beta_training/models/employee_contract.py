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
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from dateutil.relativedelta import relativedelta


class EmployeeTrainingContract(models.Model):
    _name = "employee.training.contract"
    _description = "Employee Training Contract"
    _rec_name = 'training_card_id'
    _order = "id desc"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    def od_get_company_id(self):
        return self.env.user.company_id

    company_id = fields.Many2one('res.company', string='Company', default=od_get_company_id)
    name = fields.Char('Name', track_visibility='onchange')
    employee_name = fields.Char('Employee', track_visibility='onchange')
    user_id = fields.Many2one('res.users', string="Responsible Person")
    training_id = fields.Many2one('trainer.contract', string="Training")
    training_certificate_img_id = fields.Many2one('training.certificate.image', string="Training CertificateImg")
    employee_user_id = fields.Many2one('res.users', string="Employee")
    employee_id = fields.Many2one('hr.employee', string="Employee", compute="_compute_employee_id", store=True)
    training_card_id = fields.Many2one('hr.training.card', "Training Name", select=True, track_visibility='onchange')
    trainer_id = fields.Many2one('trainer.info', "Trainer Name", select=True, track_visibility='onchange')
    training_date = fields.Date('Date', track_visibility='onchange', select=True, copy=False)
    total_training_hours = fields.Float('Total Training Hours', track_visibility='onchange', select=True, copy=False)
    training_plan_ids = fields.One2many('training.plan', 'emp_training_id', string="Training Plan")
    budget_per_emp = fields.Float('Budget Per Employee', track_visibility='onchange', select=True, copy=False)
    additional_budget = fields.Float('Additional Budget', track_visibility='onchange', select=True, copy=False)
    total_budget = fields.Float('Total Budget', track_visibility='onchange', select=True, copy=False,
                                compute="od_compute_duration")
    state = fields.Selection(
        [('draft', 'Draft'), ('confirm', 'Confirmed By Employee'),
         ('reject', 'Rejected By Employee'),
         ('waiting_hr', 'Waiting HR Confirmation'),
         ('completed', 'Completed'),
         ('absent', 'Not Attended'),
         ('cancel', 'Cancelled')],
        string="Status",
        default='draft', track_visibility='onchange')
    event_count = fields.Integer(string='Attendees',
                                 compute='_count_training_events')
    training_location = fields.Selection(
        [('internal', 'Internal'), ('external', 'External'),
         ('remote', 'Remote')],
        string="Training Location")
    training_type_id = fields.Many2one('training.type', string="Training Type", ondelete="cascade")
    manager_id = fields.Many2one('res.users', 'Manager', compute="_compute_manager_id", store=True)
    confirmed_date = fields.Datetime(string="Confirmed On")
    rejection_date = fields.Datetime(string="Rejected On")
    training_feedback = fields.Selection(
        [('good', 'Good'),
         ('avg', 'Average'),
         ('bad', 'Bad')],
        string="Quality Of Training",
        track_visibility='onchange')
    emp_comments = fields.Text(string="Employee Feedback")
    completed_date = fields.Date('Completed On', track_visibility='onchange', select=True, copy=False)
    hr_comments = fields.Text(string="HR Feedback")
    hr_feedback = fields.Selection(
        [('good', 'Good'),
         ('avg', 'Average'),
         ('bad', 'Bad')],
        string="Quality Of Training",
        track_visibility='onchange')
    attach_file_emp = fields.Binary('Attach Docs/Certificate')
    attach_fname_emp = fields.Char('Attach Doc Name')
    scheduled_date = fields.Text('Scheduled Dates', track_visibility='onchange', compute='_compute_scheduled_date')
    training_status = fields.Selection(
        [('scheduled', 'Scheduled'), ('not_scheduled', 'Not Scheduled')], compute='_compute_training_status',
        string="Training Status")


    def _compute_training_status(self):
        status = 'not_scheduled'
        for rec in self:
            date_string = ''
            if rec.training_id.state == 'scheduled':
                status = 'scheduled'
            rec.training_status = status

    # @api.one
    # @api.depends('training_card_id')
    def _compute_scheduled_date(self):
        for rec in self:
            date_string = ''
            if rec.training_id.state == 'scheduled':
                status = 'scheduled'
                if rec.training_id.training_plan_ids:
                    start_date = rec.training_id.training_plan_ids[0].start_date
                    end_date = rec.training_id.training_plan_ids[-1].end_date
                    if start_date and end_date:
                        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
                        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
                        new_start_date_obj = start_date_obj + timedelta(hours=4)
                        new_end_date_obj = end_date_obj + timedelta(hours=4)
                        start_date = new_start_date_obj.strftime("%d-%m-%Y %H:%M:%S")
                        end_date = new_end_date_obj.strftime("%d-%m-%Y %H:%M:%S")
                        date_string = "From " + ': ' + start_date + "\n" + "To" + ': ' + end_date
            rec.scheduled_date = date_string

    @api.one
    @api.depends('employee_user_id')
    def _compute_employee_id(self):
        for rec in self:
            employee_user = rec.employee_user_id or False
            if employee_user:
                employee_id = self.env['hr.employee'].search([('user_id', '=', employee_user.id)])
                rec.employee_id = employee_id.id or False

    @api.one
    @api.depends('employee_id')
    def _compute_manager_id(self):
        for rec in self:
            employee = rec.employee_id or False
            if employee:
                rec.manager_id = employee.sudo().parent_id and employee.sudo().parent_id.user_id and employee.sudo().parent_id.user_id.id or False

    @api.one
    def _count_training_events(self):
        events = self.env['calendar.event'].search([('emp_training_id', '=', self.id)])
        self.event_count = len(events)

    @api.one
    @api.depends('budget_per_emp', 'additional_budget')
    def od_compute_duration(self):
        budget_per_emp = self.budget_per_emp
        additional_budget = self.additional_budget
        self.total_budget = budget_per_emp + additional_budget

    def od_send_mail(self, template):
        ir_model_data = self.env['ir.model.data']
        email_obj = self.pool.get('email.template')
        # if self.company_id.id == 6:
        #     template = template + '_saudi'
        template_id = ir_model_data.get_object_reference('beta_training', template)[1]
        rec_id = self.id
        if template_id:
            email_obj.send_mail(self.env.cr, self.env.uid, template_id, rec_id, force_send=True)
        return True

    @api.one
    def action_confirm_training(self):
        if self.employee_user_id.id != self.env.user.id:
            if self.user_id.id != self.env.user.id:
                raise Warning(
                    "You are not allowed to do this action, Please ask %s to do this." % self.employee_user_id.name)
        employee_idp = self.env['employee.idp'].search([('employee_id', '=', self.employee_id.id)])
        for training_paln in employee_idp.assign_training_actual_ids:
            if training_paln.trainer_contract_id.id == self.training_id.id:
                training_paln.write(
                    {
                        'employee_status': 'confirmed',
                    })
        self.od_send_mail('od_training_accepted')
        return self.write({'state': 'confirm', 'confirmed_date': fields.datetime.now()})

    @api.one
    def action_reject_training(self):
        self.od_send_mail('od_training_rejected')
        employee_idp = self.env['employee.idp'].search([('employee_id', '=', self.employee_id.id)])
        for training_paln in employee_idp.assign_training_actual_ids:
            if training_paln.trainer_contract_id.id == self.training_id.id:
                training_paln.write(
                    {
                        'employee_status': 'rejected',
                    })
        return self.write({'state': 'reject', 'rejection_date': fields.datetime.now()})

    @api.one
    def action_confirm_attendance(self):
        return self.write({'state': 'completed'})

    @api.one
    def action_mark_absent(self):
        employee_idp = self.env['employee.idp'].search([('employee_id', '=', self.employee_id.id)])
        for training_paln in employee_idp.assign_training_actual_ids:
            if training_paln.trainer_contract_id.id == self.training_id.id:
                training_paln.write(
                    {
                        'employee_status': 'absent',
                    })
        return self.write({'state': 'absent'})

    @api.one
    def action_create_event(self):
        if self.training_plan_ids:
            print("^^^^^^^^^^^^^^^^^^^^^^^")
            for line in self.training_plan_ids:
                event = self.env['calendar.event'].create({
                    'start_datetime': line.start_date,
                    'stop_datetime': line.end_date,
                    'name': self.training_card_id.program,
                    'emp_training_id': self.id,
                    'partner_ids': [(4, self.employee_user_id.partner_id.id)],
                })
            # Assign the prepared invoice lines to the vals dictionary

    def od_view_training_events(self, cr, uid, ids, context=None):
        events = self.pool.get('calendar.event').search(cr, uid, [('emp_training_id', '=', ids[0])])
        action = self.pool['ir.actions.act_window'].for_xml_id(
            cr, uid, 'calendar', 'action_calendar_event')
        action['domain'] = unicode([('id', 'in', events)])
        return action

    def training_date_reminder(self, cr, uid, context=None):
        template = 'training_reminder_email_template'
        ir_model_data = self.pool.get('ir.model.data')
        employee_training_obj = self.pool.get('employee.training.contract')
        user_obj = self.pool.get('res.users')
        template_id = ir_model_data.get_object_reference(cr, uid, 'beta_training', template)[1]
        employee_trainings = employee_training_obj.search(cr, uid, [('state', '=', 'draft')])
        for training in employee_trainings:
            employee_training = employee_training_obj.browse(cr, uid, training)
            today = datetime.now()
            if employee_training:
                created_date = employee_training.create_date
                created_date = datetime.strptime(employee_training.create_date, "%Y-%m-%d %H:%M:%S").date()
                check_date = created_date + relativedelta(days=3)
                check_date = check_date.strftime('%Y-%m-%d')
                target_date = today.strftime('%Y-%m-%d')
                if target_date == check_date:
                    self.pool.get('email.template').send_mail(cr, uid, template_id, training, force_send=True,
                                                              context=context)
        return True

    def training_completion_reminder(self, cr, uid, context=None):
        template = 'training_completion_reminder_email_template'
        ir_model_data = self.pool.get('ir.model.data')
        employee_training_obj = self.pool.get('employee.training.contract')
        user_obj = self.pool.get('res.users')
        template_id = ir_model_data.get_object_reference(cr, uid, 'beta_training', template)[1]
        employee_trainings = employee_training_obj.search(cr, uid, [('state', '=', 'confirm')])
        for training in employee_trainings:
            employee_training = employee_training_obj.browse(cr, uid, training)
            today = datetime.now()
            if employee_training:
                end_date = employee_training.training_plan_ids[-1].end_date
                end_date = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S").date()
                check_date = end_date + relativedelta(days=1)
                check_date = check_date.strftime('%Y-%m-%d')
                target_date = today.strftime('%Y-%m-%d')
                if target_date == check_date:
                    self.pool.get('email.template').send_mail(cr, uid, template_id, training, force_send=True,
                                                              context=context)
        return True
