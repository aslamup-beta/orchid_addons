# -*- encoding: utf-8 -*-
##############################################################################
import time
from openerp.osv import osv
from openerp.report import report_sxw
from pprint import pprint
class report_orchid_trend(report_sxw.rml_parse):
    _name = "orchid_acc_report.report.orchid.trend"

    def set_context(self, objects, data, ids, report_type=None):
        return super(report_orchid_trend, self).set_context(objects, data, ids, report_type=report_type)


    def __init__(self, cr, uid, name, context):
        super(report_orchid_trend, self).__init__(cr, uid, name, context=context)

        self.localcontext.update({
            'time': time,
            'get_lines': self._get_lines,
            'get_period_name': self._get_period_name,
        })
        
    def od_tup_to_dict(self,res):
        result =[]
        for data in res:
            balance = dict(data['balance'])
            data['balance'] =balance
            result.append(data)
        return result
    def od_deduplicate(self,l):
        result = []
        for item in l :
            check = False
            # check item, is it exist in result yet (r_item)
            for r_item in result :
                if item['obj_id'] == r_item['obj_id'] :
                    # if found, add all key to r_item ( previous record)
                    check = True
                    balance = r_item['balance'] 
                    for line in item['balance']:
                        balance.append(line)
                    r_item['balance'] = balance
            if check == False :
                # if not found, add item to result (new record)
                result.append( item )
        
        bal_to_dict = self.od_tup_to_dict(result)
        return bal_to_dict
    
    def od_make_dict(self,res,rpt_type):
        result =[]
        if rpt_type == 'ledger':
            obj_pool = self.pool['account.account']
            for data in res:
                obj = obj_pool.browse(self.cr,self.uid,data[0])
                result.append({'obj_id':obj,'balance':[(data[1],data[2])] })
        if rpt_type == 'partner':
            obj_pool = self.pool['res.partner']
            for data in res:
                obj = obj_pool.browse(self.cr,self.uid,data[0])
                result.append({'obj_id':obj,'balance':[(data[1],data[2])] })
        if rpt_type == 'analytic':
            obj_pool = self.pool['account.analytic.account']
            for data in res:
                obj = obj_pool.browse(self.cr,self.uid,data[0])
                result.append({'obj_id':obj,'balance':[(data[1],data[2])] })               
        if rpt_type == 'costcentre':
            obj_pool = self.pool['od.cost.centre']
            for data in res:
                obj = obj_pool.browse(self.cr,self.uid,data[0])
                result.append({'obj_id':obj,'balance':[(data[1],data[2])] })
        res = self.od_deduplicate(result)        
        return res

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
        pprint(dict_res)
        return dict_res
    def _get_period_name(self,val):
        period_ids = val.get('period_ids')
        period_obj = self.pool['account.period']
        name = map(lambda x:period_obj.read(self.cr,self.uid,x,['name']),period_ids)
        return name
#     def _get_asset_by_category(self,category_id):
#         asset_obj = self.pool['account.asset.asset']
#         asset_ids = asset_obj.search(self.cr, self.uid, [('category_id','=',category_id)])
#         return asset_obj.browse(self.cr,self.uid,asset_ids)
# 
#     def _get_category_by_id(self,category_id):
#         if category_id:
#             return self.pool['account.asset.category'].browse(self.cr, self.uid,category_id).name
#         return {}
# 
#     def _get_history_lines(self,val,asset):
#         move_ids = []
#         if val.get('period_ids'):
#             acc_move_pool = self.pool['account.move.line']
#             move_ids = acc_move_pool.search(self.cr, self.uid,[('period_id','in',val.get('period_ids')),('asset_id','=',asset.id)])
#         else:
#             return asset.account_move_line_ids
#         return self.pool['account.move.line'].browse(self.cr,self.uid,move_ids)
# 
# 
#     def _get_depreciation_amt(self,val,asset):
#         move_ids = []
#         res =0.0
#         if val.get('period_ids'):
#             acc_move_pool = self.pool['account.move.line']
#             move_ids = acc_move_pool.search(self.cr, self.uid,[('period_id','in',val.get('period_ids')),('asset_id','=',asset.id)])
#             data = acc_move_pool.read(self.cr,self.uid,move_ids,['debit','credit'])
#             res = data and (sum([val.get('debit') for val in data]) - sum([val.get('credit') for val in data])) or 0.0
#         print "DD",asset.id,"&&",res
#         return res
# 
#     def _get_acc_depreciation_amt(self,val,asset):
#         move_ids = []
#         res = 0.0
#         acc_move_pool = self.pool['account.move.line']
# 
#         if val.get('accum_periods'):
#             accu_move_ids = acc_move_pool.search(self.cr, self.uid,[('period_id','in',val.get('accum_periods')),('asset_id','=',asset.id)]) or []
#             print "####",val.get('accum_periods'),"~~~~",asset.id
#             accu_data = acc_move_pool.read(self.cr,self.uid,accu_move_ids,['debit','credit'])
#             res = accu_data and (sum([val.get('debit') for val in accu_data]) - sum([val.get('credit') for val in accu_data])) or 0.0
#         print "DD",asset.id,"&&",res
#         return res

class report_asset_statement(osv.AbstractModel):
    _name = 'report.orchid_acc_report.report_orchid_trend'
    _inherit = 'report.abstract_report'
    _template = 'orchid_acc_report.report_orchid_trend'
    _wrapped_report_class = report_orchid_trend

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
