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


class HrTrainingCard(models.Model):
    _name = "hr.training.card"
    _description = "Training Card"
    _rec_name = 'program'
    _order = "id desc"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    def od_get_company_id(self):
        return self.env.user.company_id

    company_id = fields.Many2one('res.company', string='Company', default=od_get_company_id)
    program = fields.Char('Program', track_visibility='onchange')
    code = fields.Char('Code', track_visibility='onchange')
    training_hours = fields.Char('Training Hours', track_visibility='onchange')
    program_imp_channel = fields.Char('Program Implementation Channel', track_visibility='onchange')
    potential_trainer_id = fields.Many2one('trainer.info', string='Potential Trainer', track_visibility='onchange')
    general_purpose = fields.Html(string='General Purpose')
    target_audience = fields.Html(string='Target Audience')
    # training_schedule_ids = fields.One2many('training.schedule', 'training_card_id',
    #                                         string="Training Schedule")
    training_type_id = fields.Many2one('training.type', string="Training Type", ondelete="cascade")
    department_id = fields.Many2one('hr.department', string="Department", ondelete="cascade")

    def action_generate_trainer_contract(self, cr, uid, ids, context=None):
        # training_contracts = self.pool.get('trainer.contract').search(cr, uid, [('training_card_id', '=', ids[0])])
        # # emp_training_ids = self.env['employee.training.dashboard'].search([('training_id', '=', self.id)])
        # print("training_contracts", training_contracts)
        # if training_contracts:
        #     action = self.pool['ir.actions.act_window'].for_xml_id(
        #         cr, uid, 'beta_training', 'action_open_trainer_contract')
        #     action['domain'] = unicode([('id', 'in', training_contracts)])
        # else:
        action = self.pool['ir.actions.act_window'].for_xml_id(
            cr, uid, 'beta_training', 'action_open_trainer_contract_form')
        action['context'] = unicode({'default_training_card_id': ids[0]})
        return action

    def action_view_trainer_contract(self, cr, uid, ids, context=None):
        training_contracts = self.pool.get('trainer.contract').search(cr, uid, [('training_card_id', '=', ids[0])])
        # emp_training_ids = self.env['employee.training.dashboard'].search([('training_id', '=', self.id)])
        # ctx = {'default_training_card_id': self.id}
        if training_contracts:
            action = self.pool['ir.actions.act_window'].for_xml_id(
                cr, uid, 'beta_training', 'action_open_trainer_contract')
            action['domain'] = unicode([('id', 'in', training_contracts)])
            # action['context'] = unicode({'default_training_card_id': ids[0]})
            # action['context'] = ctx
        else:
            action = self.pool['ir.actions.act_window'].for_xml_id(
                cr, uid, 'beta_training', 'action_open_trainer_contract_form')
        return action

    @api.one
    def unlink(self):
        training_contracts = self.env['trainer.contract'].search([('training_card_id','=',self.id)])
        if training_contracts:
            raise Warning("You cannot delete a card that has been used to create training contracts.")
        return super(HrTrainingCard, self).unlink()
