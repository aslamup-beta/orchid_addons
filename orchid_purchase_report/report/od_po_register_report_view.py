# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import fields, osv
class od_po_register_report_view(osv.osv):
    _name = "od.po.register.report.view"
    _description = "od.po.register.report.view"
    _auto = False
    _rec_name = 'name'
    _columns = {
        'name':fields.char('Name'),
        'date_order': fields.date('Date Order', readonly=True),
        'location_id': fields.many2one('stock.location','Location'),
        'partner_id': fields.many2one('res.partner','Partner'),
        'state': fields.char('State'),
        'partner_ref':fields.char('Partner Reference'),
        'date_approve':fields.date('Date Approve', readonly=True),
        'date_planned':fields.date('Date Planned', readonly=True),
        'product_id':fields.many2one('product.product','Product'),
        'product_uom': fields.many2one('product.uom','Unit of Measure'),
        'price_unit':fields.float('Price Unit'),
        'product_qty': fields.float('Product Quantity'),
        'povalue':fields.float('PO Value'),
        'purchase_order_line_id': fields.many2one('purchase.order.line','Purchase Line ID'),
        'company_id' : fields.many2one('res.company','Company'),
        'currency_id': fields.many2one('res.currency','Currency')
    }


    def _select(self):
        select_str = """
             SELECT ROW_NUMBER () OVER (ORDER BY  ph.id ) AS id,
            ph.name AS name,
            ph.date_order as date_order,
            ph.company_id as company_id,
            ph.partner_id as partner_id,
            ph.currency_id as currency_id,
            ph.state as state,
            ph.location_id as location_id,
            ph.partner_ref as partner_ref,
            ph.date_approve as date_approve,
            pl.product_id as product_id,
            pl.product_uom as product_uom,
            pl.price_unit as price_unit,
            pl.product_qty as product_qty,
            (pl.price_unit*pl.product_qty) as povalue,
            pl.date_planned as date_planned
        """
        return select_str

    def _from(self):
        from_str = """
                purchase_order ph
        """
        return from_str
#    def _group_by(self):
#        group_by_str = """
#            GROUP BY ph.partner_id, 
#                   pl.product_id,
#                   ph.name,
#                   ph.date_order,
#                   ph.state,
#                   ph.location_id,
#                   ph.partner_ref,
#                   ph.date_approve,
#                   pl.product_uom,
#                   pl.price_unit,
#                   pl.product_qty,
#                   pl.date_planned,
#                   ph.id
#                   
#        """
#        return group_by_str        

    def _order_by(self):
        order_by_str = """
            ORDER BY ph.name, 
                   ph.date_order
        """
        return order_by_str

#    def init(self, cr):
#        # self._table = sale_report
#        tools.drop_view_if_exists(cr, self._table)
#        cr.execute("""CREATE or REPLACE VIEW %s as (
#            %s
#            FROM  %s 
#    inner join purchase_order_line pl ON (pl.order_id = ph.id) %s
#            )""" % (self._table, self._select(), self._from(),self._order_by))


#od_po_register_report_view()

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM  %s 
INNER JOIN purchase_order_line pl ON (pl.order_id = ph.id)
  %s
            )""" % (self._table, self._select(), self._from(), self._order_by()))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:










































     

#    SO Register

#     

#    SELECT SH.NAME,SH.DATE_ORDER,SH.PARTNER_ID,SH.STATE,SH.PRICELIST_ID,SH.PARTNER_INVOICE_ID,

#    SL.PRODUCT_ID,SL.PRODUCT_UOM,SL.DATE_PLANNED,SL.PRICE_UNIT,SL.PRODUCT_UOM_QTY,SL.PRICE_UNIT,(SL.PRICE_UNIT*SL.PRODUCT_UOM_QTY) AS SOVALUE,

#    SL.SALESMAN_ID

#    FROM SALE_ORDER SH

#    INNER JOIN SALE_ORDER_LINE SL ON (SL.ORDER_ID = SH.ID)

#    ORDER BY SH.NAME,SH.DATE_ORDER

#(2)  Group By required on Partner, Product & Salesman (SO)


