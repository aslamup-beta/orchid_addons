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


class TrainerInfo(models.Model):
    _name = "trainer.info"
    _description = "Trainer Info"
    _rec_name = 'name'
    _order = 'create_date desc'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    def od_get_company_id(self):
        return self.env.user.company_id

    company_id = fields.Many2one('res.company', string='Company', default=od_get_company_id)
    state = fields.Selection(
        [('draft', 'To Submit'), ('confirm', 'To Approve'),
         ('validate', 'Approved'), ('refuse', 'Refused')],
        'Status', readonly=True, track_visibility='onchange', copy=False, default='draft')

    # Trainer Information
    name = fields.Char('Name')
    nationality = fields.Many2one('res.country', string="Nationality")
    residence = fields.Char('ID/Residence')
    qualification = fields.Many2one('trainer.academic.qualification', string="Qualification")
    experience = fields.Integer('Years of Experience')

    # Training Program Information
    training_title = fields.Char(string="Training Program Title")  # change the model to correct ones
    program_desc = fields.Text(string="Program Description/Objectives")  # on change from above fields
    target_audience = fields.Text('Target Audience: EMS')

    # Trainer Qualification Criteria
    trn_rel_qualification = fields.Text('Relevant Qualifications and Experience Related to the Program Topic')
    previous_experience = fields.Text('Previous Experience in Delivering Similar Programs')
    trainer_strength1 = fields.Selection(
        [('low', 'Low'), ('normal', 'Normal'),
         ('high', 'High')],
        'Strength in Presentation Skills', track_visibility='onchange', copy=False)
    trainer_strength2 = fields.Selection(
        [('low', 'Low'), ('normal', 'Normal'),
         ('high', 'High')],
        'Strength in Communication Skills', track_visibility='onchange', copy=False)
    flexibilty = fields.Selection(
        [('low', 'Low'), ('normal', 'Normal'),
         ('high', 'High')],
        'Flexibility in Response and Communication', track_visibility='onchange', copy=False)
    pricing = fields.Text('Competitive Pricing in Relation to the Training Program')

    @api.one
    def send_to_training_committee(self):
        return self.write({'state': 'confirm'})

    @api.one
    def confirm_trainer(self):
        return self.write({'state': 'validate'})

    @api.one
    def action_refuse(self):
        return self.write({'state': 'refuse'})
