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


class TrainingType(models.Model):
    _name = "training.type"
    _description = "Training Type"
    _rec_name = 'name'
    _order = "id desc"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    name = fields.Char('Name', track_visibility='onchange')


class TrainingCategory(models.Model):
    _name = "training.category"
    _description = "Training Category"
    _rec_name = 'name'
    _order = "id desc"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    name = fields.Char('Name', track_visibility='onchange')


class TrainingCertificateImage(models.Model):
    _name = "training.certificate.image"
    _description = "Training Certificate Image"
    _rec_name = 'name'
    _order = "id desc"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    def od_get_company_id(self):
        return self.env.user.company_id

    company_id = fields.Many2one('res.company', string='Company', default=od_get_company_id)
    name = fields.Char('Name', track_visibility='onchange')
    border_img_1 = fields.Binary(string="Border Img 1")
    border_img_2 = fields.Binary(string="Border Img 2")
    logo = fields.Binary(string="Logo")
    company_seal = fields.Binary(string="Company Seal")
    watermark = fields.Binary(string="Watermark")


class TrainerAcademicQualification(models.Model):
    _name = "trainer.academic.qualification"
    _description = "Training Certificate Image"
    _rec_name = 'name'
    _order = "id desc"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    name = fields.Char('Name', track_visibility='onchange')
