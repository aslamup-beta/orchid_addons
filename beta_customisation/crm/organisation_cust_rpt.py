# -*- coding: utf-8 -*-
from openerp import models, fields, api
from pprint import pprint
import openerp.addons.decimal_precision as dp
import datetime
from dateutil.relativedelta import relativedelta



class org_cust_rpt_wiz(models.TransientModel):
    _name = 'org.cust.rpt.wiz'
    
    wiz_line = fields.One2many('org.cust.rpt.data','wiz_id',string="Wiz Line")
    
    def od_get_company_id(self):
        return self.env.user.company_id
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    
    @api.multi 
    def export_rpt(self):
        fm_view = "od_org_cust_tree_view"
        wiz_id = self.id
        company_id = self.company_id and self.company_id.id 
        domain2= [('is_company','=',True),('customer','=',True),('supplier','=',False),('company_id','=',company_id)]
        result =[]
        analytic_pool = self.env['account.analytic.account']
        partner_pool = self.env['res.partner'].search(domain2)
        for partner in partner_pool:
            pipeline_sales = 0.0
            pipeline_profit = 0.0
            commit_sales = 0.0
            commit_profit = 0.0
            won_sales = 0.0
            won_profit = 0.0
            partner_id = partner.id
            domain = [('company_id','=',company_id),('status','=','active'),('state','!=','cancel'),('od_customer_id','=',partner_id)]
            cost_sheet_data = self.env['od.cost.sheet'].search(domain)
            for sheet in cost_sheet_data:
                state = sheet.state
                stage_id = sheet.op_stage_id and sheet.op_stage_id.id or False
                approved_date = sheet.approved_date and sheet.approved_date[:10] or False
                if stage_id in (12,5,4,14):
                    pipeline_sales += sheet.sum_total_sale
                    pipeline_profit += sheet.total_gp
#                 if state == 'commit' and stage_id !=6:
#                     commit_sales += sheet.sum_total_sale
#                     commit_profit += sheet.total_gp

                if approved_date:
                    today = datetime.date.today()
                    approved_date =datetime.datetime.strptime(approved_date,'%Y-%m-%d')
                    if approved_date.year==today.year and state in ('approved','done','modify','change','analytic_change','change_processed','redistribution_processed') and stage_id ==6:
                        won_sales += sheet.sum_total_sale
                        won_profit += sheet.total_gp
            result.append((0,0,{
                            'wiz_id':wiz_id,
                            'name':partner.id, 
                            'industry':partner.od_industry_id and partner.od_industry_id.id or False ,
                            'od_class':partner.od_class or None,
                            'sam_id':partner.user_id and partner.user_id.id or False,
                            'pipeline_sale':pipeline_sales,
                            'pipeline_profit':pipeline_profit,
                            'commit_sale':commit_sales,
                            'commit_profit':commit_profit,
                            'won_sale': won_sales,
                            'won_profit':won_profit,
                            'phone': partner.phone or None,
                            'od_territory': partner.od_territory_id and partner.od_territory_id.id or False,
                            'od_city':partner.city or None,
                            }))
                        
        self.wiz_line.unlink()
        self.write({'wiz_line':result})
        model_data = self.env['ir.model.data']
        tree_view = model_data.get_object_reference( 'beta_customisation', fm_view)
        return {
            'domain': [('wiz_id','=',wiz_id)],
            'name': 'Named Accounts',
            'view_type': 'form',
            'view_mode': 'tree',
            'context':{'search_default_class':1, 'search_default_sam':1},
            'views': [(tree_view and tree_view[1] or False, 'tree')],
            'res_model': 'org.cust.rpt.data',
            'type': 'ir.actions.act_window',
        }

                        
class org_cust_rpt_data(models.TransientModel):
    _name = 'org.cust.rpt.data'
    
    wiz_id = fields.Many2one('org.cust.rpt.wiz',string="Wizard")
    name = fields.Many2one('res.partner',string="Name")
    industry = fields.Many2one('od.partner.industry',string="Industry")
    od_class = fields.Char(string="Class")
    phone = fields.Char(string="Phone")
    sam_id = fields.Many2one('res.users',string="Sales Account Manager")
    od_territory = fields.Many2one('od.partner.territory',string="Territory")
    od_city = fields.Char(string="City")
    pipeline_sale = fields.Float(string="Pipeline-Sales",digits=dp.get_precision('Account'))
    pipeline_profit = fields.Float(string="Pipeline-Profit",digits=dp.get_precision('Account'))
    commit_sale = fields.Float(string="Commit-Sales",digits=dp.get_precision('Account'))
    commit_profit = fields.Float(string="Commit-Profit",digits=dp.get_precision('Account'))
    won_sale = fields.Float(string="Won-Sales",digits=dp.get_precision('Account'))
    won_profit = fields.Float(string="Won-Profit",digits=dp.get_precision('Account'))

    