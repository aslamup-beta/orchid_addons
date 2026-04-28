# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from lxml import etree
from pprint import pprint
from openerp.exceptions import Warning
class sale_order(models.Model):
    _inherit = 'sale.order'
   
#    
#     def get_manager_id(self):
#         hr = self.env['hr.employee']
#         user_id = self.env.uid
#         users_list =hr.search([('user_id','=',user_id)])
#         if users_list and users_list[0]:
#             manager_id=users_list[0].parent_id and  users_list[0].parent_id.user_id and users_list[0].parent_id.user_id.id or False
#             return manager_id
#         return False
      
           
    
    
    
    @api.multi
    def btn_change_req(self):
        change_pool = self.env['change.management']
        sale_id = self.id
        change_ids = [ ch.id for ch in change_pool.search([('so_id','=',sale_id)])]
        ctx = {}
        ctx['default_so_id'] = self.id
        ctx['default_cost_sheet_id'] = self.od_cost_sheet_id and self.od_cost_sheet_id.id or False
        ctx['default_project_id'] = self.project_id and self.project_id.id or False
#         ctx['default_manager_id']= self.get_manager_id()
        
        value = {
            'domain': [('id','in',change_ids)],
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'change.management',
            'context':ctx,
            'type': 'ir.actions.act_window'
             }
        return value