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
from openerp import tools, models, api
from itertools import groupby

from openerp.osv import osv
from openerp.tools.translate import _


class CrmLead(models.Model):
    _inherit = "crm.lead"

    opp_warning = fields.Text('Customer Warning Message', compute='_compute_opp_warning')
    opp_warn_flag = fields.Boolean('Customer Warning Flag')
    etimad_summary_line = fields.One2many('etimad.summary', 'crm_id', strint="Etimad Summary")

    @api.one
    @api.depends('opp_warn_flag', 'partner_id')
    def _compute_opp_warning(self):
        if self.partner_id and self.opp_warn_flag:
            self.opp_warning = self.partner_id.opp_warn_msg
        else:
            self.opp_warning = ''

    def on_change_partner_id(self, cr, uid, ids, part, context=None):
        if not part:
            return {'value':{'opp_warn_flag': False}}
        warning = {}
        title = False
        message = False
        partner = self.pool.get('res.partner').browse(cr, uid, part, context=context)
        if partner.opp_warn != 'no-message':
            title = _("Warning for %s") % partner.name
            message = partner.opp_warn_msg
            warning = {
                'title': title,
                'message': message
            }
            if partner.opp_warn == 'block':
                return {'value': {'partner_id': False}, 'warning': warning, 'opp_warning': partner.opp_warn_msg}

        result = super(CrmLead, self).on_change_partner_id(cr, uid, ids, part, context=context)
        if result.get('warning', False):
            warning['title'] = title and title + ' & ' + result['warning']['title'] or result['warning']['title']
            warning['message'] = message and message + ' ' + result['warning']['message'] or result['warning'][
                'message']
        if warning:
            result['warning'] = warning
            if result.get('value'):
                result['value']['opp_warn_flag'] = True
        else:
            if result.get('value'):
                result['value']['opp_warn_flag'] = False
        return result


class EtimadSummary(models.Model):
    _name = 'etimad.summary'

    def od_get_company_id(self):
        return self.env.user.company_id

    company_id = fields.Many2one('res.company', string='Company', default=od_get_company_id)
    crm_id = fields.Many2one('crm.lead', string="Opportunity")
    vendor_id = fields.Many2one('od.product.brand', string="Category")
    product_id = fields.Many2one('product.product', string="Item")
    uom_id = fields.Many2one('product.uom','UoM')
    name = fields.Char(string='Description')
    quantity = fields.Float(string='Quantity')
    specifications = fields.Char(string='Specifications')
    unit_price = fields.Float(string='Unit Price')
    unit_price_in_words = fields.Char(string='Unit Price IN Words')
    discount_percentage = fields.Float(string='Discount Percentage')
    vat_percentage = fields.Float(string='VAT Percentage')
    total_price = fields.Float(string='Total Price')
    total_price_in_words = fields.Char(string='Total Price IN Words')
    country_of_origin = fields.Char(string='Country of Origin')
    certificate_of_origin = fields.Char(string='Certificate of Origin')
    product_of_mandatory_list = fields.Char(string='Product of Mandatory List')
    code = fields.Char(string='Code')
    availability = fields.Boolean(string='Availability')
    attachment = fields.Binary(string='Attachments')
    attach_fname = fields.Char(string='Attachments Name')
