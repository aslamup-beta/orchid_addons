# -*- coding: utf-8 -*-
import time
from openerp import models, fields, api

from pprint import pprint
from datetime import datetime
import openerp.addons.decimal_precision as dp

class inv_pay_details_rpt(models.TransientModel):
    _name = 'inv.pay.rpt.wiz'
    
    
    cust_ids = fields.Many2many('res.partner',string="Customer")
    date_start = fields.Date(string="Invoice Date From")
    date_end = fields.Date(string="Invoice Date To")
    wiz_line = fields.One2many('inv.pay.rpt.data.line','org_wiz_id',string="Wiz Line")
    
    def od_get_company_id(self):
        return self.env.user.company_id
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    
    
    def _get_paid_invoices(self):
        inv_obj = self.env['account.invoice']
        company_id = self.company_id and self.company_id.id 
        domain = [('company_id','=',company_id),('state','=','paid'),('type','=','out_invoice')]
        date_start = self.date_start
        date_end = self.date_end
        if date_start:
            domain += [('date_invoice','>=',date_start)]
        if date_end:
            domain += [('date_invoice','<=',date_end)]
        cust_ids = [pr.id for pr in self.cust_ids]
        if cust_ids:
            domain += [('partner_id','in', cust_ids)]
        invoice_data = inv_obj.search(domain)
        return invoice_data
    
    def get_pay_date(self,invoice_id):
        inv_obj = self.env['account.invoice']
        inv = inv_obj.search([('id','=', invoice_id)])
        datez = []
        pay_ids = inv.payment_ids
        for line in pay_ids:
            datez.append(line.date)
        pay_date = max(datez)
        return pay_date

    def get_detailed_data(self):        
        result  = []
        invoices = self._get_paid_invoices()
        for inv in invoices:
            inv_date = inv.date_invoice
            pay_date = self.get_pay_date(inv.id)
            age = (datetime.strptime(pay_date, '%Y-%m-%d') - datetime.strptime(inv_date, '%Y-%m-%d')).days
            result.append((0,0,{
                'inv_id':inv.id,
                'age':age,
                'name': inv.number,
                'inv_amount': inv.amount_untaxed,
                'partner_id': inv.partner_id and inv.partner_id.id,
                'invoice_date': inv_date,
                'pay_date':pay_date
                }))
        return result
    

#     @api.multi
#     def print_directly(self):
#         if self.detail:
#             data = self.get_detailed_data()
#             rpt_temp = 'report.od_pre_oprn_rpt'
#         else:
#             data = self.get_data()
#             rpt_temp = 'report.od_pre_oprn_anal_rpt1'
#         account_id = self.account_id.id
#         rpt_pool = self.env['pre.oprn.rpt.data']
#         currency_id = self.env.user.company_id.currency_id.id
#         vals = {
#             'name': "Pre Operation Analysis Report",
#             'account_id':account_id,
#             'line_ids':data,
#             'currency_id':currency_id,
#             }
#         
#         rpt =rpt_pool.create(vals)
#         rpt_id =rpt.id
#         ctx = self.env.context
#         cr = self.env.cr
#         uid = self.env.uid
#         return self.pool['report'].get_action(cr, uid, [rpt_id], rpt_temp , context=ctx)
    
    @api.multi
    def export_rpt(self):
        model_data = self.env['ir.model.data']
        result = self.get_detailed_data()
        vw = 'tree_view_inv_pay_detail'            
        tree_view = model_data.get_object_reference( 'beta_customisation', vw)
        self.wiz_line.unlink()
        self.write({'wiz_line':result})
        del(result)
        return {
            'domain': [('org_wiz_id','=',self.id)],
            'name': 'Invoice Payment Analysis Report',
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(tree_view and tree_view[1] or False, 'tree')],
            'res_model': 'inv.pay.rpt.data.line',
            'type': 'ir.actions.act_window',
        }


      
class inv_pay_rpt_data(models.TransientModel):
    _name = 'inv.pay.rpt.data'
    
    def od_get_currency(self):
        return self.env.uid.company_id.currency_id
    
    def _get_today_date(self):
        return datetime.today().strftime('%d-%b-%y')
    
    name = fields.Char()
    line_ids = fields.One2many('inv.pay.rpt.data.line','wiz_id',string="Wiz Line",readonly=True)
    currency_id = fields.Many2one('res.currency',string='Currency') 
    date = fields.Date(default=_get_today_date)
        
class inv_pay_rpt_data_line(models.TransientModel):
    _name = 'inv.pay.rpt.data.line'
    _order = 'invoice_date'
    
    def od_get_company_id(self):
        return self.env.user.company_id
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)

    
    wiz_id = fields.Many2one('inv.pay.rpt.data',string="Wizard data")
    org_wiz_id = fields.Many2one('inv.pay.rpt.wiz',string="Wizard")
    inv_id = fields.Many2one('account.invoice',string="Invoice")
    name = fields.Char(string="Invoice Number")
    inv_amount = fields.Float(string="Invoice Amount")
    partner_id = fields.Many2one('res.partner', string="Customer Name")
    invoice_date = fields.Date(string="Invoice Date")
    pay_date = fields.Date(string="Payment Date")
    age = fields.Integer(string="Age(Days)")
    
    
    @api.multi
    def btn_open_inv(self):
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.invoice',
                'res_id':self.inv_id and self.inv_id.id or False,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }
    

