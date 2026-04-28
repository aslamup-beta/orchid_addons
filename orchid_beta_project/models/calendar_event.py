# -*- coding: utf-8 -*-
from openerp import models,fields,api,_
class calendar_event(models.Model):
    """ Model for Calendar Event """
    _inherit = 'calendar.event'
    od_analytic_account_id = fields.Many2one('account.analytic.account',string="Analytic Account")
    
