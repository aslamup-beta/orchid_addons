# -*- coding: utf-8 -*-
from openerp import models, fields, api
from pprint import pprint
from datetime import datetime
class project_inv_wiz(models.TransientModel):
    _name = 'project.inv.wiz'
    od_inv_sch_line = fields.Many2many('od.project.invoice.schedule','rel_inv_proj_wiz','wiz_id','inv_id')
    
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        items = []
        analytic_pool = self.pool.get('account.analytic.account')
        res = super(project_inv_wiz, self).default_get(cr, uid, fields, context=context)
        root_id = context.get('root_id',False)
        root_lev = analytic_pool.browse(cr,uid,root_id)
        for line in root_lev.prj_inv_sch_line:
            items.append(line.id)
        
        res['od_inv_sch_line'] = [[6,False,items]]
        return res

