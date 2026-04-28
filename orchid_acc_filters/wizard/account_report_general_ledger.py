# -*- coding: utf-8 -*-
from openerp.osv import fields, osv

class account_report_general_ledger(osv.osv_memory):
    _inherit = "account.report.general.ledger"

    def check_report(self, cr, uid, ids, context=None):
        print "printing from orchid acc filter"
        if context is None:
            context = {}
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids, ['date_from',  'date_to',  'fiscalyear_id', 'journal_ids', 'period_from', 'period_to',  'filter',  'chart_account_id', 'target_move','x_account_ids'], context=context)[0]

        if data['form']["x_account_ids"]:
            data['ids'] =list(set(data['form']["x_account_ids"] + context.get('active_ids', [])))
            data['model'] = 'account.account'
        for field in ['fiscalyear_id', 'chart_account_id', 'period_from', 'period_to']:
            if isinstance(data['form'][field], tuple):
                data['form'][field] = data['form'][field][0]
        used_context = self._build_contexts(cr, uid, ids, data, context=context)
        data['form']['periods'] = used_context.get('periods', False) and used_context['periods'] or []
        data['form']['used_context'] = dict(used_context, lang=context.get('lang', 'en_US'))
        return self._print_report(cr, uid, ids, data, context=context)

    _columns = {
        'x_account_ids': fields.many2many('account.account', 'x_account_report_general_ledger_account_rel', 'account_ledger_id', 'account_id', 'Accounts',domain=[('type', '!=', 'view')]),
    }

