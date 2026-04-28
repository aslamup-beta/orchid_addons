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


class HrContractQuarterly(models.Model):
    _name = "hr.contract.quarterly"
    _description = "Hr Contract Quarterly"
    _rec_name = 'name'
    _order = "date_from asc"
    _inherit = ['mail.thread', 'ir.needaction_mixin']



    date_from = fields.Date('Created On', readonly=True, track_visibility='onchange',select=True, copy=False)
    date_to = fields.Date('End Date', readonly=True, track_visibility='onchange',copy=False)
    name = fields.Text('Description')
    emp_contracts_line_ids = fields.One2many('emp.contract.line', 'quarterly_id', strint="Expiring Contracts List",
                                            readonly=True, copy=False)

    def od_get_company_id(self):
        return self.env.user.company_id

    company_id = fields.Many2one('res.company', string='Company', default=od_get_company_id)



    def od_send_mail(self, template):
        ir_model_data = self.env['ir.model.data']
        email_obj = self.pool.get('email.template')
        # if self.company_id.id == 6:
        #     template = template + '_saudi'
        template_id = ir_model_data.get_object_reference('beta_extended', template)[1]
        rec_id = self.id
        email_obj.send_mail(self.env.cr, self.env.uid, template_id, rec_id, force_send=True)
        return True

    # @api.one
    # def action_confirm(self):
    #     self.date_log_history_line = [
    #         {'name': 'Business Trip Request Submitted', 'user_id': self.env.user.id, 'date': str(datetime.now())}]
    #     self.od_send_mail('od_buisness_trip_approval_manager')
    #     return self.write({'state': 'confirm'})




class HrContractQuarterlyLine(models.Model):
    _name = 'emp.contract.line'

    def od_get_company_id(self):
        return self.env.user.company_id

    company_id = fields.Many2one('res.company', string='Company', default=od_get_company_id)
    quarterly_id = fields.Many2one('hr.contract.quarterly', string="Quarterly")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    contract_id = fields.Many2one('hr.contract', string="Contract")
    id_number = fields.Char(string="ID Number")
    start_date = fields.Date(string="Contract Start Date")
    end_date = fields.Date(string="Contract End Date")
    remaining_days = fields.Float(string="Remaining Days Until Contract Expiration")

    @api.multi
    def btn_open_contract(self):
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.contract',
            'res_id': self.contract_id and self.contract_id.id or False,
            'type': 'ir.actions.act_window',
            'target': 'new',

        }
