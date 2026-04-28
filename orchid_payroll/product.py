# -*- coding: utf-8 -*-
import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp.osv import fields, osv
from openerp.tools.translate import _


class product_template(osv.osv):
    _inherit = 'product.template'
    
    _columns = {
        'od_payroll_item':fields.boolean('Payroll Item'),
    }

    def unlink(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
       
        for rec in self.browse(cr, uid, ids, context=context):
            product_tmpl_ids_in_loan_line = self.pool.get('od.hr.loans.line').search(cr,uid,[('product_id','=',rec.id)])
            product_tmpl_ids_in_transaction_line = self.pool.get('od.payroll.transactions.line').search(cr,uid,[('product_id','=',rec.id)])
            if product_tmpl_ids_in_loan_line or product_tmpl_ids_in_transaction_line:
                raise osv.except_osv(_('Warning!'),_('you cant delete,it is used in some other records'))
                
        return super(product_template, self).unlink(cr, uid, ids, context=context)