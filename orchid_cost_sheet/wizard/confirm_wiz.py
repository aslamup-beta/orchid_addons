# -*- coding: utf-8 -*-
from openerp import models, fields, api
class confirm_wiz(models.TransientModel):
    _name = 'confirm.wiz'
    
    reason = fields.Text(string="Reason")
    @api.one
    def btn_yes(self):
        context = self._context
        action = context.get('action')
        active_id = context.get('active_id')
        cost_sheet = self.env['od.cost.sheet']
        cost_sheet_obj = cost_sheet.browse(active_id)
        if action == 'btn_reset_submit':
            cost_sheet_obj.write({'return_reason': self.reason})
            cost_sheet_obj.btn_reset_submit()
        elif action == 'btn_reset_handover':
            cost_sheet_obj.write({'return_reason': self.reason})
            cost_sheet_obj.btn_reset_handover()
        elif action == 'btn_reset_change':
            cost_sheet_obj.write({'return_reason': self.reason})
            cost_sheet_obj.btn_reset_change()
        # cost_sheet_obj.od_send_mail('cst_sheet_owner_assigned')
        return True
