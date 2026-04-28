# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning
class hr_analytic_timesheet(models.Model):
    _inherit ="hr.analytic.timesheet"
    
    @api.one 
    @api.depends('overtime_type','hourly_rate','unit_amount')
    def od_get_amount(self):
        hourly_rate = self.hourly_rate
        duration =  self.unit_amount
        total = hourly_rate * duration
        self.normal_amount = total
        overtime_type = self.overtime_type
        overtime_amount = 0.0
        if overtime_type:
            if overtime_type.amount_select == 'percentage':
                amount_percentage =  overtime_type.amount_percentage
                overtime_amount  = total * (amount_percentage/100)
                self.overtime_amount = overtime_amount
            elif overtime_type.amount_select == 'fix':
                fix_amount = overtime_type.amount_fix
                overtime_amount = fix_amount * duration
                self.overtime_amount = overtime_amount
        amount = total + overtime_amount
#         self.amount = amount
    
    
    @api.onchange('hourly_rate','overtime_type')
    def onchange_hourly_rate(self):
        overtime_amount = self.overtime_amount
        normal_amount = self.normal_amount
        amount =normal_amount + overtime_amount
        self.amount = amount
      
        
    
    od_unit_cost = fields.Float(string="Nominal Value",related="product_id.standard_price")
    hourly_rate = fields.Float(string="Hourly Rate")
    overtime_type = fields.Many2one('hr.salary.rule',string="Overtime Type")
    overtime_percentage = fields.Float(string="Overtime Percentage",related='overtime_type.amount_percentage',store=True)
    overtime_amount = fields.Float(string="Overtime Amount",compute="od_get_amount",store=True)
    normal_amount = fields.Float(string="Normal Amount",compute="od_get_amount",store=True)
    
    narration  = fields.Char(string="Narration")
    cancelled_by_owner = fields.Boolean(string="Cancelled By Owner")
    cancelled_by_id  = fields.Many2one('res.users',string="Cancelled By")
    
    
    @api.model
    def create(self,vals):
        account_id = vals.get('account_id',False)
        if account_id:
            analytic_pool = self.env['account.analytic.account']
            analytic_obj = analytic_pool.browse(account_id)
            state = analytic_obj.state
            if state in ('cancelled','close'):
                raise Warning("This Analytic Account/Project Either Closed or Cancelled,You Cant Create Timesheet Further")
        return super(hr_analytic_timesheet,self).create(vals)
