# -*- coding: utf-8 -*-
from openerp import models, fields, api
class od_attachement(models.Model):
    _inherit = 'od.attachement'
    owner_feedback_id = fields.Many2one('od.reviewer.comment',string="Owner Feedback")
    finance_feedback_id = fields.Many2one('od.finance.comment',string="Finance Feedback")
    costsheet_doc = fields.Boolean(string="Costing Sheet Doc")
