# -*- encoding: utf-8 -*-
import time
from openerp.tools.translate import _
from openerp.osv import orm, fields
import logging
_logger = logging.getLogger(__name__)

class od_asset_report(orm.TransientModel):
    _name = 'od.asset.report' 
    _description = 'Asset Report'
    _columns = {
        'company_id': fields.many2one('res.company', 'Company',readonly=True),
        'category_ids': fields.many2many('account.asset.category', 'account_asset_report_rel','category_id','report_id','Asset Category'),
        'period_from': fields.many2one('account.period', 'Start Period',required=True,domain="[('company_id','=',company_id)]"),
        'period_to': fields.many2one('account.period', 'End Period',required=True,domain="[('company_id','=',company_id)]"),
#        'state': fields.selection([('draft','Draft'),('open','Running'),('close','Close')], 'Status', required=True)
    }    
    _defaults={
        'company_id': lambda s,cr,uid,c: s.pool.get('res.company')._company_default_get(cr, uid, 'res.partner', context=c),
    }

    def pre_print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        #data['form'].update(self.read(cr, uid, ids, ['display_account'], context=context)[0])
        return data

    def build_filter(self,cr,uid,ids,context=None):
        data = self.read(cr, uid, ids,['category_ids','company_id','period_from','period_to'])[0]
        
        if not data.get('category_ids'):
            data['category_ids'] = self.pool['account.asset.category'].search(cr,uid,[('company_id','=',data.get('company_id')[0])])
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
            acc_periods = acc_period.search(cr,uid,[('company_id','=',data.get('company_id')[0]),('id','<',period_from)])
            data['accum_periods'] = acc_periods or []
            data['period_ids'] = acc_period.build_ctx_periods(cr,uid,period_from,period_to)
        return data

    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = self.build_filter(cr,uid,ids,context=context)
        return self.pool['report'].get_action(cr, uid, [], 'orchid_asset.report_asset_statement', data=data, context=context)

