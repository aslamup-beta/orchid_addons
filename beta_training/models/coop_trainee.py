# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning
from datetime import date, timedelta, datetime

class CoopTrainee(models.Model):
    _name = "coop.trainee"
    _description = "Coop Trainee"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    def od_get_company_id(self):
        return self.env.user.company_id

    @api.one
    def _od_attachement_count(self):
        for obj in self:
            attachement_ids = self.env['od.attachement'].search(
                [('model_name', '=', self._name), ('object_id', '=', obj.id)])
            if attachement_ids:
                self.od_attachement_count = len(attachement_ids)

    company_id = fields.Many2one('res.company', string='Company', default=od_get_company_id)
    name = fields.Char(string="Trainee Name")
    training_start_date = fields.Date(string="Training Start Date")
    training_end_date = fields.Date(string="Training End Date")
    stipend_amount = fields.Float('Stipend', help="Stipend")
    personal_email = fields.Char('Email', size=128, help="Personal Email of the Trainee")
    # work_email = fields.Char('Work Email', size=128, help="Work Email of the outsourced emloyee")
    description = fields.Text(string="Additional Notes")
    mobile_phone = fields.Char(string="Mobile")
    od_attachement_count = fields.Integer(string="Attachement Count", compute="_od_attachement_count")
    active = fields.Boolean(string="Active", default=True)
    country_id = fields.Many2one('res.country', string='Nationality')
    od_father = fields.Char(string="Father Name")
    identification_id = fields.Char(string="ID number")
    passport_id = fields.Char(string="Passport No")
    od_street = fields.Char(string="Street")
    od_street2 = fields.Char(string="Street 2")
    od_state_id = fields.Many2one('res.country.state', string='State')
    od_city = fields.Char(string="City")
    od_zip = fields.Char(string="Zip")
    od_country_id = fields.Many2one('res.country', string='Country')
    birthday = fields.Date(string='Date Of Birth')
    place_of_birth = fields.Char(string="Place of Birth")
    profession = fields.Char(string="Profession")
    training_location = fields.Char(string="Training Location")
    training_type = fields.Char(string="Training Type")
    training_duration = fields.Char(string="Training Duration")
    national_address = fields.Char(string="National Address")
    marital_status = fields.Selection(
        [('single', 'Single'), ('married', 'Married'),('widower', 'Widower'),('divorced', 'Divorced')],
        string="Marital Status")
    responsible_user_id = fields.Many2one('res.users', string="Responsible Person")

    def od_open_attachement(self, cr, uid, ids, context=None):

        model_name = self._name
        object_id = ids[0]
        domain = [('model_name', '=', model_name), ('object_id', '=', object_id)]
        ctx = {'default_model_name': model_name, 'default_object_id': object_id}
        return {
            'domain': domain,
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'od.attachement',
            'type': 'ir.actions.act_window',
            'context': ctx
        }

