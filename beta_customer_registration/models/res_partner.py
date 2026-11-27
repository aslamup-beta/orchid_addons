# -*- coding: utf-8 -*-
from openerp import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    contact_dept = fields.Selection([
        ('pro', 'Procurement'),
        ('net', 'Networking'),
        ('cs', 'Cyber Security'),
        ('dc', 'Data Center'),
        ('ot', 'OT Security'),
        ('info', 'InfoSec / GRC'),
    ], string='Department', default=False)
