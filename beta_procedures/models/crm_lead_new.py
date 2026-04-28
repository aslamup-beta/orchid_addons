# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import Warning
import datetime
from dateutil.relativedelta import relativedelta

class crm_lead(models.Model):
    _inherit = "crm.lead"
    
    expiry_date = fields.Date(string="Expiry Date")
    
    @api.onchange('create_date')
    def onchange_create_date(self):
        today = datetime.date.today()
        today_date = datetime.datetime.strptime(str(today), "%Y-%m-%d").date()
        expiry_date = today_date + relativedelta(days=14)
        self.expiry_date = expiry_date