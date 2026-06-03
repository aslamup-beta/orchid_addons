import datetime
from openerp import models, fields, api, _
from datetime import date
from openerp.exceptions import Warning
from openerp import SUPERUSER_ID
from dateutil.relativedelta import relativedelta
import openerp.addons.decimal_precision as dp


class od_cost_sheet(models.Model):
    _inherit = 'od.cost.sheet'

    all_brand_weight_line = fields.One2many('od.cost.all.brand.weight', 'cost_sheet_id', string='All Brand Weight',
                                            readonly=True)

    # Override the function to create new Sale In brand report include brands in all tabs
    def get_all_brand_vals(self):
        trn_included = self.included_trn_in_quotation
        mat_incuded = self.included_in_quotation
        ps_incuded = self.included_bim_in_quotation
        is_incuded = self.included_info_sec_in_quotation
        mc_incuded = self.included_bmn_in_quotation
        disc = (abs(self.special_discount) / (self.sum_tot_sale or 1.0)) * 100.0
        res = []
        all_brand_cost = 0.0
        for line in self.mat_main_pro_line:
            if mat_incuded:
                res.append({'manufacture_id': line.manufacture_id and line.manufacture_id.id or False,
                            'total_sale': line.line_price,
                            'total_sale_after_disc': line.line_price * (1 - (disc / 100.0)),
                            'total_cost': line.line_cost_local_currency,
                            'sup_cost': line.discounted_total_supplier_currency,
                            })
                all_brand_cost += line.line_cost_local_currency
        for line in self.trn_customer_training_line:
            if trn_included:
                res.append({'manufacture_id': line.manufacture_id and line.manufacture_id.id or False,
                            'total_sale': line.line_price,
                            'total_sale_after_disc': line.line_price * (1 - (disc / 100.0)),
                            'total_cost': line.line_cost_local_currency,
                            'sup_cost': line.discounted_total_supplier_currency,
                            # 'sup_cost':0.0 Commented by aslam and above line added by aslam because it is manually making zero instead of supplier cost currency
                            })
                all_brand_cost += line.line_cost_local_currency
        for ps_line in self.ps_vendor_line:
            if ps_incuded:
                res.append({'manufacture_id': ps_line.manufacture_id and ps_line.manufacture_id.id or False,
                            'total_sale': ps_line.line_price,
                            'total_sale_after_disc': ps_line.line_price * (1 - (disc / 100.0)),
                            'total_cost': ps_line.line_cost_local_currency,
                            'sup_cost': ps_line.discounted_total_supplier_currency,
                            })
                all_brand_cost += ps_line.line_cost_local_currency
        for is_line in self.info_sec_vendor_line:
            if is_incuded:
                res.append({'manufacture_id': is_line.manufacture_id and is_line.manufacture_id.id or False,
                            'total_sale': is_line.line_price,
                            'total_sale_after_disc': is_line.line_price * (1 - (disc / 100.0)),
                            'total_cost': is_line.line_cost_local_currency,
                            'sup_cost': is_line.discounted_total_supplier_currency,
                            })
                all_brand_cost += is_line.line_cost_local_currency
        for is_line in self.info_sec_vendor_line:
            if is_incuded:
                res.append({'manufacture_id': is_line.manufacture_id and is_line.manufacture_id.id or False,
                            'total_sale': is_line.line_price,
                            'total_sale_after_disc': is_line.line_price * (1 - (disc / 100.0)),
                            'total_cost': is_line.line_cost_local_currency,
                            'sup_cost': is_line.discounted_total_supplier_currency,
                            })
                all_brand_cost += is_line.line_cost_local_currency
        result = self.grouped_brand_weight(res, all_brand_cost)
        return result

    @api.one
    def generate_all_brand_weight(self):
        vals = self.get_all_brand_vals()
        self.all_brand_weight_line.unlink()
        self.all_brand_weight_line = vals

    @api.one
    def update_cost_sheet(self):
        super(od_cost_sheet, self).update_cost_sheet()
        self.generate_all_brand_weight()



class od_cost_all_brand_weight(models.Model):
    _name = 'od.cost.all.brand.weight'
    _order = "item_int ASC"

    @api.one
    @api.depends('total_sale_after_disc', 'total_cost')
    def _compute_vals(self):
        total_sale = round(self.total_sale_after_disc)
        total_cost = round(self.total_cost)
        profit = total_sale - total_cost
        self.profit = profit
        all_brand_cost = self.all_brand_cost
        if total_sale:
            self.profit_percent = (profit / (total_sale or 1.0)) * 100
        if all_brand_cost:
            self.weight = (total_cost / (all_brand_cost or 1.0)) * 100

    item_int = fields.Integer(string="Item Seq", default=1)
    cost_sheet_id = fields.Many2one('od.cost.sheet', string='Cost Sheet', ondelete='cascade', )
    manufacture_id = fields.Many2one('od.product.brand', string='Brand')
    total_sale = fields.Float(string="Total Brand Sales", digits=dp.get_precision('Account'))
    total_sale_after_disc = fields.Float(string="Total Brand Sales After Discount", digits=dp.get_precision('Account'))
    total_cost = fields.Float(string="Total Brand cost", digits=dp.get_precision('Account'))
    sup_cost = fields.Float(string="Supplier Discounted Price", digits=dp.get_precision('Account'))
    all_brand_cost = fields.Float(string="All Brand Cost", digits=dp.get_precision('Account'))
    profit = fields.Float(string="Profit", compute="_compute_vals", digits=dp.get_precision('Account'))
    profit_percent = fields.Float(string="Profit %", compute="_compute_vals", digits=dp.get_precision('Account'))
    weight = fields.Float(string="Weight", compute="_compute_vals", digits=dp.get_precision('Account'))
