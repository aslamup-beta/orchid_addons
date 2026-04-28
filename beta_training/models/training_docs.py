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


class TrainingDocs(models.Model):
    _name = 'training.docs'
    _description = "Training Documents"
    _order = 'sequence'

    def od_get_company_id(self):
        return self.env.user.company_id

    name = fields.Char('Reference')
    company_id = fields.Many2one('res.company', string='Company', default=od_get_company_id)
    attach_file = fields.Binary('Attach File')
    attach_fname = fields.Char('File Name')
    issue_date = fields.Date('Issue Date')
    expiry_date = fields.Date('Expiry Date')
    sequence = fields.Integer('sequence', help="Sequence for the handle.", default=10)