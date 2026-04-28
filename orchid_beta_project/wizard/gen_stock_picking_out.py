# -*- coding: utf-8 -*-
from pprint import pprint
from openerp import models,fields,api
class od_tsk_gen_picking_out(models.TransientModel):
    _name = "od.tsk.gen.picking.out"
    _description = 'Generate Picking Out From Task'



    def mark_do(self,task):
        """ This function for mark Material Line in task after Delivery Order Created ,
            this will tick DO Field in the line  """

        for line in task.od_material_request_line:
            if line.state == 'requested':
                line.do = True

    @api.multi
    def button_delivery_order(self):
        context = self._context
        tsk = self.env['project.task']
        # active_id = context.get('active_id',False)
        active_id = context.get('task_id',False)
        task = self.env['project.task']
        task_obj = task.browse(active_id)
        picking_ids = self.gen_delivery_order()
        delivery_line_obj = self.env['od.task.delivery.order']
        for picking_id in picking_ids:
            delivery_line_obj.create({
                    'task_id':active_id,
                    'picking_id':picking_id
              })
        self.mark_do(task_obj)



    def gen_delivery_order(self):
        picking_ids = []

        context = self._context
        task_id = context.get('task_id',False)
        task = self.env['project.task']
        task_obj = task.browse(task_id)
        task_name = task_obj.name

        picking = self.env['stock.picking']
        stockMove = self.env['stock.move']
        picking_type_id = self.picking_type_id and self.picking_type_id.id
        default_location_src_id = self.picking_type_id and self.picking_type_id.default_location_src_id and self.picking_type_id.default_location_src_id.id
        default_location_dest_id = self.picking_type_id and self.picking_type_id.default_location_dest_id and self.picking_type_id.default_location_dest_id.id
        notes = self.notes
        for line in self.od_tsk_picking_line:
            partner_id = line.partner_id and line.partner_id.id
            product_id = line.product_id and line.product_id.id
            # uom_id = line.product_id and line.product_id.uom_id and line.product_id.uom_id.id
            qty = line.qty
            move_line_vals = {
            'product_id':product_id,
            'product_uom_qty':qty,
            'location_id':default_location_src_id,
            'location_dest_id':default_location_dest_id,

            }
            onchange_product_id = stockMove.onchange_product_id(product_id,default_location_src_id,default_location_dest_id,partner_id)['value']
            move_line_vals.update(onchange_product_id)
            vals = {
                'partner_id':partner_id,'picking_type_id':picking_type_id,'od_notes':notes,'origin':task_name,
                'move_lines':[(0,0,move_line_vals)]
            }
            picking_ids.append(picking.create(vals).id)
        return picking_ids
    def od_deduplicate(self,l):
        result = []
        for item in l :
            check = False
            for r_item in result :
                if item['partner_id'] == r_item['partner_id'] :
                    check = True
                    qty = r_item['qty']
                    r_item['qty'] = qty + item['qty']
            if check == False :
                result.append( item )

        return result

    def od_get_picking_line(self):
        context = self._context
        tsk = self.env['project.task']
        # active_id = context.get('active_id',False)
        active_id = context.get('task_id',False)
        res = []
        if active_id:
            task_obj = tsk.browse(active_id)
            for line in task_obj.od_material_request_line:
                if line.state == 'requested':
                    res.append({'product_id':line.product_id and line.product_id.id,
                                'partner_id':line.partner_id and line.partner_id.id,
                                'qty':line.qty,
                                })
        # result = self.od_deduplicate(res)
        return res

    def _od_get_picking_out(self, cr, uid, context=None):
        obj_data = self.pool.get('ir.model.data')
        type_obj = self.pool.get('stock.picking.type')
        user_obj = self.pool.get('res.users')
        company_id = user_obj.browse(cr, uid, uid, context=context).company_id.id
        types = type_obj.search(cr, uid, [('code', '=', 'outgoing'), ('warehouse_id.company_id', '=', company_id)], context=context)
        if not types:
            types = type_obj.search(cr, uid, [('code', '=', 'outgoing'), ('warehouse_id', '=', False)], context=context)
            if not types:
                raise osv.except_osv(_('Error!'), _("Make sure you have at least an incoming picking type defined"))
        return types[0]

    def od_get_company_id(self):
		return self.env.user.company_id

    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    picking_type_id = fields.Many2one('stock.picking.type',string="Picking Type",required=True)
    notes = fields.Text(string='Notes')
    od_tsk_picking_line = fields.One2many('od.tsk.picking.out.line','wiz_id',string='Picking Line',default=od_get_picking_line)

class od_tsk_picking_out_line(models.TransientModel):
    _name = 'od.tsk.picking.out.line'
    _description = "Generate Picking Out Line"
    wiz_id = fields.Many2one('od.tsk.gen.picking.out',string="WizID")
    product_id = fields.Many2one('product.product',string="Product")
    qty = fields.Float(string="Quantity")
    partner_id = fields.Many2one('res.partner',string="Partner")
