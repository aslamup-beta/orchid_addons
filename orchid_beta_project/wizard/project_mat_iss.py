# -*- coding: utf-8 -*-
from openerp import models, fields, api
from pprint import pprint
from datetime import datetime
class project_material_issue_wiz(models.TransientModel):
    _name = 'project.material.issue.wiz'



    def get_project_ob(self):
        context = self._context
        project_id = context.get('active_id',False)
        project_obj = self.env['project.project'].browse(project_id)
        return project_obj
    def get_sale_ob(self):
        context = self._context
        project_id = context.get('active_id',False)
        project_obj = self.env['project.project'].browse(project_id)
        analytic = project_obj.analytic_account_id and project_obj.analytic_account_id
        analytic_id = analytic.id or False
        parent =analytic.parent_id
        parent_id = parent.id or False
        grand_parent = parent.parent_id
        grand_parent_id = grand_parent.id or False
        order_ids = []
        if analytic_id:
            order_ids.append(analytic_id)
        if parent_id:
            order_ids.append(parent_id)
        if grand_parent_id:
            order_ids.append(grand_parent_id)
        sale = self.env['sale.order']
        sale_id = sale.search([('project_id','in',order_ids)],limit=1)
        
        return sale_id



    def default_vals(self):
        sale_ob = self.get_sale_ob()
        partner_id = sale_ob.partner_id and sale_ob.partner_id.id
        picking_type_id = sale_ob.warehouse_id and sale_ob.warehouse_id.out_type_id and \
        sale_ob.warehouse_id.out_type_id.id
        company_id = sale_ob.company_id and sale_ob.company_id.id
        od_order_type_id = sale_ob.od_order_type_id and sale_ob.od_order_type_id.id
        od_analytic_id = sale_ob.project_id and sale_ob.project_id.id
        return {'partner_id':partner_id,'company_id':company_id,'od_analytic_id':od_analytic_id,
                'od_order_type_id':od_order_type_id,'picking_type_id':picking_type_id,'origin':sale_ob.name,
                }
    def od_create_stock_moves(self,wiz_line,picking_id):
        stock_move = self.env['stock.move']
        todo_moves = []
        location_id = picking_id.picking_type_id and picking_id.picking_type_id.default_location_src_id and \
        picking_id.picking_type_id.default_location_src_id.id
        location_dest_id = picking_id.picking_type_id and picking_id.picking_type_id.default_location_dest_id and \
        picking_id.picking_type_id.default_location_dest_id.id
        invoice_state = self.get_invoice_control()
        partner_id = picking_id.partner_id and picking_id.partner_id.id
        for line in wiz_line:
            vals ={
                'product_id':line.product_id and line.product_id.id,
                'partner_id':partner_id,
                'procure_method':'make_to_stock',
                'product_uom':line.product_uom_id and line.product_uom_id.id,
                'name':line.name,
                'product_uom_qty':line.qty,
                'date':datetime.now(),
                'date_expected':datetime.now(),
                'location_id':location_id,
                'location_dest_id':location_dest_id,
                'picking_id':picking_id.id,
                'so_line_id':line.so_line_id and line.so_line_id.id,
                'invoice_state':invoice_state,
                'picking_type_id':picking_id.picking_type_id and picking_id.picking_type_id.id or False
            }
            if line.product_id.type in ('product', 'consu'):
                move = stock_move.create(vals)
#                 move.action_confirm()
        # todo_moves = stock_move.action_confirm(cr, uid, todo_moves)
    def get_invoice_control(self):
        sale_obj = self.get_sale_ob()
        order_policy = sale_obj.order_policy
        if order_policy == 'picking':
            return '2binvoiced'
        return 'none'
    
          
    def od_send_mail(self,template,ctx):
        ir_model_data = self.env['ir.model.data']
        email_obj = self.pool.get('email.template')
        send_to ='mohammed.siddiqui@betait.net'
        if self.env.user.company_id.id == 6:
            template = template +'_saudi'
            send_to = 'ahmed.siddiqui@sa.betait.net'
        template_id = ir_model_data.get_object_reference('beta_customisation', template)[1]
        rec_id = self.id
        context = self.env.context.copy()
        context.update(ctx)
        context['send_to'] = send_to
        email_obj.send_mail(self.env.cr,self.env.uid,template_id,rec_id, force_send=True,context=context)
        return True
    
    @api.one
    def generate_delivery_order(self):
        order = self.get_sale_ob()
        wiz_line = self.wiz_line
        invoice_state = self.get_invoice_control()
        ctx = {}
        picking_vals = {
            'date': order.date_order,
            'origin': order.name,
            'invoice_state':invoice_state,
            'od_cost_sheet_id':order.od_cost_sheet_id and order.od_cost_sheet_id.id or False,
            'od_cost_centre_id':order.od_cost_centre_id and order.od_cost_centre_id.id or False,
            'od_branch_id':order.od_branch_id and order.od_branch_id.id or False,
            'od_division_id':order.od_division_id and order.od_division_id.id or False
        }
        vals = self.default_vals()
        picking_vals.update(vals)
        ctx.update(picking_vals)
        picking_id = self.env['stock.picking'].create(picking_vals)
        self.od_create_stock_moves(wiz_line, picking_id)
        ctx['dn_id'] =  picking_id.id
        ctx['so_name'] = order.name
        ctx['picking_id'] =  picking_vals
        self.od_send_mail('project_delivery_request',ctx)

    def get_default_line(self):
        res = []
        project_ob = self.get_project_ob()
        for line in project_ob.od_sale_line:
            od_issue_req_qty = line.od_issue_req_qty
            product_qty = line.product_uom_qty
            qty = product_qty - od_issue_req_qty
            ptype = line.product_id and line.product_id.type
            if qty > 0 and ptype != 'service' :
                res.append({'product_id':line.product_id and line.product_id.id or False,
                            'name':line.name,
                            'product_uom_id':line.product_uom and line.product_uom.id or False,
                            'qty':qty,
                            'so_line_id':line.id
                            })
        return res
    def get_val(self,key):
        res =self.default_vals()
        return res.get(key,False)
    def get_partner_id(self):
        return self.get_val('partner_id')
    def get_company_id(self):
        return self.get_val('company_id')
    def get_picking_type_id(self):
        return self.get_val('picking_type_id')
    def get_order_type_id(self):
        return self.get_val('od_order_type_id')
    def get_analytic_id(self):
        return self.get_val('od_analytic_id')
    
    @api.onchange('prod_select_all')
    def onchange_prod_select_all(self):
        if self.prod_select_all:
            for x in self.wiz_line:
                x.check = True
        else:
            for x in self.wiz_line:
                x.check = False
                 
    @api.multi
    def delete_prod_lines(self):
        for line in self.wiz_line:
            if line.check:
                line.unlink()
        return {
        'context': self.env.context,
        'view_type': 'form',
        'view_mode': 'form',
        'res_model': 'project.material.issue.wiz',
        'res_id': self.id,
        'view_id': False,
        'type': 'ir.actions.act_window',
        'target': 'new',
    }

    wiz_line = fields.One2many('project.material.issue.wiz.line','wiz_id',default=get_default_line)
    picking_type_id = fields.Many2one('stock.picking.type',string="Picking Type",required=True,readonly=True,default=get_picking_type_id)
    company_id = fields.Many2one('res.company',string='Company',required=True,readonly=True,default=get_company_id)
    partner_id = fields.Many2one('res.partner',string="Partner",default=get_partner_id,required=True)
    od_order_type_id = fields.Many2one('od.order.type',string="Transaction Type",default=get_order_type_id)
    od_analytic_id  = fields.Many2one('account.analytic.account',string="Analytic Account",default=get_analytic_id)
    prod_select_all = fields.Boolean(string="Select All")



class project_material_issue_wiz_line(models.TransientModel):
    _name = 'project.material.issue.wiz.line'
    wiz_id = fields.Many2one('project.material.issue.wiz',string="Wizard")
    product_id = fields.Many2one('product.product',string="Product")
    name = fields.Char(string='Name')
    product_uom_id =fields.Many2one('product.uom',string='Unit')
    qty = fields.Float(string='Product Qty')
    so_line_id = fields.Many2one('sale.order.line',string="Sale Order Line")
    check = fields.Boolean(string="Check")
