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


class EmployeeIDP(models.Model):
    _name = "employee.idp"
    _description = "Employee IDP"
    _rec_name = 'employee_id'
    _order = "id desc"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    def od_get_company_id(self):
        return self.env.user.company_id

    company_id = fields.Many2one('res.company', string='Company', default=od_get_company_id)
    active = fields.Boolean(string="Active", default=True)
    employee_id = fields.Many2one('hr.employee', string="Employee")
    manager_id = fields.Many2one('hr.employee', 'Manager')
    employee_user_id = fields.Many2one('res.users', string="Employee", related="employee_id.user_id", store=True)
    coach_id = fields.Many2one('hr.employee', 'Coach')
    department_id = fields.Many2one('hr.department', 'Department', related="employee_id.department_id", store=True)
    assign_training_plan_ids = fields.One2many('assign.training.plan', 'idp_id', string="Plan Training")
    idp_year = fields.Char('Year')
    assign_training_actual_ids = fields.One2many('assign.training.actual', 'idp_id', string="Assigned Training")
    completed_trainings = fields.One2many(
        'employee.training.contract',
        compute='_compute_completed_trainings',
        string='Completed Trainings'
    )

    actual_trainings = fields.One2many(
        'employee.training.contract',
        compute='_compute_actual_trainings',
        string='Actual Trainings'
    )

    # @api.depends('state')
    def _compute_actual_trainings(self):
        print("_compute_actual_trainings")
        for record in self:
            print("record11111111", record)
            # Search for completed records based on your criteria
            actual_recs = self.env['employee.training.contract'].search([
                ('state', 'in', ['draft', 'confirm', 'reject', 'waiting_hr', ]), ('employee_id', '=', record.employee_id.id)
                # Add other filters as needed, for example:
                # ('employee_field', '=', record.employee_field.id)
            ])
            print("actual_recs", actual_recs)
            if actual_recs:
                record.actual_trainings = actual_recs.ids
            else:
                record.actual_trainings = False

    # @api.depends('state')
    def _compute_completed_trainings(self):
        print("_compute_completed_trainings")
        for record in self:
            print("record2222222222222222", record)
            # Search for completed records based on your criteria
            completed_recs = self.env['employee.training.contract'].search([
                ('state', '=', 'completed'), ('employee_id', '=', record.employee_id.id)
                # Add other filters as needed, for example:
                # ('employee_field', '=', record.employee_field.id)
            ])
            print("completed_recs", completed_recs)
            record.completed_trainings = completed_recs.ids


class AssignTrainingPlan(models.Model):
    _name = 'assign.training.plan'
    _description = "Assign Training Plan"

    idp_id = fields.Many2one('employee.idp', string="IDP", ondelete="cascade")
    training_card_id = fields.Many2one('hr.training.card', string="Training", ondelete="cascade")
    training_type_id = fields.Many2one('training.type', string="Training Type",
                                       related="training_card_id.training_type_id", store=True)
    trainer_contract_id = fields.Many2one('trainer.contract', string="Training", ondelete="cascade")
    training_status = fields.Selection(
        [('scheduled', 'Scheduled'), ('not_scheduled', 'Not Scheduled')], compute='_compute_training_status',
        string="Training Status")

    employee_status = fields.Selection(
        [('nominated', 'Nominated'), ('not_nominated', 'Not Nominated'), ('confirmed', 'Confirmed By Employee'),
         ('rejected', 'Rejected By Employee')], compute='_compute_employee_status',
        string="Employee Status")
    scheduled_date = fields.Text('Scheduled Dates', track_visibility='onchange', compute='_compute_training_status')

    @api.one
    @api.depends('training_card_id')
    def _compute_training_status(self):
        status = 'not_scheduled'
        date_string = ''
        if self.training_card_id:
            trainer_contract = self.env['trainer.contract'].search(
                [('training_card_id', '=', self.training_card_id.id)])
            # print("trainer_contract", trainer_contract)
            employee_contract = self.env['employee.training.contract'].search(
                [('training_card_id', '=', self.training_card_id.id), ('employee_id', '=', self.idp_id.employee_id.id)])
            # print("employee_contract", employee_contract)
            if employee_contract:
                if employee_contract[0].training_id.state == 'scheduled':
                    status = 'scheduled'
                    if employee_contract[0].training_id.training_plan_ids:
                        start_date = employee_contract[0].training_id.training_plan_ids[0].start_date
                        end_date = employee_contract[0].training_id.training_plan_ids[-1].end_date
                        if start_date and end_date:
                            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
                            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
                            new_start_date_obj = start_date_obj + timedelta(hours=4)
                            new_end_date_obj = end_date_obj + timedelta(hours=4)
                            start_date = new_start_date_obj.strftime("%d-%m-%Y %H:%M:%S")
                            end_date = new_end_date_obj.strftime("%d-%m-%Y %H:%M:%S")
                            date_string = "From " + ': ' + start_date + "\n" + "To" + ': ' + end_date
            else:
                if trainer_contract:
                    # print("trainer_contract[-1]", trainer_contract[-1])
                    # print("trainer_contract[0]", trainer_contract[0])
                    if trainer_contract[0].state == 'scheduled':
                        status = 'scheduled'
                        if trainer_contract[0].training_plan_ids:
                            start_date = trainer_contract[0].training_plan_ids[0].start_date
                            end_date = trainer_contract[0].training_plan_ids[-1].end_date
                            if start_date and end_date:
                                start_date_obj = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
                                end_date_obj = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
                                new_start_date_obj = start_date_obj + timedelta(hours=4)
                                new_end_date_obj = end_date_obj + timedelta(hours=4)
                                start_date = new_start_date_obj.strftime("%d-%m-%Y %H:%M:%S")
                                end_date = new_end_date_obj.strftime("%d-%m-%Y %H:%M:%S")
                                date_string = "From " + ': ' + start_date + "\n" + "To" + ': ' + end_date
        self.training_status = status
        self.scheduled_date = date_string

    @api.one
    @api.depends('training_card_id')
    def _compute_employee_status(self):
        status = 'not_nominated'
        if self.training_card_id:
            employee_contract = self.env['employee.training.contract'].search(
                [('training_card_id', '=', self.training_card_id.id), ('employee_id', '=', self.idp_id.employee_id.id)])
            print("employee_contract", employee_contract)
            if employee_contract:
                status = 'nominated'
        self.employee_status = status


class AssignTrainingActual(models.Model):
    _name = 'assign.training.actual'
    _description = "Assign Training Actual"

    idp_id = fields.Many2one('employee.idp', string="IDP", ondelete="cascade")
    training_card_id = fields.Many2one('hr.training.card', string="Training", ondelete="cascade")
    training_type_id = fields.Many2one('training.type', string="Training Type",
                                       related="training_card_id.training_type_id", store=True)
    trainer_contract_id = fields.Many2one('trainer.contract', string="Training", ondelete="cascade")
    training_status = fields.Selection(
        [('scheduled', 'Scheduled'), ('not_scheduled', 'Not Scheduled')],
        string="Training Status")

    employee_status = fields.Selection(
        [('nominated', 'Nominated'), ('not_nominated', 'Not Nominated'), ('confirmed', 'Confirmed By Employee'),
         ('rejected', 'Rejected By Employee'), ('waiting_hr', 'Waiting HR Confirmation'),
         ('completed', 'Completed'),
         ('absent', 'Not Attended'), ],
        string="Employee Status")
    scheduled_date = fields.Text('Scheduled Dates', track_visibility='onchange')
