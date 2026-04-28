# -*- coding: utf-8 -*-
from openerp import models,fields,api,_
class hr_expense_line(models.Model):
    _inherit = "hr.expense.line"
    DOM_STATES = [
        ('draft', 'New'),
        ('cancelled', 'Refused'),
        ('confirm', 'Waiting Approval'),
        ('accepted', 'Approved'),
        ('done', 'Waiting Payment'),
        ('paid', 'Paid'),
        ]
    od_opp_id = fields.Many2one('crm.lead',string="Opportunity")
    od_brand_id = fields.Many2one('od.product.brand',string="Brand")
    od_state = fields.Selection(DOM_STATES,readonly=True,related="expense_id.state")
    date_value_to = fields.Date(string="Expense Date To")