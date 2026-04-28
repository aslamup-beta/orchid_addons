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


class EmployeeTrainingFeedbackWiz(models.TransientModel):
    _name = 'emp.training.feedback.wiz'

    training_feedback = fields.Selection(
        [('good', 'Good'),
         ('avg', 'Average'),
         ('bad', 'Bad')],
        string="Quality Of Training",
        track_visibility='onchange')
    emp_comments = fields.Text(string="Employee Feedback")
    completed_date = fields.Date('Completed On', track_visibility='onchange', select=True, copy=False)
    attach_file_emp = fields.Binary('Attach Docs/Certificate')
    attach_fname_emp = fields.Char('Attach Doc Name')

    @api.one
    def action_submit(self):
        context = self._context
        active_id = context.get('active_id')
        emp_contract = self.env['employee.training.contract']
        emp_contract_obj = emp_contract.browse(active_id)
        emp_contract_obj.write({'training_feedback': self.training_feedback,
                                'emp_comments': self.emp_comments,
                                'attach_file_emp': self.attach_file_emp,
                                'attach_fname_emp': self.attach_fname_emp,
                                'state': 'waiting_hr',
                                })
        emp_contract_obj.od_send_mail('od_training_completion_hr_validation')
        employee_idp = self.env['employee.idp'].search([('employee_id', '=', emp_contract_obj.employee_id.id)])
        for training_paln in employee_idp.assign_training_actual_ids:
            if training_paln.trainer_contract_id.id == emp_contract_obj.training_id.id:
                training_paln.write(
                    {
                        'employee_status': 'waiting_hr',
                    })
        return True


class HrTrainingFeedbackWiz(models.TransientModel):
    _name = 'hr.training.feedback.wiz'

    hr_feedback = fields.Selection(
        [('good', 'Good'),
         ('avg', 'Average'),
         ('bad', 'Bad')],
        string="Quality Of Training",
        track_visibility='onchange')
    hr_comments = fields.Text(string="HR Feedback")

    @api.one
    def action_submit(self):
        context = self._context
        active_id = context.get('active_id')
        emp_contract = self.env['employee.training.contract']
        emp_contract_obj = emp_contract.browse(active_id)
        emp_contract_obj.write({
                                'hr_feedback': self.hr_feedback,
                                'hr_comments': self.hr_comments,
                                'state': 'completed',
                                })
        employee_idp = self.env['employee.idp'].search([('employee_id', '=', emp_contract_obj.employee_id.id)])
        for training_paln in employee_idp.assign_training_actual_ids:
            if training_paln.trainer_contract_id.id == emp_contract_obj.training_id.id:
                training_paln.write(
                    {
                        'employee_status': 'completed',
                    })
        return True
