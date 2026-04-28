# -*- coding: utf-8 -*-
from openerp import models,fields,api,_
from openerp.exceptions import Warning
class hr_contract(models.Model):
    _inherit ="hr.contract"
    @api.constrains('xo_working_hours')
    def od_check_working_hours(self):
        if not self.xo_working_hours:
            raise Warning("Working Hours Must Enter and Cannot Be Zero")
