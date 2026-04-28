# -*- coding: utf-8 -*-


import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.osv import fields, osv
from openerp.tools.translate import _


class account_aged_trial_balance(osv.osv_memory):
    _inherit = 'account.aged.trial.balance'

    _columns = {
        'od_partner_ids': fields.many2many('res.partner', 'partner_report_aged_balance_rel' , string='Filter on partner',domain="['|',('customer','=',True),('supplier','=',True)]"),
        'od_sale_person_ids': fields.many2many('res.users', 'sales_person_aged_balance_report_rel' , string='Filter on Sales Person'),
        'od_account_ids':fields.many2many('account.account','wiz_id','account_id' ,'account_agingreport_aged_balance_report_rel' , string='Filter on Accounts'),
        'od_cost_centre_ids': fields.many2many('od.cost.centre','account_agingreportcost_centre_reporcv_rel', 'wiz_id', 'cost_centre_id', string='Cost Centre'),
        'od_branch_ids': fields.many2many('od.cost.branch','account_agingreport_bracnh_reporcv_rel', 'wiz_id', 'branch_id', string='Branch'),
        'od_division_ids': fields.many2many('od.cost.division','account_agingreport_division_reporcv_rel', 'wiz_id', 'division_id', string='Division'),

    }

    
    def xls_export(self, cr, uid, ids, context=None):
        return self.check_report(cr, uid, ids, context=context)
    def check_report(self, cr, uid, ids, context=None):
        result = super(account_aged_trial_balance, self).check_report(cr, uid, ids, context=context)
        dat = result.get('data',False)
        used_context = {}
        
        if dat:
            used_context = result['data']['form']['used_context'] or {}
        
        data_toadd = self.read(cr, uid, ids, ['od_partner_ids','od_sale_person_ids','od_account_ids','od_cost_centre_ids','od_branch_ids','od_division_ids'])[0]

        inv_ids = self.pool['account.invoice'].search(cr,uid,[('user_id','in',data_toadd['od_sale_person_ids'])])

        sales_person_ids = []
        if inv_ids:
            inv_data = self.pool['account.invoice'].read(cr, uid,inv_ids,['partner_id'])
            sales_person_ids = [x.get('partner_id')[0] for x in inv_data]
        
        if dat:
            used_context['partner_ids'] = data_toadd['od_partner_ids'] + sales_person_ids
            used_context['od_account_ids'] = data_toadd['od_account_ids']
            used_context['od_cost_centre_ids'] = data_toadd['od_cost_centre_ids']
            used_context['od_branch_ids'] = data_toadd['od_branch_ids']
            used_context['od_division_ids'] = data_toadd['od_division_ids']
            result['data']['form']['used_context'] = used_context
        
        return result


    def _build_contexts(self, cr, uid, ids, data, context=None):
        result = super(account_aged_trial_balance, self)._build_contexts(cr, uid, ids,data, context=context)
        return result


    def _print_report(self, cr, uid, ids, data, context=None):
        res = {}
        context = context or {}
       
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        
        data['form'].update(self.read(cr, uid, ids, ['period_length', 'direction_selection',' 00','od_sale_person_ids','od_account_ids','od_cost_centre_ids','od_branch_ids','od_division_ids'])[0])
        period_length = data['form']['period_length']
        if period_length<=0:
            raise osv.except_osv(_('User Error!'), _('You must set a period length greater than 0.'))
        if not data['form']['date_from']:
            raise osv.except_osv(_('User Error!'), _('You must set a start date.'))

        start = datetime.strptime(data['form']['date_from'], "%Y-%m-%d")

        if data['form']['direction_selection'] == 'past':
            for i in range(5)[::-1]:
                stop = start - relativedelta(days=period_length)
                res[str(i)] = {
                    'name': (i!=0 and (str((5-(i+1)) * period_length) + '-' + str((5-i) * period_length)) or ('+'+str(4 * period_length))),
                    'stop': start.strftime('%Y-%m-%d'),
                    'start': (i!=0 and stop.strftime('%Y-%m-%d') or False),
                }
                start = stop - relativedelta(days=1)
        else:
            for i in range(5):
                stop = start + relativedelta(days=period_length)
                res[str(5-(i+1))] = {
                    'name': (i!=4 and str((i) * period_length)+'-' + str((i+1) * period_length) or ('+'+str(4 * period_length))),
                    'start': start.strftime('%Y-%m-%d'),
                    'stop': (i!=4 and stop.strftime('%Y-%m-%d') or False),
                }
                start = stop + relativedelta(days=1)
        data['form'].update(res)
        if data.get('form',False):
            data['ids']=[data['form'].get('chart_account_id',False)]
        
        return self.pool['report'].get_action(cr, uid, [], 'account.report_agedpartnerbalance', data=data, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
