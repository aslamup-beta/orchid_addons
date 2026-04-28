# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import fields, osv
from openerp.tools.translate import _
class od_location_stock_view(osv.osv):
    _name = "od.location.stock.view"
    _description = "od.location.stock.view"
    _auto = False
    _rec_name = 'product_id'


    _columns = {
        'product_id':fields.many2one('product.product','Product'),
        'stock':fields.float('Stock'),
        'location_id': fields.many2one('stock.location', 'Warehouse', required=True, select=True),
        'quant_location_id':fields.many2one('stock.location', 'Location', required=True, select=True),
        'value':fields.float('Value'),
        'company_id':fields.many2one('res.company','Company'),
        'categ_id':fields.many2one('product.category','Product Category'),
        'lot_id':fields.many2one('stock.production.lot','Lot')


    }

    def get_cost_method(self,cr):
        parameter_obj = self.pool.get('ir.config_parameter')
        parameter_ids = parameter_obj.search(cr,1,[('key', '=', 'cost_method')])

        if not parameter_ids:
            return 'SUM(stock_quant.qty * odf_get_product_average_price(stock_quant.company_id,stock_quant.product_id)) as value'
            # raise osv.except_osv(_('Settings Warning!'),_('configure cost_method'))

        parameter_data = parameter_obj.browse(cr,1,parameter_ids).value
        if parameter_data == 'real':
            return 'SUM(stock_quant.qty *stock_quant.cost) as value'
        else:
            return 'SUM(stock_quant.qty * odf_get_product_average_price(stock_quant.company_id,stock_quant.product_id)) as value'


    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute(
        """
         CREATE OR REPLACE FUNCTION odf_get_product_average_price(integer,integer) RETURNS numeric AS $$
         select p.value_float ::decimal(16,3) as cost from ir_property  p
         left join product_product pdt ON pdt.product_tmpl_id = trim('product.template,' from p.res_id)::integer
         where name='standard_price' and p.res_id like 'product.template,%'
         and p.company_id = $1 and pdt.id = $2
         $$ LANGUAGE SQL;
        """
        )
        cr.execute(
        """
        CREATE OR REPLACE FUNCTION odf_get_move_avg_cost(integer) RETURNS numeric AS $$
         select coalesce((hist.cost*mv.product_qty),0)::decimal(16,3) from stock_move mv
         left join product_product pdt ON (mv.product_id=pdt.id)
         left join product_price_history hist ON (hist.product_template_id = pdt.product_tmpl_id and hist.datetime <= mv.date)
         where mv.id = $1 order by hist.datetime desc 
        $$ LANGUAGE SQL;
        """
        )
        cr.execute(
        """
        CREATE OR REPLACE FUNCTION odf_get_move_real_cost(integer) RETURNS numeric AS $$
         select coalesce(sum(qnt.cost*qnt.qty),0)::decimal(16,3) from stock_quant qnt
         left join stock_quant_move_rel mv_rel ON (mv_rel.quant_id = qnt.id)
         left join stock_move mv on (mv_rel.move_id = mv.id)
         where mv.id = $1
        $$ LANGUAGE SQL;
        """
        )                
        cr.execute(
        """
        CREATE or REPLACE VIEW %s as
        SELECT ROW_NUMBER () OVER (ORDER BY stock_location.location_id ) AS id,
             stock_location.location_id AS location_id,
             stock_quant.location_id AS quant_location_id,
             stock_quant.company_id AS company_id,
             product_template.categ_id as categ_id,
             stock_quant.product_id AS product_id,
             stock_quant.lot_id AS lot_id,
             SUM (stock_quant.qty) AS stock, %s
               from stock_quant
            INNER JOIN stock_location ON stock_quant.location_id = stock_location.id
	        LEFT JOIN product_product pdt ON (stock_quant.product_id = pdt.id)
            LEFT JOIN product_template on (pdt.product_tmpl_id = product_template.id )
            WHERE
            stock_location.usage = 'internal' 
                   GROUP BY stock_location.location_id,
                    stock_quant.location_id,
                   stock_quant.product_id,
                    stock_quant.lot_id,
                    product_template.categ_id,
                   stock_quant.company_id

        """ %(self._table, self.get_cost_method(cr))
        )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

    
