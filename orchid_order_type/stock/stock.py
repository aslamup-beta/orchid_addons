# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import SUPERUSER_ID, api
from openerp.exceptions import Warning
class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    _columns ={
               'od_order_type_id':fields.many2one('od.order.type','Order Type')
               }

class procurement_group(osv.osv):
    _inherit = 'procurement.group'
    _columns = {
        'od_order_type_id': fields.many2one('od.order.type','Type'),
        'od_analytic_id':fields.many2one('account.analytic.account','Analytic Account'),
        'od_cost_sheet_id': fields.many2one('od.cost.sheet','Cost Sheet'),
        'od_cost_centre_id':fields.many2one('od.cost.centre','Cost Center'),
        'od_branch_id':fields.many2one('od.cost.branch','Branch'),
        'od_division_id':fields.many2one('od.cost.division','Division'),
    }


class stock_picking(osv.osv):
    _inherit = "stock.picking"
    
    
    def __get_invoice_state(self, cr, uid, ids, name, arg, context=None):
        result = {} 
        for pick in self.browse(cr, uid, ids, context=context):
            no_invoice = pick.od_order_type_id and pick.od_order_type_id.sample
            result[pick.id] = 'none'
            for move in pick.move_lines:
                if move.invoice_state == 'invoiced':
                    result[pick.id] = 'invoiced'
                elif move.invoice_state == '2binvoiced':
                    result[pick.id] = '2binvoiced'
                    break
            if no_invoice:
                result[pick.id] = 'none'
            
        return result
    def onchange_order_type(self,cr,uid,ids,order_type,context=None):
        res ={}
        if order_type:
            order_pool = self.poo.get('od.order.type')
            order_obj = order_pool.browse(cr,uid,order_type)
            stock_picking_id = order_obj.stock_picking_id and order_obj.stock_picking_id.id
            if stock_picking_id:
                res['value'] = {'stock_picking_id':stock_picking_id}
        return res
    def __get_picking_move(self, cr, uid, ids, context={}):
        res = []
        for move in self.pool.get('stock.move').browse(cr, uid, ids, context=context):
            if move.picking_id:
                res.append(move.picking_id.id)
        return res

    def _set_inv_state(self, cr, uid, picking_id, name, value, arg, context=None):
        pick = self.browse(cr, uid, picking_id, context=context)
        moves = [x.id for x in pick.move_lines]
        move_obj= self.pool.get("stock.move")
        move_obj.write(cr, uid, moves, {'invoice_state': value}, context=context)
    
    _columns = {
        'od_order_type_id': fields.many2one('od.order.type','Type',readonly=True),
        'od_analytic_id':fields.many2one('account.analytic.account','Analytic Account'),
        'od_cost_sheet_id': fields.many2one('od.cost.sheet','Cost Sheet'),
        'od_cost_centre_id':fields.many2one('od.cost.centre','Cost Center'),
        'od_branch_id':fields.many2one('od.cost.branch','Branch'),
        'od_division_id':fields.many2one('od.cost.division','Division'),
        
        'invoice_state': fields.function(__get_invoice_state, type='selection', selection=[
            ("invoiced", "Invoiced"),
            ("2binvoiced", "To Be Invoiced"),
            ("none", "Not Applicable")
          ], string="Invoice Control", required=True,
        fnct_inv = _set_inv_state,
        store={
            'stock.picking': (lambda self, cr, uid, ids, c={}: ids, ['state'], 10),
            'stock.move': (__get_picking_move, ['picking_id', 'invoice_state'], 10),
        },)
                
    }
   
    
    
    def action_invoice_create(self, cr, uid, ids, journal_id=False,
            group=False, type='out_invoice', context=None):
        res = super(stock_picking,self).action_invoice_create(cr, uid, ids, journal_id, group, type, context=context)

        od_type_ids = list(set([p.od_order_type_id for p in self.browse(cr,uid,ids)]))
        od_order_type = len(od_type_ids) == 1 and od_type_ids[0] and od_type_ids[0]
        cost_sheet_ids = list(set([p.od_cost_sheet_id for p in self.browse(cr,uid,ids)]))
        cost_centre_ids = list(set([p.od_cost_centre_id for p in self.browse(cr,uid,ids)]))
        branch_ids = list(set([p.od_branch_id for p in self.browse(cr,uid,ids)]))
        division_ids = list(set([p.od_division_id for p in self.browse(cr,uid,ids)]))
        cost_sheet_id = cost_sheet_ids and cost_sheet_ids[0] and cost_sheet_ids[0].id
        cost_centre_id = cost_centre_ids and cost_centre_ids[0] and cost_centre_ids[0].id
        branch_id = branch_ids and branch_ids[0] and branch_ids[0].id
        division_id = division_ids and division_ids[0] and division_ids[0].id
        vals = {'od_cost_sheet_id':cost_sheet_id,'od_cost_centre_id':cost_centre_id,
                'od_branch_id':branch_id,'od_division_id':division_id}
        if not (branch_id and cost_centre_id):
            raise Warning("Branch and Cost Center Need to Fill")
        if od_order_type:
            vals.update({
                'od_order_type_id':od_order_type and od_order_type.id,
                'od_inter_exp_acc_id': od_order_type and od_order_type.expense_acc_id and od_order_type.expense_acc_id.id,
                'od_inter_inc_acc_id': od_order_type and od_order_type.income_acc_id and od_order_type.income_acc_id.id
            })
        self.pool.get('account.invoice').write(cr, uid, res,vals, context=context)

        return res

class stock_move(osv.osv):
    _inherit = "stock.move"

    _columns = {
        'od_order_type_id': fields.many2one('od.order.type','Type',readonly=True)
    }
    


    @api.cr_uid_ids_context
    def _picking_assign(self, cr, uid, move_ids, procurement_group, location_from, location_to, context=None):
        """Assign a picking on the given move_ids, which is a list of move supposed to share the same procurement_group, location_from and location_to
        (and company). Those attributes are also given as parameters.
        """
        pick_obj = self.pool.get("stock.picking")
        picks = pick_obj.search(cr, uid, [
                ('group_id', '=', procurement_group),
                ('location_id', '=', location_from),
                ('location_dest_id', '=', location_to),
                ('state', 'in', ['draft', 'confirmed', 'waiting'])], context=context)
        update_vals={}
        if picks:
            pick = picks[0]
            update_vals={'picking_id':pick}
        else:
            move = self.browse(cr, uid, move_ids, context=context)[0]
            od_order_type_id = move.group_id and move.group_id.od_order_type_id and move.group_id.od_order_type_id.id
            analytic_id = move.group_id and move.group_id.od_analytic_id and move.group_id.od_analytic_id.id
            values = {
                'origin': move.origin,
                'company_id': move.company_id and move.company_id.id or False,
                'move_type': move.group_id and move.group_id.move_type or 'direct',
                'partner_id': move.partner_id.id or False,
                'picking_type_id': move.picking_type_id and move.picking_type_id.id or False,
            }
            if od_order_type_id:
                values['od_order_type_id'] = od_order_type_id
                values['od_analytic_id'] = analytic_id
            pick = pick_obj.create(cr, uid, values, context=context)
            update_vals={'picking_id':pick}
            if od_order_type_id:
                update_vals['od_order_type_id'] = od_order_type_id
              
#        return self.write(cr, uid, move_ids, {'picking_id': pick}, context=context)
        return self.write(cr, uid, move_ids, update_vals, context=context)

class stock_quant(osv.osv):
    _inherit = "stock.quant"
    def _get_accounting_data_for_valuation(self, cr, uid, move, context=None):
        journal_id, acc_src, acc_dest, acc_valuation = super(stock_quant,self)._get_accounting_data_for_valuation(cr, uid, move, context=context)
        order_type_id = move.picking_id and move.picking_id.od_order_type_id and move.picking_id.od_order_type_id.id
        if order_type_id:
            order_type = self.pool.get('od.order.type').browse(cr,uid,order_type_id,context=context)
            stock_journal_id = order_type.stock_journal_id and order_type.stock_journal_id.id
            stock_input = order_type.stock_input_account_id and order_type.stock_input_account_id.id
            stock_output = order_type.stock_output_account_id and order_type.stock_output_account_id.id
            stock_valuation = order_type.stock_valuation_account_id and order_type.stock_valuation_account_id.id
            if stock_journal_id:
                journal_id = stock_journal_id
            if stock_input:
                acc_src = stock_input
            if stock_output:
                acc_dest = stock_output
            if stock_valuation:
                acc_valuation = stock_valuation
        return journal_id, acc_src, acc_dest, acc_valuation
    
#     def _prepare_account_move_line(self, cr, uid, move, qty, cost, credit_account_id, debit_account_id, context=None):
#         """
#         Generate the account.move.line values to post to track the stock valuation difference due to the
#         processing of the given quant.
#         """
#         print "prepare account move line orchid order type"
#         result = []
#         picking_id = move.picking_id and move.picking_id.id
#         pick_obj = self.pool.get('stock.picking')
#         res = super(stock_quant,self)._prepare_account_move_line(cr, uid, move, qty, cost, credit_account_id, debit_account_id, context=context)
#         if picking_id:
#             analytic_id = pick_obj.browse(cr,uid,picking_id).od_analytic_id and pick_obj.browse(cr,uid,picking_id).od_analytic_id.id
#             if analytic_id:
#                 for x in res:
#                     data = x[2]
#                     data.update({'analytic_account_id':analytic_id})
#                     result.append((0,0,data))
#                 return result
#         return res
#     
    
    
