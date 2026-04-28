# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import fields, osv
class od_so_register_report_view(osv.osv):
    _name = "od.so.register.report.view"
    _description = "od.so.register.report.view"
    _auto = False
    _rec_name = 'name'
    _columns = {
        'name':fields.char('Name'),
        'date_order': fields.date('Date Order', readonly=True),
        'partner_id': fields.many2one('res.partner','Partner'),
        'state': fields.char('State'),
        'pricelist_id':fields.many2one('product.pricelist','Price List'),
        'partner_invoice_id':fields.many2one('res.partner','Invoice Address'),
        'product_id':fields.many2one('product.product','Product'),
        'product_uom': fields.many2one('product.uom','Unit of Measure'),
        'price_unit':fields.float('Price Unit'),
        'product_uom_qty':fields.float('Quantity'),
        'date_planned':fields.date('Date Planned', readonly=True),
        'sovalue':fields.float('SO Value'),
        'salesman_id':fields.many2one('res.users','Salesman'),
        'sale_order_line_id': fields.many2one('sale.order.line','Sale Line ID'),
        'company_id' : fields.many2one('res.company','Company'),
        
    }
    def _select(self):
        select_str = """
              SELECT ROW_NUMBER () OVER (ORDER BY sh.id ) AS id,
             sh.name AS name,
            sh.company_id as company_id,
             sh.date_order as date_order,
             sh.partner_id as partner_id,
             sh.state as state,
             sh.pricelist_id as pricelist_id,
             sh.partner_invoice_id as partner_invoice_id,
             sl.product_id as product_id,
             sl.product_uom as product_uom,
             sl.price_unit as price_unit,
             sl.product_uom_qty as product_uom_qty,
             (sl.price_unit*sl.product_uom_qty) as sovalue,
             sl.salesman_id as salesman_id
             
        """
        return select_str
#sl.date_planned as date_planned
    def _from(self):
        from_str = """
                sale_order sh
        """
        return from_str

    def _order_by(self):
        order_by_str = """
            ORDER BY sh.name, 
                   sh.date_order
        """
        return order_by_str


    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM  %s 
    INNER JOIN sale_order_line sl ON (sl.order_id = sh.id)
  %s
            )""" % (self._table, self._select(), self._from(), self._order_by()))



