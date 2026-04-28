# -*- encoding: utf-8 -*-
from openerp.osv import fields
from openerp.osv import osv

class income_expense_accounts(osv.osv):
    _inherit = "income_expense.accounts"
    _columns = {
        'od_cost_centre_id': fields.many2one('od.cost.centre','Cost Centre'),
        'od_warehouse_id': fields.many2one('stock.warehouse','Warehouse'),
    }


class account_voucher(osv.osv):
    _inherit = 'account.voucher' 
    _description = 'Update for Bank type voucher'

#    _columns = {
#        'od_payment_type': fields.char('Payment Type'),
#    }

#     def default_get(self, cr, uid, ids, context=None):
#         res = super(account_voucher, self).default_get(cr, uid, ids, context=context)
#         if res:
#             if 'journal_id' in res.keys():
#                 journal_id = res['journal_id']
#                 journal_obj = self.pool.get('account.journal').browse(cr,uid,journal_id,context)
#         
#                 res.update({'reference': journal_obj.name,'od_acc_payee':True})
#         return res

#    def onchange_journal(self, cr, uid, ids, journal_id, line_ids, tax_id, partner_id, date, amount, ttype, company_id, context=None):
#        res = super(account_voucher, self).onchange_journal(cr, uid, ids, journal_id, line_ids, tax_id, partner_id, date, amount, ttype, company_id, context)
        




    def _get_expense_entries(self, cr, uid, voucher, journal_id, move_id, acc_info, company_currency, current_currency, context=None):
        dr_move_line =  super(account_voucher, self)._get_expense_entries(cr,uid,voucher,journal_id,move_id,acc_info,company_currency,current_currency,context=context)
        dr_move_line.update({'od_cost_centre_id':acc_info.od_cost_centre_id and acc_info.od_cost_centre_id.id or False})
        return dr_move_line

    def _get_income_entries(self, cr, uid, voucher, journal_id, move_id, acc_info, company_currency, current_currency, context=None):
        cr_move_line = super(account_voucher, self)._get_income_entries(cr, uid, voucher, journal_id, move_id, acc_info, company_currency, current_currency, context=context)
        cr_move_line.update({'od_cost_centre_id':acc_info.od_cost_centre_id and acc_info.od_cost_centre_id.id or False})
        return cr_move_line
    

    def _get_partner_dr_entries(self, cr, uid, voucher, journal_id, move_id, dr_account_id, company_currency, current_currency, context=None):
        dr_move_line = super(account_voucher, self)._get_partner_dr_entries(cr, uid, voucher, journal_id, move_id, dr_account_id, company_currency, current_currency, context=context)
#        dr_move_line.update({'od_cost_centre_id':acc_info.od_cost_centre_id and acc_info.od_cost_centre_id.id or False})
        return dr_move_line
    
    def _get_partner_cr_entries(self, cr, uid, voucher, journal_id, move_id, cr_account_id, company_currency, current_currency, context=None):
        cr_move_line = super(account_voucher,self)._get_partner_cr_entries(cr, uid, voucher, journal_id, move_id, cr_account_id, company_currency, current_currency, context=context)
#        cr_move_line.update({'od_cost_centre_id':acc_info.od_cost_centre_id and acc_info.od_cost_centre_id.id or False})
        return cr_move_line

