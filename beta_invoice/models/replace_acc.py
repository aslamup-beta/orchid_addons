# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import Warning
class BetaReplaceAccount(models.TransientModel):
    _name = 'beta.replace.account'
    name = fields.Char('Name', required=True, help="Give name of the new entries")
    fiscalyear_id = fields.Many2one('account.fiscalyear','Fiscal Year', required=True)
    journal_id = fields.Many2one('account.journal', 'Journal', domain="[('type','=','situation')]",\
                                  required=True, \
                                  help='The best practice here is to use a journal dedicated  \
                                   to contain the opening entries of all fiscal years. Note that you \
                                   should define it with default debit/credit accounts, of type \'situation\' and with a centralized counterpart.')
    period_id = fields.Many2one('account.period', 'Opening Entries Period', required=True)
    transfer_line_ids = fields.One2many('beta.replace.account.line','trans_id',string="Transfer")
#     move_id = fields.Many2one('account.move',string="Journal Entry")
    state = fields.Selection([('draft','Draft'),('done','Done')],string="Status",default='draft')
    
    @api.one
    def unlink(self):
       
        if self.state != 'draft':
            raise Warning("Please Reset to Draft")
        return super(BetaReplaceAccount, self).unlink()
    def create_move(self,vals):
        
        move_obj = self.env['account.move']
        date = fields.Date.today()
        period_ids =vals.get('period_id')
        journal_id = vals.get('journal_id')
        move_lines = vals.get('move_lines')
        move_vals = {
                'date': date,
                'period_id': period_ids ,
                'journal_id': journal_id,
                'line_id':move_lines
                }
        move_id = move_obj.create(move_vals).id
        return move_id
    
    
    @api.one 
    def button_reset(self):
        self.write({'state':'draft'})
    
    
    def reconcile_fy_closing(self,cr, uid, ids, context=None):
            """
            This private function manually do the reconciliation on the account_move_line given as `ids´, and directly
            through psql. It's necessary to do it this way because the usual `reconcile()´ function on account.move.line
            object is really resource greedy (not supposed to work on reconciliation between thousands of records) and
            it does a lot of different computation that are useless in this particular case.
            """
            #check that the reconcilation concern journal entries from only one company
            
            obj_acc_move_line = self.pool.get('account.move.line')
            cr.execute('select distinct(company_id) from account_move_line where id in %s',(tuple(ids),))
            if len(cr.fetchall()) > 1:
                raise Warning('The entries to reconcile should belong to the same company.')
            r_id = self.pool.get('account.move.reconcile').create(cr, uid, {'type': 'auto', 'opening_reconciliation': True})
            cr.execute('update account_move_line set reconcile_id = %s where id in %s',(r_id, tuple(ids),))
            # reconcile_ref deptends from reconcile_id but was not recomputed
            obj_acc_move_line._store_set_values(cr, uid, ids, ['reconcile_ref'], context=context)
            obj_acc_move_line.invalidate_cache(cr, uid, ['reconcile_id'], ids, context=context)
            return r_id
    
    
    @api.one
    def button_replace(self):
        date = fields.Date.today()
        credit_account_id = False
        debit_account_id = False
        name = self.name 
        period_id = self.period_id and self.period_id.id 
        journal_id = self.journal_id and self.journal_id.id
        vals ={'period_id':period_id,'journal_id':journal_id}
        account_move_line = self.env['account.move.line']
        
        for line in self.transfer_line_ids:
            new_account_id = line.new_account_id and line.new_account_id.id or False
            old_acct_id = line.old_account_id and line.old_account_id.id or False
            od_cost_centre_id = line.od_cost_centre_id and line.od_cost_centre_id.id  or False
            od_branch_id = line.od_branch_id and line.od_branch_id.id or False
            od_division_id = line.od_division_id and line.od_division_id.id or False
            acc_move_lines = account_move_line.search([('account_id','=',old_acct_id),('period_id','=',period_id)]) 
            
            for line in  acc_move_lines:
                reconcile_id = line.reconcile_id.unlink()
                line.write({'reconcile_id':False,'account_id':new_account_id,
                'od_cost_centre_id':od_cost_centre_id,
                'od_branch_id':od_branch_id,
                'od_division_id':od_division_id})
               
                
#             acc_move_lines.write({
#                 'account_id':new_account_id,
#                 'od_cost_centre_id':od_cost_centre_id,
#                 'od_branch_id':od_branch_id,
#                 'od_division_id':od_division_id
#                 })
           
        self.state = 'done'
        return True
                               
     
class TransferAccountLine(models.TransientModel):
    _name = 'beta.replace.account.line'
    trans_id = fields.Many2one('beta.replace.account',string="Transfer")
    new_account_id = fields.Many2one('account.account',string="New Account")
    old_account_id = fields.Many2one('account.account',string="Old Account")
    od_cost_centre_id = fields.Many2one('od.cost.centre',string="Cost Centre")
    od_branch_id = fields.Many2one('od.cost.branch',string="Branch")
    od_division_id = fields.Many2one('od.cost.division',string="Division")
    
    
