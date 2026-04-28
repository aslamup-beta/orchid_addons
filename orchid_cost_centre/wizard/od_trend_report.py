# -*- encoding: utf-8 -*-
import time
from openerp.tools.translate import _
from openerp.osv import orm, fields
import logging
_logger = logging.getLogger(__name__)

class od_trend_report(orm.TransientModel):
    _inherit = 'od.trend.report' 
    _columns = {
		'costcentre_ids': fields.many2many('od.cost.centre','od_rel_trend_costcentre_id','trend_id','cost_centre_id','Partner',domain="['|',('company_id','=',company_id),('company_id','=','')]"),
    }    


    def build_filter(self,cr,uid,ids,context=None):
        data = self.read(cr, uid, ids,['company_id','period_from','period_to','fiscal_year','group_by','account_ids','analytic_ids','partner_ids','costcentre_ids'])[0]
      
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

