# -*- coding: utf-8 -*-
from pprint import pprint
from openerp import models,fields,api
from openerp.exceptions import Warning
class od_tsk_gen_purchase(models.TransientModel):
    _name = "od.tsk.gen.purchase"
    _description = 'Generate Purchase Order From Task'

    def mark_po(self,task):
        """ This function for mark Material Line in task after Purchase Order Created ,
            this will tick PO Field in the line  """

        for line in task.od_material_request_line:
            if line.state == 'requested':
                line.po = True
    @api.multi
    def button_purchase_order(self):
        context = self._context
        tsk = self.env['project.task']
        active_id = context.get('task_id',False)
        task = self.env['project.task']
        task_obj = task.browse(active_id)
        purchase_id = task_obj.od_purchase_id and task_obj.od_purchase_id.id
        if not purchase_id:
            purchase_id = self.gen_purchase_order()
            self.mark_po(task_obj)
            task_obj.write({
            'od_purchase_id':purchase_id
            })

        return {
                    'res_id': purchase_id,
                    'view_type': 'form',
                    "view_mode": 'form',
                    'res_model': 'purchase.order',
                    'type': 'ir.actions.act_window',
                    'context': context
        }


    def gen_purchase_order(self):
        context = self._context
        task_id = context.get('task_id',False)

        purchase_obj = self.env['purchase.order']
        purchase_line_obj = self.env['purchase.order.line']
        warehouse_id  = self.warehouse_id and self.warehouse_id.id
        pricelist_id = self.pricelist_id and self.pricelist_id.id
        currency_id = self.pricelist_id and self.pricelist_id.currency_id and self.pricelist_id.currency_id.id
        partner_id = self.partner_id and self.partner_id.id
        notes = self.notes
        picking_type_id = purchase_obj._get_picking_in()
        onchange_pick_type = purchase_obj.onchange_picking_type_id(picking_type_id)['value']
        purchase_line_vals =[]
        for line in self.od_tsk_purchase_line:
            product_id = line.product_id and line.product_id.id
            price_unit = line.product_id and line.product_id.standard_price
            uom_id = line.product_id and line.product_id.uom_id and line.product_id.uom_id.id
            product_uom_qty = line.qty
            order_line=purchase_line_obj.onchange_product_id(pricelist_id,product_id,
                                            product_uom_qty, uom_id, partner_id)['value']

            order_line['product_id'] = product_id
            order_line['product_uom'] = uom_id
            order_line['price_unit'] = price_unit
            order_line['product_uom_qty'] = product_uom_qty
            purchase_line_vals.append((0,0,order_line))
        purchase_vals = {
            'partner_id':partner_id,
            'pricelist_id':pricelist_id,
            'currency_id':currency_id,
            'warehouse_id':warehouse_id,
            'od_notes':notes,
            'order_line':purchase_line_vals,

            'picking_type_id':picking_type_id,
        }
        purchase_vals.update(onchange_pick_type)
        if not purchase_line_vals:
            raise Warning("Without Purchase Line You cant Create a Purchase Order")
        purchase_id = purchase_obj.create(purchase_vals)
        purchase_id.od_task_ids = [(4,task_id)]
        return purchase_id.id

    def od_deduplicate(self,l):
        result = []
        for item in l :
            check = False
            for r_item in result :
                if item['product_id'] == r_item['product_id'] :
                    check = True
                    qty = r_item['qty']
                    r_item['qty'] = qty + item['qty']
            if check == False :
                result.append( item )
        return result

    def od_get_purchase_line(self):
        context = self._context
        tsk = self.env['project.task']
        active_id = context.get('task_id')
        res = []
        if active_id:
            task_obj = tsk.browse(active_id)
            for line in task_obj.od_material_request_line:
                if line.state == 'requested':
                    res.append({'product_id':line.product_id and line.product_id.id,
                            'qty':line.qty,
                            })
        result = self.od_deduplicate(res)
        return result

    def od_get_company_id(self):
		return self.env.user.company_id

    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    partner_id = fields.Many2one('res.partner', 'Supplier', required=True, domain="[('supplier','=',True)]")
    pricelist_id = fields.Many2one('product.pricelist', 'Purchase Pricelist', required=True, domain="[('type','=','purchase')]",
                        help="This pricelist will be used, instead of the default one, for purchases from the current partner",)
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse', required=True)
    od_tsk_purchase_line = fields.One2many('od.tsk.purchase.line','purhase_wiz_id',string='Purchase Generate Line',default=od_get_purchase_line)
    notes = fields.Text(string="Notes")
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        partner = self.partner_id
        self.pricelist_id = partner.property_product_pricelist_purchase and partner.property_product_pricelist_purchase.id
od_tsk_gen_purchase()

class od_tsk_purchase_line(models.TransientModel):
    _name = 'od.tsk.purchase.line'
    _description = "Generate Purchase Line"
    purhase_wiz_id = fields.Many2one('od.tsk.gen.purchase',string="WizID")
    product_id = fields.Many2one('product.product',string="Product")
    qty = fields.Float(string="Quantity")
