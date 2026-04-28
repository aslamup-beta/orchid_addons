# -*- coding: utf-8 -*-
from openerp import models,fields,api
class wiz_assign_user(models.TransientModel):
    _name = "wiz.assign.user"
    _description = 'Assign User for Sending Email'
    # user_id = fields.Many2one('res.users',string="User",required=True,readonlT)

    @api.one
    def assign_user(self):
        context = self._context
        task_id = context.get('task_id')
        task = self.env['project.task']
        task_obj = task.browse(task_id)
        if task_obj.od_type == 'activities':
            task_obj.od_send_mail('od_task_assign_user_mail')
        return {
                    'res_id': task_id,
                    'view_type': 'form',
                    "view_mode": 'form',
                    'res_model': 'project.task',
                    'type': 'ir.actions.act_window',

        }
