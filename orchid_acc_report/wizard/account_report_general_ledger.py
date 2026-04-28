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
        'od_print_template': fields.many2one('ir.actions.report.xml',string="Template",domain="[('report_name','=like','account.report_generalledger%')]"),
        'od_partner_ids': fields.many2many('res.partner', string='Filter on partner',help="Only selected partners will be printed.Leave empty to print all partners.",domain="['|',('customer','=',True),('supplier','=',True)]"),

        'od_employe_ids': fields.many2many('res.partner','res_partner_report_employee_general_ledger_rel','ledger_id','partner_id', string='Filter on Employe',help="Only selected partners will be printed.Leave empty to print all partners.",domain="[('employee','=',True)]"),

        'od_analytic_account_ids': fields.many2many('account.analytic.account','analytic_report_general_ledger_rel', 'ledger', 'analytic_id', string='Analytic'),
        'od_account_ids' : fields.many2many('account.account','od_account_report_general_ledger_rel','report_wiz_id','account_id',string="Accounts"),
        'od_branch_ids': fields.many2many('od.cost.branch','account_gen_ledg_bracnh_reporcv_rel', 'wiz_id', 'branch_id', string='Branch'),
        'od_division_ids': fields.many2many('od.cost.division','account_gen_ledg_division_reporcv_rel', 'wiz_id', 'division_id', string='Division'),

    }


    def _build_contexts(self, cr, uid, ids, data, context=None):
        result = super(account_report_general_ledger, self)._build_contexts(cr, uid, ids,data, context=context)
        partners = 'od_partner_ids' in data['form'] and data['form']['od_partner_ids'] or []
        employees = 'od_employe_ids' in data['form'] and data['form']['od_employe_ids'] or []
        result['partner_ids'] = partners + employees
        result['analytic_account_ids'] = 'od_analytic_account_ids' in data['form'] and data['form']['od_analytic_account_ids'] or False
        result['od_account_ids'] = 'od_account_ids' in data['form'] and data['form']['od_account_ids'] or False
        result['od_branch_ids'] = 'od_branch_ids' in data['form'] and data['form']['od_branch_ids'] or False
        result['od_division_ids'] = 'od_division_ids' in data['form'] and data['form']['od_division_ids'] or False
        return result


#     def check_report(self, cr, uid, ids, context=None):
#         print "printing from orchid account repooort"
#         if context is None:
#             context = {}
#         data = {}
#         data['ids'] = context.get('active_ids', [])
#         data['model'] = context.get('active_model', 'ir.ui.menu')
#         data['form'] = self.read(cr, uid, ids, ['date_from',  'date_to',  'fiscalyear_id', 'journal_ids', 'od_partner_ids','od_employe_ids','od_analytic_account_ids','od_branch_ids','od_division_ids','od_account_ids','period_from', 'period_to',  'filter',  'chart_account_id', 'target_move'], context=context)[0]
#         for field in ['fiscalyear_id', 'chart_account_id', 'period_from', 'period_to']:
#             if isinstance(data['form'][field], tuple):
#                 data['form'][field] = data['form'][field][0]
#         used_context = self._build_contexts(cr, uid, ids, data, context=context)
#         data['form']['periods'] = used_context.get('periods', False) and used_context['periods'] or []
#         data['form']['used_context'] = dict(used_context, lang=context.get('lang', 'en_US'))
#         return self._print_report(cr, uid, ids, data, context=context)


 
#     def _print_report(self, cr, uid, ids, data, context=None):
#         print "printing generla ledger>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
#         if context is None:
#             context = {}
#         data = self.pre_print_report(cr, uid, ids, data, context=context)
#         data['form'].update(self.read(cr, uid, ids, ['landscape',  'initial_balance', 'od_print_template','od_partner_ids','od_employe_ids','od_analytic_account_ids','od_branch_ids','od_division_ids','od_account_ids','amount_currency', 'sortby'])[0])
#         if not data['form']['fiscalyear_id']:# GTK client problem onchange does not consider in save record
#             data['form'].update({'initial_balance': False})
#  
#         if data['form']['landscape'] is False:
#             data['form'].pop('landscape')
#         else:
#             context['landscape'] = data['form']['landscape']
#         if data['model'] == 'account.account':
#             data['form']['id'] = data['ids'][0]
#         if data['form'].get('od_print_template'):
#             report_obj = self.pool.get('ir.actions.report.xml')
#             od_print_template = data['form'].get('od_print_template')[0]
#             if od_print_template:
#                 report_data = report_obj.browse(cr, uid,od_print_template)
#                 report_name = str(report_data.report_name)
#                 return self.pool['report'].get_action(cr, uid, [], report_name, data=data, context=context)
#         
#         if context.get('xls_export'):
#             print "context xlssssss.>>>>>>>>>>>>>>>"
#             return {'type': 'ir.actions.report.xml',
#                         'report_name': 'account.account_report_general_ledger_xls',
#                         'datas': data}
#         
#         
#         return self.pool['report'].get_action(cr, uid, [], 'account.report_generalledger', data=data, context=context)
 
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
