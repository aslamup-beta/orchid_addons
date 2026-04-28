from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.exceptions import Warning
from datetime import datetime
class stock_quant(osv.osv):
    _inherit = "stock.quant"
    
    def _prepare_account_move_line(self, cr, uid, move, qty, cost, credit_account_id, debit_account_id, context=None):
        """
        Generate the account.move.line values to post to track the stock valuation difference due to the
        processing of the given quant.
        """
        
        print "prepare account move line orchid landed cost"
        move_lines = super(stock_quant,self)._prepare_account_move_line(cr, uid, move, qty, cost, credit_account_id, debit_account_id, context=context)
        min_date = move.picking_id and move.picking_id.min_date or move.date
        if context is None:
            context = {}
        currency_obj = self.pool.get('res.currency')
        if context.get('force_valuation_amount'):
            valuation_amount = context.get('force_valuation_amount')
        else:
            if move.product_id.cost_method == 'average':
                valuation_amount = move.location_id.usage != 'internal' and move.location_dest_id.usage == 'internal' and cost or move.product_id.standard_price
            else:
                valuation_amount = cost if move.product_id.cost_method == 'real' else move.product_id.standard_price
        #the standard_price of the product may be in another decimal precision, or not compatible with the coinage of
        #the company currency... so we need to use round() before creating the accounting entries.
        valuation_amount = currency_obj.round(cr, uid, move.company_id.currency_id, valuation_amount * qty)
        analytic_account_id = False
        analytic_level = move.picking_id and move.picking_id.od_analytic_id and move.picking_id.od_analytic_id.od_analytic_level 
        print "analytic level", analytic_level
        if analytic_level != 'level0':
            analytic_account_id = move.picking_id and move.picking_id.od_analytic_id and move.picking_id.od_analytic_id.id or False
        
        
        # if not analytic_account_id:
        #     analytic_account_id =move.so_line_id and move.so_line_id.od_analytic_acc_id and move.so_line_id.od_analytic_acc_id.id or False
        
        if not analytic_account_id:
            analytic_account_id =move.purchase_line_id and move.purchase_line_id.so_line_id and move.purchase_line_id.so_line_id.od_analytic_acc_id and move.purchase_line_id.so_line_id.od_analytic_acc_id.id or False

        if not analytic_account_id:
            analytic_account_id =move.so_line_id and move.so_line_id.od_analytic_acc_id and move.so_line_id.od_analytic_acc_id.id or False 
        
        if not analytic_account_id:
            raise Warning("Kindly Link Analytic Account on the Picking")



        
        partner_id = (move.picking_id and move.picking_id.partner_id and self.pool.get('res.partner')._find_accounting_partner(move.picking_id.partner_id).id) or False
        od_cost_centre_id = move.picking_id and move.picking_id.od_cost_centre_id and move.picking_id.od_cost_centre_id.id or False
        od_branch_id = move.picking_id and move.picking_id.od_branch_id and move.picking_id.od_branch_id.id or False
        od_division_id = move.picking_id and move.picking_id.od_division_id and move.picking_id.od_division_id.id or False
        #pick_date = move.picking_id and move.picking_id.date or False
        #Below warning added by Aslam as per muthanna request
        dateTimeObj = datetime.now()
        current_date = dateTimeObj.strftime("%Y-%m-%d %H:%M:%S")
        sch_date = min_date[:10]
        current_date = current_date[:10]
        if sch_date < current_date :
            raise Warning("Scheduled Date Should be greater than or equal to Today date  !!")
        
        if not od_cost_centre_id:
            od_cost_centre_id = (move.picking_id and move.picking_id.od_analytic_id and move.picking_id.od_analytic_id.od_cost_centre_id  and move.picking_id.od_analytic_id.od_cost_centre_id.id) or (move.picking_id and move.picking_id.od_analytic_id and move.picking_id.od_analytic_id.cost_centre_id  and move.picking_id.od_analytic_id.cost_centre_id.id) 
        if not od_branch_id:
            od_branch_id = (move.picking_id and move.picking_id.od_analytic_id and move.picking_id.od_analytic_id.od_branch_id  and move.picking_id.od_analytic_id.od_branch_id.id) or (move.picking_id and move.picking_id.od_analytic_id and move.picking_id.od_analytic_id.branch_id  and move.picking_id.od_analytic_id.branch_id.id) 
        if not od_division_id:
            od_division_id = (move.picking_id and move.picking_id.od_analytic_id and move.picking_id.od_analytic_id.od_division_id  and move.picking_id.od_analytic_id.od_division_id.id) or (move.picking_id and move.picking_id.od_analytic_id and move.picking_id.od_analytic_id.division_id  and move.picking_id.od_analytic_id.division_id.id) 
        if not (od_cost_centre_id and od_branch_id):
            raise Warning("Need to Fill Cost Center and Branch")
        debit_line_vals = {
                    'name': move.name,
                    'product_id': move.product_id.id,
                    'quantity': qty,
                    'product_uom_id': move.product_id.uom_id.id,
                    'ref': move.picking_id and move.picking_id.name or False,
                    'date': min_date,
                    'partner_id': partner_id,
                    'debit': valuation_amount > 0 and valuation_amount or 0,
                    'credit': valuation_amount < 0 and -valuation_amount or 0,
                    'account_id': debit_account_id,
                    'od_cost_centre_id':od_cost_centre_id,
                    'od_branch_id':od_branch_id,
                    'od_division_id':od_division_id,
                    'analytic_account_id':analytic_account_id,
        }
        credit_line_vals = {
                    'name': move.name,
                    'product_id': move.product_id.id,
                    'quantity': qty,
                    'product_uom_id': move.product_id.uom_id.id,
                    'ref': move.picking_id and move.picking_id.name or False,
                    'date': min_date,
                    'partner_id': partner_id,
                    'credit': valuation_amount > 0 and valuation_amount or 0,
                    'debit': valuation_amount < 0 and -valuation_amount or 0,
                    'account_id': credit_account_id,
                    'od_cost_centre_id':od_cost_centre_id,
                    'od_branch_id':od_branch_id,
                    'od_division_id':od_division_id,
                    'analytic_account_id':analytic_account_id,
        }
        return [(0, 0, debit_line_vals), (0, 0, credit_line_vals)]
    
    def _create_account_move_line(self, cr, uid, quants, move, credit_account_id, debit_account_id, journal_id, context=None):
            #group quants by cost        
            min_date = move.picking_id and move.picking_id.min_date or move.date
            
            quant_cost_qty = {}
            for quant in quants:
                if quant_cost_qty.get(quant.cost):
                    quant_cost_qty[quant.cost] += quant.qty
                else:
                    quant_cost_qty[quant.cost] = quant.qty
            move_obj = self.pool.get('account.move')
            for cost, qty in quant_cost_qty.items():
                move_lines = self._prepare_account_move_line(cr, uid, move, qty, cost, credit_account_id, debit_account_id, context=context)
#                 period_id = context.get('force_period', self.pool.get('account.period').find(cr, uid, date, context=context)[0])
                period_id =  self.pool.get('account.period').find(cr, uid, min_date, context=context)
                move_obj.create(cr, uid, {'journal_id': journal_id,
                                          'line_id': move_lines,
                                          'period_id': period_id and period_id[0],
                                          'date': min_date,
                                          'ref': move.picking_id.name}, context=context)
