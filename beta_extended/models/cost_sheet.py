# -*- coding: utf-8 -*-

import itertools
from lxml import etree
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp
from openerp.tools import amount_to_text_en
# from . import amount_to_ar
from pprint import pprint
from openerp import tools
from itertools import groupby


class OdCostSheet(models.Model):
    _inherit = "od.cost.sheet"

    show_managed_services = fields.Boolean("Show Managed Services", default=False)
    managed_services_line = fields.One2many('managed.services', 'cost_sheet_id', strint="Managed Services",
                                            readonly=False, copy=False)

    @api.one
    def btn_approved(self):
        res = super(OdCostSheet, self).btn_approved()
        if self.mat_main_pro_line:
            for line in self.mat_main_pro_line:
                if line.part_no.is_renewal_required:
                    self.managed_services_line = [
                        {'product_id': line.part_no.id, 'description': line.name, 'product_qty': line.qty}]
                    self.write({'show_managed_services': True})

    def ms_subscription_dates_entry_reminder(self, cr, uid, context=None):
        today = date.today()
        context = dict(context or {})
        cost_sheet_ids = self.pool['od.cost.sheet'].search(cr, uid, [('state', '=', 'done'),
                                                                     ('show_managed_services', '=', True)],
                                                           context=context)
        cost_sheets = self.pool['od.cost.sheet'].browse(cr, uid, cost_sheet_ids, context=context)
        for sheet in cost_sheets:
            template_id = self.pool['email.template'].browse(cr, uid, 402)[0]
            if sheet.company_id.id == 6:
                template_id = self.pool['email.template'].browse(cr, uid, 403)[0]
            sheet_approved_date = datetime.strptime(sheet.approved_date, "%Y-%m-%d %H:%M:%S").date()
            date_after_7_day_of_approval = sheet_approved_date + relativedelta(days=7)
            if today >= date_after_7_day_of_approval:
                if sheet.managed_services_line:
                    send_reminder = False
                    for ms_line in sheet.managed_services_line:
                        if not ms_line.start_date or not ms_line.end_date:
                            send_reminder = True
                    if send_reminder:
                        self.pool.get('email.template').send_mail(cr, uid, template_id.id, sheet.id,
                                                                  force_send=True, context=context)
        return True

    def ms_subscription_expiry_reminder(self, cr, uid, context=None):
        today = date.today()
        context = dict(context or {})
        cost_sheet_ids = self.pool['od.cost.sheet'].search(cr, uid, [('state', '=', 'done'),
                                                                     ('show_managed_services', '=', True)],
                                                           context=context)
        cost_sheets = self.pool['od.cost.sheet'].browse(cr, uid, cost_sheet_ids, context=context)
        for sheet in cost_sheets:
            if sheet.managed_services_line:
                send_monthly_reminder = False
                send_weekly_reminder = False
                send_same_day_reminder = False
                for ms_line in sheet.managed_services_line:
                    if ms_line.end_date:
                        ms_line_end_date = datetime.strptime(ms_line.end_date, "%Y-%m-%d %H:%M:%S").date()
                        one_month_before_day_of_expiry = ms_line_end_date - relativedelta(days=30)
                        if today == one_month_before_day_of_expiry:
                            send_monthly_reminder = True
                        seven_day_before_day_of_expiry = ms_line_end_date - relativedelta(days=7)
                        if today == seven_day_before_day_of_expiry:
                            send_weekly_reminder = True
                        same_day_of_expiry = ms_line_end_date
                        if today == same_day_of_expiry:
                            send_same_day_reminder = True
                if send_monthly_reminder:
                    template_id = self.pool['email.template'].browse(cr, uid, 404)[0]
                    if sheet.company_id.id == 6:
                        template_id = self.pool['email.template'].browse(cr, uid, 405)[0]
                    self.pool.get('email.template').send_mail(cr, uid, template_id.id, sheet.id,
                                                              force_send=True, context=context)
                if send_weekly_reminder:
                    template_id = self.pool['email.template'].browse(cr, uid, 406)[0]
                    if sheet.company_id.id == 6:
                        template_id = self.pool['email.template'].browse(cr, uid, 407)[0]
                    self.pool.get('email.template').send_mail(cr, uid, template_id.id, sheet.id,
                                                              force_send=True, context=context)
                if send_same_day_reminder:
                    template_id = self.pool['email.template'].browse(cr, uid, 408)[0]
                    if sheet.company_id.id == 6:
                        template_id = self.pool['email.template'].browse(cr, uid, 409)[0]
                    self.pool.get('email.template').send_mail(cr, uid, template_id.id, sheet.id,
                                                              force_send=True, context=context)

        return True


class ManagedServices(models.Model):
    _name = 'managed.services'

    def od_get_company_id(self):
        return self.env.user.company_id

    company_id = fields.Many2one('res.company', string='Company', default=od_get_company_id)
    cost_sheet_id = fields.Many2one('od.cost.sheet', string="Cost Sheet")
    product_id = fields.Many2one('product.product', string="Product")
    product_qty = fields.Float(string="Quantity")
    description = fields.Char(string="Description")
    start_date = fields.Datetime(string="Start Date")
    end_date = fields.Datetime(string="End Date")

class od_cost_summary_weight(models.Model):
    _inherit = 'od.cost.summary.group.weight'

    presales_id = fields.Many2one('res.users',string='Solution Architect')

class od_cost_original_summary_weight(models.Model):
    _inherit = 'od.cost.original.summary.group.weight'

    presales_id = fields.Many2one('res.users',string='Solution Architect')
