# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import Warning
from openerp import SUPERUSER_ID
from math import exp,log10
import openerp.addons.decimal_precision as dp
class ChangeInvPLan(models.Model):
    _name = 'change.invplan'
    _description = 'Change INV Plan'
    _inherit = ['mail.thread']
    _order = 'id desc'

        
    
    
    
   
    def check_inv_sheet_sum(self):
        sheet = self.cost_sheet_id
        total_sale = sheet.sum_total_sale 
        inv_amount_total = self.inv_amount_1 + self.inv_amount_2 + self.inv_amount_3 + self.inv_amount_4 + self.inv_amount_5 + self.inv_amount_6 + self.inv_amount_7 + self.inv_amount_8 + self.inv_amount_9 +  self.inv_amount_10 + self.inv_amount_11 + self.inv_amount_12
        diff = abs(total_sale- inv_amount_total)
        if diff>1:
            raise Warning("Total Sale And Invoice Planned Total Are Not Matching")
   
     
    def check_inv_vat_sum(self):
        sheet = self.cost_sheet_id
        total_vat = sheet.sum_vat 
        inv_vat_total = self.inv_vat_1 + self.inv_vat_2 + self.inv_vat_3 + self.inv_vat_4 + self.inv_vat_5 + self.inv_vat_6 + self.inv_vat_7 + self.inv_vat_8 + self.inv_vat_9 +  self.inv_vat_10 + self.inv_vat_11 + self.inv_vat_12
        diff = abs(total_vat- inv_vat_total)
        if diff>1:
            raise Warning("Total Vat amount And Invoice Vat Amount Are Not Matching")
   
    def check_plan_dist_condition(self):
        self.check_inv_sheet_sum()
        self.check_inv_vat_sum()
        
        inv1=inv2=inv3=inv4=inv5=inv6=inv7=inv8=inv9=inv10=inv11=inv12=0.0
        res = []
        for line in self.cm_dist_line:
            
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
    
    
    def plan_val_up_in_sheet(self,i):
       
        sheet = self.cost_sheet_id
        po_select =eval('self.inv_select_'+str(i)) 
        po_select_val ='inv_select_'+str(i)

       

        po_date=eval('self.planned_date_'+str(i)) or False
        po_date_val='planned_date_'+str(i)
        po_amount=eval('self.inv_amount_'+str(i)) or 0.0
        po_amount_val='inv_amount_'+str(i)
        po_vat=eval('self.inv_vat_'+str(i)) or 0.0
        po_vat_val='inv_vat_'+str(i)
        
       
        po_cred=eval('self.inv_cred_'+str(i))
        po_cred_val='inv_cred_'+str(i)
        sheet.write({po_select_val:po_select,po_date_val:po_date,po_amount_val:po_amount,po_vat_val:po_vat,po_cred_val:po_cred})



    def up_sheet(self):
        for num in range(1,13):
            self.plan_val_up_in_sheet(num)
        res =[]
        for line in self.cm_dist_line:
            dat ={'analytic_tag':line.analytic_tag}
            for i in range(1,13):
                inv = 'inv'+ str(i)
                dat[inv] = eval('line.'+inv)
            res.append((0,0,dat))
        sheet = self.cost_sheet_id
        sheet.od_plan_dist_line.unlink()
        sheet.write({'od_plan_dist_line':res,'state':'change_processed'})
        sheet.update_inv_relation()
        


    

    
    def od_send_mail(self,template):
        ir_model_data = self.env['ir.model.data']
        email_obj = self.pool.get('email.template')
        if self.company_id.id == 6:
            template = template +'_saudi'
        template_id = ir_model_data.get_object_reference('beta_customisation', template)[1]
        cost_sheet_id = self.id
        email_obj.send_mail(self.env.cr,self.env.uid,template_id,cost_sheet_id, force_send=True)
        return True
    
    
    
   
    
    @api.one 
    def button_submit(self):
        cost_sheet_id = self.cost_sheet_id

        cost_sheet_state = self.cost_sheet_id.state
        if cost_sheet_state != 'done':
            raise Warning("Cost Sheet Not in Done State ,Pls Check the Costsheet")
        self.check_plan_dist_condition()
        self.state = 'submit'
        self.date = fields.Date.context_today(self)
        self.od_send_mail('inv_submit_mail')
    

    @api.one 
    def button_cancel(self):
        self.state = 'cancel'

    
    @api.one 
    def button_reject(self):
        self.state = 'reject'



    @api.one 
    def button_pmo_approval(self):
        cost_sheet_id = self.cost_sheet_id
        cost_sheet_state = self.cost_sheet_id.state
        if cost_sheet_state != 'done':
            raise Warning("Cost Sheet Not in Done State ,Pls Check the Costsheet")
        self.up_sheet()
        self.state = 'pmo'
        self.cost_sheet_id.inv_schedule_change = True
        #self.od_send_mail('inv_first_approval_mail')
        


    @api.model
    def create(self,vals):
        ctx =self.env.context
        change = super(ChangeInvPLan, self).create(vals)
        #change.import_cost_sheet()
        return change
    
    def create_seq(self):
        sheet =self.cost_sheet_id
        sheet_id = sheet.id
        sheet_num = sheet.number
        costsheets = self.search([('cost_sheet_id','=',sheet_id)])
        cst_sheet_count = len(costsheets) 
        self.name = sheet_num +'-INV-'+str(cst_sheet_count)
            
    
    def import_inv_plan(self):
        sheet =self.cost_sheet_id
        for i in range(1,13):
            po_select=eval('sheet.inv_select_'+str(i)) or False
            po_select_val='inv_select_'+str(i) 

            po_date=eval('sheet.planned_date_'+str(i)) or False
            po_date_val='planned_date_'+str(i)
            po_date_val_old='old_planned_date_'+str(i)
            po_amount=eval('sheet.inv_amount_'+str(i)) or 0.0
            po_amount_val='inv_amount_'+str(i)


            po_vat=eval('sheet.inv_vat_'+str(i)) or 0.0
            po_vat_val='inv_vat_'+str(i)
            

          


            po_cred=eval('sheet.inv_cred_'+str(i))
            po_cred_val='inv_cred_'+str(i)
            self.write({po_select_val:po_select, po_date_val:po_date, po_date_val_old:po_date, po_amount_val:po_amount, po_vat_val:po_vat, po_cred_val:po_cred})

    def import_inv_dist(self):
        sheet =self.cost_sheet_id
        res = []
        for line in sheet.od_plan_dist_line:
            dat ={'analytic_tag':line.analytic_tag, 'sale_amount': line.sale_amount}
            for i in range(1,13):
                inv = 'inv'+ str(i)
                dat[inv] = eval('line.'+inv)
            res.append((0,0,dat))
        self.write({'cm_dist_line':res})
    
    @api.one 
    def import_cost_sheet(self):
        self.create_seq()
        self.import_inv_plan()
        self.import_inv_dist()
        self.state = 'imported'
    
    def od_get_company_id(self):
        return self.env.user.company_id

      
    def get_current_user(self):
        return self._uid
    
    
    selection_list = [
            ('draft','Draft'),
            ('imported','Imported'),
            ('submit','Submitted'),
            ('pmo','PMO Approval'),
        
            ('cancel','Cancel'),
            ('reject','Rejected')
            ]
    
        
    def get_pmo_user(self):
        company_id =self.env.user.company_id
        pmo_user =19 
        if company_id.id ==6:
            pmo_user = 135  
        return pmo_user
    
    
        
    
    cm_dist_line = fields.One2many('od.cm.dist.line','cm_id',string="Dist Line")
    
    name = fields.Char(string="Reference",track_visibility='always',default='/')
    state = fields.Selection(selection_list,string="Status",default='draft',track_visibility='always')
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id,readonly=True)
    pmo_user_id = fields.Many2one('res.users',string="First Approval Manager",track_visibility='always',default=get_pmo_user)
    branch_id = fields.Many2one('od.cost.branch',string="Branch",track_visibility='always')
    partner_id = fields.Many2one('res.partner',string="Customer")
    date = fields.Date(string="Requested Date",default=fields.Date.context_today,track_visibility='always')
    user_id = fields.Many2one('res.users',string="Requested By",default=get_current_user)
    cost_sheet_id = fields.Many2one('od.cost.sheet',string="Cost Sheet",readonly=False)
    project_id = fields.Many2one('project.project',string="Project",readonly=False)
    level_0_id =fields.Many2one('account.analytic.account',string="Level 0",readonly=False)
    change_type = fields.Selection([('add','Add New PO')],default='add')
    reason = fields.Text(string="Reason for Change")
    
    @api.onchange('cost_sheet_id')
    def onchange_cost_sheet_id(self):
        if self.cost_sheet_id:
            level0_id = self.cost_sheet_id.analytic_a0 and self.cost_sheet_id.analytic_a0.id or False
            branch_id = self.cost_sheet_id.od_branch_id and self.cost_sheet_id.od_branch_id.id or False
            self.level_0_id = level0_id
            self.branch_id = branch_id
            partner_id = self.cost_sheet_id and self.cost_sheet_id.od_customer_id and self.cost_sheet_id.od_customer_id.id or False
            self.partner_id = partner_id
    
    def get_vat(self):
        val = 0.0
        if self.inv_tax_id_1:
            val = self.inv_tax_id_1.amount
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
    
    old_planned_date_1= fields.Date(string="Old Planned Date 1")
    old_planned_date_2= fields.Date(string="Old Planned Date 2")
    old_planned_date_3= fields.Date(string="Old Planned Date 3")
    old_planned_date_4= fields.Date(string="Old Planned Date 4")
    old_planned_date_5= fields.Date(string="Old Planned Date 5")
    old_planned_date_6= fields.Date(string="Old Planned Date 6")
    old_planned_date_7= fields.Date(string="Old Planned Date 7")
    old_planned_date_8= fields.Date(string="Old Planned Date 8")
    old_planned_date_9= fields.Date(string="Old Planned Date 9")
    old_planned_date_10= fields.Date(string="Old Planned Date 10")
    old_planned_date_11= fields.Date(string="Old Planned Date 11")
    old_planned_date_12= fields.Date(string="Old Planned Date 12")
    
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
    
    inv_tax_id_1 = fields.Many2one('account.tax', string="Tax 2", domain=[('type_tax_use','=','sale')])

    
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
    



class od_cm_dist_line(models.Model):
    _name ='od.cm.dist.line'

 
    cm_id = fields.Many2one('change.invplan',string="INV PLAN")
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
    sale_amount = fields.Float(string="Sale Amount")

    ####

