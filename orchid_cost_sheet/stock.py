# -*- coding: utf-8 -*-
from openerp import models, fields, api, _

class stock_move(models.Model):
    _inherit = 'stock.move'
    so_line_id = fields.Many2one('sale.order.line',string="Sale Order Line")
