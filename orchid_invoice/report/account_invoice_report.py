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

from openerp import tools
import openerp.addons.decimal_precision as dp
from openerp.osv import fields,osv

class account_invoice_report(osv.osv):
    _inherit = "account.invoice.report"


    _columns = {
        'od_account_invoice_id':fields.many2one('account.invoice','Invoice'),
        'price_total': fields.float('Invoice', readonly=True),
        
    }




    def _select(self):
        result = super(account_invoice_report, self)._select()
        select_str = result + """,sub.od_account_invoice_id as od_account_invoice_id
                              """
        return select_str

    def _sub_select(self):
        result = super(account_invoice_report, self)._sub_select()
        select_str = result + """,ai.id as od_account_invoice_id
                              """
              
        return select_str


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
