# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning
class hr_analytic_timesheet(models.Model):
    _inherit ="hr.contract"
    
    @api.one 
    @api.depends('xo_total_wage','xo_working_hours')
    def _get_hourly_rate(self):
        total_wage = self.xo_total_wage
        working_hour = self.xo_working_hours
        if working_hour:
            hour_rate = total_wage/(working_hour * 30)
            self.xo_hourly_rate = hour_rate
            self.od_hourly_rate = hour_rate
    
    od_hourly_rate = fields.Float(string="Timesheet Hourly Rate",compute="_get_hourly_rate")
    
    
    