# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from pprint import pprint
from datetime import datetime,timedelta,date as dt
from od_default_milestone import od_project_vals,od_om_vals,od_amc_vals
from openerp.exceptions import Warning
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
import openerp.addons.decimal_precision as dp
# from openerp.tools.safe_eval import safe_eval as eval



class purchase_order(models.Model):
    _inherit = 'purchase.order'
    od_confirm_date = fields.Date("Confirm Date")


    @api.multi    
    def write_confirm_date(self):
        date_td = fields.Date.today()
        self.write({'od_confirm_date':date_td})




class account_invoice(models.Model):
    _inherit = 'account.invoice'
    inv_seq = fields.Selection([('inv1','INV 1'),('inv2','INV 2'),('inv3','INV 3'),('inv4','INV 4'),('inv5','INV 5'),('inv6','INV 6'),
                              ('inv7','INV 7'),('inv8','INV 8'),('inv9','INV 9'),('inv10','INV 10'),('inv11','INV 11'),('inv12','INV 12')],string="Invoice Seq")
    
    grand_analytic_id =  fields.Many2one('account.analytic.account',string="Level 0 Analytic Account")
    
    dist_line = fields.One2many('od.dist.line','invoice_id',string="Dist Line")
    
    @api.one 
    def update_share(self):
        self.dist_line.unlink()
        inv_seq = self.inv_seq 
        grand_analytic_id = self.grand_analytic_id and self.grand_analytic_id.id or False
        data =self.env['od.inv.analytic.rel.per'].search([('inv_seq','=',inv_seq),('analytic_id','=',grand_analytic_id)])
        res = []
        for dat in data:
            analytic_id = dat.child_analytic_id and dat.child_analytic_id.id or False
            inv_seq = dat.inv_seq
            value = dat.value
            res.append({
                'inv_seq':inv_seq,
                'value':value,
                'analytic_id':analytic_id,
                })
        self.dist_line = res

class od_dist_line(models.Model):
    _name ='od.dist.line'
    invoice_id = fields.Many2one('account.invoice',string="Invoice")
    analytic_id = fields.Many2one('account.analytic.account',string="Analytic")
    share = fields.Float(string="Share")
    value = fields.Float(string="Value")
    inv_seq = fields.Selection([('inv1','INV 1'),('inv2','INV 2'),('inv3','INV 3'),('inv4','INV 4'),
                                ('inv5','INV 5'),('inv6','INV 6'),
                              ('inv7','INV 7'),('inv8','INV 8'),('inv9','INV 9'),
                              ('inv10','INV 10'),('inv11','INV 11'),('inv12','INV 12')],string="Invoice Seq")
    



class od_project_invoice_schedule(models.Model):
    _inherit = "od.project.invoice.schedule"
   
    grand_analytic_id =  fields.Many2one('account.analytic.account',string="Analytic Account")
    inv_seq = fields.Selection([('inv1','INV 1'),('inv2','INV 2'),('inv3','INV 3'),('inv4','INV 4'),('inv5','INV 5'),('inv6','INV 6'),
                              ('inv7','INV 7'),('inv8','INV 8'),('inv9','INV 9'),('inv10','INV 10'),('inv11','INV 11'),('inv12','INV 12')],string="Invoice Seq")
    
    credit_days = fields.Integer(string="Credit Days")
    
    
    @api.one 
    def _compute_paid_amount(self):
        payed_amount =0.0
        share_dict={}
        payment_share =000
        for line in self.invoice_id.payment_ids:
            payed_amount += line.credit
             
        for line in self.invoice_id.dist_line:
            share_dict[line.analytic_id.id] = line.value
        if share_dict:
            analytic_id = self.analytic_id.id 
            if share_dict.get(analytic_id,False):
                share_value = share_dict.get(analytic_id,False)
                payment_share = (share_value/100.0) *payed_amount
        else:
            if self.invoice_status =='paid':
                payment_share = payed_amount 
        self.paid_amount = payment_share
    
    paid_amount = fields.Float(string="Paid Amount",compute="_compute_paid_amount")

class od_proc_schedule(models.Model):
    _name = "od.proc.schedule"

    STATE_SELECTION = [
        ('draft', 'Draft PO'),
        ('sent', 'RFQ'),
        ('bid', 'Bid Received'),
        ('submit', 'Submitted'),('first_approval','First Approval'),('second_approval','Second Approval'),
        ('confirmed', 'Waiting Approval'),
        ('approved', 'Purchase Confirmed'),
        ('except_picking', 'Shipping Exception'),
        ('except_invoice', 'Invoice Exception'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ]

    grand_analytic_id =  fields.Many2one('account.analytic.account',string="Analytic Account")

    plan_date = fields.Date(string="Plan Date")
    amount = fields.Float(string="Planned Amount")
    partner_id = fields.Many2one('res.partner',string="Recommended Supplier")
    credit_days = fields.Integer(string="Credit Days")
    purchase_id = fields.Many2one('purchase.order',string="Purchase Order")
    confirm_date = fields.Date(string="Confirm Date",related='purchase_id.od_confirm_date')
    state = fields.Selection(STATE_SELECTION,related='purchase_id.state')
    supplier_id = fields.Many2one('res.partner',string="Supplier",related="purchase_id.partner_id")
    @api.multi
    def create_po(self):
        name="Generate Purchase Order"
        act_id="action_generate_purchase_order"
        src_model="sale.order"
        res_model="orchid_so2po.generate_purchase_order"
        view_mode="form" 
        target="new" 
        view_type="form"
        view_id=[2370]
        
        grand_analytic_id = self.grand_analytic_id and self.grand_analytic_id.id or False
        sale_id =self.env['sale.order'].search([('project_id','=',grand_analytic_id)],limit=1)
        sale_id = sale_id and sale_id.id
        partner_id = self.partner_id and self.partner_id.id or False
        planned_date = self.plan_date

        context ={'analytic':True,'sale_id':sale_id,'partner_id':partner_id,'date':planned_date,'proc_line_id':self.id}
        if self.purchase_id:
            return True
        return {
          
            'name': name,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': res_model,
            'view_id': view_id,
            'context':context,
            'target':"new",
            'type': 'ir.actions.act_window'
             }



    



class account_analytic_account(models.Model):
    _inherit = "account.analytic.account"
#     od_an_inv_plan_line = fields.One2many('od.analytic.inv.plan.line','analytic_id',string="Invoice Planning")
    
    od_proc_schedule_line = fields.One2many('od.proc.schedule','grand_analytic_id',string="Procurment Schedule")
    od_sale_line = fields.One2many('sale.order.line','od_analytic_acc_id',string="BOQ")
    
    
    @api.multi 
    def btn_wip_process(self):
        return {
            
            'name': _('WIP Process'),
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'od.wip',
            'context': {'default_project_id':self.id},
            'type': 'ir.actions.act_window'
             }

        
    
    
    @api.one 
    def _compute_sale_order_amount(self):
        project_id = self.id 
        sale =self.env['sale.order'].search([('project_id','=',project_id)],limit=1)
        amount = sale and sale.amount_total or 0.0
        self.r_sale_amount = amount
    
    @api.one 
    def _compute_invoice_prog(self):
        inv_amount =0.0
        r_invoice_progress = 0.0
        
        if self.od_analytic_level == 'level0':
        
            sale_amount = self.r_sale_amount or 1.0
            for line in self.prj_inv_sch_line:
                invoice_state = line.invoice_status
                if invoice_state in ('accept','paid'):
                    inv_amount += line.invoice_amount
           
            
            r_invoice_progress = (inv_amount /sale_amount)*100.0 
            if r_invoice_progress >100:
                r_invoice_progress =0.0
        
        else:
            sale_amount = self.od_amended_sale_price or 1.0
            for line in self.od_project_invoice_schedule_line:
                invoice_state = line.invoice_status
                if invoice_state in ('accept','paid'):
                    inv_amount += line.invoice_amount
           
            
            r_invoice_progress = (inv_amount /sale_amount)*100.0 
            if r_invoice_progress >100:
                r_invoice_progress =100.0
                if sale_amount <1:
                    r_invoice_progress =0.0
                 
            
        
        self.r_invoice_progress = r_invoice_progress
    
    
    @api.one 
    def _compute_closing_prog(self):
        closed_amount =0.0
#         sale_amount = self.r_sale_amount or 1.0
        total_sale_amount =0.0
        for line in self.od_child_data + self.od_grandchild_data:
            state = line.state
            total_sale_amount += line.od_amended_sale_price
            if state =='close':
                closed_amount += line.od_amended_sale_price 
        
        sale_amount = total_sale_amount or 1.0   
        prog = (closed_amount/sale_amount) *100.0
        if prog >100:
            prog =100
        self.r_closing_progress = prog
        
        
    
    
    
    
    
    @api.one 
    def _compute_budget_consume(self):
        amended_cost =0.0
        jv_cost =0.0
        if self.od_analytic_level == 'level0':
            for line in self.od_child_data + self.od_grandchild_data:
                amended_cost += line.od_amended_sale_cost
                jv_cost +=line.od_actual_cost
        else:
            amended_cost += self.od_amended_sale_cost
            jv_cost +=self.od_actual_cost
            
        
        res = jv_cost/(amended_cost or 1.0)
        res = res *100.0 
#         if res >100:
#             res=100.0
        self.r_budget_consumption =res
    
    @api.one             
    def compute_warn_string(self):
        if self.r_budget_consumption > 100.00 :
            self.warn_string ="Warning: Budget Overconsumption Detected. The actual cost has exceeded the allocated budget."     
    
    r_sale_amount = fields.Float(string="Sale Order Amount",compute="_compute_sale_order_amount")
    r_invoice_progress = fields.Float(string="Invoice Progress",compute='_compute_invoice_prog')
    r_closing_progress = fields.Float(string="Closing Progress",compute="_compute_closing_prog")
    r_budget_consumption = fields.Float(string="Budget Consumption",compute='_compute_budget_consume')
    od_an_inv_plan_dist_line =fields.One2many('od.analytic.inv.dist.plan.line','analytic_id',string="Invoice Distribution Planning")
    od_an_inv_rel_line =fields.One2many('od.inv.analytic.rel.per','analytic_id',string="Invoice Analytic Relation")
    od_inv_plan_locked = fields.Boolean(string="Locked")
    prj_inv_sch_line = fields.One2many('od.project.invoice.schedule','analytic_id',string="Project Invoice Schedule Line")
    schedule_created= fields.Boolean("Schedule Created")
    warn_string = fields.Char(string="Warning",compute="compute_warn_string")
    
    analytic_tag = fields.Selection([('a1','A1'),('a2','A2'),('a3','A3'),('a4','A4'),('a5','A5'),('child_amc1','Child AMC-1'),('child_amc1','Child AMC-1'),
                                    ('child_amc2','Child AMC-2'),('child_amc3','Child AMC-3'),('child_amc4','Child AMC-4'),('child_amc5','Child AMC-5'),
                                    ('child_amc6','Child AMC-6'),('child_amc7','Child AMC-7'),('child_amc8','Child AMC-8'),('child_amc9','Child AMC-9'),
                                    ('child_amc10','Child AMC-10'),('child_amc11','Child AMC-11'),('child_amc12','Child AMC-12'),
                                    ('child_om1','Child OM-1'),('child_om2','Child OM-2'),('child_om3','Child OM-3'),('child_om4','Child OM-4'),
                                    ('child_om5','Child OM-5'),('child_om6','Child OM-6'),('child_om7','Child OM-7'),('child_om8','Child OM-8'),
                                    ('child_om9','Child OM-9'),('child_om10','Child OM-10'),('child_om11','Child OM-11'),('child_om12','Child OM-12'),
                                    ],string="Analytic Tag") 
    
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

    
    
    inv_id_1 = fields.Many2one('account.invoice',string="Invoice 1")
    inv_id_2 = fields.Many2one('account.invoice',string="Invoice 2")
    inv_id_3 = fields.Many2one('account.invoice',string="Invoice 3")
    inv_id_4 = fields.Many2one('account.invoice',string="Invoice 4")
    inv_id_5 = fields.Many2one('account.invoice',string="Invoice 5")
    inv_id_6 = fields.Many2one('account.invoice',string="Invoice 6")
    inv_id_7 = fields.Many2one('account.invoice',string="Invoice 7")
    inv_id_8 = fields.Many2one('account.invoice',string="Invoice 8")
    inv_id_9 = fields.Many2one('account.invoice',string="Invoice 9")
    inv_id_10 = fields.Many2one('account.invoice',string="Invoice 10")
    inv_id_11 = fields.Many2one('account.invoice',string="Invoice 11")
    inv_id_12 = fields.Many2one('account.invoice',string="Invoice 12")
    
    
    analytic_id_1 = fields.Many2one('account.analytic.account',string="Analytic 1")
    analytic_id_2 = fields.Many2one('account.analytic.account',string="Analytic 2")
    analytic_id_3 = fields.Many2one('account.analytic.account',string="Analytic 3")
    analytic_id_4 = fields.Many2one('account.analytic.account',string="Analytic 4")
    analytic_id_5 = fields.Many2one('account.analytic.account',string="Analytic 5")
    analytic_id_6 = fields.Many2one('account.analytic.account',string="Analytic 6")
    analytic_id_7 = fields.Many2one('account.analytic.account',string="Analytic 7")
    analytic_id_8 = fields.Many2one('account.analytic.account',string="Analytic 8")
    analytic_id_9 = fields.Many2one('account.analytic.account',string="Analytic 9")
    analytic_id_10 = fields.Many2one('account.analytic.account',string="Analytic 10")
    analytic_id_11 = fields.Many2one('account.analytic.account',string="Analytic 11")
    analytic_id_12 = fields.Many2one('account.analytic.account',string="Analytic 12")
    
    sch_1 = fields.Boolean(string="Schedule 1")
    sch_2 = fields.Boolean(string="Schedule 2")
    sch_3 = fields.Boolean(string="Schedule 3")
    sch_4 = fields.Boolean(string="Schedule 4")
    sch_5 = fields.Boolean(string="Schedule 5")
    sch_6 = fields.Boolean(string="Schedule 6")
    sch_7 = fields.Boolean(string="Schedule 7")
    sch_8 = fields.Boolean(string="Schedule 8")
    sch_9 = fields.Boolean(string="Schedule 9")
    sch_10 = fields.Boolean(string="Schedule 10")
    sch_11 = fields.Boolean(string="Schedule 11")
    sch_12 = fields.Boolean(string="Schedule 12")
    
    
    @api.one 
    def btn_inv_plan(self):
        self.get_inv_plan()
    
    def get_inv_plan(self):
        
        sheet_id = self.od_cost_sheet_id
     
        inv_select_1 = sheet_id.inv_select_1
        inv_select_2 = sheet_id.inv_select_2
        inv_select_3 = sheet_id.inv_select_3
        inv_select_4 = sheet_id.inv_select_4
        inv_select_5 = sheet_id.inv_select_5
        inv_select_6 = sheet_id.inv_select_6
        inv_select_7 = sheet_id.inv_select_7
        inv_select_8 = sheet_id.inv_select_8
        inv_select_9 = sheet_id.inv_select_9
        inv_select_10 = sheet_id.inv_select_10
        inv_select_11 = sheet_id.inv_select_11
        inv_select_12 = sheet_id.inv_select_12
        
        inv_amount_1=sheet_id.inv_amount_1
        inv_amount_2=sheet_id.inv_amount_2
        inv_amount_3=sheet_id.inv_amount_3
        inv_amount_4=sheet_id.inv_amount_4
        inv_amount_5=sheet_id.inv_amount_5
        inv_amount_6=sheet_id.inv_amount_6
        inv_amount_7=sheet_id.inv_amount_7
        inv_amount_8=sheet_id.inv_amount_8
        inv_amount_9=sheet_id.inv_amount_9
        inv_amount_10=sheet_id.inv_amount_10
        inv_amount_11=sheet_id.inv_amount_11
        inv_amount_12=sheet_id.inv_amount_12
        
        planned_date_1= sheet_id.planned_date_1
        planned_date_2= sheet_id.planned_date_2
        planned_date_3= sheet_id.planned_date_3
        planned_date_4= sheet_id.planned_date_4
        planned_date_5= sheet_id.planned_date_5
        planned_date_6= sheet_id.planned_date_6
        planned_date_7= sheet_id.planned_date_7
        planned_date_8= sheet_id.planned_date_8
        planned_date_9= sheet_id.planned_date_9
        planned_date_10= sheet_id.planned_date_10
        planned_date_11= sheet_id.planned_date_11
        planned_date_12= sheet_id.planned_date_12
        
        pmo_inv_date_1 = sheet_id.pmo_inv_date_1
        pmo_inv_date_2 = sheet_id.pmo_inv_date_2
        pmo_inv_date_3 = sheet_id.pmo_inv_date_3
        pmo_inv_date_4 = sheet_id.pmo_inv_date_4
        pmo_inv_date_5 = sheet_id.pmo_inv_date_5
        pmo_inv_date_6 = sheet_id.pmo_inv_date_6
        pmo_inv_date_7 = sheet_id.pmo_inv_date_7
        pmo_inv_date_8 = sheet_id.pmo_inv_date_8
        pmo_inv_date_9 = sheet_id.pmo_inv_date_9
        pmo_inv_date_10 = sheet_id.pmo_inv_date_10
        pmo_inv_date_11 = sheet_id.pmo_inv_date_11
        pmo_inv_date_12 = sheet_id.pmo_inv_date_12
        
        
         
        self.inv_select_1 = inv_select_1
        self.inv_select_2 = inv_select_2
        self.inv_select_3 = inv_select_3
        self.inv_select_4 = inv_select_4
        self.inv_select_5 = inv_select_5
        self.inv_select_6 = inv_select_6
        self.inv_select_7 = inv_select_7
        self.inv_select_8 = inv_select_8
        self.inv_select_9 = inv_select_9
        self.inv_select_10 =inv_select_10
        self.inv_select_11 = inv_select_11
        self.inv_select_12 = inv_select_12
        
        self.inv_amount_1=inv_amount_1
        self.inv_amount_2=inv_amount_2
        self.inv_amount_3=inv_amount_3
        self.inv_amount_4=inv_amount_4
        self.inv_amount_5=inv_amount_5
        self.inv_amount_6=inv_amount_6
        self.inv_amount_7=inv_amount_7
        self.inv_amount_8=inv_amount_8
        self.inv_amount_9=inv_amount_9
        self.inv_amount_10=inv_amount_10
        self.inv_amount_11=inv_amount_11
        self.inv_amount_12=inv_amount_12
        
        self.planned_date_1= planned_date_1
        self.planned_date_2= planned_date_2
        self.planned_date_3= planned_date_3
        self.planned_date_4= planned_date_4
        self.planned_date_5= planned_date_5
        self.planned_date_6= planned_date_6
        self.planned_date_7= planned_date_7
        self.planned_date_8= planned_date_8
        self.planned_date_9= planned_date_9
        self.planned_date_10= planned_date_10
        self.planned_date_11= planned_date_11
        self.planned_date_12= planned_date_12
        
        self.pmo_inv_date_1 = pmo_inv_date_1
        self.pmo_inv_date_2 = pmo_inv_date_2
        self.pmo_inv_date_3 = pmo_inv_date_3
        self.pmo_inv_date_4 = pmo_inv_date_4
        self.pmo_inv_date_5 = pmo_inv_date_5
        self.pmo_inv_date_6 = pmo_inv_date_6
        self.pmo_inv_date_7 = pmo_inv_date_7
        self.pmo_inv_date_8 = pmo_inv_date_8
        self.pmo_inv_date_9 = pmo_inv_date_9
        self.pmo_inv_date_10 = pmo_inv_date_10
        self.pmo_inv_date_11 = pmo_inv_date_11
        self.pmo_inv_date_12 = pmo_inv_date_12
            
    
    
    def sch_inv(self,number):
        if self.schedule_created:
            raise Warning("Already schedule Created")
        planned_amount = eval('self.'+'inv_amount_'+str(number))
        analytic = eval('self.'+'analytic_id_'+str(number))
        analytic_id = analytic.id
        planned_date = eval('self.'+'planned_date_'+str(number))
        pmo_inv_date =  eval('self.'+'pmo_inv_date_'+str(number))
        name = 'INV'+str(number)
        inv_seq = 'inv'+str(number)
        grand_analytic_id = self.id
        inv_sch = self.env['od.project.invoice.schedule']
        inv_sch.create({
            'name':name,
            'date':planned_date,
            'pmo_date':pmo_inv_date,
            'inv_seq':inv_seq,
            'amount':planned_amount,
            'analytic_id':analytic_id,
            'grand_analytic_id':grand_analytic_id,
            })
        sch ='sch_'+str(number)
        self.write({sch:True})
        
    
    
    @api.one
    def sch_inv_1(self):
        self.sch_inv(1)
    
    
    @api.one
    def sch_inv_2(self):
        self.sch_inv(2)
    
    @api.one
    def sch_inv_3(self):
        self.sch_inv(3)
        
            
    @api.one
    def sch_inv_4(self):
        self.sch_inv(4)
            
    @api.one
    def sch_inv_5(self):
        self.sch_inv(5)
            
    @api.one
    def sch_inv_6(self):
        self.sch_inv(6)
            
    @api.one
    def sch_inv_7(self):
        self.sch_inv(7)
            
    @api.one
    def sch_inv_8(self):
        self.sch_inv(8)
            
    @api.one
    def sch_inv_9(self):
        self.sch_inv(9)
            
    @api.one
    def sch_inv_10(self):
        self.sch_inv(10)
            
    @api.one
    def sch_inv_11(self):
        self.sch_inv(11)
            
    @api.one
    def sch_inv_12(self):
        self.sch_inv(12)
        
    
    
    
    
    @api.one 
    def create_schedules(self):
        if not self.od_inv_plan_locked:
            raise Warning("Kindly Update Relation First")
        for i in range(1,13):
            if eval('self.'+'inv_select_'+str(i)):
                eval('self.'+'sch_inv'+'('+str(i)+')')
        
        self.schedule_created =True
    
    
    
    
    @api.one 
    def get_all_child(self):
        analytic_id = self.id
        child_ids = self.search([('parent_id','=',analytic_id)])
        grand_child_ids = self.search([('grand_parent_id','=',analytic_id)])
        res =[]
        for an in child_ids+grand_child_ids:
            res.append({'child_analytic_id':an.id,'sale_amount':an.od_amended_sale_price})
        
        if not self.od_an_inv_plan_dist_line:
            self.od_an_inv_plan_dist_line = res
            
    def check_condition(self):
        inv1=inv2=inv3=inv4=inv5=inv6=inv7=inv8=inv9=inv10=inv11=inv12=0.0
        res = []
        for line in self.od_an_inv_plan_dist_line:
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
                res.append({'inv_seq':'inv1','child_analytic_id':line.child_analytic_id.id,'value':(line.inv1/self.inv_amount_1)*100.0})
            if self.inv_amount_2 and line.inv2:
                res.append({'inv_seq':'inv2','child_analytic_id':line.child_analytic_id.id,'value':(line.inv2/self.inv_amount_2)*100.0})
            if self.inv_amount_3 and line.inv3:
                res.append({'inv_seq':'inv3','child_analytic_id':line.child_analytic_id.id,'value':(line.inv3/self.inv_amount_3)*100.0})
            if self.inv_amount_4 and line.inv4:
                res.append({'inv_seq':'inv4','child_analytic_id':line.child_analytic_id.id,'value':(line.inv4/self.inv_amount_4)*100.0})
            if self.inv_amount_5 and line.inv5:
                res.append({'inv_seq':'inv5','child_analytic_id':line.child_analytic_id.id,'value':(line.inv5/self.inv_amount_5)*100.0})
            if self.inv_amount_6 and line.inv6:
                res.append({'inv_seq':'inv6','child_analytic_id':line.child_analytic_id.id,'value':(line.inv6/self.inv_amount_6)*100.0})
            if self.inv_amount_7 and line.inv7:
                res.append({'inv_seq':'inv7','child_analytic_id':line.child_analytic_id.id,'value':(line.inv7/self.inv_amount_7)*100.0})
            if self.inv_amount_8 and line.inv8:
                res.append({'inv_seq':'inv8','child_analytic_id':line.child_analytic_id.id,'value':(line.inv8/self.inv_amount_8)*100.0})
            if self.inv_amount_9 and line.inv9:
                res.append({'inv_seq':'inv9','child_analytic_id':line.child_analytic_id.id,'value':(line.inv9/self.inv_amount_9)*100.0})
            if self.inv_amount_10 and line.inv10:
                res.append({'inv_seq':'inv10','child_analytic_id':line.child_analytic_id.id,'value':(line.inv10/self.inv_amount_10)*100.0})
            if self.inv_amount_11 and line.inv11:
                res.append({'inv_seq':'inv11','child_analytic_id':line.child_analytic_id.id,'value':(line.inv11/self.inv_amount_11)*100.0})
            if self.inv_amount_12 and line.inv12:
                res.append({'inv_seq':'inv12','child_analytic_id':line.child_analytic_id.id,'value':(line.inv12/self.inv_amount_12)*100.0})
            if abs(sale_amount - inv_amount) >0.1:
                raise Warning("Sale Amount and Invoice Amount is Not Matching")
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
        if abs(self.inv_amount_12 -inv12) >0.1:
            raise Warning("Invoice Planning and Invoice Distribution Not Matching for Inv Seq 12")
        return res
    
    @api.one 
    def update_inv_relation(self):
        res=self.check_condition()
        self.od_an_inv_rel_line.unlink()
        self.od_an_inv_rel_line = res
        self.od_inv_plan_locked =True

