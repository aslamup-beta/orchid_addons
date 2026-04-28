# -*- coding: utf-8 -*-

import itertools
from lxml import etree

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp
from openerp.tools import amount_to_text_en
# from . import amount_to_ar
from pprint import pprint
from openerp import tools
from itertools import groupby


class ResPartner(models.Model):
    _inherit = "res.partner"

    opp_warn = fields.Selection(
        [('no-message', 'No Message'), ('warning', 'Warning'),
         ('block', 'Blocking Message')],
        'Opportunity', track_visibility='onchange', copy=False, default='no-message')

    opp_warn_msg = fields.Text('Message for Opportunity')
