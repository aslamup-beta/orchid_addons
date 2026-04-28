import time
from openerp.report import report_sxw
from openerp.addons.account.report.account_balance import account_balance
from openerp.tools.translate import _
from datetime import datetime, date, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from openerp.osv import osv

class account_balance(account_balance):
    _inherit = 'report.account.account.balance'
    def __init__(self, cr, uid, name, context=None):
        super(account_balance, self).__init__(cr, uid, name, context=context)
        self.od_prev_result_acc = []
        self.od_next_result_acc = []
        self.context = context

    def lines(self, form, ids=None, done=None):
        od_next_done = done
        required_currency_id = form.get('od_currency_id') and form.get('od_currency_id')[0] or False
        robj_move = self.pool.get('account.move.line')
        cust_query = robj_move._query_get(self.cr, self.uid, obj='l', context={})
        
        def od_get_partner_ids():
            query1 = """
                    SELECT DISTINCT res_partner.id AS id                    
                        FROM res_partner,account_move_line AS l, 
                        account_account, account_move am                
                        WHERE (l.account_id=account_account.id)                     
                        AND (l.move_id=am.id)                     
                        AND (am.state ='posted')                    
                        AND (account_account.type ='receivable')                     
                        AND account_account.active                    
                        AND ((l.reconcile_id IS NULL)                    
                        OR (l.reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date >'%s' )))  """%(form['date_to'])
                    
            query2= """
                        AND (l.partner_id=res_partner.id)                    
                        AND (l.date <= '%s' )
                     """%(form['date_to'])
                    
#             query = query1 +cust_query + query2
            
            query = query1  + query2
                    
            self.cr.execute(query)
            partners=self.cr.fetchall()
            partner_ids = [x[0] for x in partners]
            print "partner ids>>>>>>>>>>>>>>>>>",partner_ids
            return partner_ids
        def od_get_move_ids(partner_ids,recv_account_id):
            qr1= """
                       SELECT l.move_id                     
                        FROM account_move_line AS l, account_account, account_move am 
                        WHERE (l.account_id = account_account.id) 
                        AND (l.move_id=am.id)
                        AND (am.state ='posted')                    
                        AND (account_account.type ='receivable')                    
                        AND (l.partner_id IN %s)                   
                        AND ((l.reconcile_id IS NULL)                    
                        OR (l.reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date >'%s' )))  
                     """%(tuple(partner_ids),form['date_to'])
            qr2= """
                       AND account_account.active                    
                        AND (l.date <='%s')
                        AND (l.account_id=%s)                                                                                
                        GROUP BY l.partner_id,l.move_id
                        
                    
                    """%(form['date_to'],recv_account_id)
                      
                    
#             qr =qr1+cust_query + qr2
            
            qr =qr1 + qr2
            
            self.cr.execute(qr)
            moves =self.cr.fetchall()
            move_ids= [x[0] for x in moves]
            print "move ids>>>>>>>>>>>>>>>>>",move_ids
            return move_ids
        
        def od_get_total_rec_amount(partner_ids,recv_account_id):
            print "partner ids????????????????",partner_ids
            qr1= """
                       SELECT l.partner_id,SUM(l.debit-l.credit) as balance                     
                        FROM account_move_line AS l, account_account, account_move am 
                        WHERE (l.account_id = account_account.id) 
                        AND (l.move_id=am.id)
                        AND (am.state ='posted')                    
                        AND (account_account.type ='receivable')                    
                        AND (l.partner_id IN %s)                   
                        AND ((l.reconcile_id IS NULL)                    
                        OR (l.reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date >'%s' ))) AND  
                     """%(tuple(partner_ids),form['date_to'])
            qr2= """
                        account_account.active                    
                        AND (l.date <='%s')
                         AND (l.account_id=%s)                                                                                         
                        GROUP BY l.partner_id
                    
                    """%(form['date_to'],recv_account_id)
                      
                    
            qr =qr1 + qr2
            print "query>>>>>>>>>>>>>>>>>>>>>>>cust rece>>>>>>>>>>>",qr
            self.cr.execute(qr)
            partner_amount =self.cr.fetchall()
            amount= sum([x[1] for x in partner_amount])
            print "total amout>>>>>>>>>>>>>>>>>",amount
            return amount
            
        
        
        def od_get_open_analytic_ids(company_id):
            open_an_qr = "select id from account_analytic_account where state not in ('close','cancelled') and company_id=%s"%company_id
            self.cr.execute(open_an_qr)
            open_analytic =self.cr.fetchall()
            analytic_ids= [x[0] for x in open_analytic]
            print "analyti ids>>>>>>>>>>>>>>>>>",analytic_ids
            return analytic_ids
        def get_advance_invoice_account():
            #uae 4006
            #ksa 5332
            return [4006,5332]
        def get_analytic_amounts(company_id,recv_account_id):
            print "getting amount"
            partner_ids = od_get_partner_ids()
            move_ids = od_get_move_ids(partner_ids,recv_account_id)
            analytic_ids = od_get_open_analytic_ids(company_id)
            advance_invoice_acc_ids = get_advance_invoice_account()
            query ="""
             select sum(l.credit - l.debit) from account_move_line l where l.move_id IN %s
             AND l.account_id IN %s
             AND l.analytic_account_id IN %s
             """
            param =(tuple(move_ids),tuple(advance_invoice_acc_ids),tuple(analytic_ids))
            
            self.cr.execute(query,param)
            res=self.cr.fetchall()
            print "res>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",res
            amt = res and res[0] and res[0][0] or 0.0
            tax_amount =amt *0.05
            open_amount = amt +tax_amount
            total_amount =od_get_total_rec_amount(partner_ids,recv_account_id)
            print "total amount>>>>>>>>>>>>>>>>>account_id",total_amount,recv_account_id
            closed_amount = total_amount - open_amount
            print "closed amount>>>>>>>>>>>>>>>>",closed_amount
            return open_amount,closed_amount
        
        def _process_child(accounts, disp_acc, parent):
                
                account_rec = [acct for acct in accounts if acct['id']==parent][0]
                currency_obj = self.pool.get('res.currency')
                
                acc_id = self.pool.get('account.account').browse(self.cr, self.uid, account_rec['id'])
                currency = acc_id.currency_id and acc_id.currency_id or acc_id.company_id.currency_id
                company_id =  acc_id.company_id and acc_id.company_id.id or False
                
                
                
                res = {
                    'id': account_rec['id'],
                    'type': account_rec['type'],
                    'code': account_rec['code'],
                    'name': account_rec['name'],
                    'level': account_rec['level'],
                    'debit': account_rec['debit'],
                    'credit': account_rec['credit'],
                    'balance': account_rec['balance'],
                    'parent_id': account_rec['parent_id'],
                    'bal_type': '',
                    'project_open':0.0,
                    'project_close':0.0,
                    
                }
                #jm to get open and closed project value in account receivable
                account_id = account_rec['id']
                proj_fin_status = form.get('x_proj_fin_status')
                if proj_fin_status and account_id in [2118,5201,5641]:
                    recv_account_id = False
                    
                    if account_id == 2118:
                        recv_account_id = 2119
                    if account_id ==5201:
                        recv_account_id = 5202
                    if account_id  == 5641:
                        recv_account_id =5204
                        
                        
                    
                        
                    open_amount,closed_amount  =  get_analytic_amounts(company_id,recv_account_id)
                    res.update({
                            'project_open': open_amount,
                            'project_close': closed_amount,
                            })
                    
                self.sum_debit += account_rec['debit']
                self.sum_credit += account_rec['credit']

#Existing code is modified as sageer told all the account and balances are correct for if display account is all
                if disp_acc == 'movement':
#                    if not currency_obj.is_zero(self.cr, self.uid, currency, res['credit']) or not currency_obj.is_zero(self.cr, self.uid, currency, res['debit']) or not currency_obj.is_zero(self.cr, self.uid, currency, res['balance']):
                    self.result_acc.append(res)
                elif disp_acc == 'not_zero':
#                    if not currency_obj.is_zero(self.cr, self.uid, currency, res['balance']):
                    self.result_acc.append(res)
                else:
                    self.result_acc.append(res)
                if account_rec['child_id']:
                    for child in account_rec['child_id']:
                        _process_child(accounts,disp_acc,child)
#Custom code Prev
        def _od_prev_process_child(accounts, disp_acc, parent):
                account_rec = [acct for acct in accounts if acct['id']==parent][0]
                currency_obj = self.pool.get('res.currency')
                acc_id = self.pool.get('account.account').browse(self.cr, self.uid, account_rec['id'])
                currency = acc_id.currency_id and acc_id.currency_id or acc_id.company_id.currency_id
                res = {
                    'id': account_rec['id'],
                    'type': account_rec['type'],
                    'code': account_rec['code'],
                    'name': account_rec['name'],
                    'level': account_rec['level'],
                    'debit': account_rec['debit'],
                    'credit': account_rec['credit'],
                    'balance': account_rec['balance'],
                    'parent_id': account_rec['parent_id'],
                    'bal_type': '',
                }
                self.sum_debit += account_rec['debit']
                self.sum_credit += account_rec['credit']
                if disp_acc == 'movement':
                    if not currency_obj.is_zero(self.cr, self.uid, currency, res['credit']) or not currency_obj.is_zero(self.cr, self.uid, currency, res['debit']) or not currency_obj.is_zero(self.cr, self.uid, currency, res['balance']):
                        self.od_prev_result_acc.append(res)
                elif disp_acc == 'not_zero':
                    if not currency_obj.is_zero(self.cr, self.uid, currency, res['balance']):
                        self.od_prev_result_acc.append(res)
                else:
                    self.od_prev_result_acc.append(res)
                if account_rec['child_id']:
                    for child in account_rec['child_id']:
                        _od_prev_process_child(accounts,disp_acc,child)


#Custom code Next
        def _od_next_process_child(accounts, disp_acc, parent):
                account_rec = [acct for acct in accounts if acct['id']==parent][0]
                currency_obj = self.pool.get('res.currency')
                acc_id = self.pool.get('account.account').browse(self.cr, self.uid, account_rec['id'])
                currency = acc_id.currency_id and acc_id.currency_id or acc_id.company_id.currency_id
                res = {
                    'id': account_rec['id'],
                    'type': account_rec['type'],
                    'code': account_rec['code'],
                    'name': account_rec['name'],
                    'level': account_rec['level'],
                    'debit': account_rec['debit'],
                    'credit': account_rec['credit'],
                    'balance': account_rec['balance'],
                    'parent_id': account_rec['parent_id'],
                    'bal_type': '',
                }
                self.sum_debit += account_rec['debit']
                self.sum_credit += account_rec['credit']
                if disp_acc == 'movement':
                    if not currency_obj.is_zero(self.cr, self.uid, currency, res['credit']) or not currency_obj.is_zero(self.cr, self.uid, currency, res['debit']) or not currency_obj.is_zero(self.cr, self.uid, currency, res['balance']):
                        self.od_next_result_acc.append(res)
                elif disp_acc == 'not_zero':
                    if not currency_obj.is_zero(self.cr, self.uid, currency, res['balance']):
                        self.od_next_result_acc.append(res)
                else:
                    self.od_next_result_acc.append(res)
                if account_rec['child_id']:
                    for child in account_rec['child_id']:
                        _od_next_process_child(accounts,disp_acc,child)



        obj_account = self.pool.get('account.account')
        if not ids:
            ids = self.ids
        if not ids:
            return []
        if not done:
            done={}

        ctx = self.context.copy()

        ctx['fiscalyear'] = form['fiscalyear_id']
        if form['filter'] == 'filter_period':
            ctx['period_from'] = form['period_from']
            ctx['period_to'] = form['period_to']
        elif form['filter'] == 'filter_date':
            ctx['date_from'] = form['date_from']
            ctx['date_to'] =  form['date_to']
        ctx['state'] = form['target_move']
        parents = ids
        child_ids = obj_account._get_children_and_consol(self.cr, self.uid, ids, ctx)
        if child_ids:
            ids = child_ids
        accounts = obj_account.read(self.cr, self.uid, ids, ['type','code','name','debit','credit','balance','parent_id','level','child_id'], ctx)
        for parent in parents:
                if parent in done:
                    continue
                done[parent] = 1
                _process_child(accounts,form['display_account'],parent)

#Custom Code Prev
        od_prev_ctx_date_to = form['date_from'] and (datetime.strptime(form['date_from'], DEFAULT_SERVER_DATE_FORMAT) - timedelta(days=1)) or False
        od_prev_ctx_date_from = form['date_from'] and datetime.strptime(form['date_from'], DEFAULT_SERVER_DATE_FORMAT) - timedelta(days=3650) or False
        od_next_ctx_date_from =  form['date_from'] and datetime.strptime(form['date_from'], DEFAULT_SERVER_DATE_FORMAT) - timedelta(days=3650) or False


        log_user = self.pool.get('res.users').browse(self.cr,self.uid,self.uid)
        company_id = log_user and log_user.company_id and log_user.company_id.id
        od_prev_ctx = ctx.copy()
        flag=False
        if form['filter'] == 'filter_date':
            od_prev_ctx['date_to'] = str(od_prev_ctx_date_to)
            od_prev_ctx['date_from'] = str(od_prev_ctx_date_from)
        elif form['filter'] == 'filter_period':
            od_period_obj = self.pool.get('account.period')
            crnt_fiscalyearyear = od_prev_ctx.get('fiscalyear')
#            search_periods = od_period_obj.search(self.cr,self.uid,[('od_sequence','=',0),('company_id','=',company_id)])
            search_periods = od_period_obj.search(self.cr,self.uid,[('special','=',True),('fiscalyear_id','=',crnt_fiscalyearyear),('company_id','=',company_id)])
            od_prev_ctx['period_from'] = search_periods and search_periods[0]
            od_prev_ctx['period_to'] = search_periods and search_periods[0] #Changed period to as the selected from period one date back period of the current selected period start_date
            #++++++++++++++++++++++++++++++++++++++++++++ code commented by jm ++++++++++
            # if od_prev_ctx['period_from'] !=  form['period_to'] :
            #     od_prev_ctx['period_to'] = form['period_from'] - 1
            #_____________________________________________________________________________

        parents = ids
        child_ids = obj_account._get_children_and_consol(self.cr, self.uid, ids, od_prev_ctx)
        if child_ids:
            od_ids = child_ids
        accounts = obj_account.read(self.cr, self.uid, od_ids, ['type','code','name','debit','credit','balance','parent_id','level','child_id'], od_prev_ctx)
#        print "accountssss\n\n\n!!!!!",accounts
        for parent in parents:
                if parent in done:
                    continue
                done[parent] = 1
                _od_prev_process_child(accounts,False,parent)


#Custom code for Next
        od_next_ctx = ctx.copy()
        if not od_next_done:
            od_next_done = {}
        if form['filter'] == 'filter_date':
            od_next_ctx['date_to'] = form['date_to']
            od_next_ctx['date_from'] = str(od_next_ctx_date_from)
        elif form['filter'] == 'filter_period':
            od_next_ctx['period_from'] = False
            od_period_obj = self.pool.get('account.period')
#            search_periods = od_period_obj.search(self.cr,self.uid,[('od_sequence','=',0),('company_id','=',company_id)])

            crnt_fiscalyearyear = od_next_ctx.get('fiscalyear')
            search_periods = od_period_obj.search(self.cr,self.uid,[('special','=',True),('fiscalyear_id','=',crnt_fiscalyearyear),('company_id','=',company_id)])
            
            od_next_ctx['period_from'] = search_periods and search_periods[0]

            od_next_ctx['period_to'] = form['period_to']
        parents = ids
        child_ids = obj_account._get_children_and_consol(self.cr, self.uid, ids, od_next_ctx)
        if child_ids:
            od_ids = child_ids
        accounts = obj_account.read(self.cr, self.uid, od_ids, ['type','code','name','debit','credit','balance','parent_id','level','child_id'], od_next_ctx)
        for parent in parents:
                if parent in od_next_done:
                    continue
                od_next_done[parent] = 1
                _od_next_process_child(accounts,False,parent)

        new_res=[]

        a=[x.get('id') for x in self.result_acc]
        b=[x.get('id') for x in self.od_prev_result_acc]
        c=[x.get('id') for x in self.od_next_result_acc]


#New Code tried to make the parent account
        extra_prev_res=[]

        for opening in self.result_acc:
            opening['opening_credit'],opening['opening_debit'],opening['opening_balance'],opening['opening_balance_cr'],opening['opening_balance_dr'] = 0,0,0,0,0
            opening['closing_credit'],opening['closing_debit'],opening['closing_balance'],opening['closing_balance_cr'],opening['closing_balance_dr'] = 0,0,0,0,0
            opening['balance_dr'],opening['balance_cr']=opening.get('credit') < 0 and opening.get('credit') or 0,opening.get('credit') > 0 and opening.get('credit') or 0
            for prev in self.od_prev_result_acc:
                if prev.get('id') == opening.get('id'):
                    opening['opening_credit']=prev.get('credit')
                    opening['opening_debit'] = prev.get('debit')
                    opening['opening_balance'] = prev.get('balance')

                    cr,dr = (prev.get('balance') < 0) and prev.get('balance')*-1 or 0,(prev.get('balance') > 0) and prev.get('balance') or 0
                    opening['opening_balance_dr'] = dr + 0.0000001
                    opening['opening_balance_cr'] = cr + 0.0000001

                elif prev.get('id') != opening.get('id'):
                    extra_prev_res.append(prev)
#                    
            for closing in self.od_next_result_acc:
                if closing.get('id') == opening.get('id'):
                    opening['closing_credit'] = closing.get('credit')
                    opening['closing_debit'] = closing.get('debit')
                    opening['closing_balance'],opening['closing_balance_cr'],opening['closing_balance_dr'] = closing.get('balance'),closing.get('balance') < 0 and closing.get('balance')*-1 or 0,closing.get('balance') > 0 and closing.get('balance') or 0


            new_res.append(opening)


        seen = set()
        new_l = []
        for d in new_res:
            t = tuple(d.items())
            if t not in seen:
                seen.add(t)
                new_l.append(d)
        return new_l


class report_trialbalance(osv.AbstractModel):
    _name = 'report.account.report_trialbalance'
    _inherit = 'report.abstract_report'
    _template = 'account.report_trialbalance'
    _wrapped_report_class = account_balance

class report_trialbalance_detail(osv.AbstractModel):
    _name = 'report.account.report_trialbalance_detail'
    _inherit = 'report.abstract_report'
    _template = 'account.report_trialbalance_detail'
    _wrapped_report_class = account_balance

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
