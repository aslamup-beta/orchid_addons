# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import fields, osv
class od_stock_history(osv.osv):
    _name = "od.stock.history"
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
        'cost':fields.float("Cost"),
        'move_type':fields.selection([('purchase','Purchase'),('purchase_return','Purchase Return'),('sale','Sale'),('sale_return','Sale Return'),('internal','Internal Transfer'),
        ('inventory_loss','Inventory Loss'),('inventory_add','Inventory Add'),('others','Others')],string="Type")
                }

    def od_refresh_data(self,cr,cost_method="avg"):
        if cost_method == 'real':
            cr.execute("""
            INSERT INTO
            od_stock_history
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
                quantity,
                cost,
                move_type
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
                foo.quantity,
                foo.cost,
                foo.move_type
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
                            END AS quantity,
                            CASE
                                WHEN (((source_loc.usage)::text <> 'internal'::text) AND ((destination_loc.usage)::text = 'internal'::text)) THEN (odf_get_move_real_cost(stock_move.id))::double precision
                                WHEN (((source_loc.usage)::text = 'internal'::text) AND ((destination_loc.usage)::text <> 'internal'::text)) THEN ((odf_get_move_real_cost(stock_move.id) * ((-1))::numeric))::double precision
                                WHEN (((source_loc.usage)::text = 'internal'::text) AND ((destination_loc.usage)::text = 'internal'::text)) THEN (odf_get_move_real_cost(stock_move.id))::double precision
                                ELSE (0)::double precision
                            END AS cost,
                            CASE
                                WHEN source_loc.id = 8 and  destination_loc.usage = 'internal' THEN 'purchase'
                                WHEN source_loc.usage = 'internal' and  destination_loc.id = 8 THEN 'purchase_return'
                                WHEN source_loc.usage = 'internal' and  destination_loc.id = 9 THEN 'sale'
                                WHEN source_loc.id = 9 and  destination_loc.usage = 'internal' THEN 'sale_return'
                                WHEN source_loc.id = 5 and  destination_loc.usage = 'internal' THEN 'inventory_add'
                                WHEN source_loc.usage = 'internal' and  destination_loc.id = 5 THEN 'inventory_loss'
                                WHEN source_loc.usage = 'internal' and  destination_loc.usage = 'internal' THEN 'Internal'

                                else 'others'
                            END AS move_type

                       FROM ((((((stock_move
                         LEFT JOIN stock_picking ON ((stock_move.picking_id = stock_picking.id)))
                         LEFT JOIN stock_picking_type ON ((stock_picking.picking_type_id = stock_picking_type.id)))
                         LEFT JOIN stock_location source_loc ON ((stock_move.location_id = source_loc.id)))
                         LEFT JOIN stock_location destination_loc ON ((stock_move.location_dest_id = destination_loc.id)))
                         LEFT JOIN product_product pdt ON ((stock_move.product_id = pdt.id)))
                         LEFT JOIN product_template pdt_tmp ON ((pdt.product_tmpl_id = pdt_tmp.id)))
                         WHERE ((stock_move.state)::text = 'done'::text) and stock_move.id not in (select move_id from od_stock_history)
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
                            END AS quantity,
                            CASE
                                WHEN (((source_loc.usage)::text <> 'internal'::text) AND ((destination_loc.usage)::text = 'internal'::text)) THEN (odf_get_move_real_cost(stock_move.id))::double precision
                                WHEN (((source_loc.usage)::text = 'internal'::text) AND ((destination_loc.usage)::text <> 'internal'::text)) THEN ((odf_get_move_real_cost(stock_move.id) * ((-1))::numeric))::double precision
                                WHEN (((source_loc.usage)::text = 'internal'::text) AND ((destination_loc.usage)::text = 'internal'::text)) THEN ((odf_get_move_real_cost(stock_move.id) * ((-1))::numeric))::double precision
                                ELSE (0)::double precision
                            END AS cost,
                            CASE
                                WHEN source_loc.id = 8 and  destination_loc.usage = 'internal' THEN 'purchase'
                                WHEN source_loc.usage = 'internal' and  destination_loc.id = 8 THEN 'purchase_return'
                                WHEN source_loc.usage = 'internal' and  destination_loc.id = 9 THEN 'sale'
                                WHEN source_loc.id = 9 and  destination_loc.usage = 'internal' THEN 'sale_return'
                                WHEN source_loc.id = 5 and  destination_loc.usage = 'internal' THEN 'inventory_add'
                                WHEN source_loc.usage = 'internal' and  destination_loc.id = 5 THEN 'inventory_loss'
                                WHEN source_loc.usage = 'internal' and  destination_loc.usage = 'internal' THEN 'Internal'

                                else 'others'
                            END AS move_type
                       FROM ((((((stock_move
                         LEFT JOIN stock_picking ON ((stock_move.picking_id = stock_picking.id)))
                         LEFT JOIN stock_picking_type ON ((stock_picking.picking_type_id = stock_picking_type.id)))
                         LEFT JOIN stock_location source_loc ON ((stock_move.location_id = source_loc.id)))
                         LEFT JOIN stock_location destination_loc ON ((stock_move.location_dest_id = destination_loc.id)))
                         LEFT JOIN product_product pdt ON ((stock_move.product_id = pdt.id)))
                         LEFT JOIN product_template pdt_tmp ON ((pdt.product_tmpl_id = pdt_tmp.id)))
                     WHERE ((stock_move.state)::text = 'done'::text) and stock_move.id not in (select move_id from od_stock_history))  foo
              WHERE (foo.warehouse_id IN ( SELECT stock_location.id
                       FROM stock_location
                       WHERE stock_location.location_id = 1 ))

                     """)
        else:
            cr.execute("""
            INSERT INTO
            od_stock_history
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
                quantity,
                cost,
                move_type)
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
                foo.quantity,
                foo.cost,
                foo.move_type
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
                                WHEN (((source_loc.usage)::text = 'internal'::text) AND ((destination_loc.usage)::text = 'internal'::text)) THEN 'internal'::character varying
                                WHEN (((source_loc.usage)::text = 'internal'::text) AND ((destination_loc.usage)::text = 'inventory'::text)) THEN 'neg_adj'::character varying
                                WHEN (((source_loc.usage)::text = 'inventory'::text) AND ((destination_loc.usage)::text = 'internal'::text)) THEN 'pos_adj'::character varying
                                ELSE stock_picking_type.code
                            END AS code,
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
                            END AS quantity,
                            CASE
                                WHEN (((source_loc.usage)::text <> 'internal'::text) AND ((destination_loc.usage)::text = 'internal'::text)) THEN (odf_get_move_avg_cost(stock_move.id))::double precision
                                WHEN (((source_loc.usage)::text = 'internal'::text) AND ((destination_loc.usage)::text <> 'internal'::text)) THEN ((odf_get_move_avg_cost(stock_move.id) * ((-1))::numeric))::double precision
                                WHEN (((source_loc.usage)::text = 'internal'::text) AND ((destination_loc.usage)::text = 'internal'::text)) THEN (odf_get_move_avg_cost(stock_move.id))::double precision
                                ELSE (0)::double precision
                            END AS cost,
                            CASE
                                WHEN source_loc.id = 8 and  destination_loc.usage = 'internal' THEN 'purchase'
                                WHEN source_loc.usage = 'internal' and  destination_loc.id = 8 THEN 'purchase_return'
                                WHEN source_loc.usage = 'internal' and  destination_loc.id = 9 THEN 'sale'
                                WHEN source_loc.id = 9 and  destination_loc.usage = 'internal' THEN 'sale_return'
                                WHEN source_loc.id = 5 and  destination_loc.usage = 'internal' THEN 'inventory_add'
                                WHEN source_loc.usage = 'internal' and  destination_loc.id = 5 THEN 'inventory_loss'
                                WHEN source_loc.usage = 'internal' and  destination_loc.usage = 'internal' THEN 'Internal'

                                else 'others'
                            END AS move_type

                       FROM ((((((stock_move
                         LEFT JOIN stock_picking ON ((stock_move.picking_id = stock_picking.id)))
                         LEFT JOIN stock_picking_type ON ((stock_picking.picking_type_id = stock_picking_type.id)))
                         LEFT JOIN stock_location source_loc ON ((stock_move.location_id = source_loc.id)))
                         LEFT JOIN stock_location destination_loc ON ((stock_move.location_dest_id = destination_loc.id)))
                         LEFT JOIN product_product pdt ON ((stock_move.product_id = pdt.id)))
                         LEFT JOIN product_template pdt_tmp ON ((pdt.product_tmpl_id = pdt_tmp.id)))
                       WHERE ((stock_move.state)::text = 'done'::text) and stock_move.id not in (select move_id from od_stock_history)
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
                                WHEN (((source_loc.usage)::text = 'internal'::text) AND ((destination_loc.usage)::text = 'internal'::text)) THEN 'internal'::character varying
                                WHEN (((source_loc.usage)::text = 'internal'::text) AND ((destination_loc.usage)::text = 'inventory'::text)) THEN 'neg_adj'::character varying
                                WHEN (((source_loc.usage)::text = 'inventory'::text) AND ((destination_loc.usage)::text = 'internal'::text)) THEN 'pos_adj'::character varying
                                ELSE stock_picking_type.code
                            END AS code,
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
                            END AS quantity,
                            CASE
                                WHEN (((source_loc.usage)::text <> 'internal'::text) AND ((destination_loc.usage)::text = 'internal'::text)) THEN (odf_get_move_avg_cost(stock_move.id))::double precision
                                WHEN (((source_loc.usage)::text = 'internal'::text) AND ((destination_loc.usage)::text <> 'internal'::text)) THEN ((odf_get_move_avg_cost(stock_move.id) * ((-1))::numeric))::double precision
                                WHEN (((source_loc.usage)::text = 'internal'::text) AND ((destination_loc.usage)::text = 'internal'::text)) THEN ((odf_get_move_avg_cost(stock_move.id) * ((-1))::numeric))::double precision
                                ELSE (0)::double precision
                            END AS cost,
                            CASE
                                WHEN source_loc.id = 8 and  destination_loc.usage = 'internal' THEN 'purchase'
                                WHEN source_loc.usage = 'internal' and  destination_loc.id = 8 THEN 'purchase_return'
                                WHEN source_loc.usage = 'internal' and  destination_loc.id = 9 THEN 'sale'
                                WHEN source_loc.id = 9 and  destination_loc.usage = 'internal' THEN 'sale_return'
                                WHEN source_loc.id = 5 and  destination_loc.usage = 'internal' THEN 'inventory_add'
                                WHEN source_loc.usage = 'internal' and  destination_loc.id = 5 THEN 'inventory_loss'
                                WHEN source_loc.usage = 'internal' and  destination_loc.usage = 'internal' THEN 'Internal'

                                else 'others'
                            END AS move_type
                       FROM ((((((stock_move
                         LEFT JOIN stock_picking ON ((stock_move.picking_id = stock_picking.id)))
                         LEFT JOIN stock_picking_type ON ((stock_picking.picking_type_id = stock_picking_type.id)))
                         LEFT JOIN stock_location source_loc ON ((stock_move.location_id = source_loc.id)))
                         LEFT JOIN stock_location destination_loc ON ((stock_move.location_dest_id = destination_loc.id)))
                         LEFT JOIN product_product pdt ON ((stock_move.product_id = pdt.id)))
                         LEFT JOIN product_template pdt_tmp ON ((pdt.product_tmpl_id = pdt_tmp.id)))
                      WHERE ((stock_move.state)::text = 'done'::text) and stock_move.id not in (select move_id from od_stock_history))  foo
              WHERE (foo.warehouse_id IN ( SELECT stock_location.id
                       FROM stock_location
                       WHERE stock_location.location_id = 1 ))

                     """)
