# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
import time
class account_balance_report(osv.osv_memory):
    _inherit = "account.balance.report"
    _columns = {
        'od_detail': fields.boolean('Detail'),
         'x_proj_fin_status':fields.boolean("Project Finance Status"),
        'od_child':fields.selection([(1,'Level 1'),(2,'Level 2'),(3,'Level 3'),(4,'Level 4'),(5,'Level 5')],'Level'),
         'od_currency_id': fields.many2one('res.currency',string="Currency",domain="[('active','=',True)]"),
         'od_branch_id': fields.many2one('od.cost.branch',string="Branch"),
#        'display_account': fields.selection([('all','All'), 
#                                            ('not_zero','With balance is not equal to 0'),
#                                            ],'Display Accounts', required=True),
#         'od_child':fields.boolean('Show Child'),
#       'od_print_template': fields.many2one('ir.actions.report.xml',string="Template",domain="[('report_name','=like','account.report_trialbalance%')]"),
    }
    _defaults = {
        'display_account': 'not_zero',
       # 'od_child': 4
    }
#     _defaults ={
# #                 'od_child':True
#                 }

    def onchange_filter(self, cr, uid, ids, filter='filter_no', fiscalyear_id=False, context=None):
        res = super(account_balance_report, self).onchange_filter(cr, uid, ids, filter=filter, fiscalyear_id=fiscalyear_id, context=context)
        if filter in ['filter_no', 'filter_period']:
            res['value'].update({'x_proj_fin_status': False})
        if filter == 'filter_date':
            res['value'] = {'period_from': False, 'period_to': False, 'date_from': time.strftime('%Y-%m-01'), 'date_to': time.strftime('%Y-%m-%d')}
        return res



    def _print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        data['form'].update(self.read(cr, uid, ids, ['od_detail','od_child','od_currency_id','x_proj_fin_status', 'od_branch_id'])[0])
        if data['model'] == 'account.account':
            data['form']['id'] = data['ids'][0]
        if data['form'].get('od_detail'):
            return self.pool['report'].get_action(cr, uid, [], 'account.report_trialbalance_detail', data=data, context=context)
        return self.pool['report'].get_action(cr, uid, [], 'account.report_trialbalance', data=data, context=context)


    
