# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import Warning
from openerp import SUPERUSER_ID



class project_project(models.Model):
    _inherit ='project.project'

    @api.multi
    def od_change_proc(self):
        project_id = self.id
        cost_sheet = self.od_cost_sheet_id and self.od_cost_sheet_id.id or False
        analytic_id =self.od_cost_sheet_id and self.od_cost_sheet_id.analytic_a0 and self.od_cost_sheet_id.analytic_a0.id or False
        branch_id = self.od_cost_sheet_id and self.od_cost_sheet_id.od_branch_id and self.od_cost_sheet_id.od_branch_id.id or False
        return {
              'name': 'Change Procurment Plan',
              'view_type': 'form',
              "view_mode": 'tree,form',
              'res_model': 'change.procurment',
              'type': 'ir.actions.act_window',
              'domain':[('project_id','=',project_id)],
              'context': {'default_cost_sheet_id':cost_sheet,'default_project_id':project_id,
                           'default_level_0_id':analytic_id,'default_branch_id':branch_id },
        }


    @api.multi
    def od_change_inv(self):
        project_id = self.id
        cost_sheet = self.od_cost_sheet_id and self.od_cost_sheet_id.id or False
        analytic_id =self.od_cost_sheet_id and self.od_cost_sheet_id.analytic_a0 and self.od_cost_sheet_id.analytic_a0.id or False
        branch_id = self.od_cost_sheet_id and self.od_cost_sheet_id.od_branch_id and self.od_cost_sheet_id.od_branch_id.id or False
        return {
              'name': 'Change Inv Plan',
              'view_type': 'form',
              "view_mode": 'tree,form',
              'res_model': 'change.invplan',
              'type': 'ir.actions.act_window',
              'domain':[('project_id','=',project_id)],
              'context': {'default_cost_sheet_id':cost_sheet,'default_project_id':project_id,
                           'default_level_0_id':analytic_id,'default_branch_id':branch_id },
        }
    


    @api.multi
    def od_change_redist(self):
        
        cost_sheet = self.od_cost_sheet_id and self.od_cost_sheet_id.id or False
        
        branch_id = self.od_cost_sheet_id and self.od_cost_sheet_id.od_branch_id and self.od_cost_sheet_id.od_branch_id.id or False
        return {
              'name': 'Change Revenue Structure',
              'view_type': 'form',
              "view_mode": 'tree,form',
              'res_model': 'change.management',
              'type': 'ir.actions.act_window',
              'domain':[('cost_sheet_id','=',cost_sheet)],
              'context': {'default_cost_sheet_id':cost_sheet,'default_change_method':'redist',
                        'default_branch_id':branch_id },
        }

              


