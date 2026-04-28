from openerp import models, fields, api
from openerp.tools import amount_to_text_en
import re


class ChequePrint(models.Model):
    
    _name = 'od.cheque.print'
    _description = "Cheque Print"
    _order = 'date desc'
    _rec_name = "ref"
    
    def od_get_company_id(self):
        return self.env.user.company_id
    
    name = fields.Many2one('od.cust.partner', string='Cheque To')
    partner_id = fields.Many2one('res.partner', string='Cheque To')
    custom = fields.Boolean("Custom")
    ac_pay = fields.Boolean("A/C Payee")
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    date = fields.Date(string='Cheque Date')
    amount = fields.Float(string="Amount")
    amt_words = fields.Char('Amount in Words')
    ref = fields.Char('Reference')
    title = fields.Selection([
            ('Mr.','Mr.'),
            ('Mrs.','Mrs.'),
        ],string="Contact Title")
    
    @api.onchange('amount')
    def onchange_amount(self):
        print "xx"*88
        amount = self.amount or 0.0
        currency = self.env.user.company_id.currency_id.name
        convert_amount_in_words = amount_to_text_en.amount_to_text(amount, lang='en', currency=currency)        
        convert_amount_in_words = convert_amount_in_words.replace('AED','')
        convert_amount_in_words = convert_amount_in_words.replace('-',' ')
        company_id = self.company_id and self.company_id.id
        if company_id ==6:
            convert_amount_in_words = convert_amount_in_words.replace('Cent', 'Halala')
        else:
            convert_amount_in_words = convert_amount_in_words.replace('Cent', 'Fil')
        amt_words = re.sub('[,]', '', convert_amount_in_words)
        self.amt_words = amt_words or ''
    
class BetaCustomPartner(models.Model):
    
    _name = 'od.cust.partner'
    _description = "Beta Custom Partner"
    
    def od_get_company_id(self):
        return self.env.user.company_id
    
    name = fields.Char()
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
        