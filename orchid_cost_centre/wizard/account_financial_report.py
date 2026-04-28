from openerp.osv import fields, osv


class accounting_report(osv.osv_memory):
    _inherit = 'accounting.report'

    def _get_all_cost_centre(self, cr, uid, context=None):
        return self.pool.get('od.cost.centre').search(cr, uid ,[('code','=',1)])[0]

    _columns = {
        'od_cost_centre_ids': fields.many2many('od.cost.centre', string='CostCentre'),
#        'od_cost_centre_id': fields.many2one('od.cost.centre','CostCentre'),
    }
    _defaults = {
#        'od_cost_centre_id': _get_all_cost_centre
    }

    def check_report(self, cr, uid, ids, context=None):
        result = super(accounting_report, self).check_report(cr, uid, ids, context=context)
        used_context = result['data']['form']['used_context']
        data_toadd = self.read(cr, uid, ids, ['od_cost_centre_ids'])[0]
        used_context['od_cost_centre_ids'] = data_toadd['od_cost_centre_ids']
        result['data']['form']['used_context'] = used_context
        return result


#    def _build_contexts(self, cr, uid, ids, data, context=None):
#        print "******ID in _build_contexts:",ids
#        if context is None:
#            context = {}
#        result = {}
#        result['fiscalyear'] = 'fiscalyear_id' in data['form'] and data['form']['fiscalyear_id'] or False
#        result['journal_ids'] = 'journal_ids' in data['form'] and data['form']['journal_ids'] or False
#        result['chart_account_id'] = 'chart_account_id' in data['form'] and data['form']['chart_account_id'] or False
#        result['od_cost_centre_ids'] = 'od_cost_centre_ids' in data['form'] and data['form']['od_cost_centre_ids'] or False
#        result['state'] = 'target_move' in data['form'] and data['form']['target_move'] or ''
#        if data['form']['filter'] == 'filter_date':
#            result['date_from'] = data['form']['date_from']
#            result['date_to'] = data['form']['date_to']
#        elif data['form']['filter'] == 'filter_period':
#            if not data['form']['period_from'] or not data['form']['period_to']:
#                raise osv.except_osv(_('Error!'),_('Select a starting and an ending period.'))
#            result['period_from'] = data['form']['period_from']
#            result['period_to'] = data['form']['period_to']
#        return result


#    def _build_comparison_context(self, cr, uid, ids, data, context=None):
#        print "******ID in _build_comparison_context:",ids
#        if context is None:
#            context = {}
#        result = {}
#        result['fiscalyear'] = 'fiscalyear_id_cmp' in data['form'] and data['form']['fiscalyear_id_cmp'] or False
#        result['journal_ids'] = 'journal_ids' in data['form'] and data['form']['journal_ids'] or False
#        result['od_cost_centre_ids'] = 'od_cost_centre_ids' in data['form'] and data['form']['od_cost_centre_ids'] or False
#        result['chart_account_id'] = 'chart_account_id' in data['form'] and data['form']['chart_account_id'] or False
#        result['state'] = 'target_move' in data['form'] and data['form']['target_move'] or ''
#        if data['form']['filter_cmp'] == 'filter_date':
#            result['date_from'] = data['form']['date_from_cmp']
#            result['date_to'] = data['form']['date_to_cmp']
#        elif data['form']['filter_cmp'] == 'filter_period':
#            if not data['form']['period_from_cmp'] or not data['form']['period_to_cmp']:
#                raise osv.except_osv(_('Error!'),_('Select a starting and an ending period'))
#            result['period_from'] = data['form']['period_from_cmp']
#            result['period_to'] = data['form']['period_to_cmp']
#        return result

#    def check_report(self, cr, uid, ids, context=None):
#        if context is None:
#            context = {}
#        res = super(accounting_report, self).check_report(cr, uid, ids, context=context)
#        data = {}
##'date_from',  'date_to',  'fiscalyear_id','period_from', 'period_to',  'filter'
#        data['form'] = self.read(cr, uid, ids, ['account_report_id', 'date_from_cmp',  'date_to_cmp',  'fiscalyear_id_cmp', 'journal_ids', 'period_from_cmp', 'period_to_cmp', 'filter_cmp',  'chart_account_id', 'target_move','od_cost_centre_ids'], context=context)[0]
#        for field in ['fiscalyear_id_cmp', 'chart_account_id', 'period_from_cmp', 'period_to_cmp', 'account_report_id']:
#            if isinstance(data['form'][field], tuple):
#                data['form'][field] = data['form'][field][0]
##        used_context = self._build_contexts(cr, uid, ids, data, context=context)
#        comparison_context = self._build_comparison_context(cr, uid, ids, data, context=context)
#        res['datas']['form']['comparison_context'] = comparison_context
##        res['datas']['form']['used_context']['od_c'] = dict(used_context, lang=context.get('lang', 'en_US'))
#        print "$$$$$$$$$",res
#        return res

#    def _print_report(self, cr, uid, ids, data, context=None):
#        data['form'].update(self.read(cr, uid, ids, ['date_from_cmp',  'debit_credit', 'date_to_cmp',  'fiscalyear_id_cmp', 'period_from_cmp', 'period_to_cmp',  'filter_cmp', 'account_report_id', 'enable_filter', 'label_filter','target_move','od_cost_centre_ids'], context=context)[0])
#        print "@@@@@@",data
#        return {
#            'type': 'ir.actions.report.xml',
#            'report_name': 'account.financial.report',
#            'datas': data,
#        }


