# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import fields, osv
class od_sales_analysis_view(osv.osv):
    _name = "od.sales.analysis.view"
    _description = "od.sales.analysis.view"
    _auto = False
    _rec_name = 'product_id'
    _columns = {
        'product_id':fields.many2one('product.product',string='Product'),
        'margin':fields.float('Margin'),
        'type':fields.char('Type'),
        'sale':fields.float('Sale'),
        'cost':fields.float('Cost'),
        'profit':fields.float('Profit'),
        'markup':fields.float('Markup'),


    }

    def _select(self):
        select_str = """
  SELECT ROW_NUMBER () OVER (ORDER BY Credit.product_id) AS id,
Credit.product_id as product_id,
CASE WHEN
 INV.type='out_invoice' THEN
  'Sales'
 ELSE
  'Sales Return'
END AS type,


sum (Credit.credit*-1) AS sale,
sum(Debit.debit) AS cost,
(sum(Credit.credit)+sum(Debit.debit))*-1 AS profit,
CASE WHEN
 sum(Credit.credit)<>0 THEN
  ((sum(Credit.credit)+sum(Debit.debit))/sum(Credit.credit))*100
 ELSE
  0
END AS margin,
CASE WHEN
 sum(Debit.debit)<>0 THEN
  ((sum(Credit.credit)+sum(Debit.debit))/sum(Debit.debit))*100*-1
 ELSE
  0
END AS markup

        """
        return select_str



    def _from(self):
        from_str = """
                account_invoice AS INV  
        """
        return from_str

    def _group_by(self):
        group_by_str = """
            GROUP BY 
Credit.product_id,INV.type

        """
        return group_by_str


    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM  %s 
LEFT OUTER JOIN od_account_move_line_debit AS Debit ON Debit.move_id = INV.move_id
LEFT OUTER JOIN od_account_move_line_credit AS Credit ON Credit.move_id = INV.move_id
WHERE
Debit.code = 'expense' OR
Credit.code = 'revenue' AND
INV.type='out_invoice' OR 
INV.type='out_refund'
%s
 
            )""" % (self._table, self._select(), self._from(),self._group_by()))



