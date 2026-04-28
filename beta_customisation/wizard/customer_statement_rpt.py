# -*- coding: utf-8 -*-
from openerp import models, fields, api
from pprint import pprint
from datetime import datetime
import openerp.addons.decimal_precision as dp


class customer_statement(models.TransientModel):
    _name = 'cust.statement.rpt.wiz'
    
    def get_default_partner_id(self):
        partner_id = False
        ctx = self.env.context 
        partner_id = ctx.get('active_id')
        return partner_id
    
    partner_id = fields.Many2one('res.partner',string="Customer",default=get_default_partner_id)
    
    def od_get_company_id(self):
        return self.env.user.company_id
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    
    
    
    def _mv_lines_get(self, partner_id,move_ids,payment_move_ids):
        moveline_obj = self.env['account.move.line']
        movelines = moveline_obj.search(
                [('partner_id', '=', partner_id),
                 ('move_id','not in',move_ids),('id','not in',payment_move_ids),
                    ('account_id.type', '=', 'receivable',),
                    ('move_id.state', '<>', 'draft'), ('reconcile_id', '=', False)])
        return movelines

    
    
    def get_data(self):
        partner_id = self.partner_id.id
        invoice_ids = self.env['account.invoice'].search([('state','in',('open', 'accept')),('type','=', 'out_invoice'), ('partner_id','=',partner_id),('account_id.type', '=', 'receivable')])
        move_ids = []
        payment_move_ids = []
        result  = []
        for inv in invoice_ids:
            due = inv.amount_total
            bal = inv.residual 
            paid = due -bal
            move_ids.append(inv.move_id.id)
            if paid:
                payment_move_ids += [pay.id for pay in inv.payment_ids]
            currency = inv.currency_id
            company_currency = inv.company_id.currency_id
            if currency != company_currency:
                due  = currency.compute(due,company_currency,round=False)
                bal =currency.compute(bal,company_currency,round=False)
                paid  = currency.compute(paid,company_currency,round=False)
            age = (datetime.strptime(datetime.strftime(datetime.now(), '%Y-%m-%d'),'%Y-%m-%d') - datetime.strptime(inv.move_id.date, '%Y-%m-%d')).days
            result.append((0,0,{
                'date':inv.move_id.date,
                'beta_ref':inv.number,
                'part_ref':inv.name or "/",
                'due':due,
                'paid':paid,
                'bal':bal,
                'age':age,
                'remark':inv.od_remarks[:20] if inv.od_remarks else "",
                'move_id':inv.move_id.id
                }))
        due_moves = self._mv_lines_get(partner_id, move_ids, payment_move_ids)
        for mvl in due_moves:
            age = (datetime.strptime(datetime.strftime(datetime.now(), '%Y-%m-%d'),'%Y-%m-%d') - datetime.strptime(mvl.move_id.date, '%Y-%m-%d')).days
            result.append((0,0,{
                'date':mvl.date,
                'beta_ref':mvl.ref,
                'part_ref':mvl.name or "/",
                'due':mvl.debit,
                'age':age,
                'paid':mvl.credit,
                'bal': mvl.debit - mvl.credit,
                'remark':  mvl.invoice.od_remarks[:20] if mvl.invoice.od_remarks else "",
                'move_id': mvl.move_id.id
                
                }))
        return result
    
    
    
    
    def _lines_get_ord(self, partner_id,period_lengh,ord):
        moveline_obj = self.env['account.move.line']
        movelines = moveline_obj.search(
                [('partner_id', '=', partner_id),
                    ('account_id.type', '=', 'receivable',),
                    ('move_id.state', '<>', 'draft'), ('reconcile_id', '=', False)])
        
        result = []
        x =(ord-1) * period_lengh 
        y = ord * period_lengh
        for move in movelines:
            age = (datetime.strptime(datetime.strftime(datetime.now(), '%Y-%m-%d'),'%Y-%m-%d') - datetime.strptime(move.date, '%Y-%m-%d')).days
            if x<age<=y:
                result.append(move.id)
        movelines = moveline_obj.browse(result)
        return movelines
    
    
    
    def _lines_get_plus(self, partner_id,period_length,ord):
        moveline_obj = self.env['account.move.line']
        movelines = moveline_obj.search(
                [('partner_id', '=', partner_id),
                    ('account_id.type', '=', 'receivable',),
                    ('move_id.state', '<>', 'draft'), ('reconcile_id', '=', False)])
        
        result = []
        y = period_length * ord
        for move in movelines:
            age = (datetime.strptime(datetime.strftime(datetime.now(), '%Y-%m-%d'),'%Y-%m-%d') - datetime.strptime(move.date, '%Y-%m-%d')).days
            if age>y:
                result.append(move.id)
        movelines = moveline_obj.browse(result)
        return movelines
    
    
    def get_bucket_vals(self,partner_id):
        
        period_length = 30
        
        due_zero_thirty = reduce(lambda x, y: x + ((y['account_id']['type'] == 'receivable' and y['debit'] or 0) ), self._lines_get_ord(partner_id,period_length,1), 0)
        due_thirty_sixty = reduce(lambda x, y: x + ((y['account_id']['type'] == 'receivable' and y['debit'] or 0) ), self._lines_get_ord(partner_id,period_length,2), 0)
        due_sixty_ninty = reduce(lambda x, y: x + ((y['account_id']['type'] == 'receivable' and y['debit'] or 0) ), self._lines_get_ord(partner_id,period_length,3), 0)
        due_ninty_onetwenty = reduce(lambda x, y: x + ((y['account_id']['type'] == 'receivable' and y['debit'] or 0) ), self._lines_get_ord(partner_id,period_length,4), 0)
        due_onetwenty_onefifty = reduce(lambda x, y: x + ((y['account_id']['type'] == 'receivable' and y['debit'] or 0) ), self._lines_get_ord(partner_id,period_length,5), 0)
        due_onefifty_oneeighty = reduce(lambda x, y: x + ((y['account_id']['type'] == 'receivable' and y['debit'] or 0) ), self._lines_get_ord(partner_id,period_length,6), 0)
        due_oneeighty_plus = reduce(lambda x, y: x + ((y['account_id']['type'] == 'receivable' and y['debit'] or 0) ), self._lines_get_plus(partner_id,period_length,6), 0)
            
        paid_zero_thirty = reduce(lambda x, y: x + ((y['account_id']['type'] == 'receivable' and y['credit'] or 0) ), self._lines_get_ord(partner_id,period_length,1), 0)
        paid_thirty_sixty = reduce(lambda x, y: x + ((y['account_id']['type'] == 'receivable' and y['credit'] or 0) ), self._lines_get_ord(partner_id,period_length,2), 0)
        paid_sixty_ninty = reduce(lambda x, y: x + ((y['account_id']['type'] == 'receivable' and y['credit'] or 0) ), self._lines_get_ord(partner_id,period_length,3), 0)
        paid_ninty_onetwenty = reduce(lambda x, y: x + ((y['account_id']['type'] == 'receivable' and y['credit'] or 0) ), self._lines_get_ord(partner_id,period_length,4), 0)
        paid_onetwenty_onefifty = reduce(lambda x, y: x + ((y['account_id']['type'] == 'receivable' and y['credit'] or 0)), self._lines_get_ord(partner_id,period_length,5), 0)
        paid_onefifty_oneeighty = reduce(lambda x, y: x + ((y['account_id']['type'] == 'receivable' and y['credit'] or 0) ), self._lines_get_ord(partner_id,period_length,6), 0)
        paid_oneeighty_plus = reduce(lambda x, y: x + ((y['account_id']['type'] == 'receivable' and y['credit'] or 0) ), self._lines_get_plus(partner_id,period_length,6), 0)
        tot_due = due_zero_thirty + due_thirty_sixty + due_sixty_ninty + due_ninty_onetwenty + due_onetwenty_onefifty + due_onefifty_oneeighty + due_oneeighty_plus
        tot_paid = paid_zero_thirty+paid_thirty_sixty+paid_sixty_ninty+paid_ninty_onetwenty+paid_onetwenty_onefifty+paid_onefifty_oneeighty+paid_oneeighty_plus
        
        bal1 = 0.00
        bal2 = 0.00
        bal3 = 0.00
        bal4 = 0.00
        bal5 = 0.00
        bal6 = 0.00
        bal7 = 0.00
        data = self.get_data()
        for line in data:
            if line[2]['age'] <=30:
                bal1 += line[2]['bal']
            if 30 < line[2]['age'] <=60:
                bal2 += line[2]['bal']
            if 60 < line[2]['age'] <=90:
                bal3 += line[2]['bal']
            if 90 < line[2]['age'] <=120:
                bal4 += line[2]['bal']
            if 120 < line[2]['age'] <=150:
                bal5 += line[2]['bal']
            if 150 < line[2]['age'] <=180:
                bal6 += line[2]['bal']
            if line[2]['age'] > 180:
                bal7 += line[2]['bal']
            
                    
            
        
        return {
            'due1':due_zero_thirty,
            'due2':due_thirty_sixty,
            'due3':due_sixty_ninty,
            'due4':due_ninty_onetwenty,
            'due5':due_onetwenty_onefifty,
            'due6':due_onefifty_oneeighty,
            'due7':due_oneeighty_plus,
            'paid1':paid_zero_thirty,
            'paid2':paid_thirty_sixty,
            'paid3':paid_sixty_ninty,
            'paid4':paid_ninty_onetwenty,
            'paid5':paid_onetwenty_onefifty,
            'paid6':paid_onefifty_oneeighty,
            'paid7':paid_oneeighty_plus,
            'bal1': bal1,
            'bal2':bal2,
            'bal3':bal3,
            'bal4':bal4,
            'bal5': bal5,
            'bal6': bal6,
            'bal7': bal7,
            'total':bal1+bal2+bal3+bal4+bal5+bal6+bal7
            }
    
    
    
    @api.multi
    def print_directly(self):
        data = self.get_data()
        partner_id = self.partner_id.id
        rpt_pool = self.env['od.cust.statement.rpt.data']
        currency_id = self.partner_id.company_id.currency_id.id
        vals = {
            'name': "Customer Statement Report",
            'partner_id':partner_id,
            'line_ids':data,
            'currency_id':currency_id,
            }
        bucket_vals = self.get_bucket_vals(partner_id)
        vals.update(bucket_vals)
        
        rpt =rpt_pool.create(vals)
        rpt_id =rpt.id
        ctx = self.env.context
        cr = self.env.cr
        uid = self.env.uid
        return self.pool['report'].get_action(cr, uid, [rpt_id], 'report.od_cust_statement', context=ctx)
    
    @api.multi 
    def export_rpt(self):
#         self.write({'wiz_line':result})
        data = self.get_data()
        partner_id = self.partner_id.id
        rpt_pool = self.env['od.cust.statement.rpt.data']
        currency_id = self.env.user.company_id.currency_id.id
        
        vals = {
            'name': "Customer Statement Report",
            'partner_id':partner_id,
            'line_ids':data,
            'currency_id':currency_id,
            }
        bucket_vals = self.get_bucket_vals(partner_id)
        vals.update(bucket_vals)
        
        rpt =rpt_pool.create(vals)
        rpt_id =rpt.id
        
        
        
        return {
            'name': 'Customer Statement',
            'view_type': 'form',
            'view_mode': 'form',
             'res_id':rpt_id,
            'res_model': 'od.cust.statement.rpt.data',
            'type': 'ir.actions.act_window',
        }
    
class customer_statement_rpt_data(models.TransientModel):
    _name = 'od.cust.statement.rpt.data'
    
    def od_get_currency(self):
        return self.env.uid.company_id.currency_id
    
    def _get_today_date(self):
        return datetime.today().strftime('%d-%b-%y')
    
    name = fields.Char()
    partner_id = fields.Many2one('res.partner',string="Customer", )
    line_ids = fields.One2many('cust.statement.rpt.data.line','wiz_id',string="Wiz Line",readonly=True)
    currency_id = fields.Many2one('res.currency',string='Currency') 
    date = fields.Date(default=_get_today_date)
    due1 = fields.Float(string="Due 1")
    due2 = fields.Float(string="Due 2")
    due3 = fields.Float(string="Due 3")
    due4 = fields.Float(string="Due 4")
    due5 = fields.Float(string="Due 5")
    due6 = fields.Float(string="Due 6")
    due7 = fields.Float(string="Due 7")
    
    paid1 = fields.Float(string="Paid 1")
    paid2 = fields.Float(string="Paid 2")
    paid3 = fields.Float(string="Paid 3")
    paid4 = fields.Float(string="Paid 4")
    paid5 = fields.Float(string="Paid 5")
    paid6 = fields.Float(string="Paid 6")
    paid7 = fields.Float(string="Paid 7")
    
    bal1 = fields.Float(string="Bal 1")
    bal2 = fields.Float(string="Bal 2")
    bal3 = fields.Float(string="Bal 3")
    bal4 = fields.Float(string="Bal 4")
    bal5 = fields.Float(string="Bal 5")
    bal6 = fields.Float(string="Bal 6")
    bal7 = fields.Float(string="Bal 7")
    
    total = fields.Float(string="Total")

    
    def print_cust_statement(self, cr, uid, ids, context=None):
        return self.pool['report'].get_action(cr, uid, ids, 'report.od_cust_statement', context=context)
    
class customer_statement_rpt_data_line(models.TransientModel):
    _name = 'cust.statement.rpt.data.line'
    _order = 'date desc'
    
    company_id = fields.Many2one('res.company',string="Company")
    wiz_id = fields.Many2one('od.cust.statement.rpt.data',string="Wizard")
    s_no = fields.Integer(string="S N")
    date = fields.Date(string='Date')
    beta_ref = fields.Char(string="Beta IT Reference")
    part_ref = fields.Char(string="Partner Reference")
    age = fields.Integer(string="Age(Days)")
    due = fields.Float(string="Amount", digits=(16,2))
    paid = fields.Float(string="Paid", digits=(16,2))
    bal = fields.Float(string="Balance",digits=(16,2))
    remark = fields.Char(string="Remarks")
    move_id = fields.Many2one('account.move', string="Move")
    
    @api.multi
    def btn_open_move(self):
        
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.move',
                'res_id':self.move_id and self.move_id.id or False,
                'type': 'ir.actions.act_window',
                'target': 'new',
 
            }
