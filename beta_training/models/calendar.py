# -*- coding: utf-8 -*-

import itertools
from lxml import etree
from openerp.osv import osv
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp
from openerp.tools import amount_to_text_en
# from . import amount_to_ar
from pprint import pprint
from openerp import tools
from itertools import groupby


class calendar_event(osv.Model):
    _inherit = "calendar.event"

    emp_training_id = fields.Many2one('employee.training.contract', string="Training", ondelete="cascade")
