# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import Warning
from openerp import SUPERUSER_ID
from datetime import datetime
from dateutil.relativedelta import relativedelta

from pprint import pprint
class BetaCustomeAgingWiz(models.TransientModel):
    _name='beta.customer.aging.wiz'
#     name = fields.Char(string="Name",required=True)
    partner_ids = fields.Many2many('res.partner',string="Customer")
    branch_ids= fields.Many2many('od.cost.branch',string="Branch")
    date_from = fields.Date(string='Start Date',default=fields.Date.context_today)
    direction_selection = fields.Selection([('future','Future'),('past','Past')],string="Direction",default='past')
    wiz_line = fields.One2many('beta.customer.aging.data','wiz_id',string="Wiz Line")
    def od_get_company_id(self):
        return self.env.user.company_id
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    
    
    
    def get_form(self):
        res = {}
        date_from = self.date_from
        period_length =30
        start = datetime.strptime(date_from, "%Y-%m-%d")
        for i in range(5)[::-1]:
                stop = start - relativedelta(days=period_length)
                res[str(i)] = {
                    'name': (i!=0 and (str((5-(i+1)) * period_length) + '-' + str((5-i) * period_length)) or ('+'+str(4 * period_length))),
                    'stop': start.strftime('%Y-%m-%d'),
                    'start': (i!=0 and stop.strftime('%Y-%m-%d') or False),
                }
                start = stop - relativedelta(days=1)
        return res
    def _get_lines(self):
        res = []
        form = self.get_form()
        move_state = ['draft','posted']
        target_move = 'posted'
        ACCOUNT_TYPE = ['receivable']
        total_account =[]
        obj_move = self.pool.get('account.move.line')
        branch_ids = [pr.id for pr in self.branch_ids]
        partner_ids =[pr.id for pr in self.partner_ids]
        ctx = {}   
        ctx.update({'partner_ids':partner_ids,'od_branch_ids':branch_ids,'fiscalyear': False, 'all_fiscalyear': True,'state':'posted'})
        cr = self.env.cr
        uid = self.env.uid
        self.query = obj_move._query_get(cr, uid, obj='l', context=ctx)
        if target_move == 'posted':
            move_state = ['posted']
        cr.execute('SELECT DISTINCT res_partner.id AS id,\
                    res_partner.name AS name \
                FROM res_partner,account_move_line AS l, account_account, account_move am\
                WHERE (l.account_id=account_account.id) \
                    AND (l.move_id=am.id) \
                    AND (am.state IN %s)\
                    AND (account_account.type IN %s)\
                    AND account_account.active\
                    AND ((reconcile_id IS NULL)\
                       OR (reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s )))\
                    AND (l.partner_id=res_partner.id)\
                    AND (l.date <= %s)\
                    AND ' + self.query + ' \
                ORDER BY res_partner.name', (tuple(move_state), tuple(ACCOUNT_TYPE), self.date_from, self.date_from,))
        partners = cr.dictfetchall()
        ## mise a 0 du total
        for i in range(7):
            total_account.append(0)
        #
        # Build a string like (1,2,3) for easy use in SQL query
        partner_ids = [x['id'] for x in partners]
        partner_ids = [x['id'] for x in partners]
        print "lenght partner id in recievvvfgedfsdfsdfsdfsdf aging>>>>>>>>>>>>>>>>>>>>>>>>>>>>",len(partner_ids)
        if not partner_ids:
            return []
        # This dictionary will store the debit-credit for all partners, using partner_id as key.

        totals = {}
        cr.execute('SELECT l.partner_id, SUM(l.debit-l.credit) \
                    FROM account_move_line AS l, account_account, account_move am \
                    WHERE (l.account_id = account_account.id) AND (l.move_id=am.id) \
                    AND (am.state IN %s)\
                    AND (account_account.type IN %s)\
                    AND (l.partner_id IN %s)\
                    AND ((l.reconcile_id IS NULL)\
                    OR (l.reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s )))\
                    AND ' + self.query + '\
                    AND account_account.active\
                    AND (l.date <= %s)\
                    GROUP BY l.partner_id ', (tuple(move_state), tuple(ACCOUNT_TYPE), tuple(partner_ids), self.date_from, self.date_from,))
        t = cr.fetchall()
        for i in t:
            totals[i[0]] = i[1]

        # This dictionary will store the future or past of all partners
        future_past = {}
        if self.direction_selection == 'future':
            cr.execute('SELECT l.partner_id, SUM(l.debit-l.credit) \
                        FROM account_move_line AS l, account_account, account_move am \
                        WHERE (l.account_id=account_account.id) AND (l.move_id=am.id) \
                        AND (am.state IN %s)\
                        AND (account_account.type IN %s)\
                        AND (COALESCE(l.date_maturity, l.date) < %s)\
                        AND (l.partner_id IN %s)\
                        AND ((l.reconcile_id IS NULL)\
                        OR (l.reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s )))\
                        AND '+ self.query + '\
                        AND account_account.active\
                    AND (l.date <= %s)\
                        GROUP BY l.partner_id', (tuple(move_state), tuple(ACCOUNT_TYPE), self.date_from, tuple(partner_ids),self.date_from, self.date_from,))
            t = cr.fetchall()
            for i in t:
                future_past[i[0]] = i[1]
        elif self.direction_selection == 'past': # Using elif so people could extend without this breaking
            cr.execute('SELECT l.partner_id, SUM(l.debit-l.credit) \
                    FROM account_move_line AS l, account_account, account_move am \
                    WHERE (l.account_id=account_account.id) AND (l.move_id=am.id)\
                        AND (am.state IN %s)\
                        AND (account_account.type IN %s)\
                        AND (COALESCE(l.date_maturity,l.date) > %s)\
                        AND (l.partner_id IN %s)\
                        AND ((l.reconcile_id IS NULL)\
                        OR (l.reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s )))\
                        AND '+ self.query + '\
                        AND account_account.active\
                    AND (l.date <= %s)\
                        GROUP BY l.partner_id', (tuple(move_state), tuple(ACCOUNT_TYPE), self.date_from, tuple(partner_ids), self.date_from, self.date_from,))
            t = cr.fetchall()
            for i in t:
                future_past[i[0]] = i[1]

        # Use one query per period and store results in history (a list variable)
        # Each history will contain: history[1] = {'<partner_id>': <partner_debit-credit>}
        history = []
        for i in range(5):
            args_list = (tuple(move_state), tuple(ACCOUNT_TYPE), tuple(partner_ids),self.date_from,)
            dates_query = '(COALESCE(l.date_maturity,l.date)'
            if form[str(i)]['start'] and form[str(i)]['stop']:
                dates_query += ' BETWEEN %s AND %s)'
                args_list += (form[str(i)]['start'], form[str(i)]['stop'])
            elif form[str(i)]['start']:
                dates_query += ' >= %s)'
                args_list += (form[str(i)]['start'],)
            else:
                dates_query += ' <= %s)'
                args_list += (form[str(i)]['stop'],)
            args_list += (self.date_from,)
            cr.execute('''SELECT l.partner_id, SUM(l.debit-l.credit), l.reconcile_partial_id
                    FROM account_move_line AS l, account_account, account_move am 
                    WHERE (l.account_id = account_account.id) AND (l.move_id=am.id)
                        AND (am.state IN %s)
                        AND (account_account.type IN %s)
                        AND (l.partner_id IN %s)
                        AND ((l.reconcile_id IS NULL)
                          OR (l.reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s )))
                        AND ''' + self.query + '''
                        AND account_account.active
                        AND ''' + dates_query + '''
                    AND (l.date <= %s)
                    GROUP BY l.partner_id, l.reconcile_partial_id''', args_list)
            partners_partial = cr.fetchall()
            partners_amount = dict((i[0],0) for i in partners_partial)
            for partner_info in partners_partial:
                if partner_info[2]:
                    # in case of partial reconciliation, we want to keep the left amount in the oldest period
                    cr.execute('''SELECT MIN(COALESCE(date_maturity,date)) FROM account_move_line WHERE reconcile_partial_id = %s''', (partner_info[2],))
                    date = cr.fetchall()
                    partial = False
                    if 'BETWEEN' in dates_query:
                        partial = date and args_list[-3] <= date[0][0] <= args_list[-2]
                    elif '>=' in dates_query:
                        partial = date and date[0][0] >= form[str(i)]['start']
                    else:
                        partial = date and date[0][0] <= form[str(i)]['stop']
                    if partial:
                        # partial reconcilation
                        limit_date = 'COALESCE(l.date_maturity,l.date) %s %%s' % '<=' if self.direction_selection == 'past' else '>='
                        cr.execute('''SELECT SUM(l.debit-l.credit)
                                           FROM account_move_line AS l, account_move AS am
                                           WHERE l.move_id = am.id AND am.state in %s
                                           AND l.reconcile_partial_id = %s
                                           AND ''' + limit_date, (tuple(move_state), partner_info[2], self.date_from))
                        unreconciled_amount = cr.fetchall()
                        partners_amount[partner_info[0]] += unreconciled_amount[0][0]
                else:
                    partners_amount[partner_info[0]] += partner_info[1]
            history.append(partners_amount)

        for partner in partners:
            values = {}
            ## If choise selection is in the future
            if self.direction_selection == 'future':
                # Query here is replaced by one query which gets the all the partners their 'before' value
                before = False
                if future_past.has_key(partner['id']):
                    before = [ future_past[partner['id']] ]
                total_account[6] = total_account[6] + (before and before[0] or 0.0)
                values['direction'] = before and before[0] or 0.0
            elif self.direction_selection == 'past': # Changed this so people could in the future create new direction_selections
                # Query here is replaced by one query which gets the all the partners their 'after' value
                after = False
                if future_past.has_key(partner['id']): # Making sure this partner actually was found by the query
                    after = [ future_past[partner['id']] ]

                total_account[6] = total_account[6] + (after and after[0] or 0.0)
                values['direction'] = after and after[0] or 0.0

            for i in range(5):
                during = False
                if history[i].has_key(partner['id']):
                    during = [ history[i][partner['id']] ]
                # Ajout du compteur
                total_account[(i)] = total_account[(i)] + (during and during[0] or 0)
                values[str(i)] = during and during[0] or 0.0
            total = False
            if totals.has_key( partner['id'] ):
                total = [ totals[partner['id']] ]
            values['total'] = total and total[0] or 0.0
            ## Add for total
            total_account[(i+1)] = total_account[(i+1)] + (total and total[0] or 0.0)
            values['name'] = partner['name']
            values['partner_id'] = partner['id']
            part =self.pool.get('res.partner').browse(cr,SUPERUSER_ID,partner['id'])
            payment_term = part.property_payment_term and part.property_payment_term.id or ''
            values['payment_term_id'] = payment_term
            res.append(values)

        total = 0.0
        totals = {}
        for r in res:
            total += float(r['total'] or 0.0)
            for i in range(5)+['direction']:
                totals.setdefault(str(i), 0.0)
                totals[str(i)] += float(r[str(i)] or 0.0)
        pprint(res)      
        return res
#     def _get_lines(self):
#         form = self.get_form()
#         res = []
#         total_account =[]
#         obj_move = self.pool.get('account.move.line')
#         branch_ids = [pr.id for pr in self.branch_ids]
#         partner_ids =[pr.id for pr in self.partner_ids]
#         ctx =form.get('used_context',{})
#         ctx.update({'partner_ids':partner_ids,'od_branch_ids':branch_ids,'fiscalyear': False, 'all_fiscalyear': True,'state':'posted'})
#         cr = self.env.cr
#         uid = self.env.uid
#         self.query = obj_move._query_get(cr, uid, obj='l', context=ctx)
#         print "self.query >>>>>>>>>>>>my form>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",self.query
#         move_state = ['posted']
#         ACCOUNT_TYPE = ['receivable']
#         cr.execute('SELECT DISTINCT res_partner.id AS id,\
#                     res_partner.name AS name \
#                 FROM res_partner,account_move_line AS l, account_account, account_move am\
#                 WHERE (l.account_id=account_account.id) \
#                     AND (l.move_id=am.id) \
#                     AND (am.state IN %s)\
#                     AND (account_account.type IN %s)\
#                     AND account_account.active\
#                     AND ((reconcile_id IS NULL)\
#                        OR (reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s AND not recon.opening_reconciliation)))\
#                     AND (l.partner_id=res_partner.id)\
#                     AND (l.date <= %s)\
#                     AND ' + self.query + ' \
#                 ORDER BY res_partner.name', (tuple(move_state), tuple(ACCOUNT_TYPE), self.date_from, self.date_from,))
#         partners = cr.dictfetchall()
#         ## mise a 0 du total
#         for i in range(7):
#             total_account.append(0)
#         #
#         # Build a string like (1,2,3) for easy use in SQL query
#         partner_ids = [x['id'] for x in partners]
#         if not partner_ids:
#             return []
#         # This dictionary will store the debit-credit for all partners, using partner_id as key.
# 
#         totals = {}
#         cr.execute('SELECT l.partner_id, SUM(l.debit-l.credit) \
#                     FROM account_move_line AS l, account_account, account_move am \
#                     WHERE (l.account_id = account_account.id) AND (l.move_id=am.id) \
#                     AND (am.state IN %s)\
#                     AND (account_account.type IN %s)\
#                     AND (l.partner_id IN %s)\
#                     AND ((l.reconcile_id IS NULL)\
#                     OR (l.reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s AND not recon.opening_reconciliation)))\
#                     AND ' + self.query + '\
#                     AND account_account.active\
#                     AND (l.date <= %s)\
#                     GROUP BY l.partner_id ', (tuple(move_state), tuple(ACCOUNT_TYPE), tuple(partner_ids), self.date_from, self.date_from,))
#         t = cr.fetchall()
#         for i in t:
#             totals[i[0]] = i[1]
# 
#         # This dictionary will store the future or past of all partners
#         future_past = {}
#         if self.direction_selection == 'future':
#             cr.execute('SELECT l.partner_id, SUM(l.debit-l.credit) \
#                         FROM account_move_line AS l, account_account, account_move am \
#                         WHERE (l.account_id=account_account.id) AND (l.move_id=am.id) \
#                         AND (am.state IN %s)\
#                         AND (account_account.type IN %s)\
#                         AND (COALESCE(l.date_maturity, l.date) < %s)\
#                         AND (l.partner_id IN %s)\
#                         AND ((l.reconcile_id IS NULL)\
#                         OR (l.reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s AND not recon.opening_reconciliation)))\
#                         AND '+ self.query + '\
#                         AND account_account.active\
#                     AND (l.date <= %s)\
#                         GROUP BY l.partner_id', (tuple(move_state), tuple(ACCOUNT_TYPE), self.date_from, tuple(partner_ids),self.date_from, self.date_from,))
#             t = cr.fetchall()
#             for i in t:
#                 future_past[i[0]] = i[1]
#         elif self.direction_selection == 'past': # Using elif so people could extend without this breaking
#             cr.execute('SELECT l.partner_id, SUM(l.debit-l.credit) \
#                     FROM account_move_line AS l, account_account, account_move am \
#                     WHERE (l.account_id=account_account.id) AND (l.move_id=am.id)\
#                         AND (am.state IN %s)\
#                         AND (account_account.type IN %s)\
#                         AND (COALESCE(l.date_maturity,l.date) > %s)\
#                         AND (l.partner_id IN %s)\
#                         AND ((l.reconcile_id IS NULL)\
#                         OR (l.reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s  AND not recon.opening_reconciliation)))\
#                         AND '+ self.query + '\
#                         AND account_account.active\
#                     AND (l.date <= %s)\
#                         GROUP BY l.partner_id', (tuple(move_state), tuple(ACCOUNT_TYPE), self.date_from, tuple(partner_ids), self.date_from, self.date_from,))
#             t = cr.fetchall()
#             for i in t:
#                 future_past[i[0]] = i[1]
# 
#         # Use one query per period and store results in history (a list variable)
#         # Each history will contain: history[1] = {'<partner_id>': <partner_debit-credit>}
#         history = []
#         for i in range(5):
#             args_list = (tuple(move_state), tuple(ACCOUNT_TYPE), tuple(partner_ids),self.date_from,)
#             dates_query = '(COALESCE(l.date_maturity,l.date)'
#             date_partial = ''
#             arg_partial = ()
#             if form[str(i)]['start'] and form[str(i)]['stop']:
#                 dates_query += ' BETWEEN %s AND %s)'
#                 args_list += (form[str(i)]['start'], form[str(i)]['stop'])
#                 date_partial = 'AND l.date <= %s'
#                 arg_partial = (form[str(i)]['stop'],)
#             elif form[str(i)]['start']:
#                 dates_query += ' >= %s)'
#                 args_list += (form[str(i)]['start'],)
#                 date_partial = 'AND l.date >= %s'
#                 arg_partial = (form[str(i)]['start'],)
#             else:
#                 dates_query += ' <= %s)'
#                 args_list += (form[str(i)]['stop'],)
#                 date_partial = 'AND l.date <= %s'
#                 arg_partial = (form[str(i)]['stop'],)
#             args_list += (self.date_from,)
#             cr.execute('''SELECT l.partner_id, SUM(l.debit-l.credit), l.reconcile_partial_id
#                     FROM account_move_line AS l, account_account, account_move am 
#                     WHERE (l.account_id = account_account.id) AND (l.move_id=am.id)
#                         AND (am.state IN %s)
#                         AND (account_account.type IN %s)
#                         AND (l.partner_id IN %s)
#                         AND ((l.reconcile_id IS NULL)
#                           OR (l.reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s AND not recon.opening_reconciliation)))
#                         AND ''' + self.query + '''
#                         AND account_account.active
#                         AND ''' + dates_query + '''
#                     AND (l.date <= %s)
#                     GROUP BY l.partner_id, l.reconcile_partial_id''', args_list)
#             partners_partial = cr.fetchall()
#             partners_amount = dict((i[0],0) for i in partners_partial)
#             for partner_info in partners_partial:
#                 if partner_info[2]:
#                     # in case of partial reconciliation, we want to keep the remaining amount in the
#                     # period corresponding to the maturity date of the invoice.
#                     cr.execute('''
#                         SELECT MAX(COALESCE(l.date_maturity, l.date))
#                         FROM account_move_line AS l
#                         JOIN account_account AS a ON l.account_id = a.id
#                         WHERE reconcile_partial_id = %s
#                             AND a.type IN %s
#                             ''' + date_partial
#                         , (partner_info[2], tuple(ACCOUNT_TYPE),) + arg_partial)
#                     date = cr.fetchall()
#                     # Just in case date is not defined (but it should be defined)
#                     if date and not date[0][0]:
#                         cr.execute('''SELECT MIN(COALESCE(date_maturity,date)) FROM account_move_line WHERE reconcile_partial_id = %s''', (partner_info[2],))
#                         date = cr.fetchall()
#                     partial = False
#                     if 'BETWEEN' in dates_query:
#                         partial = date and args_list[-3] <= date[0][0] <= args_list[-2]
#                     elif '>=' in dates_query:
#                         partial = date and date[0][0] >= form[str(i)]['start']
#                     else:
#                         partial = date and date[0][0] <= form[str(i)]['stop']
#                     if partial:
#                         # partial reconcilation
#                         limit_date = 'COALESCE(l.date_maturity,l.date) %s %%s' % ('<=' if self.direction_selection == 'past' else '>=',)
#                         cr.execute('''SELECT SUM(l.debit-l.credit)
#                                            FROM account_move_line AS l, account_move AS am
#                                            WHERE l.move_id = am.id AND am.state in %s
#                                            AND l.reconcile_partial_id = %s
#                                            AND ''' + limit_date, (tuple(move_state), partner_info[2], self.date_from))
#                         unreconciled_amount = cr.fetchall()
#                         partners_amount[partner_info[0]] += unreconciled_amount[0][0]
#                 else:
#                     partners_amount[partner_info[0]] += partner_info[1]
#             history.append(partners_amount)
# 
#         for partner in partners:
#             values = {}
#             ## If choise selection is in the future
#             if self.direction_selection == 'future':
#                 # Query here is replaced by one query which gets the all the partners their 'before' value
#                 before = False
#                 if future_past.has_key(partner['id']):
#                     before = [ future_past[partner['id']] ]
#                 total_account[6] = total_account[6] + (before and before[0] or 0.0)
#                 values['direction'] = before and before[0] or 0.0
#             elif self.direction_selection == 'past': # Changed this so people could in the future create new direction_selections
#                 # Query here is replaced by one query which gets the all the partners their 'after' value
#                 after = False
#                 if future_past.has_key(partner['id']): # Making sure this partner actually was found by the query
#                     after = [ future_past[partner['id']] ]
# 
#                 total_account[6] = total_account[6] + (after and after[0] or 0.0)
#                 values['direction'] = after and after[0] or 0.0
# 
#             for i in range(5):
#                 during = False
#                 if history[i].has_key(partner['id']):
#                     during = [ history[i][partner['id']] ]
#                 # Ajout du compteur
#                 total_account[(i)] = total_account[(i)] + (during and during[0] or 0)
#                 values[str(i)] = during and during[0] or 0.0
#             total = False
#             if totals.has_key( partner['id'] ):
#                 total = [ totals[partner['id']] ]
#             values['total'] = total and total[0] or 0.0
#             ## Add for total
#             total_account[(i+1)] = total_account[(i+1)] + (total and total[0] or 0.0)
#             values['name'] = partner['name']
#             values['partner_id'] = partner['id']
#             part =self.pool.get('res.partner').browse(cr,SUPERUSER_ID,partner['id'])
#             payment_term = part.property_payment_term and part.property_payment_term.id or False
#             values['payment_term_id'] = payment_term
#             res.append(values)
# 
#         total = 0.0
#         totals = {}
#         for r in res:
#             total += float(r['total'] or 0.0)
#             for i in range(5)+['direction']:
#                 totals.setdefault(str(i), 0.0)
#                 totals[str(i)] += float(r[str(i)] or 0.0)
#         return res

    
    @api.multi 
    def export_rpt(self):
        wiz_id = self.id
        values = self._get_lines()
        pprint(values)
        result =[]
        for val in values:
            result.append((0,0,{
                'wiz_id':wiz_id,
                'partner_id':val.get('partner_id'),
                'payment_term_id':val.get('payment_term_id'),
                'current':val.get('direction'),
                'bal1':val.get('4'),
                'bal2':val.get('3'),
                'bal3':val.get('2'),
                'bal4':val.get('1'),
                'bal5':val.get('0'),
                'balance':val.get('total')
                }))
        self.wiz_line.unlink()
        self.write({'wiz_line':result})
            
        return {
            'domain': [('wiz_id','=',wiz_id)],
            'name': 'Customer Aging Report',
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'beta.customer.aging.data',
            'type': 'ir.actions.act_window',
        }

class wiz_project_rpt_data(models.TransientModel):
    _name = 'beta.customer.aging.data'
    wiz_id = fields.Many2one('beta.customer.aging.wiz',string="Wizard")
    partner_id = fields.Many2one('res.partner',string="Customer")
    company_id = fields.Many2one('res.company',string="Company")
    branch_id = fields.Many2one('od.cost.branch',string="Branch")
    current = fields.Float(string="Current")
    bal1= fields.Float(string="0  -  30")
    bal2= fields.Float(string="30 -  60")
    bal3= fields.Float(string="60 -  90")
    bal4= fields.Float(string="90 - 120")
    bal5= fields.Float(string="  +120  ")
    balance = fields.Float(string="Balance")
    payment_term_id = fields.Many2one('account.payment.term',string="Payment Term")
    