# -*- encoding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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
from openerp.osv import fields
from openerp.osv import osv
import time
import openerp.netsvc
#import ir
from mx import DateTime
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import openerp.pooler
from openerp.tools import config
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp.osv.fields import _column

class account_journal(osv.osv):
    _inherit = 'account.journal' 
    _description = 'PDC Journal'
    
    def onchange_pdc_pay_type(self, cr, uid, ids, pdc_payable, context=None):
        if pdc_payable:
            return {'value': {'pdc_payable':True, 'pdc_receivable':False}}
        else:
            return {}
    
    def onchange_pdc_receive_type(self, cr, uid, ids, pdc_receivable, context=None):
        if pdc_receivable:
            return {'value': {'pdc_payable':False, 'pdc_receivable':True}}
        else:
            return {}
        
    _columns = {
         'pdc_payable': fields.boolean('PDC Payable'),
         'pdc_receivable': fields.boolean('PDC Receivable'),
         'income_expense': fields.boolean("Income/Expense", help="journal will be income/expense type"),
        }
account_journal()

class account_voucher(osv.osv):
    _inherit = 'account.voucher' 
    _description = 'Update for Bank type voucher'


    def od_deallocate(self,cr, uid, ids, context=None):
        if not context:
            context = {}
#        if (context.get('type') == 'payment'):
        for voucher in self.browse(cr,uid,ids,context):
            line_ids = [line.id for line in voucher.line_dr_ids]
            vals={'reconcile':False,'amount':0.0}
            self.pool.get('account.voucher.line').write(cr,uid,line_ids,vals)
#        if (context.get('type') == 'receipt'):
        for voucher in self.browse(cr,uid,ids,context):
            line_ids = [line.id for line in voucher.line_cr_ids]
            vals={'reconcile':False,'amount':0.0}
            self.pool.get('account.voucher.line').write(cr,uid,line_ids,vals)
        return True

    def od_refresh_allocation(self,cr, uid, ids, context=None):
#        if (context.get('type') == 'payment'):
        for voucher in self.browse(cr,uid,ids,context):
            line_ids = [line.id for line in voucher.line_dr_ids if line.amount == 0]
            self.pool.get('account.voucher.line').unlink(cr,uid,line_ids)

#        if (context.get('type') == 'receipt'):
        for voucher in self.browse(cr,uid,ids,context):
            line_ids = [line.id for line in voucher.line_cr_ids if line.amount == 0]
            self.pool.get('account.voucher.line').unlink(cr,uid,line_ids)
        return True

    
    def proforma_voucher(self, cr, uid, ids, context=None):
        total_acc_info_amt = 0.0
        for voucher in self.browse(cr, uid, ids, context):
            if voucher.journal_id.type == 'bank' and not voucher.pdc_check:
                self.write(cr, uid, ids, {'check_clear':True})
            if voucher.payment_type in ('expense','income'):
                if not voucher.income_expense_ids:
                    raise osv.except_osv(_('Warning !'),
                        _('Please enter account lines.'))
                else:
                    for acc_info in voucher.income_expense_ids:
                        total_acc_info_amt += acc_info.amount_currency
                    
                    if round(voucher.amount,2) != round(total_acc_info_amt,2):
                        raise osv.except_osv(_('Warning !'),
                        _('Account lines total should be equal of paid amount.'))
                    return self.action_release_cheque(cr, uid, ids, context=context)
            else:
                return super(account_voucher, self).proforma_voucher(cr, uid, ids, context=context)
            
    def bounce_action_on_multiple_selection(self, cr, uid, ids, context=None):
        """User will select multiple records to perform bounce operation"""
        acc_voucher = self.pool.get('account.voucher')
        selected_ids = []
        all_entries = False
        cust_sup_entries = False
        if context:
            selected_ids = context.get('active_ids')
        for acc_brw in acc_voucher.browse(cr, uid, selected_ids, context):
            if acc_brw.state == 'posted' and acc_brw.check_bank == True and acc_brw.check_clear == True:
                self.action_bounce_check(cr, uid, [acc_brw.id], context)
            else:
                raise osv.except_osv(_('Warning !'),
                        _('Make sure all selected records are validate and Released !'))
                
            default_type = acc_brw.type or False
            if acc_brw.all_entries:
                all_entries = True
            if acc_brw.type in ('receipt', 'payment'):
                cust_sup_entries = True
                
        if  cust_sup_entries and not all_entries:
            return {
                'view_type': 'list',
                'view_mode': 'list,form',
                'res_model': 'account.voucher',
                'type':'ir.actions.act_window',
                'target': 'current',
                'nodestroy': True,
                'domain':[('type','=',default_type)],
                'context': context,
            }
        elif all_entries:
            return {
                'view_type': 'list',
                'view_mode': 'list,form',
                'res_model': 'account.voucher',
                'type':'ir.actions.act_window',
                'target': 'current',
                'nodestroy': True,
                'domain':['|',('check_bank','=',True),('payment_type','in',['expense','income'])],
                'context': context,
            }
            
    def release_action_on_multiple_selection(self, cr, uid, ids, context=None):
        """User will select multiple records to perform release cheque operation"""
        acc_voucher = self.pool.get('account.voucher')
        selected_ids = []
        all_entries = False
        cust_sup_entries = False
        default_pay_type = False
        if context:
            selected_ids = context.get('active_ids')
        for acc_brw in acc_voucher.browse(cr, uid, selected_ids, context):
            if acc_brw.state == 'posted' and acc_brw.pdc_check == True and acc_brw.check_clear == False:
                self.action_release_cheque(cr, uid, [acc_brw.id], context)
#                pass
            else:
                raise osv.except_osv(_('Warning !'),
                        _('Make sure all selected records are validate !'))
                
            default_type = acc_brw.type or False
            if acc_brw.all_entries:
                all_entries = True
            if acc_brw.type in ('receipt', 'payment'):
                cust_sup_entries = True
                
#        if default_pay_type in ('cust_payment','sup_payment'):
        if  cust_sup_entries and not all_entries:
            return {
                'view_type': 'list',
                'view_mode': 'list,form',
                'res_model': 'account.voucher',
                'type':'ir.actions.act_window',
                'target': 'current',
                'nodestroy': True,
                'domain':[('type','=',default_type)],
                'context': context,
            }
        elif all_entries:
            return {
                'view_type': 'list',
                'view_mode': 'list,form',
                'res_model': 'account.voucher',
                'type':'ir.actions.act_window',
                'target': 'current',
                'nodestroy': True,
                'domain':['|',('check_bank','=',True),('payment_type','in',['expense','income'])],
                'context': context,
            }

#actual_credit = currency_obj.compute(cr, uid, line_currency.id, target_currency.id, actual_credit, context=ctx)
            
    def _get_expense_entries(self, cr, uid, voucher, journal_id, move_id, acc_info, company_currency, current_currency, context=None):
        sign = voucher.type == 'expense' and -1 or 1
        currency_obj = self.pool.get('res.currency')
        actual_debit = currency_obj.compute(cr, uid, current_currency, company_currency, acc_info.amount_currency, context=context)
        cheque_release_date = voucher.cheque_release_date or voucher.check_date or voucher.date
        if voucher.state == 'draft':
            cheque_release_date = voucher.date
        period_pool = self.pool.get('account.period')
        search_periods = period_pool.find(cr, uid, cheque_release_date, context=context) 
        period_id = search_periods and search_periods[0]


        dr_move_line = {
            'name': voucher.name or acc_info.name or '/',
            'debit': actual_debit,
            'credit': 0.0,
            'account_id': acc_info.account_id.id,
            'partner_id':acc_info.partner_id.id or False,
            'move_id': move_id,
            'journal_id': journal_id,
            'period_id': period_id or voucher.period_id.id,
            'analytic_account_id': acc_info.analytic_account_id.id or False,
            'currency_id': company_currency <> current_currency and  current_currency or False,
            'amount_currency': company_currency <> current_currency and sign * acc_info.amount_currency or 0.0,
#            'date': voucher.date,
            'date': cheque_release_date, #modifed to get the check release date in movelines
            'date_maturity': voucher.date_due,
            }
        return dr_move_line

    def _get_income_entries(self, cr, uid, voucher, journal_id, move_id, acc_info, company_currency, current_currency, context=None):
        sign = voucher.type == 'income' and 1 or -1

        currency_obj = self.pool.get('res.currency')
        actual_credit = currency_obj.compute(cr, uid, current_currency, company_currency, acc_info.amount_currency, context=context)

        cheque_release_date = voucher.cheque_release_date or voucher.check_date or voucher.date
        if voucher.state == 'draft':
            cheque_release_date = voucher.date
        period_pool = self.pool.get('account.period')
        search_periods = period_pool.find(cr, uid, cheque_release_date, context=context) 
        period_id = search_periods and search_periods[0]

        cr_move_line = {
            'name': voucher.name or acc_info.name or '/',
            'debit': 0.0,
            'credit': actual_credit,
            'account_id': acc_info.account_id.id,
            'partner_id':acc_info.partner_id.id or False,
            'move_id': move_id,
            'journal_id': journal_id,
            'period_id': period_id or voucher.period_id.id,
            'analytic_account_id': acc_info.analytic_account_id.id or False,
            'currency_id': company_currency <> current_currency and  current_currency or False,
            'amount_currency': company_currency <> current_currency and sign * acc_info.amount_currency or 0.0,
#            'date': voucher.date,
            'date': cheque_release_date, #modifed to get the check release date in movelines
            'date_maturity': voucher.date_due,
            }
        return cr_move_line
    
    def _get_partner_dr_entries(self, cr, uid, voucher, journal_id, move_id, dr_account_id, company_currency, current_currency, context=None):
        sign = 1
        cheque_release_date = voucher.cheque_release_date or voucher.check_date or voucher.date
        if voucher.state == 'draft':
            cheque_release_date = voucher.date
        period_pool = self.pool.get('account.period')
        search_periods = period_pool.find(cr, uid, cheque_release_date, context=context) 
        period_id = search_periods and search_periods[0]

        dr_move_line = {
                'name': voucher.name or '/',
                'debit': voucher.paid_amount_in_company_currency,
                'credit': 0.0,
                'account_id': dr_account_id,
                'move_id': move_id,
                'journal_id': journal_id,
                'period_id': period_id or voucher.period_id.id,
                'partner_id': voucher.partner_id.id,
                'currency_id': company_currency <> current_currency and  current_currency or False,
                'amount_currency': company_currency <> current_currency and sign * voucher.amount or 0.0,
#                'date': voucher.date,
                'date': cheque_release_date, #modifed to get the check release date in movelines
                'date_maturity': voucher.date_due,
            }
        return dr_move_line
    
    def _get_partner_cr_entries(self, cr, uid, voucher, journal_id, move_id, cr_account_id, company_currency, current_currency, context=None):
        sign = -1 

        cheque_release_date = voucher.cheque_release_date or voucher.check_date or voucher.date
        if voucher.state == 'draft':
            cheque_release_date = voucher.date
        period_pool = self.pool.get('account.period')
        search_periods = period_pool.find(cr, uid, cheque_release_date, context=context) 
        period_id = search_periods and search_periods[0]

        cr_move_line = {
            'name': voucher.name or '/',
            'debit': 0.0,
            'credit': voucher.paid_amount_in_company_currency,
            'account_id': cr_account_id,
            'move_id': move_id,
            'journal_id': journal_id,
            'period_id': period_id or voucher.period_id.id,
            'partner_id': voucher.partner_id.id,
            'currency_id': company_currency <> current_currency and  current_currency or False,
            'amount_currency': company_currency <> current_currency and sign * voucher.amount or 0.0,
#            'date': voucher.date,
            'date': cheque_release_date, #modifed to get the check release date in movelines
            'date_maturity': voucher.date_due,
        }
        return cr_move_line
        
                
    def action_release_cheque(self, cr, uid, ids, context=None):
        acc_voucher = self.pool.get('account.voucher')
        move_pool = self.pool.get('account.move')
        move_line_pool = self.pool.get('account.move.line')
        if context is None:
            context = {}

        for voucher in self.browse(cr, uid, ids, context=context):
            check_date = voucher.date





            period_pool = self.pool.get('account.period')
            search_periods = period_pool.find(cr, uid, check_date, context=context) 
            period_id = search_periods[0]

            seq_obj = self.pool.get('ir.sequence')
            journal_id = False
            
            ref = ''
            date_switch=False
            if voucher.payment_type in ('expense','income') and voucher.state == 'draft':
                if voucher.number:
                    name = voucher.number
                elif voucher.journal_id.sequence_id.id:
                    if not voucher.journal_id.sequence_id.active:
                        raise osv.except_osv(_('Configuration Error !'),
                        _('Please activate the sequence of selected journal !'))
                    c = dict(context)
                    c.update({'fiscalyear_id': self.pool.get('account.period').browse(cr,uid,period_id,context).fiscalyear_id.id})
                    name = seq_obj.next_by_id(cr, uid, voucher.journal_id.sequence_id.id, context=c)
                else:
                    raise osv.except_osv(_('Error!'),
                            _('Please define a sequence on the journal.'))
                if not voucher.reference:
                    ref = name.replace('/','')
                else:
                    ref = voucher.reference
                journal_id = voucher.journal_id.id
            else:
                cheque_release_date = voucher.cheque_release_date
                
                if cheque_release_date:

                    period_pool = self.pool.get('account.period')
                    search_periods = period_pool.find(cr, uid, cheque_release_date, context=context) 
                    period_id = search_periods[0]
                    date_switch = True





                if voucher.release_number:
                    name = voucher.release_number
                elif voucher.journal_ids.sequence_id.id:
                    if not voucher.journal_ids.sequence_id.active:
                        raise osv.except_osv(_('Configuration Error !'),
                        _('Please activate the sequence of selected journal !'))
                    c = dict(context)
                    c.update({'fiscalyear_id': self.pool.get('account.period').browse(cr,uid,period_id,context).fiscalyear_id.id})
                    name = seq_obj.next_by_id(cr, uid, voucher.journal_ids.sequence_id.id, context=c)
                else:
                    raise osv.except_osv(_('Error!'),
                            _('Please define a sequence on the journal.'))
                if not voucher.number:
                    ref = name.replace('/','')
                else:
                    ref = voucher.number
                journal_id = voucher.journal_ids.id
            voucher_date2mv = voucher.date

            if date_switch:
#            if voucher.release_number:
                voucher_date2mv = voucher.cheque_release_date or voucher.check_date or voucher.date

            if voucher.od_with_out_allocaion:
                #Used to get the back accounts
                if voucher.type in ('sale', 'receipt'):
                    rele_account_id = voucher.journal_ids and voucher.journal_ids.default_debit_account_id
                elif voucher.type in ('purchase', 'payment'):
                    rele_account_id = voucher.journal_ids and voucher.journal_ids.default_credit_account_id
                else:
                    rele_account_id = voucher.journal_ids and voucher.journal_ids.default_credit_account_id or voucher.journal_ids.default_debit_account_id

                release_context={
                                'pdc_allocation_release':True,
                                'journal_id':voucher.journal_ids.id,
                                'account_id':rele_account_id and rele_account_id.id,
                                'od_check_clearing_acc_id':'',
                                'od_with_out_allocaion':False,
                                'od_fwith_out_allocaion':True,
                                'od_related_voucher_id': voucher.id,
                                'payment_type' :voucher.payment_type,
                                'type':voucher.type,
                                }
                release_voucher_id = voucher.copy(default=release_context)
#                account_ids=[voucher.od_check_clearing_acc_id,voucher.partner_id.property_account_receivable]
#                self.pool.get('account.automatic.reconcile').reconcile_on_releasepdc(cr,uid,account_ids,context)
#                print "dddddddd\n\n\n\ndddd",release_voucher_id

            move = {
                'name': name,
                'journal_id': journal_id,
                'narration': voucher.narration,
                #'date': voucher.check_bank and voucher.check_date or voucher.date,
#                'date': voucher.cheque_release_date or voucher.check_date or voucher.date, #changed as per avinash
                'date': voucher_date2mv, #changed as per yas sunil-fakru suggested
                'ref': ref,
#                'pos_shop_id': voucher.shop_id.id or False,
                'period_id': period_id or voucher.period_id.id,
            }
            #create move
            move_id = move_pool.create(cr, uid, move, context=context)
            # Get the name of the account_move just created
            name = move_pool.browse(cr, uid, move_id, context=context).name
            
            company_currency = self._get_company_currency(cr, uid, voucher.id, context)
            current_currency = self._get_current_currency(cr, uid, voucher.id, context)
            
            dr_account_id = False
            cr_account_id = False

#For Bridge Account
            clearance_dr_account_id = False
            clearance_cr_account_id = False
            
            if voucher.type in ('sale','receipt'):
                dr_account_id = voucher.check_clearance_acc_ids.id
                cr_account_id = voucher.journal_id.default_credit_account_id.id

                if voucher.od_with_out_allocaion:
                    clearance_dr_account_id = voucher.od_check_clearing_acc_id.id
                    clearance_cr_account_id = voucher.partner_id.property_account_receivable.id
#                    if voucher.state <> 'draft': ###########Lithinn
#                        print "##########\n\n\n#########################3",clearance_cr_account_id
#                        clearance_cr_account_id = voucher.od_check_clearing_acc_id.id
#                print "###########!!!!!!!!!!!!!!!@@@@@@@@@XX@@@",clearance_cr_account_id



            elif voucher.type in ('purchase', 'payment'):
                dr_account_id = voucher.journal_id.default_debit_account_id.id
                cr_account_id = voucher.check_clearance_acc_ids.id

                if voucher.od_with_out_allocaion:
#                    clearance_dr_account_id = voucher.partner_id.property_account_receivable.id
                    clearance_dr_account_id = voucher.journal_id.default_debit_account_id.id
                    clearance_cr_account_id = voucher.od_check_clearing_acc_id.id
#                    if voucher.state <> 'draft': ###########Lithinn
#                        print "##########\n\n\n#########################3",clearance_cr_account_id
#                        clearance_cr_account_id = voucher.od_check_clearing_acc_id.id



            elif voucher.payment_type =='expense':
                if voucher.state == 'draft':
                    cr_account_id = voucher.journal_id.default_credit_account_id.id
                else:
                    dr_account_id = voucher.journal_id.default_debit_account_id.id
                    cr_account_id = voucher.check_clearance_acc_ids.id
            elif voucher.payment_type =='income':
                if voucher.state == 'draft':
                    dr_account_id = voucher.journal_id.default_debit_account_id.id
                else:
                    dr_account_id = voucher.check_clearance_acc_ids.id
                    cr_account_id = voucher.journal_id.default_credit_account_id.id
            else:
                dr_account_id = voucher.journal_id.default_debit_account_id.id
                cr_account_id = voucher.journal_id.default_credit_account_id.id
    
            #Dr. entry
            if voucher.payment_type =='expense' and voucher.state == 'draft':
                for acc_info in voucher.income_expense_ids:
                    line_desc = acc_info.name or voucher.name or '/'
                    expense_line_ids = move_line_pool.create(cr, uid, self._get_expense_entries(cr, uid, voucher, journal_id, move_id, acc_info, company_currency, current_currency, context), context)
                    self.pool.get('account.move.line').write(cr,uid,[expense_line_ids],{'name':line_desc},context)
            else:
#                move_line_pool.create(cr, uid, self._get_partner_dr_entries(cr, uid, voucher, journal_id, move_id, dr_account_id, company_currency, current_currency, context), context)
                #Extra added for getting bridge account dr #Lithin #Customer paymnet values
                if voucher.od_with_out_allocaion and voucher.state <> 'draft':
                    move_line_pool.create(cr, uid, self._get_partner_dr_entries(cr, uid, voucher, journal_id, move_id, clearance_dr_account_id, company_currency, current_currency, context), context)
                else:
                    move_line_pool.create(cr, uid, self._get_partner_dr_entries(cr, uid, voucher, journal_id, move_id, dr_account_id, company_currency, current_currency, context), context)

            #Cr. Entry
            if voucher.payment_type =='income' and voucher.state == 'draft':
                for acc_info in voucher.income_expense_ids:
                    move_line_pool.create(cr, uid, self._get_income_entries(cr, uid, voucher, journal_id, move_id, acc_info, company_currency, current_currency, context), context)
            else:
                if voucher.od_with_out_allocaion and voucher.state <> 'draft' and voucher.type in ('purchase', 'payment'):
                    cr_account_id = clearance_cr_account_id
                move_line_pool.create(cr, uid, self._get_partner_cr_entries(cr, uid, voucher, journal_id, move_id, cr_account_id, company_currency, current_currency, context), context)
                #added to get the cr lines
#                if voucher.od_with_out_allocaion:
#                    move_line_pool.create(cr, uid, self._get_partner_cr_entries(cr, uid, voucher, journal_id, move_id, clearance_cr_account_id, company_currency, current_currency, context), context)
            if voucher.state == 'draft':
                self.write(cr, uid, ids, {
                'move_id': move_id,
                'state': 'posted',
                'number': name,
                })
            else:
                self.write(cr, uid, ids, {'check_clear': True, 'release_number': name})
        account_ids=[voucher.journal_id.default_credit_account_id,voucher.journal_ids.default_credit_account_id]
        self.pool.get('account.automatic.reconcile').reconcile_on_releasepdc(cr,uid,account_ids,context)
        return True
    
    def action_bounce_check(self, cr, uid, ids, context=None):
        move_pool = self.pool.get('account.move')
        
        for voucher in self.browse(cr, uid, ids, context):
            ref = voucher.number
        move_ids = move_pool.search(cr,uid,[('ref','=',ref)])
        
        reconcile_pool = self.pool.get('account.move.reconcile')
        recs = []
        for line_id in move_ids:
            move_brw = move_pool.browse(cr, uid, line_id, context)
            for line in move_brw.line_id: 
                if line.reconcile_id:
                    recs += [line.reconcile_id.id]
                if line.reconcile_partial_id:
                    recs += [line.reconcile_partial_id.id]
            reconcile_pool.unlink(cr, uid, recs)
        
        if move_ids:
            move_pool.button_cancel(cr, uid, move_ids)
            move_pool.unlink(cr, uid, move_ids) 
        
        self.write(cr, uid, ids, {'check_clear':False, 'check_bounce':True})
        return self.cancel_voucher(cr, uid, ids, context=context)
    
    def action_cancel_draft(self, cr, uid, ids, context=None):
        """Override method to update some boolean fields, so that in draft they should be false"""
        self.write(cr, uid, ids, {'check_clear':False, 'check_bounce':False})
        return super(account_voucher, self).action_cancel_draft(cr, uid, ids, context)


    def onchange_journal(self, cr, uid, ids, journal_id, line_ids, tax_id, partner_id, date, amount, ttype, company_id, context=None):
        """ Inherit onchange_journal to check journal is PDC or not"""
        vals = super(account_voucher, self).onchange_journal(cr, uid, ids, journal_id, line_ids, tax_id, partner_id, date, amount, ttype, company_id, context)
        journal_pool = self.pool.get('account.journal')
        if journal_id:
            journal = journal_pool.browse(cr, uid, journal_id, context=context)
            od_account_id = journal.default_credit_account_id or journal.default_debit_account_id
            vals['value'].update({'account_id':od_account_id})
            if journal.pdc_payable or journal.pdc_receivable:
                vals['value'].update({'pdc_check': True})
            else:
                vals['value'].update({'pdc_check': False})
            if journal.type == 'bank':
                vals['value'].update({'check_bank':True, 'check_date':time.strftime('%Y-%m-%d'), 'cheque_release_date':time.strftime('%Y-%m-%d'),'all_entries':True})
            else:
                vals['value'].update({'check_bank':False, 'check_date':False, 'all_entries':False})
            if journal.income_expense:
                vals['value'].update({'recurring_bool':True})
            else:
                vals['value'].update({'recurring_bool':False})
        return vals
    
    def onchange_partner_id(self, cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, context=None):
        """Override method to add payment type in account voucher"""
        partner_obj = self.pool.get('res.partner')
        res = super(account_voucher, self).onchange_partner_id(cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, context)
        if partner_id and res:
            part_data = partner_obj.browse(cr, uid, partner_id)
            if part_data.customer:
                res['value']['payment_type'] = 'cust_payment'
            if part_data.supplier:
                res['value']['payment_type'] = 'sup_payment'
        return res
        
    
    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default ={}
        default['pdc_check'] = False
        default['check_clear'] = False
        default['check_bounce'] = False
        if not default.get('pdc_allocation_release'):
#            return super(account_voucher, self).copy(cr, uid, id, default, context)
            raise osv.except_osv(_('Warning !'),
                _('You are not allowed to Duplicate!!\nCreate a new one'))
        return super(account_voucher, self).copy(cr, uid, id, default, context)
    
    
    def onchange_payment_type(self, cr, uid, ids, payment_type, context=None):
        acc_journal = self.pool.get('account.journal')
        res = {}
        f_ids = []
        if payment_type == 'cust_payment':
            res['type'] = 'receipt'
            res['payment_type'] = 'cust_payment'
            f_ids = acc_journal.search(cr, uid, [('type','in',['bank', 'cash']), ('pdc_payable','=',False), ('income_expense','=',False)])
            return {'value': res, 
            'domain': {
                'partner_id': [('customer', '=', True)], 'journal_id': [('id', 'in', f_ids)],
            } }
        elif payment_type == 'sup_payment':
            res['type'] = 'payment'
            res['payment_type'] = 'sup_payment'
            f_ids = acc_journal.search(cr, uid, [('type','in',['bank', 'cash']), ('pdc_receivable','=',False), ('income_expense','=',False)])
            return {'value': res,
            'domain': {
                'partner_id': [('supplier', '=', True)], 'journal_id': [('id', 'in', f_ids)],
            } }
        elif payment_type == 'expense':
            res['type'] = ''
            res['payment_type'] = 'expense'
            res['partner_id'] = False
            f_ids = acc_journal.search(cr, uid, [('type','in',['bank', 'cash']), ('pdc_receivable','=',False)])
            return {'value': res, 
            'domain': {
                'journal_id': [('id', 'in', f_ids)],
            } }
        elif payment_type == 'income':
            res['type'] = ''
            res['payment_type'] = 'income'
            res['partner_id'] = False
            f_ids = acc_journal.search(cr, uid, [('type','in',['bank', 'cash']), ('pdc_payable','=',False)])
            return {'value': res,
            'domain': {
                'journal_id': [('id', 'in', f_ids)],
            } }
        else:
            res['type'] = ''
            res['partner_id'] = False
            return {'value': res,
            'domain': {
                'partner_id': [('id', '!=', False )],
            } }

    def onchange_check_date(self,cr, uid,ids,check_date,context=None):
        return {'value':{'cheque_release_date':check_date}}
        
    _columns = {
        'od_manual_allocate':fields.boolean('Allocate manually'),
        'check_no': fields.char('Cheque No', size=20, readonly=True, states={'draft':[('readonly',False)]}),
        'check_date': fields.date('Cheque Date', readonly=True, states={'draft':[('readonly',False)]}),
        'cheque_release_date': fields.date('Cheque Release Date', readonly=True),
        'bank_ids': fields.many2one('res.partner.bank', 'Bank Name', readonly=True, states={'draft':[('readonly',False)]}),
        'pdc_check': fields.boolean('PDC Check'),
        'check_bank':fields.boolean('Check Bank'),
        'check_clear': fields.boolean('Release Cheque'),
        'check_bounce': fields.boolean('Bounce cheque'),

        'od_with_out_allocaion': fields.boolean('W/O Allocation'),
        'od_fwith_out_allocaion': fields.boolean('FW/O Allocation'),
        'od_related_voucher_id': fields.many2one('account.voucher',string="Related Voucher"),


        'od_check_clearing_acc_id': fields.many2one('account.account', 'Check Clearing Account', help="check clearance Account for PDC Receivable/payable"),


        'payment_type': fields.selection([('cust_payment', 'Customer Payment'), ('sup_payment', 'Supplier Payment'), ('expense', 'Expense'), ('income', 'Income')], 'Type', size=24, readonly=True, states={'draft':[('readonly',False)]}),
        'od_payment_type': fields.selection([('expense', 'Expense'), ('income', 'Income')], 'Type', size=24, readonly=True, states={'draft':[('readonly',False)]}),
        'check_clearance_acc_ids': fields.many2one('account.account', 'Check Clearance Account(Deposit Bank)', help="check clearance Account for PDC Receivable/payable"),
        'journal_ids': fields.many2one('account.journal', 'Release Journal'),
        #'account_id':fields.many2one('account.account', 'Account', readonly=True, states={'draft':[('readonly',False)]}),
        'all_entries': fields.boolean('All Entries', help="used to show all entries (customer, supplier, income and expence entries) in PDC views"),
        'income_expense_ids': fields.one2many('income_expense.accounts', 'account_voucher_id', 'Account Information'),
        'release_number': fields.char('Release Line Number', size=20),
        }
    _defaults = {  
        }

account_voucher()

class income_expense_accounts(osv.osv):
    _name = "income_expense.accounts"
    _description = "Income Expense Account Details"
    _columns = {
        'account_voucher_id': fields.many2one('account.voucher', 'Voucher'),
        'name': fields.char('Description', size=60, help='Description about account information line'),
        'account_id': fields.many2one('account.account', 'Account', required=True, ondelete="cascade", domain=[('type','<>','view'), ('type', '<>', 'closed')], select=2),
        'analytic_account_id': fields.many2one('account.analytic.account', 'Analytic Account'),
        'amount_currency': fields.float('Amount', help="The amount expressed in expense/income entries.", digits_compute=dp.get_precision('Account')),
        'partner_id':fields.many2one('res.partner','Partner')
        }
    _defaults = {  
        'amount_currency': 0.0,
        }
income_expense_accounts()


class account_move_line(osv.osv):
    _inherit = "account.move.line"
    _description = "Inherit Journal Items"
    _columns = {
        'name': fields.char('Narration', size=64, required=True),
        }
account_move_line()

class res_partner(osv.osv):
    _inherit = "res.partner"
    _description = "Res partner Update"
    
    def default_get(self, cr, uid, fields, context=None):
        
        if context.get('payment_type') == 'sup_payment':
            context.update({'default_customer':False, 'default_supplier':True, 'search_default_supplier': True})
        return super(res_partner, self).default_get(cr, uid, fields, context=context)
    
res_partner()


class account_automatic_reconcile(osv.osv_memory):
    _inherit = 'account.automatic.reconcile'
    _description = 'Automatic Reconcile'
    
    def reconcile_on_releasepdc(self, cr, uid, account_ids, context=None):
        move_line_obj = self.pool.get('account.move.line')
        obj_model = self.pool.get('ir.model.data')
        if context is None:
            context = {}
#        form = self.browse(cr, uid, ids, context=context)[0]
#        print form
        max_amount = 0.0
#        power = form.power
#        allow_write_off = form.allow_write_off
        allow_write_off=False
        reconciled = unreconciled = 0
        if not account_ids:
            raise osv.except_osv(_('User Error!'), _('You must select accounts to reconcile.'))
        for account_id in account_ids:
            if account_id:
                params = (account_id.id,)
                if not allow_write_off:
                    query = """SELECT partner_id FROM account_move_line WHERE account_id=%s AND reconcile_id IS NULL
                    AND state <> 'draft' GROUP BY partner_id
                    HAVING ABS(SUM(debit-credit)) = 0.0 AND count(*)>0"""
                else:
                    query = """SELECT partner_id FROM account_move_line WHERE account_id=%s AND reconcile_id IS NULL
                    AND state <> 'draft' GROUP BY partner_id
                    HAVING ABS(SUM(debit-credit)) < %s AND count(*)>0"""
                    params += (max_amount,)
                # reconcile automatically all transactions from partners whose balance is 0
                cr.execute(query, params)
                partner_ids = [id for (id,) in cr.fetchall()]
                for partner_id in partner_ids:
                    cr.execute(
                        "SELECT id " \
                        "FROM account_move_line " \
                        "WHERE account_id=%s " \
                        "AND partner_id=%s " \
                        "AND state <> 'draft' " \
                        "AND reconcile_id IS NULL",
                        (account_id.id, partner_id))
                    line_ids = [id for (id,) in cr.fetchall()]
                    if line_ids:
                        reconciled += len(line_ids)
    #                    if allow_write_off:
    #                        move_line_obj.reconcile(cr, uid, line_ids, 'auto', form.writeoff_acc_id.id, form.period_id.id, form.journal_id.id, context)
    #                    else:
                        move_line_obj.reconcile_partial(cr, uid, line_ids, 'manual', context=context)
    
                # get the list of partners who have more than one unreconciled transaction
                cr.execute(
                    "SELECT partner_id " \
                    "FROM account_move_line " \
                    "WHERE account_id=%s " \
                    "AND reconcile_id IS NULL " \
                    "AND state <> 'draft' " \
                    "AND partner_id IS NOT NULL " \
                    "GROUP BY partner_id " \
                    "HAVING count(*)>1",
                    (account_id.id,))
                partner_ids = [id for (id,) in cr.fetchall()]
                #filter?
                for partner_id in partner_ids:
                    # get the list of unreconciled 'debit transactions' for this partner
                    cr.execute(
                        "SELECT id, debit " \
                        "FROM account_move_line " \
                        "WHERE account_id=%s " \
                        "AND partner_id=%s " \
                        "AND reconcile_id IS NULL " \
                        "AND state <> 'draft' " \
                        "AND debit > 0 " \
                        "ORDER BY date_maturity",
                        (account_id.id, partner_id))
                    debits = cr.fetchall()
    
                    # get the list of unreconciled 'credit transactions' for this partner
                    cr.execute(
                        "SELECT id, credit " \
                        "FROM account_move_line " \
                        "WHERE account_id=%s " \
                        "AND partner_id=%s " \
                        "AND reconcile_id IS NULL " \
                        "AND state <> 'draft' " \
                        "AND credit > 0 " \
                        "ORDER BY date_maturity",
                        (account_id.id, partner_id))
                    credits = cr.fetchall()
    
                    (rec, unrec) = self.do_reconcile(cr, uid, credits, debits, max_amount, 2, False, False, False, context)
                    reconciled += rec
                    unreconciled += unrec
    
                # add the number of transactions for partners who have only one
                # unreconciled transactions to the unreconciled count
                partner_filter = partner_ids and 'AND partner_id not in (%s)' % ','.join(map(str, filter(None, partner_ids))) or ''
                cr.execute(
                    "SELECT count(*) " \
                    "FROM account_move_line " \
                    "WHERE account_id=%s " \
                    "AND reconcile_id IS NULL " \
                    "AND state <> 'draft' " + partner_filter,
                    (account_id.id,))
                additional_unrec = cr.fetchone()[0]
                unreconciled = unreconciled + additional_unrec
#        context.update({'reconciled': reconciled, 'unreconciled': unreconciled})
        model_data_ids = obj_model.search(cr,uid,[('model','=','ir.ui.view'),('name','=','account_automatic_reconcile_view1')])
        resource_id = obj_model.read(cr, uid, model_data_ids, fields=['res_id'])[0]['res_id']
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.automatic.reconcile',
            'views': [(resource_id,'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
        }
        
account_automatic_reconcile()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


