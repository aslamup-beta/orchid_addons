# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
class res_currency(osv.osv):
    _inherit = 'res.currency'
    _columns = {
        'od_pos':fields.boolean('Available in POS'),
    }
