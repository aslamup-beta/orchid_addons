# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
class account_partner_ledger(osv.osv_memory):
    _inherit = "account.partner.ledger"

    def check_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids, ['date_from',  'date_to',  'fiscalyear_id', 'journal_ids', 'period_from', 'period_to',  'filter',  'chart_account_id', 'target_move','x_account_ids','x_partner_ids'], context=context)[0]

        if data['form']["x_partner_ids"]:
            data['ids'] =list(set(data['form']["x_partner_ids"] + context.get('active_ids', [])))
            data['model'] = 'res.partner'
        for field in ['fiscalyear_id', 'chart_account_id', 'period_from', 'period_to']:
            if isinstance(data['form'][field], tuple):
                data['form'][field] = data['form'][field][0]
        used_context = self._build_contexts(cr, uid, ids, data, context=context)
        data['form']['periods'] = used_context.get('periods', False) and used_context['periods'] or []
        data['form']['used_context'] = dict(used_context, lang=context.get('lang', 'en_US'))
        return self._print_report(cr, uid, ids, data, context=context)

    _columns = {
        'x_partner_ids': fields.many2many('res.partner', 'x_partner_ledger_journal_rel', 'account_ledger_id', 'partner_id', 'Partners'),
    }
