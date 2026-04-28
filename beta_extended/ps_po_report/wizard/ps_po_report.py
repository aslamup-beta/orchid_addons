# -*- coding: utf-8 -*-
import time
from openerp import models, fields, api

from pprint import pprint
from datetime import datetime
import openerp.addons.decimal_precision as dp


class PsPoReportWizard(models.TransientModel):
    _name = 'ps.po.rpt.wiz'

    partner_ids = fields.Many2many('res.partner', string="Supplier")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    wiz_line = fields.One2many('ps.po.rpt.data.line', 'org_wiz_id', string="Wiz Line")

    def od_get_company_id(self):
        return self.env.user.company_id

    company_id = fields.Many2one('res.company', string='Company', default=od_get_company_id)

    def get_purchase_orders(self):
        po_obj = self.env['purchase.order']
        company_id = self.env.user.company_id.id
        domain = [('company_id', '=', company_id), ('state', 'not in', ['cancel', 'draft', 'sent', 'bid'])]

        date_start = self.start_date
        date_end = self.end_date
        if date_start:
            domain += [('date_order', '>=', date_start)]
        if date_end:
            domain += [('date_order', '<=', date_end)]

        if self.partner_ids:
            domain += [('partner_id', 'in', self.partner_ids.ids)]

        purchase_orders = po_obj.search(domain)
        return purchase_orders

    def get_data(self):
        # account_id = self.account_id.id
        company_id = self.env.user.company_id.id
        result = []
        purchase_orders = self.get_purchase_orders()
        # moves1 = self.de_duplicate_moves(moves)
        print("purchase_orders", purchase_orders)
        for order in purchase_orders:
            include_po = False
            order_po_sum = 0
            for line in order.order_line:
                if line.product_id.od_pdt_type_id.name == 'Service':
                    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@",
                          line.product_id.od_pdt_type_id.name)
                    if line.product_id.id not in [209917, 264782, 231446, 265264]:
                        currency = order.currency_id
                        company_currency = order.company_id.currency_id
                        if currency != company_currency:
                            ps_total = currency.compute(line.price_subtotal, company_currency, round=False)
                        else:
                            ps_total = line.price_subtotal
                        line_dict = {
                            'order_date': order.date_order,
                            'partner_id': order.partner_id.id,
                            'purchase_id': order.id,
                            'product_id': line.product_id.id,
                            'pdt_description': line.name,
                            'od_pdt_brand_id': line.od_pdt_brand_id.id,
                            'od_product_group_id': line.product_id.od_pdt_group_id.id,
                            'org_wiz_id': self.id,
                            'ps_total': ps_total,
                            'od_division_id': order.od_division_id.id,
                            'od_customer_id': order.od_customer_id.id,
                            'state': order.state,
                        }
                        po_rpt_line = self.env['ps.po.rpt.data.line']
                        line = po_rpt_line.create(line_dict)
                        print("line", line)
                        result.append(line.id)

        return result

    def get_print_data(self):
        # account_id = self.account_id.id
        company_id = self.env.user.company_id.id
        result = []
        purchase_orders = self.get_purchase_orders()
        # moves1 = self.de_duplicate_moves(moves)
        print("purchase_orders", purchase_orders)
        for order in purchase_orders:
            include_po = False
            order_po_sum = 0
            for line in order.order_line:
                if line.product_id.od_pdt_type_id.name == 'Service':
                    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@",
                          line.product_id.od_pdt_type_id.name)
                    currency = order.currency_id
                    company_currency = order.company_id.currency_id
                    if currency != company_currency:
                        ps_total = currency.compute(line.price_subtotal, company_currency, round=False)
                    else:
                        ps_total = line.price_subtotal
                    line_dict = {
                        'order_date': order.date_order,
                        'partner_id': order.partner_id.id,
                        'purchase_id': order.id,
                        'product_id': line.product_id.id,
                        'pdt_description': line.name,
                        'od_pdt_brand_id': line.od_pdt_brand_id.id,
                        'od_product_group_id': line.product_id.od_pdt_group_id.id,
                        'org_wiz_id': self.id,
                        'ps_total': ps_total,
                        'od_division_id': order.od_division_id.id,
                        'od_customer_id': order.od_customer_id.id,
                        'state': order.state,
                    }
                    # po_rpt_line = self.env['ps.po.rpt.data.line']
                    # line = po_rpt_line.create(line_dict)
                    # print("line", line)
                    result.append((0, 0, line_dict))

            # result.append(line.id)
        return result

    @api.multi
    def print_directly(self):
        data = self.get_print_data()
        print("########################### print_directly data", data)
        rpt_temp = 'report.ps_po_rpt'
        rpt_pool = self.env['ps.po.rpt.data']
        currency_id = self.env.user.company_id.currency_id.id
        vals = {
            'name': "PS PO Report",
            'line_ids': data,
            'currency_id': currency_id,
        }

        rpt = rpt_pool.create(vals)
        print("rpt rpt ..................................", rpt)
        rpt_id = rpt.id
        ctx = self.env.context
        cr = self.env.cr
        uid = self.env.uid
        return self.pool['report'].get_action(cr, uid, [rpt_id], rpt_temp, context=ctx)
        # datas = {
        #     'form': data
        # }
        # return self.pool['report'].get_action(cr, uid, [], 'beta_extended.ps_po_custom_report', data=datas, context=ctx)

    @api.multi
    def export_rpt(self):
        model_data = self.env['ir.model.data']
        result = self.get_data()
        print("result", result)
        vw = 'tree_view_ps_po_rpt_data_line'
        #         result = self.get_data()

        tree_view = model_data.get_object_reference('beta_extended', vw)
        # self.wiz_line.unlink()
        # self.write({'wiz_line': result})
        # del (result)
        return {
            'domain': [('id', 'in', result)],
            'name': 'PS PO Report',
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(tree_view and tree_view[1] or False, 'tree')],
            'res_model': 'ps.po.rpt.data.line',
            'type': 'ir.actions.act_window',
        }


class ps_po_rpt_data(models.TransientModel):
    _name = 'ps.po.rpt.data'

    def od_get_currency(self):
        return self.env.uid.company_id.currency_id

    def _get_today_date(self):
        return datetime.today().strftime('%d-%b-%y')

    name = fields.Char()
    line_ids = fields.One2many('ps.po.rpt.data.line', 'wiz_id', string="Wiz Line", readonly=True)
    currency_id = fields.Many2one('res.currency', string='Currency')
    date = fields.Date(default=_get_today_date)

    total = fields.Float(string="Total")


class ps_po_rpt_data_line(models.TransientModel):
    _name = 'ps.po.rpt.data.line'

    def od_get_company_id(self):
        return self.env.user.company_id

    company_id = fields.Many2one('res.company', string='Company', default=od_get_company_id)

    wiz_id = fields.Many2one('ps.po.rpt.data', string="Wizard data")
    org_wiz_id = fields.Many2one('ps.po.rpt.wiz', string="Wizard")
    s_no = fields.Integer(string="S N")
    order_date = fields.Datetime(string='Order Date')
    ps_total = fields.Float(string="Total Excluding VAT")
    pdt_description = fields.Char(string="Description")
    partner_id = fields.Many2one('res.partner', string="Supplier")
    product_id = fields.Many2one('product.product', string="Part Number")
    od_pdt_brand_id = fields.Many2one('od.product.brand', string="Vendor")
    purchase_id = fields.Many2one('purchase.order', string="PO Number")
    od_division_id = fields.Many2one('od.cost.division', string="Technology Unit")
    od_product_group_id = fields.Many2one('od.product.group', string="Unit")
    od_customer_id = fields.Many2one('res.partner', string="End User")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'RFQ'),
        ('bid', 'Bid Received'),
        ('submit', 'Submitted'),
        ('first_approval', 'First Approval'),
        ('second_approval', 'Second Approval'),
        ('confirmed', 'Waiting Approval'),
        ('approved', 'Purchase Confirmed'),
        ('except_picking', 'Shipping Exception'),
        ('except_invoice', 'Invoice Exception'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string="State")

    @api.multi
    def btn_open_po(self):
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'purchase.order',
            'res_id': self.purchase_id and self.purchase_id.id or False,
            'type': 'ir.actions.act_window',
            'target': 'new',

        }
