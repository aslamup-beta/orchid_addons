# -*- coding: utf-8 -*-
from openerp.osv import osv
from openerp.tools.translate import _
from openerp.osv import fields, osv

class account_move(osv.osv):
    _inherit = 'account.move'

    _columns = {
        'od_voucher_type': fields.selection([
            ('asset', 'Asset'),
            ('general', 'General'),
            ('inventory', 'Inventory'),
            ], 'Voucher Type'),

    }

    _defaults = {
        'od_voucher_type': 'general',

    }
  

#{'search_default_draft': 1,'od_voucher_type':'general'}
#{'search_default_draft': 1,'od_voucher_type':'asset'}
#{'search_default_draft': 1,'od_voucher_type':'inventory'}


    def print_journal_entry(self, cr, uid, ids, context=None):
        """
        To get the date and print the report
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param context: A standard dictionary
        @return : retrun report
        """
        if context is None:
            context = {}
        datas = {'ids': ids}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'journal_entry',
            'datas': datas,
        }

class account_move_line(osv.osv):
    _inherit = 'account.move.line'


    def onchange_od_amount_currency(self, cr, uid, ids,company_id, from_currency_id,from_amount,debit,credit, context=None):
        res={}
        cur_obj= self.pool.get('res.currency')
        company_obj = self.pool.get('res.company')
        if from_currency_id:
            to_currency_id = company_obj.browse(cr, uid, company_id).currency_id and company_obj.browse(cr, uid, company_id).currency_id.id
            exchange_value= cur_obj.compute(cr, uid, from_currency_id, to_currency_id, from_amount)
            if exchange_value < 0:
                res = {'value':{'credit':(exchange_value * -1)}}
            else:
                res = {'value':{'debit':exchange_value}}
        return res


