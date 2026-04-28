# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import fields, osv
class od_quant_move_analysis_view(osv.osv):
    _name = "od.quant.move.analysis.view"
    _description = "od.quant.move.analysis.view"
    _auto = False
    _rec_name = 'move_id'
    _columns = {
        'move_id': fields.many2one('stock.move', 'Stock Move', required=True),
        'location_id': fields.many2one('stock.location', 'Location', required=True),
        'company_id': fields.many2one('res.company', 'Company'),
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'product_categ_id': fields.many2one('product.category', 'Product Category', required=True),
        'quantity': fields.float('Product Quantity'),
        'date': fields.datetime('Operation Date'),
#        'price_unit_on_quant': fields.float('Value'),
        'source': fields.char('Source'),
        'partner_id':fields.many2one('res.partner','Partner'),
        'invoice_state':fields.char('Invoice State'),
        'picking_type_id': fields.many2one('stock.picking.type', 'Document Type'),
        'picking_name':fields.char('Picking'),
        'lot_id': fields.many2one('stock.production.lot', 'Lot'),
        'picking_state':fields.char('Picking State'),
    }
#price_unit_on_quant,
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'od_quant_move_analysis_view')
        cr.execute("""
            CREATE OR REPLACE VIEW od_quant_move_analysis_view AS (
                SELECT MIN(id) as id,
                move_id,
                location_id,
                company_id,
                product_id,
                product_categ_id,
                SUM(quantity) as quantity,
                date,
                
                source,
                partner_id,
                invoice_state,
                picking_state,
                picking_name,
                picking_type_id,
                lot_id
                FROM
                ((SELECT
                    stock_move.id::text || '-' || quant.id::text AS id,
                    quant.id AS quant_id,
                    stock_move.id AS move_id,
                    dest_location.id AS location_id,
                    dest_location.company_id AS company_id,
                    stock_move.product_id AS product_id,
                    product_template.categ_id AS product_categ_id,
                    quant.qty AS quantity,
                    stock_move.date AS date,

                    stock_move.origin AS source,
                    stock_picking.partner_id AS partner_id,
                    stock_picking.invoice_state as invoice_state,
                    stock_picking.state as picking_state,
                    stock_picking.name as picking_name,
                    stock_picking.picking_type_id as picking_type_id,
                    quant.lot_id as lot_id
                FROM
                    stock_quant as quant, stock_quant_move_rel, stock_move
                LEFT JOIN
                   stock_location dest_location ON stock_move.location_dest_id = dest_location.id
                LEFT JOIN
                    stock_location source_location ON stock_move.location_id = source_location.id
                LEFT JOIN
                    product_product ON product_product.id = stock_move.product_id
                LEFT JOIN
                    product_template ON product_template.id = product_product.product_tmpl_id
                LEFT JOIN 
                    stock_picking ON stock_picking.id = stock_move.picking_id
                WHERE stock_move.state = 'done' AND dest_location.usage in ('internal', 'transit') AND stock_quant_move_rel.quant_id = quant.id
                AND stock_quant_move_rel.move_id = stock_move.id AND ((source_location.company_id is null and dest_location.company_id is not null) or
                (source_location.company_id is not null and dest_location.company_id is null) or source_location.company_id != dest_location.company_id)
                ) UNION
                (SELECT
                    '-' || stock_move.id::text || '-' || quant.id::text AS id,
                    quant.id AS quant_id,
                    stock_move.id AS move_id,
                    source_location.id AS location_id,
                    source_location.company_id AS company_id,
                    stock_move.product_id AS product_id,
                    product_template.categ_id AS product_categ_id,
                    - quant.qty AS quantity,
                    stock_move.date AS date,

                    stock_move.origin AS source,
                    stock_picking.partner_id AS partner_id,
                    stock_picking.invoice_state as invoice_state,
                    stock_picking.state as picking_state,
                    stock_picking.name as picking_name,
                    stock_picking.picking_type_id as picking_type_id,
                    quant.lot_id as lot_id
                FROM
                    stock_quant as quant, stock_quant_move_rel, stock_move
                LEFT JOIN
                    stock_location source_location ON stock_move.location_id = source_location.id
                LEFT JOIN
                    stock_location dest_location ON stock_move.location_dest_id = dest_location.id
                LEFT JOIN
                    product_product ON product_product.id = stock_move.product_id
                LEFT JOIN
                    product_template ON product_template.id = product_product.product_tmpl_id
                LEFT JOIN 
                    stock_picking ON stock_picking.id = stock_move.picking_id
                WHERE stock_move.state = 'done' AND source_location.usage in ('internal', 'transit') AND stock_quant_move_rel.quant_id = quant.id
                AND stock_quant_move_rel.move_id = stock_move.id AND ((dest_location.company_id is null and source_location.company_id is not null) or
                (dest_location.company_id is not null and source_location.company_id is null) or dest_location.company_id != source_location.company_id)
                ))
                AS foo
                GROUP BY move_id, location_id, company_id, product_id, product_categ_id, date, source,partner_id,invoice_state,picking_state,picking_name,picking_type_id,lot_id  )""")






















