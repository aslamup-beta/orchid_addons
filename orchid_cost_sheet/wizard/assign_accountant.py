# -*- coding: utf-8 -*-
from openerp import models, fields, api

class wiz_assign_accountant(models.TransientModel):

    _name = 'wiz.assign.accountant'
    accountant_id = fields.Many2one('res.users',string='Accountant',required=True)

    @api.one
    def assign_accountant(self):
        context = self._context
        active_id = context.get('active_id')
        accountant_id = self.accountant_id and self.accountant_id.id or False
        cost_sheet = self.env['od.cost.sheet']
        cost_sheet_obj = cost_sheet.browse(active_id)
        cost_sheet_obj.write({'accountant':accountant_id})
        cost_sheet_obj.od_send_mail('cst_sheet_accountant_assigned')
        return True
