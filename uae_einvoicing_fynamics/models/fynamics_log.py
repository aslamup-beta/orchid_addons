# -*- coding: utf-8 -*-
from openerp import models, fields

class FynamicsLog(models.Model):
    _name = 'fynamics.api.log'
    _description = 'Fynamics API Log'
    _order = 'create_date desc'

    name = fields.Char(required=True)
    invoice_id = fields.Many2one('account.invoice', ondelete='set null')
    operation = fields.Char()
    endpoint = fields.Char()
    request_body = fields.Text()
    response_body = fields.Text()
    http_status = fields.Integer()
    status = fields.Selection([
        ('success', 'Success'),
        ('error', 'Error'),
        ('queued', 'Queued'),
    ], default='queued')
    error_message = fields.Text()
    uuid = fields.Char(string='UUID')