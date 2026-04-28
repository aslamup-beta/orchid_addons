# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import fields, osv

class od_stock_move_quantity_analysis(osv.osv):
    _name = "od.stock.move.quantity.analysis"
    _description = "od.stock.move.quantity.analysis"
    _auto = False
    _rec_name = 'product_id'

    _columns = {

        'date':fields.datetime('Date'),
        'company_id':fields.many2one('res.company','Company'),
        'name':fields.char('Name'),
        'state':fields.selection([
            ("invoiced", "Invoiced"),
            ("2binvoiced", "To Be Invoiced"),
            ("none", "Not Applicable")], "Invoice Status",),

        'origin':fields.char('Origin'),
        'warehouse_id':fields.many2one('stock.warehouse','Warehouse'),
        'product_id':fields.many2one('product.product','Product'),
        'incoming_qty':fields.float('Incoming Qty'),
        'outgoing_qty':fields.float('Outgoing Qty'),
        'transfer':fields.float('Transfer'),
        'transfer_in':fields.float('Transfer In'),
        'transfer_out':fields.float('Transfer Out'),
        'qty':fields.float('Qty'),

        'location_id': fields.many2one('stock.location', 'Source Location'),
        'location_dest_id':fields.many2one('stock.location', 'Destination Location'),

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


#        
        
    }
##stock_pack_operation.product_qty as product_qty,
##stock_move.price_unit as cost_per_unit,

    def _select(self):
        select_str = """
 SELECT row_number() OVER () AS id,
    foo.date as date,
    foo.company_id as company_id,
    foo.name as name,
    foo.origin as origin,
    foo.warehouse_id as warehouse_id,
    foo.product_id as product_id,
    foo.incoming_qty as incoming_qty,
    foo.outgoing_qty as outgoing_qty,
    foo.transfer_in as transfer_in,
    foo.transfer_out as transfer_out,
    foo.transfer as transfer,
    foo.qty as qty,
    foo.location_id as location_id,
    foo.location_dest_id as location_dest_id,
    foo.state as state,
    foo.code as code,
    foo.document_type,
    foo.source_usage,
    foo.dest_usage
        """
        return select_str

    def _from(self):
        from_str = """
        (SELECT row_number() OVER (ORDER BY stock_move.id) AS id,
            stock_move.date,
            stock_move.company_id,
      
            stock_picking.name,
            stock_move.origin,
            destination_loc.location_id AS warehouse_id,
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
                END AS qty,
            stock_move.location_dest_id,
            stock_move.location_id,
            stock_move.invoice_state AS state,
            stock_picking_type.name AS document_type,
            source_loc.usage AS source_usage,
            destination_loc.usage AS dest_usage
           FROM (((((((stock_move
             LEFT JOIN stock_picking ON ((stock_move.picking_id = stock_picking.id)))
             LEFT JOIN stock_picking_type ON ((stock_picking.picking_type_id = stock_picking_type.id)))
             LEFT JOIN stock_location source_loc ON ((stock_move.location_id = source_loc.id)))
             LEFT JOIN stock_location destination_loc ON ((stock_move.location_dest_id = destination_loc.id)))
             LEFT JOIN product_product pdt ON ((stock_move.product_id = pdt.id)))
        
)
            
)
          WHERE ((stock_move.state)::text = 'done'::text)
        UNION
         SELECT row_number() OVER (ORDER BY stock_move.id) AS id,
            stock_move.date,
            stock_move.company_id,
        
            stock_picking.name,
            stock_move.origin,
            source_loc.location_id AS warehouse_id,
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
                END AS qty,
            stock_move.location_id,
            stock_move.location_dest_id,
            stock_move.invoice_state AS state,
            stock_picking_type.name AS document_type,
            source_loc.usage AS source_usage,
            destination_loc.usage AS dest_usage
           FROM (((((((stock_move
             LEFT JOIN stock_picking ON ((stock_move.picking_id = stock_picking.id)))
             LEFT JOIN stock_picking_type ON ((stock_picking.picking_type_id = stock_picking_type.id)))
             LEFT JOIN stock_location source_loc ON ((stock_move.location_id = source_loc.id)))
             LEFT JOIN stock_location destination_loc ON ((stock_move.location_dest_id = destination_loc.id)))
             LEFT JOIN product_product pdt ON ((stock_move.product_id = pdt.id)))
            
)
            
)
          WHERE ((stock_move.state)::text = 'done'::text)) foo
  WHERE (foo.warehouse_id IN ( SELECT stock_location.id
           FROM stock_location
          WHERE (stock_location.location_id = 1))

        ) 
        """
        return from_str

    def _group_by(self):
        group_by_str = """

        """
        return group_by_str


    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        tools.sql.drop_view_if_exists(cr, 'od_stock_move_quantity_analysis')

        cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM  %s 


  %s
            )""" % (self._table, self._select(), self._from(), self._group_by()))
