# -*- coding: utf-8 -*-
##############################################################################

from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning

import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta
from operator import itemgetter
import time

class od_closing_inventory_wiz(osv.osv_memory):
    _name = "od.closing.inventory.wiz"
    _description = "Closing Inventory"


    def _get_fiscalyear_start_date(self, cr, uid, context=None):
        if context is None:
            context = {}
        start_date = ''
        now = time.strftime('%Y-%m-%d')
        company_id = False
        ids = context.get('active_ids', [])
        if ids and context.get('active_model') == 'account.account':
            company_id = self.pool.get('account.account').browse(cr, uid, ids[0], context=context).company_id.id
        else:  # use current company id
            company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        domain = [('company_id', '=', company_id), ('date_start', '<', now), ('date_stop', '>', now)]
        fiscalyears = self.pool.get('account.fiscalyear').search(cr, uid, domain, limit=1)
        if fiscalyears:
            fiscalyears = fiscalyears[0]
            
            start_date = self.pool.get('account.fiscalyear').browse(cr,uid,fiscalyears,context).date_start
        return start_date or ''



    def _get_current_date(self, cr, uid, context=None):
        now = datetime.now()
        return str(now) or ''


    
    product_id = fields.Many2one('product.product',string='Product')
    location_id = fields.Many2one('stock.location',domain=[('usage', '=', 'internal')], string='Location')
    from_date = fields.Date(string="From Date",required="1")
    to_date = fields.Date(string="To Date",required="1")
    categ_id = fields.Many2one('product.category', string='Product Category')

    _defaults = {
            'from_date': _get_fiscalyear_start_date,
            'to_date':_get_current_date,
    }

    def pre_print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        return data

    def build_filter(self,cr,uid,ids,context=None):
        data = self.read(cr, uid, ids,['product_id','location_id','from_date','to_date','categ_id'])[0]
        return data

    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = self.build_filter(cr,uid,ids,context=context)
      
        return self.pool['report'].get_action(cr, uid, [], 'orchid_stock_report.report_stock_closing', data=data, context=context)



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
