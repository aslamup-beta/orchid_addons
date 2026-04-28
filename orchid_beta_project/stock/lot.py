# -*- coding: utf-8 -*-
from openerp import models,fields,api
class stock_production_lot(models.Model):
    _inherit = "stock.production.lot"
    od_partner_id = fields.Many2one('res.partner',string="Partner")
