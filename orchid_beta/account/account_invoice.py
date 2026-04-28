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
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import itertools
from lxml import etree

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp

class account_invoice(models.Model):
    _inherit = "account.invoice"
    od_discount = fields.Float(string='Discount',digits= dp.get_precision('Account'))
    od_discount_acc_id = fields.Many2one('account.account', string='Dis. Account', readonly=True, states={'draft': [('readonly', False)]},       help="The account used for write of discount.")
    od_allow_extra_exp = fields.Boolean(string="Allow Extra Expense")
    @api.one
    @api.depends('invoice_line.price_subtotal', 'tax_line.amount','od_discount')
    def _compute_amount(self):
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line) 
        self.amount_tax = sum(line.amount for line in self.tax_line)
        #Added by aslam: to adjust tax amount while applying special discount
        if self.od_discount:
            amount_tax = sum(line.amount for line in self.tax_line)
            discount_amt_tax = self.od_discount * .05
            self.amount_tax = amount_tax - discount_amt_tax
        self.amount_total = self.amount_untaxed + self.amount_tax - self.od_discount

    
             
    def get_extra_exp_products(self):
        extra_exp_products = [214224,214227,211865,210151,214225,214229,214228,214226]
        return extra_exp_products
    def _check_extra_exp_products(self):
        check = False
        extra_exp_products = self.get_extra_exp_products()
        for line in self.invoice_line:
            product_id = line.product_id and line.product_id.id
            if product_id:
                if product_id in extra_exp_products:
                    check = True
        return check
    
    def od_print_invoice(self, cr, uid, ids, context=None):
        return self.pool['report'].get_action(cr, uid, ids, 'report.report_ksa_e_invoice1', context=context)
            
    
    def _check_extra_exp(self):
        check_extra_exp = self._check_extra_exp_products()
        allow_extra_exp = self.od_allow_extra_exp
        if not allow_extra_exp and check_extra_exp:
            raise Warning("This Invoice Contains Extra Expense Products, If you need to proceed Kindly Enable Allow Extra Expense")
        
    def send_mail_to_pm(self,template):
        ir_model_data = self.env['ir.model.data']
        email_obj = self.pool.get('email.template')
        if self.company_id.id == 6:
            template = template +'_saudi'
        template_id = ir_model_data.get_object_reference('orchid_beta', template)[1]
        rec_id = self.id
        email_obj.send_mail(self.env.cr,self.env.uid,template_id,rec_id, force_send=True)
        return True
    
    @api.multi
    def finalize_invoice_move_lines(self, move_lines):
        self._check_extra_exp()
        if self.type == 'out_invoice':
            self.send_mail_to_pm('od_invoice_validated_email_template')
        def get_currency_check(from_currncy,to_currecny):
            return from_currncy != to_currecny
        
        cur_check = get_currency_check(self.currency_id, self.company_id.currency_id)
        amt_currency_id = False
        amount_currency = 0.0
        if cur_check:
            amt_currency_id = self.currency_id and self.currency_id.id
        
        if self.type == 'in_invoice' and self.od_discount > 0:
            new_line=[]
            discount = self.od_discount
            from_currency = self.currency_id
            discount = from_currency.compute(discount,self.company_id.currency_id)
            for line in move_lines:
                if line[2].get('credit'):
                    line[2]['credit'] = line[2].get('credit') - discount
                    if cur_check:
                        line[2]['amount_currency'] = line[2].get('amount_currency') + self.od_discount #-ve sign when credit
                    break
            if cur_check:
                amount_currency =-1 * self.od_discount
            vals={'analytic_account_id': False, 'tax_code_id': False, 'analytic_lines': [], 'tax_amount': False, 'name': u'Supplier Discount', 'ref': False, 'asset_id': False, 
                  'currency_id': amt_currency_id, 'credit': discount, 'product_id': False, 'date_maturity': self.date_due, 'debit': 0, 'date': self.date_invoice, 'amount_currency': amount_currency, 'product_uom_id': False, 'quantity': 1.0, 'partner_id': self.partner_id.id, 'account_id': self.od_discount_acc_id and self.od_discount_acc_id.id or False
                }
            move_lines.append((0,0,vals))  
        if self.type == 'out_invoice' and self.od_discount > 0:
            discount = self.od_discount
            from_currency = self.currency_id
            if cur_check:
                discount = from_currency.compute(discount,self.company_id.currency_id)             
            for line in move_lines:
                if line[2].get('debit'):
                    line[2]['debit'] = line[2].get('debit') - discount
                    if cur_check:
                        line[2]['amount_currency'] = line[2].get('amount_currency') + self.od_discount
                    break
            if cur_check:
                amount_currency = self.od_discount
            vals={'analytic_account_id': False, 'tax_code_id': False, 'analytic_lines': [], 
                  'tax_amount': False, 'name': u'Customer Discount', 'ref': False, 'asset_id': False, 
                  'currency_id': amt_currency_id, 'debit':discount, 'product_id': False, 'date_maturity': self.date_due, 'credit': 0, 'date': self.date_invoice, 'amount_currency': amount_currency, 'product_uom_id': False, 'quantity': 1.0, 'partner_id': self.partner_id.id, 'account_id': self.od_discount_acc_id and self.od_discount_acc_id.id or False
                }
            move_lines.append((0,0,vals))    
        return super(account_invoice, self).finalize_invoice_move_lines(move_lines)

