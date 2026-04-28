# -*- coding: utf-8 -*-
from openerp import models, fields, api
class confirm_wiz(models.TransientModel):
    _name = 'task.confirm.wiz'
    @api.one
    def btn_yes(self):
        context = self._context
        action = context.get('action')
        active_id = context.get('active_id')
        task = self.env['project.task']
        task_obj = task.browse(active_id)
        task_obj.unlink()
        return True
