# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import fields, osv
class od_stock_empty_location_report(osv.osv):
    _name = "od.stock.empty.location.report"
    _description = "od.stock.empty.location.report"
    _auto = False
    _rec_name = 'location_id'
    _columns = {
        'location_id': fields.many2one('stock.location', 'Location',),
        'complete_name':fields.char('Complete Name')
        
    }




    def _select(self):
        select_str = """
              SELECT ROW_NUMBER () OVER (ORDER BY stock_location.id ) AS id,
             id AS location_id,
             complete_name AS complete_name
             
        """
        return select_str
    def _from(self):
        from_str = """
                stock_location 
        """
        return from_str

    def _group_by(self):
        group_by_str = """
            GROUP BY id,
                    complete_name
        """
        return group_by_str


    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM  %s 
where id not in (select location_id from stock_quant where qty <> 0) and usage = 'internal'
  %s
            )""" % (self._table, self._select(), self._from(), self._group_by()))




