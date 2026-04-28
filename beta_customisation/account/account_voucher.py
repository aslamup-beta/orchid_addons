# -*- coding: utf-8 -*-
from openerp import models, fields, api, _

class account_voucher(models.Model):
    _inherit = "account.voucher"
    od_analytic_line = fields.One2many('od.voucher.analytic.distribution','voucher_id',string="Analytic Distribution Line")
    is_bc = fields.Boolean(string="Bank Charge")
    bc_amount = fields.Float(string="Amount")
    bc_journal = fields.Many2one("account.journal","Journal")
    bc_debit_acc_id =fields.Many2one("account.account",string="Debit Account")
    bc_credit_acc_id =fields.Many2one("account.account",string="Credit Account")
    bc_narration = fields.Char("Narration")
    bc_move_id = fields.Many2one('account.move',string="Move")



    def move_post_bank_charge(self):
        if self.bc_move_id and self.bc_move_id.id:
            return True
        period_obj = self.env['account.period']
        move_obj = self.env['account.move']
        date = self.date
        period_ids = period_obj.find(date).id
        ref = self.name
        partner_id = self.partner_id.id
        journal_id = self.bc_journal and self.bc_journal.id
        debit_account = self.bc_debit_acc_id.id
        credit_account = self.bc_credit_acc_id.id
        bc_narration = self.bc_narration
        move_lines =[]
        amount = self.bc_amount
        
        vals1={
                'name': bc_narration,
                'ref': ref,
                'period_id': period_ids ,
                'journal_id': journal_id,
                'date': date,
                'account_id': credit_account,
                'debit': 0.0,
                'credit': abs(amount),
                'partner_id': partner_id,
               

            }
        vals2={
                'name': bc_narration,
                'ref': ref,
                'period_id': period_ids ,
                'journal_id': journal_id,
                'date': date,
                'account_id': debit_account,
                'credit': 0.0,
                'debit': abs(amount),
                'partner_id': partner_id,
                

            }
        move_lines.append([0,0,vals1])
        move_lines.append([0,0,vals2])
        
        move_vals = {

                'date': date,
                'ref': ref,
                'period_id': period_ids ,
                'journal_id': journal_id,
                'line_id':move_lines

                }
        move = move_obj.create(move_vals)
        move_id = move.id
        move.post()
        self.bc_move_id = move_id




class od_voucher_analytic_distribution(models.Model):
    _name = "od.voucher.analytic.distribution"
    voucher_id = fields.Many2one('account.voucher',string="Voucher")
    analytic_id =fields.Many2one('account.analytic.account',string="Analytic")
    amount = fields.Float(string="Amount")