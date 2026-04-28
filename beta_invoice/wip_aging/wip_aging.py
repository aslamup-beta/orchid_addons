# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import Warning
from openerp import SUPERUSER_ID
from dateutil.relativedelta import relativedelta
from pprint import pprint
import time
import datetime
from datetime import date
from itertools import groupby
from operator import itemgetter


class BetaWipAgingWiz(models.TransientModel):
    _name='od.beta.wip.aging.wiz'
    
    partner_ids = fields.Many2many('res.partner',string="Customer",domain=[('customer','=',True)])
    branch_ids= fields.Many2many('od.cost.branch',string="Branch")
    date_from = fields.Date(string='Start Date',default=fields.Date.context_today)
    direction_selection = fields.Selection([('future','Future'),('past','Past')],string="Direction",default='past')
    wiz_line = fields.One2many('od.beta.wip.aging.data','wiz_id',string="Wiz Line")
    period_length = fields.Selection([(30,'30'),(60,'60')],string="Period Length",default=30)
    
    type = fields.Selection([('job','JOB'),('sup','SUPPLY')],string="WIP Finance A/C Type")
    high_level = fields.Boolean(string="High Level",default=True)
    def od_get_company_id(self):
        return self.env.user.company_id
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    
    def get_form(self):
        res = {}
        date_from = self.date_from
        period_length =self.period_length
        start = datetime.datetime.strptime(date_from, "%Y-%m-%d")
        for i in range(7)[::-1]:
                stop = start - relativedelta(days=period_length)
                res[str(i)] = {
                    'name': (i!=0 and (str((7-(i+1)) * period_length) + '-' + str((7-i) * period_length)) or ('+'+str(6 * period_length))),
                    'stop': start.strftime('%Y-%m-%d'),
                    'start': (i!=0 and stop.strftime('%Y-%m-%d') or False),
                }
                start = stop - relativedelta(days=1)
        
        return res
    
    
    def _get_lines(self):
        res = []
        form = self.get_form()
        move_state = ['posted','posted']
        target_move = 'posted'
        ACCOUNT_TYPE = ['other']
        if self.company_id.id == 6:
            if self.type== 'job':
                ACCOUNT_IDS = [5732,]
            elif self.type=='sup':
                ACCOUNT_IDS = [5734,]
            else:
                ACCOUNT_IDS = [5734,5732,]
                
        else:
            if self.type== 'job':
                ACCOUNT_IDS = [2128,]
            elif self.type=='sup':
                ACCOUNT_IDS = [2137,]
            else:
                ACCOUNT_IDS = [2137,2128,]
                

        total_account =[]
        obj_move = self.pool.get('account.move.line')
        branch_ids = [pr.id for pr in self.branch_ids]
        partner_ids =[pr.id for pr in self.partner_ids]
        ctx = {}
        ctx.update({'fiscalyear': False, 'all_fiscalyear': True,'state':'posted'})
        cr = self.env.cr
        uid = self.env.uid
        self.query = obj_move._query_get(cr, uid, obj='l', context=ctx)
        if target_move == 'posted':
            move_state = ['posted','posted']
            if len(ACCOUNT_IDS) ==1:
                cr.execute('SELECT DISTINCT l.id AS id,\
                        l.name AS name \
                    FROM account_move_line AS l,account_move am\
                    WHERE l.account_id = %s \
                    AND (l.move_id=am.id) \
                    AND (am.state IN %s)\
                    ORDER BY l.name', (tuple(ACCOUNT_IDS),tuple(move_state)))
            else:
                cr.execute('SELECT DISTINCT l.id AS id,\
                        l.name AS name \
                    FROM account_move_line AS l,account_move am\
                    WHERE l.account_id IN %s \
                    AND (l.move_id=am.id) \
                    AND (am.state IN %s)\
                    ORDER BY l.name', (tuple(ACCOUNT_IDS),tuple(move_state)))
                
        moves= cr.dictfetchall()
        ## mise a 0 du total
        for i in range(9):
            total_account.append(0)
        #
        # Build a string like (1,2,3) for easy use in SQL query
        move_ids = [x['id'] for x in moves]
        print len(move_ids),"1"*88
        if not move_ids:
            return []
        # This dictionary will store the debit-credit for all analytics, using analytic_id as key.

        totals = {}
        if len(ACCOUNT_IDS) ==1:         
            cr.execute('SELECT l.id, l.analytic_account_id, SUM(l.debit-l.credit) \
                        FROM account_move_line AS l \
                        WHERE l.account_id = %s\
                        AND (l.date <= %s)\
                        GROUP BY l.id, l.analytic_account_id', (tuple(ACCOUNT_IDS), self.date_from,))
        else:
            cr.execute('SELECT l.id, l.analytic_account_id, SUM(l.debit-l.credit) \
                        FROM account_move_line AS l \
                        WHERE l.account_id IN %s\
                        AND (l.date <= %s)\
                        GROUP BY l.id, l.analytic_account_id', (tuple(ACCOUNT_IDS), self.date_from,))
            
        
        t = cr.fetchall()
        
        for i in t:
            totals[i[0]] = [i[2],i[1]]
                    
        # This dictionary will store the future or past of all partners
        future_past = {}
        if self.direction_selection == 'future':
            cr.execute('SELECT l.analytic_account_id, SUM(l.debit-l.credit) \
                        FROM account_move_line AS l, account_account, account_move am \
                        WHERE (l.account_id IN %s) AND (l.move_id=am.id) \
                        AND (am.state IN %s)\
                        AND (account_account.type IN %s)\
                        AND (COALESCE(l.date_maturity, l.date) < %s)\
                        AND '+ self.query + '\
                        AND account_account.active\
                        AND l.analytic_account_id IN %s\
                    AND (l.date <= %s)\
                        GROUP BY l.analytic_account_id', (tuple(ACCOUNT_IDS), tuple(move_state), tuple(ACCOUNT_TYPE), tuple(move_ids),self.date_from,self.date_from, self.date_from,))
            t = cr.fetchall()
            for i in t:
                future_past[i[0]] = i[2]
        
        elif self.direction_selection == 'past': # Using elif so people could extend without this breaking
            cr.execute('SELECT l.id, l.analytic_account_id, SUM(l.debit-l.credit) \
                    FROM account_move_line AS l \
                    WHERE l.account_id IN %s\
                    AND (COALESCE(l.date_maturity,l.date) > %s)\
                    AND (l.date <= %s)\
                    GROUP BY l.id, l.analytic_account_id ', (tuple(ACCOUNT_IDS), self.date_from,self.date_from))
            t = cr.fetchall()
            for i in t:
                future_past[i[0]] = i[2]

        # Use one query per period and store results in history (a list variable)
        # Each history will contain: history[1] = {'<partner_id>': <partner_debit-credit>}
        
        
        # direction is past, dict return blank dict
        history = []
        for i in range(7):
            if len(ACCOUNT_IDS) ==1:
                args_list = (tuple(ACCOUNT_IDS))
            else:
                args_list = (tuple(ACCOUNT_IDS),)
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
            if len(ACCOUNT_IDS) ==1:
                cr.execute('''SELECT l.id, l.analytic_account_id, SUM(l.debit-l.credit), l.reconcile_partial_id
                        FROM account_move_line AS l 
                        WHERE l.account_id = %s\
                        AND ''' + self.query + '''
                        AND ''' + dates_query + '''
                        AND (l.date <= %s)
                        GROUP BY l.id, l.analytic_account_id,l.reconcile_partial_id''', args_list)
            else:
                cr.execute('''SELECT l.id, l.analytic_account_id, SUM(l.debit-l.credit), l.reconcile_partial_id
                        FROM account_move_line AS l 
                        WHERE l.account_id IN %s\
                        AND ''' + self.query + '''
                        AND ''' + dates_query + '''
                        AND (l.date <= %s)
                        GROUP BY l.id, l.analytic_account_id,l.reconcile_partial_id''', args_list)
                
            partners_partial = cr.fetchall()
            partners_amount = dict((i[0],0) for i in partners_partial)
            for partner_info in partners_partial:
                if partner_info[3]:
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
                    partners_amount[partner_info[0]] += partner_info[2]
            history.append(partners_amount)
        
        # history be like  [{7978: 1700613.02}, {7978: 147195.05}, {7978: 886936.1}, {7978: 2213980.7}, {7978: 0.01}]
        for partner in moves:
            #Here partner=each moveline in that dict,renaming issue
            values = {}
            ## If choise selection is in the future
            if self.direction_selection == 'future':
                # Query here is replaced by one query which gets the all the partners their 'before' value
                before = False
                if future_past.has_key(partner['id']):
                    before = [ future_past[partner['id']] ]
                total_account[8] = total_account[8] + (before and before[0] or 0.0)
                values['direction'] = before and before[0] or 0.0
            elif self.direction_selection == 'past': # Changed this so people could in the future create new direction_selections
                # Query here is replaced by one query which gets the all the partners their 'after' value
                after = False
                if future_past.has_key(partner['id']): # Making sure this partner actually was found by the query
                    after = [ future_past[partner['id']] ]

                total_account[8] = total_account[8] + (after and after[0] or 0.0)
                values['direction'] = after and after[0] or 0.0

            for i in range(7):
                during = False
                if history[i].has_key(partner['id']):
                    during = [ history[i][partner['id']] ]
                # Ajout du compteur
                total_account[(i)] = total_account[(i)] + (during and during[0] or 0)
                values[str(i)] = during and during[0] or 0.0
            total = False
            if totals.has_key(partner['id']):
                total = [ totals[partner['id']][0] ]
                anal_id = [ totals[partner['id']][1] ]
            values['total'] = total and total[0] or 0.0
            ## Add for total
            total_account[(i+1)] = total_account[(i+1)] + (total and total[0] or 0.0)
            values['name'] = partner['name']
            values['move_id1'] = partner['id']
            
            values['anal_id'] = anal_id[0]
            payment_term =  ''
            values['payment_term_id'] = payment_term
            res.append(values)

        total = 0.0
        totals = {}
        for r in res:
            total += float(r['total'] or 0.0)
            for i in range(7)+['direction']:
                totals.setdefault(str(i), 0.0)
                totals[str(i)] += float(r[str(i)] or 0.0)
#         pprint(res)       
        return res
    
    

    def get_account_ids(self,company_id):
        ACCOUNT_IDS =[]
        if company_id == 6:
            audit_temp_id =9
            if self.type== 'job':
                ACCOUNT_IDS = [5732,]
            elif self.type=='sup':
                ACCOUNT_IDS = [5734,]
            else:
                ACCOUNT_IDS = [5734,5732,]
                
        else:
            if self.type== 'job':
                ACCOUNT_IDS = [2128,]
            elif self.type=='sup':
                ACCOUNT_IDS = [2137,]
            else:
                ACCOUNT_IDS = [2137,2128,]
        return ACCOUNT_IDS
    
    def get_audit_temp_id(self,company_id):
        audit_temp_id=14
        if company_id == 6:
            audit_temp_id =9
        return audit_temp_id
    
    def get_sample_id(self,audit_temp_id):
        sample_id = self.env['audit.sample'].search([('aud_temp_id','=',audit_temp_id)])
        samp_id =sample_id[-1].id
        return samp_id
    
    def get_data_set(self,ACCOUNT_IDS):
        cr = self.env.cr
        if len(ACCOUNT_IDS) ==1:         
            cr.execute('SELECT l.analytic_account_id,SUM(l.debit-l.credit) \
                        FROM account_move_line AS l \
                        WHERE l.account_id = %s\
                        AND (l.date <= %s)\
                        GROUP BY  l.analytic_account_id \
                        ', (tuple(ACCOUNT_IDS), self.date_from,))
        else:
            cr.execute('SELECT l.analytic_account_id, SUM(l.debit-l.credit) \
                        FROM account_move_line AS l \
                        WHERE l.account_id IN %s\
                        AND (l.date <= %s)\
                        GROUP BY  l.analytic_account_id \
                        ', (tuple(ACCOUNT_IDS), self.date_from,))
            
        
        data_set = cr.fetchall()
        
        return data_set
#     def process_data(self,data_set):
#         
#         result = [(k, list(list(zip(*g))[1])) for k, g in groupby(data_set, itemgetter(0))]
#         print "processed result>>>>>>>>>>>>>>>>>>>>>>>>>>",result
#         return result
    
    
#     def get_collected(self,samp_id,analytic_id):
#         cr = self.env.cr
#         query = """
#                 select collected from pmo_open_project_sample where sample_id=%s and analytic_id=%s
#           """
#         cr.execute(query,(samp_id,analytic_id,))
#         result = cr.fetchone()
#         print "result>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",result
#         result = result and result[0] or 0.0
#         return result
#     
#     def get_high_level_rpt(self):
#         company_id = self.company_id and self.company_id.id
#         cr = self.env.cr
#         ACCOUNT_IDS = self.get_account_ids(company_id)
#         audit_temp_id = self.get_audit_temp_id(company_id)
#         samp_id =self.get_sample_id(audit_temp_id)
#         data_set =self.get_data_set(ACCOUNT_IDS)
# #         process_data = self.process_data(data_set)
#         analytic_pool = self.env['account.analytic.account']
#         for dat in data_set:
#             status='normal'
#             analytic_id = dat[0]
#             balance =dat[1]
#             
#             ob = analytic_pool.browse(analytic_id)
#             partner_id = ob.partner_id and ob.partner_id.id
#             
#             if ob.state =='close' or not analytic_id:
#                 continue
#             
#             if analytic_id and balance:
#                 if abs(balance) <1:
#                     continue
#                 collected = ob.get_invoice_amt()
#                 if collected <balance:
#                     status = 'priority'
#                 
#                 data ={
#                     'data_id':self.id,
#                     'analytic_id':analytic_id,
#                     'balance':balance,
#                     'partner_id':partner_id,
#                     'collected':collected,
#                     
#                     'status':status,
#                     'create_uid':self.create_uid and self.create_uid.id,
#                     'create_date':self.create_date,
#                     'write_date':self.write_date,
#                     'write_uid':self.write_uid and self.write_uid.id
#                     
#                     }
#                 
#                 query = """
#                 
#                     INSERT INTO wiz_wip_high_level_data (data_id,analytic_id,
#                     balance,collected,partner_id,status,
#                     create_uid,create_date,write_date,write_uid) 
#                     VALUES (%(data_id)s, %(analytic_id)s,
#                     %(balance)s,%(collected)s,%(partner_id)s,%(status)s,
#                     %(create_uid)s,%(create_date)s,%(write_date)s,%(write_uid)s);"""
#                 
#                 cr.execute(query,data)
#         
#         wiz_id = self.id    
#         model_data = self.env['ir.model.data']
#         vw ='od_wip_high_level_tree_view_2'
#         tree_view = model_data.get_object_reference( 'beta_invoice', vw)
#         
#         
#         return {
#             'domain': [('data_id','=',wiz_id)],
#             'name': 'WIP Balance/Collected Report',
#             'view_type': 'form',
#             'view_mode': 'tree',
#             'context':{'search_default_partner': 1},
#             'views': [(tree_view and tree_view[1] or False, 'tree')],
#             'res_model':'wiz.wip.high.level.data',
#             'type': 'ir.actions.act_window',
#         }
    
    

        
    def insert_data(self):
                    
        wiz_id = self.id
        values = self._get_lines()
        result =[]
        
        analytic_pool = self.env['account.analytic.account']
        cr = self.env.cr
       
        date =str(datetime.datetime.now())
        for val in values:
            if round(val.get('total')) !=0.00 :
                a_id=val.get('anal_id')
                ob = analytic_pool.browse(a_id)
                if ob.state in ('close','cancelled') or not a_id:
                    continue
                project_type = ob.od_type_of_project
                partner_id = ob.partner_id and ob.partner_id.id
                result={
                    'data_id':wiz_id,
                    'move_id1':val.get('move_id1',None),
                    'anal_id':val.get('anal_id',None),
                    'partner_id':partner_id or None,
                    'payment_term_id':val.get('payment_term_id',None),
                    'current':val.get('direction',None),
                    'project_type':project_type,
                    
                    
                    'bal_30_1':val.get('6'),
                    'bal_30_2':val.get('5'),
                    'bal_30_3':val.get('4'),
                    'bal_30_4': val.get('3'),
                    'bal_30_5': val.get('2'),
                    'bal_30_6': val.get('1'),
                    'bal_30_plus':val.get('0'),
                    
                    'bal_60_1':val.get('6'),
                    'bal_60_2':val.get('5'),
                    'bal_60_3': val.get('4'),
                    'bal_60_4': val.get('3'),
                    'bal_60_5': val.get('2'),
                    'bal_60_6': val.get('1'),
                    'bal_60_plus':val.get('0'),
                    
                    
                    'balance':val.get('total',0.0),
                    'create_uid':self.create_uid and self.create_uid.id,
                    'create_date':self.create_date,
                    'write_date':self.write_date,
                    'write_uid':self.write_uid and self.write_uid.id
                    
                    }
                query = """INSERT INTO od_beta_wip_aging_data (data_id,move_id1,anal_id,partner_id,current,project_type,balance,
                                    bal_30_1,bal_30_2,
                                    bal_30_3,bal_30_4,bal_30_5,bal_30_6,bal_30_plus,
                                    bal_60_1,bal_60_2,
                                    bal_60_3,bal_60_4,bal_60_5,bal_60_6,bal_60_plus,create_uid,create_date,write_date,write_uid) 
                            
                            VALUES (%(data_id)s, %(move_id1)s,%(anal_id)s,%(partner_id)s,%(current)s,%(project_type)s,
                            %(balance)s,
                            %(bal_30_1)s,%(bal_30_2)s,%(bal_30_3)s,%(bal_30_4)s,%(bal_30_5)s,%(bal_30_6)s,%(bal_30_plus)s,
                            %(bal_60_1)s,%(bal_60_2)s,%(bal_60_3)s,%(bal_60_4)s,%(bal_60_5)s,%(bal_60_6)s,%(bal_60_plus)s,
                            %(create_uid)s,%(create_date)s,%(write_date)s,%(write_uid)s);"""
                
                cr.execute(query,result)
            
    
    
    def get_high_lvl_rpt(self):
        wiz_id = self.id
        cr = self.env.cr
        self.insert_data()
        query ="""
            select anal_id as analytic_id,sum(balance) as balance,sum(bal_30_1) as bal_30_1,sum(bal_30_2) as bal_30_2,
            sum(bal_30_3) as bal_30_3,sum(bal_30_4) as bal_30_4,
            sum(bal_30_5) as bal_30_5,sum(bal_30_6) as bal_30_6,sum(bal_30_plus) as bal_30_plus,
            sum(bal_60_1) as bal_60_1,sum(bal_60_2) as bal_60_2,sum(bal_60_3) as bal_60_3,sum(bal_60_4) as bal_60_4,
            sum(bal_60_5)  as bal_60_5,sum(bal_60_6) as bal_60_6,sum(bal_60_plus) as bal_60_plus 
            from od_beta_wip_aging_data
            where data_id=%s 
            group by anal_id 
        
        
          """
        cr.execute(query,(wiz_id,))
        data = cr.dictfetchall()
        analytic_pool = self.env['account.analytic.account']
        for res in data:
            status='normal'
            analytic_id =res.get('analytic_id',False)
            balance=res.get('balance',False)
            
            ob = analytic_pool.browse(analytic_id)
            
            partner_id = ob.partner_id and ob.partner_id.id or False
            print analytic_id, partner_id, "X"*88
            project_type = ob.od_type_of_project
            amended_sale = ob.od_amended_sale_rg
            amended_cost = ob.od_amended_cost_rg
            collected = ob.get_invoice_amt()
            if collected <balance:
                status = 'priority'
                
                
            res.update({
                    'data_id':self.id,
                    'collected':collected,
                    'partner_id':partner_id,
                    'status':status,
                    'project_type':project_type,
                    'amended_sale':amended_sale,
                    'amended_cost':amended_cost,
                    'create_uid':self.create_uid and self.create_uid.id,
                    'create_date':self.create_date,
                    'write_date':self.write_date,
                    'write_uid':self.write_uid and self.write_uid.id
                    })
                
                
            query = """
                
                    INSERT INTO wiz_wip_high_level_data (data_id,analytic_id,
                    balance,collected,partner_id,status,project_type,amended_sale,amended_cost,
                    create_uid,create_date,write_date,write_uid,
                    bal_30_1,bal_30_2,bal_30_3,bal_30_4,
            bal_30_5,bal_30_6,bal_30_plus,bal_60_1,bal_60_2,bal_60_3,bal_60_4,
            bal_60_5,bal_60_6,bal_60_plus
                    ) 
                    VALUES (%(data_id)s, %(analytic_id)s,
                    %(balance)s,%(collected)s,%(partner_id)s,%(status)s,%(project_type)s,%(amended_sale)s,%(amended_cost)s,
                    %(create_uid)s,%(create_date)s,%(write_date)s,%(write_uid)s,
                    %(bal_30_1)s,%(bal_30_2)s,%(bal_30_3)s,%(bal_30_4)s,
                    %(bal_30_5)s,%(bal_30_6)s,%(bal_30_plus)s,%(bal_60_1)s,
                    %(bal_60_2)s,%(bal_60_3)s,%(bal_60_4)s,%(bal_60_5)s,
                    %(bal_60_6)s,%(bal_60_plus)s
                    
                    );"""
                
            cr.execute(query,res)
        
        wiz_id = self.id    
        model_data = self.env['ir.model.data']
        vw ='od_wip_high_level_tree_view_2'
        period_length = self.period_length
        if period_length == 60:
            vw ='od_wip_high_level_tree_view_3'
        tree_view = model_data.get_object_reference( 'beta_invoice', vw)
        
       
        
        
        return {
            'domain': [('data_id','=',wiz_id)],
            'name': 'WIP Balance/Collected Report',
            'view_type': 'form',
            'view_mode': 'tree',
            'context':{'search_default_partner': 1},
            'views': [(tree_view and tree_view[1] or False, 'tree')],
            'res_model':'wiz.wip.high.level.data',
            'type': 'ir.actions.act_window',
        }
    
            
        
    
    @api.multi 
    def export_rpt(self):
        if self.high_level:
            return self.get_high_lvl_rpt()
        wiz_id = self.id
        self.insert_data()
        model_data = self.env['ir.model.data']
        period_length = self.period_length
        vw ='od_wip_aging_data_tree_view_1'
        if period_length == 60:
            vw = 'od_wip_aging_data_tree_view_2'
        tree_view = model_data.get_object_reference( 'beta_invoice', vw)
        
        
        return {
            'domain': [('data_id','=',wiz_id)],
            'name': 'WIP Aging Report',
            'view_type': 'form',
            'view_mode': 'tree',
            'context':{'search_default_partner': 1},
            'views': [(tree_view and tree_view[1] or False, 'tree')],
            'res_model': 'od.beta.wip.aging.data',
            'type': 'ir.actions.act_window',
        }

class wiz_wip_project_rpt_data(models.TransientModel):
    _name = 'od.beta.wip.aging.data'
    
    DOMAIN = [('parent_level0','Parent Level View'),('amc_view','AMC View'),('o_m_view','O&M View'),('credit','Credit'),('sup','Supply'),('imp','Implementation'),('sup_imp','Supply & Implementation'),
              ('amc','AMC'),('o_m','O&M'),('cust_trn','Customer Training'),('poc','(POC,Presales)'), ('comp_gen','Company General -(Training,Labs,Trips,etc.)')]
   
    project_type = fields.Selection(DOMAIN,string="Analytic Type")
    data_id = fields.Integer(string="Data ID")
    wiz_id = fields.Many2one('od.beta.wip.aging.wiz',string="Wizard")
    partner_id = fields.Many2one('res.partner',string="Customer")
    anal_id = fields.Many2one('account.analytic.account',string="Analytic Account")
    move_id1 = fields.Many2one('account.move.line',string="Account Move")
    company_id = fields.Many2one('res.company',string="Company")
    branch_id = fields.Many2one('od.cost.branch',string="Branch")
    current = fields.Float(string="Current")
    period_length = fields.Selection([(30,'30'),(60,'60')],string="Period Length")
    bal_30_1  = fields.Float(string="0  -  30")
    bal_30_2  = fields.Float(string="30 -  60")
    bal_30_3  = fields.Float(string="60 -  90")
    bal_30_4  = fields.Float(string="90 - 120")
    bal_30_5  = fields.Float(string="120 - 150")
    bal_30_6  = fields.Float(string="150 - 180")
    bal_30_plus = fields.Float(string=" 180+  ")
    
    bal_60_1= fields.Float(string="0  -  60")
    bal_60_2= fields.Float(string="60 -  120")
    bal_60_3= fields.Float(string="120 -  180")
    bal_60_4= fields.Float(string="180 - 240")
    bal_60_5= fields.Float(string="240 - 300")
    bal_60_6= fields.Float(string="300 - 360")
    bal_60_plus= fields.Float(string=" 360+  ")
    balance = fields.Float(string="Balance")
    payment_term_id = fields.Many2one('account.payment.term',string="Payment Term")


class wiz_wip_high_level_data(models.TransientModel):
    _name = 'wiz.wip.high.level.data'
    
    DOMAIN = [('parent_level0','Parent Level View'),('amc_view','AMC View'),('o_m_view','O&M View'),('credit','Credit'),('sup','Supply'),('imp','Implementation'),('sup_imp','Supply & Implementation'),
              ('amc','AMC'),('o_m','O&M'),('cust_trn','Customer Training'),('poc','(POC,Presales)'), ('comp_gen','Company General -(Training,Labs,Trips,etc.)')]
   
    project_type = fields.Selection(DOMAIN,string="Analytic Type")
    amended_cost = fields.Float(string="Amended Cost")
    amended_sale = fields.Float(string="Amended Sale")
    data_id = fields.Integer(string="Data ID")
    analytic_id = fields.Many2one('account.analytic.account',string="Analytic Account")
    balance = fields.Float(string="Balance")
    collected =fields.Float(string="Collected From Customer")
    partner_id = fields.Many2one('res.partner',string="Customer")
    status = fields.Selection([('normal','Normal'),('priority','Priority')],string="Priority")
    bal_30_1  = fields.Float(string="0  -  30")
    bal_30_2  = fields.Float(string="30 -  60")
    bal_30_3  = fields.Float(string="60 -  90")
    bal_30_4  = fields.Float(string="90 - 120")
    bal_30_5  = fields.Float(string="120 - 150")
    bal_30_6  = fields.Float(string="150 - 180")
    bal_30_plus = fields.Float(string=" 180+  ")
    
    bal_60_1 = fields.Float(string="0  -  60")
    bal_60_2 = fields.Float(string="60 -  120")
    bal_60_3 = fields.Float(string="120 -  180")
    bal_60_4 = fields.Float(string="180 - 240")
    bal_60_5 = fields.Float(string="240 - 300")
    bal_60_6 = fields.Float(string="300 - 360")
    bal_60_plus= fields.Float(string=" 360+  ")
    