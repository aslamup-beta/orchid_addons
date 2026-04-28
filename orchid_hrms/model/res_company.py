# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
from openerp.tools.translate import _
import copy
import math
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
import datetime
import dateutil.relativedelta
from datetime import date, timedelta
import itertools
from lxml import etree
import openerp.addons.decimal_precision as dp

class res_company(models.Model):
    _inherit = 'res.company'

    od_routing_codes = fields.Char(string='Routing Code')
    od_establishment = fields.Char(string='Establishment')
