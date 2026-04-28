# -*- coding: utf-8 -*-
from openerp import workflow
from openerp.osv import fields, osv
class account_move_line(osv.osv):
    _inherit = "account.move.line"
#Include partner in the move
    def _query_get(self, cr, uid, obj='l', context=None):
        result = super(account_move_line, self)._query_get(cr, uid, obj=obj, context=context)
        account_obj = self.pool.get('account.account')
        if context.get('partner_ids'):
            partner_id = tuple(context['partner_ids'])
            if len(partner_id) == 1:
                result += ' AND '+obj+'.partner_id = '+str(context['partner_ids'][0])+ ' '
            else:
                result += ' AND '+obj+'.partner_id IN '+str(partner_id)+ ' '
        if context.get('analytic_account_ids'):
            analytic_account_id = tuple(context['analytic_account_ids'])
            if len(analytic_account_id) == 1:
                result += ' AND '+obj+'.analytic_account_id = '+str(context['analytic_account_ids'][0])+ ' '
            else:
                result += ' AND '+obj+'.analytic_account_id IN '+str(analytic_account_id)+ ' '

        if context.get('od_account_ids'):
            account_id = tuple(context['od_account_ids'])
            account_id = tuple(account_obj.search(cr, uid,[('id','child_of',account_id)]))
            if len(account_id) == 1:
                result += ' AND '+obj+'.account_id = '+str(context['od_account_ids'][0])+ ' '
            else:
                result += ' AND '+obj+'.account_id IN '+str(account_id)+ ' '
        
        if context.get('od_cost_centre_ids'):
            cost_centre_id = tuple(context['od_cost_centre_ids'])
            if len(cost_centre_id) == 1:
                result += ' AND '+obj+'.od_cost_centre_id = '+str(context['od_cost_centre_ids'][0])+ ' '
            else:
                result += ' AND '+obj+'.od_cost_centre_id IN '+str(cost_centre_id)+ ' '
        
        if context.get('od_branch_ids'):
            od_branch_ids = tuple(context['od_branch_ids'])
            if len(od_branch_ids) == 1:
                result += ' AND '+obj+'.od_branch_id = '+str(context['od_branch_ids'][0])+ ' '
            else:
                result += ' AND '+obj+'.od_branch_id IN '+str(od_branch_ids)+ ' '
                
        if context.get('od_division_ids'):
            od_division_ids = tuple(context['od_division_ids'])
            if len(od_division_ids) == 1:
                result += ' AND '+obj+'.od_division_id = '+str(context['od_division_ids'][0])+ ' '
            else:
                result += ' AND '+obj+'.od_division_id IN '+str(od_division_ids)+ ' '
        
        return result
