# -*- coding: utf-8 -*-
from openerp import fields,api,models

class res_company(models.Model):
    _inherit ='res.company'
    od_cost_factor = fields.Float('Manpower Implementation Cost Factor (%)')
    od_log_factor = fields.Float('Manpower Implementation Log Factor ')
    od_supplier_currency_id  = fields.Many2one('res.currency',string="Default Supplier Currency",help="Costgroup Lines Default Supplier Curreny ")
    od_vat = fields.Float(string="VAT %")
    od_tax_id = fields.Many2one('account.tax',string="VAT")