# -*- coding: utf-8 -*-
import time
from openerp import models, fields, api

from pprint import pprint
from datetime import datetime
import openerp.addons.decimal_precision as dp

class asset_addition_rpt(models.TransientModel):
    _name = 'asset.add.rpt.wiz'
    
    date_start = fields.Date(string="Date Start")
    date_end =fields.Date(string="Date End")
    categ_ids = fields.Many2many('account.asset.category',string="Asset Category")
    wiz_line = fields.One2many('asset.add.rpt.data.line','org_wiz_id',string="Wiz Line")
    
    def od_get_company_id(self):
        return self.env.user.company_id
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    
    def _get_assets(self):
        asset_obj = self.env['account.asset.asset']
        date_start = self.date_start
        date_end = self.date_end
        company_id = self.company_id and self.company_id.id
        categ_ids = [pr.id for pr in self.categ_ids]
        domain =[]
        if company_id:
            domain += [('company_id','=',company_id)]
        if date_start:
            domain += [('od_purchase_date','>=',date_start)]
        if date_end:
            domain += [('od_purchase_date','<=',date_end)]
        if categ_ids:
            domain += [('category_id','in',categ_ids)]
        assets = asset_obj.search(domain)
        return assets

    def get_detailed_data(self):
        result  = []
        assets = self._get_assets()
        for asset in assets:
            result.append((0,0,{
                'code':asset.code,
                'name':asset.name,
                'categ_id':asset.category_id and asset.category_id.id or False,
                'purc_date':asset.od_purchase_date,
                'method_number':asset.method_number,
                'partner_id':asset.partner_id and asset.partner_id.id or False,
                'od_cost': asset.od_cost,
                'residual_val':asset.value_residual,
                'state': asset.state
                }))
        return result

    @api.multi
    def print_directly(self):
        data = self.get_detailed_data()
        rpt_temp = 'report.od_asset_add_rpt'
        rpt_pool = self.env['asset.add.rpt.data']
        vals = {
            'name': "Asset Addition Report",
            'line_ids':data,
            'date_start':self.date_start,
            'date_end':self.date_end,
            }
        rpt =rpt_pool.create(vals)
        rpt_id =rpt.id
        ctx = self.env.context
        cr = self.env.cr
        uid = self.env.uid
        return self.pool['report'].get_action(cr, uid, [rpt_id], rpt_temp , context=ctx)
    
#     @api.multi
#     def export_rpt(self):
#         model_data = self.env['ir.model.data']
#         if self.detail:
#             result = self.get_detailed_data()
#             vw = 'tree_view_pre_oprn_analysis_rpt2'
#         tree_view = model_data.get_object_reference( 'beta_customisation', vw)
#         self.wiz_line.unlink()
#         self.write({'wiz_line':result})
#         del(result)
#         return {
#             'domain': [('org_wiz_id','=',self.id)],
#             'name': 'Pre-Oprn Analysis Report',
#             'view_type': 'form',
#             'view_mode': 'tree',
#             'views': [(tree_view and tree_view[1] or False, 'tree')],
#             'res_model': 'pre.oprn.rpt.data.line',
#             'type': 'ir.actions.act_window',
#         }


class asset_add_report_data(models.TransientModel):
    _name = 'asset.add.rpt.data'
    
    def od_get_currency(self):
        return self.env.uid.company_id.currency_id
    def od_get_company_id(self):
        return self.env.user.company_id
    
    def _get_today_date(self):
        return datetime.today().strftime('%d-%b-%y')
    
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    name = fields.Char()
    line_ids = fields.One2many('asset.add.rpt.data.line','wiz_id',string="Wiz Line",readonly=True)
    currency_id = fields.Many2one('res.currency',string='Currency') 
    date = fields.Date(default=_get_today_date)
    date_start = fields.Date(string="Date Start")
    date_end =fields.Date(string="Date End")
    
class asset_add_report_data_line(models.TransientModel):
    _name = 'asset.add.rpt.data.line'
    _order = 'purc_date'
    
    def od_get_company_id(self):
        return self.env.user.company_id
    
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    wiz_id = fields.Many2one('asset.add.rpt.data',string="Wizard data")
    org_wiz_id = fields.Many2one('asset.add.rpt.wiz',string="Wizard")
    code = fields.Char(string="Reference")
    name = fields.Char(string="Asset Name")
    categ_id = fields.Many2one('account.asset.category', string='Asset Category')
    purc_date = fields.Date(string='Purchase Date')
    method_number = fields.Integer(string="No of Depr")
    partner_id = fields.Many2one('res.partner', string="Partner")
    od_cost = fields.Float(string="Gross Value", digits=(16,2))
    residual_val = fields.Float(string="Residual Value", digits=(16,2))
    state = fields.Selection([('draft','Draft'),('open','Running'),('close','Close')], "State")
    
    
