# -*- encoding: utf-8 -*-
##############################################################################
import time
from openerp.report import report_sxw
from openerp.addons.orchid_acc_report.report.orchid_trend_report import report_orchid_trend
from openerp.tools.translate import _
from openerp.osv import osv


class report_orchid_trend(report_orchid_trend):
    _inherit = "orchid_acc_report.report.orchid.trend"

    def __init__(self, cr, uid, name, context=None):
        super(report_orchid_trend, self).__init__(cr, uid, name, context=context)

#    def __init__(self, cr, uid, name, context):
#        super(report_orchid_trend, self).__init__(cr, uid, name, context=context)

#        self.localcontext.update({
#            'time': time,
#            'get_lines': self._get_lines,
#            'get_period_name': self._get_period_name,
#        })

    def _get_lines(self,val):
        period_ids =val.get('period_ids')
        query = ''
        domain = []
        if val.get('account_ids'):
            account_obj = self.pool.get('account.account')
            account_id =  val.get('account_ids')
            account_ids = account_obj.search(self.cr, self.uid,[('id','child_of',account_id)])
            domain.append(('account_id','in', account_ids))
        if val.get('analytic_ids'):
            domain.append(('analytic_account_id','in',val.get('analytic_ids')))
        if val.get('partner_ids'):
            domain.append(('partner_id','in',val.get('partner_ids')))
        if val.get('costcentre_ids'):
            domain.append(('od_cost_centre_id','in',val.get('costcentre_ids')))
        
        move_ids = self.pool['account.move.line'].search(self.cr,self.uid,domain) or []
       
        if not move_ids:
            return []

        
        if val.get('group_by') == 'ledger':
            query ="SELECT account_id ,period_id, (sum(debit) - sum(credit)) as balance FROM account_entries_report WHERE period_id IN %s  and id IN %s group by account_id, period_id"
        if val.get('group_by') == 'partner':
            query = "SELECT partner_id ,period_id, (sum(debit) - sum(credit)) as balance FROM account_entries_report WHERE period_id IN %s and id IN %s group by partner_id, period_id"
        if val.get('group_by') == 'analytic':
            query = "SELECT analytic_account_id ,period_id, (sum(debit) - sum(credit)) as balance FROM account_entries_report WHERE period_id IN %s and id IN %s group by analytic_account_id, period_id"
        if val.get('group_by') == 'costcentre':
            query = "SELECT od_cost_centre_id ,period_id, (sum(debit) - sum(credit)) as balance FROM account_entries_report WHERE period_id IN %s and id IN %s group by od_cost_centre_id, period_id"
        params = (tuple(period_ids),tuple(move_ids))
        self.cr.execute(query,params)
        res = self.cr.fetchall()
        dict_res = self.od_make_dict(res,val.get('group_by'))
        return dict_res

class report_asset_statement(osv.AbstractModel):
    _name = 'report.orchid_acc_report.report_orchid_trend'
    _inherit = 'report.abstract_report'
    _template = 'orchid_acc_report.report_orchid_trend'
    _wrapped_report_class = report_orchid_trend

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
