# -*- encoding: utf-8 -*-
from openerp.osv import fields, orm
import openerp.addons.decimal_precision as dp
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP
import pytz
from openerp import SUPERUSER_ID, workflow
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP
from openerp.tools.float_utils import float_compare



class PurchaseOrderLine(orm.Model):
    _inherit = "purchase.order.line"


    def onchange_product_qty(self, cr, uid, ids, od_gross, product_qty, discount, context=None):
        res = {}
        unit_price =0.0
        if discount >0:
            total_price = od_gross * product_qty
            discount_value = total_price * (discount/100)
            total_price_with_discount = total_price - discount_value
            if product_qty != 0:
                unit_price = total_price_with_discount / product_qty
            res = {'value': {'price_unit': unit_price or 0.0}}
        else:
            res = {'value': {'price_unit': od_gross or 0.0}}
            

        return res

    def onchange_discount(self, cr, uid, ids, od_gross, product_qty, discount, context=None):
        res = {}
        unit_price = 0.0
        if discount >0:
            total_price = od_gross * product_qty
            discount_value = total_price * (discount/100)
            total_price_with_discount = total_price - discount_value
            if product_qty !=0: 
                unit_price = total_price_with_discount / product_qty
            res = {'value': {'price_unit': unit_price or 0.0}}
        else:
            res = {'value': {'price_unit': od_gross or 0.0}}
            

        return res
    def onchange_od_gross(self, cr, uid, ids, od_gross, product_qty, discount, context=None):
        res = {}
        unit_price =0.0
        if discount >0:
            total_price = od_gross * product_qty
            discount_value = total_price * (discount/100)
            total_price_with_discount = total_price - discount_value
            if product_qty !=0:
                unit_price = total_price_with_discount / product_qty
            res = {'value': {'price_unit': unit_price or 0.0}}
        else:
            res = {'value': {'price_unit': od_gross or 0.0}}
            

        return res
         


    def onchange_product_id(self, cr, uid, ids, pricelist_id, product_id, qty, uom_id,
            partner_id, date_order=False, fiscal_position_id=False, date_planned=False,
            name=False, price_unit=False, state='draft', context=None):
        """
        onchange handler of product_id.
        """
        if context is None:
            context = {}

        res = {'value': {'price_unit': price_unit or 0.0, 'name': name or '', 'product_uom' : uom_id or False}}
        if not product_id:
            return res

        product_product = self.pool.get('product.product')
        product_uom = self.pool.get('product.uom')
        res_partner = self.pool.get('res.partner')
        product_pricelist = self.pool.get('product.pricelist')
        account_fiscal_position = self.pool.get('account.fiscal.position')
        account_tax = self.pool.get('account.tax')

        # - check for the presence of partner_id and pricelist_id
        #if not partner_id:
        #    raise osv.except_osv(_('No Partner!'), _('Select a partner in purchase order to choose a product.'))
        #if not pricelist_id:
        #    raise osv.except_osv(_('No Pricelist !'), _('Select a price list in the purchase order form before choosing a product.'))

        # - determine name and notes based on product in partner lang.
        context_partner = context.copy()
        if partner_id:
            lang = res_partner.browse(cr, uid, partner_id).lang
            context_partner.update( {'lang': lang, 'partner_id': partner_id} )
        product = product_product.browse(cr, uid, product_id, context=context_partner)
        #call name_get() with partner in the context to eventually match name and description in the seller_ids field
#        dummy, name = product_product.name_get(cr, uid, product_id, context=context_partner)[0]
        name = product.name
        if product.description_purchase:
            name = product.description_purchase
        res['value'].update({'name': name})

        # - set a domain on product_uom
        res['domain'] = {'product_uom': [('category_id','=',product.uom_id.category_id.id)]}

        # - check that uom and product uom belong to the same category
        product_uom_po_id = product.uom_po_id.id
        if not uom_id:
            uom_id = product_uom_po_id

        if product.uom_id.category_id.id != product_uom.browse(cr, uid, uom_id, context=context).category_id.id:
            if context.get('purchase_uom_check') and self._check_product_uom_group(cr, uid, context=context):
                res['warning'] = {'title': _('Warning!'), 'message': _('Selected Unit of Measure does not belong to the same category as the product Unit of Measure.')}
            uom_id = product_uom_po_id

        res['value'].update({'product_uom': uom_id})

        # - determine product_qty and date_planned based on seller info
        if not date_order:
            date_order = fields.datetime.now()


        supplierinfo = False
        precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Product Unit of Measure')
        for supplier in product.seller_ids:
            if partner_id and (supplier.name.id == partner_id):
                supplierinfo = supplier
                if supplierinfo.product_uom.id != uom_id:
                    res['warning'] = {'title': _('Warning!'), 'message': _('The selected supplier only sells this product by %s') % supplierinfo.product_uom.name }
                min_qty = product_uom._compute_qty(cr, uid, supplierinfo.product_uom.id, supplierinfo.min_qty, to_uom_id=uom_id)
                if float_compare(min_qty , qty, precision_digits=precision) == 1: # If the supplier quantity is greater than entered from user, set minimal.
                    if qty:
                        res['warning'] = {'title': _('Warning!'), 'message': _('The selected supplier has a minimal quantity set to %s %s, you should not purchase less.') % (supplierinfo.min_qty, supplierinfo.product_uom.name)}
                    qty = min_qty
        dt = self._get_date_planned(cr, uid, supplierinfo, date_order, context=context).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        qty = qty or 1.0
        res['value'].update({'date_planned': date_planned or dt})
        if qty:
            res['value'].update({'product_qty': qty})

        price = price_unit
        if price_unit is False or price_unit is None:
            # - determine price_unit and taxes_id
            if pricelist_id:
                date_order_str = datetime.strptime(date_order, DEFAULT_SERVER_DATETIME_FORMAT).strftime(DEFAULT_SERVER_DATE_FORMAT)
                price = product_pricelist.price_get(cr, uid, [pricelist_id],
                        product.id, qty or 1.0, partner_id or False, {'uom': uom_id, 'date': date_order_str})[pricelist_id]
            else:
                price = product.standard_price

        taxes = account_tax.browse(cr, uid, map(lambda x: x.id, product.supplier_taxes_id))
        fpos = fiscal_position_id and account_fiscal_position.browse(cr, uid, fiscal_position_id, context=context) or False
        taxes_ids = account_fiscal_position.map_tax(cr, uid, fpos, taxes)
        res['value'].update({'price_unit': price, 'taxes_id': taxes_ids,'od_gross':price})

        return res


 
    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        res = super(PurchaseOrderLine,self)._amount_line(cr, uid, ids, field_name, arg, context=context)
        cur_obj = self.pool['res.currency']
        tax_obj = self.pool['account.tax']
        for line in self.browse(cr, uid, ids, context=context):
            discount = line.discount or 0.0
            new_price_unit = line.price_unit + line.additional_cost
            taxes = tax_obj.compute_all(cr, uid, line.taxes_id, line.price_unit,
                                        line.product_qty, line.product_id,
                                        line.order_id.partner_id)
            currency = line.order_id.pricelist_id.currency_id
            res[line.id] = cur_obj.round(cr, uid, currency, taxes['total'])
        return res




    _columns = {
        'discount': fields.float('Disc(%)',
                                 digits_compute=dp.get_precision('Discount')),
        'price_subtotal': fields.function(
            _amount_line, string='Subtotal',
            digits_compute=dp.get_precision('Account')),
        'od_gross':fields.float('Unit Price',required="1",digits_compute= dp.get_precision('Product Price'))
    }

    _defaults = {
        'discount': 0.0,
    }

    _sql_constraints = [
        ('discount_limit', 'CHECK (discount <= 100.0)',
         'Discount must be lower than 100%.'),
    ]


class PurchaseOrder(orm.Model):
    _inherit = "purchase.order"

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        
        res = super(PurchaseOrder,self)._amount_all(cr, uid, ids, field_name, arg, context=None)
        
        
        cur_obj = self.pool['res.currency']
        tax_obj = self.pool['account.tax']
        for order in self.browse(cr, uid, ids, context=context):
            val = {}
            amount_taxed = amount_untaxed = 0.0
            currency = order.pricelist_id.currency_id
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                discount = line.discount or 0.0
                new_price_unit = line.price_unit * (1 - discount / 100.0)
                for c in tax_obj.compute_all(cr, uid, line.taxes_id,
                                             line.price_subtotal,1,
                                             line.product_id.id,
                                             order.partner_id)['taxes']:
                    amount_taxed += c.get('amount', 0.0)
            discount = order.od_discount
            val['amount_tax'] = cur_obj.round(cr, uid, currency, amount_taxed)
            val['amount_untaxed'] = cur_obj.round(cr, uid, currency,
                                                  amount_untaxed)
            val['amount_total'] = (val['amount_untaxed'] + val['amount_tax']) - discount
            res[order.id] = val
        return res
    
    
#     def od_recalculate_tax(self):
#         self._amount_all(cr, uid, ids, 'field_name', arg, context)
    
    def _prepare_inv_line(self, cr, uid, account_id, order_line,
                          context=None):
        result = super(PurchaseOrder, self)._prepare_inv_line(cr, uid,
                                                              account_id,
                                                              order_line,
                                                              context)
        result['discount'] = order_line.discount or 0.0
        return result

    def _get_order(self, cr, uid, ids, context=None):
        result = set()
        po_line_obj = self.pool['purchase.order.line']
        for line in po_line_obj.browse(cr, uid, ids, context=context):
            result.add(line.order_id.id)
        return list(result)
    
   

    _columns = {
        'amount_untaxed': fields.function(
            _amount_all, digits_compute=dp.get_precision('Account'),
            string='Untaxed Amount',
            store={
                'purchase.order.line': (_get_order, None, 10),
            }, multi="sums", help="The amount without tax"),
        'amount_tax': fields.function(
            _amount_all, digits_compute=dp.get_precision('Account'),
            string='Taxes',
            store={
                'purchase.order.line': (_get_order, None, 10),
            }, multi="sums", help="The tax amount"),
        
        'amount_total': fields.function(
            _amount_all, digits_compute=dp.get_precision('Account'),
            string='Total',
            store={
                'purchase.order.line': (_get_order, None, 10),
                'purchase.order': (lambda self, cr, uid, ids, c=None: ids, [], 10)

            }, multi="sums", help="The total amount"),
        'od_discount':fields.float('Discount',readonly=True,states={'draft':[('readonly',False)]}),
    }


class StockPicking(orm.Model):
    _inherit = 'stock.picking'

    def _invoice_line_hook(self, cr, uid, move_line, invoice_line_id):
        if move_line.purchase_line_id:
            line = {'discount': move_line.purchase_line_id.discount}
            self.pool['account.invoice.line'].write(cr, uid,
                                                    [invoice_line_id], line)
        return super(StockPicking, self)._invoice_line_hook(cr, uid,
                                                            move_line,
                                                            invoice_line_id)
