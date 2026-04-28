# -*- coding: utf-8 -*-
from openerp import models, fields, api
from pprint import pprint
from datetime import datetime
class project_proc_wiz(models.TransientModel):
    _name = 'project.proc.wiz'
    od_proc_sch_line = fields.Many2many('od.proc.schedule','rel_proc_sch_proj_wiz','wiz_id','proc_id')
    
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        items = []
        analytic_pool = self.pool.get('account.analytic.account')
        res = super(project_proc_wiz, self).default_get(cr, uid, fields, context=context)
        root_id = context.get('root_id',False)
        root_lev = analytic_pool.browse(cr,uid,root_id)
        for line in root_lev.od_proc_schedule_line:
            items.append(line.id)
        
        res['od_proc_sch_line'] = [[6,False,items]]
        return res

