from openerp import models, fields, api, _
from openerp.osv import osv
from openerp.tools.translate import _
from openerp.exceptions import Warning
import openerp.addons.decimal_precision as dp
class od_wip(models.Model):
    _name = 'od.wip'
    _order = 'id desc'
    
    def od_get_company_id(self):
        return self.env.user.company_id
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    name = fields.Char(string='Title', required=True,readonly=True, states={'draft': [('readonly', False)]})
    date = fields.Date(required=True,readonly=True, states={'draft': [('readonly', False)]})
    project_id = fields.Many2one('account.analytic.account','Project/Contract',required=True,readonly=True, states={'draft': [('readonly', False)]})
    wip_account_balance = fields.Float(string='WIP Balance',required=True,readonly=True, states={'draft': [('readonly', False)]},digits=dp.get_precision('Account'))
    wip_account_id = fields.Many2one('account.account','WIP Account',required=True,readonly=True, states={'draft': [('readonly', False)]})
    invoice_amount = fields.Float(string="Invoice Amount",readonly=True,states={'draft': [('readonly', False)]},copy=False,digits=dp.get_precision('Account'))
    provision_account_id = fields.Many2one('account.account','Provision Account',readonly=True, states={'draft': [('readonly', False)]})
    journal_id = fields.Many2one('account.journal','Journal',required=True,readonly=True,states={'draft': [('readonly', False)]})
    expense_account_id = fields.Many2one('account.account','Expense Account',required=True,readonly=True,states={'draft': [('readonly', False)]})
    provision_percentage = fields.Float('Provision %',readonly=True, states={'draft': [('readonly', False)]},copy=False,digits=dp.get_precision('Account'))
    provision_amount = fields.Float(string='Provision Amount',readonly=True, states={'draft': [('readonly', False)]},copy=False,digits=dp.get_precision('Account'))
    project_cost = fields.Float(string="Project Cost",readonly=True,states={'draft': [('readonly', False)]},copy=False,digits=dp.get_precision('Account'))
    invoice_account_id  = fields.Many2one('account.account','Invoice Account',required=True,readonly=True,states={'draft': [('readonly', False)]})
    income_account_id = fields.Many2one('account.account','Income Account',required=True,readonly=True,states={'draft': [('readonly', False)]})
    move = fields.Many2one('account.move','Journal Entry',readonly=True,copy=False)
    state = fields.Selection([('draft','Draft'),('done','Done')],default='draft',string='State')
    provision = fields.Boolean('Provision',readonly=True,states={'draft': [('readonly', False)]},copy=False)
    profit = fields.Float(string='Profit',compute='get_profit',store=True,digits=dp.get_precision('Account'))
    
    
    
    @api.one
    @api.depends('invoice_amount','project_cost')
    def get_profit(self):
        self.profit = self.invoice_amount - self.project_cost
    @api.one
    def unlink(self):
        if self.state != 'draft':
            raise osv.except_osv(_('User Error!'), _('You can only delete draft Wip'))
        return super(od_wip, self).unlink()

    
    def onchange_analytic_account(self,cr,uid,ids,analytic_acc_id,wip_acc_id,invoice_account_id,context=None):
        invoice_amount=0.0
        wip_balance = 0.0
        if analytic_acc_id and wip_acc_id and invoice_account_id:
          
            query_param1 = (wip_acc_id,analytic_acc_id,)
            query_param2 = (invoice_account_id,analytic_acc_id,)
            query1 = ("select sum(debit-credit) from account_move_line where account_id =%s and analytic_account_id = %s and state='valid'"%query_param1)
            query2 = "select sum(credit-debit) from account_move_line where account_id =%s and analytic_account_id = %s and state='valid'"%query_param2
            cr.execute(query1)
            wip_balance = cr.fetchone()[0]
            cr.execute(query2)
            invoice_amount = cr.fetchone()[0]
        else:
            invoice_amount =0.0
            wip_balance =0.0
        return {'value':{'invoice_amount':invoice_amount,'wip_account_balance':wip_balance}}
    @api.onchange('wip_account_balance','invoice_amount','provision_percentage')
    def onchange_invoice_amount(self):
        invoice_amount = self.invoice_amount
        wip_amount = self.wip_account_balance
        prov_perc = self.provision_percentage
        self.project_cost = wip_amount + (invoice_amount*prov_perc/100)
        self.provision_amount = invoice_amount*prov_perc/100
    
  
       
    @api.one
    def validate(self):
            date = self.date
            period_obj = self.env['account.period']
            period_id = period_obj.find(date).id
            journal_id = self.journal_id and self.journal_id.id
            wip_acc_id = self.wip_account_id and self.wip_account_id.id
            expense_acc_id = self.expense_account_id and self.expense_account_id.id
            inv_acc_id = self.invoice_account_id and self.invoice_account_id.id 
            income_acc_id = self.income_account_id and self.income_account_id.id
            prov_acc_id = self.provision_account_id and self.provision_account_id.id
            analytic_acc_id = self.project_id and self.project_id.id
            partner_id = self.project_id and self.project_id.partner_id and self.project_id.partner_id.id or False
            wip_balance = self.wip_account_balance
            cost = self.project_cost
            invoice_amount = self.invoice_amount
            provision_amount = self.provision_amount
            name =self.name
            line_name = self.name
            
            od_cost_centre_id = self.project_id and self.project_id.od_cost_centre_id and self.project_id.od_cost_centre_id.id or False 
            od_branch_id  = self.project_id and self.project_id.od_branch_id and self.project_id.od_branch_id.id or False 
            od_division_id = self.project_id and self.project_id.od_division_id and self.project_id.od_division_id.id
            manual = self.project_id.od_manual 
            if manual:
                od_cost_centre_id = self.project_id and self.project_id.cost_centre_id and self.project_id.cost_centre_id.id or False 
                od_branch_id  = self.project_id and self.project_id.branch_id and self.project_id.branch_id.id or False 
                od_division_id = self.project_id and self.project_id.division_id and self.project_id.division_id.id
                
            if not (od_cost_centre_id and od_branch_id and od_division_id):
                raise Warning("In Analytic Cost center and Branch and Division Must be Linked")
            l1 = {
                'name': line_name,
                'credit': wip_balance,
                'debit':0.0,
                'account_id': wip_acc_id,
                'analytic_account_id':analytic_acc_id,
                'partner_id':partner_id,
                'date':self.date,
                'od_cost_centre_id': od_cost_centre_id,
                'od_branch_id':od_branch_id,
                'od_division_id':od_division_id,
            }
            l2 = {
                'name':line_name,
                'debit': cost,
                'credit':0.0 ,
                'account_id': expense_acc_id ,
                'analytic_account_id':analytic_acc_id,
                'partner_id':partner_id,
                'date':self.date,
                'od_cost_centre_id': od_cost_centre_id,
                'od_branch_id':od_branch_id,
                'od_division_id':od_division_id,
            }
            l4= {
                'name':line_name,
                'debit': invoice_amount,
                'credit':0.0 ,
                'account_id': inv_acc_id ,
                'analytic_account_id':analytic_acc_id,
                'partner_id':partner_id,
                'date':self.date,
                'od_cost_centre_id': od_cost_centre_id,
                'od_branch_id':od_branch_id,
                'od_division_id':od_division_id,
                 
                 }
            l5= {
                'name':line_name,
                'debit': 0.0,
                'credit':invoice_amount,
                'account_id': income_acc_id,
                'analytic_account_id':analytic_acc_id,
                'partner_id':partner_id,
                'date':self.date,
                'od_cost_centre_id': od_cost_centre_id,
                'od_branch_id':od_branch_id,
                'od_division_id':od_division_id,
                 
                 }
            if self.provision and prov_acc_id:
                l3 = {
                    'name':line_name,
                    'credit':provision_amount,
                    'debit':0.0,
                    'account_id':prov_acc_id,
                    'analytic_account_id':analytic_acc_id,
                    'partner_id':partner_id,
                    'date':self.date,
                    'od_cost_centre_id': od_cost_centre_id,
                    'od_branch_id':od_branch_id,
                    'od_division_id':od_division_id,
                    }
                line_ids = [(0,0,l1),(0, 0, l2),(0, 0, l3),(0,0,l4),(0,0,l5)]
            else:
                line_ids = [(0,0,l1),(0, 0, l2),(0,0,l4),(0,0,l5)]
            move = self.env['account.move'].create({
                'narration':name,
                'line_id': line_ids,
                'journal_id': journal_id,
                'period_id': period_id,
                'date': self.date,
            })
            self.move = move
            self.state = 'done'
            self.project_id.set_close()
            return self.write({})
        