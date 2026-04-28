# -*- coding: utf-8 -*-
import openerp
from openerp import tools
from openerp.osv import fields, osv
from openerp.tools.translate import _
class pos_config(osv.osv):
    _inherit = 'pos.config'
    _columns = {
        'od_cost_centre_id': fields.many2one('od.cost.centre','Cost Centre'),
    }
