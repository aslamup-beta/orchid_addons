from openerp import models, fields, api, _

class stock_production_lot(models.Model):
    _inherit ='stock.production.lot'
    def od_get_company_id(self):
        return self.env.user.company_id
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    od_applicable = fields.Many2one('product.product',string='Applicable To')
    od_serial = fields.Many2one('stock.production.lot',string='Serial No')
    od_supply_by = fields.Selection([('beta','Beta'),('other','Other')],string='Supply By')
    