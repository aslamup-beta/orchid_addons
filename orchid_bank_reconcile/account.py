# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning

class account_move_line(models.Model):
    _inherit = 'account.move.line'

    @api.one
    @api.depends('move_id')
    def _compute_check_no(self):
        if self.move_id:
            account_voucher_id = self.env['account.voucher'].search([('move_id', '=', self.move_id.id)])
            if account_voucher_id:
                self.od_check_vnumber = account_voucher_id.check_no or False

    od_reconcile_date = fields.Date(string='Bank Date',default=False,copy=False)
    od_check_vnumber = fields.Char(string='Check Number',readonly="1",compute='_compute_check_no')


    def od_list_accounts(self, cr, uid, context=None):
        ng = dict(self.pool.get('account.journal').name_search(cr,uid,'',[('type','=','bank')]))
        journal_ids = ng.keys()
        account_ids = []
        for journal in self.pool.get('account.journal').browse(cr, uid, journal_ids, context=context):
            credit_acc_id = journal.default_credit_account_id and journal.default_credit_account_id.id or ''
            debit_acc_id = journal.default_debit_account_id and journal.default_debit_account_id.id or ''
            credit_acc_id and (credit_acc_id not in account_ids) and account_ids.append(credit_acc_id)
            debit_acc_id and (debit_acc_id not in account_ids) and account_ids.append(debit_acc_id)
        return self.pool.get('account.account').name_get(cr, uid, account_ids, context=context)


    def od_list_journals(self, cr, uid, context=None):
        ng = dict(self.pool.get('account.journal').name_search(cr,uid,'',[('type','=','bank')]))
        ids = ng.keys()
        result = []
        for journal in self.pool.get('account.journal').browse(cr, uid, ids, context=context):
            result.append((journal.id,ng[journal.id],journal.type,
                bool(journal.currency),bool(journal.analytic_journal_id)))
        return result

    def od_get_periods(self):
        
        period_pool = self.env['account.period']
        periods = [period.id for period in period_pool.search()] 
        return periods


    def od_list_periods(self, cr, uid, context=None):
        ids = self.pool.get('account.period').search(cr,uid,['|',('od_sequence','=',0),('special','=',False)])
        return self.pool.get('account.period').name_get(cr, uid, ids, context=context)
    
    
    
    
#     def od_rm_posted(self,cr,uid,query,query_params):
#         
#         
#         new_query_param = query_params + tuple(not_posted_moves)
#         query = query + 'AND move_id NOT IN %s'
#         return query,new_query_param
    def od_get_query(self,query,account_id,period_ids,from_date,to_date):
       
        if from_date and to_date:
            query_params = (account_id,tuple(period_ids),from_date,to_date)
            query = query + ' AND (date>=%s) AND (date <=%s)'
        if from_date and not to_date:
            query_params = (account_id,tuple(period_ids),from_date)
            query = query+ ' AND (date>=%s) '
        if to_date and not from_date:   
            query_params = (account_id,tuple(period_ids),to_date)
            query = query+ ' AND (date<=%s)  '
        if not (from_date or to_date):
            query_params = (account_id,tuple(period_ids))
        
        return query,query_params
    def od_book_bank_balance(self, cr, uid,from_date,to_date, context=None):
        if context is None:
            context = {}
       
        
        ng = dict(self.pool.get('account.journal').name_search(cr,uid,'',[('type','=','bank')]))
        journal_ids = ng.keys()
        account_ids = []
        result = {
            'book_balance':0.0,
            'bank_balance':0.0,
            'fc_book_balance':0.0,
            'fc_bank_balance':0.0,
            'reconciled_balance':0.0,
            'unconciled_balance':0.0,
        }
        period_ids = self.pool.get('account.period').search(cr,uid,['|',('od_sequence','=',0),('special','=',False)])

        for journal in self.pool.get('account.journal').browse(cr, uid, journal_ids, context=context):
            credit_acc_id = journal.default_credit_account_id and journal.default_credit_account_id.id or ''
            debit_acc_id = journal.default_debit_account_id and journal.default_debit_account_id.id or ''
            credit_acc_id and (credit_acc_id not in account_ids) and account_ids.append(credit_acc_id)
            debit_acc_id and (debit_acc_id not in account_ids) and account_ids.append(debit_acc_id)

        account_id = account_ids[0] or ''
        if context.has_key('account_id') and context.get('account_id'):
            account_id = context.get('account_id')

#book Balance

      
        qry ="SELECT (sum(debit) - sum(credit)) as bank_balance FROM account_move_line WHERE account_id = %s AND period_id IN %s AND move_id in (select id from account_move where state='posted')"
        query,query_params = self.od_get_query(qry, account_id, period_ids, from_date, to_date)
       
#         cr.execute('SELECT (sum(debit) - sum(credit)) as bank_balance FROM '+self._table+' '\
#                 'WHERE account_id = %s AND period_id IN %s',(account_id,tuple(period_ids)))
#         
        cr.execute(query,query_params)
        res = cr.fetchone()
        book = res[0] or 0.0
        if res: result['book_balance'] = book


#bank Balance 
#         query_params = ''
#         query = ''
#         print "from date>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",type(from_date),to_date
#         if from_date and to_date:
#             query_params = (account_id,tuple(period_ids),from_date,to_date)
#             query = 'SELECT (sum(debit) - sum(credit)) as bank_balance FROM '+self._table+' WHERE account_id = %s AND od_reconcile_date is not null AND period_id IN %s AND (date>=%s) AND (date <=%s)'
#         if from_date and not to_date:
#             query_params = (account_id,tuple(period_ids),from_date)
#             query = 'SELECT (sum(debit) - sum(credit)) as bank_balance FROM '+self._table+' WHERE account_id = %s AND od_reconcile_date is not null AND period_id IN %s AND (date>=%s) '
#         if to_date and not from_date:   
#             query_params = (account_id,tuple(period_ids),to_date)
#             query = 'SELECT (sum(debit) - sum(credit)) as bank_balance FROM '+self._table+' WHERE account_id = %s AND od_reconcile_date is not null AND  period_id IN %s AND (date<=%s)  '
#             
#         if not from_date and not to_date:
#             query_params = (account_id,tuple(period_ids))
#             query='SELECT (sum(debit) - sum(credit)) as bank_balance FROM '+self._table+' WHERE account_id = %s AND od_reconcile_date is not null AND period_id IN %s'
#         cr.execute('SELECT (sum(debit) - sum(credit)) as bank_balance FROM '+self._table+' '\
#              '   'WHERE account_id = %s AND od_reconcile_date is not null AND period_id IN %s',(account_id,tuple(period_ids)))
        qry1 = 'SELECT (sum(debit) - sum(credit)) as bank_balance FROM '+self._table+' '\
                 'WHERE account_id = %s AND od_reconcile_date is not null AND period_id IN %s '
        query,query_params = self.od_get_query(qry1, account_id, period_ids,from_date, to_date)
        cr.execute(query,query_params)
        res = cr.fetchone()
        bank = res[0] or 0.0
        if res: result['bank_balance'] = bank 
##Reconciled Balance
        if bank: result['reconciled_balance'] = bank or 0.0
        result['unconciled_balance'] = book - bank

#Currency bank Balance
        cr.execute('SELECT sum(amount_currency) as amount_currency_book_balance FROM '+self._table+' '\
                'WHERE account_id = %s AND period_id IN %s',(account_id,tuple(period_ids)))
        res = cr.fetchone()
        if res: result['fc_book_balance'] = res[0] or 0.0

#Currency book Balance
        cr.execute('SELECT sum(amount_currency) as amount_currency_bank_balance FROM '+self._table+' '\
                'WHERE account_id = %s AND od_reconcile_date is not null AND period_id IN %s',(account_id,tuple(period_ids)))
        res = cr.fetchone()
        if res: result['fc_bank_balance'] = res[0] or 0.0


        return result

    def _default_get(self, cr,uid, fields,context=None):
        data = super(account_move_line,self)._default_get(cr, uid,fields,context)
        ng = dict(self.pool.get('account.journal').name_search(cr,uid,'',[('type','=','bank')]))
        journal_ids = ng.keys()
        account_ids = []
        for journal in self.pool.get('account.journal').browse(cr, uid, journal_ids, context=context):
            credit_acc_id = journal.default_credit_account_id and journal.default_credit_account_id.id or ''
            debit_acc_id = journal.default_debit_account_id and journal.default_debit_account_id.id or ''
            credit_acc_id and (credit_acc_id not in account_ids) and account_ids.append(credit_acc_id)
            debit_acc_id and (debit_acc_id not in account_ids) and account_ids.append(debit_acc_id)
#        if not data.get('account_id'): data['account_id'] = account_ids[0]
#        if not data.get('journal_id'):
#            data['journal_id'] = journal_ids and journal_ids[0]
        return data







