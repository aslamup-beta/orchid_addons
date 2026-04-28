# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import openerp.addons.decimal_precision as dp

class sale_order(osv.osv):
    _inherit = 'sale.order'

#     def assign_contract(self,cr, uid, ids,context=None):
#         so_ids = self.search(cr, uid,[('project_id','=',False)])
#         print "@@@@@@@@@",so_ids
# 
#         for so in self.browse(cr, uid, so_ids):
#             part = so.partner_id.id
#             if part:
#                 analytic = self.pool.get('account.analytic.account')
#                 analytic_id = analytic.search(cr, uid,[('partner_id','=',part)])
#                 if not analytic_id:
#                     part_obj = self.pool.get('res.partner').browse(cr,uid,part)
#                     part= part_obj.parent_id and part_obj.parent_id.id
#                     if part:
#                         analytic_id = analytic.search(cr, uid,[('partner_id','=',part)])
#                     if (not part_obj.affiliate_ids and not part_obj.parent_id and part_obj.is_company and part_obj.customer):
#                         analytic_id = [22] #analytic.search(cr, uid,[('type','=','normal'),('')])
#                         print "**"
#                 analytic_id = analytic_id and analytic_id[0] or ''
#             vals={'project_id':analytic_id}
#             self.write(cr, uid,[so.id],vals)
#             print "!!",so
#         return True
    def assign_contract(self,cr, uid, ids,context=None):
        so_ids = self.search(cr, uid,[('project_id','=',False)])

        for so in self.browse(cr, uid, so_ids):
            part = so.partner_id.id
            if part:
                analytic_default_obj=self.pool.get('account.analytic.default')
                analytic_default_id = analytic_default_obj.search(cr,uid,[('partner_id','=',part)])
                if analytic_default_id:
                    analytic_id =analytic_default_obj.browse(cr,uid,analytic_default_id[0]).analytic_id and analytic_default_obj.browse(cr,uid,analytic_default_id[0]).analytic_id.id
                    if analytic_id:
                        vals={'project_id':analytic_id}
                        self.write(cr, uid,[so.id],vals)
        return True
    def onchange_partner_id(self, cr, uid, ids, part, context=None):
        res = super(sale_order, self).onchange_partner_id(cr, uid, ids, part, context=context)
        if part:
            analytic_default_obj=self.pool.get('account.analytic.default')
            analytic_default_id = analytic_default_obj.search(cr,uid,[('partner_id','=',part)])
            if analytic_default_id:
                analytic_id =analytic_default_obj.browse(cr,uid,analytic_default_id[0]).analytic_id and analytic_default_obj.browse(cr,uid,analytic_default_id[0]).analytic_id.id
                if analytic_id:
                    res['value'].update({'project_id':analytic_id})
        return res
#     def _od_analytic_account(self, cr, uid, ids, field_name, arg, context=None): 
#         res ={} 
#         for obj in self.browse(cr, uid, ids, context): 
#             part = obj.partner_id.id
#             if part:
#                 analytic_default_obj=self.pool.get('account.analytic.default')
#                 analytic_default_id = analytic_default_obj.search(cr,uid,[('partner_id','=',part)])
#                 if analytic_default_id:
#                     analytic_id =analytic_default_obj.browse(cr,uid,analytic_default_id).analytic_id and analytic_default_obj.browse(cr,uid,analytic_default_id).analytic_id.id
#                     if analytic_id:
#                         res[obj.id] = analytic_id
#         return res

#     _columns = { 
#         'project_id': fields.function(_od_analytic_account, type='many2one', relation='account.analytic.account', string='Contract / Analytic',store=True),
#     }

