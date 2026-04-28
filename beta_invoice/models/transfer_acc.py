# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import Warning
class BetaTransferAccount(models.Model):
    _name = 'beta.transfer.account'
    name = fields.Char('Name', required=True, help="Give name of the new entries")
    fiscalyear_id = fields.Many2one('account.fiscalyear','Fiscal Year', required=True)
    journal_id = fields.Many2one('account.journal', 'Journal',\
                                  required=True, \
                                  help='The best practice here is to use a journal dedicated  \
                                   to contain the opening entries of all fiscal years. Note that you \
                                   should define it with default debit/credit accounts, of type \'situation\' and with a centralized counterpart.')
    period_id = fields.Many2one('account.period', 'Opening Entries Period', required=True)
    transfer_line_ids = fields.One2many('beta.transfer.account.line','trans_id',string="Transfer",copy=True)
    move_id = fields.Many2one('account.move',string="Journal Entry",copy=False)
    state = fields.Selection([('draft','Draft'),('done','Done')],string="Status",default='draft')
    
    @api.one
    def unlink(self):
        if self.move_id:
            raise Warning("Please Delete the Journal Entry First")
        if self.state != 'draft':
            raise Warning("Please Reset to Draft")
        return super(BetaTransferAccount, self).unlink()
    
    def get_move_lines(self,period_id,account_id):
        result = []
        move_line_ob = self.env['account.move.line']
        move_line_ids = move_line_ob.search([('period_id','=',period_id),('account_id','=',account_id)])
        return move_line_ids
    
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
    
    @api.one 
    def button_transfer_detail(self):
        if self.move_id:
            raise Warning("Already JV Linked, Please Delete First")
        date = fields.Date.today()
        credit_account_id = False
        debit_account_id = False
        name = self.name 
        period_id = self.period_id and self.period_id.id 
        journal_id = self.journal_id and self.journal_id.id
        vals ={'period_id':period_id,'journal_id':journal_id}
        result = []
        for line in self.transfer_line_ids:
            new_account_id = line.new_account_id and line.new_account_id.id
            old_acct_id = line.old_account_id
            move_lines = self.get_move_lines(period_id, old_acct_id.id)
            for mvl in move_lines:
                if mvl.debit > 0.0:
                    vals1 = {
                          'name': mvl.name,
                           'period_id': period_id ,
                          'journal_id': journal_id,
                            'date': date,
                            'account_id': old_acct_id.id,
                            'debit': 0.0,
                            'credit': abs(mvl.debit),  
                        }
                    vals2 = {
                         'name': mvl.name,
                           'period_id': period_id ,
                          'journal_id': journal_id,
                            'od_branch_id':line.od_branch_id and line.od_branch_id.id or False,
                            'od_cost_centre_id':line.od_cost_centre_id and line.od_cost_centre_id.id or False,
                            'od_division_id':line.od_division_id and line.od_division_id.id or False,
                            'partner_id':mvl.partner_id and mvl.partner_id.id,
                            'analytic_account_id':mvl.analytic_account_id and mvl.analytic_account_id.id or False,
                            'date': date,
                            'account_id': new_account_id,
                            'debit': abs(mvl.debit),
                            'credit': 0.0,  
                        
                        }
                elif mvl.credit >0.0:
                    
                    vals1 = {
                          'name': mvl.name,
                           'period_id': period_id ,
                          'journal_id': journal_id,
                            'date': date,
                            'account_id': old_acct_id.id,
                            'debit': mvl.credit,
                            'credit':0.0,  
                        }
                    vals2 = {
                         'name': mvl.name,
                           'period_id': period_id ,
                          'journal_id': journal_id,
                            'od_branch_id':line.od_branch_id and line.od_branch_id.id or False,
                            'od_cost_centre_id':line.od_cost_centre_id and line.od_cost_centre_id.id or False,
                            'od_division_id':line.od_division_id and line.od_division_id.id or False,
                            'partner_id':mvl.partner_id and mvl.partner_id.id,
                            'analytic_account_id':mvl.analytic_account_id and mvl.analytic_account_id.id or False,
                            'date': date,
                            'account_id': new_account_id,
                            'debit': 0.0,
                            'credit': line.credit,  
                        
                        }
             
           
                result.append((0,0,vals1))
                result.append((0,0,vals2))
        vals['move_lines'] = result
        move_id = self.create_move(vals)
        self.move_id = move_id 
        self.state = 'done'
        return True
    
    @api.one
    def button_transfer(self):
        if self.move_id:
            raise Warning("Already JV Linked, Please Delete First")
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
            old_acct_id = line.old_account_id
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
                    'od_branch_id':line.od_branch_id and line.od_branch_id.id or False,
                    'od_cost_centre_id':line.od_cost_centre_id and line.od_cost_centre_id.id or False,
                    'od_division_id':line.od_division_id and line.od_division_id.id or False,
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
                    'od_branch_id':line.od_branch_id and line.od_branch_id.id or False,
                    'od_cost_centre_id':line.od_cost_centre_id and line.od_cost_centre_id.id or False,
                    'od_division_id':line.od_division_id and line.od_division_id.id or False,
                    'account_id': debit_account_id,
                    'credit': 0.0,
                    'debit': abs(balance),
                }
            move_lines.append((0,0,vals1))
            move_lines.append((0,0,vals2))
        vals['move_lines'] = move_lines
        move_id = self.create_move(vals)
        self.move_id = move_id 
        self.state = 'done'
        return True
                               
     
class TransferAccountLine(models.Model):
    _name = 'beta.transfer.account.line'
    trans_id = fields.Many2one('beta.transfer.account',string="Transfer")
    new_account_id = fields.Many2one('account.account',string="New Account")
    old_account_id = fields.Many2one('account.account',string="Old Account")
    od_cost_centre_id = fields.Many2one('od.cost.centre',string="Cost Centre")
    od_branch_id = fields.Many2one('od.cost.branch',string="Branch")
    od_division_id = fields.Many2one('od.cost.division',string="Division")
    
    
