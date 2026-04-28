# -*- coding: utf-8 -*-
from openerp import models,fields,api,_
from openerp.exceptions import Warning
class employee_certificate(models.Model):
    _name ="employee.certificate"
    name = fields.Char(string="Name",required=True)
    pn = fields.Char(string="Part Number")
    abr = fields.Char(string="Abbreviation")
    desc = fields.Text(string="Description")
    validity = fields.Integer(string="Validity")
    