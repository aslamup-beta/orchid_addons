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

def _employee_get(obj, cr, uid, context=None):
    if context is None:
        context = {}
    ids = obj.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
    if ids:
        return ids[0]
    return False

class od_hr_loans_loans(osv.osv):

    def _amount(self, cr, uid, ids, field_name, arg, context=None):
        res= {}
        for loans in self.browse(cr, uid, ids, context=context):
            total = 0.0
            for line in loans.line_ids:
                total += line.amount
            res[loans.id] = total
        return res

    def _get_loans_from_line(self, cr, uid, ids, context=None):
        return [line.loans_id.id for line in self.pool.get('od.hr.loans.line').browse(cr, uid, ids, context=context)]

    def _get_currency(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, [uid], context=context)[0]
        return user.company_id.currency_id.id

    _name = "od.hr.loans.loans"
    _description = "Loans"
#    _inherit = ['mail.thread']

    _columns = {
        'name': fields.char('Description', readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
        'id': fields.integer('Sheet ID', readonly=True),
        'date': fields.date('Date', select=True, readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
        'journal_id': fields.many2one('account.journal', 'Force Journal', help = "The journal used when the loans is done."),
        'employee_id': fields.many2one('hr.employee', "Employee", required=True, readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
        'user_id': fields.many2one('res.users', 'User', required=True),
        'date_confirm': fields.date('Confirmation Date', select=True, copy=False,
                                    help="Date of the confirmation of the sheet loans. It's filled when the button Confirm is pressed."),
        'date_valid': fields.date('Validation Date', select=True, copy=False,
                                  help="Date of the acceptation of the sheet loans. It's filled when the button Accept is pressed."),
        'user_valid': fields.many2one('res.users', 'Validation By', readonly=True, copy=False,
                                      states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
        'account_move_id': fields.many2one('account.move', 'Ledger Posting', copy=False),
        'line_ids': fields.one2many('od.hr.loans.line', 'loans_id', 'loans Lines', copy=True,
                                    readonly=True, states={'draft':[('readonly',False)]} ),
        'loan_info_line': fields.one2many('od.hr.loan.info.line', 'hr_loan_id', 'loans Lines', copy=True,
                                    readonly=True, states={'draft':[('readonly',False)]} ),
        'note': fields.text('Note'),
        'amount': fields.function(_amount, string='Total Amount', digits_compute=dp.get_precision('Account'), 
            store={
                'od.hr.loans.line': (_get_loans_from_line, ['unit_amount','unit_quantity'], 10)
            }),
        'currency_id': fields.many2one('res.currency', 'Currency', required=True, readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
        'department_id':fields.many2one('hr.department','Department', readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'state': fields.selection([
            ('draft', 'New'),
            ('cancelled', 'Refused'),
            ('confirm', 'Waiting Approval'),
            ('second_approval', 'Second Approval'),
            ('accepted', 'Approved'),
            ('done', 'Waiting Payment'),
            ('paid', 'Paid'),
            ],
            'Status', readonly=True, track_visibility='onchange', copy=False,
            help='When the loans request is created the status is \'Draft\'.\n It is confirmed by the user and request is sent to admin, the status is \'Waiting Confirmation\'.\
            \nIf the admin accepts it, the status is \'Accepted\'.\n If the accounting entries are made for the loans request, the status is \'Waiting Payment\'.'),

    }
    _defaults = {
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'hr.employee', context=c),
        'date': fields.date.context_today,
        'state': 'draft',
        'employee_id': _employee_get,
        'user_id': lambda cr, uid, id, c={}: id,
        'currency_id': _get_currency,
    }

    def unlink(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.state != 'draft':
                raise osv.except_osv(_('Warning!'),_('You can only delete draft loanss!'))
        return super(od_hr_loans_loans, self).unlink(cr, uid, ids, context)

    def onchange_currency_id(self, cr, uid, ids, currency_id=False, company_id=False, context=None):
        res =  {'value': {'journal_id': False}}
        journal_ids = self.pool.get('account.journal').search(cr, uid, [('type','=','purchase'), ('currency','=',currency_id), ('company_id', '=', company_id)], context=context)
        if journal_ids:
            res['value']['journal_id'] = journal_ids[0]
        return res

    def onchange_employee_id(self, cr, uid, ids, employee_id, context=None):
        emp_obj = self.pool.get('hr.employee')
        department_id = False
        company_id = False
        if employee_id:
            employee = emp_obj.browse(cr, uid, employee_id, context=context)
            department_id = employee.department_id.id
            company_id = employee.company_id.id
        return {'value': {'department_id': department_id, 'company_id': company_id}}

    def loans_confirm(self, cr, uid, ids, context=None):
        for obj in self.browse(cr,uid,ids,context):
            for line in obj.loan_info_line:
                self.pool.get('od.hr.loan.info.line').write(cr,uid,[line.id],{'state':'confirm'},context)



#        for loans in self.browse(cr, uid, ids):
#            if loans.employee_id and loans.employee_id.parent_id.user_id:
#                print "DDDDDDDDDDDDDDDDDDDDDD",loans.employee_id and loans.employee_id.parent_id.user_id
#                self.message_subscribe_users(cr, uid, [loans.id], user_ids=[loans.employee_id.parent_id.user_id.id])
        return self.write(cr, uid, ids, {'state': 'confirm', 'date_confirm': time.strftime('%Y-%m-%d')}, context=context)
    def loans_refuse(self, cr, uid, ids, context=None):
        for obj in self.browse(cr,uid,ids,context):
            for line in obj.loan_info_line:
                self.pool.get('od.hr.loan.info.line').write(cr,uid,[line.id],{'state':'cancelled'},context)

        return self.write(cr, uid, ids, {'state': 'cancelled'}, context=context)
    def loans_set_draft(self, cr, uid, ids, context=None):
        for obj in self.browse(cr,uid,ids,context):
            for line in obj.loan_info_line:
                self.pool.get('od.hr.loan.info.line').write(cr,uid,[line.id],{'state':'draft'},context)

        return self.write(cr, uid, ids, {'state': 'draft'}, context=context)
    def loans_accept(self, cr, uid, ids, context=None):
        for obj in self.browse(cr,uid,ids,context):
            for line in obj.loan_info_line:
                self.pool.get('od.hr.loan.info.line').write(cr,uid,[line.id],{'state':'accepted'},context)
        return self.write(cr, uid, ids, {'state': 'accepted', 'date_valid': time.strftime('%Y-%m-%d'), 'user_valid': uid}, context=context)

    def loans_canceled(self, cr, uid, ids, context=None):
        for obj in self.browse(cr,uid,ids,context):
            for line in obj.loan_info_line:
                self.pool.get('od.hr.loan.info.line').write(cr,uid,[line.id],{'state':'cancelled'},context)

        return self.write(cr, uid, ids, {'state': 'cancelled'}, context=context)

    def account_move_get(self, cr, uid, loans_id, context=None):
        '''
        This method prepare the creation of the account move related to the given loans.

        :param loans_id: Id of loans for which we are creating account_move.
        :return: mapping between fieldname and value of account move to create
        :rtype: dict
        '''
        journal_obj = self.pool.get('account.journal')
        loans = self.browse(cr, uid, loans_id, context=context)
        company_id = loans.company_id.id
        date = loans.date_confirm
        ref = loans.name
        journal_id = False
        if loans.journal_id:
            journal_id = loans.journal_id.id
        else:
            journal_id = journal_obj.search(cr, uid, [('type', '=', 'purchase'), ('company_id', '=', company_id)])
            if not journal_id:
                raise osv.except_osv(_('Error!'), _("No loans journal found. Please make sure you have a journal with type 'purchase' configured."))
            journal_id = journal_id[0]
        return self.pool.get('account.move').account_move_prepare(cr, uid, journal_id, date=date, ref=ref, company_id=company_id, context=context)

    def line_get_convert(self, cr, uid, x, part, date, context=None):
        partner_id  = self.pool.get('res.partner')._find_accounting_partner(part).id
        return {
            'date_maturity': x.get('date_maturity', False),
            'partner_id': partner_id,
            'name': x['name'][:64],
            'date': date,
            'debit': x['price']>0 and x['price'],
            'credit': x['price']<0 and -x['price'],
            'account_id': x['account_id'],
            'analytic_lines': x.get('analytic_lines', False),
            'amount_currency': x['price']>0 and abs(x.get('amount_currency', False)) or -abs(x.get('amount_currency', False)),
            'currency_id': x.get('currency_id', False),
            'tax_code_id': x.get('tax_code_id', False),
            'tax_amount': x.get('tax_amount', False),
            'ref': x.get('ref', False),
            'quantity': x.get('quantity',1.00),
            'product_id': x.get('product_id', False),
            'product_uom_id': x.get('uos_id', False),
            'analytic_account_id': x.get('account_analytic_id', False),
        }

    def compute_loans_totals(self, cr, uid, loan, company_currency, ref, account_move_lines, context=None):
        '''
        internal method used for computation of total amount of an loans in the company currency and
        in the loans currency, given the account_move_lines that will be created. It also do some small
        transformations at these account_move_lines (for multi-currency purposes)
        
        :param account_move_lines: list of dict
        :rtype: tuple of 3 elements (a, b ,c)
            a: total in company currency
            b: total in hr.loans currency
            c: account_move_lines potentially modified
        '''
        cur_obj = self.pool.get('res.currency')
        context = dict(context or {}, date=loan.date_confirm or time.strftime('%Y-%m-%d'))
        total = 0.0
        total_currency = 0.0
        for i in account_move_lines:
            if loan.currency_id.id != company_currency:
                i['currency_id'] = loan.currency_id.id
                i['amount_currency'] = i['price']
                i['price'] = cur_obj.compute(cr, uid, loan.currency_id.id,
                        company_currency, i['price'],
                        context=context)
            else:
                i['amount_currency'] = False
                i['currency_id'] = False
            total -= i['price']
            total_currency -= i['amount_currency'] or i['price']
        return total, total_currency, account_move_lines
        
    def action_move_create(self, cr, uid, ids, context=None):
        '''
        main function that is called when trying to create the accounting entries related to an loans
        '''
        move_obj = self.pool.get('account.move')
        for loan in self.browse(cr, uid, ids, context=context):
            if not loan.employee_id.address_home_id:
                raise osv.except_osv(_('Error!'), _('The employee must have a home address.'))
            if not loan.employee_id.address_home_id.property_account_payable.id:
                raise osv.except_osv(_('Error!'), _('The employee must have a payable account set on his home address.'))
            company_currency = loan.company_id.currency_id.id
            diff_currency_p = loan.currency_id.id <> company_currency
            
            #create the move that will contain the accounting entries
            move_id = move_obj.create(cr, uid, self.account_move_get(cr, uid, loan.id, context=context), context=context)
        
            #one account.move.line per loans line (+taxes..)
            eml = self.move_line_get(cr, uid, loan.id, context=context)
            
            #create one more move line, a counterline for the total on payable account
            total, total_currency, eml = self.compute_loans_totals(cr, uid, loan, company_currency, loan.name, eml, context=context)
            acc = loan.employee_id.address_home_id.property_account_payable.id
            eml.append({
                    'type': 'dest',
                    'name': '/',
                    'price': total, 
                    'account_id': acc, 
                    'date_maturity': loan.date_confirm, 
                    'amount_currency': diff_currency_p and total_currency or False, 
                    'currency_id': diff_currency_p and loan.currency_id.id or False, 
                    'ref': loan.name
                    })

            #convert eml into an osv-valid format
            lines = map(lambda x:(0,0,self.line_get_convert(cr, uid, x, loan.employee_id.address_home_id, loan.date_confirm, context=context)), eml)
            journal_id = move_obj.browse(cr, uid, move_id, context).journal_id
            # post the journal entry if 'Skip 'Draft' State for Manual Entries' is checked
            if journal_id.entry_posted:
                move_obj.button_validate(cr, uid, [move_id], context)
            move_obj.write(cr, uid, [move_id], {'line_id': lines}, context=context)
            self.write(cr, uid, ids, {'account_move_id': move_id, 'state': 'done'}, context=context)
        return True

    def move_line_get(self, cr, uid, loans_id, context=None):
        res = []
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        if context is None:
            context = {}
        loan = self.browse(cr, uid, loans_id, context=context)
        company_currency = loan.company_id.currency_id.id

        for line in loan.line_ids:
            mres = self.move_line_get_item(cr, uid, line, context)
            if not mres:
                continue
            res.append(mres)
            tax_code_found= False
            
            #Calculate tax according to default tax on product
            taxes = []
            #Taken from product_id_onchange in account.invoice
            if line.product_id:
                fposition_id = False
                fpos_obj = self.pool.get('account.fiscal.position')
                fpos = fposition_id and fpos_obj.browse(cr, uid, fposition_id, context=context) or False
                product = line.product_id
                taxes = product.supplier_taxes_id
                #If taxes are not related to the product, maybe they are in the account
                if not taxes:
                    a = product.property_account_expense.id #Why is not there a check here?
                    if not a:
                        a = product.categ_id.property_account_expense_categ.id
                    a = fpos_obj.map_account(cr, uid, fpos, a)
                    taxes = a and self.pool.get('account.account').browse(cr, uid, a, context=context).tax_ids or False
                tax_id = fpos_obj.map_tax(cr, uid, fpos, taxes)
            if not taxes:
                continue
            #Calculating tax on the line and creating move?
            for tax in tax_obj.compute_all(cr, uid, taxes,
                    line.unit_amount ,
                    line.unit_quantity, line.product_id,
                    loan.user_id.partner_id)['taxes']:
                tax_code_id = tax['base_code_id']
                tax_amount = line.total_amount * tax['base_sign']
                if tax_code_found:
                    if not tax_code_id:
                        continue
                    res.append(self.move_line_get_item(cr, uid, line, context))
                    res[-1]['price'] = 0.0
                    res[-1]['account_analytic_id'] = False
                elif not tax_code_id:
                    continue
                tax_code_found = True
                res[-1]['tax_code_id'] = tax_code_id
                res[-1]['tax_amount'] = cur_obj.compute(cr, uid, loan.currency_id.id, company_currency, tax_amount, context={'date': loan.date_confirm})
                ## 
                is_price_include = tax_obj.read(cr,uid,tax['id'],['price_include'],context)['price_include']
                if is_price_include:
                    ## We need to deduce the price for the tax
                    res[-1]['price'] = res[-1]['price']  - (tax['amount'] * tax['base_sign'] or 0.0)
                assoc_tax = {
                             'type':'tax',
                             'name':tax['name'],
                             'price_unit': tax['price_unit'],
                             'quantity': 1,
                             'price':  tax['amount'] * tax['base_sign'] or 0.0,
                             'account_id': tax['account_collected_id'] or mres['account_id'],
                             'tax_code_id': tax['tax_code_id'],
                             'tax_amount': tax['amount'] * tax['base_sign'],
                             }
                res.append(assoc_tax)
        return res

    def move_line_get_item(self, cr, uid, line, context=None):
        company = line.loans_id.company_id
        property_obj = self.pool.get('ir.property')
        if line.product_id:
            acc = line.product_id.property_account_expense
            if not acc:
                acc = line.product_id.categ_id.property_account_expense_categ
            if not acc:
                raise osv.except_osv(_('Error!'), _('No purchase account found for the product %s (or for his category), please configure one.') % (line.product_id.name))
        else:
            acc = property_obj.get(cr, uid, 'property_account_expense_categ', 'product.category', context={'force_company': company.id})
            if not acc:
                raise osv.except_osv(_('Error!'), _('Please configure Default loans account for Product purchase: `property_account_expense_categ`.'))
        return {
            'type':'src',
            'name': line.name.split('\n')[0][:64],
            'price_unit':line.unit_amount,
            'quantity':line.unit_quantity,
            'price':line.total_amount,
            'account_id':acc.id,
            'product_id':line.product_id.id,
            'uos_id':line.uom_id.id,
            'account_analytic_id':line.analytic_account.id,
        }

    def action_view_move(self, cr, uid, ids, context=None):
        '''
        This function returns an action that display existing account.move of given loans ids.
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time'
        loans = self.browse(cr, uid, ids[0], context=context)
        assert loans.account_move_id
        try:
            dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account', 'view_move_form')
        except ValueError, e:
            view_id = False
        result = {
            'name': _('loans Account Move'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': loans.account_move_id.id,
        }
        return result

class od_hr_loans_line(osv.osv):
    _name = "od.hr.loans.line"
    _description = "loans Line"

    def _amount(self, cr, uid, ids, field_name, arg, context=None):
#        if not ids:
#            return {}
#        cr.execute("SELECT l.id,COALESCE(SUM(l.unit_amount*l.unit_quantity),0) AS amount FROM od_hr_loans_line l WHERE id IN %s GROUP BY l.id ",(tuple(ids),))
#        res = dict(cr.fetchall())
        res = {}
        for obj in self.browse(cr,uid,ids,context):
            total = obj.amount
            res[obj.id] = total
        return res


#    def _emi(self, cr, uid, ids, field_name, arg, context=None): 
#        result = {} 
#        for line in self.browse(cr, uid, ids, context=context): 
#            unit_amount = line.unit_amount
#            unit_quantity = line.unit_quantity
#            emi = 0
#            if unit_quantity >0.0:
#                emi =(unit_amount / 
#                             unit_quantity)
#            else:
#                emi =0.0
#                 
#            result[line.id] = emi
#        return result 


    def onchange_amount(self, cr, uid, ids, amount, unit_quantity,context=None): 
        res = {} 
        emi = amount / unit_quantity
        return {'value':{'unit_amount':emi}}


    def onchange_unit_quantity(self, cr, uid, ids, amount, unit_quantity,context=None): 
        res = {} 
        emi = amount / unit_quantity
        return {'value':{'unit_amount':emi}}
    def _get_uom_id(self, cr, uid, context=None):
        result = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'product', 'product_uom_unit')
        return result and result[1] or False
    def create(self, cr, uid, vals, context=None):
        res = super(od_hr_loans_line, self).create(cr, uid, vals, context=context)
        loan_data = self.browse(cr, uid,res)
        product_id = vals['product_id']
        hr_loans_line_obj = self.pool.get('od.hr.loans.line')
        unit_quantity = vals['unit_quantity']
        product_obj = self.pool.get('product.template') 
        next_date = vals['date_value']
        unit_amount = vals['unit_amount']
        next_date_strp = datetime.strptime(next_date, '%Y-%m-%d')
        next_date_strp_rel = relativedelta(next_date_strp)
        months = (12*(next_date_strp_rel.years) +(next_date_strp_rel.months+1))
        od_hr_loan_info_line_pool = self.pool.get('od.hr.loan.info.line')
#        for i in range(0,unit_quantity):
        if product_id:
            salary_pool = self.pool.get('hr.salary.rule')
            salary_rule_ids =  self.pool.get('hr.salary.rule').search(cr,uid, [('od_product_id','=',product_id)])
            if salary_rule_ids:
                salary_rule_data = salary_pool.browse(cr, uid, salary_rule_ids, context=context)[0]
                od_hr_loan_info_line_pool.create(cr, uid, {
                        'date_value': next_date_strp,
                        'amount': unit_amount,
                        'rule_id': salary_rule_data.id,
                        'hr_loan_id':loan_data.loans_id and loan_data.loans_id.id ,
                })
                for i in range(1,unit_quantity):
                    next_date_strp = next_date_strp + relativedelta(months=1)
                    od_hr_loan_info_line_pool.create(cr, uid, {
                        'date_value': next_date_strp,
                        'amount': unit_amount,
                        'rule_id': salary_rule_data.id,
                        'hr_loan_id':loan_data.loans_id and loan_data.loans_id.id ,
                })   
        return res
#    def write(self, cr, uid, ids, vals, context=None):
#        print "jjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj",vals
#        new_vals = vals
#        od_hr_loan_info_line_pool = self.pool.get('od.hr.loan.info.line')
#        if vals.has_key('date_value') or vals.has_key('unit_amount') or vals.has_key('product_id') or vals.has_key('name') or vals.has_key('unit_quantity'):
#            unit_amount = vals.get('unit_amount') or self.browse(cr, uid, ids, context)[0].unit_amount
#            od_hr_loan_info_line_pool.write(cr, uid, ids, {'unit_amount':unit_amount}, context=None)
#        return super(od_hr_loans_line, self).write(cr, uid, vals, context=context)

    _columns = {
        'name': fields.char('Transaction Note',required=True),
        'date_value': fields.date('Date', required=True),
        'loans_id': fields.many2one('od.hr.loans.loans', 'loans', ondelete='cascade', select=True),
        'total_amount': fields.function(_amount, string='Total', digits_compute=dp.get_precision('Account')),
        'amount':fields.float('Total Amount'),
        'unit_amount': fields.float('EMI', digits_compute=dp.get_precision('Product Price')),
        'unit_quantity': fields.float('No Of Instalment', digits_compute= dp.get_precision('Product Unit of Measure')),
        'product_id': fields.many2one('product.template', 'Payroll Item',domain="[('od_payroll_item','=',True),('name','=','Loan')]",required="1"),
        'uom_id': fields.many2one('product.uom', 'Unit of Measure'),
#        'emi': fields.function(_emi, string='EMI',store=True),
        'description': fields.text('Description'),
        'analytic_account': fields.many2one('account.analytic.account','Analytic account'),
        'ref': fields.char('Reference'),
        'sequence': fields.integer('Sequence', select=True, help="Gives the sequence order when displaying a list of loans lines."),
        }
    _defaults = {
        'unit_quantity': 1,
        'date_value': lambda *a: time.strftime('%Y-%m-%d'),
        'uom_id': _get_uom_id,
    }
    _order = "sequence, date_value desc"


class od_hr_loan_info_line(osv.osv):
    _name = "od.hr.loan.info.line"
    _columns = {
        'payslip_loan_id':fields.many2one('hr.payslip','PaySlip'),
        'date_value': fields.date('Date'),
        'amount': fields.float('Amount'),
        'rule_id':fields.many2one('hr.salary.rule','Rule'),
        'hr_loan_id': fields.many2one('od.hr.loans.loans','Loans',ondelete='cascade'),
        'employee_id': fields.related('hr_loan_id', 'employee_id', type='many2one', relation='hr.employee', string='Employee', store=True, readonly=True),
        'company_id': fields.related('hr_loan_id','company_id',type="many2one",relation="res.company", string="Company", store=True),
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
        'state': 'draft',
    }

#commented in june 30 as Riyas/Jamshi dont know about the code

#class account_move_line(osv.osv):
#    _inherit = "account.move.line"

#    def reconcile(self, cr, uid, ids, type='auto', writeoff_acc_id=False, writeoff_period_id=False, writeoff_journal_id=False, context=None):
#        res = super(account_move_line, self).reconcile(cr, uid, ids, type=type, writeoff_acc_id=writeoff_acc_id, writeoff_period_id=writeoff_period_id, writeoff_journal_id=writeoff_journal_id, context=context)
#        #when making a full reconciliation of account move lines 'ids', we may need to recompute the state of some hr.loans
#        account_move_ids = [aml.move_id.id for aml in self.browse(cr, uid, ids, context=context)]
#        loans_obj = self.pool.get('od.hr.loans.loans')
#        currency_obj = self.pool.get('res.currency')
#        if account_move_ids:
#            loans_ids = loans_obj.search(cr, uid, [('account_move_id', 'in', account_move_ids)], context=context)
#            for loans in loans_obj.browse(cr, uid, loans_ids, context=context):
#                if loans.state == 'done':
#                    #making the postulate it has to be set paid, then trying to invalidate it
#                    new_status_is_paid = True
#                    for aml in loans.account_move_id.line_id:
#                        if aml.account_id.type == 'payable' and not currency_obj.is_zero(cr, uid, loans.company_id.currency_id, aml.amount_residual):
#                            new_status_is_paid = False
#                    if new_status_is_paid:
#                        loans_obj.write(cr, uid, [loans.id], {'state': 'paid'}, context=context)
#        return res

# vim:loanandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
