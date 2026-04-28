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


class account_report_general_ledger(osv.osv_memory):
    _inherit = "account.report.general.ledger"
    _columns = {
        'od_cost_centre_ids': fields.many2many('od.cost.centre','cost_centre_report_general_ledger_rel', 'ledger', 'cost_centre_id', string='Cost Centre'),
    }


    def _build_contexts(self, cr, uid, ids, data, context=None):
        result = super(account_report_general_ledger, self)._build_contexts(cr, uid, ids,data, context=context)
        result['od_cost_centre_ids'] = 'od_cost_centre_ids' in data['form'] and data['form']['od_cost_centre_ids'] or False
        return result


    def check_report(self, cr, uid, ids, context=None):
        print "check report from orchid cost centereeeeee"
        if context is None:
            context = {}
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids, ['date_from',  'date_to',  'fiscalyear_id', 'journal_ids', 'od_partner_ids','od_employe_ids','od_analytic_account_ids','od_branch_ids','od_division_ids','od_account_ids','od_cost_centre_ids','period_from', 'period_to',  'filter',  'chart_account_id', 'target_move'], context=context)[0]
        for field in ['fiscalyear_id', 'chart_account_id', 'period_from', 'period_to']:
            if isinstance(data['form'][field], tuple):
                data['form'][field] = data['form'][field][0]
        used_context = self._build_contexts(cr, uid, ids, data, context=context)
        data['form']['periods'] = used_context.get('periods', False) and used_context['periods'] or []
        data['form']['used_context'] = dict(used_context, lang=context.get('lang', 'en_US'))
        return self._print_report(cr, uid, ids, data, context=context)


 
    def _print_report(self, cr, uid, ids, data, context=None):
        print "print report from orchid cost centereeeeee"
        if context is None:
            context = {}
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        data['form'].update(self.read(cr, uid, ids, ['landscape',  'initial_balance', 'od_print_template','od_partner_ids','od_employe_ids','od_analytic_account_ids','od_branch_ids','od_division_ids','od_cost_centre_ids','od_account_ids','amount_currency', 'sortby'])[0])
        if not data['form']['fiscalyear_id']:# GTK client problem onchange does not consider in save record
            data['form'].update({'initial_balance': False})
 
        if data['form']['landscape'] is False:
            data['form'].pop('landscape')
        else:
            context['landscape'] = data['form']['landscape']
        if data['model'] == 'account.account':
            data['form']['id'] = data['ids'][0]
        if data['form'].get('od_print_template'):
            report_obj = self.pool.get('ir.actions.report.xml')
            od_print_template = data['form'].get('od_print_template')[0]
            if od_print_template:
                report_data = report_obj.browse(cr, uid,od_print_template)
                report_name = str(report_data.report_name)
                return self.pool['report'].get_action(cr, uid, [], report_name, data=data, context=context)
        if context.get('xls_export'):
            # we update form with display account value
            data = self.pre_print_report(cr, uid, ids, data, context=context)
            return {'type': 'ir.actions.report.xml',
                    'report_name': 'account.account_report_general_ledger_xls',
                    'datas': data}
        return self.pool['report'].get_action(cr, uid, [], 'account.report_generalledger', data=data, context=context)
 
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
