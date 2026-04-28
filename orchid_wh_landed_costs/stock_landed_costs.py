# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.tools import float_compare, float_round
from openerp.tools.translate import _
from operator import itemgetter
from pprint import pprint
class stock_landed_cost(osv.osv):
    _inherit = 'stock.landed.cost'
    _order = "name desc"
    def unlink(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.state not in ['draft', 'cancel']:
                raise osv.except_osv(_('Invalid Action!'), _('Cannot delete a landed cost doc which is in state \'%s\'.') %(rec.state,))
        return super(stock_landed_cost, self).unlink(cr, uid, ids, context=context)
    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'stock.landed.cost') or '/'
        return super(stock_landed_cost, self).create(cr, uid, vals, context=context)
#inherited to correct the rounding- float to int for rounding checking
    def _check_sum(self, cr, uid, landed_cost, context=None):
        """
        Will check if each cost line its valuation lines sum to the correct amount
        and if the overall total amount is correct also
        """
        costcor = {}
        tot = 0
        for valuation_line in landed_cost.valuation_adjustment_lines:
            if costcor.get(valuation_line.cost_line_id):
                costcor[valuation_line.cost_line_id] += valuation_line.additional_landed_cost
            else:
                costcor[valuation_line.cost_line_id] = valuation_line.additional_landed_cost
            tot += valuation_line.additional_landed_cost

        prec = self.pool['decimal.precision'].precision_get(cr, uid, 'Account')
        # float_compare returns 0 for equal amounts
        res = not bool(float_compare(tot, landed_cost.amount_total, precision_digits=prec))
        res = (round(tot) == round(landed_cost.amount_total))
#        print "###### check total ", res,"FFF", tot,"%%%%",landed_cost.amount_total
#        for costl in costcor.keys():
#            if float_compare(costcor[costl], costl.price_unit, precision_digits=prec):
#                res = False
#        print "###### check line ", res,"FFF", costcor[costl],"%%%%",costl.price_unit
        return res
#the button_validate overrided for product master avg price updation only
    
    def od_get_analytic_from_pick(self,cr, uid, ids, context=None):
        picking_ids = self.browse(cr,uid,ids).picking_ids
        analytic_acc_id =False
        for pick in picking_ids:
            analytic_acc_id = pick.od_analytic_id and pick.od_analytic_id.id or False 
        return analytic_acc_id
    
    
    def button_validate(self, cr, uid, ids, context=None):
        quant_obj = self.pool.get('stock.quant')
        #object defining
        prod_obj = self.pool.get('product.template')
        # analytic_account_id = self.od_get_analytic_from_pick(cr, uid, ids, context)
        for cost in self.browse(cr, uid, ids, context=context):
            if not cost.valuation_adjustment_lines or not self._check_sum(cr, uid, cost, context=context):
                raise osv.except_osv(_('Error!'), _('You cannot validate a landed cost which has no valid valuation lines.'))
#            move_id = self._create_account_move(cr, uid, cost, context=context)
            quant_dict = {}
            product_ids_in_valuation_adjustment_lines = []
            account_move_lines = []
            for line in cost.valuation_adjustment_lines:
                analytic_account_id = line._od_get_analytic_account()
                total_new_each_product_avg_cost = 0
                total_cost_from_product_template =0
                if not line.move_id:
                    continue
                if line.product_id.id not in product_ids_in_valuation_adjustment_lines:
                    # we are taking template_id for calling do_change_standard_price(cr, uid, [product_temp_id], value, context)
                    product_ids_in_valuation_adjustment_lines.append(line.product_id.id)
                    product_temp_id = line.product_id.product_tmpl_id and line.product_id.product_tmpl_id.id
                    cr.execute("select sum(additional_landed_cost) from stock_valuation_adjustment_lines where cost_id = %s and product_id = %s GROUP BY product_id",(cost.id,line.product_id.id,))
                    res = cr.fetchall()
                    total_cost_from_product_template = total_cost_from_product_template + (line.product_id.product_tmpl_id.standard_price * line.product_id.product_tmpl_id.qty_available)
                    if line.product_id.product_tmpl_id.qty_available ==0:
                        raise osv.except_osv(_('Error!'), _('on hand qty is zero'))
                    total_new_each_product_avg_cost =  (total_cost_from_product_template + res[0][0]) / line.product_id.product_tmpl_id.qty_available
                    line.product_id.write({'standard_price':total_new_each_product_avg_cost})
                if line.quantity:
                    per_unit = line.final_cost / line.quantity
                    diff = per_unit - line.former_cost_per_unit
                    quants = [quant for quant in line.move_id.quant_ids]
                    for quant in quants:
                        if quant.id not in quant_dict:
                            quant_dict[quant.id] = quant.cost + diff

                        else:
                            quant_dict[quant.id] += diff
                    for key, value in quant_dict.items():
                        quant_obj.write(cr, uid, key, {'cost': value}, context=context)
                    qty_out = 0
                    for quant in line.move_id.quant_ids:
                        if quant.location_id.usage != 'internal':
                            qty_out += quant.qty
                    account_move_lines = account_move_lines + self._create_accounting_entries(cr, uid, line, qty_out, context=context)
#Modified for beta on March 07
            b_mv_cr_line = []
            for b_mv_cost_line in cost.cost_lines:
                n_val = {
                    'partner_id': b_mv_cost_line.od_partner_id and b_mv_cost_line.od_partner_id.id or False,
                    'product_id': b_mv_cost_line.product_id and b_mv_cost_line.product_id.id or False,
                    'name':b_mv_cost_line.name or b_mv_cost_line.product_id and b_mv_cost_line.product_id.name or '/',
                    'account_id': b_mv_cost_line.account_id and b_mv_cost_line.account_id.id or False,
                    'credit': b_mv_cost_line.price_unit,
                    'debit':0.0,
                    'analytic_account_id': analytic_account_id,
                }
                b_mv_cr_line.append([0,0,n_val])

            pprint(account_move_lines)
            for mvline in account_move_lines:
                if mvline[2].has_key('debit') or 'already out' in  mvline[2].get('name',''):
                    l = mvline[2]
                    if not l.get('credit',False):
                        l['credit'] = 0
                    if not l.get('debit',False):
                        l['debit'] = 0
                    l['partner_id']=False
                    b_mv_cr_line.append([0,0,l])
#Modified for beta end


#Modified by Lithin on Dec 19 @ASN
            move_vals = {
                'journal_id': cost.account_journal_id.id,
                'period_id': self.pool.get('account.period').find(cr, uid, cost.date, context=context)[0],
                'date': cost.date,
                'ref': cost.name,
                'line_id':b_mv_cr_line
            }
            pprint(move_vals)
            move_id = self.pool.get('account.move').create(cr, uid, move_vals, context=context)
            self.write(cr, uid, cost.id, {'state': 'done', 'account_move_id': move_id}, context=context)
        return True
    def get_valuation_lines(self, cr, uid, ids, picking_ids=None, context=None):
        picking_obj = self.pool.get('stock.picking')
        lines = []
        if not picking_ids:
            return lines
        for picking in picking_obj.browse(cr, uid, picking_ids):
            for move in picking.move_lines:
                #it doesn't make sense to make a landed cost for a product that isn't set as being valuated in real time at real cost
                # commented by riyas according to the task http://orchiderp.com/web?#id=1539&view_type=form&model=project.task&action=212

#                if move.product_id.valuation != 'real_time' or move.product_id.cost_method != 'real':
#                    continue
                total_cost = 0.0
                total_qty = move.product_qty
                weight = move.product_id and move.product_id.weight * move.product_qty
                volume = move.product_id and move.product_id.volume * move.product_qty
                pdt_dic={}
                for quant in move.quant_ids:
                    if quant.product_id not in pdt_dic:
                        pdt_dic[quant.product_id]=quant.id
                        total_cost += quant.cost
                vals = dict(product_id=move.product_id.id, move_id=move.id, quantity=move.product_uom_qty, former_cost=total_cost * total_qty, weight=weight, volume=volume)
                lines.append(vals)
        if not lines:
            raise osv.except_osv(_('Error!'), _('The selected picking does not contain any move that would be impacted by landed costs. Landed costs are only possible for products configured in real time valuation with real price costing method. Please make sure it is the case, or you selected the correct picking'))
        return lines
#
#     def get_valuation_adjustment_limited_lines(self, cr, uid, ids, field_name,arg,context=None):
#         limited_ids = []
#         adjust_line_obj = self.pool.get('od.stock.valuation.adjustment.limited.lines')
# #        old_adj_ids = adjust_line_obj.search(cr, uid,[('cost_id','in',ids)])
#         old_adj_ids = adjust_line_obj.search(cr, uid,[])
#         adjust_line_obj.unlink(cr, uid,old_adj_ids)
#         for landed_cost in self.browse(cr, uid, ids, context=context):
#             dict_line = {}
#             dict_pdt_additional_cost = {}
#             dict_pdt_qty={}
#             dict_pdt_formar_cost = {}
#             cost_list = []
#             #Sum of grouped qty
#             qry = "select product_id,sum(quantity) from ( \
# select move_id,product_id,quantity from stock_valuation_adjustment_lines  where cost_id=%s group by move_id,product_id,quantity) as foo \
# group by product_id"%(landed_cost.id)
#             cr.execute(qry)
#             dict_pdt_qty  = dict(cr.fetchall()) or {}
#             #Sum of grouped additional cost
#             qry_cost = "select product_id as product_id,sum(additional_landed_cost) as cost from stock_valuation_adjustment_lines  \
# where cost_id=%s group by product_id"%(landed_cost.id)
#             cr.execute(qry_cost)
#             dict_pdt_additional_cost = dict(cr.fetchall()) or {}
#             cost_list.append(dict_pdt_additional_cost)
#             #Sum of grouped formal cost
#             qry_former_cost = "select product_id,sum(former_cost) as cost from ( select move_id,product_id,former_cost from stock_valuation_adjustment_lines where cost_id=%s group by move_id,product_id,former_cost) as foo group by product_id"%(landed_cost.id)
#             cr.execute(qry_former_cost)
#             dict_pdt_formar_cost = dict(cr.fetchall()) or {}
#             cost_list.append(dict_pdt_formar_cost)
#             lc_cost = {k:sum(map(itemgetter(k), cost_list)) for k in cost_list[0]}
#             for product_id in lc_cost.keys():
#                     cost = lc_cost[product_id]
#                     qty = dict_pdt_qty[product_id]
#                     cost_per_unit = cost/(qty or 1)
#                     vals = {
#                         'product_id': product_id,
#                         'quantity': qty,
#                         'cost': cost,
#                         'cost_per_unit': cost_per_unit
#                     }
#                     limited_ids.append(adjust_line_obj.create(cr, uid,vals))
#         return dict([(id,limited_ids) for id in ids])

    def get_valuation_adjustment_limited_lines(self, cr, uid, ids, field_name,arg,context=None):
        limited_ids = []
        adjust_line_obj = self.pool.get('od.stock.valuation.adjustment.limited.lines')
        old_adj_ids = adjust_line_obj.search(cr, uid,[])
        adjust_line_obj.unlink(cr, uid,old_adj_ids)
        for landed_cost in self.browse(cr, uid, ids, context=context):
            line_dict = {}
            for line in landed_cost.valuation_adjustment_lines:
                if not line.move_id:
                    continue
                if line.quantity:
                    per_unit = line.final_cost / line.quantity
                    diff = per_unit - line.former_cost_per_unit
                    if line.product_id.id not in line_dict:
                        line_dict[line.product_id.id] = {'cost_per_unit':line.move_id.price_unit + diff,
                                                         'product_id':line.product_id.id,
                                                         'qty':line.quantity}
                    else:
                        line_dict[line.product_id.id]['cost_per_unit'] += diff
            for dict_val in line_dict.values():
                    cost_per_unit = dict_val['cost_per_unit']
                    product_id = dict_val['product_id']
                    qty = dict_val['qty']
                    cost = qty * cost_per_unit
                    vals = {
                        'product_id': product_id,
                        'quantity': qty,
                        'cost': cost,
                        'cost_per_unit': cost_per_unit
                    }
                    limited_ids.append(adjust_line_obj.create(cr, uid,vals))
        return dict([(id,limited_ids) for id in ids])
    def compute_landed_cost(self, cr, uid, ids, context=None):
        line_obj = self.pool.get('stock.valuation.adjustment.lines')
        unlink_ids = line_obj.search(cr, uid, [('cost_id', 'in', ids)], context=context)
        line_obj.unlink(cr, uid, unlink_ids, context=context)
        towrite_dict = {}
        for cost in self.browse(cr, uid, ids, context=None):
            if not cost.picking_ids:
                continue
            picking_ids = [p.id for p in cost.picking_ids]
            total_qty = 0.0
            total_cost = 0.0
            total_weight = 0.0
            total_volume = 0.0
            total_line = 0.0
            vals = self.get_valuation_lines(cr, uid, [cost.id], picking_ids=picking_ids, context=context)
            for v in vals:
                for line in cost.cost_lines:
                    v.update({'cost_id': cost.id, 'cost_line_id': line.id,'od_partner_id':line.od_partner_id and line.od_partner_id.id})
                    self.pool.get('stock.valuation.adjustment.lines').create(cr, uid, v, context=context)
                total_qty += v.get('quantity', 0.0)
                total_cost += v.get('former_cost', 0.0)
                total_weight += v.get('weight', 0.0)
                total_volume += v.get('volume', 0.0)
                total_line += 1

            for line in cost.cost_lines:
                for valuation in cost.valuation_adjustment_lines:
                    value = 0.0
                    if valuation.cost_line_id and valuation.cost_line_id.id == line.id:
                        if line.split_method == 'by_quantity' and total_qty:
                            per_unit = (line.price_unit / total_qty)
                            value = valuation.quantity * per_unit
                        elif line.split_method == 'by_weight' and total_weight:
                            per_unit = (line.price_unit / total_weight)
                            value = valuation.weight * per_unit
                        elif line.split_method == 'by_volume' and total_volume:
                            per_unit = (line.price_unit / total_volume)
                            value = valuation.volume * per_unit
                        elif line.split_method == 'equal':
                            value = (line.price_unit / total_line)
                        elif line.split_method == 'by_current_cost_price' and total_cost:
                            per_unit = (line.price_unit / total_cost)
                            value = valuation.former_cost * per_unit
                        else:
                            value = (line.price_unit / total_line)

                        if valuation.id not in towrite_dict:
                            towrite_dict[valuation.id] = value
                        else:
                            towrite_dict[valuation.id] += value
        if towrite_dict:
            for key, value in towrite_dict.items():
                line_obj.write(cr, uid, key, {'additional_landed_cost': value}, context=context)
        return True
    def od_re_disribute(self, cr, uid, ids, context=None):
        if not context:
            context = dict()
        line_obj = self.pool.get('stock.valuation.adjustment.lines')
        towrite_dict = {}
        for cost in self.browse(cr, uid, ids, context=None):
            if not cost.picking_ids:
                continue
            picking_ids = [p.id for p in cost.picking_ids]
            total_qty = 0.0
            total_cost = 0.0
            total_weight = 0.0
            total_volume = 0.0
            total_line = 0.0
#            vals = self.get_valuation_lines(cr, uid, [cost.id], picking_ids=picking_ids, context=context)
#            for v in vals:
#                for line in cost.cost_lines:
#                    v.update({'cost_id': cost.id, 'cost_line_id': line.id,'od_partner_id':line.od_partner_id and line.od_partner_id.id})
##                    self.pool.get('stock.valuation.adjustment.lines').create(cr, uid, v, context=context)
#                total_qty += v.get('quantity', 0.0)
#                total_cost += v.get('former_cost', 0.0)
#                total_weight += v.get('weight', 0.0)
#                total_volume += v.get('volume', 0.0)

#            for line in
            for line in cost.cost_lines:
#                line_qty=
                disc_qty_cost_line={}
                disc_cost_cost_line={}
                disc_weight_cost_line={}
                disc_volume_cost_line={}
                disc_total_cost_line={}
                if not cost.valuation_adjustment_lines:
                    raise osv.except_osv(_('warning!'), _('no lines for redistribution'))
                for valuation in cost.valuation_adjustment_lines:
                    disc_qty_cost_line[valuation.cost_line_id]= valuation.cost_line_id in disc_qty_cost_line and disc_qty_cost_line[valuation.cost_line_id] + valuation.quantity or valuation.quantity
                    disc_cost_cost_line[valuation.cost_line_id]= valuation.cost_line_id in disc_cost_cost_line and disc_cost_cost_line[valuation.cost_line_id] + valuation.former_cost or valuation.former_cost
                    disc_weight_cost_line[valuation.cost_line_id]= valuation.cost_line_id in disc_weight_cost_line and disc_weight_cost_line[valuation.cost_line_id] + valuation.weight or valuation.weight
                    disc_volume_cost_line[valuation.cost_line_id]= valuation.cost_line_id in disc_volume_cost_line and disc_volume_cost_line[valuation.cost_line_id] + valuation.volume or valuation.volume
                    disc_total_cost_line[valuation.cost_line_id]= valuation.cost_line_id in disc_total_cost_line and disc_total_cost_line[valuation.cost_line_id] + 1 or 1
            for line in cost.cost_lines:
                for valuation in cost.valuation_adjustment_lines:
                    value = 0.0
                    total_qty = disc_qty_cost_line[valuation.cost_line_id]
                    total_cost = disc_cost_cost_line[valuation.cost_line_id]
                    total_weight = disc_weight_cost_line[valuation.cost_line_id]
                    total_volume = disc_volume_cost_line[valuation.cost_line_id]
                    total_line = disc_total_cost_line[valuation.cost_line_id]
                    if valuation.cost_line_id and valuation.cost_line_id.id == line.id:
                        if line.split_method == 'by_quantity' and total_qty:
                            per_unit = (line.price_unit / total_qty)
                            value = valuation.quantity * per_unit
                        elif line.split_method == 'by_weight' and total_weight:
                            per_unit = (line.price_unit / total_weight)
                            value = valuation.weight * per_unit
                        elif line.split_method == 'by_volume' and total_volume:
                            per_unit = (line.price_unit / total_volume)
                            value = valuation.volume * per_unit
                        elif line.split_method == 'equal':
                            value = (line.price_unit / total_line)
                        elif line.split_method == 'by_current_cost_price' and total_cost:
                            per_unit = (line.price_unit / total_cost)
                            value = valuation.former_cost * per_unit
                        else:
                            value = (line.price_unit / total_line)

                        if valuation.id not in towrite_dict:
                            towrite_dict[valuation.id] = value
                        else:
                            towrite_dict[valuation.id] += value
        if towrite_dict:
            for key, value in towrite_dict.items():
                line_obj.write(cr, uid, key, {'additional_landed_cost': value}, context=context)
        return True
    def _create_accounting_entries(self, cr, uid, line, qty_out, context=None):
        product_obj = self.pool.get('product.template')
        cost_product = line.cost_line_id and line.cost_line_id.product_id
        if not cost_product:
            return False
        accounts = product_obj.get_product_accounts(cr, uid, line.product_id.product_tmpl_id.id, context=context)
        debit_account_id = accounts['property_stock_valuation_account_id']
        already_out_account_id = accounts['stock_account_output']
        credit_account_id = line.cost_line_id.account_id.id or cost_product.property_account_expense.id or cost_product.categ_id.property_account_expense_categ.id
        if not credit_account_id:
            raise osv.except_osv(_('Error!'), _('Please configure Stock Expense Account for product: %s.') % (cost_product.name))
        return self._create_account_move_line(cr, uid, line, credit_account_id, debit_account_id, qty_out, already_out_account_id, context=context)
#        return self._create_account_move_line(cr, uid, line, move_id, credit_account_id, debit_account_id, qty_out, already_out_account_id, context=context)
#####################################
# Lithin Comments THis is latest ## def _create_account_move_line is the orginal one fine tuned to get some accurate values #######

###################################
    def _create_account_move_line(self, cr, uid, line,  credit_account_id, debit_account_id, qty_out, already_out_account_id, context=None):
        """
        Generate the account.move.line values to track the landed cost.
        Afterwards, for the goods that are already out of stock, we should create the out moves
        """
        aml_obj = self.pool.get('account.move.line')
        base_line = {
            'name': line.name,
            'product_id': line.product_id.id,
            'quantity': line.quantity,
        }
        partner_id = line.od_partner_id and line.od_partner_id.id
        analytic_account_id= line._od_get_analytic_account()
        print "analytic account on landed cost",analytic_account_id
        debit_line = dict(base_line, account_id=debit_account_id,analytic_account_id=analytic_account_id)
#        credit_line = dict(base_line, account_id=credit_account_id,partner_id = partner_id)
        credit_line = dict(base_line, account_id=credit_account_id,analytic_account_id=analytic_account_id)
        move_line_data = []
        diff = float(line.additional_landed_cost)
        if diff > 0:
            debit_line['debit'] = diff
            credit_line['credit'] = diff
        else:
            # negative cost, reverse the entry
            debit_line['credit'] = -diff
            credit_line['debit'] = -diff
        if diff != 0:
            move_line_data.append([0,0,debit_line])
            move_line_data.append([0,0,credit_line])
#
        # Create account move lines for quants already out of stock
        if qty_out > 0 and diff != 0:
            debit_line = dict(debit_line,
                              name=(line.name + ": " + str(qty_out) + _(' already out')),
                              quantity=qty_out,
                              account_id=already_out_account_id,analytic_account_id=analytic_account_id)
            credit_line = dict(credit_line,
                              name=(line.name + ": " + str(qty_out) + _(' already out')),
                              quantity=qty_out,
                              account_id=debit_account_id,analytic_account_id=analytic_account_id)
            diff = diff * qty_out / line.quantity
            if diff > 0:
                debit_line['debit'] = diff
                credit_line['credit'] = diff
            else:
                # negative cost, reverse the entry
                debit_line['credit'] = -diff
                credit_line['debit'] = -diff
            move_line_data.append([0,0,debit_line])
            move_line_data.append([0,0,credit_line])
        return move_line_data
    def _get_shipment_no(self, cr, uid, ids, field, arg, context=None):
        res = {}
        for data in self.browse(cr, uid, ids, context=context):
            for picking_id in data.picking_ids:
                pick_id = picking_id.id
                shipment_number = self.pool.get('stock.picking').browse(cr, uid, pick_id, context=context).od_shipment_no or False
                if shipment_number:
                    res[data.id] = shipment_number or ''
                else:
                    res[data.id] = ''
        return res
    def _get_partner_id(self,cr,uid,ids,field,arg,context=None):
        res = {}
        for data in self.browse(cr, uid, ids, context=context):
            for picking_id in data.picking_ids:
                pick_id = picking_id.id
                partner_id = self.pool.get('stock.picking').browse(cr, uid, pick_id, context=context).partner_id.id
                res[data.id] = partner_id or False
        return res
    

#    def _get_od_final_cost(self,cr,uid,ids,field,arg,context=None):
#        res = {}
#        final_cost = 0
#        for data in self.browse(cr, uid, ids, context=context):
#            print "FFFFFFF",data
#
#            for obj in data.od_valuation_adjustment_limited_lines:
#                print "::::::",obj.cost_per_unit
#                final_cost = final_cost + obj.cost_per_unit
#            res[data.id] = final_cost
#        return res

    def od_final_cost_generate(self, cr, uid, ids, context=None):
        for data in self.browse(cr, uid, ids, context=context):
            final_cost = 0
            for obj in data.od_valuation_adjustment_limited_lines:
                final_cost = final_cost + obj.cost
            self.pool.get('stock.landed.cost').write(cr,uid,[data.id],{'od_final_cost':final_cost},context=context)
        return True
    def _get_od_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id
    _columns = {
        'od_valuation_adjustment_limited_lines':fields.function(get_valuation_adjustment_limited_lines,type='one2many',relation="od.stock.valuation.adjustment.limited.lines"),
        'od_airway_bill_no':fields.char('Airway Bill No'),
        'od_shipment_number':fields.function(_get_shipment_no,type='char',string='Shipment'),
        'od_partner_id': fields.function(_get_partner_id, type='many2one', relation='res.partner', string='Partner',store=True),
        'od_final_cost':fields.float('Final Cost'),
        'od_company_id': fields.many2one('res.company','Company',required=True),
    }
    _defaults = {
        'od_final_cost' : 0,
        'name':'/',
        'od_company_id': _get_od_default_company,
    }
class stock_landed_cost_lines(osv.osv):
    _inherit = 'stock.landed.cost.lines'
    _columns = {
        'od_partner_id': fields.many2one('res.partner', 'Partner'),
    }
class stock_valuation_adjustment_lines(osv.osv):
    _inherit = 'stock.valuation.adjustment.lines'
    _columns = {
        'od_partner_id': fields.many2one('res.partner', 'Partner'),
        'weight': fields.float('Weight', digits_compute=dp.get_precision('Landed Cost Weight')),#@RM for changing Precsion
    }
    
    
    def _od_get_analytic_account(self,cr,uid,ids,context=None):
                
        data = self.browse(cr,uid,ids)
        # analytic_id = data.move_id and data.move_id.picking_id and data.move_id.picking_id.od_analytic_id and data.move_id.picking_id.od_analytic_id.id  or False
        analytic_id=data.move_id.purchase_line_id and data.move_id.purchase_line_id.so_line_id and data.move_id.purchase_line_id.so_line_id.od_analytic_acc_id and data.move_id.purchase_line_id.so_line_id.od_analytic_acc_id.id or False
        return analytic_id
    
    
    def od_get_move_cost(self,cr,uid,ids,context=None):
        data = self.browse(cr,uid,ids)
        cost = data.move_id and data.move_id.price_unit or ''
        return {

                    'view_type': 'form',
                    "view_mode": 'form',
                    'res_model': 'cost.wiz',
                    'type': 'ir.actions.act_window',
                    'context': {'cost': str(cost)},
                    'target':'new',
            }

class od_stock_valuation_adjustment_limited_lines(osv.osv):
    _name = 'od.stock.valuation.adjustment.limited.lines'
    _description = 'od.stock.valuation.adjustment.limited.lines'
    _columns = {
        'cost_id': fields.many2one('stock.landed.cost', 'Landed Cost'),
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'quantity': fields.float('Quantity', digits_compute=dp.get_precision('Product Unit of Measure'), required=True),
        'cost':fields.float('Final Cost', digits_compute=dp.get_precision('Product Price')),
        'cost_per_unit':fields.float('Cost Per Unit', digits_compute=dp.get_precision('Product Price')),
    }
class stock_picking(osv.osv):
    _inherit = "stock.picking"
    _columns = {
        'od_shipment_no': fields.char('Shipment#'),
    }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
