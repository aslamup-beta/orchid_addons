# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
class account_partner_ledger(osv.osv_memory):
    """
    This wizard will provide the partner Ledger in different Templates.
    """
    _inherit = 'account.partner.ledger'
    _columns = {
        'od_print_template': fields.many2one('ir.actions.report.xml',string="Template",domain="[('report_name','=like','account.report_partnerledger%')]"),
        'od_paid_invoice': fields.boolean('Paid Invoice'),
        'od_aged_on': fields.date('Aged On'),
    }

    def _print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        data['form'].update(self.read(cr, uid, ids, ['initial_balance', 'filter', 'page_split','od_print_template', 'amount_currency','od_paid_invoice','od_aged_on'])[0])
        if data['form'].get('od_print_template'):
            report_obj = self.pool.get('ir.actions.report.xml')
            od_print_template = data['form'].get('od_print_template')[0]
            if od_print_template:
                report_data = report_obj.browse(cr, uid,od_print_template)
                report_name = str(report_data.report_name)
                return self.pool['report'].get_action(cr, uid, [], report_name, data=data, context=context)
        return self.pool['report'].get_action(cr, uid, [], 'account.report_partnerledger', data=data, context=context)
