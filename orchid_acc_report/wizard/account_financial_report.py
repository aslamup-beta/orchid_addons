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

from openerp.osv import fields, osv
import pyPdf

class accounting_report(osv.osv_memory):
    _inherit = "accounting.report"
   

    _columns = {
                 'od_print_template': fields.many2one('ir.actions.report.xml',string="Template",domain="[('report_name','=like','account.report_financial%')]"),
    }
    def _print_report(self, cr, uid, ids, data, context=None):
        data['form'].update(self.read(cr, uid, ids, ['date_from_cmp',  'debit_credit', 'date_to_cmp',  'fiscalyear_id_cmp', 'period_from_cmp', 'period_to_cmp',  'filter_cmp', 'account_report_id', 'enable_filter', 'label_filter','target_move','od_print_template'], context=context)[0])
        if data['form'].get('od_print_template'):
            report_obj = self.pool.get('ir.actions.report.xml')
            od_print_template = data['form'].get('od_print_template')[0]
            if od_print_template:
                report_data = report_obj.browse(cr, uid,od_print_template)
                report_name = str(report_data.report_name)
                return self.pool['report'].get_action(cr, uid, [], report_name, data=data, context=context)
        return self.pool['report'].get_action(cr, uid, [], 'account.report_financial', data=data, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
