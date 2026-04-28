# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import fields, osv
class od_stock_move_analysis_for_closing_report(osv.osv):
    _name = "od.stock.move.analysis.for.closing.report"
    _description = "od.stock.move.analysis.for.closing.report"
    _auto = False
    _rec_name = 'product_id'
    _columns = {
        'product_id':fields.many2one('product.product','Product'),
        'location_id': fields.many2one('stock.location', 'Source Location',),
        'location_dest_id': fields.many2one('stock.location', 'Destination Location',),
        'date':fields.date('Date'),
        'in_qty':fields.float('In Qty'),
        'out_qty':fields.float('Out Qty'),
        
    }
    def _select(self):
        select_str = """
              SELECT ROW_NUMBER () OVER (ORDER BY od_stock_move_quantity_analysis.id ) AS id,
product_id as product_id,CAST(date AS date) as date,location_id as location_id,location_dest_id as location_dest_id,incoming_qty as in_qty,outgoing_qty as out_qty

        """
        return select_str
    def _from(self):
        from_str = """
                od_stock_move_quantity_analysis 
        """
        return from_str



    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM  %s 
            )""" % (self._table, self._select(), self._from()))




