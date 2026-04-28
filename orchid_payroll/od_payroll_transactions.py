# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from datetime import datetime
from dateutil.relativedelta import relativedelta
import calendar


class od_payroll_transactions(osv.osv):
    _name = "od.payroll.transactions"
    _description = "Payroll Transactions"

    def loans_confirm(self, cr, uid, ids, context=None):
        for obj in self.browse(cr,uid,ids,context):
            for line in obj.payroll_transactions_line:
                self.pool.get('od.payroll.transactions.line').write(cr,uid,[line.id],{'state':'confirm'},context)

        return self.write(cr, uid, ids, {'state': 'confirm'}, context=context)



    def loans_refuse(self, cr, uid, ids, context=None):
        for obj in self.browse(cr,uid,ids,context):
            for line in obj.payroll_transactions_line:
                self.pool.get('od.payroll.transactions.line').write(cr,uid,[line.id],{'state':'cancelled'},context)

        return self.write(cr, uid, ids, {'state': 'cancelled'}, context=context)
    def loans_set_draft(self, cr, uid, ids, context=None):
        for obj in self.browse(cr,uid,ids,context):
            for line in obj.payroll_transactions_line:
                self.pool.get('od.payroll.transactions.line').write(cr,uid,[line.id],{'state':'draft'},context)

        return self.write(cr, uid, ids, {'state': 'draft'}, context=context)
    def loans_accept(self, cr, uid, ids, context=None):
        for obj in self.browse(cr,uid,ids,context):
            for line in obj.payroll_transactions_line:
                self.pool.get('od.payroll.transactions.line').write(cr,uid,[line.id],{'state':'accepted'},context)
        return self.write(cr, uid, ids, {'state': 'accepted'}, context=context)

    def loans_canceled(self, cr, uid, ids, context=None):
        for obj in self.browse(cr,uid,ids,context):
            for line in obj.payroll_transactions_line:
                self.pool.get('od.payroll.transactions.line').write(cr,uid,[line.id],{'state':'cancelled'},context)

        return self.write(cr, uid, ids, {'state': 'cancelled'}, context=context)
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id

    _columns = {
        'name': fields.char('Description', readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
        'company_id': fields.many2one('res.company','Company'),
        'date': fields.date('Date', select=True, readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
        'payroll_transactions_line': fields.one2many('od.payroll.transactions.line', 'payroll_transactions_id', 'Transaction Lines',readonly=True, states={'draft':[('readonly',False)]} ),
        'note': fields.text('Note'),
        'period_id':fields.many2one('account.period','Period',required="1"),
        
        'state': fields.selection([
            ('draft', 'New'),
            ('cancelled', 'Refused'),
            ('confirm', 'Waiting Approval'),
            ('accepted', 'Approved'),
            ('done', 'Waiting Payment'),
            ('paid', 'Paid'),
            ],
            'Status', readonly=True, track_visibility='onchange', copy=False,
            help='When the loans request is created the status is \'Draft\'.\n It is confirmed by the user and request is sent to admin, the status is \'Waiting Confirmation\'.\
            \nIf the admin accepts it, the status is \'Accepted\'.\n If the accounting entries are made for the loans request, the status is \'Waiting Payment\'.'),

    }
    _defaults = {
        
        'date': fields.date.context_today,
        'state': 'draft',
        'company_id': _get_default_company,

    }

class od_payroll_transactions_line(osv.osv):
    _name = "od.payroll.transactions.line"
    _description = "Transaction Line"
    def _get_uom_id(self, cr, uid, context=None):
        result = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'product', 'product_uom_unit')
        return result and result[1] or False

    def onchange_employee_id(self, cr, uid, ids, employee_id,parent, context=None):
        period_id = parent.period_id
 
        return {'value': {'period_id': period_id}}

    def _check_allowance_deduction(self, cr, uid, ids, context=None): 
        obj_fy = self.browse(cr, uid, ids[0], context=context) 
        if obj_fy.allowance >0 and obj_fy.deduction >0: 
            return False 
        if obj_fy.allowance <0 and obj_fy.deduction <0: 
            return False

        if obj_fy.allowance <0 or obj_fy.deduction <0: 
            return False
        if obj_fy.allowance ==0 and obj_fy.deduction ==0: 
            return False
        if not obj_fy.product_id:
            return False

        return True 





    _columns = {
        'employee_id':fields.many2one('hr.employee','Employee',required="1"),
        'transaction_note_id': fields.many2one('od.transaction.note','Transaction Note',required=True),
        'payroll_transactions_id': fields.many2one('od.payroll.transactions', 'Payroll Transaction', ondelete='cascade'),
        'period_id':fields.many2one('account.period','Period',required="1"),
        'allowance':fields.float('Allowance'),
        'deduction':fields.float('Deduction'),
        'product_id': fields.many2one('product.template', 'Payroll Item',domain="[('od_payroll_item','=',True),('name','!=','Loan')]",required="1"),
        'uom_id': fields.many2one('product.uom', 'Unit of Measure'),
        'analytic_account': fields.many2one('account.analytic.account','Analytic account'),
        'state': fields.selection([
            ('draft', 'New'),
            ('cancelled', 'Refused'),
            ('confirm', 'Waiting Approval'),
            ('accepted', 'Approved'),
            ('done', 'Waiting Payment'),
            ('paid', 'Paid'),
            ],
            'Status', readonly=True),
        

        }
    _defaults = {
        
        
        'uom_id': _get_uom_id,
        'state': 'draft',
    }
    _constraints = [ 
        (_check_allowance_deduction, 'pls check the lines', ['allowance','deduction','product']) 
    ]
   



   

# vim:loanandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
