# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
from openerp.tools.translate import _
import copy
import math
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
import datetime
import dateutil.relativedelta
from datetime import date, timedelta
import itertools
from lxml import etree
import openerp.addons.decimal_precision as dp
import time
from openerp import workflow


class res_partner(models.Model):
    _inherit = "res.partner"
    AVAILABLE_PRIORITIES = [
    ('0', 'Very Low'),
    ('1', 'Low'),
    ('2', 'Normal'),
    ('3', 'High'),
    ('4', 'Very High'),
    ]
    od_industry_id = fields.Many2one('od.partner.industry',string='Industry')
    od_territory_id = fields.Many2one('od.partner.territory',string='Territory')
    child_ids = fields.One2many('res.partner','parent_id',string='Contacts',domain=[('is_company', '=', False)])
    affiliate_ids = fields.One2many('res.partner','parent_id',string='Affiliates',domain=[('is_company', '=', True)])
    od_direct_no = fields.Char(string='Direct Number')
    od_extn = fields.Char(string='Extension')
    priority = fields.Selection(AVAILABLE_PRIORITIES, string='Priority')
# class organization_chart(models.Model):
#     _name = "org.chart"
#     partner = fields.Many2one('res.partner','Partner')
#     manager_name = fields.Many2one('res.partner','Top Manager')
#     title = fields.Char(string="Title")
#     color = fields.Char(string='Attitude')
#    
# 
# class od_top_opportunity(models.Model):
#     _name = "od.top.opportunity" 
#     name = fields.Char(string="Opportunity Name") 
#     partner_id = fields.Many2one('res.partner',string='Partner')
#     product_id = fields.Many2one('product.product',string='Product')
#     expected_value = fields.Float(string="Expected Value")
#     date_close = fields.Date(string="Closing Date")
#     competitors = fields.Char("Competitors")



class od_partner_industry(models.Model):
    _name = "od.partner.industry"
    name = fields.Char(string='Name',required="1")
    notes = fields.Text(string='Remarks')
class od_partner_territory(models.Model):
    _name = "od.partner.territory"
    name = fields.Char(string='Name',required="1")
    country_id = fields.Many2one('res.country','Country',required="1")
    notes = fields.Text(string='Remarks')

