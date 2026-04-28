# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import fields, osv
class od_stock_history_qty(osv.osv):
    _name = "od.stock.history.qty"
    _columns = {
        'move_id':fields.many2one('stock.move','Stock Move'),
        'date':fields.date('Date'),
        'company_id':fields.many2one('res.company','Company'),
        'picking_id':fields.many2one('stock.picking','Picking'),
        'warehouse_id':fields.many2one('stock.location','Warehouse'),
        'location_id':fields.many2one('stock.location','Source Location'),
        'location_dest_id':fields.many2one('stock.location','Destination Location'),
        'category_id':fields.many2one('product.category','Product Category'),
        'product_id':fields.many2one('product.product','Product'),
        'incoming_qty':fields.float("Incoming Qty"),
        'outgoing_qty':fields.float("Outgoing Qty"),
        'transfer_in':fields.float("Transfer In"),
        'transfer_out':fields.float("Transfer Out"),
        'transfer':fields.float("Transfer"),
        'quantity':fields.float("Quantity"),

                }

    def od_refresh_data(self,cr):
        cr.execute("""
            INSERT INTO
            od_stock_history_qty
                 (move_id,
                date,
                company_id,
                picking_id,
                warehouse_id,
                location_id,
                location_dest_id,
                category_id,
                product_id,
                incoming_qty,
                outgoing_qty,
                transfer_in,
                transfer_out,
                transfer,
                quantity
                )
             SELECT
                foo.move_id,
                foo.date,
                foo.company_id,
                foo.picking_id,
                foo.warehouse_id,
                foo.location_id,
                foo.location_dest_id,
                foo.category_id,
                foo.product_id,
                foo.incoming_qty,
                foo.outgoing_qty,
                foo.transfer_in,
                foo.transfer_out,
                foo.transfer,
                foo.quantity

               FROM ( SELECT
                        stock_move.id AS move_id,
                        stock_move.date,
                        stock_move.company_id,
                        stock_picking.id AS picking_id,
                        destination_loc.location_id AS warehouse_id,
                        stock_move.location_id,
                        stock_move.location_dest_id,
                        pdt_tmp.categ_id as category_id,
                        stock_move.product_id,

                            CASE
                                WHEN (((source_loc.usage)::text <> 'internal'::text) AND ((destination_loc.usage)::text = 'internal'::text)) THEN stock_move.product_qty
                                ELSE (0)::numeric
                            END AS incoming_qty,
                            CASE
                                WHEN (((source_loc.usage)::text = 'internal'::text) AND ((destination_loc.usage)::text <> 'internal'::text)) THEN (stock_move.product_qty * ((-1))::numeric)
                                ELSE (0)::numeric
                            END AS outgoing_qty,
                            CASE
                                WHEN (((source_loc.usage)::text = 'internal'::text) AND ((destination_loc.usage)::text = 'internal'::text)) THEN stock_move.product_qty
                                ELSE (0)::numeric
                            END AS transfer_in,
                            CASE
                                WHEN (((source_loc.usage)::text = 'internal'::text) AND ((destination_loc.usage)::text = 'internal'::text)) THEN (0)::numeric
                                ELSE (0)::numeric
                            END AS transfer_out,
                            CASE
                                WHEN (((source_loc.usage)::text <> 'internal'::text) AND ((destination_loc.usage)::text <> 'internal'::text)) THEN stock_move.product_qty
                                ELSE (0)::numeric
                            END AS transfer,
                            CASE
                                WHEN (((source_loc.usage)::text <> 'internal'::text) AND ((destination_loc.usage)::text = 'internal'::text)) THEN stock_move.product_qty
                                WHEN (((source_loc.usage)::text = 'internal'::text) AND ((destination_loc.usage)::text <> 'internal'::text)) THEN (stock_move.product_qty * ((-1))::numeric)
                                WHEN (((source_loc.usage)::text = 'internal'::text) AND ((destination_loc.usage)::text = 'internal'::text)) THEN stock_move.product_qty
                                ELSE (0)::numeric
                            END AS quantity

                       FROM ((((((stock_move
                         LEFT JOIN stock_picking ON ((stock_move.picking_id = stock_picking.id)))
                         LEFT JOIN stock_picking_type ON ((stock_picking.picking_type_id = stock_picking_type.id)))
                         LEFT JOIN stock_location source_loc ON ((stock_move.location_id = source_loc.id)))
                         LEFT JOIN stock_location destination_loc ON ((stock_move.location_dest_id = destination_loc.id)))
                         LEFT JOIN product_product pdt ON ((stock_move.product_id = pdt.id)))
                         LEFT JOIN product_template pdt_tmp ON ((pdt.product_tmpl_id = pdt_tmp.id)))
                      WHERE ((stock_move.state)::text = 'done'::text) and stock_move.id not in (select move_id from od_stock_history_qty)
                    UNION
                     SELECT
                        stock_move.id AS move_id,
                        stock_move.date,
                        stock_move.company_id,
                        stock_picking.id AS picking_id,
                        source_loc.location_id AS warehouse_id,
                        stock_move.location_id,
                        stock_move.location_dest_id,
                        pdt_tmp.categ_id as category_id,
                        stock_move.product_id,

                            CASE
                                WHEN (((source_loc.usage)::text <> 'internal'::text) AND ((destination_loc.usage)::text = 'internal'::text)) THEN stock_move.product_qty
                                ELSE (0)::numeric
                            END AS incoming_qty,
                            CASE
                                WHEN (((source_loc.usage)::text = 'internal'::text) AND ((destination_loc.usage)::text <> 'internal'::text)) THEN (stock_move.product_qty * ((-1))::numeric)
                                ELSE (0)::numeric
                            END AS outgoing_qty,
                            CASE
                                WHEN (((source_loc.usage)::text = 'internal'::text) AND ((destination_loc.usage)::text = 'internal'::text)) THEN (0)::numeric
                                ELSE (0)::numeric
                            END AS transfer_in,
                            CASE
                                WHEN (((source_loc.usage)::text = 'internal'::text) AND ((destination_loc.usage)::text = 'internal'::text)) THEN (stock_move.product_qty * ((-1))::numeric)
                                ELSE (0)::numeric
                            END AS transfer_out,
                            CASE
                                WHEN (((source_loc.usage)::text <> 'internal'::text) AND ((destination_loc.usage)::text <> 'internal'::text)) THEN stock_move.product_qty
                                ELSE (0)::numeric
                            END AS transfer,
                            CASE
                                WHEN (((source_loc.usage)::text <> 'internal'::text) AND ((destination_loc.usage)::text = 'internal'::text)) THEN stock_move.product_qty
                                WHEN (((source_loc.usage)::text = 'internal'::text) AND ((destination_loc.usage)::text <> 'internal'::text)) THEN (stock_move.product_qty * ((-1))::numeric)
                                WHEN (((source_loc.usage)::text = 'internal'::text) AND ((destination_loc.usage)::text = 'internal'::text)) THEN (stock_move.product_qty * ((-1))::numeric)
                                ELSE (0)::numeric
                            END AS quantity

                       FROM ((((((stock_move
                         LEFT JOIN stock_picking ON ((stock_move.picking_id = stock_picking.id)))
                         LEFT JOIN stock_picking_type ON ((stock_picking.picking_type_id = stock_picking_type.id)))
                         LEFT JOIN stock_location source_loc ON ((stock_move.location_id = source_loc.id)))
                         LEFT JOIN stock_location destination_loc ON ((stock_move.location_dest_id = destination_loc.id)))
                         LEFT JOIN product_product pdt ON ((stock_move.product_id = pdt.id)))
                         LEFT JOIN product_template pdt_tmp ON ((pdt.product_tmpl_id = pdt_tmp.id)))
                     WHERE ((stock_move.state)::text = 'done'::text) and stock_move.id not in (select move_id from od_stock_history_qty))  foo
              WHERE (foo.warehouse_id IN ( SELECT stock_location.id
                       FROM stock_location
                     WHERE stock_location.location_id = 1 ))

                     """)
