# -*- coding: utf-8 -*-

import itertools
from lxml import etree

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp
from openerp.tools import amount_to_text_en
# from . import amount_to_ar
from pprint import pprint
from openerp import tools
from itertools import groupby

from openerp.tools.translate import _
from openerp import models, fields, api
from datetime import date, timedelta, datetime


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"

    customer_id = fields.Many2one('res.partner', string="Customer")
    supplier_id = fields.Many2one('res.partner', string="Supplier")
    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account")

    @api.onchange('name')
    def onchange_payment_term(self):
        for rec in self:
            if rec.name:
                rec.ref = rec.name


class StockPackOperation(models.Model):
    _inherit = "stock.pack.operation"

    lot_start_date = fields.Datetime(string="Start Date", related="lot_id.use_date")
    lot_end_date = fields.Datetime(string="End Date", related="lot_id.life_date")
    # customer_id = fields.Many2one('res.partner', string="Customer",related="lot_id.life_date")
    # supplier_id = fields.Many2one('res.partner', string="Supplier",related="lot_id.life_date")
    # analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account",related="lot_id.life_date")


class stock_transfer_details(models.TransientModel):
    _inherit = "stock.transfer_details"

    customer_id = fields.Many2one('res.partner', string="Customer")
    supplier_id = fields.Many2one('res.partner', string="Supplier")
    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account")


    def default_get(self, cr, uid, fields, context=None):
        print("1111111111111111111")
        if context is None: context = {}
        res = super(stock_transfer_details, self).default_get(cr, uid, fields, context=context)
        print("222222222222222222222222")
        picking_ids = context.get('active_ids', [])
        active_model = context.get('active_model')

        if not picking_ids or len(picking_ids) != 1:
            # Partial Picking Processing may only be done for one picking at a time
            return res
        assert active_model in ('stock.picking'), 'Bad context propagation'
        picking_id, = picking_ids
        picking = self.pool.get('stock.picking').browse(cr, uid, picking_id, context=context)
        print("picking", picking)
        items = []
        packs = []
        if not picking.pack_operation_ids:
            picking.do_prepare_partial()
        for op in picking.pack_operation_ids:
            item = {
                'packop_id': op.id,
                'product_id': op.product_id.id,
                'product_uom_id': op.product_uom_id.id,
                'quantity': op.product_qty,
                'package_id': op.package_id.id,
                'lot_id': op.lot_id.id,
                'sourceloc_id': op.location_id.id,
                'destinationloc_id': op.location_dest_id.id,
                'result_package_id': op.result_package_id.id,
                'date': op.date,
                'owner_id': op.owner_id.id,
                'customer_id': picking.od_customer_id.id if picking.od_customer_id else False,
                'supplier_id': picking.partner_id.id if picking.partner_id else False,
                'analytic_account_id': picking.od_analytic_id.id if picking.od_analytic_id else False,
            }
            if op.product_id:
                items.append(item)
            elif op.package_id:
                packs.append(item)
        res.update(item_ids=items)
        res.update(packop_ids=packs)
        return res


class stock_transfer_details_items(models.TransientModel):
    _inherit = "stock.transfer_details_items"

    customer_id = fields.Many2one('res.partner', string="Customer")
    supplier_id = fields.Many2one('res.partner', string="Supplier")
    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account")
