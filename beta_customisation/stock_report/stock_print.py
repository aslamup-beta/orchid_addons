
# from openerp import tools
from openerp.osv import osv
# from openerp.tools.translate import _
from openerp import models, fields, api
from openerp.exceptions import Warning
from openerp import SUPERUSER_ID
from dateutil.relativedelta import relativedelta
from pprint import pprint
import time
#import datetime
from datetime import date, datetime
import openerp.addons.decimal_precision as dp

class StockPrintWiz(models.TransientModel):
    _name='od.beta.stock.print.wiz'
    
    def od_get_company_id(self):
        return self.env.user.company_id
    
    date_from  =  fields.Date(string='Start Date')
    wiz_line =  fields.One2many('od.beta.stock.inv.data','wiz_id1',string="Wiz Line")
    product_id = fields.Many2one('product.product', 'Product', required=True)
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    
    def _get_lines(self):
        cr = self.env.cr
        cr.execute("""
              SELECT MIN(id) as id,
                move_id,
                location_id,
                company_id,
                product_id,
                product_categ_id,
                SUM(quantity) as quantity,
                date,
                price_unit_on_quant,
                source,
                partner_id,
                reference,
                analytic_id
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
                    quant.cost as price_unit_on_quant,
                    picking.origin AS source,
                    picking.partner_id AS partner_id,
                    picking.name AS reference,
                    picking.od_analytic_id AS analytic_id
                FROM
                    stock_quant as quant, stock_quant_move_rel, stock_move
                LEFT JOIN
                   stock_picking picking ON stock_move.picking_id = picking.id

                LEFT JOIN
                   stock_location dest_location ON stock_move.location_dest_id = dest_location.id
                LEFT JOIN
                    stock_location source_location ON stock_move.location_id = source_location.id
                LEFT JOIN
                    product_product ON product_product.id = stock_move.product_id
                LEFT JOIN
                    product_template ON product_template.id = product_product.product_tmpl_id
                WHERE quant.qty>0 AND stock_move.state = 'done' AND dest_location.usage in ('internal', 'transit') AND stock_quant_move_rel.quant_id = quant.id
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
                    quant.cost as price_unit_on_quant,
                    picking.origin AS source,
                    picking.partner_id AS partner_id,
                    picking.name AS reference,
                    picking.od_analytic_id AS analytic_id

                FROM
                    stock_quant as quant, stock_quant_move_rel, stock_move
                LEFT JOIN
                   stock_picking picking ON stock_move.picking_id = picking.id

                LEFT JOIN
                    stock_location source_location ON stock_move.location_id = source_location.id
                LEFT JOIN
                    stock_location dest_location ON stock_move.location_dest_id = dest_location.id
                LEFT JOIN
                    product_product ON product_product.id = stock_move.product_id
                LEFT JOIN
                    product_template ON product_template.id = product_product.product_tmpl_id
                WHERE quant.qty>0 AND stock_move.state = 'done' AND source_location.usage in ('internal', 'transit') AND stock_quant_move_rel.quant_id = quant.id
                AND stock_quant_move_rel.move_id = stock_move.id AND ((dest_location.company_id is null and source_location.company_id is not null) or
                (dest_location.company_id is not null and source_location.company_id is null) or dest_location.company_id != source_location.company_id)
                ))
                AS foo
                GROUP BY move_id, location_id, company_id, product_id, product_categ_id, date, price_unit_on_quant, source, partner_id, reference, analytic_id
            """)
        
        lines = cr.dictfetchall()
        return lines
    
    def get_data(self):
        result = []
        values = self._get_lines()
        product_id = self.product_id.id
        company_id = self.company_id.id
        res = filter(lambda values: values['product_id'] == product_id and values['company_id'] ==company_id, values)
        for line in res:
            inv_value = line.get('quantity',0.0) * line.get('price_unit_on_quant',0.0)
            result.append((0,0,{
                'move_id': line.get('move_id',False),
                'product_id': line.get('product_id',False),
                'location_id': line.get('location_id',False),
                'product_categ_id': line.get('product_categ_id',False),
                'quantity': line.get('quantity',False),
                'reference': line.get('reference',''),
                'inventory_value': inv_value or 0.0,
                'partner_id': line.get('partner_id',False),
                'date': line.get('date',False),
                'company_id': line.get('company_id',False),
                'analytic_id': line.get('analytic_id',False),
                'source': line.get('source','')
                }))
        return result
                   
    @api.multi
    def print_directly(self):
        data = self.get_data()
        rpt_pool = self.env['od.beta.stock.inv.data']
        vals = {
            'name': "Current Inventory Report",
            'product_id': self.product_id.id,
            'line_ids':data,
            }
        rpt =rpt_pool.create(vals)
        rpt_id =rpt.id
        ctx = self.env.context
        cr = self.env.cr
        uid = self.env.uid
        return self.pool['report'].get_action(cr, uid, [rpt_id], 'report.od_current_stock_inv', context=ctx)
      
class wiz_stock_print_inv_data(models.TransientModel):
    _name = 'od.beta.stock.inv.data'
    
    def _get_today_date(self):
        return datetime.today().strftime('%d-%b-%y')
    
    name = fields.Char()
    line_ids = fields.One2many('od.beta.stock.inv.data.line','wiz_id',string="Wiz Line",readonly=True)
    date = fields.Date(default=_get_today_date)
    wiz_id1 = fields.Many2one('od.beta.stock.print.wiz',string="Wizard")
    product_id = fields.Many2one('product.product', 'Product', required=True)
        
class wiz_stock_print_inv_data_line(models.TransientModel):
    _name = 'od.beta.stock.inv.data.line'
    _order = 'date'
    
    company_id = fields.Many2one('res.company',string="Company")
    wiz_id = fields.Many2one('od.beta.stock.inv.data',string="Wizard")
    move_id= fields.Many2one('stock.move', 'Stock Move', required=True)
    location_id= fields.Many2one('stock.location', 'Location', required=True)
    company_id= fields.Many2one('res.company', 'Company')
    product_id = fields.Many2one('product.product', 'Product', required=True)
    product_categ_id = fields.Many2one('product.category', 'Product Category', required=True)
    quantity = fields.Float('Product Quantity',digits=(16,2))
    date =fields.Datetime('Operation Date')
    price_unit_on_quant = fields.Float('Value',digits=(16,2))
    inventory_value = fields.Float(string="Inventory Value",digits=(16,2))
    source = fields.Char('Source')
    partner_id = fields.Many2one('res.partner', 'Partner')
    reference = fields.Char('Transaction reference')
    analytic_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    
