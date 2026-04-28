# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning
class account_move(models.Model):
    _inherit = "account.move"

    def button_cancel(self, cr, uid, ids, context=None):
        data = self.browse(cr,uid,ids)
        period = data.period_id
        period_state = period and period.state
        if period_state == 'done':
            raise Warning("You Cannot Cancel This Journal Entry ,Because Period or Financial Year Closed")
        return super(account_move,self).button_cancel(cr, uid, ids, context=None)
