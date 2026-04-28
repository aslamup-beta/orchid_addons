# -*- coding: utf-8 -*-

import itertools
from lxml import etree

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning



class res_users(models.Model):
    _inherit = "res.users"
    beta_digital_sign= fields.Binary(string="User Signature")
    beta_title = fields.Char(string="Job Title")
    


class res_company(models.Model):
    _inherit = "res.company"
    beta_digital_stamp= fields.Binary(string="Digital Stamp")
    beta_inv_stamp =fields.Binary(string="Invoice Stamp")
    beta_logo = fields.Binary(string="Logo")