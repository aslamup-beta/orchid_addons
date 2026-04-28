# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import Warning
from openerp import SUPERUSER_ID
from math import exp,log10
import openerp.addons.decimal_precision as dp
class ChangeProc(models.Model):
    _name = 'change.procurment'
    _description = 'Change Procurment'
    _inherit = ['mail.thread']
    _order = 'id desc'

        
    
    
    
 
    def sch_po(self,number):
        
        planned_amount = eval('self.'+'po_amount_'+str(number))
        plan_date = eval('self.'+'po_date_'+str(number))
        po_sup =  eval('self.'+'po_sup_'+str(number))
        po_sup = po_sup.id
        credit = eval('self.'+'po_cred_'+str(number))
       
        grand_analytic_id = self.level_0_id and self.level_0_id.id or False
        po_sch = self.env['od.proc.schedule']
        po_sch.create({
            'plan_date':plan_date,
            'credit_days':credit,
            'amount':planned_amount,
            'partner_id':po_sup,
            'grand_analytic_id':grand_analytic_id,
          
            })
    def plan_val_up_in_sheet(self,i):
       
        sheet = self.cost_sheet_id
        po_select =True
        po_select_val ='po_select_'+str(i)

       

        po_date=eval('self.po_date_'+str(i)) or False
        po_date_val='po_date_'+str(i)
        po_amount=eval('self.po_amount_'+str(i)) or 0.0
        po_amount_val='po_amount_'+str(i)
        po_vat=eval('self.po_vat_'+str(i)) or 0.0
        po_vat_val='po_vat_'+str(i)
        
        po_sup=eval('self.po_sup_'+str(i))
        po_sup = po_sup and po_sup.id or False
        po_sup_val='po_sup_'+str(i) 
        po_cred=eval('self.po_cred_'+str(i))
        po_cred_val='po_cred_'+str(i)
        sheet.write({po_select_val:po_select,po_date_val:po_date,po_amount_val:po_amount,po_vat_val:po_vat,po_cred_val:po_cred})



     
    def create_po_schedule(self):
        
        for num in range(1,13):
            if eval('self.'+'po_new_'+str(num)):
                self.sch_po(num)
                self.plan_val_up_in_sheet(num)
    
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
       
        self.state = 'submit'
        self.date = fields.Date.context_today(self)
        self.od_send_mail('proc_submit_mail')
    

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
        self.create_po_schedule()
        self.state = 'pmo'
        #self.od_send_mail('proc_first_approval_mail')
        


    @api.model
    def create(self,vals):
        ctx =self.env.context
        change = super(ChangeProc, self).create(vals)
        change.import_cost_sheet()
        return change
    
    def create_seq(self):
        sheet =self.cost_sheet_id
        sheet_id = sheet.id
        sheet_num = sheet.number
        costsheets = self.search([('cost_sheet_id','=',sheet_id)])
        cst_sheet_count = len(costsheets) 
        self.name = sheet_num +'-PROC-'+str(cst_sheet_count)
            
    
    def import_po_plan(self):
        sheet =self.cost_sheet_id
        for i in range(1,13):
            po_select=eval('sheet.po_select_'+str(i)) or False
            po_select_val='po_select_'+str(i) 

            po_date=eval('sheet.po_date_'+str(i)) or False
            po_date_val='po_date_'+str(i)
            po_amount=eval('sheet.po_amount_'+str(i)) or 0.0
            po_amount_val='po_amount_'+str(i)


            po_vat=eval('sheet.po_vat_'+str(i)) or 0.0
            po_vat_val='po_vat_'+str(i)
            

            po_sup=eval('sheet.po_sup_'+str(i))
            po_sup = po_sup and po_sup.id or False
            po_sup_val='po_sup_'+str(i) 


            po_cred=eval('sheet.po_cred_'+str(i))
            po_cred_val='po_cred_'+str(i)
            self.write({po_select_val:po_select,po_date_val:po_date,po_amount_val:po_amount,po_vat_val:po_vat,po_cred_val:po_cred})


    
    @api.one 
    def import_cost_sheet(self):
        self.create_seq()
        self.import_po_plan()
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
    
    name = fields.Char(string="Reference",track_visibility='always',default='/')
    state = fields.Selection(selection_list,string="Status",default='draft',track_visibility='always')
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id,readonly=True)
    pmo_user_id = fields.Many2one('res.users',string="First Approval Manager",track_visibility='always',default=get_pmo_user)
    branch_id = fields.Many2one('od.cost.branch',string="Branch",track_visibility='always')
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
    
    def get_purchase_vat(self):
        val = 0.0
        if self.po_tax_id_1:
            val = self.po_tax_id_1.amount
            return val
        else:
            return val

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

    po_new_1 = fields.Boolean(string="Add New 1")
    po_new_2 = fields.Boolean(string="Add New 2")
    po_new_3 = fields.Boolean(string="Add New 3")
    po_new_4 = fields.Boolean(string="Add New 4")
    po_new_5 = fields.Boolean(string="Add New 5")
    po_new_6 = fields.Boolean(string="Add New 6")
    po_new_7 = fields.Boolean(string="Add New 7")
    po_new_8 = fields.Boolean(string="Add New 8")
    po_new_9 = fields.Boolean(string="Add New 9")
    po_new_10 = fields.Boolean(string="Add New 10")
    po_new_11 = fields.Boolean(string="Add New 11")
    po_new_12 = fields.Boolean(string="Add New 12")


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

