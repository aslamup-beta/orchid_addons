from openerp import models, fields, api, _
class account_invoice(models.Model):
    _inherit = "account.invoice"
    
#    @api.one 
#    @api.depends('partner_id') 
#    def _get_analytic_account(self):
#        if self.partner_id:
#            partner_id =self.partner_id.id
#            analytic_default_obj=self.env['account.analytic.default'].search([('partner_id','=',partner_id)])
#            if analytic_default_obj:
#                analytic_id =analytic_default_obj[0] and analytic_default_obj[0].analytic_id and analytic_default_obj[0].analytic_id.id
#                if analytic_id:
#                    self.od_analytic_account = analytic_id
            
    
#    od_analytic_account = fields.Many2one('account.analytic.account',string='Analytic Account',compute='_get_analytic_account',store=True) 
    od_analytic_account = fields.Many2one('account.analytic.account',string='Analytic Account') 
    
    
    def assign_analytic(self,cr,uid,ids,context=None):
        so_ids = self.search(cr, uid,[])
        account_invoice_line =self.pool.get('account.invoice.line')
        for so in self.browse(cr, uid, so_ids):
            part = so.partner_id.id
            if part:
                analytic_default_obj=self.pool.get('account.analytic.default')
                analytic_default_id = analytic_default_obj.search(cr,uid,[('partner_id','=',part)])
                if analytic_default_id:
                    analytic_id =analytic_default_obj.browse(cr,uid,analytic_default_id[0]).analytic_id.id
                    if analytic_id:
                        vals={'od_analytic_account':analytic_id}
                        for line in so.invoice_line:
                            account_invoice_line.write(cr,uid,[line.id],{'account_analytic_id':analytic_id})
                        self.write(cr, uid,[so.id],vals)
                        
    @api.multi
    def onchange_partner_id(self, type, partner_id, date_invoice=False,
            payment_term=False, partner_bank_id=False, company_id=False):
        res = super(account_invoice, self).onchange_partner_id(type, partner_id, date_invoice,
            payment_term, partner_bank_id, company_id)
        if partner_id:
            res_obj = self.env['res.partner'].browse(partner_id)
            user_id = res_obj.user_id or False
            analytic_default_obj=self.env['account.analytic.default'].search([('partner_id','=',partner_id)])
            analytic_id = analytic_default_obj and analytic_default_obj[0] and analytic_default_obj[0].analytic_id and analytic_default_obj[0].analytic_id.id
            if analytic_id:
                res['value'].update({'od_analytic_account':analytic_id,'user_id':user_id})
        return res
    @api.model
    def create(self, values):
        if not values.get('date_due'):
            payment_term = values.get('payment_term')
            date_invoice = values.get('date_invoice')
            res=self.onchange_payment_term_date_invoice(payment_term,date_invoice)
            values.update(res['value'])
        return super(account_invoice, self).create(values)

#    @api.multi
#    def invoice_validate(self):
#        move_id = self.move_id and self.move_id.id or False

#        if self.partner_id.supplier and move_id:
#            for obj in self.invoice_line:
#                product_id = obj.product_id and obj.product_id.id or False
#                if product_id:
#                    debit = 0
#                    obj.write({'od_line_cost': debit})
#        if self.partner_id.customer and move_id:
#            for obj in self.invoice_line:
#                product_id = obj.product_id and obj.product_id.id or False
#                if product_id:
#                    move_line_ids = self.env['account.move.line'].search([('product_id','=',product_id),('move_id','=',move_id),('state','=','valid')]) 
#                    debit = 0
#                    for obje in move_line_ids:
#                        debit = debit + obje.debit
#                obj.write({'od_line_cost': debit})
#        return self.write({'state': 'open'})
#    def write(self,cr,uid,ids,vals,context=None):
#        invoice_line_ids = self.pool.get('account.invoice.line').search(cr, uid, [('invoice_id','=',ids[0])])
#        if invoice_line_ids:
#            account_analytic_id =self.pool.get('account.invoice.line').browse(cr,uid,invoice_line_ids[0]).account_analytic_id.id
#            
#        move_id = vals.get('move_id')
#        if move_id :
#            move_lines = self.pool.get('account.move.line').search(cr,uid,[('move_id','=',move_id)])
#            for line in move_lines:
#                self.pool.get('account.move.line').write(cr,uid,[line],{'analytic_account_id':account_analytic_id},context=context)
#        return super(account_invoice,self).write(cr,uid,ids,vals,context=context)
#        if self.partner_id.supplier and move_id:
#            for obj in self.invoice_line:
#                product_id = obj.product_id and obj.product_id.id or False
#                if product_id:
#                    debit = 0
#                    obj.write({'od_line_cost': debit})
#        if self.partner_id.customer and move_id:
#            for obj in self.invoice_line:
#                product_id = obj.product_id and obj.product_id.id or False
#                if product_id:
#                    move_line_ids = self.env['account.move.line'].search([('product_id','=',product_id),('move_id','=',move_id),('state','=','valid')]) 
#                    debit = 0
#                    for obje in move_line_ids:
#                        debit = debit + obje.debit
#                obj.write({'od_line_cost': debit})
#        return self.write({'state': 'open'})
#    def write(self,cr,uid,ids,vals,context=None):
#        invoice_line_ids = self.pool.get('account.invoice.line').search(cr, uid, [('invoice_id','=',ids[0])])
#        if invoice_line_ids:
#            account_analytic_id =self.pool.get('account.invoice.line').browse(cr,uid,invoice_line_ids[0]).account_analytic_id.id
#            
#        move_id = vals.get('move_id')
#        if move_id :
#            move_lines = self.pool.get('account.move.line').search(cr,uid,[('move_id','=',move_id)])
#            for line in move_lines:
#                self.pool.get('account.move.line').write(cr,uid,[line],{'analytic_account_id':account_analytic_id},context=context)
#        return super(account_invoice,self).write(cr,uid,ids,vals,context=context)

#class account_invoice_line(models.Model):
#    _inherit = "account.invoice.line"
#    od_line_cost = fields.Float(string='Total Cost',store=True,readonly="1")
