# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning

class od_cost_tabs(models.Model):
    _name = 'od.cost.tabs'
    name = fields.Char(string="Name")
    code = fields.Char(string="Code")