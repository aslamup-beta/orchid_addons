# -*- coding: utf-8 -*-
from openerp import models, fields, api

class wiz_assign_owner(models.TransientModel):

    _name = 'wiz.assign.owner'
    reviewer_id = fields.Many2one('res.users',string='Reviewer',required=True)

    @api.one
    def assign_owner(self):
        context = self._context
        active_id = context.get('active_id')
        reviewer_id = self.reviewer_id and self.reviewer_id.id or False
        cost_sheet = self.env['od.cost.sheet']
        cost_sheet_obj = cost_sheet.browse(active_id)
        #branch.write({'named_account_ids': [(4, line.account_id.id)]})
        cost_sheet_obj.write({'reviewed_id':reviewer_id})
        cost_sheet_obj.od_send_mail('cst_sheet_owner_assigned')
        return True
