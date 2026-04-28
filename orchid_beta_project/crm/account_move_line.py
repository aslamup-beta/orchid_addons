# -*- coding: utf-8 -*-
from openerp import models,fields,api,_
from openerp.exceptions import Warning
from __builtin__ import False

class account_move_line(models.Model):
    _inherit = "account.move.line"
    od_opp_id = fields.Many2one('crm.lead',string="Opportunity")
    
    @api.onchange('od_opp_id') # if these fields are changed, call method
    def onchange_od_opp_id(self):
        account_id = self.account_id.id
        if account_id in (6567,2135,6632):
            opp_status_id = self.od_opp_id.stage_id.id
            if opp_status_id in (6,7,8):
                raise Warning("Opportunity you have selected is won/lost/cancelled. You cannot post this on a pre-operation account, use a different account instead")