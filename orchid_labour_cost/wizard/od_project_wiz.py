# -*- coding: utf-8 -*-
from pprint import pprint
from openerp import models, fields, api
class od_project_wiz(models.TransientModel):
    _name = 'od.project.wiz'
    
    project_ids = fields.Many2many('account.analytic.account','rel_analytic_labourcost_wiz', 'wiz_id', 'analytic_id', string="Projects")
    excluded_project_ids = fields.Many2many('account.analytic.account','rel_analytic_labourcost_excluded_wiz', 'wiz_id', 'analytic_id', string="Excluded Projects")
    
    @api.one
    def generate_timesheet(self):
        labour = self.env['od.labour']
        context = self._context
        active_id = context.get('active_id',False)
        pprint(context)
        project_ids  = []
        excluded_project_ids = []
        for project_id in self.project_ids:
            project_ids.append(project_id.id)
        for excl_project_id in self.excluded_project_ids:
            excluded_project_ids.append(excl_project_id.id)
        labour_obj = labour.browse(active_id)
        labour_obj.get_timesheet(project_ids,excluded_project_ids)
