# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
class hr_expense_expense(models.Model):
    _inherit = "hr.expense.expense"
    @api.one
    @api.depends('date')
    def od_get_year(self):
        if self.date:
            date = self.date
            date = datetime.strptime(date, DEFAULT_SERVER_DATE_FORMAT)
            year = date.year
            self.od_year = year
    od_year = fields.Integer(string="Year",compute="od_get_year")
