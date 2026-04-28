# -*- coding: utf-8 -*-
from openerp.tools.translate import _
from openerp.tools import float_round, float_is_zero, float_compare
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from dateutil.relativedelta import relativedelta
from datetime import date, timedelta,datetime
import openerp.addons.decimal_precision as dp
from collections import defaultdict,Counter
from math import exp,log10
from pprint import pprint
from openerp.osv import expression
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
import logging
import time
_logger = logging.getLogger(__name__)



class od_an_inv_dist_plan_line(models.Model):
    _name ='od.analytic.inv.dist.plan.line'
    
    @api.one 
    def _compute_sale_amount(self):
        res =0.0
        sheet_id = self.sheet_id
        total_sale = sheet_id.sum_tot_sale
        special_discount = sheet_id.special_discount
        if sheet_id:
            if self.analytic_tag == 'a1':
                res = sheet_id.sales_a1
                if special_discount and total_sale:
                    disc=(res/total_sale) * abs(special_discount)
                    res = res -disc
                    
            if self.analytic_tag =='a2':
                res = sheet_id.sales_a2
                if special_discount and total_sale:
                    disc=(res/total_sale) * abs(special_discount)
                    res = res -disc
            if self.analytic_tag =='a3':
                res = sheet_id.sales_a3
                if special_discount and total_sale:
                    disc=(res/total_sale) * abs(special_discount)
                    res = res -disc
            
            if self.analytic_tag in ('child_amc1','child_amc2','child_amc3','child_amc4','child_amc5','child_amc6','child_amc7','child_amc8','child_amc9','child_amc10','child_amc11','child_amc12',):
                res = sheet_id.sales_a4/(sheet_id.no_of_l2_accounts_amc or 1.0)
                if special_discount and total_sale:
                    disc=(sheet_id.sales_a4/total_sale) * abs(special_discount)
                    disc = disc/(sheet_id.no_of_l2_accounts_amc or 1.0)
                    res = res -disc
            
            if self.analytic_tag in ('child_om1','child_om2','child_om3','child_om4','child_om5','child_om6','child_om7','child_om8','child_om9','child_om10','child_om11','child_om12',):
                res = sheet_id.sales_a5/(sheet_id.no_of_l2_accounts_om or 1.0)
                if special_discount and total_sale:
                    disc=(sheet_id.sales_a5/total_sale) * abs(special_discount)
                    disc = disc/(sheet_id.no_of_l2_accounts_om or 1.0)
                    res  =  res - disc
        
        self.sale_amount = res
            
                
    
    ####
    analytic_id = fields.Many2one('account.analytic.account',string="A0 Analytic Account")
    child_analytic_id = fields.Many2one('account.analytic.account',string="Analytic Account")
    sale_amount = fields.Float(string="Sale Amount",compute='_compute_sale_amount')
    sheet_id = fields.Many2one('od.cost.sheet',string="Sheet ID")
    ####
    analytic_tag = fields.Selection([('a1','A1'),('a2','A2'),('a3','A3'),('child_amc1','Child AMC-1'),('child_amc1','Child AMC-1'),
                                    ('child_amc2','Child AMC-2'),('child_amc3','Child AMC-3'),('child_amc4','Child AMC-4'),('child_amc5','Child AMC-5'),
                                    ('child_amc6','Child AMC-6'),('child_amc7','Child AMC-7'),('child_amc8','Child AMC-8'),('child_amc9','Child AMC-9'),
                                    ('child_amc10','Child AMC-10'),('child_amc11','Child AMC-11'),('child_amc12','Child AMC-12'),
                                    ('child_om1','Child OM-1'),('child_om2','Child OM-2'),('child_om3','Child OM-3'),('child_om4','Child OM-4'),
                                    ('child_om5','Child OM-5'),('child_om6','Child OM-6'),('child_om7','Child OM-7'),('child_om8','Child OM-8'),
                                    ('child_om9','Child OM-9'),('child_om10','Child OM-10'),('child_om11','Child OM-11'),('child_om12','Child OM-12'),
                                    ],string="Analytic Tag")
    inv1 = fields.Float(string="INV 1")
    inv2 = fields.Float(string="INV 2")
    inv3 = fields.Float(string="INV 3")
    inv4 = fields.Float(string="INV 4")
    inv5 = fields.Float(string="INV 5")
    inv6 = fields.Float(string="INV 6")
    inv7 = fields.Float(string="INV 7")
    inv8 = fields.Float(string="INV 8")
    inv9 = fields.Float(string="INV 9")
    ####
    inv10 = fields.Float(string="INV 10")
    inv11 = fields.Float(string="INV 11")
    inv12 = fields.Float(string="INV 12")
    locked = fields.Boolean(string="Locked")
    ####



class od_inv_analytic_rel_per(models.Model):
    _name='od.inv.analytic.rel.per'
    inv_seq=fields.Selection([('inv1','INV 1'),('inv2','INV 2'),('inv3','INV 3'),('inv4','INV 4'),('inv5','INV 5'),('inv6','INV 6'),
                              ('inv7','INV 7'),('inv8','INV 8'),('inv9','INV 9'),('inv10','INV 10'),('inv11','INV 11'),('inv12','INV 12')],string="Invoice Seq")
    

    sheet_id = fields.Many2one('od.cost.sheet',string="Sheet ID")
    analytic_id = fields.Many2one('account.analytic.account',string="A0 Analytic Account")
    child_analytic_id = fields.Many2one('account.analytic.account',string="Analytic Account")
    value = fields.Float("Percentage")
    analytic_tag= fields.Selection([('a1','A1'),('a2','A2'),('a3','A3'),('child_amc1','Child AMC-1'),('child_amc1','Child AMC-1'),
                                    ('child_amc2','Child AMC-2'),('child_amc3','Child AMC-3'),('child_amc4','Child AMC-4'),('child_amc5','Child AMC-5'),
                                    ('child_amc6','Child AMC-6'),('child_amc7','Child AMC-7'),('child_amc8','Child AMC-8'),('child_amc9','Child AMC-9'),
                                    ('child_amc10','Child AMC-10'),('child_amc11','Child AMC-11'),('child_amc12','Child AMC-12'),
                                    ('child_om1','Child OM-1'),('child_om2','Child OM-2'),('child_om3','Child OM-3'),('child_om4','Child OM-4'),
                                    ('child_om5','Child OM-5'),('child_om6','Child OM-6'),('child_om7','Child OM-7'),('child_om8','Child OM-8'),
                                    ('child_om9','Child OM-9'),('child_om10','Child OM-10'),('child_om11','Child OM-11'),('child_om12','Child OM-12'),
                                    ],string="Analytic Tag")    











   
    




class od_cost_sheet(models.Model):
    _inherit = 'od.cost.sheet'
    
    
#     def get_analytic_from_rel(self,num):
#         inv_seq ='inv'+str(num)
#         sheet_id = self.id
#         rel_line=self.env['od.inv.analytic.rel.per'].search([('sheet_id','=',sheet_id),('inv_seq','=',inv_seq)],limit=1,order='value desc')
#         return rel_line and rel_line.child_analytic_id and rel_line.child_analytic_id.id or False
    
    
    
    
    @api.multi
    def od_change_proc(self):
        
        cost_sheet = self.id
        analytic_id =self.analytic_a0 and self.analytic_a0.id or False
        branch_id = self.od_branch_id and self.od_branch_id.id or False
        return {
              'name': 'Change Procurment Plan',
              'view_type': 'form',
              "view_mode": 'tree,form',
              'res_model': 'change.procurment',
              'type': 'ir.actions.act_window',
              'domain':[('cost_sheet_id','=',cost_sheet)],
              'context': {'default_cost_sheet_id':cost_sheet,
                           'default_level_0_id':analytic_id,'default_branch_id':branch_id },
        }


    @api.multi
    def od_change_inv(self):
         
        cost_sheet = self.id
        analytic_id =self.analytic_a0 and self.analytic_a0.id or False
        branch_id = self.od_branch_id and self.od_branch_id.id or False
        return {
              'name': 'Change Inv Plan',
              'view_type': 'form',
              "view_mode": 'tree,form',
              'res_model': 'change.invplan',
              'type': 'ir.actions.act_window',
              'domain':[('cost_sheet_id','=',cost_sheet)],
              'context': {'default_cost_sheet_id':cost_sheet,
                           'default_level_0_id':analytic_id,'default_branch_id':branch_id },
        }
    


    @api.multi
    def od_change_redist(self):
         
        cost_sheet = self.id
        analytic_id =self.analytic_a0 and self.analytic_a0.id or False
        branch_id = self.od_branch_id and self.od_branch_id.id or False
        
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

    
    
    
    def sch_inv(self,number):
        if self.schedule_created:
            return True
        planned_amount = eval('self.'+'inv_amount_'+str(number))
#         analytic_id = self.get_analytic_from_rel(number)
        planned_date = eval('self.'+'planned_date_'+str(number))
        pmo_inv_date =  eval('self.'+'planned_date_'+str(number))
        credit_days = eval('self.'+'inv_cred_'+str(number))
        name = 'INV'+str(number)
        inv_seq = 'inv'+str(number)
        grand_analytic_id = self.analytic_a0 and self.analytic_a0.id or False
        inv_sch = self.env['od.project.invoice.schedule']
        inv_sch.create({
            'name':name,
            'date':planned_date,
            'pmo_date':pmo_inv_date,
            'inv_seq':inv_seq,
            'amount':planned_amount,
            'analytic_id':grand_analytic_id,
            'grand_analytic_id':grand_analytic_id,
            'credit_days':credit_days,
          
            })
    
    def sch_po(self,number):
        if self.po_schedule_created:
            return True
        planned_amount = eval('self.'+'po_amount_'+str(number))
        plan_date = eval('self.'+'po_date_'+str(number))
        po_sup =  eval('self.'+'po_sup_'+str(number))
        po_sup = po_sup.id
        credit = eval('self.'+'po_cred_'+str(number))
       
        grand_analytic_id = self.analytic_a0 and self.analytic_a0.id or False
        po_sch = self.env['od.proc.schedule']
        po_sch.create({
            'plan_date':plan_date,
            'credit_days':credit,
            'amount':planned_amount,
            'partner_id':po_sup,
            'grand_analytic_id':grand_analytic_id,
          
            })
    
    

    
    def check_inv_sheet_sum(self):
        total_sale = self.sum_total_sale 
        inv_amount_total = self.inv_amount_1 + self.inv_amount_2 + self.inv_amount_3 + self.inv_amount_4 + self.inv_amount_5 + self.inv_amount_6 + self.inv_amount_7 + self.inv_amount_8 + self.inv_amount_9 +  self.inv_amount_10 + self.inv_amount_11 + self.inv_amount_12
        diff = abs(total_sale- inv_amount_total)
        if diff>1:
            raise Warning("Total Sale And Invoice Planned Total Are Not Matching")
    
    def check_inv_vat_sum(self):
        total_vat = self.sum_vat 
        inv_vat_total = self.inv_vat_1 + self.inv_vat_2 + self.inv_vat_3 + self.inv_vat_4 + self.inv_vat_5 + self.inv_vat_6 + self.inv_vat_7 + self.inv_vat_8 + self.inv_vat_9 +  self.inv_vat_10 + self.inv_vat_11 + self.inv_vat_12
        diff = abs(total_vat- inv_vat_total)
        if diff>1:
            raise Warning("Total Vat amount And Invoice Vat Amount Are Not Matching")
    
    def check_plan_dist_condition(self):
        self.check_inv_sheet_sum()
        self.check_inv_vat_sum()
        if not self.inv_amount_1:
            raise Warning("Invoice Planning Needed")
        inv1=inv2=inv3=inv4=inv5=inv6=inv7=inv8=inv9=inv10=inv11=inv12=0.0
        res = []
        for line in self.od_plan_dist_line:
            sale_amount = line.sale_amount 
            inv_amount =line.inv1 + line.inv2 + line.inv3+ line.inv4 + line.inv5 +line.inv6 + line.inv7 + line.inv8+ line.inv9 + line.inv10 +line.inv11 +line.inv12 
            
            inv1 +=line.inv1
            inv2 +=line.inv2
            inv3 +=line.inv3
            inv4 +=line.inv4
            inv5 +=line.inv5
            inv6 +=line.inv6
            inv7 +=line.inv7
            inv8 +=line.inv8
            inv9 +=line.inv9
            inv10 +=line.inv10
            inv11 +=line.inv11
            inv12 +=line.inv12
            if self.inv_amount_1 and line.inv1:
                res.append({'inv_seq':'inv1','analytic_tag':line.analytic_tag,'value':(line.inv1/self.inv_amount_1)*100.0})
            if self.inv_amount_2 and line.inv2:
                res.append({'inv_seq':'inv2','analytic_tag':line.analytic_tag,'value':(line.inv2/self.inv_amount_2)*100.0})
            if self.inv_amount_3 and line.inv3:
                res.append({'inv_seq':'inv3','analytic_tag':line.analytic_tag,'value':(line.inv3/self.inv_amount_3)*100.0})
            if self.inv_amount_4 and line.inv4:
                res.append({'inv_seq':'inv4','analytic_tag':line.analytic_tag,'value':(line.inv4/self.inv_amount_4)*100.0})
            if self.inv_amount_5 and line.inv5:
                res.append({'inv_seq':'inv5','analytic_tag':line.analytic_tag,'value':(line.inv5/self.inv_amount_5)*100.0})
            if self.inv_amount_6 and line.inv6:
                res.append({'inv_seq':'inv6','analytic_tag':line.analytic_tag,'value':(line.inv6/self.inv_amount_6)*100.0})
            if self.inv_amount_7 and line.inv7:
                res.append({'inv_seq':'inv7','analytic_tag':line.analytic_tag,'value':(line.inv7/self.inv_amount_7)*100.0})
            if self.inv_amount_8 and line.inv8:
                res.append({'inv_seq':'inv8','analytic_tag':line.analytic_tag,'value':(line.inv8/self.inv_amount_8)*100.0})
            if self.inv_amount_9 and line.inv9:
                res.append({'inv_seq':'inv9','analytic_tag':line.analytic_tag,'value':(line.inv9/self.inv_amount_9)*100.0})
            if self.inv_amount_10 and line.inv10:
                res.append({'inv_seq':'inv10','analytic_tag':line.analytic_tag,'value':(line.inv10/self.inv_amount_10)*100.0})
            if self.inv_amount_11 and line.inv11:
                res.append({'inv_seq':'inv11','analytic_tag':line.analytic_tag,'value':(line.inv11/self.inv_amount_11)*100.0})
            if self.inv_amount_12 and line.inv12:
                res.append({'inv_seq':'inv12','analytic_tag':line.analytic_tag,'value':(line.inv12/self.inv_amount_12)*100.0})
            if abs(sale_amount - inv_amount) >0.1:
                raise Warning("Invoice Distribution : Sale Amount and Invoice Amount is Not Matching")
            line.write({'locked':True})
        if abs(self.inv_amount_1 -inv1) >0.1:
            raise Warning("Invoice Planning and Invoice Distribution Not Matching for Inv Seq 1")
        if abs(self.inv_amount_2 -inv2) >0.1:
            raise Warning("Invoice Planning and Invoice Distribution Not Matching for Inv Seq 2")
        if abs(self.inv_amount_3 -inv3) >0.1:
            raise Warning("Invoice Planning and Invoice Distribution Not Matching for Inv Seq 3")
        if abs(self.inv_amount_4 -inv4) >0.1:
            raise Warning("Invoice Planning and Invoice Distribution Not Matching for Inv Seq 4")
        if abs(self.inv_amount_5 -inv5) >0.1:
            raise Warning("Invoice Planning and Invoice Distribution Not Matching for Inv Seq 5")
        if abs(self.inv_amount_6 -inv6) >0.1:
            raise Warning("Invoice Planning and Invoice Distribution Not Matching for Inv Seq 6")
        if abs(self.inv_amount_7 -inv7) >0.1:
            raise Warning("Invoice Planning and Invoice Distribution Not Matching for Inv Seq 7")
        if abs(self.inv_amount_8 -inv8) >0.1:
            raise Warning("Invoice Planning and Invoice Distribution Not Matching for Inv Seq 8")
        if abs(self.inv_amount_9 -inv9) >0.1:
            raise Warning("Invoice Planning and Invoice Distribution Not Matching for Inv Seq 9")
        if abs(self.inv_amount_10 -inv10) >0.1:
            raise Warning("Invoice Planning and Invoice Distribution Not Matching for Inv Seq 10")
        if abs(self.inv_amount_11 -inv11) >0.1:
            raise Warning("Invoice Planning and Invoice Distribution Not Matching for Inv Seq 11")
        if abs(self.inv_amount_12 - inv12) >0.1:
            raise Warning("Invoice Planning and Invoice Distribution Not Matching for Inv Seq 12")
        return res
    
    
    
    
    def update_inv_relation(self):
        res=self.check_plan_dist_condition()
        self.od_an_inv_rel_line.unlink()
        self.od_an_inv_rel_line = res
        self.od_inv_plan_locked =True
    
    @api.one
    def populate_tech(self):
        res =[]
        pdt_group_ids =[1,2,3,21,23]
        for pdt_grp_id in pdt_group_ids:
            res.append({'pdt_grp_id':pdt_grp_id,'value':20})
        if not self.dist_tech_line:
            self.dist_tech_line = res
    
    @api.one
    def populate_re(self):
        res =[]
        pdt_group_ids =[1,2,3,21,23]
        for pdt_grp_id in pdt_group_ids:
            res.append({'pdt_grp_id':pdt_grp_id,'value':20})
        if not self.dist_re_line:
            self.dist_re_line = res
    
    def get_default_tech_pop(self):
        res =[]
        pdt_group_ids =[1,2,3,21,23]
        for pdt_grp_id in pdt_group_ids:
            res.append({'pdt_grp_id':pdt_grp_id,'value':20})
        return res
    def _check_full_tech(self):
        if self.redist_tech_manual:
            value =0.0
            for line in self.dist_tech_line:
                value +=line.value 
            if value != 100.0:
                raise Warning("Eqn Manual Distribution Should Be 100.0")
        if self.redist_re_manual:
            value =0.0
            for line in self.dist_re_line:
                value +=line.value 
            if value != 100.0:
                raise Warning("Eqn Manual Distribution Should Be 100.0")
    redist_tech_manual = fields.Boolean(string="Distribute Log Eqn Revenue Manually")
    redist_re_manual = fields.Boolean(string="Distribute Resident Engineer Revenue Manually")
    
    dist_tech_line = fields.One2many('od.dist.tech','costsheet_id',string='Distribution Product Group',default=get_default_tech_pop)
    dist_re_line = fields.One2many('od.dist.tech.re','costsheet_id',string='Distribution Product Group',default=get_default_tech_pop)
    
    od_plan_dist_line = fields.One2many('od.analytic.inv.dist.plan.line','sheet_id',string="Invoice Distribution Planning")
    od_an_inv_rel_line =fields.One2many('od.inv.analytic.rel.per','sheet_id',string="Invoice Analytic Relation")
    od_inv_plan_locked = fields.Boolean(string="Inv Plan Locked")
    schedule_created= fields.Boolean("Schedule Created")
    po_schedule_created = fields.Boolean("PO Schedule Created")
    ignore_inv_plan = fields.Boolean("Ignore Inv Plan")
    inv_schedule_change = fields.Boolean("Inv Plan Changed")
    
    
    
    inv_select_1 = fields.Boolean(string="Select 1")
    inv_select_2 = fields.Boolean(string="Select 2")
    inv_select_3 = fields.Boolean(string="Select 3")
    inv_select_4 = fields.Boolean(string="Select 4")
    inv_select_5 = fields.Boolean(string="Select 5")
    inv_select_6 = fields.Boolean(string="Select 6")
    inv_select_7 = fields.Boolean(string="Select 7")
    inv_select_8 = fields.Boolean(string="Select 8")
    inv_select_9 = fields.Boolean(string="Select 9")
    inv_select_10 = fields.Boolean(string="Select 10")
    inv_select_11 = fields.Boolean(string="Select 11")
    inv_select_12 = fields.Boolean(string="Select 12")
    
    def get_vat(self):
        val = 0.0
        if self.inv_tax_id_1:
            val = self.inv_tax_id_1.amount
            return val
        else:
            return val
        
    def get_purchase_vat(self):
        val = 0.0
        if self.po_tax_id_1:
            val = self.po_tax_id_1.amount
            return val
        else:
            return val
        
        

    @api.onchange('inv_amount_1','inv_tax_id_1')
    def onchange_inv_amount_1(self):
        val = self.get_vat()
        if self.inv_amount_1:
            vat = self.inv_amount_1 * val
            self.inv_vat_1 = vat
    @api.onchange('inv_amount_2','inv_tax_id_1')
    def onchange_inv_amount_2(self):
        val = self.get_vat()
        if self.inv_amount_2:
            vat = self.inv_amount_2 * val
            self.inv_vat_2 = vat

    @api.onchange('inv_amount_3','inv_tax_id_1')
    def onchange_inv_amount_3(self):
        val = self.get_vat()
        if self.inv_amount_3:
            vat = self.inv_amount_3 * val
            self.inv_vat_3 = vat
    

    @api.onchange('inv_amount_4','inv_tax_id_1')
    def onchange_inv_amount_4(self):
        val = self.get_vat()
        if self.inv_amount_4:
            vat = self.inv_amount_4 * val
            self.inv_vat_4 = vat
    
    @api.onchange('inv_amount_5','inv_tax_id_1')
    def onchange_inv_amount_5(self):
        val = self.get_vat()
        if self.inv_amount_5:
            vat = self.inv_amount_5 * val
            self.inv_vat_5 = vat
    
    @api.onchange('inv_amount_6','inv_tax_id_1')
    def onchange_inv_amount_6(self):
        val = self.get_vat()
        if self.inv_amount_6:
            vat = self.inv_amount_6 * val
            self.inv_vat_6 = vat
    
    @api.onchange('inv_amount_7','inv_tax_id_1')
    def onchange_inv_amount_7(self):
        val = self.get_vat()
        if self.inv_amount_7:
            vat = self.inv_amount_7 * val
            self.inv_vat_7 = vat


    @api.onchange('inv_amount_8','inv_tax_id_1')
    def onchange_inv_amount_8(self):
        val = self.get_vat()
        if self.inv_amount_8:
            vat = self.inv_amount_8 * val
            self.inv_vat_8 = vat



    @api.onchange('inv_amount_9','inv_tax_id_1')
    def onchange_inv_amount_9(self):
        val = self.get_vat()
        if self.inv_amount_9:
            vat = self.inv_amount_9 * val
            self.inv_vat_9 = vat
    
    @api.onchange('inv_amount_10','inv_tax_id_1')
    def onchange_inv_amount_10(self):
        val = self.get_vat()
        if self.inv_amount_10:
            vat = self.inv_amount_10 * val
            self.inv_vat_10 = vat
    
    @api.onchange('inv_amount_11','inv_tax_id_1')
    def onchange_inv_amount_11(self):
        val = self.get_vat()
        if self.inv_amount_11:
            vat = self.inv_amount_11 * val
            self.inv_vat_11 = vat
    
    @api.onchange('inv_amount_12','inv_tax_id_1')
    def onchange_inv_amount_12(self):
        val = self.get_vat()
        if self.inv_amount_12:
            vat = self.inv_amount_12 * val
            self.inv_vat_12 = vat
    
    
    

    @api.onchange('po_amount_1','po_tax_id_1')
    def onchange_po_amount_1(self):
        val = self.get_purchase_vat()
        if self.po_amount_1:
            vat = self.po_amount_1 * val
            self.po_vat_1 = vat


    @api.onchange('po_amount_2','po_tax_id_1')
    def onchange_po_amount_2(self):
        val = self.get_purchase_vat()
        if self.po_amount_2:
            vat = self.po_amount_2 * val
            self.po_vat_2 = vat


    @api.onchange('po_amount_3','po_tax_id_1')
    def onchange_po_amount_3(self):
        val = self.get_purchase_vat()
        if self.po_amount_3:
            vat = self.po_amount_3 * val
            self.po_vat_3 = vat


    @api.onchange('po_amount_4','po_tax_id_1')
    def onchange_po_amount_4(self):
        val = self.get_purchase_vat()
        if self.po_amount_4:
            vat = self.po_amount_4 * val
            self.po_vat_4 = vat


    @api.onchange('po_amount_5','po_tax_id_1')
    def onchange_po_amount_5(self):
        val = self.get_purchase_vat()
        if self.po_amount_5:
            vat = self.po_amount_5 * val
            self.po_vat_5 = vat


    @api.onchange('po_amount_6','po_tax_id_1')
    def onchange_po_amount_6(self):
        val = self.get_purchase_vat()
        if self.po_amount_6:
            vat = self.po_amount_6 * val
            self.po_vat_6 = vat


    @api.onchange('po_amount_7','po_tax_id_1')
    def onchange_po_amount_7(self):
        val = self.get_purchase_vat()
        if self.po_amount_7:
            vat = self.po_amount_7 * val
            self.po_vat_7 = vat


    @api.onchange('po_amount_8','po_tax_id_1')
    def onchange_po_amount_8(self):
        val = self.get_purchase_vat()
        if self.po_amount_8:
            vat = self.po_amount_8 * val
            self.po_vat_8 = vat


    @api.onchange('po_amount_9','po_tax_id_1')
    def onchange_po_amount_9(self):
        val = self.get_purchase_vat()
        if self.po_amount_9:
            vat = self.po_amount_9 * val
            self.po_vat_9 = vat


    @api.onchange('po_amount_10','po_tax_id_1')
    def onchange_po_amount_10(self):
        val = self.get_purchase_vat()
        if self.po_amount_10:
            vat = self.po_amount_10 * val
            self.po_vat_10 = vat


    @api.onchange('po_amount_11','po_tax_id_1')
    def onchange_po_amount_11(self):
        val = self.get_purchase_vat()
        if self.po_amount_11:
            vat = self.po_amount_11 * val
            self.po_vat_11 = vat


    @api.onchange('po_amount_12','po_tax_id_1')
    def onchange_po_amount_12(self):
        val = self.get_purchase_vat()
        if self.po_amount_12:
            vat = self.po_amount_12 * val
            self.po_vat_12 = vat




    
    inv_amount_1=fields.Float(string="Invoice Planned Amount 1")
    inv_amount_2=fields.Float(string="Invoice Planned Amount 2")
    inv_amount_3=fields.Float(string="Invoice Planned Amount 3")
    inv_amount_4=fields.Float(string="Invoice Planned Amount 4")
    inv_amount_5=fields.Float(string="Invoice Planned Amount 5")
    inv_amount_6=fields.Float(string="Invoice Planned Amount 6")
    inv_amount_7=fields.Float(string="Invoice Planned Amount 7")
    inv_amount_8=fields.Float(string="Invoice Planned Amount 8")
    inv_amount_9=fields.Float(string="Invoice Planned Amount 9")
    inv_amount_10=fields.Float(string="Invoice Planned Amount 10")
    inv_amount_11=fields.Float(string="Invoice Planned Amount 11")
    inv_amount_12=fields.Float(string="Invoice Planned Amount 12")
    
    planned_date_1= fields.Date(string="Planned Date 1")
    planned_date_2= fields.Date(string="Planned Date 2")
    planned_date_3= fields.Date(string="Planned Date 3")
    planned_date_4= fields.Date(string="Planned Date 4")
    planned_date_5= fields.Date(string="Planned Date 5")
    planned_date_6= fields.Date(string="Planned Date 6")
    planned_date_7= fields.Date(string="Planned Date 7")
    planned_date_8= fields.Date(string="Planned Date 8")
    planned_date_9= fields.Date(string="Planned Date 9")
    planned_date_10= fields.Date(string="Planned Date 10")
    planned_date_11= fields.Date(string="Planned Date 11")
    planned_date_12= fields.Date(string="Planned Date 12")
    
    pmo_inv_date_1 = fields.Date(string="PMO Expected Invoice Date 1")
    pmo_inv_date_2 = fields.Date(string="PMO Expected Invoice Date 2")
    pmo_inv_date_3 = fields.Date(string="PMO Expected Invoice Date 3")
    pmo_inv_date_4 = fields.Date(string="PMO Expected Invoice Date 4")
    pmo_inv_date_5 = fields.Date(string="PMO Expected Invoice Date 5")
    pmo_inv_date_6 = fields.Date(string="PMO Expected Invoice Date 6")
    pmo_inv_date_7 = fields.Date(string="PMO Expected Invoice Date 7")
    pmo_inv_date_8 = fields.Date(string="PMO Expected Invoice Date 8")
    pmo_inv_date_9 = fields.Date(string="PMO Expected Invoice Date 9")
    pmo_inv_date_10 = fields.Date(string="PMO Expected Invoice Date 10")
    pmo_inv_date_11 = fields.Date(string="PMO Expected Invoice Date 11")
    pmo_inv_date_12 = fields.Date(string="PMO Expected Invoice Date 12")
    
    inv_cred_1 = fields.Integer(string="Credit Days 1")
    inv_cred_2 = fields.Integer(string="Credit Days 2")
    inv_cred_3 = fields.Integer(string="Credit Days 3")
    inv_cred_4 = fields.Integer(string="Credit Days 4")
    inv_cred_5 = fields.Integer(string="Credit Days 5")
    inv_cred_6 = fields.Integer(string="Credit Days 6")
    inv_cred_7 = fields.Integer(string="Credit Days 7")
    inv_cred_8 = fields.Integer(string="Credit Days 8")
    inv_cred_9 = fields.Integer(string="Credit Days 9")
    inv_cred_10 = fields.Integer(string="Credit Days 10")
    inv_cred_11 = fields.Integer(string="Credit Days 11")
    inv_cred_12 = fields.Integer(string="Credit Days 12")
    
    
    inv_vat_1 = fields.Float(string="Vat 1")
    inv_vat_2 = fields.Float(string="Vat 2")
    inv_vat_3 = fields.Float(string="Vat 3")
    inv_vat_4 = fields.Float(string="Vat 4")
    inv_vat_5 = fields.Float(string="Vat 5")
    inv_vat_6 = fields.Float(string="Vat 6")
    inv_vat_7 = fields.Float(string="Vat 7")
    inv_vat_8 = fields.Float(string="Vat 8")
    inv_vat_9 = fields.Float(string="Vat 9")
    inv_vat_10 = fields.Float(string="Vat 10")
    inv_vat_11 = fields.Float(string="Vat 11")
    inv_vat_12 = fields.Float(string="Vat 12")
    
    inv_tax_id_1 = fields.Many2one('account.tax', string="Tax 1", domain=[('type_tax_use','=','sale')])
    
       
    po_select_1 = fields.Boolean(string="Select 1")
    po_select_2 = fields.Boolean(string="Select 2")
    po_select_3 = fields.Boolean(string="Select 3")
    po_select_4 = fields.Boolean(string="Select 4")
    po_select_5 = fields.Boolean(string="Select 5")
    po_select_6 = fields.Boolean(string="Select 6")
    po_select_7 = fields.Boolean(string="Select 7")
    po_select_8 = fields.Boolean(string="Select 8")
    po_select_9 = fields.Boolean(string="Select 9")
    po_select_10 = fields.Boolean(string="Select 10")
    po_select_11 = fields.Boolean(string="Select 11")
    po_select_12 = fields.Boolean(string="Select 12")


    po_amount_1=fields.Float(string="po Amount 1")
    po_amount_2=fields.Float(string="po Amount 2")
    po_amount_3=fields.Float(string="po Amount 3")
    po_amount_4=fields.Float(string="po Amount 4")
    po_amount_5=fields.Float(string="po Amount 5")
    po_amount_6=fields.Float(string="po Amount 6")
    po_amount_7=fields.Float(string="po Amount 7")
    po_amount_8=fields.Float(string="po Amount 8")
    po_amount_9=fields.Float(string="po Amount 9")
    po_amount_10=fields.Float(string="po Amount 10")
    po_amount_11=fields.Float(string="po Amount 11")
    po_amount_12=fields.Float(string="po Amount 12")

    po_date_1= fields.Date(string="PO Date 1")
    po_date_2= fields.Date(string="PO Date 2")
    po_date_3= fields.Date(string="PO Date 3")
    po_date_4= fields.Date(string="PO Date 4")
    po_date_5= fields.Date(string="PO Date 5")
    po_date_6= fields.Date(string="PO Date 6")
    po_date_7= fields.Date(string="PO Date 7")
    po_date_8= fields.Date(string="PO Date 8")
    po_date_9= fields.Date(string="PO Date 9")
    po_date_10= fields.Date(string="PO Date 10")
    po_date_11= fields.Date(string="PO Date 11")
    po_date_12= fields.Date(string="PO Date 12")


    po_cred_1 = fields.Integer(string="Credit Days 1")
    po_cred_2 = fields.Integer(string="Credit Days 2")
    po_cred_3 = fields.Integer(string="Credit Days 3")
    po_cred_4 = fields.Integer(string="Credit Days 4")
    po_cred_5 = fields.Integer(string="Credit Days 5")
    po_cred_6 = fields.Integer(string="Credit Days 6")
    po_cred_7 = fields.Integer(string="Credit Days 7")
    po_cred_8 = fields.Integer(string="Credit Days 8")
    po_cred_9 = fields.Integer(string="Credit Days 9")
    po_cred_10 = fields.Integer(string="Credit Days 10")
    po_cred_11 = fields.Integer(string="Credit Days 11")
    po_cred_12 = fields.Integer(string="Credit Days 12")
    
        
    po_vat_1 = fields.Float(string="Vat 1")
    po_vat_2 = fields.Float(string="Vat 2")
    po_vat_3 = fields.Float(string="Vat 3")
    po_vat_4 = fields.Float(string="Vat 4")
    po_vat_5 = fields.Float(string="Vat 5")
    po_vat_6 = fields.Float(string="Vat 6")
    po_vat_7 = fields.Float(string="Vat 7")
    po_vat_8 = fields.Float(string="Vat 8")
    po_vat_9 = fields.Float(string="Vat 9")
    po_vat_10 = fields.Float(string="Vat 10")
    po_vat_11 = fields.Float(string="Vat 11")
    po_vat_12 = fields.Float(string="Vat 12")
    
    po_tax_id_1 = fields.Many2one('account.tax', string="Tax 2", domain=[('type_tax_use','=','purchase')])
    

    po_sup_1 = fields.Many2one('res.partner',string="Supplier 1",domain=[('supplier','=',True),('is_company','=',True)])
    po_sup_2 = fields.Many2one('res.partner',string="Supplier 1",domain=[('supplier','=',True),('is_company','=',True)])    
    po_sup_3 = fields.Many2one('res.partner',string="Supplier 1",domain=[('supplier','=',True),('is_company','=',True)])
    po_sup_4 = fields.Many2one('res.partner',string="Supplier 1",domain=[('supplier','=',True),('is_company','=',True)])
    po_sup_5 = fields.Many2one('res.partner',string="Supplier 1",domain=[('supplier','=',True),('is_company','=',True)])
    po_sup_6 = fields.Many2one('res.partner',string="Supplier 1",domain=[('supplier','=',True),('is_company','=',True)])
    po_sup_7 = fields.Many2one('res.partner',string="Supplier 1",domain=[('supplier','=',True),('is_company','=',True)])
    po_sup_8 = fields.Many2one('res.partner',string="Supplier 1",domain=[('supplier','=',True),('is_company','=',True)])
    po_sup_9 = fields.Many2one('res.partner',string="Supplier 1",domain=[('supplier','=',True),('is_company','=',True)])
    po_sup_10 = fields.Many2one('res.partner',string="Supplier 1",domain=[('supplier','=',True),('is_company','=',True)])
    po_sup_11 = fields.Many2one('res.partner',string="Supplier 1",domain=[('supplier','=',True),('is_company','=',True)])
    po_sup_12 = fields.Many2one('res.partner',string="Supplier 1",domain=[('supplier','=',True),('is_company','=',True)])
    
class od_dist_tech(models.Model):
    _name = 'od.dist.tech'
    costsheet_id = fields.Many2one('od.cost.sheet',string="Costsheet",ondelete='cascade')
    pdt_grp_id = fields.Many2one('od.product.group',string="Product Group")
    value = fields.Float(string="Percentage")


class od_dist_tech_re(models.Model):
    _name = 'od.dist.tech.re'
    costsheet_id = fields.Many2one('od.cost.sheet',string="Cost Sheet",ondelete='cascade')
    pdt_grp_id = fields.Many2one('od.product.group',string="Product Group")
    value = fields.Float(string="Percentage")
        
    