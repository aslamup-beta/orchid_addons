# -*- coding: utf-8 -*-
from openerp import models, fields, api
class pmo_wiz(models.TransientModel):
    _name = 'pmo.wiz'
    @api.one
    def btn_yes(self):
        context = self._context
        action = context.get('action')
        active_id = context.get('active_id')
        cost_sheet = self.env['od.cost.sheet']
        cost_sheet_obj = cost_sheet.browse(active_id)
        cost_sheet_obj.action_pmo_director()
        return True