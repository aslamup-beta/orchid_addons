# -*- coding: utf-8 -*-

import itertools
from lxml import etree

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp
from openerp.tools import amount_to_text_en
from . import amount_to_ar
from pprint import pprint
from openerp import tools
from itertools import groupby







class account_invoice(models.Model):
    _inherit = "account.invoice"
    
    
    
    def get_gov_section(self):
        res = []
        for line in self.gov_alternate_line:
            res.append({'name':line.name , 'name2': line.name2,'section':line.section2 or 'Uncategorized','quantity':line.quantity,'unit_price':line.unit_price,'total_bf_tax':line.total_bf_tax,'tax_rate':line.tax_rate,'tax_amount':line.tax_amount,'total_amount':line.total_amount})
        result = self.od_categorize(res)
        return result
    def od_categorize(self,res):
        result =[]
        for k,vals in groupby(res,key=lambda x:x['section']):
            data_list =[]
            for val in vals:
                data_list.append(val)
            result.append({'categ':k,'data':data_list})
        return result
    @api.multi    
    def amount_to_text_en(self, amount, currency):
        convert_amount_in_words = amount_to_text_en.amount_to_text(amount, lang='en', currency=currency)        
        company_id = self.company_id and self.company_id.id
        if company_id ==6:
            convert_amount_in_words = convert_amount_in_words.replace('Cent', 'Halala')
        else:
            convert_amount_in_words = convert_amount_in_words.replace('Cent', 'Fill')
                              
        return convert_amount_in_words
    
    @api.multi    
    def amount_to_text_ar(self, amount, currency):
        convert_amount_in_words = amount_to_ar.amount_to_text_ar(amount, currency='')        
        return convert_amount_in_words
    
    
    @api.one
    @api.depends(
        'state', 'currency_id', 'invoice_line.price_subtotal',
        'move_id.line_id.account_id.type',
        'move_id.line_id.amount_residual',
        # Fixes the fact that move_id.line_id.amount_residual, being not stored and old API, doesn't trigger recomputation
        'move_id.line_id.reconcile_id',
        'move_id.line_id.amount_residual_currency',
        'move_id.line_id.currency_id',
        'move_id.line_id.reconcile_partial_id.line_partial_ids.invoice.type',
    )
    # An invoice's residual amount is the sum of its unreconciled move lines and,
    # for partially reconciled move lines, their residual amount divided by the
    # number of times this reconciliation is used in an invoice (so we split
    # the residual amount between all invoice)
    def _compute_residual(self):
        self.residual = 0.0
        # Each partial reconciliation is considered only once for each invoice it appears into,
        # and its residual amount is divided by this number of invoices
        partial_reconciliations_done = []
        for line in self.sudo().move_id.line_id:
            if line.account_id.type not in ('receivable', 'payable'):
                continue
            if line.reconcile_partial_id and line.reconcile_partial_id.id in partial_reconciliations_done:
                continue
            # Get the correct line residual amount
            if line.currency_id == self.currency_id:
                line_amount = line.amount_residual_currency if line.currency_id else line.amount_residual
            else:
                from_currency = line.company_id.currency_id.with_context(date=line.date)
                line_amount = from_currency.compute(line.amount_residual, self.currency_id)
            # For partially reconciled lines, split the residual amount
            if line.reconcile_partial_id:
                partial_reconciliation_invoices = set()
                for pline in line.reconcile_partial_id.line_partial_ids:
                    if pline.invoice and self.type == pline.invoice.type:
                        partial_reconciliation_invoices.update([pline.invoice.id])
                line_amount = self.currency_id.round(line_amount / len(partial_reconciliation_invoices))
                partial_reconciliations_done.append(line.reconcile_partial_id.id)
            self.residual += line_amount
        if self.state =='manual':
            self.residual =0.0
        self.residual = max(self.residual, 0.0)
        
        
    
    
    @api.multi
    def action_date_assign(self):
        super(account_invoice,self).action_date_assign()
        for inv in self:
            today = fields.Date.today()
            inv.write({'date_invoice':today,'date_due':today})
#             res = inv.onchange_payment_term_date_invoice(inv.payment_term.id, today)
#             if res and res.get('value'):
#                 inv.write(res['value'])
        return True
  
    
    state = fields.Selection([('draft','Draft'),('proforma','Pro-forma'),('proforma2','Pro-forma'),('open','Open'),('accept','Accepted By Customer'),('paid','Paid'),('cancel','Cancelled'),('asset_done','Asset Done'),('manual','Manually Settled')],string="Invoice Status")
    residual = fields.Float(string='Balance', digits=dp.get_precision('Account'),
        compute='_compute_residual', store=True,
        help="Remaining amount due.")
    
    
    date_invoice = fields.Date(string="Invoice Date",default=fields.Date.today())
    od_analytic_account = fields.Many2one('account.analytic.account',string='Analytic Account') 
    reason_for_credit_note = fields.Char(string="Reason For Credit Note")
    reason_for_debit_note = fields.Char(string="Reason For Debit Note")
    bank1_id = fields.Many2one('res.partner.bank',string="Bank 1")
    bank2_id = fields.Many2one('res.partner.bank',string="Bank 2",readonly=True,states={'draft':[('readonly',False)]})
    payment_term_detail_line = fields.One2many('invoice.beta.payment.terms','invoice_id',string="Payment Term Details",readonly=True,states={'draft':[('readonly',False)]})
    gov_alternate_line = fields.One2many('invoice.alternate.line','invoice_id',string="Alternate Line")
   
    od_original_invoice_id = fields.Many2one('account.invoice',string="Original Invoice")
    od_cost_sheet_id = fields.Many2one('od.cost.sheet',string="Cost Sheet",readonly=True)
    od_cost_centre_id =fields.Many2one('od.cost.centre',string='Cost Centre',readonly=True,states={'draft':[('readonly',False)]})
    od_branch_id =fields.Many2one('od.cost.branch',string='Branch',readonly=True,states={'draft':[('readonly',False)]})
    od_division_id = fields.Many2one('od.cost.division',string='Division',readonly=True,states={'draft':[('readonly',False)]})
    lead_id = fields.Many2one('crm.lead',string="Opportunity",related="od_cost_sheet_id.lead_id",readonly=True)
     
    od_sale_team_id = fields.Many2one('crm.case.section',string="Sale Team",related="lead_id.section_id",readonly=True)
    op_stage_id = fields.Many2one('crm.case.stage',string="Opp Stage",related="lead_id.stage_id",readonly=True)    
    op_expected_booking = fields.Date(string="Opp Expected Booking",related="lead_id.date_action",readonly=True)    
   
      
    fin_approved_date = fields.Datetime(string="Finance Approved Date",related="od_cost_sheet_id.approved_date",readonly=True)
    od_closing_date = fields.Date(string="Closing Date")
    bt_enable = fields.Boolean(string="Enable Payment Percentage",readonly=True,states={'draft':[('readonly',False)]})
    bt_pay_perc = fields.Float(string="Payment %",readonly=True,states={'draft':[('readonly',False)]})
    bt_supply_date = fields.Date(string="Supply Date",readonly=True,states={'draft':[('readonly',False)]})
    bt_po_ref = fields.Char(string="Client PO Ref",readonly=True,states={'draft':[('readonly',False)]})
    
    add_fin_stamp = fields.Boolean(string="Add Finance Stamp")
    fin_stamp_date= fields.Date("Finance Stamp Date")
    fin_stamp_user_id= fields.Many2one('res.users',string="Finance Stamp User")
    fin_stamp_img = fields.Binary(string="Seal/Stamp")
    fin_sign= fields.Binary(string="Finance Signature")
#     bt_client_po_ref = fields.Char(string="Client PO Ref",readonly=True,states={'draft':[('readonly',False)]})
    
    
    
    
    
    @api.onchange('add_fin_stamp')
    def onchange_fin_stamp(self):
        date = fields.Date.today()
        if self.add_fin_stamp:
            if not self.fin_stamp_date:
                self.fin_stamp_date = date 
            if not self.fin_stamp_user_id:
                self.fin_stamp_user_id = self._uid
    
    @api.multi  
    def bt_apply_percent(self):
        bt_enable = self.bt_enable 
        bt_pay_perc = self.bt_pay_perc 
        for line in self.invoice_line:
            line.bt_enable = bt_enable 
            line.bt_pay_perc = bt_pay_perc
        
        for line in self.gov_alternate_line:
            line.bt_enable = bt_enable 
            line.bt_pay_perc = bt_pay_perc
            
    def get_extra_exp_products(self):
        extra_exp_products = [226414,226417,222244,226415,226419,226418,226416]
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
            
    
    def _check_extra_exp(self):
        check_extra_exp = self._check_extra_exp_products()
        allow_extra_exp = self.od_allow_extra_exp 
        if not allow_extra_exp and check_extra_exp:
            raise Warning("This Invoice Contains Extra Expense Products, If you need to proceed Kindly Enable Allow Extra Expense")
    @api.multi
    def finalize_invoice_move_lines(self, move_lines):
        self._check_extra_exp()
        od_cost_centre_id = self.od_cost_centre_id and self.od_cost_centre_id.id or False
        od_branch_id = self.od_branch_id and self.od_branch_id.id or False
        od_division_id = self.od_division_id and self.od_division_id.id or False
        if not od_cost_centre_id:
            od_cost_centre_id = (self.od_analytic_account and self.od_analytic_account.od_cost_centre_id and self.od_analytic_account.od_cost_centre_id.id) or (self.od_analytic_account and self.od_analytic_account.cost_centre_id and self.od_analytic_account.cost_centre_id.id)
        if not od_branch_id:
            od_branch_id = (self.od_analytic_account and self.od_analytic_account.od_branch_id and self.od_analytic_account.od_branch_id.id) or (self.od_analytic_account and self.od_analytic_account.branch_id and self.od_analytic_account.branch_id.id)
        if not od_division_id:
            od_division_id = (self.od_analytic_account and self.od_analytic_account.od_division_id and self.od_analytic_account.od_division_id.id) or (self.od_analytic_account and self.od_analytic_account.division_id and self.od_analytic_account.division_id.id)

        if not (od_cost_centre_id  and od_branch_id):
            raise Warning("Need to Fill Cost center and Branch")
        remarks = self.od_remarks or " "
        for _,_,move_line in move_lines:
            if move_line['name'] == 'PVAT 5%':
                name = move_line['name'] + " " + remarks
            else:
                name = move_line['name']
            move_line.update({
                'od_cost_centre_id':od_cost_centre_id,
                'od_branch_id':od_branch_id,
                'od_division_id':od_division_id,
                'name': name
                })
            
        return super(account_invoice, self).finalize_invoice_move_lines(move_lines)

    @api.multi
    def copy_from_invoice_lines(self):
        if self.gov_alternate_line:
            for line in self.gov_alternate_line:
                line.unlink()
        tax_rate = 0.00
        discount = 0.00
        disc_amount = 0.00
        for line in self.invoice_line:
            unit_price = line.price_unit
            quantity = line.quantity
            total_bf_tax =  unit_price* quantity
            total_bf_discount = unit_price* quantity
            bt_pay_perc = line.bt_pay_perc
            discount = line.discount
            if line.invoice_line_tax_id:
                tax_rate = 15.0 /100.0
                
            if discount:
                if bt_pay_perc:
                    total_bf_discount = total_bf_discount  * (bt_pay_perc/100.0)
                print "total_before_disc", total_bf_discount
                    
                disc_amount1 = total_bf_discount * (1 - (discount or 0.0) / 100.0)
                print "Amount to reduced", disc_amount1
                disc_amount = total_bf_discount - disc_amount1
                print "total_after_discount", disc_amount
                
            if bt_pay_perc:
                
                total_bf_discount = total_bf_discount  * (bt_pay_perc/100.0)
                total_bf_tax1 = total_bf_tax * (bt_pay_perc/100.0)
                total_bf_tax = total_bf_tax1 - disc_amount
            
            
                
             
                
                
            tax_amount = total_bf_tax * tax_rate
            total_amount = total_bf_tax + tax_amount
             

            vals = {'invoice_id': self.id,
                    'name': line.name_ar or line.name,
                    'name2': line.name,
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'bt_pay_perc': bt_pay_perc,
                    'disc_amount': discount,
                    'total_bf_discount': total_bf_discount,
                    'total_bf_tax': total_bf_tax,
                    'tax_rate': 15.00 if line.invoice_line_tax_id else 0.00,
                    'tax_amount': tax_amount,
                    'total_amount': total_amount
                
                }
            
            self.gov_alternate_line.create(vals)
        return True


class account_invoice_tax(models.Model):
    _inherit = "account.invoice.tax"
    @api.v8
    def compute(self, invoice):
        tax_grouped = {}
        currency = invoice.currency_id.with_context(date=invoice.date_invoice or fields.Date.context_today(invoice))
        company_currency = invoice.company_id.currency_id
        for line in invoice.invoice_line:
            price_unit = line.price_unit 
            bt_enable = line.bt_enable 
            bt_pay_perc = line.bt_pay_perc
            if bt_enable:
                price_unit = price_unit * (bt_pay_perc/100.0)
            taxes = line.invoice_line_tax_id.compute_all(
                (price_unit * (1 - (line.discount or 0.0) / 100.0)),
                line.quantity, line.product_id, invoice.partner_id)['taxes']
            for tax in taxes:
                val = {
                    'invoice_id': invoice.id,
                    'name': tax['name'],
                    'amount': tax['amount'],
                    'manual': False,
                    'sequence': tax['sequence'],
                    'base': currency.round(tax['price_unit'] * line['quantity']),
                }
                if invoice.type in ('out_invoice','in_invoice'):
                    val['base_code_id'] = tax['base_code_id']
                    val['tax_code_id'] = tax['tax_code_id']
                    val['base_amount'] = currency.compute(val['base'] * tax['base_sign'], company_currency, round=False)
                    val['tax_amount'] = currency.compute(val['amount'] * tax['tax_sign'], company_currency, round=False)
                    val['account_id'] = tax['account_collected_id'] or line.account_id.id
                    val['account_analytic_id'] = tax['account_analytic_collected_id']
                else:
                    val['base_code_id'] = tax['ref_base_code_id']
                    val['tax_code_id'] = tax['ref_tax_code_id']
                    val['base_amount'] = currency.compute(val['base'] * tax['ref_base_sign'], company_currency, round=False)
                    val['tax_amount'] = currency.compute(val['amount'] * tax['ref_tax_sign'], company_currency, round=False)
                    val['account_id'] = tax['account_paid_id'] or line.account_id.id
                    val['account_analytic_id'] = tax['account_analytic_paid_id']

                # If the taxes generate moves on the same financial account as the invoice line
                # and no default analytic account is defined at the tax level, propagate the
                # analytic account from the invoice line to the tax line. This is necessary
                # in situations were (part of) the taxes cannot be reclaimed,
                # to ensure the tax move is allocated to the proper analytic account.
                if not val.get('account_analytic_id') and line.account_analytic_id and val['account_id'] == line.account_id.id:
                    val['account_analytic_id'] = line.account_analytic_id.id

                key = (val['tax_code_id'], val['base_code_id'], val['account_id'])
                if not key in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['base'] += val['base']
                    tax_grouped[key]['amount'] += val['amount']
                    tax_grouped[key]['base_amount'] += val['base_amount']
                    tax_grouped[key]['tax_amount'] += val['tax_amount']

        for t in tax_grouped.values():
            t['base'] = currency.round(t['base'])
            t['amount'] = currency.round(t['amount'])
            t['base_amount'] = currency.round(t['base_amount'])
            t['tax_amount'] = currency.round(t['tax_amount'])

        return tax_grouped
    
    
class account_invoice_line(models.Model):
    _inherit = "account.invoice.line"
    
    name_ar = fields.Text(string="Product Description(Arabic)")
    bt_enable = fields.Boolean(string="Enable Pay %")
    bt_pay_perc = fields.Float(string="Payment %")
    
    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_id', 'quantity',
        'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id','bt_enable','bt_pay_perc')
    def _compute_price(self):
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        bt_enable = self.bt_enable
        if bt_enable:
            bt_pay_perc = self.bt_pay_perc
            price = price * (bt_pay_perc/100.0)
        taxes = self.invoice_line_tax_id.compute_all(price, self.quantity, product=self.product_id, partner=self.invoice_id.partner_id)
        self.price_subtotal = taxes['total']
        if self.invoice_id:
            self.price_subtotal = self.invoice_id.currency_id.round(self.price_subtotal)

class invoice_beta_payment_terms(models.Model):
    _name = "invoice.beta.payment.terms"
    invoice_id = fields.Many2one('account.invoice',string="Invoice",ondelete='cascade')
    name = fields.Char(string="Payment Term")


class invoice_alternate_line(models.Model):
    _name = "invoice.alternate.line"
    
    
    @api.one 
    @api.depends('unit_price','quantity','tax_rate','bt_pay_perc','discount','disc_amount')
    def _compute_calc(self):
        total_bf_tax = self.unit_price * self.quantity
        total_bf_discount = self.unit_price * self.quantity
        bt_pay_perc = self.bt_pay_perc
        discount = self.discount
        disc_amount = self.disc_amount
        tax_rate = self.tax_rate /100.0
        
        original_total_bf_discount = total_bf_discount 
        original_total_bf_tax = original_total_bf_discount - disc_amount
        original_tax_amount = original_total_bf_tax * tax_rate
        original_total_amount = original_total_bf_tax + original_tax_amount
        
        self.original_total_bf_discount = original_total_bf_discount 
        self.original_total_bf_tax = original_total_bf_tax 
        self.original_tax_amount = original_tax_amount 
        self.original_total_amount = original_total_amount 
        
        if bt_pay_perc:
            total_bf_tax = total_bf_tax * (bt_pay_perc/100.0)
            total_bf_discount = total_bf_discount  * (bt_pay_perc/100.0)
            disc_amount = disc_amount * (bt_pay_perc/100.0)
        if discount:
            total_bf_tax = total_bf_tax * (1 - (discount or 0.0) / 100.0)
        
        if disc_amount:
            total_bf_tax = total_bf_discount - disc_amount
            
        
        tax_rate = self.tax_rate /100.0
        tax_amount = total_bf_tax * tax_rate
        total_amount = total_bf_tax + tax_amount
        self.total_bf_tax = total_bf_tax 
        self.total_bf_discount = total_bf_discount
        self.tax_amount = tax_amount 
        self.total_amount = total_amount
    
    
    invoice_id = fields.Many2one('account.invoice',string="Invoice",ondelete='cascade')
    name = fields.Text(string="Description Arabic")
    name2 = fields.Text(string="Description English")
    section2 = fields.Char(string="Section")
    quantity = fields.Float(string="Quantity")
    unit_price = fields.Float(string="Unit Price",digits=dp.get_precision('Gov'))
    total_bf_discount = fields.Float(string="Total Before Discount",compute="_compute_calc",digits=dp.get_precision('Gov'))
    total_bf_tax = fields.Float(string="Total After Discount",compute="_compute_calc",digits=dp.get_precision('Gov'))
    tax_rate =fields.Float(string="Tax Rate(%)")
    
    original_total_bf_discount = fields.Float(string="Original Total Before Discount",compute="_compute_calc",digits=dp.get_precision('Gov'))
    original_total_bf_tax = fields.Float(string="Original Total After Discount",compute="_compute_calc",digits=dp.get_precision('Gov'))
    
    original_tax_amount =fields.Float(string="Tax Amount",compute="_compute_calc",digits=dp.get_precision('Gov'))
    original_total_amount= fields.Float(string="Total Amount",compute="_compute_calc",digits=dp.get_precision('Gov'))
    
    tax_amount =fields.Float(string="Tax Amount",compute="_compute_calc",digits=dp.get_precision('Gov'))
    total_amount= fields.Float(string="Total Amount",compute="_compute_calc",digits=dp.get_precision('Gov'))
    bt_enable = fields.Boolean(string="Enable Pay %")
    bt_pay_perc = fields.Float(string="Payment %",digits=dp.get_precision('Pay Perc'))
    discount = fields.Float(string="Discount %",digits=dp.get_precision('Gov Disc'))
    disc_amount = fields.Float(string="Discount Amount",digits=dp.get_precision('Gov'))
    
class res_partner_bank(models.Model):
    _inherit = "res.partner.bank"
    
    od_account_no = fields.Char(string="Account Number")
    