# -*- coding: utf-8 -*-

from openerp import models, fields, api
class TransferAccount(models.TransientModel):
    _name = 'wiz.transfer.account'
    name = fields.Char('Name of new entries', required=True, help="Give name of the new entries")
    fiscalyear_id = fields.Many2one('account.fiscalyear','Fiscal Year', required=True)
    journal_id = fields.Many2one('account.journal', 'Journal', domain="[('type','=','situation')]",\
                                  required=True, \
                                  help='The best practice here is to use a journal dedicated  \
                                   to contain the opening entries of all fiscal years. Note that you \
                                   should define it with default debit/credit accounts, of type \'situation\' and with a centralized counterpart.')
    period_id = fields.Many2one('account.period', 'Opening Entries Period', required=True)
    transfer_line_ids = fields.One2many('wiz.transfer.account.line','wiz_id',string="Transfer")
    
   
    

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
    def button_transfer(self):
        date = fields.Date.today()
        credit_account_id = False
        debit_account_id = False
        name = self.name 
        period_id = self.period_id and self.period_id.id 
        journal_id = self.journal_id and self.journal_id.id
        vals ={'period_id':period_id,'journal_id':journal_id}
        move_lines = []
        for line in self.transfer_line_ids:
            new_account_id = line.new_account_id and line.new_account_id.id
            for old_acct_id in line.old_account_ids:
                balance = old_acct_id.balance
                if balance <0.0:
                    credit_account_id = new_account_id
                    debit_account_id = old_acct_id.id
                else:
                    credit_account_id = old_acct_id.id
                    debit_account_id = new_account_id
                vals1={
                    'name': name,
                    'period_id': period_id ,
                    'journal_id': journal_id,
                    'od_branch_id':old_acct_id.od_branch_id and old_acct_id.od_branch_id.id or False,
                    'od_cost_centre_id':old_acct_id.od_cost_centre_id and old_acct_id.od_cost_centre_id.id or False,
                    'date': date,
                    'account_id': credit_account_id,
                    'debit': 0.0,
                    'credit': abs(balance),
                    }
                vals2={
                    'name': name,
                    'period_id': period_id,
                    'journal_id': journal_id,
                    'date': date,
                    'od_branch_id':old_acct_id.od_branch_id and old_acct_id.od_branch_id.id or False,
                    'od_cost_centre_id':old_acct_id.od_cost_centre_id and old_acct_id.od_cost_centre_id.id or False,
                    'account_id': debit_account_id,
                    'credit': 0.0,
                    'debit': abs(balance),
                }
                move_lines.append((0,0,vals1))
                move_lines.append((0,0,vals2))
        vals['move_lines'] = move_lines
        move_id = self.create_move(vals)
        return True
                               
     
class TransferAccountLine(models.TransientModel):
    _name = 'wiz.transfer.account.line'
    wiz_id = fields.Many2one('wiz.transfer.account',string="Wizard")
#     old_accnt_ids = fields.Many2many('account.account','wizard_accoun_wiz_accounts_temp','line_id','account_id',string="Accounts")
    new_account_id = fields.Many2one('account.account',string="New Chart Of Account")
    old_account_ids = fields.Many2many('account.account','wizrd_rel_account_transfer_beta_wiz', 'wizard_id', 'account_id', string="Accounts")
    

    
    
