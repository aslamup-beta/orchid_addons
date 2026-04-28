import time
from datetime import datetime

from openerp.osv import fields, osv,expression
from openerp import tools
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class account_analytic_account(osv.osv):
    _inherit = 'account.analytic.account'
    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        if isinstance(ids, (int, long)):
                    ids = [ids]
        reads = self.read(cr, uid, ids, ['name', 'code'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['code']:
                name ='[' + record['code'] +  ']' + name
            res.append((record['id'], name))
        return res
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        args.append(('state', 'in', ('open','sign_off')))
        if operator in expression.NEGATIVE_TERM_OPERATORS:
            domain = [('code', operator, name), ('name', operator, name)]
        else:
            domain = ['|', ('code', operator, name), ('name', operator, name)]
        ids = self.search(cr, user, expression.AND([domain, args]), limit=limit, context=context)
        return self.name_get(cr, user, ids, context=context)
#class account_invoice(osv.osv):
# _inherit = 'account.invoice'
# def write(self,cr,uid,ids,vals,context=None):
#     invoice_line_ids = self.pool.get('account.invoice.line').search(cr, uid, [('invoice_id','=',ids[0])])
#     if invoice_line_ids:
#         account_analytic_id =self.pool.get('account.invoice.line').browse(cr,uid,invoice_line_ids[0]).account_analytic_id.id
#         print "account analytic idddddddddddddddddddddddddd",account_analytic_id
#     move_id = vals.get('move_id')
#     if move_id :
#         move_lines = self.pool.get('account.move.line').search(cr,uid,[('move_id','=',move_id)])
#         for line in move_lines:
#             self.pool.get('account.move.line').write(cr,uid,[line],{'analytic_account_id':account_analytic_id},context=context)
#             
#     
#     return super(account_invoice,self).write(cr,uid,ids,vals,context=context)
#         
