from openerp import models, fields, api, _

class PreoprnLog(models.Model):
    
    _name = 'od.pre_opr.log'
    _description = 'Pre-Operation Logs'
    
    def od_get_company_id(self):
        return self.env.user.company_id
    
    opp_id = fields.Many2one('crm.lead', 'Opportunity')
    cancel_date = fields.Date(string="Cancelled Date")
    cancel_by = fields.Many2one('res.users', 'Cancelled_by')
    sam_id = fields.Many2one('res.users', 'Salesperson')
    amount = fields.Float()
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
 
class CrmLead(models.Model):
    
    _inherit = 'crm.lead'
    lost_date = fields.Date(string="Lost Date/Cancelled Date")
    sm_io1 = fields.Text(string="GM Input-Why We lost")
    sm_io2 = fields.Text(string="GM Input-Solution")
    tum_io1 = fields.Text(string="Technology Unit Manger Input-Why We lost")
    tum_io2 = fields.Text(string="Technology Unit Manger Input-Solution")
    portal_date = fields.Datetime(string="Last Day/Time to Submit on Etimad or Customer Portal")
    
    def create_pre_opne_cost_move(self, preopr_cost):
        company_id = self.company_id and self.company_id.id or False
        period_obj = self.env['account.period']
        move_obj = self.env['account.move']
        date = fields.Date.today()
        period_ids = period_obj.find(date).id
        ref = self.od_number
        journal_id = self.get_product_id_from_param('pre_op_journal_id')
        debit_account = self.get_product_id_from_param('expense_account_id')
        credit_account = self.get_product_id_from_param('pre_op_account_id')
        cost_centre_id = 93
        if company_id ==6:
            journal_id = self.get_product_id_from_param('pre_op_journal_id_ksa')
            debit_account = self.get_product_id_from_param('expense_account_id_ksa')
            credit_account = self.get_product_id_from_param('pre_op_account_id_ksa')
            cost_centre_id = 65
            
        
        partner_id =self.partner_id and self.partner_id.id or False
        od_opp_id = self.id or False
        amount = preopr_cost
        move_lines =[]
        branch_id = self.od_branch_id and self.od_branch_id.id or False
        
        if branch_id == 2:
            debit_account = 5689
            credit_account = 6632
            cost_centre_id = 4
        vals1={
                'name': ref,
                'ref': ref,
                'period_id': period_ids ,
                'journal_id': journal_id,
                'date': date,
                'account_id': credit_account,
                'debit': 0.0,
                'od_opp_id':od_opp_id,
                'credit': abs(amount),
                'partner_id':partner_id,
                'od_branch_id': branch_id,
                'od_cost_centre_id': cost_centre_id

            }
        vals2={
                'name': ref,
                'ref': ref,
                'period_id': period_ids ,
                'journal_id': journal_id,
                'date': date,
                'account_id': debit_account,
                'credit': 0.0,
                'od_opp_id':od_opp_id,
                'debit': abs(amount),
                'partner_id':partner_id,
                'od_branch_id': branch_id,
                'od_cost_centre_id': cost_centre_id

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
        move_id = move_obj.create(move_vals).id
#         self.pre_opn_move_id = move_id
        
        return True
    
    def get_product_id_from_param(self,product_param):
        parameter_obj = self.env['ir.config_parameter']
        key =[('key', '=', product_param)]
        product_param_obj = parameter_obj.search(key)
        if not product_param_obj:
            raise Warning(_('Settings Warning!'),_('NoParameter Not defined\nconfig it in System Parameters with %s'%product_param))
        product_id = product_param_obj.od_model_id and product_param_obj.od_model_id.id or False
        return product_id
    
    def calculate_preopr_cost(self):
        pre_op_cost =0.0
        company_id = self.company_id and self.company_id.id or False
        account_id_dxb = self.get_product_id_from_param('pre_op_account_id')
        account_id = [6632] + [account_id_dxb]
        if company_id ==6:
            account_id = [self.get_product_id_from_param('pre_op_account_id_ksa')]
        moveline_obj = self.env['account.move.line']
        movelines = moveline_obj.search([('od_opp_id', '=', self.id),
                                            ('move_id.state', '<>', 'draft'), 
                                            ('account_id', 'in', account_id)])  
        if movelines:
            pre_op_cost = sum([line.debit - line.credit for line in movelines])
        return pre_op_cost
    
    def create_pre_opn_log(self, preopr_cost):
        pre_op_log_obj = self.env['od.pre_opr.log']
        vals = {'opp_id': self.id,
                'cancel_date': fields.Date.today(),
                'cancel_by': self.env.user and self.env.user.id or False,
                'sam_id':self.user_id and self.user_id.id or False,
                'amount': preopr_cost}
        log_id = pre_op_log_obj.create(vals)
        return log_id
    
    @api.multi
    def write(self, vals):
        stage_id = vals.get('stage_id')
        current_stage_id = self.stage_id.id
        if not current_stage_id in (7,8,13): #Bug Fix: No Need to create Jv's when moving from Lost -> Cancel or Cancel ->Lost
            if stage_id in (7,8,13):
                #self.od1_send_mail('crm_cancel_email_template')
                preopr_cost = self.calculate_preopr_cost()
                vals.update({'lost_date':fields.Date.today()})
                if preopr_cost:
                    move_id = self.create_pre_opne_cost_move(preopr_cost)
                    log_id = self.create_pre_opn_log(preopr_cost)
        return super(CrmLead, self).write(vals)
    
    