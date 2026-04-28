# -*- coding: utf-8 -*-
import openerp
from openerp import SUPERUSER_ID
from openerp import pooler, tools
from openerp.osv import fields, osv, expression
from openerp.tools.translate import _
from lxml import etree


class account_move(osv.osv):
    _inherit = 'account.move'

    def od_onchange_journal_id(self, cr, uid, ids,journal_id,context=None):
        res = {}
        if journal_id:
            journal_obj = self.pool.get('account.journal').browse(cr,uid,journal_id,context)
            ref = journal_obj.name
            return {'value':{'ref':ref}}
        return res
    
    




class account_move_line(osv.osv):
    _inherit = 'account.move.line'

#Include cost center in the move

    def _query_get(self, cr, uid, obj='l', context=None):
        result = super(account_move_line, self)._query_get(cr, uid, obj=obj, context=context)
        if context.get('od_cost_centre_ids'):
            cost_centre_id = tuple(context['od_cost_centre_ids'])
            if len(cost_centre_id) == 1:
                result += ' AND '+obj+'.od_cost_centre_id = '+str(context['od_cost_centre_ids'][0])+ ' '
            else:
                result += ' AND '+obj+'.od_cost_centre_id IN '+str(cost_centre_id)+ ' '
        import sys,inspect
        return result

    def od_onchange_account_id(self, cr, uid, ids, account_id, journal_id,context=None):
        res = {}
        journal_obj = self.pool.get('account.journal')

        od_is_asset_req = False
        od_is_product_req = False
        od_is_analytic_req = False
                
        if account_id and journal_id:
            journal = journal_obj.browse(cr, uid, journal_id,context)
            account_id_obj = self.pool.get('account.account').browse(cr,uid,account_id,context)
            if account_id_obj:
                
                od_is_asset_req = account_id_obj.od_is_asset
                od_is_product_req = account_id_obj.od_is_product
                od_is_analytic_req = account_id_obj.od_is_analytic
                od_branch_id = account_id_obj.od_branch_id and account_id_obj.od_branch_id.id or False
            return {'value':{'od_cost_centre_id':journal.od_default_cost_centre_id.id or False,'od_is_asset_req':od_is_asset_req,'od_is_product_req':od_is_product_req,'od_is_analytic_req':od_is_analytic_req, 'od_branch_id': od_branch_id}}
        return res

# (vals.get('journal_id')=='/') or
    def create(self, cr, user, vals, context=None):
        if ('od_cost_centre_id' not in vals) or (vals.get('od_cost_centre_id') == False):
            vals['od_cost_centre_id'] = False
            if ('move_id' in vals):
                acc_move_obj = self.pool.get('account.move')
                move_id = vals.get('move_id')
                if move_id:
                    move_rec = acc_move_obj.browse(cr, user, move_id,context)
                    journal_rec = move_rec.journal_id
                    vals['od_cost_centre_id'] = move_rec.journal_id and move_rec.journal_id.od_default_cost_centre_id and move_rec.journal_id.od_default_cost_centre_id.id
            if vals.get('account_id'):
                acc_obj = self.pool.get('account.account')
                acc = acc_obj.browse(cr, user, [vals.get('account_id')], context=context)
                vals['od_branch_id'] = acc.od_branch_id and acc.od_branch_id.id or False
                if acc.od_is_cc_required and not vals.get('od_cost_centre_id'):
                    raise osv.except_osv(_('Warning!'), _('Please select Cost centre for the Acc: '+acc.name+' '))
        return super(account_move_line, self).create(cr, user, vals, context)



    _columns = {
        'od_cost_centre_id': fields.many2one('od.cost.centre','Cost Centre'),
        'od_branch_id':fields.many2one('od.cost.branch','Branch'),
        'od_division_id':fields.many2one('od.cost.division','Division'),
#        'od_warehouse_id': fields.many2one('stock.warehouse','Warehouse'),
        'od_product_brand_id': fields.many2one('od.product.brand','Brand'),
        'od_is_asset_req':fields.boolean('Asset Req'),
        'od_is_product_req':fields.boolean('Product Req'),
        'od_is_analytic_req':fields.boolean('Analytic Req'),

    }





class account_journal(osv.osv):
    _inherit = 'account.journal'
    _columns = {
        'od_default_cost_centre_id': fields.many2one('od.cost.centre','Cost Centre'),
    }


class account_account(osv.osv):
    """ Inherited to Filter based on Accounts in lines"""
    _inherit = 'account.account'
    _columns = {
        'od_cost_centre_ids':fields.many2many('od.cost.centre','account_cost_centre_rel', 'account_id', 'cost_centre_id', 'Cost Centre'),
        'od_is_cc_required':fields.boolean('Required'),
        'od_branch_id' : fields.many2one('od.cost.branch','Branch'),
        'od_cost_centre_id':fields.many2one('od.cost.centre','Cost Centre')
        }
