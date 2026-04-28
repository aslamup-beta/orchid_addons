from openerp import models, fields, api
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp.osv import osv, fields as fields2,orm
# class purchase_order(models.Model):
#     _inherit = "purchase.order"
#     landed_cost_line_ids =fields.One2many('od.landed.cost.line','purchase_order_id','Landed Costs')
#
class product_product(orm.Model):
    _inherit = "product.product"

    def _choose_exp_account_from(self, cr, uid, product, fiscal_position=False,
                                 context=None):
        """ Method to compute the expense account to chose based on product and
        fiscal position.

        Used in invoice creation and on_change of landed costs.
        Taken from method : _choose_account_from_po_line of purchase.py in
        purchase module.

        """
        fiscal_obj = self.pool.get('account.fiscal.position')
        property_obj = self.pool.get('ir.property')
        if product:
            acc_id = product.property_account_expense.id
            if not acc_id:
                acc_id = product.categ_id.property_account_expense_categ.id
            if not acc_id:
                raise orm.except_orm(
                    _('Error!'),
                    _('Define expense account for this company: "%s" (id:%d).')
                    % (product.name, product.id,))
        else:
            acc_id = property_obj.get(cr, uid,
                                      'property_account_expense_categ',
                                      'product.category').id
        return fiscal_obj.map_account(cr, uid, fiscal_position, acc_id)

class purchase_order(osv.osv):
    _inherit = "purchase.order"

    # def copy(self, cr, uid, id, default=None, context=None):
    #     default = dict(context or {})
    #     purchase = self.browse(cr, uid, id, context=context)
    #     po_line = self.pool.get('purchase.order.line')
    #     product_obj = self.pool.get('product.product')
    #     pricelist_id = purchase.pricelist_id and purchase.pricelist_id.id
    #     partner_id = purchase.partner_id and purchase.partner_id.id
    #     date_order = purchase.date_order
    #     date_planned = purchase.minimum_planned_date
    #     fiscal_position= purchase.fiscal_position.id
    #     print "defaultttttttttttttttttttttttttt",default
    #     res = self.onchange_partner_id(cr,uid,id,partner_id,context=context)
    #     print "ressssssssssssssssssssssssssssssssssssssssssssssssssssss",res
    #     for line in purchase.order_line:
    #         price =  po_line.onchange_product_id(cr, uid,line.id, pricelist_id, line.product_id.id, line.product_qty, line.product_uom.id,
    #         partner_id, date_order=date_order, fiscal_position_id=fiscal_position, date_planned=date_planned,
    #         name=False, price_unit=False, state='draft', context=context)
    #         price_unit = price['value']['price_unit']
    #         od_gross = price['value']['od_gross']
    #         line['price_unit'] = price_unit
    #         line['od_gross'] = od_gross
    #     return super(purchase_order, self).copy(cr, uid, id, default, context=context)

    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('purchase.order.line').browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()
    def _get_landcost(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('od.landed.cost.line').browse(cr, uid, ids, context=context):
            result[line.purchase_order_id.id] = True
        return result.keys()

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        res = super(purchase_order,self)._amount_all(cr, uid, ids, field_name, arg, context=None)
        cur_obj=self.pool.get('res.currency')
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id]['od_amount_additional_exp'] = 0.0
            res[order.id]['od_amount_sub'] = 0.0
            val3= 0.0
            val2 =  0.0
            cur = order.pricelist_id.currency_id
            for line in order.order_line:
                val2 += line.final_cost
                val3 += line.additional_cost
            res[order.id]['od_amount_additional_exp'] = cur_obj.round(cr, uid, cur, val3)
            res[order.id]['od_amount_sub']=cur_obj.round(cr, uid, cur, val2)
        return res
#     def _amount_od_subtotal(self,cr,uid,ids,field_name,arg,context=None):
#         res = {}
#         cur_obj=self.pool.get('res.currency')
#         for order in self.browse(cr, uid, ids, context=context):
#             res[order.id]= {'od_amount_additional_exp':0.0,
#                    'od_amount_sub':0.0
#                    }
#             val3= 0.0
#             val2 =  0.0
#             cur = order.pricelist_id.currency_id
#             for line in order.order_line:
#                 val2 += line.final_cost
#                 val3 += line.additional_cost
#             res[order.id]['od_amount_additional_exp'] = cur_obj.round(cr, uid, cur, val3)
#             res[order.id]['od_amount_sub']=cur_obj.round(cr, uid, cur, val2)
#         return res
    _columns = {


        'landed_cost_line_ids' :fields2.one2many('od.landed.cost.line','purchase_order_id','Landed Costs',states={'draft': [('readonly', False)]},readonly=True),
                 'od_amount_sub': fields2.function(
            _amount_all, digits_compute=dp.get_precision('Account'),
            string='Subtotal',
            store={
                'purchase.order.line': (_get_order,None, 10),
                 'od.landed.cost.line':(_get_landcost,None,10)
            }, multi="sums", help="The amount without tax"),
        'amount_tax': fields2.function(
            _amount_all, digits_compute=dp.get_precision('Account'),
            string='Taxes',
            store={
                'purchase.order.line': (_get_order, None, 10),
                 'od.landed.cost.line':(_get_landcost,None,10)
            }, multi="sums", help="The tax amount"),
        'amount_total': fields2.function(
            _amount_all, digits_compute=dp.get_precision('Account'),
            string='Total',
            store={
                'purchase.order.line': (_get_order, None, 10),
                 'od.landed.cost.line':(_get_landcost,None,10)
            }, multi="sums", help="The total amount"),
                'od_amount_additional_exp': fields2.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Addl.Exp',
             multi="sums", help="The total amount"),
              'amount_untaxed': fields2.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Untaxed Amount',
            store={
                'purchase.order.line': (_get_order, None, 10),
                 'od.landed.cost.line':(_get_landcost,None,10),
                
            }, multi="sums", help="The amount without tax", track_visibility='always'),
                }


#
#     def _prepare_order_line_move(self, cr, uid, order, order_line, picking_id,
#                                   group_id, context=None):
#         """ Here, the technical price_unit field will store the purchase
#         price + landed cost. The original purchase price is stored in
#         price_unit_net new field to keep record of it.
#
#         """
#         result = []
#         res = super(purchase_order,self)._prepare_order_line_move(
#             cr, uid, order, order_line, picking_id, group_id, context=context)[0]
#         cur_obj = self.pool.get('res.currency')
#         cmp_cur_id = order.company_id.currency_id.id
#         po_cur_id = order.pricelist_id.currency_id.id
#         try:
# #            amount=order_line.final_cost
# #            amt = cur_obj.compute(cr, uid,
# #                                         po_cur_id,
# #                                         cmp_cur_id,
# #                                         amount,
# #                                         context=context)
# #            res['price_unit'] = amt
#
#             price_unit = order_line.price_subtotal / res['product_uom_qty'] or 1
#             amt = cur_obj.compute(cr, uid,
#                                          po_cur_id,
#                                          cmp_cur_id,
#                                          price_unit,
#                                          context=context)
#             res['price_unit'] = amt
#         except ZeroDivisionError:
#             pass
#         result.append(res)
#         return result
#
#     def _prepare_landed_cost_inv_line(self, cr, uid, account_id, inv_id,
#                                       landed_cost, context=None):
#         """ Collects require data from landed cost position that is used to
#         create invoice line for that particular position.
#
#         If it comes from a PO line and Distribution type is per unit
#         the quantity of the invoice is the PO line quantity
#
#         :param account_id: Expense account.
#         :param inv_id: Related invoice.
#         :param browse_record landed_cost: Landed cost position browse record
#         :return: Value for fields of invoice lines.
#         :rtype: dict
#
#         """
#         qty = 1.0
# #         if (landed_cost.purchase_order_line_id and
# #                 landed_cost.distribution_type_id.landed_cost_type == 'per_unit'):
# #         qty = landed_cost.purchase_order_line_id.product_qty
#         line_tax_ids = [x.id for x in landed_cost.name.supplier_taxes_id]
#         return {
#             'name': landed_cost.name.name,
#             'account_id': account_id,
#             'invoice_id' : inv_id,
#             'price_unit': landed_cost.amount or 0.0,
#             'quantity': qty,
#             'product_id': landed_cost.name.id or False,
#             'invoice_line_tax_id': [(6, 0, line_tax_ids)],
#         }
#
#     def _prepare_landed_cost_inv(self, cr, uid, landed_cost, context=None):
#         """ Collects require data from landed cost position that is used to
#         create invoice for that particular position.
#
#         Note that _landed can come from a line or at whole PO level.
#
#         :param browse_record landed_cost: Landed cost position browse record
#         :return: Value for fields of invoice.
#         :rtype: dict
#
#         """
#         po = (landed_cost.purchase_order_id or
#               landed_cost.purchase_order_line_id.order_id)
#         currency_id = landed_cost.purchase_order_id.pricelist_id.currency_id.id
#         fiscal_position = po.fiscal_position or False
#         journal_obj = self.pool.get('account.journal')
#         journal_ids = journal_obj.search(
#             cr, uid,
#             [('type', '=', 'purchase'),
#              ('company_id', '=', po.company_id.id)],
#             limit=1)
#         if not journal_ids:
#             raise orm.except_orm(
#                 _('Error!'),
#                 _('Define purchase journal for this company: "%s" (id: %d).')
#                 % (po.company_id.name, po.company_id.id))
#         return {
#             'currency_id': currency_id,
#             'partner_id': landed_cost.partner_id.id,
#             'account_id': landed_cost.partner_id.property_account_payable.id,
#             'type': 'in_invoice',
#             'origin': po.name,
#             'fiscal_position':  fiscal_position,
#             'company_id': po.company_id.id,
#             'check_total':landed_cost.amount,
#             'journal_id': len(journal_ids) and journal_ids[0] or False,
#         }
#
#     def _generate_invoice_from_landed_cost(self, cr, uid, landed_cost,
#                                            context=None):
#         """ Generate an invoice from order landed costs (means generic
#         costs to a whole PO) or from a line landed costs.
#
#         """
#         invoice_obj = self.pool.get('account.invoice')
#         invoice_line_obj = self.pool.get('account.invoice.line')
#         prod_obj = self.pool.get('product.product')
#         po = (landed_cost.purchase_order_id or
#               landed_cost.purchase_order_line_id.order_id)
#         vals_inv = self._prepare_landed_cost_inv(cr, uid, landed_cost,
#                                                  context=context)
#         inv_id = invoice_obj.create(cr, uid, vals_inv, context=context)
#         fiscal_position = (po.fiscal_position or False)
#         exp_account_id = self.pool.get('product.product')._choose_exp_account_from(
#             cr, uid,
#             landed_cost.name,
#             fiscal_position=fiscal_position,
#             context=context
#         )
# #         exp_account_id =3489
#         vals_line = self._prepare_landed_cost_inv_line(
#             cr, uid, exp_account_id, inv_id,
#             landed_cost, context=context
#         )
#         inv_line_id = invoice_line_obj.create(cr, uid, vals_line,
#                                               context=context)
#         return inv_id
#
#
#     def wkf_approve_order(self, cr, uid, ids, context=None):
#         """ On PO approval, generate all invoices for all landed cost position.
#
#         Remember that only landed cost position with the checkbox
#         generate_invoice ticked are generated.
#
#         """
#         res = super(purchase_order,self).wkf_approve_order(cr, uid, ids,
#                                                            context=context)
#         for order in self.browse(cr, uid, ids, context=context):
#             invoice_ids = []
#             for order_cost in order.landed_cost_line_ids:
#
#                 inv_id = self._generate_invoice_from_landed_cost(
#                         cr, uid, order_cost, context=context)
#                 invoice_ids.append(inv_id)
# #             for po_line in order.order_line:
# #                 for line_cost in po_line.landed_cost_line_ids:
# #                     inv_id = self._generate_invoice_from_landed_cost(
# #                         cr, uid, line_cost, context=context)
# #                     invoice_ids.append(inv_id)
#             # Link this new invoice to related purchase order
#             # 4 in that list is "Add" mode in a many2many used here because
#             # the call to super() already add the main invoice
#             if invoice_ids:
#                 commands = [(4, invoice_id) for invoice_id in invoice_ids]
#                 order.write({'invoice_ids': commands}, context=context)
#         return res

    def invoice_open(self, cr, uid, ids, context=None):
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        acc_inv_obj= self.pool.get('account.invoice')
        name= self.browse(cr, uid, ids,context)[0].name or ''
        result = mod_obj.get_object_reference(cr, uid, 'account', 'action_invoice_tree2')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        inv_ids = []
        #inv_ids = acc_inv_obj.search(cr, uid,[('origin','=',name)])
        for po in self.browse(cr, uid, ids, context=context):
            inv_ids+= [invoice.id for invoice in po.invoice_ids]

        if not inv_ids:
            raise osv.except_osv(_('Error!'), _('Please create Invoices.'))
         #choose the view_mode accordingly
        if len(inv_ids)>1:
            result['domain'] = "[('id','in',["+','.join(map(str, inv_ids))+"])]"
        else:
            res = mod_obj.get_object_reference(cr, uid, 'account', 'invoice_supplier_form')
            result['views'] = [(res and res[1] or False, 'form')]
            result['res_id'] = inv_ids and inv_ids[0] or False
        return result



class od_landed_cost_line(models.Model):
    _name = "od.landed.cost.line"
    purchase_order_id = fields.Many2one('purchase.order',string="Purchase Order")
    name = fields.Many2one('product.product','Landed Cost Name',domain=[('landed_cost_ok', '!=', False)],required=True)
    partner_id = fields.Many2one('res.partner',string="Partner")
    od_pdt_type_id = fields.Many2one('od.product.type',string='Type')
    amount = fields.Float(string="Amount",required=True)
    distribution_type =fields.Selection([('by_quantity','Distributed By Quantity'),
                                         ('by_price','Distributed By Price'),
                                         ('by_weight','Distributed By Weight')],string='Distribution Type',required=True,default='by_quantity')



class purchase_order_line(osv.osv):
    _inherit = 'purchase.order.line'
    def action_confirm(self, cr, uid, ids, context=None):
        for data in self.browse(cr,uid,ids):
            addl_cost = data.additional_cost
            price_unit = data.price_unit
            qty = data.product_qty
            new_price = price_unit + addl_cost/qty
            self.write(cr, uid, [data.id], {'state': 'confirmed','price_unit':new_price}, context=context)
        return True
    def _od_get_landed_cost_line(self, cr, uid, ids, name, args, context=None):
        result ={}
        qty_s =  self.od_total_qty(cr,uid,ids,name,args,context=context)
        landed_cost_line = self.pool.get('od.landed.cost.line')
        all_tot_qty = sum(qty_s.values())
        distributed_amount = 0.0
        price_s = self.od_total_price(cr,uid,ids,name,args,context=context)
        all_tot_price = sum(price_s.values())
        weight_s = self.od_total_weight(cr,uid,ids,name,args,context=context)
        all_tot_weight = sum( weight_s.values())
        for line in self.browse(cr, uid, ids, context=context):
            od_pdt_type_id = line.product_id and line.product_id.od_pdt_type_id and line.product_id.od_pdt_type_id.id
            #for by qty
            x=[{data.od_pdt_type_id.id:data.id} for data in line.order_id.landed_cost_line_ids if data.od_pdt_type_id.id == od_pdt_type_id and data.distribution_type=='by_quantity']
            blank_type = [data.id for data in line.order_id.landed_cost_line_ids if data.od_pdt_type_id.id == False and data.distribution_type=='by_quantity']
            al_base_tot = 0.0
            al_base_dis = 0.0
            if blank_type:

                for  y in blank_type:
                    cost_obj =  landed_cost_line.browse(cr,uid,y)
                    al_base_tot += cost_obj.amount
            if all_tot_qty:
                al_base_dis = (al_base_tot /all_tot_qty *line.product_qty)
                print al_base_dis
            if x:
                cost_obj = landed_cost_line.browse(cr,uid,x[0].get(od_pdt_type_id))
                base_amount = cost_obj.amount
                qty_total = qty_s.get(str(od_pdt_type_id))
                distributed_amount = ((base_amount/qty_total * line.product_qty) + al_base_dis)
            else:
                distributed_amount = al_base_dis
                #for by cost
            x_price=[{data.od_pdt_type_id.id:data.id} for data in line.order_id.landed_cost_line_ids if data.od_pdt_type_id.id == od_pdt_type_id and data.distribution_type=='by_price']
            blank_type_price = [data.id for data in line.order_id.landed_cost_line_ids if data.od_pdt_type_id.id == False and data.distribution_type=='by_price']
            al_base_tot_price = 0.0
            al_base_dis_price = 0.0

            if blank_type_price:
                for  y in blank_type_price:
                    cost_obj =  landed_cost_line.browse(cr,uid,y)
                    al_base_tot_price += cost_obj.amount

            if all_tot_price:
                    al_base_dis_price = (al_base_tot_price  /(all_tot_price) ) * line.od_gross * line.product_qty

            if x_price:
                cost_obj = landed_cost_line.browse(cr,uid,x_price[0].get(od_pdt_type_id))
                base_amount = cost_obj.amount
                price_total = price_s.get(str(od_pdt_type_id))
                if price_total * line.od_gross == 0:
                    raise osv.except_osv(_('Error!'), _('Price Should Not be Zero!'))
                distributed_amount += (((base_amount  /(price_total)) * line.od_gross * line.product_qty )  + al_base_dis_price)
            else:
                distributed_amount += al_base_dis_price
#for by weight
            x_weight=[{data.od_pdt_type_id.id:data.id} for data in line.order_id.landed_cost_line_ids if data.od_pdt_type_id.id == od_pdt_type_id and data.distribution_type=='by_weight']
            blank_type_weight = [data.id for data in line.order_id.landed_cost_line_ids if data.od_pdt_type_id.id == False and data.distribution_type=='by_weight']
            al_base_tot_weight = 0.0
            al_base_dis_weight = 0.0

            if blank_type_weight:
                for  y in blank_type_weight:
                    cost_obj =  landed_cost_line.browse(cr,uid,y)
                    al_base_tot_weight += cost_obj.amount

            if all_tot_weight:
                    al_base_dis_weight = (al_base_tot_weight /all_tot_weight) * line.product_qty *line.product_id.weight_net

            if x_weight:

                cost_obj = landed_cost_line.browse(cr,uid,x_weight[0].get(od_pdt_type_id))
                base_amount = cost_obj.amount
                weight_total = weight_s.get(str(od_pdt_type_id))
                if weight_total * line.product_id.weight_net  * line.product_qty == 0:
                    raise osv.except_osv(_('Error!'), _('Product weight Not be Zero!'))
                distributed_amount += ((base_amount/weight_total * line.product_id.weight_net * line.product_qty)  + al_base_dis_weight)
            else:
                distributed_amount += al_base_dis_weight
            result[line.id] = {
                            'additional_cost' :distributed_amount
                            }
        return result

    def od_total_qty(self,cr,uid,ids,name,args,context=None):
        qty_sum = []
        result ={}
        for line in self.browse(cr,uid,ids,context=context):
            qty ={}
            od_pdt_type_id = line.product_id and line.product_id.od_pdt_type_id and line.product_id.od_pdt_type_id.id
            if od_pdt_type_id:
                qty[str(od_pdt_type_id)] =line.product_qty
                qty_sum.append(qty)
            else:
                qty['all'] =line.product_qty
                qty_sum.append(qty)


        if qty_sum:
            for y in qty_sum:
                result[y.keys()[0]]= y.keys()[0] in result and result[y.keys()[0]] + y.values()[0] or  y.values()[0]
        return result

    def od_total_price(self,cr,uid,ids,name,args,context=None):
        qty_sum = []
        result ={}
        for line in self.browse(cr,uid,ids,context=context):
            qty ={}
            od_pdt_type_id = line.product_id and line.product_id.od_pdt_type_id and line.product_id.od_pdt_type_id.id
            if od_pdt_type_id:
                qty[str(od_pdt_type_id)] =line.od_gross * line.product_qty
                qty_sum.append(qty)
            else:
                qty['all'] =line.od_gross * line.product_qty
                qty_sum.append(qty)

        if qty_sum:
            for y in qty_sum:
                result[y.keys()[0]]= y.keys()[0] in result and result[y.keys()[0]] + y.values()[0] or  y.values()[0]
        return result

    def od_total_weight(self,cr,uid,ids,name,args,context=None):
        qty_sum = []
        result ={}
        for line in self.browse(cr,uid,ids,context=context):
            qty ={}
            od_pdt_type_id = line.product_id and line.product_id.od_pdt_type_id and line.product_id.od_pdt_type_id.id
            if od_pdt_type_id:
                qty[str(od_pdt_type_id)] =line.product_id.weight_net * line.product_qty
                qty_sum.append(qty)
            else:
                qty['all'] =line.product_id.weight_net * line.product_qty
                qty_sum.append(qty)

        if qty_sum:
            for y in qty_sum:
                result[y.keys()[0]]= y.keys()[0] in result and result[y.keys()[0]] + y.values()[0] or  y.values()[0]
        return result

    def _od_get_total(self,cr,uid,ids,name,args,context=None):
        result = {}
        tot = 0.0
        for line in self.browse(cr,uid,ids):
            tot  = line.price_subtotal - line.additional_cost
            result[line.id] = tot
            if line.state == 'draft':
                tot  = line.price_unit * line.product_qty
                result[line.id] = tot

        return result
    def _amount_line(self, cr, uid, ids, prop, arg, context=None):
        result=super(purchase_order_line,self)._amount_line(cr, uid, ids, prop, arg, context=context)
        res = {}
        cur_obj=self.pool.get('res.currency')
        tax_obj = self.pool.get('account.tax')
        for line in self.browse(cr, uid, ids, context=context):
            taxes = tax_obj.compute_all(cr, uid, line.taxes_id, line.price_unit, line.product_qty, line.product_id, line.order_id.partner_id)
            cur = line.order_id.pricelist_id.currency_id
            res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'])
            if line.state == 'draft':
                taxes = tax_obj.compute_all(cr, uid, line.taxes_id, line.price_unit+(line.additional_cost/line.product_qty), line.product_qty, line.product_id, line.order_id.partner_id)
                cur = line.order_id.pricelist_id.currency_id
                res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'])

        return res
    _columns = {
                'additional_cost' :fields2.function(_od_get_landed_cost_line,type='float',string='Addl.Exp', multi="_compute_amounts"),
                'final_cost':fields2.function(_od_get_total,type="float",string="Final"),
                'price_subtotal': fields2.function(_amount_line, string='Subtotal', digits_compute= dp.get_precision('Account')),
                }
