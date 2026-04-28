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


class TrainerContract(models.Model):
    _name = "trainer.contract"
    _description = "Trainer Contract"
    _rec_name = 'training_card_id'
    _order = "id desc"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    def od_get_company_id(self):
        return self.env.user.company_id

    company_id = fields.Many2one('res.company', string='Company', default=od_get_company_id)
    name = fields.Char('Name', track_visibility='onchange')
    user_id = fields.Many2one('res.users', string="Responsible Person", track_visibility='onchange',
                              default=lambda self: self.env.user)
    training_card_id = fields.Many2one('hr.training.card', "Training Name", select=True, track_visibility='onchange')
    brand_id = fields.Many2one('od.product.brand', "Vendor", select=True, track_visibility='onchange')
    # training_schedule_id = fields.Many2one('training.schedule', "Training Schedule", select=True,
    #                                        track_visibility='onchange')
    trainer_id = fields.Many2one('trainer.info', "Trainer Name", select=True, track_visibility='onchange')
    training_date = fields.Date('Date', track_visibility='onchange', select=True, copy=False)
    total_training_hours = fields.Float('Total Training Hours', track_visibility='onchange', select=True, copy=False)
    attendees_ids = fields.One2many('training.attendees', 'training_id', string="Candidates for Training")
    training_plan_ids = fields.One2many('training.plan', 'training_id', string="Training Plan")
    budget_per_emp = fields.Float('Budget Per Employee', track_visibility='onchange', select=True, copy=False)
    additional_budget = fields.Float('Additional Budget', track_visibility='onchange', select=True, copy=False)
    total_budget = fields.Float('Total Budget', track_visibility='onchange', select=True, copy=False,
                                compute="od_compute_total_budget")
    state = fields.Selection(
        [('draft', 'Draft'), ('scheduled', 'Scheduled')],
        string="Status",
        default='draft', track_visibility='onchange')
    attendees_count = fields.Integer(string='Attendees',
                                     compute='_count_attendees')

    training_location = fields.Selection(
        [('internal', 'Internal'), ('external', 'External'),
         ('remote', 'Remote')],
        string="Training Location", track_visibility='onchange')
    training_type_id = fields.Many2one('training.type', string="Training Type", ondelete="cascade",
                                       track_visibility='onchange')
    venue = fields.Char('Venue')

    @api.one
    def _count_attendees(self):
        emp_training_ids = self.env['employee.training.contract'].search([('training_id', '=', self.id)])
        self.attendees_count = len(emp_training_ids)

    @api.one
    @api.depends('budget_per_emp', 'additional_budget')
    def od_compute_total_budget(self):
        total_budget_per_emp = 0
        budget_per_emp = self.budget_per_emp
        additional_budget = self.additional_budget
        if self.attendees_ids:
            total_budget_per_emp = len(self.attendees_ids) * budget_per_emp
        else:
            total_budget_per_emp = budget_per_emp
        self.total_budget = total_budget_per_emp + additional_budget

    @api.onchange('training_card_id')
    def onchange_training_card_id(self):
        if self.training_card_id:
            self.training_type_id = self.training_card_id.training_type_id

    # @api.model
    # def create(self, vals):
    #     res = super(TrainerContract, self).create(vals)
    #     employee_idps = self.env['employee.idp'].search([])
    #     for idp in employee_idps:
    #         idp.write({
    #             'assign_training_plan_ids': [(0, 0, {'training_card_id': res.training_card_id.id,
    #                                                  'trainer_contract_id': res.id,
    #                                                  'training_status': 'not_scheduled'})],
    #         })
    #     # res = super(AssignTraining, self).create(vals)
    #     # if res.company_id.id == 6:
    #     #     res.name = self.env['ir.sequence'].get('od.assign.training') or '/'
    #     # if res.company_id.id == 1:
    #     #     res.name = self.env['ir.sequence'].get('od.assign.training.uae') or '/'
    #     return res

    @api.one
    def action_schedule_training(self):
        candidate_list = []
        if not self.attendees_ids:
            raise Warning("It is not permitted to schedule a training without any attendees.")
        if not self.training_plan_ids:
            raise Warning("Training sessions cannot be scheduled without first specifying the date and time.")
        if self.attendees_ids:
            for attendee in self.attendees_ids:
                employee_id = self.env['hr.employee'].search([('user_id', '=', attendee.user_id.id)])
                candidate_list.append(employee_id.id)
                vals = {
                    'training_id': self.id,
                    'employee_user_id': attendee.user_id.id,
                    'employee_name': employee_id.name,
                    'training_card_id': self.training_card_id.id,
                    'trainer_id': self.trainer_id.id,
                    'training_type_id': self.training_type_id.id,
                    'user_id': self.user_id.id,
                    # 'training_date': self.training_date,
                    'total_training_hours': self.total_training_hours,
                    'budget_per_emp': self.budget_per_emp,
                    'training_location': self.training_location,
                    'additional_budget': self.additional_budget,
                    'state': 'draft',
                }
                emp_training = self.env['employee.training.contract'].create(vals)
                if emp_training:
                    emp_training.od_send_mail('od_training_assigned')
                    for line in self.training_plan_ids:
                        print("line", line)
                        self.env['training.plan'].create({
                            'start_date': line.start_date,
                            'end_date': line.end_date,
                            'duration': line.duration,
                            'emp_training_id': emp_training.id,
                        })
                    emp_training.action_create_event()

                    # Assign the prepared invoice lines to the vals dictionary
        employee_idps = self.env['employee.idp'].search([])
        print("candidate_list", candidate_list)
        start_date = self.training_plan_ids[0].start_date
        end_date = self.training_plan_ids[-1].end_date
        date_string = ''
        if start_date and end_date:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
            new_start_date_obj = start_date_obj + timedelta(hours=4)
            new_end_date_obj = end_date_obj + timedelta(hours=4)
            start_date = new_start_date_obj.strftime("%d-%m-%Y %H:%M:%S")
            end_date = new_end_date_obj.strftime("%d-%m-%Y %H:%M:%S")
            date_string = "From " + ': ' + start_date + "\n" + "To" + ': ' + end_date
        for idp in employee_idps:
            if idp.employee_id.id in candidate_list:
                idp.write({
                    'assign_training_actual_ids': [(0, 0, {'training_card_id': self.training_card_id.id,
                                                           'trainer_contract_id': self.id,
                                                           'training_status': 'scheduled',
                                                           'scheduled_date': date_string,
                                                           'employee_status': 'nominated',
                                                           })],
                })
                # for training_paln in idp.assign_training_plan_ids:
                #     if training_paln.trainer_contract_id.id == self.id:
                #         training_paln.write(
                #             {
                #                 'training_status': 'scheduled',
                #                 'scheduled_date': date_string,
                #                 'employee_status': 'nominated',
                #             })
        return self.write({'state': 'scheduled'})

    def od_view_attendees(self, cr, uid, ids, context=None):
        emp_training_ids = self.pool.get('employee.training.contract').search(cr, uid, [('training_id', '=', ids[0])])
        # emp_training_ids = self.env['employee.training.contract'].search([('training_id', '=', self.id)])
        domain = [('id', 'in', emp_training_ids)]
        # ctx = {'default_training_id': self.id}
        action = self.pool['ir.actions.act_window'].for_xml_id(
            cr, uid, 'beta_training', 'action_open_employee_training_contract')
        action['domain'] = unicode([('id', 'in', emp_training_ids)])
        return action


class TrainingAttendees(models.Model):
    _name = 'training.attendees'
    _description = "Training Attendees"

    training_id = fields.Many2one('trainer.contract', string="Training", ondelete="cascade")
    user_id = fields.Many2one('res.users', string="Attendees")
    status = fields.Selection(
        [('assigned', 'Assigned'), ('accepted', 'Accepted'), ('rejected', 'Rejected'), ('cancelled', 'Cancelled')],
        string="Status",
        default='assigned')


class TrainingPlan(models.Model):
    _name = 'training.plan'
    _description = "Training Plan"

    training_id = fields.Many2one('trainer.contract', string="Training", ondelete="cascade")
    emp_training_id = fields.Many2one('employee.training.contract', string="Training", ondelete="cascade")
    start_date = fields.Datetime(string="Start Date")
    end_date = fields.Datetime(string="End Date")
    duration = fields.Float('Duration', track_visibility='onchange', select=True, copy=False,
                            compute="od_compute_duration")

    def get_time_diff(self, start_time, complete_time):
        start_time = datetime.strptime(start_time, DEFAULT_SERVER_DATETIME_FORMAT)
        complete_time = datetime.strptime(complete_time, DEFAULT_SERVER_DATETIME_FORMAT)
        diff = (complete_time - start_time)
        days = diff.days * 24
        seconds = diff.seconds
        hour = days + float(seconds) / 3600
        return hour

    @api.one
    @api.depends('start_date', 'end_date')
    def od_compute_duration(self):
        start_date = self.start_date
        end_date = self.end_date
        if start_date and end_date:
            hour = self.get_time_diff(start_date, end_date)
            self.duration = hour
