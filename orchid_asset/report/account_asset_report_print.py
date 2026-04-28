# -*- encoding: utf-8 -*-
##############################################################################
import time
from openerp.osv import osv
from openerp.report import report_sxw

class report_orchid_asset(report_sxw.rml_parse):
    _name = "orchid_asset.report.orchid.asset"

    def set_context(self, objects, data, ids, report_type=None):
        return super(report_orchid_asset, self).set_context(objects, data, ids, report_type=report_type)


    def __init__(self, cr, uid, name, context):
        super(report_orchid_asset, self).__init__(cr, uid, name, context=context)

        self.localcontext.update({
            'time': time,
            'get_asset': self._get_asset,
            'get_asset_by_category':self._get_asset_by_category,
            'get_category_by_id':self._get_category_by_id,
            'get_history_lines':self._get_history_lines,
            'get_depreciation_amt':self._get_depreciation_amt,
            'get_acc_depreciation_amt':self._get_acc_depreciation_amt,
        })

    def _get_asset(self,val):
        asset_obj = self.pool['account.asset.asset']
        if val.get('category_ids'):
            asset_ids = asset_obj.search(self.cr, self.uid, [('category_id','in',val.get('category_ids'))])
        else:
            asset_ids = asset_obj.search(self.cr, self.uid, [])
        return asset_obj.browse(self.cr,self.uid,asset_ids)

    def _get_asset_by_category(self,category_id):
        asset_obj = self.pool['account.asset.asset']
        asset_ids = asset_obj.search(self.cr, self.uid, [('category_id','=',category_id)])
        return asset_obj.browse(self.cr,self.uid,asset_ids)

    def _get_category_by_id(self,category_id):
        if category_id:
            return self.pool['account.asset.category'].browse(self.cr, self.uid,category_id).name
        return {}

    def _get_history_lines(self,val,asset):
        move_ids = []
        if val.get('period_ids'):
            acc_move_pool = self.pool['account.move.line']
            move_ids = acc_move_pool.search(self.cr, self.uid,[('period_id','in',val.get('period_ids')),('asset_id','=',asset.id)])
        else:
            return asset.account_move_line_ids
        return self.pool['account.move.line'].browse(self.cr,self.uid,move_ids)


    def _get_depreciation_amt(self,val,asset):
        move_ids = []
        res =0.0
        if val.get('period_ids'):
            acc_move_pool = self.pool['account.move.line']
            move_ids = acc_move_pool.search(self.cr, self.uid,[('period_id','in',val.get('period_ids')),('asset_id','=',asset.id)])
            data = acc_move_pool.read(self.cr,self.uid,move_ids,['debit','credit'])
            res = data and (sum([val.get('debit') for val in data]) - sum([val.get('credit') for val in data])) or 0.0
        return res

    def _get_acc_depreciation_amt(self,val,asset):
        move_ids = []
        res = 0.0
        acc_move_pool = self.pool['account.move.line']

        if val.get('accum_periods'):
            accu_move_ids = acc_move_pool.search(self.cr, self.uid,[('period_id','in',val.get('accum_periods')),('asset_id','=',asset.id)]) or []
            accu_data = acc_move_pool.read(self.cr,self.uid,accu_move_ids,['debit','credit'])
            res = accu_data and (sum([val.get('debit') for val in accu_data]) - sum([val.get('credit') for val in accu_data])) or 0.0

        return res

class report_asset_statement(osv.AbstractModel):
    _name = 'report.orchid_asset.report_asset_statement'
    _inherit = 'report.abstract_report'
    _template = 'orchid_asset.report_asset_statement'
    _wrapped_report_class = report_orchid_asset

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

