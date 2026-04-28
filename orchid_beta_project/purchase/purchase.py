# -*- coding: utf-8 -*-
from openerp import models, fields, api

class purchaseOrder(models.Model):
    _inherit = "purchase.order"
    od_task_ids =  fields.Many2many('project.task', 'od_task_purchase_rel',
                                  'purchase_id', 'task_id', string="Requisition")
    od_notes = fields.Text(string="Notes")
