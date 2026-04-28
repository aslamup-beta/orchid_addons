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
        'date_order':fields.date('Date',readonly=True),
        'user_id': fields.many2one('res.users', 'Salesman', readonly=True),
        'bdm_user_id':fields.many2one('res.users', 'BDM', readonly=True),
        's.section_id,':fields.many2one('crm.case.section', 'Sales Team', readonly=True),
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
        'original_cost':fields.float('Org Unit Cost',readonly=True),
        'original_total_cost':fields.float('Org Cost',readonly=True),
        'original_profit':fields.float('Org Profit',readonly=True),
        'product_uom_qty': fields.float('FInal Qty', readonly=True),
        'price_unit':fields.float("Final Unit Price",readonly=True),
        'purchase_price': fields.float("Final Unit Cost",readonly=True),
        'amended_total_price':fields.float('Final Amount',readonly=True),
        'amended_total_cost':fields.float('Final Cost',readonly=True),
        'amended_profit': fields.float('Final Profit',readonly=True),
        'purchased_qty':fields.float("Purchased Qty",readonly=True),
        'purchased_price':fields.float("Purchased Amount",readonly=True),
        'invoiced_qty': fields.float("Invoiced Qty",readonly=True),
        'invoiced_price': fields.float("Invoiced Amount",readonly=True),
        'delivered':fields.float("Delivered Qty",readonly=True),
        'pending':fields.float("Pending Qty",readonly=True),
        'cancel':fields.float("Cancel Qty",readonly=True),
    }
    _order = 'product_id ASC'

    # def _select(self):
    #     select_str = """
    #         SELECT min(l.id) AS id,
    #                 s.date_order,
    #                 s.user_id,
    #                 s.bdm_user_id,
    #                 s.section_id,
    #                 s.od_order_type_id,
    #                 s.partner_id,
    #                 s.project_id,
    #                 l.company_id,
    #                 l.product_id as product_id,
    #                 l.product_uom_qty,
    #                 l.od_original_price as original_price,
    #                 l.od_original_qty as original_qty,
    #                 (l.od_original_price * l.od_original_qty) as original_total_price,
    #                 l.od_original_unit_cost as original_cost,
    #                 (l.od_original_unit_cost * l.od_original_qty) as original_total_cost,
    #                 ((l.od_original_price * l.od_original_qty) - (l.od_original_unit_cost * l.od_original_qty)) as original_profit,
    #                 l.price_unit as price_unit,
    #                 (l.price_unit * l.product_uom_qty) as amended_total_price,
    #                 l.purchase_price,
    #                 (l.purchase_price * l.product_uom_qty) as amended_total_cost,
    #                 ((l.price_unit * l.product_uom_qty) - (l.purchase_price * l.product_uom_qty)) as amended_profit,
    #                 l.order_id,
    #                 pol.price_unit as purchased_price,
    #                 pol.product_qty as purchased_qty,
    #                 inl.price_unit as invoiced_price,
    #                 inl.quantity as invoiced_qty,
    #                 l.od_cost_sheet_id as cost_sheet_id,
    #                 l.state,
    #                 t.categ_id as categ_id,
    #                 smv.delivered,
    #                 smv.pending,
    #                 smv.cancel
    #     """
    #     return select_str

    # def _from(self):
    #     from_str = """
    #         sale_order_line l
    #             join sale_order s on (s.id = l.order_id)
    #             left join product_product p on (l.product_id = p.id)
    #             left join product_template t on (p.product_tmpl_id = t.id)
    #             left join account_invoice_line inl on (inl.so_line_id = l.id)
    #             left join purchase_order_line pol on (pol.so_line_id = l.id)
    #             left join od_order_stock_move smv on (smv.so_line_id = l.id)
    #             """
    #     return from_str

    # def _group_by(self):
    #     group_by_str = """
    #         GROUP BY 
    #                 l.company_id,
    #                 s.date_order,
    #                 s.user_id,
    #                 s.bdm_user_id,
    #                 s.section_id,
    #                 s.od_order_type_id,
    #                 s.partner_id,
    #                 s.project_id,
    #                 l.state,
    #                 l.od_cost_sheet_id,
    #                 l.order_id,
    #                 t.categ_id ,
    #                 l.product_id,
    #                 l.product_uom_qty,
    #                 l.od_original_price,
    #                 l.od_original_qty,
    #                 l.od_original_unit_cost,
    #                 l.purchase_price,
    #                 l.price_unit,
    #                 pol.price_unit,
    #                 pol.product_qty,
    #                 inl.price_unit,
    #                 inl.quantity,       
    #                 smv.delivered,
    #                 smv.pending,
    #                 smv.cancel
    #     """
    #     return group_by_str

    def init(self, cr):
       
        tools.drop_view_if_exists(cr, 'od_so_analysis')
        # cr.execute("DROP TABLE IF EXISTS od_so_analysis")
        cr.execute("""
             create or replace view od_so_analysis as (
             SELECT min(l.id) AS id,
                    s.date_order,
                    s.user_id,
                    s.bdm_user_id,
                    s.section_id,
                    s.od_order_type_id,
                    s.partner_id,
                    s.project_id,
                    l.company_id,
                    l.product_id as product_id,
                    l.product_uom_qty,
                    l.od_original_price as original_price,
                    l.od_original_qty as original_qty,
                    (l.od_original_price * l.od_original_qty) as original_total_price,
                    l.od_original_unit_cost as original_cost,
                    (l.od_original_unit_cost * l.od_original_qty) as original_total_cost,
                    ((l.od_original_price * l.od_original_qty) - (l.od_original_unit_cost * l.od_original_qty)) as original_profit,
                    l.price_unit as price_unit,
                    (l.price_unit * l.product_uom_qty) as amended_total_price,
                    l.purchase_price,
                    (l.purchase_price * l.product_uom_qty) as amended_total_cost,
                    ((l.price_unit * l.product_uom_qty) - (l.purchase_price * l.product_uom_qty)) as amended_profit,
                    l.order_id,
                    pol.price_unit as purchased_price,
                    pol.product_qty as purchased_qty,
                    inl.price_unit as invoiced_price,
                    inl.quantity as invoiced_qty,
                    l.od_cost_sheet_id as cost_sheet_id,
                    l.state,
                    t.categ_id as categ_id,
                    smv.delivered,
                    smv.pending,
                    smv.cancel
        
            FROM ( 
            sale_order_line l
                join sale_order s on (s.id = l.order_id)
                left join product_product p on (l.product_id = p.id)
                left join product_template t on (p.product_tmpl_id = t.id)
                left join account_invoice_line inl on (inl.so_line_id = l.id)
                left join purchase_order_line pol on (pol.so_line_id = l.id)
                left join od_order_stock_move smv on (smv.so_line_id = l.id)
                 )
            
            GROUP BY 
                    l.company_id,
                    s.date_order,
                    s.user_id,
                    s.bdm_user_id,
                    s.section_id,
                    s.od_order_type_id,
                    s.partner_id,
                    s.project_id,
                    l.state,
                    l.od_cost_sheet_id,
                    l.order_id,
                    t.categ_id ,
                    l.product_id,
                    l.product_uom_qty,
                    l.od_original_price,
                    l.od_original_qty,
                    l.od_original_unit_cost,
                    l.purchase_price,
                    l.price_unit,
                    pol.price_unit,
                    pol.product_qty,
                    inl.price_unit,
                    inl.quantity,       
                    smv.delivered,
                    smv.pending,
                    smv.cancel
        
            )


         """)
        # cr.execute(""" create or replace view %s as (
        #     %s
        #     FROM ( %s )
        #     %s
        #     )""" % (self._table, self._select(), self._from(), self._group_by()))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
