# -*- encoding: utf-8 -*-
import time
from openerp.tools.translate import _
from openerp.osv import orm, fields
import logging
_logger = logging.getLogger(__name__)

class od_trend_report(orm.TransientModel):
    _name = 'od.trend.report' 
    _description = 'Trend Report'
    _columns = {
        'company_id': fields.many2one('res.company', 'Company',readonly=True),
        'fiscal_year':fields.many2one('account.fiscalyear','Fiscal Year',domain="[('company_id','=',company_id)]"),
        'period_from': fields.many2one('account.period', 'Start Period',required=True,domain="[('company_id','=',company_id)]"),
        'period_to': fields.many2one('account.period', 'End Period',required=True,domain="[('company_id','=',company_id)]"),
        'group_by': fields.selection([('ledger','Ledger'),('partner','Partner'),('analytic','Analytic'),('costcentre','Cost Centre')], 'Group By', required=True),
		'account_ids' : fields.many2many('account.account','od_rel_trend_account','trend_id','acc_id','Account',domain="[('company_id','=',company_id)]"),
		'analytic_ids': fields.many2many('account.analytic.account','od_rel_trend_anlytic','trend_id','analytic_id','Analytic',domain="[('company_id','=',company_id)]"),
		'partner_ids': fields.many2many('res.partner','od_rel_trend_partner','trend_id','partner_id','Partner',domain="['|',('company_id','=',company_id),('company_id','=','')]"),
    }    
    
    
    def _get_start_period(self,cr,uid,context=None):
        now = time.strftime('%Y-%m-%d')
        data=now.split('-')
        data[1] = '01'
        now = '-'.join(data)
        periods = self.pool.get('account.period').search(cr, uid, [('date_start', '<', now), ('date_stop', '>', now)], limit=1 )
        return periods and periods[0] or False
   
    def _get_period(self, cr, uid, context=None):
        now = time.strftime('%Y-%m-%d')
        periods = self.pool.get('account.period').search(cr, uid, [('date_start', '<', now), ('date_stop', '>', now)], limit=1 )
        return periods and periods[0] or False
    
    def _get_fiscalyear(self, cr, uid, context=None):
        if context is None:
            context = {}
        now = time.strftime('%Y-%m-%d')
        company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        domain = [('company_id', '=', company_id), ('date_start', '<', now), ('date_stop', '>', now)]
        fiscalyears = self.pool.get('account.fiscalyear').search(cr, uid, domain, limit=1)
        return fiscalyears and fiscalyears[0] or False

    
    _defaults={
        'company_id': lambda s,cr,uid,c: s.pool.get('res.company')._company_default_get(cr, uid, 'res.partner', context=c),
        'fiscal_year':_get_fiscalyear,
        'period_from':_get_start_period,
        'period_to': _get_period,
        'group_by':'ledger',
    }

    def pre_print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        #data['form'].update(self.read(cr, uid, ids, ['display_account'], context=context)[0])
        return data

    def build_filter(self,cr,uid,ids,context=None):
        data = self.read(cr, uid, ids,['company_id','period_from','period_to','fiscal_year','group_by','account_ids','analytic_ids','partner_ids'])[0]
      
        if data.get('period_from') or data.get('period_to'):
            acc_period = self.pool['account.period']
            period_from = data.get('period_from') and data.get('period_from')[0] or False
            period_to = data.get('period_to') and data.get('period_to')[0] or False
            if not period_from:
                period_from = acc_period.search(cr,uid,[('company_id','=',data.get('company_id')[0])])
                period_from.sort()
                period_from = period_from[0]
            if not period_to:
                period_to = acc_period.search(cr,uid,[('company_id','=',data.get('company_id')[0])])
                period_to.sort(reverse=True)
                period_to=period_to[0]
#             acc_periods = acc_period.search(cr,uid,[('company_id','=',data.get('company_id')[0]),('id','<',period_from)])
#             data['accum_periods'] = acc_periods or []
            data['period_ids'] = acc_period.build_ctx_periods(cr,uid,period_from,period_to)
        return data

    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = self.build_filter(cr,uid,ids,context=context)
       
        return self.pool['report'].get_action(cr, uid, [], 'orchid_acc_report.report_orchid_trend', data=data, context=context)

