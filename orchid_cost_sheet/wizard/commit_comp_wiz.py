# -*- coding: utf-8 -*-
from openerp import models, fields, api
from pprint import pprint
from datetime import datetime
import openerp.addons.decimal_precision as dp

class opp_comp_wiz(models.TransientModel):
    _name = 'opp.comp.wiz'
    stage_id = fields.Many2one('crm.case.stage',string="Opp Stage",default=5)
    wiz_line = fields.One2many('wiz.comp.data','wiz_id',string="Wiz Line")
    def od_get_company_id(self):
        return self.env.user.company_id
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    @api.multi 
    def export_rpt(self):
        wiz_id = self.id
        company_id = self.company_id and self.company_id.id
        stage_id = self.stage_id and self.stage_id.id 
        domain = [('stage_id','=',stage_id)]
        if company_id:
            domain += [('company_id','=',company_id)]
        
        opp_ids = self.env['crm.lead'].search(domain) 
        result =[]
        for opp in opp_ids:
            opp_id = opp.id
            stage_id = opp.stage_id and opp.stage_id.id 
           
            partner_id = opp.partner_id and opp.partner_id.id
            company_id = opp.company_id and opp.company_id.id 
            branch_id = opp.od_branch_id and opp.od_branch_id.id
            sheet = self.env['od.cost.sheet'].search([('status','=','active'),('lead_id','=',opp_id)],limit=1)
            sheet_id = sheet.id
            result.append((0,0,{
                                'wiz_id':wiz_id,
                                'cost_sheet_id':sheet_id, 
                                'opp_id':opp_id ,
                                'partner_id':partner_id,
                                'company_id':company_id,
                                'branch_id':branch_id,
                                'stage_id':stage_id,
                                'total_sale':sheet.sum_tot_sale,
                                'disc':abs(sheet.special_discount),
                                'sale_aftr_disc':sheet.sum_total_sale,
                                'total_cost':sheet.sum_tot_cost,
                                'total_gp':sheet.sum_profit + sheet.a_total_manpower_cost,
                                'total_sale_opp':opp.od_costsheet_sale,
                                'total_cost_opp':opp.od_costsheet_cost,
                                'total_gp_opp':opp.od_costsheet_new_profit,
                                
                                }))
                    
        
        self.write({'wiz_line':result})
        return {
            'domain': [('wiz_id','=',wiz_id)],
            'name': 'Commit Compare',
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'wiz.comp.data',
            'type': 'ir.actions.act_window',
        }
                        
        
        
        

class wiz_comp_rpt(models.TransientModel):
    _name = 'wiz.comp.data'
    wiz_id = fields.Many2one('opp.comp.wiz',string="Wizard")
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet')
    partner_id = fields.Many2one('res.partner',string="Customer")
    company_id = fields.Many2one('res.company',string="Company")
    branch_id = fields.Many2one('od.cost.branch',string="Branch")
    opp_id = fields.Many2one('crm.lead',string='Opportunity')
    stage_id = fields.Many2one('crm.case.stage',string="Opp Stage")
    
    
    total_sale = fields.Float(string="Sales/Costsheet",digits=dp.get_precision('Account'))
    sale_aftr_disc = fields.Float(string="Sales After Disc/Costsheet",digits=dp.get_precision('Account'))
    disc = fields.Float(string="Special Discount/Costsheet",digits=dp.get_precision('Account'))
    total_cost = fields.Float(string="Cost/Costsheet",digits=dp.get_precision('Account'))
    total_gp = fields.Float(string="Total GP/Costsheet",digits=dp.get_precision('Account'))
    
    total_sale_opp = fields.Float(string="Sales/Opportunity",digits=dp.get_precision('Account'))
    total_cost_opp = fields.Float(string="Cost/Opportunity",digits=dp.get_precision('Account'))
    total_gp_opp = fields.Float(string="Total GP/Opportunity",digits=dp.get_precision('Account'))
    
    
    
    @api.multi
    def btn_open_opp(self):
       
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'crm.lead',
                'res_id':self.opp_id and self.opp_id.id or False,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }
    @api.multi
    def btn_open_cost(self):
       
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'od.cost.sheet',
                'res_id':self.cost_sheet_id and self.cost_sheet_id.id or False,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }