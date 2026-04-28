# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from lxml import etree
from pprint import pprint
from openerp.exceptions import Warning
import openerp.addons.decimal_precision as dp
class sale_order(models.Model):
    _inherit = 'sale.order'
    
    
    def _prepare_invoice(self, cr, uid, order, lines, context=None):
        """Prepare the dict of values to create the new invoice for a
           sales order. This method may be overridden to implement custom
           invoice generation (making sure to call super() to establish
           a clean extension chain).

           :param browse_record order: sale.order record to invoice
           :param list(int) line: list of invoice line IDs that must be
                                  attached to the invoice
           :return: dict of value to create() the invoice
        """
       
        invoice_vals = super(sale_order,self)._prepare_invoice(cr, uid, order, lines, context)
        invoice_vals.update({'od_cost_sheet_id':order.od_cost_sheet_id and order.od_cost_sheet_id.id or False,
                             'od_branch_id':order.od_branch_id and order.od_branch_id.id or False,
                             'od_cost_centre_id':order.od_cost_centre_id and order.od_cost_centre_id.id or False,
                             'od_division_id':order.od_division_id and order.od_division_id.id or False,
                             'od_analytic_account':order.project_id and order.project_id.id or False
                             })
        

        return invoice_vals
    
    @api.onchange('od_order_type_id')
    def onchange_order_type(self):
        if self.od_order_type_id:
            order_type = self.od_order_type_id and self.od_order_type_id.id or False
            if order_type in  (12,26):
                self.order_policy = 'picking'
            else:
                self.order_policy = 'manual'
    @api.one
    @api.depends('order_line')
    def compute_values(self):
        original_total_price = 0.0
        original_total_cost = 0.0
        od_amd_total_price = 0.0
        od_amd_total_cost = 0.0
        original_profit_percent = 0.0
        od_amd_total_profit_percent = 0.0
        mp = self.od_cost_sheet_id and self.od_cost_sheet_id.returned_mp or 0.0
        for line in self.order_line:
            original_total_price += line.od_original_line_price
            original_total_cost += line.od_original_line_cost
            od_amd_total_price += line.price_subtotal
            od_amd_total_cost += line.od_amended_line_cost
        original_profit =  original_total_price - original_total_cost
        od_amd_total_profit =  od_amd_total_price - od_amd_total_cost
        if original_total_price:
            original_profit_percent = original_profit/original_total_price
            self.od_original_profit_percent = original_profit_percent *100
        if  od_amd_total_price:
            od_amd_total_profit_percent = od_amd_total_profit/od_amd_total_price
            self.od_amd_total_profit_percent = od_amd_total_profit_percent * 100
        self.od_original_total_price = original_total_price
        self.od_original_total_cost = original_total_cost
        self.od_original_profit = original_profit
        self.od_amd_total_price = od_amd_total_price
        self.od_amd_total_cost = od_amd_total_cost
        self.od_amd_total_profit = od_amd_total_profit
    
    
    
    def get_analytic_state(self):
        return      [             
             ('template', 'Template'),
             ('draft','New'),
             ('open','In Progress'),
            ('pending','To Renew'),
             ('close','Closed'),
            ('cancelled', 'Cancelled')
            ]

 #Related Analytic_state
    
    project_state  = fields.Selection(get_analytic_state,string='Mat Analtyic State',related="project_id.state" ,readonlyt=True)
    
    project_closing_date = fields.Date(string="Project Closing Date",related="project_id.od_closing_date")
    bdm_user_id  = fields.Many2one('res.users',string='BDM',readonly=True)
    presale_user_id = fields.Many2one('res.users',string='Presales',readonly=True)
    od_cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',readonly=True)
    od_original_total_price = fields.Float(string='Original Total Price',compute="compute_values",digits=dp.get_precision('Account'))
    od_original_total_cost = fields.Float(string='Original Total Price',compute="compute_values",digits=dp.get_precision('Account'))
    od_original_profit = fields.Float(string="Original Profit",compute="compute_values",digits=dp.get_precision('Account'))
    od_original_profit_percent = fields.Float(string="Original Profit Percentage",compute="compute_values",digits=dp.get_precision('Account'))
    od_amd_total_price = fields.Float(string="Amendement Total Price",compute="compute_values",digits=dp.get_precision('Account'))
    od_amd_total_cost = fields.Float(string="Amendement Total Cost",compute="compute_values",digits=dp.get_precision('Account'))
    od_amd_total_profit = fields.Float(string="Amendement Total Profit",compute="compute_values",digits=dp.get_precision('Account'))
    od_amd_total_profit_percent = fields.Float(string="Total Amendement Profit Percentage",compute="compute_values",digits=dp.get_precision('Account'))
    od_approved_date = fields.Date(string="Approved Date",readonly=True)
    
    
    od_cost_centre_id =fields.Many2one('od.cost.centre',string='Cost Centre',related="od_cost_sheet_id.od_cost_centre_id",readonly=True)
    od_branch_id =fields.Many2one('od.cost.branch',string='Branch',related="od_cost_sheet_id.od_branch_id",readonly=True)
    od_division_id = fields.Many2one('od.cost.division',string='Division',related="od_cost_sheet_id.od_division_id",readonly=True)
    lead_id = fields.Many2one('crm.lead',string="Opportunity",related="od_cost_sheet_id.lead_id",readonly=True)
     
    od_sale_team_id = fields.Many2one('crm.case.section',string="Sale Team",related="lead_id.section_id",readonly=True)
    op_stage_id = fields.Many2one('crm.case.stage',string="Opp Stage",related="lead_id.stage_id",readonly=True)    
    op_expected_booking = fields.Date(string="Opp Expected Booking",related="lead_id.date_action",readonly=True)    
   
    op_stage_id = fields.Many2one('crm.case.stage',string="Opp Stage",related="lead_id.stage_id",readonly=True)    
    fin_approved_date = fields.Datetime(string="Finance Approved Date",related="od_cost_sheet_id.approved_date",readonly=True)
    od_closing_date = fields.Date(string="Closing Date")        
    
    @api.multi
    def od_open_delivey_orders(self):
        name = self.name
        picking = self.env['stock.picking']
        domain = [('origin','=',name)]
        picking_obj = picking.search(domain)
        picking_ids = [pick.id for pick in picking_obj]
        dom = [('id','in',picking_ids)]
        return {
            'domain':dom,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'type': 'ir.actions.act_window',
        }
    @api.multi
    def od_open_sale_order_line(self):
        sale_id = self.id
        domain = [('order_id','=',sale_id)]
        model_data = self.env['ir.model.data']
        # Select the view
        tree_view = model_data.get_object_reference( 'orchid_cost_sheet', 'view_sale_order_line_for_beta_tree')
        form_view = model_data.get_object_reference( 'orchid_cost_sheet', 'view_sale_order_line_for_beta')
        return {
            'name': _('Extra Sale Line Info'),
            'domain':domain,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [ (tree_view and tree_view[1] or False, 'tree'),(form_view and form_view[1] or False, 'form')],
            'res_model': 'sale.order.line',
            'type': 'ir.actions.act_window',
        }
    def od_cost_check_do(self):
        picking = self.env['stock.picking']
        name = self.name
        dom = [('origin','=',name)]
        pickings = picking.search(dom)
        states = [pick.state for pick in pickings]
        for state in states:
            if state != 'cancel':
                return False
        return True
    @api.one
    def od_reset_draft(self):
        if self.od_cost_check_do():
            self.signal_workflow('reset_draft')
            self.write({'state':'draft'})
        else:
            raise Warning("Please Cancel All Material Requests Associated")
    @api.multi
    def od_open_material_issue(self):
        return {
              'name': _('Material Issue Request'),
              'view_type': 'form',
              "view_mode": 'form',
              'res_model': 'material.issue.wiz',
              'type': 'ir.actions.act_window',
              'target':'new',
              }
        
class sale_order_line(models.Model):
    _inherit = 'sale.order.line'
    _tab_type_sel = [('mat','MAT'),('trn','TRN'),('imp','IMP'),('amc','AMC'),('o_m','O&M'),(('i_s','IS'))]
#     def invoice_line_create(self, cr, uid, ids, context=None):
#         print "calling invoice_line_create>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",ids
#         create_ids = super(sale_order_line, self).invoice_line_create(cr, uid, ids, context=context)
#         print "created ids>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",create_ids
#         inv_line_obj = self.pool.get('account.invoice.line')
#          
#         if not ids:
#             return create_ids
# #         for line in inv_line_obj.browse(cr, uid, create_ids, context=context):
# #             inv_line_obj.write(cr, uid, [line.id], {'so_line_id': ids[0]}, context=context)
#         return create_ids
#     
    
    
    def _prepare_order_line_invoice_line(self, cr, uid, line, account_id=False, context=None):
        res = super(sale_order_line,self)._prepare_order_line_invoice_line(cr, uid, line, account_id=account_id, context=context)
        res['so_line_id'] = line.id
        return res
    
    @api.one
    def get_po_request_qty(self):
        po_line = self.env['purchase.order.line']
        so_line_id = self.id
        domain = [('so_line_id','=',so_line_id),('state','!=','cancel')]
        po_ob = po_line.search(domain)
        qty = 0.0
        for po in po_ob:
            qty += po.product_qty
        self.od_po_request_qty = qty or 0.0

    @api.one
    def get_po_qty(self):
        po_line = self.env['purchase.order.line']
        so_line_id = self.id
        domain = [('so_line_id','=',so_line_id),('state','=','confirmed')]
        po_ob = po_line.search(domain)
        qty = 0.0
        for po in po_ob:
            qty += po.product_qty
        self.od_po_qty = qty or 0.0

    @api.one
    def get_issue_req_qty(self):
        move_line = self.env['stock.move']
        so_line_id = self.id
        domain = [('so_line_id','=',so_line_id),('state','!=','cancel')]
        move_ob = move_line.search(domain)
        qty = 0.0
        return_qty = 0.0
        for mv in move_ob:
            picking_type_id = mv.picking_type_id
            if not picking_type_id:
                picking_type_id = mv.picking_id and mv.picking_id.picking_type_id
            if picking_type_id.code == 'outgoing':
                qty += mv.product_uom_qty
            if picking_type_id.code == 'incoming':
                return_qty += mv.product_uom_qty
        final_qty = qty - return_qty
        self.od_issue_req_qty = final_qty or 0.0
    @api.one
    def get_issued_qty(self):
        move_line = self.env['stock.move']
        so_line_id = self.id
        domain = [('so_line_id','=',so_line_id),('state','=','done')]
        move_ob = move_line.search(domain)
        qty = 0.0
        return_qty = 0.0
        for mv in move_ob:
            picking_type_id = mv.picking_type_id
            if not picking_type_id:
                picking_type_id = mv.picking_id and mv.picking_id.picking_type_id
            if picking_type_id.code == 'outgoing':
                qty += mv.product_uom_qty
            if picking_type_id.code == 'incoming':
                return_qty += mv.product_uom_qty
        final_qty = qty - return_qty
        self.od_issued_qty = final_qty or 0.0

    od_tab_type = fields.Selection(_tab_type_sel,string="Tab Type")
    od_original_qty = fields.Float(string='Original Qty',readonly=True,digits=dp.get_precision('Account'))
    od_inactive = fields.Boolean(string="Inactive",readonly=True,copy=True)
    od_original_price = fields.Float(string="Original Price",readonly=True,digits=dp.get_precision('Account'))
    od_original_line_price = fields.Float(string="Original Line Price",compute="_compute_line_price",digits=dp.get_precision('Account'))
    od_original_unit_cost = fields.Float(string="Original Unit Cost",readonly=True,digits=dp.get_precision('Account'))
    od_original_line_cost = fields.Float(string="Original Line Cost",compute="_compute_line_price",digits=dp.get_precision('Account'))
    od_sup_unit_cost= fields.Float(string="Disc.Unit Cost Supplier Currency",readonly=True,digits=dp.get_precision('Account'))
    od_sup_line_cost= fields.Float(string="Disc.Total Cost Supplier Currency",readonly=True,digits=dp.get_precision('Account'))
    od_manufacture_id = fields.Many2one('od.product.brand',string="Manufacture")
    od_amended_line_cost = fields.Float(string="Amended Line Cost",compute="_compute_line_price",digits=dp.get_precision('Account'))
    od_po_request_qty = fields.Float(string="PO Request Qty",compute="get_po_request_qty",digits=dp.get_precision('Account'))
    od_po_qty = fields.Float(string="PO Qty",compute="get_po_qty",digits=dp.get_precision('Account'))
    od_issue_req_qty = fields.Float(string="Issue Request Qty",compute="get_issue_req_qty",digits=dp.get_precision('Account'))
    od_issued_qty = fields.Float(string="Issued Qty",compute="get_issued_qty",digits=dp.get_precision('Account'))
    od_analytic_acc_id = fields.Many2one('account.analytic.account',string="Analytic Account")
    od_cost_sheet_id = fields.Many2one('od.cost.sheet',string="Cost Sheet")
    def get_line_price(self,qty,amount):
        return qty * amount

    @api.one
    @api.depends('od_original_qty','od_original_price','od_original_unit_cost','product_uom_qty','purchase_price')
    def _compute_line_price(self):
        self.od_original_line_cost = self.get_line_price(self.od_original_qty,self.od_original_unit_cost)
        self.od_original_line_price = self.get_line_price(self.od_original_qty,self.od_original_price)
        self.od_amended_line_cost = self.get_line_price(self.product_uom_qty,self.purchase_price)
