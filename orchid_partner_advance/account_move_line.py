# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from datetime import datetime

from openerp import workflow
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp import tools
from openerp.report import report_sxw
import openerp

class account_move_line(osv.osv):
    _inherit = "account.move.line"


    def _get_advance(self, cr, uid, ids, field_name, arg, context=None): 
        res ={} 
        for obj in self.browse(cr, uid, ids, context): 
            check_advance = self.pool.get('account.voucher').search(cr,uid, [('move_ids','in',[obj.id]),('od_advance_payment','=',True)])
            res[obj.id] = check_advance and True or False
        return res 
    _columns = {
        'od_advance_payment': fields.function(_get_advance,string='Advance',type='boolean',store=True),
    }

    _defaults = {  
        'od_advance_payment': False,
        }










