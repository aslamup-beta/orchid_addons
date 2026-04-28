# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import fields, osv

class od_stock_move_analysis(osv.osv):
    _name = "od.stock.move.analysis"
    _description = "od.stock.move.analysis"
    _auto = False
    _rec_name = 'product_id'
    _columns = {

        'date':fields.datetime('Date'),
#         'transfer_date':fields.datetime('Transfer Date'),
        'company_id':fields.many2one('res.company','Company'),
        'partner_id':fields.many2one('res.partner','Partner'),
#        'min_date':fields.datetime('Schedule Date'),
        'name':fields.char('Name'),

        'state':fields.selection([
            ("invoiced", "Invoiced"),
            ("2binvoiced", "To Be Invoiced"),
            ("none", "Not Applicable")], "Invoice Status",),

        'origin':fields.char('Origin'),
#        'warehouse_id':fields.many2one('stock.warehouse','Warehouse'),
        'warehouse_id':fields.many2one('stock.location','Warehouse'),
        'product_id':fields.many2one('product.product','Product'),
#        'product_qty':fields.float('Product Qty'),
        'incoming_qty':fields.float('Incoming Qty'),
        'outgoing_qty':fields.float('Outgoing Qty'),
        'transfer':fields.float('Transfer'),
        'transfer_in':fields.float('Transfer In'),
        'transfer_out':fields.float('Transfer Out'),
        'qty':fields.float('Qty'),
#        'cost_per_unit':fields.float('Unit Cost'),
        'cost':fields.float('Cost'),
        #'od_cost':fields.float('Cost'),

        'location_id': fields.many2one('stock.location', 'Source Location'),
        'location_dest_id':fields.many2one('stock.location', 'Destination Location'),

#        'code':fields.char('Type'),
        'code': fields.selection([('internal','Internal'),('outgoing','Outgoing'),('incoming','Incoming'),('neg_adj','Adjustment(-)'),('pos_adj','Adjustment(+)')],'Code'),

        'document_type':fields.char('Document Type'),

        'source_usage': fields.selection([
                        ('supplier', 'Source Loc.Type'),
                        ('view', 'View'),
                        ('internal', 'Internal Location'),
                        ('customer', 'Customer Location'),
                        ('inventory', 'Inventory'),
                        ('procurement', 'Procurement'),
                        ('production', 'Production'),
                        ('transit', 'Transit Location')],'Location Type'),
        'dest_usage': fields.selection([
                        ('supplier', 'Destination Loc. Type'),
                        ('view', 'View'),
                        ('internal', 'Internal Location'),
                        ('customer', 'Customer Location'),
                        ('inventory', 'Inventory'),
                        ('procurement', 'Procurement'),
                        ('production', 'Production'),
                        ('transit', 'Transit Location')],'Location Type'),

        'od_pdt_group_id': fields.many2one('od.product.group','Group'),
        'od_pdt_brand_id': fields.many2one('od.product.brand','Brand'),
        
    }

    def _select(self):
        select_str = """
SELECT row_number() OVER () AS id,
date,
company_id,
partner_id,
name,
origin,
warehouse_id as warehouse_id,
product_id,
od_pdt_group_id,
od_pdt_brand_id,
incoming_qty,
outgoing_qty,
transfer_in,
transfer_out,
transfer,
qty as qty,
cost,

location_id,
location_dest_id,

state,
code,
document_type,
source_usage,
dest_usage 
        """
        return select_str

    def _from(self):
        from_str = """
        (
                SELECT
                        ROW_NUMBER () OVER (ORDER BY stock_move. ID) AS ID,
                        stock_move. DATE,
                        stock_move.company_id,
                        stock_picking.partner_id,
                        stock_picking. NAME,
                        stock_move.origin,
                        destination_loc.location_id AS warehouse_id,
                        stock_move.product_id,
                        pdt_tmp.od_pdt_group_id,
                        pdt_tmp.od_pdt_brand_id,
                        CASE
                WHEN (
                        (
                                (source_loc. USAGE) :: TEXT = 'internal' :: TEXT
                        )
                        AND (
                                (destination_loc. USAGE) :: TEXT = 'internal' :: TEXT
                        )
                ) THEN
                        'internal' :: CHARACTER VARYING
                WHEN (
                        (
                                (source_loc. USAGE) :: TEXT = 'internal' :: TEXT
                        )
                        AND (
                                (destination_loc. USAGE) :: TEXT = 'inventory' :: TEXT
                        )
                ) THEN
                        'neg_adj' :: CHARACTER VARYING
                WHEN (
                        (
                                (source_loc. USAGE) :: TEXT = 'inventory' :: TEXT
                        )
                        AND (
                                (destination_loc. USAGE) :: TEXT = 'internal' :: TEXT
                        )
                ) THEN
                        'pos_adj' :: CHARACTER VARYING
                ELSE
                        stock_picking_type.code
                END AS code,
                CASE
        WHEN (
                (
                        (source_loc. USAGE) :: TEXT <> 'internal' :: TEXT
                )
                AND (
                        (destination_loc. USAGE) :: TEXT = 'internal' :: TEXT
                )
        ) THEN
                stock_move.product_qty
        ELSE
                (0) :: NUMERIC
        END AS incoming_qty,
        CASE
WHEN (
        (
                (source_loc. USAGE) :: TEXT = 'internal' :: TEXT
        )
        AND (
                (destination_loc. USAGE) :: TEXT <> 'internal' :: TEXT
        )
) THEN
        (
                stock_move.product_qty * ((- 1)) :: NUMERIC
        )
ELSE
        (0) :: NUMERIC
END AS outgoing_qty,
 CASE
WHEN (
        (
                (source_loc. USAGE) :: TEXT = 'internal' :: TEXT
        )
        AND (
                (destination_loc. USAGE) :: TEXT = 'internal' :: TEXT
        )
) THEN
        stock_move.product_qty
ELSE
        (0) :: NUMERIC
END AS transfer_in,
 CASE
WHEN (
        (
                (source_loc. USAGE) :: TEXT = 'internal' :: TEXT
        )
        AND (
                (destination_loc. USAGE) :: TEXT = 'internal' :: TEXT
        )
) THEN
        (0) :: NUMERIC
ELSE
        (0) :: NUMERIC
END AS transfer_out,

 CASE
WHEN (
        (
                (source_loc. USAGE) :: TEXT <> 'internal' :: TEXT
        )
        AND (
                (destination_loc. USAGE) :: TEXT <> 'internal' :: TEXT
        )
) THEN
        stock_move.product_qty
ELSE
        (0) :: NUMERIC
END AS transfer,
 CASE
WHEN (
        (
                (source_loc. USAGE) :: TEXT <> 'internal' :: TEXT
        )
        AND (
                (destination_loc. USAGE) :: TEXT = 'internal' :: TEXT
        )
) THEN
        stock_move.product_qty
WHEN (
        (
                (source_loc. USAGE) :: TEXT = 'internal' :: TEXT
        )
        AND (
                (destination_loc. USAGE) :: TEXT <> 'internal' :: TEXT
        )
) THEN
        (
                stock_move.product_qty * ((- 1)) :: NUMERIC
        )
WHEN (
        (
                (source_loc. USAGE) :: TEXT = 'internal' :: TEXT
        )
        AND (
                (destination_loc. USAGE) :: TEXT = 'internal' :: TEXT
        )
) THEN
        stock_move.product_qty
ELSE
        (0) :: NUMERIC
END AS qty,
    CASE
                    WHEN (((source_loc.usage)::text <> 'internal'::text) AND ((destination_loc.usage)::text = 'internal'::text)) THEN ((odf_get_move_avg_cost(stock_move.id))::double precision)
                    WHEN (((source_loc.usage)::text = 'internal'::text) AND ((destination_loc.usage)::text <> 'internal'::text)) THEN (((odf_get_move_avg_cost(stock_move.id)) * (-1))::double precision)
                    WHEN (((source_loc.usage)::text = 'internal'::text) AND ((destination_loc.usage)::text = 'internal'::text)) THEN ((odf_get_move_avg_cost(stock_move.id))::double precision)
                    ELSE (0)::double precision
                END AS cost,

 stock_move.location_dest_id,

 stock_move.location_id,
 stock_move.invoice_state AS STATE,
 stock_picking_type. NAME AS document_type,
 source_loc. USAGE AS source_usage,
 destination_loc. USAGE AS dest_usage
FROM
        (
                (
                        (
                                (
                                        (
                                                (
                                                        (
                                                                stock_move
                                                                LEFT JOIN stock_picking ON (
                                                                        (
                                                                                stock_move.picking_id = stock_picking. ID
                                                                        )
                                                                )
                                                        )
                                                        LEFT JOIN stock_picking_type ON (
                                                                (
                                                                        stock_picking.picking_type_id = stock_picking_type. ID
                                                                )
                                                        )
                                                )
                                                LEFT JOIN stock_location source_loc ON (
                                                        (
                                                                stock_move.location_id = source_loc. ID
                                                        )
                                                )
                                        )
                                        LEFT JOIN stock_location destination_loc ON (
                                                (
                                                        stock_move.location_dest_id = destination_loc. ID
                                                )
                                        )
                                )
                                LEFT JOIN product_product pdt ON ((stock_move.product_id = pdt. ID))
                        )
                        LEFT JOIN product_template pdt_tmp ON (
                                (pdt.product_tmpl_id = pdt_tmp. ID)
                        )
                )
               
        )
WHERE
        (
                (stock_move. STATE) :: TEXT = 'done' :: TEXT
        )
UNION
        SELECT
                ROW_NUMBER () OVER (ORDER BY stock_move. ID) AS ID,
                stock_move. DATE,
                stock_move.company_id,
                stock_picking.partner_id,
                stock_picking. NAME,
                stock_move.origin,
                source_loc.location_id AS warehouse_id,
                stock_move.product_id,
                pdt_tmp.od_pdt_group_id,
                pdt_tmp.od_pdt_brand_id,
                CASE
        WHEN (
                (
                        (source_loc. USAGE) :: TEXT = 'internal' :: TEXT
                )
                AND (
                        (destination_loc. USAGE) :: TEXT = 'internal' :: TEXT
                )
        ) THEN
                'internal' :: CHARACTER VARYING
        WHEN (
                (
                        (source_loc. USAGE) :: TEXT = 'internal' :: TEXT
                )
                AND (
                        (destination_loc. USAGE) :: TEXT = 'inventory' :: TEXT
                )
        ) THEN
                'neg_adj' :: CHARACTER VARYING

        WHEN (
                (
                        (source_loc. USAGE) :: TEXT = 'inventory' :: TEXT
                )
                AND (
                        (destination_loc. USAGE) :: TEXT = 'internal' :: TEXT
                )
        ) THEN
                'pos_adj' :: CHARACTER VARYING

        ELSE
                stock_picking_type.code
        END AS code,
        CASE
WHEN (
        (
                (source_loc. USAGE) :: TEXT <> 'internal' :: TEXT
        )
        AND (
                (destination_loc. USAGE) :: TEXT = 'internal' :: TEXT
        )
) THEN
        stock_move.product_qty
ELSE
        (0) :: NUMERIC
END AS incoming_qty,
 CASE
WHEN (
        (
                (source_loc. USAGE) :: TEXT = 'internal' :: TEXT
        )
        AND (
                (destination_loc. USAGE) :: TEXT <> 'internal' :: TEXT
        )
) THEN
        (
                stock_move.product_qty * ((- 1)) :: NUMERIC
        )
ELSE
        (0) :: NUMERIC
END AS outgoing_qty,
 CASE
WHEN (
        (
                (source_loc. USAGE) :: TEXT = 'internal' :: TEXT
        )
        AND (
                (destination_loc. USAGE) :: TEXT = 'internal' :: TEXT
        )
) THEN
        (0) :: NUMERIC
ELSE
        (0) :: NUMERIC
END AS transfer_in,
 CASE
WHEN (
        (
                (source_loc. USAGE) :: TEXT = 'internal' :: TEXT
        )
        AND (
                (destination_loc. USAGE) :: TEXT = 'internal' :: TEXT
        )
) THEN
        (
                stock_move.product_qty * ((- 1)) :: NUMERIC
        )
ELSE
        (0) :: NUMERIC
END AS transfer_out,
 CASE
WHEN (
        (
                (source_loc. USAGE) :: TEXT <> 'internal' :: TEXT
        )
        AND (
                (destination_loc. USAGE) :: TEXT <> 'internal' :: TEXT
        )
) THEN
        stock_move.product_qty
ELSE
        (0) :: NUMERIC
END AS transfer,
 CASE
WHEN (
        (
                (source_loc. USAGE) :: TEXT <> 'internal' :: TEXT
        )
        AND (
                (destination_loc. USAGE) :: TEXT = 'internal' :: TEXT
        )
) THEN
        stock_move.product_qty
WHEN (
        (
                (source_loc. USAGE) :: TEXT = 'internal' :: TEXT
        )
        AND (
                (destination_loc. USAGE) :: TEXT <> 'internal' :: TEXT
        )
) THEN
        (
                stock_move.product_qty * ((- 1)) :: NUMERIC
        )
WHEN (
        (
                (source_loc. USAGE) :: TEXT = 'internal' :: TEXT
        )
        AND (
                (destination_loc. USAGE) :: TEXT = 'internal' :: TEXT
        )
) THEN
        (
                stock_move.product_qty * ((- 1)) :: NUMERIC
        )
ELSE
        (0) :: NUMERIC
END AS qty,
CASE
                    WHEN (((source_loc.usage)::text <> 'internal'::text) AND ((destination_loc.usage)::text = 'internal'::text)) THEN ((odf_get_move_avg_cost(stock_move.id))::double precision)
                    WHEN (((source_loc.usage)::text = 'internal'::text) AND ((destination_loc.usage)::text <> 'internal'::text)) THEN (((odf_get_move_avg_cost(stock_move.id)) * (-1))::double precision)
                    WHEN (((source_loc.usage)::text = 'internal'::text) AND ((destination_loc.usage)::text = 'internal'::text)) THEN (((odf_get_move_avg_cost(stock_move.id)) * (-1))::double precision)
                    ELSE (0)::double precision
                END AS cost,
 stock_move.location_id,
 stock_move.location_dest_id,
 stock_move.invoice_state AS STATE,
 stock_picking_type. NAME AS document_type,
 source_loc. USAGE AS source_usage,
 destination_loc. USAGE AS dest_usage
FROM
        (
                (
                        (
                                (
                                        (
                                                (
                                                        (
                                                                stock_move
                                                                LEFT JOIN stock_picking ON (
                                                                        (
                                                                                stock_move.picking_id = stock_picking. ID
                                                                        )
                                                                )
                                                        )
                                                        LEFT JOIN stock_picking_type ON (
                                                                (
                                                                        stock_picking.picking_type_id = stock_picking_type. ID
                                                                )
                                                        )
                                                )
                                                LEFT JOIN stock_location source_loc ON (
                                                        (
                                                                stock_move.location_id = source_loc. ID
                                                        )
                                                )
                                        )
                                        LEFT JOIN stock_location destination_loc ON (
                                                (
                                                        stock_move.location_dest_id = destination_loc. ID
                                                )
                                        )
                                )
                                LEFT JOIN product_product pdt ON ((stock_move.product_id = pdt. ID))
                        )
                        LEFT JOIN product_template pdt_tmp ON (
                                (pdt.product_tmpl_id = pdt_tmp. ID)
                        )
                )
              
        )
WHERE
        (
                (stock_move. STATE) :: TEXT = 'done' :: TEXT
        )
        ) foo
WHERE
        (
                foo.warehouse_id IN (
                        SELECT
                                stock_location. ID
                        FROM
                                stock_location
                        WHERE
                                (stock_location.location_id = 1)
                )
        ) 
        """
        return from_str

    def _group_by(self):
        group_by_str = """

        """
        return group_by_str


    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        tools.sql.drop_view_if_exists(cr, 'od_stock_move_analysis')
        cr.execute("""
            create or replace view od_move_quant_cost  as (
                select
                t1.move_id,
(SUM (t1.price_unit_on_quant * t1.quantity))/(CASE SUM(t1.quantity) WHEN 0 THEN 1 ELSE  SUM(t1.quantity) END) as cost 
 from stock_history t1 
 group by t1.move_id)
"""
)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM  %s 


  %s
            )""" % (self._table, self._select(), self._from(), self._group_by()))


