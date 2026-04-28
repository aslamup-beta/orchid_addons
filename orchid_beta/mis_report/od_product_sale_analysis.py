# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import fields, osv
class od_so_analysis(osv.osv):
    _name = "od.so.analysis"
    _description = "Sales Order Report"
    _auto = False
    _columns = {
        'order_id': fields.many2one('sale.order',string="Sale Order",readonly=True),
        'cost_sheet_id':fields.many2one('od.cost.sheet',string="Cost Sheet",readonly=True),
        'project_id': fields.many2one('account.analytic.account', 'Project', readonly=True),
        'date_order':fields.datetime('Date',readonly=True),
        'user_id': fields.many2one('res.users', 'Salesman', readonly=True),
        'bdm_user_id':fields.many2one('res.users', 'BDM', readonly=True),
        'section_id':fields.many2one('crm.case.section', 'Sales Team', readonly=True),
        'od_order_type_id':fields.many2one('od.order.type', 'Order Type', readonly=True),           
        'partner_id':fields.many2one('res.partner', 'Customer', readonly=True),            
        'state': fields.selection([
            ('cancel', 'Cancelled'),
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('exception', 'Exception'),
            ('done', 'Done')], 'Status', readonly=True),
        'categ_id': fields.many2one('product.category','Product Category', readonly=True),
        'product_id': fields.many2one('product.product', 'Product', readonly=True),
        'company_id': fields.many2one('res.company', 'Company', readonly=True),
        'original_qty':fields.float('Org Qty',readonly=True),
        'original_price':fields.float('Org Unit Price',readonly=True),
        'original_total_price':fields.float('Org Amount',readonly=True),
        'original_total_cost':fields.float('Org Cost',readonly=True),
        'amended_total_cost':fields.float('Amended Cost',readonly=True),
        'product_uom_qty': fields.float('Amended Qty', readonly=True),
        'price_unit':fields.float("Final Unit Price",readonly=True),
        'amended_total_price':fields.float(' Amended Amount',readonly=True),
        'delivered':fields.float("Delivered Qty",readonly=True),
        'pending':fields.float("Pending Qty",readonly=True),
        'cancel':fields.float("Cancel Qty",readonly=True),
        'od_pdt_group_id': fields.many2one('od.product.group', 'Product Group', readonly=True),
        'od_pdt_sub_group_id': fields.many2one('od.product.sub.group', 'Product Sub Group', readonly=True),
        'od_pdt_type_id': fields.many2one('od.product.type', 'Product Type', readonly=True),
        'od_pdt_sub_type_id': fields.many2one('od.product.sub.type', 'Product Sub Type', readonly=True),
        
        
        
    
    }
    _order = 'product_id ASC'
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'od_so_analysis')
        cr.execute("""
             create or replace view od_so_analysis as (
                SELECT min(l.id) AS id,
                s.date_order,
                s.user_id,
                s.bdm_user_id,
                s.section_id as section_id,
                s.od_order_type_id,
                s.partner_id,
                s.project_id,
                l.company_id,
                l.product_id,
                l.product_uom_qty,
                l.od_original_price AS original_price,
                
                
                l.od_original_qty AS original_qty,
                (l.od_original_price * l.od_original_qty) AS original_total_price,
                (l.od_original_unit_cost * l.od_original_qty) AS original_total_cost,
                l.price_unit,
                (l.price_unit * l.product_uom_qty) AS amended_total_price,
                 (l.purchase_price * l.product_uom_qty) AS amended_total_cost,
                l.order_id,
                l.od_cost_sheet_id AS cost_sheet_id,
                l.state,
                t.categ_id,
                smv.delivered,
                smv.pending,
                smv.cancel,
                t.od_pdt_group_id,
                t.od_pdt_sub_group_id,
                t.od_pdt_type_id,
                t.od_pdt_sub_type_id,
                l.write_date
               FROM ((((sale_order_line l
                 JOIN sale_order s ON ((s.id = l.order_id)))
                 LEFT JOIN product_product p ON ((l.product_id = p.id)))
                 LEFT JOIN product_template t ON ((p.product_tmpl_id = t.id)))
                 LEFT JOIN od_order_stock_move smv ON ((smv.so_line_id = l.id)))
              GROUP BY l.company_id, s.date_order, s.user_id, s.bdm_user_id, s.section_id,
             s.od_order_type_id, s.partner_id, s.project_id, l.state, l.od_cost_sheet_id, 
            l.order_id, t.categ_id, l.product_id, l.product_uom_qty, l.od_original_price, 
            l.od_original_qty, l.od_original_unit_cost, l.purchase_price, l.price_unit,
            t.od_pdt_group_id,
            t.od_pdt_sub_group_id,
            t.od_pdt_type_id,
            t.od_pdt_sub_type_id, 
            smv.delivered, smv.pending, smv.cancel,l.id
            )
         """)
      

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
