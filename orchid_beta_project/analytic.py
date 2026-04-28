# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from pprint import pprint
from datetime import datetime,timedelta,date as dt
from od_default_milestone import od_project_vals,od_om_vals,od_amc_vals
from openerp.exceptions import Warning
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
import openerp.addons.decimal_precision as dp
class account_invoice(models.Model):
    _inherit = 'account.invoice'
    cust_date = fields.Date(string="Customer Accepted Date")
    state = fields.Selection([('draft','Draft'),('proforma','Pro-forma'),('proforma2','Pro-forma'),('open','Open'),('accept','Accepted By Customer'),('paid','Paid'),('cancel','Cancelled'),('asset_done','Asset Done'),('manual','Manually Settled')],string="Invoice Status")
    
    @api.multi
    def od_accept(self):
        dt_today = str(dt.today())
        self.cust_date  = dt_today
        self.state = 'accept'
        
    @api.multi
    def od_accept_paid(self):
        dt_today = str(dt.today())
        self.cust_date  = dt_today

    @api.multi
    def write(self, vals):
        
        res = super(account_invoice, self).write(vals)
#         self._check_od_invoice_project_amount()
        return res
    
    
    
    def _check_od_invoice_project_amount(self):
        """ Ensure the Invoice Amount Not Greater than Project Value"""
        if self.od_analytic_account:
            analytic_id  = self.od_analytic_account and self.od_analytic_account.id
            invoice_except =  self.od_analytic_account and self.od_analytic_account.od_create_inv_except
#             if self.type == 'out_invoice':
#                 if not invoice_except:
#                     project_amount = self.od_analytic_account and self.od_analytic_account.od_amended_sale_price 
#                     already_invoiced  = self.env['account.invoice'].search([('od_analytic_account','=',analytic_id),('id','!=',self.id),('state','in',('accept','paid'))])
#                     already_invoiced_amt = sum([inv.amount_untaxed for inv in already_invoiced])  
#                     customer_refund = self.env['account.invoice'].search([('od_analytic_account','=',analytic_id),('type','=','out_refund'),('state','not in',('draft','cancel'))])
#                     customer_refund_amount = sum([inv.amount_untaxed for inv in customer_refund])
#                     current_inv_amount = self.amount_untaxed
#                     collected = already_invoiced_amt + current_inv_amount -customer_refund_amount
#                     if collected > project_amount:
#                         raise Warning("Invoice Value Cannot Be Greater Than Project Value,Kindly Contact Admin")
#                     

class account_move_line(models.Model):
    _inherit = "account.move.line"
    od_state = fields.Selection([('draft','Unposted'),('posted','Posted')],string="Parent Status",related="move_id.state")

class project_project(models.Model):
    _inherit = "project.project"
    
    
    def get_invoice_amt(self):
        #this function using for high level wip report collected amount
        analytic_id = self.analytic_account_id and self.analytic_account_id.id
        pmo_collected = self.od_pmo_collected
        if pmo_collected:
            collected = self.od_collected
            return collected 
        already_invoiced  = self.env['account.invoice'].search([('od_analytic_account','=',analytic_id),('type','=','out_invoice'),('state','in',('manual','paid'))])
        already_invoiced_amt = sum([inv.amount_total for inv in already_invoiced])  
        partially_collected = self.env['account.invoice'].search([('od_analytic_account','=',analytic_id),('type','=','out_invoice'),('state','in',('accept','open'))])
        partially_collected_amt = sum([inv.amount_total  - inv.residual for inv in partially_collected])
        already_invoiced_amt += partially_collected_amt
        customer_refund = self.env['account.invoice'].search([('od_analytic_account','=',analytic_id),('type','=','out_refund'),('state','not in',('draft','cancel'))])
        customer_refund_amount = sum([inv.amount_total for inv in customer_refund])
        in_collected = already_invoiced_amt - customer_refund_amount
    
        collected = (in_collected/1.05)
        if abs(collected) <1:
            collected =0.0
         
        dist_line = self.env['od.dist.line']
        dom3 = [('analytic_id','=',analytic_id)]
        dist_line_ids = dist_line.search(dom3)
        for line in dist_line_ids:
            inv_id = line.invoice_id
            if not inv_id.od_refund:
                value = line.value
                if inv_id.state == 'paid':
                    collected +=(value/100.0) * inv_id.amount_untaxed
        return collected
    
    def od_send_mail(self,template):
        ir_model_data = self.env['ir.model.data']
        email_obj = self.pool.get('email.template')
        saudi_comp =6
        emp_company_id = self.company_id.id
        if emp_company_id == saudi_comp:
            template = template +'_saudi'
        template_id = ir_model_data.get_object_reference('orchid_beta_project', template)[1]
        proj_id = self.id
        email_obj.send_mail(self.env.cr, self.env.uid, template_id,proj_id)
        return True
    
    @api.multi
    def od_send_proj_close_mail(self):
        if self.analytic_account_id:
            self.od_send_mail('od_closed_project_notify')

class account_analytic_account(models.Model):
    _inherit = "account.analytic.account"
    DOMAIN = [('parent_level0','Parent Level View'),('amc_view','AMC View'),('o_m_view','O&M View'),('credit','Credit'),('sup','Supply'),('imp','Implementation'),('sup_imp','Supply & Implementation'),
              ('amc','AMC'),('o_m','O&M'),('cust_trn','Customer Training'),('poc','(POC,Presales)'), ('comp_gen','Company General -(Training,Labs,Trips,etc.)')]
    
    state = fields.Selection([('template','Template'),('draft','New'),('open','In Progress'),('pending','To Renew'),('sign_off','Sign Off'),('close','Closed'),('cancelled','Cancelled')],string="Status")
    
    od_type_of_project = fields.Selection(DOMAIN,string="Type Of Project")
    use_timesheets = fields.Boolean(string="Timesheets",readonly=False)
    use_tasks = fields.Boolean(string="Tasks",readonly=False)
    use_issues = fields.Boolean(string="Issues",readonly=False)
    od_create_inv_except = fields.Boolean(string="Invoice Create(Ignore Exception)")
    od_close_proj_except = fields.Boolean(string="Close Project(Ignore Exception)")
    od_cancel_analytic_except = fields.Boolean(string="Cancel Analytic(Ignore Exception)")
    
    
    od_project_invoice_schedule_line  = fields.One2many('od.project.invoice.schedule','analytic_id',string="Project Invoice Schedule")
    od_amc_invoice_schedule_line  = fields.One2many('od.amc.invoice.schedule','analytic_id',string="AMC Invoice Schedule")
    od_om_invoice_schedule_line  = fields.One2many('od.om.invoice.schedule','analytic_id',string="Operation Invoice Schedule")
    
    od_analytic_invoice_schedule_line  = fields.One2many('od.analytic.root.invoice.schedule','analytic_id',string="Analytic Invoice Schedule")
    

#     od_analytic_invoice_dist_line = fields.One2many('od.analytic.invoice.dist','analytic_id',string="Analytic Invoice Distribution")
    
    od_analytic_level = fields.Selection([('level_old','Level OLD'),('level_manual','Level Manual'),('level0','Level 0'),('level1','Level 1'),('level2','Level 2')],string="Analytic Level")
    grand_parent_id = fields.Many2one('account.analytic.account',string="Grand Parent Account")
    
    od_child_data = fields.One2many('account.analytic.account','parent_id',string="Children Account")
    od_grandchild_data = fields.One2many('account.analytic.account','grand_parent_id',string="Grand Children Account")
    od_closing_date = fields.Date(string="Closing Date")
    
    od_manual_input= fields.Boolean(string="Manual Input")
    od_manual_cost = fields.Boolean("Manually Enter Actual Cost?")
    man_original_sale = fields.Float(string="Original Sale(Manual)")
    man_original_cost = fields.Float(string="Original Cost(Manual)")
    man_mp = fields.Float(string="Returned Man Power(Manual)")
    mp_amend = fields.Float(string="Amended Returned Man Power(Manual)")
    check_amend_mp = fields.Boolean(string="Amend Return MP?")
    mp_actual = fields.Float(string="Actual MP(Manual)")
    check_actual_mp = fields.Boolean(string="Manually Enter Actual MP?")
    man_amended_sale = fields.Float(string="Amended Sale(Manual)")
    man_amended_cost = fields.Float(string="Amended Cost(Manual)")
    man_actual_sale = fields.Float(string="Actual Sale(Manual)")
    man_actual_cost = fields.Float(string="Actual Cost(Manual)")
    
    #Finance PMO dir kpi manual
    od_pmo_collected = fields.Boolean(string="PMO Manual Collected")
    od_pmo_paid = fields.Boolean(string="PMO Manual Paid")
    od_pmo_gc = fields.Boolean(string="PMO Manual General Cost")
    od_pmo_mp = fields.Boolean(string="PMO Manual Timesheet Cost")
    od_collected = fields.Float(string="Collected From Customer")
    od_paid = fields.Float(string="Paid to Supplier")
    od_gc = fields.Float(string="PMO General Cost")
    od_tm = fields.Float(string="PMO Timesheet Cost")
    
    od_manual_invoice = fields.Boolean(string="Manual Invoice")
    od_manual_invoice_amnt = fields.Float(string="Manual Invoice Amount")
    exclude_pmo_kpi = fields.Boolean(string="Exclude from PMO KPI")
    
    od_check_rebate = fields.Boolean(string="Manually Enter Rebate Amount?")
    od_manual_rebate = fields.Float(string="Manual Rebate Amount")
    
#     share_invoice = fields.Boolean(string="Share Invoice")
#     
#     
#     
#     
#     
#     @api.one
#     def od_dist_get_invoice_amount(self):
#         analytic_id = self.id
#         dist_line = self.env['od.analytic.invoice.dist']
#         dist_data=dist_line.search([('share_analytic_id','=',analytic_id),('applied','=',True)])
#         planned_amount =0.0
#         inv_accepted =0.0
#         for dist in dist_data:
#             invoice_percent = dist.invoice_percent 
#             invoice_amount = dist.invoice_amt
#             planned_amount +=invoice_amount * (invoice_percent/100.0)
#             invoice_status =  dist.invoice_root_id and dist.invoice_root_id.invoice_id and dist.invoice_root_id.invoice_id.state
#             if invoice_status in ('accept','paid'):
#                 inv_accepted +=invoice_amount * (invoice_percent/100.0)
#         self.invoice_accepted = inv_accepted 
#         self.invoice_planned = planned_amount 
#     
#     
#     invoice_planned = fields.Float(string="Invoice Planned",compute='od_dist_get_invoice_amount')
#     invoice_accepted = fields.Float(string="Invoice Accepted",compute='od_dist_get_invoice_amount')
    
    @api.multi
    def od_open_lg_request(self):
        opp_id = self.lead_id and self.lead_id.id or False
        partner_id = self.partner_id and self.partner_id.id or False
        sale_val = self.od_amended_sale_price
        context = self.env.context
        ctx = context.copy()
        ctx['default_lead_id'] = opp_id
        ctx['default_partner_id'] = partner_id
        ctx['default_job_amt'] = sale_val
        ctx['group_by'] = 'state'
        ctx['default_guarantee_name'] = 'performance_bond'
        if opp_id:
            domain = [('lead_id','=',opp_id)]
            return {
                'domain':domain,
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'od.lg.request.form',
                'type': 'ir.actions.act_window',
                'context':ctx,
            }

    
    @api.multi 
    def get_dist_child_analytic(self):
        res =[]
        if self.od_analytic_invoice_dist_line:
            raise Warning("Already Filled Up, If you want to reset, delete all the filled up data")
        analytic_id = self.id
        analytic_ids = self.search([('parent_id','=',analytic_id),('type','=','contract')])
        grand_child_ids =self.search([('grand_parent_id','=',analytic_id),('type','=','contract')])
        analytics = analytic_ids + grand_child_ids
        res = [{'share_analytic_id':an.id} for an in analytics]
        self.od_analytic_invoice_dist_line  = res
       
    
    def get_product_id_from_param(self,product_param):
        parameter_obj = self.env['ir.config_parameter']
        key =[('key', '=', product_param)]
        product_param_obj = parameter_obj.search(key)
        if not product_param_obj:
            raise Warning(_('Settings Warning!'),_('NoParameter Not defined\nconfig it in System Parameters with %s'%product_param))
        product_id = product_param_obj.od_model_id and product_param_obj.od_model_id.id or False
        return product_id
    
    
    
    
    
    def get_projet_id(self):
        analytic_account_id = self.id 
        project =self.env['project.project'].search([('analytic_account_id','=',analytic_account_id)],limit=1)
        
        return project
    
    
    def create_milestone_tasks(self,task_vals,date_start,date_end):
        task_pool = self.env['project.task']
        project = self.get_projet_id()
        project_id = project.id
        user_id = project.user_id and project.user_id.id
        partner_ids = [(6,0,[user_id])],
        for val in task_vals:
            val.update({
            'project_id':project_id,
            'user_id':user_id,
            'partner_ids':partner_ids,
            'date_start':date_start,
            'date_end':date_end,
            'no_delete':True
            })
            task = task_pool.create(val)
        return True
    
    
    @api.one 
    def btn_create_pm(self):
        self.create_crm_helpdesk()
    
    
    def create_crm_helpdesk(self):
        
        if len(self.preventive_maint_line) == 0:
            raise Warning("At Lease One Preventive Maintenance Schedule Needed to Activate AMC")
        help_desk = self.env['crm.helpdesk']
        project = self.get_projet_id()
        project_id = project.id
        user_id = self.od_amc_owner_id and self.od_amc_owner_id.id
        od_organization_id = self.partner_id and self.partner_id.id
        categ_id =17
        for line in self.preventive_maint_line:
            if not line.help_desk_id:
                vals = {
                    'od_sch_id':line.id,
                    'od_project_id':project_id,
                    'user_id':user_id,
                    'name':line.name,
                    'od_organization_id':od_organization_id,
                    'date_deadline':line.date,
                    'categ_id':categ_id,
                    'od_prev_create':True,
                    }
                hp_id =help_desk.create(vals)
                line['help_desk_id'] = hp_id.id
        
    
    def update_bools(self):
        self.write({'use_timesheets':True,'use_tasks':True,'use_issues':True})
    
    @api.multi
    def btn_activate_project(self):
        self.update_bools()
        task_vals = od_project_vals()
        date_start = self.od_project_start 
        date_end = self.od_project_end
        self.create_milestone_tasks(task_vals, date_start, date_end)
        self.od_project_status = 'active'
    
    @api.multi
    def btn_activate_amc(self):
        self.update_bools()
        task_vals = od_amc_vals()
        date_start = self.od_amc_start 
        date_end = self.od_amc_end
        self.create_milestone_tasks(task_vals, date_start, date_end)
        self.create_crm_helpdesk()
        self.od_amc_status = 'active'
        
    @api.multi
    def btn_activate_om(self):
        self.update_bools()
        task_vals = od_om_vals()
        date_start = self.od_om_start
        date_end = self.od_om_end
        self.create_milestone_tasks(task_vals, date_start, date_end)
        self.od_om_status = 'active'
        
    #closing
    
    @api.multi
    def btn_close_project(self):
        #need to update to acutal cost from jv
        today = str(dt.today())
        closing_date = today 
        project_end = self.od_project_end
        
#         self.od_project_closing = today
#         if closing_date < project_end:
#             self.od_project_end = closing_date
        self.od_project_status = 'close'
    
    
    @api.multi
    def btn_close_amc(self):
        #need to update to acutal cost from jv
        today = str(dt.today())
        closing_date = today 
        
        if self.od_project_status == 'active':
            raise Warning("Please Close the Project First")
#         self.od_amc_closing = closing_date
        self.od_amc_status = 'close'
    
    @api.multi
    def btn_close_om(self):
        #need to update to acutal cost from jv
        
        today = str(dt.today())
        closing_date = today 
        
        if not closing_date:
            raise Warning("Please Fill the Closing Date")
        self.od_om_closing = closing_date
        self.od_om_status = 'close'
    
    
    
    
    def cron_od_contract_expiry(self, cr, uid,context=None):
        context = dict(context or {})
        remind = []

        
        def get_sender_addr(partner_id):
            email = ''
            partner_obj = self.pool.get('res.partner')
            partner_ids = partner_obj.search(cr,uid,[('parent_id','=',partner_id)],limit=1)
            if partner_ids:
                partner = partner_obj.browse(cr,uid,partner_ids)
                email = partner.email
            return email


        def fill_remind( domain):
            base_domain = []
            base_domain.extend(domain)
            analytic_ids = self.search(cr, uid, base_domain, context=context)
            for analytic in self.browse(cr,uid,analytic_ids,context=context):
                today = datetime.now().date()
                end_date = analytic.date
                if end_date:
                    partner_id = analytic.partner_id and analytic.partner_id.id
                    to_mail = get_sender_addr(partner_id)
                    days_diff = (today - datetime.strptime(end_date, '%Y-%m-%d')).days + 1
                    if days_diff < 7:
                        val = {'name':analytic.name,'code':analytic.code,'end_date':end_date,'to_mail':to_mail}
                        remind.append(val)

        for company_id in [1,6]:
            remind = []
            fill_remind([('state','not in',('close','cancelled')),('company_id','=',company_id)])
            template = 'od_contract_cron_email_template'
            if company_id == 6:
                template = template + '_saudi'
            template_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'orchid_beta_project', template)[1]
            for val in remind:
                context["data"] = val
                if val:
                    self.pool.get('email.template').send_mail(cr, uid, template_id, uid, force_send=True, context=context)

        return True




    @api.one
    def od_get_timesheet_units(self):

        timesheet = self.env['hr.analytic.timesheet']
        analytic_id = self.id
        domain = [('account_id','=',analytic_id)]
        timesheet_obj = timesheet.search(domain)
        timesheet_units = sum([tm.unit_amount for tm in timesheet_obj])
        self.od_timesheet_units = timesheet_units
    def od_get_project(self):
        analytic_id = self.id
        project = self.env['project.project']
        domain = [('analytic_account_id','=',analytic_id)]
        project_obj = project.search(domain,limit=1)
        return project_obj
    
    
    def get_invoice_collected_amount(self):
        cr = self.env.cr
        analytic_id = self.id 
        company_id = self.company_id and self.company_id.id
        invoice_account_id = 4006
        if company_id ==6:
            invoice_account_id =5332
            
        query_param2 = (invoice_account_id,analytic_id,)
        query2 = "select sum(credit-debit) from account_move_line where account_id =%s and analytic_account_id = %s and state='valid'"%query_param2
        cr.execute(query2)
        invoice_amount = cr.fetchone()[0]
        return invoice_amount
#     def od_check_invoice_settled(self):
#         analytic_id = self.id 
#         if not self.od_close_proj_except:
#             project_amount = self.od_amended_sale_price 
#             already_invoiced  = self.env['account.invoice'].search([('od_analytic_account','=',analytic_id),('type','=','out_invoice'),('state','in',('accept','paid'))])
#             already_invoiced_amt = sum([inv.amount_untaxed for inv in already_invoiced])  
#             customer_refund = self.env['account.invoice'].search([('od_analytic_account','=',analytic_id),('type','=','out_refund'),('state','not in',('draft','cancel'))])
#             customer_refund_amount = sum([inv.amount_untaxed for inv in customer_refund])
#             in_collected = already_invoiced_amt - customer_refund_amount
#             collected = self.get_invoice_collected_amount()
#             if in_collected > collected:
#                 collected = in_collected
#             check_value = project_amount - collected
#             if check_value > 1.0:
#                 raise Warning("Invoice Collected is Lesser than the Project Value")
#     
    def od_check_invoice_settled(self):
        analytic_id = self.id 
        if not self.od_close_proj_except:
            project_amount = self.od_amended_sale_price 
            inv_amount =0.0
            for line in self.od_project_invoice_schedule_line:
                if line.invoice_status in ('paid','accept'):
                    inv_amount +=line.invoice_amount
            for line in self.od_amc_invoice_schedule_line:
                if line.invoice_status in ('paid','accept'):
                    inv_amount +=line.invoice_amount
            if not self.od_project_invoice_schedule_line:
                if self.od_pmo_collected:
                    inv_amount = self.od_collected 
            if inv_amount <project_amount:
                raise Warning("Invoice Collected is Lesser than the Project Value")
            
    def get_invoice_amt(self):
        #this function using for high level wip report collected amount
        analytic_id = self.id
        pmo_collected = self.od_pmo_collected
        if pmo_collected:
            collected = self.od_collected
            return collected 
        already_invoiced  = self.env['account.invoice'].search([('od_analytic_account','=',analytic_id),('type','=','out_invoice'),('state','in',('manual','paid'))])
        already_invoiced_amt = sum([inv.amount_total for inv in already_invoiced])  
        partially_collected = self.env['account.invoice'].search([('od_analytic_account','=',analytic_id),('type','=','out_invoice'),('state','in',('accept','open'))])
        partially_collected_amt = sum([inv.amount_total  - inv.residual for inv in partially_collected])
        already_invoiced_amt += partially_collected_amt
        customer_refund = self.env['account.invoice'].search([('od_analytic_account','=',analytic_id),('type','=','out_refund'),('state','not in',('draft','cancel'))])
        customer_refund_amount = sum([inv.amount_total for inv in customer_refund])
        in_collected = already_invoiced_amt - customer_refund_amount
        collected = (in_collected/1.05)
        if abs(collected) <1:
            collected =0.0
        
        dist_line = self.env['od.dist.line']
        dom3 = [('analytic_id','=',analytic_id)]
        dist_line_ids = dist_line.search(dom3)
        for line in dist_line_ids:
            inv_id = line.invoice_id
            if not inv_id.od_refund:
                value = line.value
                if inv_id.state == 'paid':
                    collected +=(value/100.0) * inv_id.amount_untaxed
        
        return collected
    
    def get_coll_amount_new(self):
        dist_line =self.env['od.dist.line'].search([('analytic_id','=',self.id)])
        amount =0.0
        for dist in dist_line:
            invoice = dist.invoice_id 
            invoice_amount = invoice.amount_total
            residual = invoice.residual
            collected = invoice_amount - residual
            share = dist.value 
            collected_share = collected * (share/100.0)
            amount += collected_share
        return amount
    
    
    @api.multi
    def set_close(self):
        project_obj = self.od_get_project()
        today = str(dt.today())
        closing_date = today
        if self.od_closing_date:
            closing_date = self.od_closing_date
        
        original_date_end = self.od_date_end_original
        if closing_date < original_date_end:
            self.od_date_end_original = closing_date
        project_obj.write({'state':'close','od_closing_date':closing_date})
        if self.od_project_status == 'active':
            self.btn_close_project()
        if self.od_amc_status == 'active':
            self.btn_close_amc()
        project_obj.od_send_proj_close_mail()
        return super(account_analytic_account,self).set_close()
    
    @api.multi
    def od_set_sign_off(self):
        self.od_check_invoice_settled()
        project_obj = self.od_get_project()
        project_obj.od_set_sign_off()
        
    
    @api.multi
    def set_open(self):
        project_obj = self.od_get_project()
        project_obj.write({'state':'open'})
        return super(account_analytic_account,self).set_open()
    
    def cancel_related_so(self):
        project_id = self.id
        active_so  = self.env['sale.order'].search([('project_id','=',project_id), ('state','!=','cancel')])
        for so in active_so:
            so.od_action_cancel()

    def check_po_generated(self):
        project_id = self.id
        analytic_except =  self.od_cancel_analytic_except
        if not analytic_except:
            active_po  = self.env['purchase.order'].search([('project_id','=',project_id), ('state','!=','cancel')])
            po_names = []
            for po in active_po:
                po_names.append(po.name)
            if active_po:
                po_names = ','.join(po_names)
                raise Warning(_('In order to Cancel an Analytic Account, You First Cancel all the related Purchase Orders - \'%s\'.') % po_names)
    
    def check_od_invoice_generated(self):
        analytic_id  = self.id
        analytic_except =  self.od_cancel_analytic_except
        if not analytic_except:
            already_invoiced  = self.env['account.invoice'].search([('od_analytic_account','=',analytic_id),('type','=','out_invoice'),('state','in',('open','accept','paid'))])
            invoiced_amt = sum([inv.amount_total for inv in already_invoiced])  
            customer_refund = self.env['account.invoice'].search([('od_analytic_account','=',analytic_id),('type','=','out_refund'),('state','not in',('draft','cancel'))])
            customer_refund_amount = sum([inv.amount_total for inv in customer_refund])
            if invoiced_amt != customer_refund_amount:
                raise Warning("In order to Cancel an Analytic Account, You First Cancel all the related Customer Invoices")
            
            already_invoiced1  = self.env['account.invoice'].search([('od_analytic_account','=',analytic_id),('type','=','in_invoice'),('state','in',('open','accept','paid'))])
            sup_invoiced_amt = sum([inv.amount_total for inv in already_invoiced1])  
            supplier_refund = self.env['account.invoice'].search([('od_analytic_account','=',analytic_id),('type','=','in_refund'),('state','not in',('draft','cancel'))])
            supplier_refund_amount = sum([inv.amount_total for inv in supplier_refund])
            if sup_invoiced_amt != supplier_refund_amount:
                raise Warning("In order to Cancel an Analytic Account, You First Cancel all the related Supplier Invoices")
            
    def check_costs_linked(self):
        pass

    @api.multi
    def set_cancel(self):
        self.check_po_generated()
        self.check_od_invoice_generated()
        self.check_costs_linked()
        project_obj = self.od_get_project()
        project_obj.write({'state':'cancelled'})
        self.write({'od_project_status':'cancel','od_amc_status':'cancel'})
        self.cancel_related_so()
        return super(account_analytic_account,self).set_cancel()

    @api.multi
    def set_pending(self):
        project_obj = self.od_get_project()
        project_obj.write({'state':'pending'})
        return super(account_analytic_account,self).set_pending()


    def od_update(self,values,data,key):
        if values.get(data,False):
            write_val = values.get(data)
            project_ob = self.od_get_project()
            project_ob.write({key:write_val})
    def od_update_vals(self,values):
        self.od_update(values,'od_owner_id','user_id')
        self.od_update(values,'quantity_max','od_quantity_max')
        self.od_update(values,'od_type_of_project','od_type_of_project')
    @api.multi
    def write(self, values):
        self.od_update_vals(values)
        return super(account_analytic_account, self).write(values)

    @api.one
    def od_get_sales_order_count(self):
        sale_order = self.env['sale.order']
        analytic_id = self.id
        domain =[('project_id','=',analytic_id)]
        count =len(sale_order.search(domain))
        self.od_sale_count = count
        
    @api.one
    def od_get_no_of_change_mgmt(self):
        cost_sheet_id = self.od_cost_sheet_id and self.od_cost_sheet_id.id or False
        cm_recs = self.env['change.management'].search([('cost_sheet_id','=', cost_sheet_id)])
        self.count_change_mgmt = len(cm_recs)


    @api.one
    @api.depends('od_cost_sheet_id')
    def od_get_po_status(self):
        if self.od_cost_sheet_id:
            self.od_po_status = self.od_cost_sheet_id.po_status


#     
#     @api.onchange('man_original_sale','man_original_cost')
#     def onchange_original_price(self):
#         original_sale = self.man_original_sale
#         original_cost = self.man_original_cost
#         self.man_amended_sale = original_sale 
#         self.man_actual_sale = original_sale 
#         self.man_amended_cost = original_cost
        
       
    
    
    
    @api.one
    def od_get_total_sale_value(self):
        #Added By Nabeel
        mp_amend_manual = self.mp_amend
        sale_order = self.env['sale.order']
        analytic_id = self.id
        parent_id = self.parent_id and self.parent_id.id
        domain =[('project_id','=',analytic_id),('state','!=','cancel')]
        sales = sale_order.search(domain,limit=1)
        bim_profit = self.bim_profit 
        bmn_profit = self.bmn_profit
#         mp_profit = bim_profit + bmn_profit
#         total = sum([sal.amount_total for sal in sales])
        original_price = 0.0
        original_cost = 0.0
        original_profit =0.0
        original_profit_perc = 0.0
        amended_profit_perc = 0.0
        amended_price = 0.0
        amended_cost = 0.0
        planned_timesheet_cost = 0.0
        rt_profit =0.0
        mp_profit =0.0
        od_rebate = 0.0
#         for sale in sales:
#             for line in sale.order_line:
#                 if line.product_id.id in (211961,208829,208831):
#                     planned_timesheet_cost += line.od_original_line_cost
#                 original_price += line.od_original_line_price
#                 original_cost += line.od_original_line_cost
#                 amended_price += line.price_subtotal
#                 amended_cost += line.od_amended_line_cost
#         original_profit = original_price - original_cost
        
        
        if sales:
            original_price = sales.od_original_total_price
            original_cost = sales.od_original_total_cost
            
            amended_price = sales.od_amd_total_price
            amended_cost = sales.od_amd_total_cost
        else:
            for line in self.od_sale_line:
                original_price += line.od_original_line_price 
                original_cost += line.od_original_line_cost
                amended_price += line.price_subtotal 
                amended_cost +=line.od_amended_line_cost
        if self.od_cost_sheet_id and self.od_cost_sheet_id.select_a0:
            a1_aa_id =self.od_cost_sheet_id and self.od_cost_sheet_id.analytic_a1 and self.od_cost_sheet_id.analytic_a1.id or False
            a2_aa_id =self.od_cost_sheet_id and self.od_cost_sheet_id.analytic_a2 and self.od_cost_sheet_id.analytic_a2.id or False
            a3_aa_id =self.od_cost_sheet_id and self.od_cost_sheet_id.analytic_a3 and self.od_cost_sheet_id.analytic_a3.id or False
            a4_aa_id =self.od_cost_sheet_id and self.od_cost_sheet_id.analytic_a4 and self.od_cost_sheet_id.analytic_a4.id or False
            a5_aa_id =self.od_cost_sheet_id and self.od_cost_sheet_id.analytic_a5 and self.od_cost_sheet_id.analytic_a5.id or False
            if analytic_id == a1_aa_id:
                if 3 in self.od_cost_sheet_id.tabs_a1.mapped('id'):
                    rt_profit = self.od_cost_sheet_id and self.od_cost_sheet_id.a_bim_cost or 0.0
                    self.mp_amend = rt_profit
                amended_price = self.od_cost_sheet_id.disc_sales_a1
                amended_cost= self.od_cost_sheet_id.cost_a1
                od_rebate = self.od_cost_sheet_id.rebate_a1
            if analytic_id == a2_aa_id:
                if 3 in self.od_cost_sheet_id.tabs_a2.mapped('id'):
                    rt_profit = self.od_cost_sheet_id and self.od_cost_sheet_id.a_bim_cost or 0.0
                    self.mp_amend = rt_profit
                amended_price = self.od_cost_sheet_id.disc_sales_a2
                amended_cost= self.od_cost_sheet_id.cost_a2
                od_rebate = self.od_cost_sheet_id.rebate_a2
            if analytic_id == a3_aa_id:
                if 3 in self.od_cost_sheet_id.tabs_a3.mapped('id'):
                    rt_profit = self.od_cost_sheet_id and self.od_cost_sheet_id.a_bim_cost or 0.0
                    self.mp_amend = rt_profit
                amended_price = self.od_cost_sheet_id.disc_sales_a3
                amended_cost= self.od_cost_sheet_id.cost_a3
                od_rebate = self.od_cost_sheet_id.rebate_a3
            if parent_id and parent_id == a4_aa_id:
                no_of_l2 = self.od_cost_sheet_id and self.od_cost_sheet_id.no_of_l2_accounts_amc 
                if no_of_l2:
                    amended_price = self.od_cost_sheet_id.disc_sales_a4/no_of_l2
                    amended_cost= self.od_cost_sheet_id.cost_a4/no_of_l2
                    bmn_cost  =self.od_cost_sheet_id and self.od_cost_sheet_id.a_bmn_cost or 0.0
                    rt_profit = bmn_cost/no_of_l2
                    self.mp_amend = rt_profit
            if parent_id and parent_id == a5_aa_id:
                no_of_l2 = self.od_cost_sheet_id and self.od_cost_sheet_id.no_of_l2_accounts_om 
                if no_of_l2:
                    amended_price = self.od_cost_sheet_id.disc_sales_a5/no_of_l2
                    amended_cost= self.od_cost_sheet_id.cost_a5/no_of_l2
            

            
                 
        
        bim_cost = self.od_cost_sheet_id and self.od_cost_sheet_id.a_bim_cost or 0.0
        bmn_cost  =self.od_cost_sheet_id and self.od_cost_sheet_id.a_bmn_cost or 0.0
        
        
        project_bmn = self.od_cost_sheet_id and self.od_cost_sheet_id.project_bmn and self.od_cost_sheet_id.project_bmn.id or False
        project_bim = self.od_cost_sheet_id and self.od_cost_sheet_id.project_bim and self.od_cost_sheet_id.project_bim.id or False
        if analytic_id == project_bmn:
            rt_profit =bmn_cost
            mp_profit = bmn_profit
        
        if analytic_id == project_bim:
            rt_profit = bim_cost
            mp_profit = bim_profit
        
        
        if self.od_manual_input:
            original_price = self.man_original_sale 
            original_cost = self.man_original_cost
            amended_price = self.man_amended_sale 
            amended_cost = self.man_amended_cost
            rt_profit = self.man_mp 
            mp_profit = self.man_mp
            bim_profit =0.0
            bmn_profit =0.0
            bmn_cost =bim_cost =0.0
        if self.check_amend_mp:
            # rt_profit = self.mp_amend
            # Added by Nabeel
            rt_profit = mp_amend_manual
        if self.od_check_rebate:
            od_rebate = self.od_manual_rebate
            
        original_profit = original_price - original_cost
        if original_price:
            original_profit_perc = (original_profit/original_price) *100
        
        amended_profit = amended_price - amended_cost
        if amended_price:
            amended_profit_perc = (amended_profit/amended_price) * 100
        
        
        
        self.od_original_sale_price = original_price
        self.od_original_sale_cost = original_cost
        self.od_original_profit = original_profit
        original_mp = self.od_original_mp
        # self.od_original_sale_profit = mp_profit + original_profit
        self.od_original_sale_profit = original_mp + original_profit
        self.od_original_sale_profit_perc = original_profit_perc
        self.od_amended_sale_price = amended_price
        self.od_amended_sale_cost = amended_cost
        self.od_rebate = od_rebate
#         self.od_actual_sale = amended_price
        self.od_amended_mp = rt_profit
        self.od_amended_prof = amended_profit
        self.od_amended_profit = amended_profit + rt_profit
        self.od_amended_profit_perc = amended_profit_perc
        self.od_planned_timesheet_cost = planned_timesheet_cost
    

    @api.one
    def od_get_total_purchase(self):
        purchase_order_line = self.env['purchase.order.line']
        analytic_id = self.id
        domain = [('account_analytic_id','=',analytic_id)]
        lines = purchase_order_line.search(domain)
        if lines:
            amount = sum([line.price_subtotal for line in lines])
            #self.od_amnt_purchased = amount
            self.od_amnt_purchased2 = amount
            
        purchase_order = self.env['purchase.order']
        domain = [('project_id','=',analytic_id),('state','in',('approved','done'))]
        pos = purchase_order.search(domain)
        if pos:
            amount = sum([po.bt_amount_total for po in pos])
            self.od_amnt_purchased = amount
#     @api.multi
#     def od_btn_open_invoice_lines(self):
#         analytic_id = self.id
#         inv_li_pool = self.env['account.invoice.line']
#         domain = [('account_analytic_id','=',analytic_id)]
#         raw_inv_ids = inv_li_pool.search(domain)
#         inv_li_ids = [line.id for line in raw_inv_ids if line.invoice_id.state not in ('draft','cancel')]
#         dom = [('id','in',inv_li_ids)]
#         return {
#             'domain':dom,
#             'view_type': 'form',
#             'view_mode': 'tree,form',
#             'res_model': 'account.invoice.line',
#             'type': 'ir.actions.act_window',
#         }
        
    
    
    
    
    
    
    
    def get_invoice_untaxed_amount(self):
        analytic_id = self.id
        manual = self.od_manual_invoice
        if manual:
            amount = self.od_manual_invoice_amnt or 0.0
            return amount
        invoice_pool = self.env['account.invoice']
        domain = [('od_analytic_account','=',analytic_id),('type','=','out_refund'),('state','not in',('draft','cancel'))]
        inv_ids = invoice_pool.search(domain)
        refund_amount_total = sum([inv.amount_untaxed for inv in inv_ids])
        
        domain2 = [('od_analytic_account','=',analytic_id),('type','=','out_invoice'),('state','not in',('draft','cancel'))]
        inv_ids = invoice_pool.search(domain2)
        amount_total = sum([inv.amount_untaxed for inv in inv_ids])
        

        dist_line = self.env['od.dist.line']
        dom3 = [('analytic_id','=',analytic_id)]
        dist_line_ids = dist_line.search(dom3)
        for line in dist_line_ids:
            inv_id = line.invoice_id
            if not inv_id.od_refund:
                value = line.value
                if inv_id.state not in ('draft','cancel'):
                    amount_total +=(value/100.0) * inv_id.amount_untaxed
    
        return amount_total -refund_amount_total 
    
    
    
    
    @api.one
    def od_get_total_invoice(self):
        analytic_id = self.id
        invoice_pool = self.env['account.invoice']
        domain = [('od_analytic_account','=',analytic_id),('type','=','out_invoice'),('state','not in',('draft','cancel')),('od_refund','=',False)]
        inv_ids = invoice_pool.search(domain)
        amount_total = sum([inv.amount_total for inv in inv_ids])
        self.od_amnt_invoiced = amount_total
        self.od_amnt_invoiced2= amount_total
    
    @api.multi
    def od_btn_open_customer_invoice(self):
        analytic_id = self.id
        invoice_pool = self.env['account.invoice']
        domain = [('od_analytic_account','=',analytic_id),('type','=','out_invoice'),('od_refund','=',False)]
        inv_ids = invoice_pool.search(domain)
        inv_li_ids = [inv.id for inv in inv_ids]
        dom = [('id','in',inv_li_ids)]
        
        model_data = self.env['ir.model.data']
        tree_view = model_data.get_object_reference('account', 'invoice_tree')
        form_view = model_data.get_object_reference('account', 'invoice_form')

        
        return {
            'domain':dom,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice',
            'views': [(tree_view and tree_view[1] or False, 'tree'),(form_view and form_view[1] or False, 'form'), ],
            'type': 'ir.actions.act_window',
        }

#     @api.multi
#     def od_btn_open_purchase_lines(self):
#         analytic_id = self.id
#         domain = [('account_analytic_id','=',analytic_id)]
#         return {
#             'domain':domain,
#             'view_type': 'form',
#             'view_mode': 'tree,form',
#             'res_model': 'purchase.order.line',
#             'type': 'ir.actions.act_window',
#         }
        
    @api.multi
    def od_btn_open_purchase_lines(self):
        analytic_id = self.id
        domain = [('project_id','=',analytic_id)]
        return {
            'domain':domain,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'purchase.order',
            'type': 'ir.actions.act_window',
        }

    def od_get_do(self):
        analytic_id = self.id
        domain = [('od_analytic_id','=',analytic_id)]
        picking_obj = self.env['stock.picking']
        pickings = picking_obj.search(domain)
        return pickings


    @api.multi
    def od_btn_open_delivery_orders(self):
        pickings = self.od_get_do()
        picking_ids = [pick.id for pick in pickings]
        dom = [('id','in',picking_ids)]
        return {
            'domain':dom,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'type': 'ir.actions.act_window',
        }
    @api.multi
    def od_btn_open_sales_orders(self):
        sales_order = self.env['sale.order']
        analytic_id = self.id
        domain = [('project_id','=',analytic_id)]
        sales = sales_order.search(domain)
        sale_ids = [sale.id for sale in sales]
        dom = [('id','in',sale_ids)]
        return {
            'domain':dom,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
        }
        
    @api.multi
    def od_btn_open_change_mgmt(self):
        
#         company_id =self.env.user.company_id
#         pmo_user =19 
#         if company_id ==6:
#             pmo_user =142  
        
        cs_id = self.od_cost_sheet_id and self.od_cost_sheet_id.id or False
        context = self.env.context
        ctx = context.copy()
        ctx['change'] = True
        ctx['default_cost_sheet_id'] = cs_id
        ctx['default_branch_id'] = self.od_branch_id and self.od_branch_id.id or False
#         ctx['default_first_approval_manager_id'] = pmo_user
        if cs_id:
            domain = [('cost_sheet_id','=',cs_id)]
            return {
                'domain':domain,
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'change.management',
                'type': 'ir.actions.act_window',
                'context':ctx
            }

    
    @api.multi
    def od_btn_open_lots(self):
        model_data = self.env['ir.model.data']
        pickings = self.od_get_do()
        picking_ids = [pick.id for pick in pickings]
        stock_pack_op_obj = self.env['stock.pack.operation']
        domain = [('picking_id','in',picking_ids)]
        pack_ops = stock_pack_op_obj.search(domain)
        pack_op_ids = [op.id for op in pack_ops]
        dom = [('id','in',pack_op_ids)]
        search_view_id = model_data.get_object_reference('orchid_beta_project', 'beta_project_stock_pakc_op_search_view')

        return {
            'name': _('Beta Lot Serial View'),
            'domain':dom,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'stock.pack.operation',
            'type': 'ir.actions.act_window',

        }
    def od_action_schedule_meeting(self, cr, uid, ids, context=None):
        """
        Open meeting's calendar view to schedule meeting on current opportunity.
        :return dict: dictionary value for created Meeting view
        """
        analytic = self.browse(cr, uid, ids[0], context)
        res = self.pool.get('ir.actions.act_window').for_xml_id(cr, uid, 'calendar', 'action_calendar_event', context)
        partner_ids = [self.pool['res.users'].browse(cr, uid, uid, context=context).partner_id.id]
        if analytic.partner_id:
            partner_ids.append(analytic.partner_id.id)
        res['context'] = {
            'search_default_od_analytic_account_id': analytic.id,
            'default_od_analytic_account_id':analytic.id,
            'default_partner_id': analytic.partner_id and analytic.partner_id.id or False,
            'default_partner_ids': partner_ids,
            'default_name': analytic.name,
        }
        ctx = {
            'search_default_od_analytic_account_id': analytic.id,
            'default_od_analytic_account_id':analytic.id,
            'default_partner_id': analytic.partner_id and analytic.partner_id.id or False,
            'default_partner_ids': partner_ids,
            'default_name': analytic.name,
        }
        domain = [('od_analytic_account_id','=',analytic.id)]
        return {
            'domain':domain,
            'context':context,
            'view_type': 'form',
            'view_mode': 'tree,form,calendar',
            'res_model': 'calendar.event',
            'type': 'ir.actions.act_window',
        }
    @api.one
    def _od_meeting_count(self):
        Event = self.env['calendar.event']
        analytic_id = self.id
        domain = [('od_analytic_account_id','=',analytic_id)]
        meeting_count =0
        meeting_count = len(Event.search(domain))
        self.od_meeting_count = meeting_count

    def od_open_timesheets(self, cr, uid, ids, context=None):
        """ open Timesheets view """
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')

        analytic_account_id = self.browse(cr, uid, ids[0], context)
        view_context = {
            'search_default_account_id': [analytic_account_id.id],
            'default_account_id': analytic_account_id.id,
        }
        res = mod_obj.get_object_reference(cr, uid, 'hr_timesheet', 'act_hr_timesheet_line_evry1_all_form')
        id = res and res[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        result['name'] = _('Timesheets')
        result['context'] = view_context

        return result
    @api.one
    def od_get_timesheet_amount(self):
        timesheet = self.env['hr.analytic.timesheet']
        analytic_id = self.id
        domain = [('account_id','=',analytic_id)]
        timesheet_obj = timesheet.search(domain)
        amount = sum([tm.normal_amount for tm in timesheet_obj])
        self.od_timesheet_amount = amount
        
        #Added by aslam for calculating Actual MP from Jv's -above code from timesheets
        move_line_pool = self.env['account.move.line']
        company_id = self.company_id and self.company_id.id 
        wip_account = [False]
        journal_id = False
        hr_pool = self.env['hr.employee']
        #excluding outsourced engineers mp and salary jv's
        emp_ids = hr_pool.sudo().search(['|',('active', '=', True), ('active', '=',False), ('company_id', '=', company_id),('job_id', 'in', (161,162))])
        partner_ids = []
        for employee in emp_ids:
            partner_ids.append(employee.address_home_id.id)
        if company_id ==6:
            wip_account = [5732]
            journal_id =58
            #partner_ids = [13781, 13572, 13623, 12952, 11882, 13076, 13010, 13084]
        if company_id ==1:
            wip_account = [2128,2137]
            journal_id =21
            #partner_ids = [47, 49, 7542, 12757, 13405, 13705]
       
        domain1 = [('partner_id','not in',partner_ids),('analytic_account_id','=',analytic_id),('journal_id','=',journal_id),('account_id','in',wip_account)]
        move_line_ids = move_line_pool.search(domain1)
        actual_mp = sum([mvl.debit for mvl in move_line_ids if mvl.od_state =='posted'])
        self.od_timesheet_amount2 = actual_mp
        if self.check_actual_mp:
            self.od_timesheet_amount2 = self.mp_actual
    @api.multi
    def od_open_hr_expense_claim(self):
        hr_exp_line = self.env['hr.expense.line']
        analytic_id = self.id
        domain = [('analytic_account','=',analytic_id),('od_state','not in',('draft','cancelled','confirm','second_approval'))]
        return {
            'domain':domain,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'hr.expense.line',
            'type': 'ir.actions.act_window',
        }
    @api.one
    def od_get_hr_exp_claim_amount(self):
        hr_exp_line = self.env['hr.expense.line']
        analytic_id = self.id
        domain = [('analytic_account','=',analytic_id),('od_state','not in',('draft','cancelled','confirm','second_approval'))]
        hr_exp_obj =hr_exp_line.search(domain)
        amount  = sum([hr.total_amount for hr in hr_exp_obj])
        self.od_hr_claim_amount = amount
    @api.multi
    def od_open_hr_expense_claim_draft(self):
        hr_exp_line = self.env['hr.expense.line']
        analytic_id = self.id
        domain = [('analytic_account','=',analytic_id),('od_state','in',('draft','cancelled','confirm','second_approval'))]
        return {
            'domain':domain,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'hr.expense.line',
            'type': 'ir.actions.act_window',
        }
    @api.one
    def od_get_hr_exp_claim_amount_draft(self):
        hr_exp_line = self.env['hr.expense.line']
        analytic_id = self.id
        domain = [('analytic_account','=',analytic_id),('od_state','in',('draft','cancelled','confirm','second_approval'))]
        hr_exp_obj =hr_exp_line.search(domain)
        amount  = sum([hr.total_amount for hr in hr_exp_obj])
        self.od_hr_claim_amount_draft = amount

    @api.multi
    def od_btn_open_account_move_lines(self):
        analytic_id = self.id
        domain = [('analytic_account_id','=',analytic_id),('od_state','=','posted')]
        return {
            'domain':domain,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'type': 'ir.actions.act_window',
        }
    @api.one
    def od_get_analytic_journal_amount(self):
        account_move_line = self.env['account.move.line']
        analytic_id = self.id
        exclude_journal_ids = self.get_exclude_journal_ids()
        wip_account_ids = self.get_wip_account_id()
        domain = [('analytic_account_id','=',analytic_id),('journal_id','not in',exclude_journal_ids),('account_id','in',wip_account_ids),('od_state','=','posted')]
        if self.state == 'close':
            cost_of_account_ids = self.get_cost_of_sale_account()
            domain = [('analytic_account_id','=',analytic_id),('account_id','in',cost_of_account_ids),('od_state','=','posted')]
        journal_lines = account_move_line.search(domain)
        amount = sum([(mvl.debit - mvl.credit) for mvl in journal_lines])
        self.od_journal_amount = amount

    @api.multi
    def od_btn_open_account_move_lines_draft(self):
        analytic_id = self.id
        domain = [('analytic_account_id','=',analytic_id),('od_state','!=','posted')]
        return {
            'domain':domain,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'type': 'ir.actions.act_window',
        }
    @api.one
    def od_get_analytic_journal_amount_draft(self):
        account_move_line = self.env['account.move.line']
        analytic_id = self.id
        exclude_journal_ids = self.get_exclude_journal_ids()
        domain = [('analytic_account_id','=',analytic_id),('journal_id','not in',exclude_journal_ids),('od_state','!=','posted')]
        journal_lines = account_move_line.search(domain)
        amount = sum([mvl.debit for mvl in journal_lines])
        self.od_journal_amount_draft = amount

    @api.one
    @api.depends('od_amended_sale_cost','od_original_sale_cost')
    def _od_get_cost_control_api(self):
        if self.od_amended_sale_cost > self.od_original_sale_cost :
            self.od_cost_control_kpi = 0
        else:
            self.od_cost_control_kpi = 100

    @api.one
    @api.depends('od_amended_profit_perc','od_original_sale_profit_perc')
    def _od_get_scope_control_kpi(self):
        if self.od_original_sale_profit_perc:
            check_val = self.od_amended_profit_perc / self.od_original_sale_profit_perc
            if check_val < 1:
                self.od_scope_control_kpi = 0
            else:
                self.od_scope_control_kpi = 100

    @api.one
    @api.depends('od_planned_timesheet_cost','od_timesheet_amount2')
    def _get_manpower_cost_control(self):
        if self.od_planned_timesheet_cost:
            if self.od_timesheet_amount2/self.od_planned_timesheet_cost <1:
                self.od_manpower_kpi = 100
            else:
                self.od_manpower_kpi = 0

#     @api.one
#     @api.depends('date')
#     def _get_original_date(self):
#         print "original date>>>>>>>>>>>>>>>",self.od_original_closing_date
#         if not self.od_date_set and self.date:
#             self.od_original_closing_date = self.date
#             self.od_date_set = True
    # od_original_closing_date = fields.Date(string="Original Closing Date",compute="_get_original_date",store=True)
    
    
    def get_value_from_param(self,param):
        parameter_obj = self.env['ir.config_parameter']
        key =[('key', '=', param)]
        param_obj = parameter_obj.search(key)
        if not param_obj:
            raise Warning(_('Settings Warning!'),_('NoParameter Not defined\nconfig it in System Parameters with %s'%param))
        result = param_obj.value
        return result
    def get_exclude_journal_ids(self):
        company_id =self.company_id and self.company_id.id 
        exclude_param ='exclude_journals'
        if company_id ==6:
            exclude_param = exclude_param +'_ksa'
        vals = self.get_value_from_param(exclude_param)
        vals = vals.split(',')
        result = [int(val) for val in vals]
        return result
    
    
    def get_cost_of_sale_account(self):
        company_id = self.company_id and self.company_id.id 
        account_ids = []
        if company_id ==6:
            account_ids = [5417,5418,5419,5423,5424,5428,5429]
        if company_id ==1:
            account_ids =[3488,3489,3972,5682,5683]
        return account_ids
    
    
    def get_wip_account_id(self):
        company_id = self.company_id and self.company_id.id 
        account_ids = []
        if company_id ==6:
            account_ids = [5732,5212,5213,5214,5734]
        if company_id ==1:
            account_ids =[2128,2129,3972,2137]
        return account_ids
    
    
    
    @api.one
    def _get_cost_from_jv(self):
        analytic_id = self.id
        move_line_pool = self.env['account.move.line']
        exclude_journal_ids = self.get_exclude_journal_ids()
        wip_account_ids = self.get_wip_account_id()
        domain = [('analytic_account_id','=',analytic_id),('journal_id','not in',exclude_journal_ids),('account_id','in',wip_account_ids)]
        move_line_ids = move_line_pool.search(domain)
        actual_cost = sum([(mvl.debit - mvl.credit)  for mvl in move_line_ids if mvl.od_state =='posted'])
        
            
        project_cost =0.0
        amc_cost =0.0
        if self.od_project_closing:
            closing_date = self.od_project_closing 
            project_cost = sum([(mvl.debit -mvl.credit) for mvl in move_line_ids if mvl.date <= closing_date and mvl.od_state =='posted'])
        if self.od_amc_closing:
            if self.od_project_closing:
                closing_date = self.od_project_closing 
                amc_cost = sum([(mvl.debit -mvl.credit) for mvl in move_line_ids if mvl.date > closing_date and mvl.od_state =='posted'])
            else:
                amc_cost = sum([(mvl.debit -mvl.credit) for mvl in move_line_ids if mvl.od_state =='posted'])
        
        if self.state == 'close':
            cost_of_sale_account_ids = self.get_cost_of_sale_account()
            domain = [('analytic_account_id','=',analytic_id),('account_id','in',cost_of_sale_account_ids)]
            move_line_ids = move_line_pool.search(domain)
            actual_cost = sum([(mvl.debit - mvl.credit) for mvl in move_line_ids if mvl.od_state =='posted'])
            closing_date = self.od_project_closing 
            if self.od_project_status =='close':
                project_cost = sum([(mvl.debit - mvl.credit) for mvl in move_line_ids if mvl.date <= closing_date and mvl.od_state =='posted'])
            if self.od_amc_status == 'close':
                amc_cost = sum([(mvl.debit - mvl.credit) for mvl in move_line_ids if mvl.date > closing_date and mvl.od_state =='posted'])
        
        if self.od_manual_cost:
            actual_cost = self.man_actual_cost
        self.od_actual_cost = actual_cost
        self.od_project_cost = project_cost
        self.od_amc_cost = amc_cost
        
    
    @api.one 
    def _get_sale_value(self):
        analytic_id = self.id
        bmn_product_id = self.get_product_id_from_param('product_bmn')
        bmn_exp_product_id = self.get_product_id_from_param('product_bmn_extra_expense')
        omn_product_id = self.get_product_id_from_param('product_omn')
        omn_exp_product_id = self.get_product_id_from_param('product_omn_extra_expense')
        amc_products = [bmn_product_id,bmn_exp_product_id,omn_product_id,omn_exp_product_id]
        sale_order = self.env['sale.order'].search([('project_id','=',analytic_id),('state','!=','cancel')],limit=1)
        amc_sale =0.0
        project_sale =0.0
        actual_sale = 0.0
        project_original_sale =0.0
        amc_original_sale =0.0
        project_original_cost =0.0
        amc_original_cost=0.0
        project_amend_cost =0.0 
        amc_amend_cost =0.0
        project_amend_profit =0.0
        amc_amend_profit =0.0
       
        
        if sale_order:
            for line in sale_order.order_line:
                actual_sale += line.price_subtotal
                
                if (line.product_id.id in amc_products) or (line.od_tab_type == 'amc'):
                    amc_sale += line.price_subtotal
                    amc_original_sale += line.od_original_line_price
                    amc_original_cost += line.od_original_line_cost
                    amc_amend_cost += line.od_amended_line_cost
                else:
                    project_sale += line.price_subtotal
                    project_original_sale += line.od_original_line_price
                    project_original_cost += line.od_original_line_cost
                    project_amend_cost += line.od_amended_line_cost
        
        else:
            for line in self.od_sale_line:
                
                actual_sale += line.price_subtotal 
            
            
            
        
        bim_cost=0.0
        bmn_cost =0.0
        original_bim_profit =0.0
        original_bmn_profit =0.0
        
        project_bmn = self.od_cost_sheet_id and self.od_cost_sheet_id.project_bmn and self.od_cost_sheet_id.project_bmn.id or False
        project_bim = self.od_cost_sheet_id and self.od_cost_sheet_id.project_bim and self.od_cost_sheet_id.project_bim.id or False
        if analytic_id == project_bmn:
            bmn_cost  =self.od_cost_sheet_id and self.od_cost_sheet_id.a_bmn_cost or 0.0
            original_bmn_profit = self.bmn_profit
        if analytic_id == project_bim:
            bim_cost = self.od_cost_sheet_id and self.od_cost_sheet_id.a_bim_cost or 0.0
            original_bim_profit = self.bim_profit 
        
        
        if self.od_manual_input:
            actual_sale = self.man_actual_sale
        
        
        self.od_actual_sale = actual_sale
        self.od_amc_sale = amc_sale 
        self.od_project_sale = project_sale
        self.od_project_amend_sale = project_sale 
        self.od_amc_amend_sale = amc_sale
        self.od_project_amend_cost = project_amend_cost 
        self.od_amc_amend_cost = amc_amend_cost
        self.od_project_amend_profit = bim_cost + project_sale - project_amend_cost
        self.od_amc_amend_profit = bmn_cost + amc_sale - amc_amend_cost    
        
        
        self.od_project_original_sale = project_original_sale 
        self.od_project_original_cost = project_original_cost 
        self.od_project_original_profit = original_bim_profit + project_original_sale -project_original_cost
        
        self.od_amc_original_sale = amc_original_sale 
        self.od_amc_original_cost = amc_original_cost 
        self.od_amc_original_profit = original_bmn_profit + amc_original_sale - amc_original_cost
        
    @api.one
    def _get_outsource_value(self):
        analytic_id = self.id
        move_line_pool = self.env['account.move.line']
        company_id = self.company_id and self.company_id.id 
        wip_account = [False]
        journal_id = False
        hr_pool = self.env['hr.employee']
        emp_ids = hr_pool.sudo().search(['|',('active', '=', True), ('active', '=',False), ('company_id', '=', company_id),('job_id', 'in', (161,162))])
        partner_ids = []
        for employee in emp_ids:
            partner_ids.append(employee.address_home_id.id)
        if company_id ==6:
            wip_account = [5732]
            journal_id =58
            #partner_ids = [13781, 13572, 13623, 12952, 11882, 13076, 13010, 13084]
        if company_id ==1:
            wip_account = [2128,2137]
            journal_id =21
            #partner_ids = [47, 49, 7542, 12757, 13405, 13705]
       
        domain1 = [('partner_id','in',partner_ids),('analytic_account_id','=',analytic_id),('journal_id','=',journal_id),('account_id','in',wip_account)]
        move_line_ids = move_line_pool.search(domain1)
        actual_outsourced = sum([mvl.debit for mvl in move_line_ids if mvl.od_state =='posted'])
        self.od_actual_outsource = actual_outsourced
            
    
    
    @api.one 
    def _get_actual_profit(self):
        timesheet_amount = self.od_timesheet_amount2 or 0.0
        actual_sale = self.od_actual_sale
        actual_profit = actual_sale - self.od_actual_cost
        if actual_sale:
            actual_profit_percent = (actual_profit/float(actual_sale))*100.0
            self.od_actual_profit_percent = actual_profit_percent
        
        self.od_actual_prof = actual_profit
        self.od_actual_profit = actual_profit + timesheet_amount
        self.od_project_profit =  self.od_project_sale - self.od_project_cost 
        self.od_amc_profit =  self.od_amc_sale - self.od_amc_cost 
    
   
    
    def get_amc_yrs(self):
        res =[]
        for i in range(1,6):
            for b in range(1,5):
                res.append(('y'+str(i) +'-' +'q'+str(b),'AMC'+' '+'Y'+str(i) +'-' +'Q'+str(b)))
        return res 
    def get_type_list(self):
        amc_list = self.get_amc_yrs()
        stat_list = [('mat','MAT Supply Only'),('imp','IMP Service Only'),('project','Project (MAT & IMP)'),('trn','TRN'),('credit','Credit')]
        final_list  =  stat_list + amc_list +[('om','O&M')]
        return final_list
    
    
    bim_profit = fields.Float(string="BIM Profit")
    bmn_profit = fields.Float(string="BMN Profit")
    od_actual_cost = fields.Float(string="Actual Cost",compute="_get_cost_from_jv",digits=dp.get_precision('Account'))
    od_actual_sale = fields.Float(string="Actual Sale",compute="_get_sale_value",digits=dp.get_precision('Account'))
    od_actual_outsource = fields.Float(string="Actual Outsourced",compute="_get_outsource_value",digits=dp.get_precision('Account'))
    od_actual_prof = fields.Float(string="Actual Profit",compute="_get_actual_profit",digits=dp.get_precision('Account'))
    od_actual_profit = fields.Float(string="Actual Profit",compute="_get_actual_profit",digits=dp.get_precision('Account'))
    od_actual_profit_percent = fields.Float(string="Actual Profit",compute="_get_actual_profit",digits=dp.get_precision('Account'))
    od_analytic_linked_table = fields.Char(string="Analytic Linked Table")
    od_analytic_pmo_closing = fields.Date(string="Analytic PMO Expected To Close")
    
    od_project_type = fields.Selection(get_type_list,string="Project Type")
    od_project_linked_table = fields.Char(string="Project Linked Table")
    od_project_start = fields.Date(string="Project Start")
    od_project_end = fields.Date(string="Project End")
    od_date_end_original = fields.Date(string="Date End Original")
    od_project_pmo_closing = fields.Date(string="Project PMO Expected To Close")
    od_project_status = fields.Selection([('active','Active'),('inactive','Inactive'),('close','Closed'),('cancel','Cancelled')],string="Project Status",default='inactive',copy=False)
    od_project_owner_id = fields.Many2one('res.users',string="Project Owner")
    od_project_closing = fields.Date(string="Project Closing Date",copy=False)
    od_project_cost = fields.Float(string="Project Cost",compute="_get_cost_from_jv",digits=dp.get_precision('Account'))
    od_project_sale =  fields.Float(string="Project Sale",compute="_get_sale_value",digits=dp.get_precision('Account'))
    od_project_amend_sale =  fields.Float(string="Project Sale Amend",compute="_get_sale_value",digits=dp.get_precision('Account'))
    od_project_amend_cost =  fields.Float(string="Project Cost Amend",compute="_get_sale_value",digits=dp.get_precision('Account'))
    od_project_amend_profit =  fields.Float(string="Project Profit Amend",compute="_get_sale_value",digits=dp.get_precision('Account'))
    od_project_original_sale =  fields.Float(string="Project Sale Amend",compute="_get_sale_value",digits=dp.get_precision('Account'))
    od_project_original_cost =  fields.Float(string="Project Sale Amend",compute="_get_sale_value",digits=dp.get_precision('Account'))
    od_project_original_profit =  fields.Float(string="Project Sale Amend",compute="_get_sale_value",digits=dp.get_precision('Account'))
    od_project_profit = fields.Float(string="Project Profit",compute="_get_actual_profit",digits=dp.get_precision('Account'))
    
    od_amc_type = fields.Selection(get_type_list,string="AMC Type")
    od_amc_linked_table = fields.Char(string="AMC Linked Table")
    od_amc_start = fields.Date(string="AMC Start")
    od_amc_end = fields.Date(string="AMC End")
    od_amc_status = fields.Selection([('active','Active'),('inactive','Inactive'),('close','Closed'),('cancel','Cancelled')],string="Project Status",default='inactive',copy=False)
    od_amc_owner_id = fields.Many2one('res.users',string="AMC Owner")
    od_amc_closing = fields.Date(string="AMC Closing Date",copy=False)
    od_amc_pmo_closing = fields.Date(string="AMC PMO Expected To Close")
    od_amc_cost = fields.Float(string="AMC Cost",compute="_get_cost_from_jv",digits=dp.get_precision('Account'))
    od_amc_sale =  fields.Float(string="AMC Sale",compute="_get_sale_value",digits=dp.get_precision('Account'))
    od_amc_amend_sale =  fields.Float(string="Project Sale Amend",compute="_get_sale_value",digits=dp.get_precision('Account'))
    od_amc_amend_cost =  fields.Float(string="Project Cost Amend",compute="_get_sale_value",digits=dp.get_precision('Account'))
    od_amc_amend_profit =  fields.Float(string="Project Profit Amend",compute="_get_sale_value",digits=dp.get_precision('Account'))
    od_amc_original_sale =  fields.Float(string="Project Sale Amend",compute="_get_sale_value",digits=dp.get_precision('Account'))
    od_amc_original_cost =  fields.Float(string="Project Sale Amend",compute="_get_sale_value",digits=dp.get_precision('Account'))
    od_amc_original_profit =  fields.Float(string="Project Sale Amend",compute="_get_sale_value",digits=dp.get_precision('Account'))
    od_amc_profit = fields.Float(string="AMC Profit",compute="_get_actual_profit",digits=dp.get_precision('Account'))
    
    od_om_start = fields.Date(string="O&M Start")
    od_om_end = fields.Date(string="O&M End")
    od_om_status = fields.Selection([('active','Active'),('inactive','Inactive'),('close','Closed'),('cancel','Cancelled')],string="O&M Status",default='inactive')
    od_om_owner_id = fields.Many2one('res.users',string="OM Owner")
    od_om_closing = fields.Date(string="O&M Closing Date",copy=False)
    od_om_cost = fields.Float(string="O&M Cost",digits=dp.get_precision('Account'))
    od_om_sale =  fields.Float(string="O&M Sale",digits=dp.get_precision('Account'))
    od_om_profit = fields.Float(string="O&M Profit",digits=dp.get_precision('Account'))
    
    
    od_cost_control_kpi = fields.Float(string="Cost Control KPI",compute="_od_get_cost_control_api")
    od_scope_control_kpi = fields.Float(string="Scope Control KPI",compute="_od_get_scope_control_kpi")
    od_manpower_kpi = fields.Float(string="Manpower Cost Control KPI",compute="_get_manpower_cost_control")
    od_timesheet_units = fields.Float(string="Timesheet Units",compute="od_get_timesheet_units")
    od_profit_percent = fields.Float(string="Profit Percentage",compute="od_get_total_sale_value")
    od_original_sale_price = fields.Float(string="Original Sale Price",compute="od_get_total_sale_value",digits=dp.get_precision('Account'))
    od_original_sale_cost = fields.Float(string="Original Sale Cost",compute="od_get_total_sale_value",digits=dp.get_precision('Account'))
    od_original_sale_profit = fields.Float(string="Original Sale Profit",compute="od_get_total_sale_value",digits=dp.get_precision('Account'))
    od_original_mp= fields.Float("Orinal MP",digits=dp.get_precision('Account'))
    od_original_profit = fields.Float(string="Original Sale Profit",compute="od_get_total_sale_value",digits=dp.get_precision('Account'))
    od_original_sale_profit_perc = fields.Float(string="Original Sale Profit Perc",compute="od_get_total_sale_value",digits=dp.get_precision('Account'))
    od_amended_sale_price = fields.Float(string="Amended Sale Price",compute="od_get_total_sale_value",digits=dp.get_precision('Account'))
    od_amended_sale_cost = fields.Float(string="Amended Sale Cost",compute="od_get_total_sale_value",digits=dp.get_precision('Account'))
    od_amended_profit = fields.Float(string="Amended Sale Profit with MP",compute="od_get_total_sale_value",digits=dp.get_precision('Account'))
    od_amended_prof= fields.Float(string="Amended Sale Profit",compute="od_get_total_sale_value",digits=dp.get_precision('Account'))
    od_amended_mp =fields.Float(string="Amended MP",compute="od_get_total_sale_value",digits=dp.get_precision('Account'))
    od_amended_profit_perc = fields.Float(string="Amended Sale Profit Perc",compute="od_get_total_sale_value",digits=dp.get_precision('Account'))
    od_rebate = fields.Float(string="Rebate",compute="od_get_total_sale_value",digits=dp.get_precision('Account'))
    
    od_amended_sale_rg= fields.Float(string="Amended Sale Price")
    od_amended_cost_rg= fields.Float(string="Amended Sale Price")
    
    od_planned_timesheet_cost = fields.Float(string="Planned Timesheet Cost",compute="od_get_total_sale_value")
    od_po_status = fields.Selection([('credit','Customer Credit'),('waiting_po','Waiting P.O'),('special_approval','Special Approval From GM'),('available','Available')],'Customer PO Status',compute="od_get_po_status")
    od_journal_amount_draft = fields.Float(string="Journal Amount Draft",compute="od_get_analytic_journal_amount_draft",digits=dp.get_precision('Account'))
    od_journal_amount = fields.Float(string="Journal Amount",compute="od_get_analytic_journal_amount",digits=dp.get_precision('Account'))
    od_hr_claim_amount = fields.Float(string="Hr Exp Claim Amount",compute="od_get_hr_exp_claim_amount",digits=dp.get_precision('Account'))
    od_hr_claim_amount_draft = fields.Float(string="Hr Exp Claim Amount Draft",compute="od_get_hr_exp_claim_amount_draft")
    od_timesheet_amount = fields.Float(string="Timesheet Amount",compute="od_get_timesheet_amount",digits=dp.get_precision('Account'))
    od_timesheet_amount2 = fields.Float(string="Timesheet Amount",compute="od_get_timesheet_amount",digits=dp.get_precision('Account'))
    od_owner_id = fields.Many2one('res.users',string="Owner",required=False)
    od_sale_count = fields.Integer(string="Sale Count",compute="od_get_sales_order_count")
    od_meeting_count = fields.Integer(string="Meeting Count",compute="_od_meeting_count")
    od_amnt_invoiced = fields.Float(string="Customer Invoice Amount",compute="od_get_total_invoice",digits=dp.get_precision('Account'))
    od_amnt_invoiced2 = fields.Float(string="Customer Invoice Amount",compute="od_get_total_invoice",digits=dp.get_precision('Account'))
    count_change_mgmt = fields.Integer(string="Change Management Count",compute="od_get_no_of_change_mgmt")
    
    
    
    
    @api.one
    def od_get_cust_refund(self):
        analytic_id = self.id
        invoice_pool = self.env['account.invoice']
        domain = [('od_analytic_account','=',analytic_id),('type','=','out_refund'),('state','not in',('draft','cancel'))]
        inv_ids = invoice_pool.search(domain)
        amount_total = sum([inv.amount_total for inv in inv_ids])
        self.od_cust_refund_amt = amount_total
       
    
    @api.multi
    def od_btn_open_customer_refund(self):
        analytic_id = self.id
        invoice_pool = self.env['account.invoice']
        domain = [('od_analytic_account','=',analytic_id),('type','=','out_refund')]
        inv_ids = invoice_pool.search(domain)
        inv_li_ids = [inv.id for inv in inv_ids]
        dom = [('id','in',inv_li_ids)]
        
        model_data = self.env['ir.model.data']
        tree_view = model_data.get_object_reference('account', 'invoice_tree')
        form_view = model_data.get_object_reference('account', 'invoice_form')
        
        return {
            'domain':dom,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice',
            'views': [ (tree_view and tree_view[1] or False, 'tree'),(form_view and form_view[1] or False, 'form'),],
            'type': 'ir.actions.act_window',
        }
    
    @api.one
    def od_get_sup_inv_amnt(self):
        analytic_id = self.id
        invoice_pool = self.env['account.invoice']
        domain = [('od_analytic_account','=',analytic_id),('type','=','in_invoice'),('state','not in',('draft','cancel'))]
        inv_ids = invoice_pool.search(domain)
        amount_total =0.0
        for inv in inv_ids:
            currency = inv.currency_id
            company_currency = inv.company_id.currency_id
            amount = currency.compute(inv.amount_total,company_currency,round=False)
            amount_total += amount
        
        self.od_sup_inv_amt = amount_total
       
    
    @api.multi
    def od_btn_open_sup_invoice(self):
        analytic_id = self.id
        invoice_pool = self.env['account.invoice']
        domain = [('od_analytic_account','=',analytic_id),('type','=','in_invoice')]
        inv_ids = invoice_pool.search(domain)
        inv_li_ids = [inv.id for inv in inv_ids]
        dom = [('id','in',inv_li_ids)]
        return {
            'domain':dom,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice',
            'type': 'ir.actions.act_window',
        }
    
    
    @api.one
    def od_get_sup_refund_amnt(self):
        analytic_id = self.id
        invoice_pool = self.env['account.invoice']
        domain = [('od_analytic_account','=',analytic_id),('type','=','in_refund'),('state','not in',('draft','cancel'))]
        inv_ids = invoice_pool.search(domain)
        amount_total = sum([inv.amount_total for inv in inv_ids])
        self.od_sup_refund_amt = amount_total
       
    
    @api.multi
    def od_btn_open_sup_refund(self):
        analytic_id = self.id
        invoice_pool = self.env['account.invoice']
        domain = [('od_analytic_account','=',analytic_id),('type','=','in_refund')]
        inv_ids = invoice_pool.search(domain)
        inv_li_ids = [inv.id for inv in inv_ids]
        dom = [('id','in',inv_li_ids)]
        return {
            'domain':dom,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice',
            'type': 'ir.actions.act_window',
        }
    
    
    
    
    od_cust_refund_amt = fields.Float(string="Customer Refund Amount",compute="od_get_cust_refund",digits=dp.get_precision('Account'))
    od_sup_inv_amt = fields.Float(string="Supplier Invoice Amount",compute="od_get_sup_inv_amnt",digits=dp.get_precision('Account'))
    od_sup_refund_amt = fields.Float(string="Supplier Invoice Amount",compute="od_get_sup_refund_amnt",digits=dp.get_precision('Account'))
    od_amnt_purchased = fields.Float(string="Supplier Purchase Amount",compute="od_get_total_purchase",digits=dp.get_precision('Account'))
    od_amnt_purchased2 = fields.Float(string="Supplier Purchase Amount",compute="od_get_total_purchase",digits=dp.get_precision('Account'))
    
    
    def get_day_procss_score(self):
        res =0.0
        cost_sheet_id = self.od_cost_sheet_id
        if cost_sheet_id:
            owner_kpi = cost_sheet_id.owner_kpi 
            if owner_kpi == 'ok':
                res =100.0
        return res
    
    
    def get_invoice_amounts(self):
    
        invoice_ids = self.env['account.invoice'].search([('od_analytic_account','=',self.id),('state','in',('open','paid'))])
        inv_amount =0.0
        for inv in invoice_ids:
            inv_amount+=inv.amount_total
        return inv_amount
    
    def get_x_days(self,date_start,date_end):
        fromdate = datetime.strptime(date_start, DEFAULT_SERVER_DATE_FORMAT)
        todate = datetime.strptime(date_end, DEFAULT_SERVER_DATE_FORMAT)
        daygenerator = (fromdate + timedelta(x + 1) for x in xrange((todate - fromdate).days))
        days =sum(1 for day in daygenerator)
        days = days+1
        return days  
    
    
    def get_avg_score(self,score_board):
        avg_score =0.0
        if score_board:
            avg_score =sum(score_board)/float(len(score_board))
        return avg_score
    def get_invoice_schedule_score(self):
        result =0.0
        type = self.od_type_of_project
        planned_amount = 0.0
        today = str(dt.today())
        score_board =[]
        if type not in ('credit','amc','o_m'):
            for line in self.od_project_invoice_schedule_line:
                date =line.date 
                if date <= today:
                    invoice = line.invoice_id 
                    planned_amount = line.amount 
                    invoice_amount = line.invoice_amount 
                    if planned_amount <invoice_amount:
                        score =0.0
                        score_board.append(score)
                        continue
                    if invoice and invoice.state in ('open','paid','accept'):
                        cust_date = invoice.cust_date 
                        score = 0.0
                        if cust_date <= date:
                            score = 100.0
                        score_board.append(score)
        avg_score = self.get_avg_score(score_board)
        return avg_score
#     def get_cost_control_score(self):
#         result =0.0
#         actual_profit = self.od_project_profit
#         original_profit = self.od_project_original_profit 
#         if original_profit:
#             result = (actual_profit/original_profit) * 100 
#         if original_profit <=0.0 and actual_profit >0.0:
#             result =100.0
#         return result
    
    def get_cost_control_score(self):
        result =0.0
        original_cost = self.od_project_original_cost
        actual_cost = self.od_project_cost
        if actual_cost:
            result = (original_cost/actual_cost) * 100 
        else:
            result =100.0
        return result
    
    
    
    def get_avg_score_board(self,score_board):
        result =0.0
        if score_board:
            result = sum(score_board)/float(len(score_board))
        return result
    def get_compliance_score(self):
        score_board =[]
        
        score = [x.score for x in self.od_comp_planning_line if x.add_score]
        score_board.extend(score)
        
        score = [x.score for x in self.od_comp_initiation_line if x.add_score]
        score_board.extend(score)
        
        score = [x.score for x in self.od_comp_excecution_line if x.add_score]
        score_board.extend(score)
        
        score = [x.score for x in self.od_comp_monitor_line if x.add_score]
        score_board.extend(score)    
        
        score = [x.score for x in self.od_comp_closing_line if x.add_score]
        score_board.extend(score)
        if self.od_type_of_project == 'amc':
            score_board =[]
            score = [x.score for x in self.od_comp_handover_line if x.add_score]
            score_board.extend(score)
            
            score = [x.score for x in self.od_comp_maint_line if x.add_score]
            score_board.extend(score)
        result = self.get_avg_score_board(score_board)
        return result
    
    def get_schedule_control_score(self):
        result =0.0
        project_planned_end = self.od_project_end 
        closed_date = self.od_project_closing 
        if closed_date <= project_planned_end:
            result =100.0
        return result
            
        
    
    
    @api.one
    def _kpi_score(self):
        
        day_process_score = .1 *self.get_day_procss_score()
        invoice_schedule_score =  .3 *self.get_invoice_schedule_score()
        cost_control_score = .2 * self.get_cost_control_score()
        compliance_score = .1 * self.get_compliance_score()
        schedule_control_score = .3 * self.get_schedule_control_score()
        
           
#         day_process_score = .1 *self.get_day_procss_score()
#         invoice_schedule_score =  .3 *self.get_invoice_schedule_score()
#         cost_control_score = .1 * self.get_cost_control_score()
#         compliance_score = .1 * self.get_compliance_score()
#         schedule_control_score = self.get_schedule_control_score()
        
        
        total_score = day_process_score + invoice_schedule_score + cost_control_score+ compliance_score + schedule_control_score
        self.day_process_score = day_process_score 
        self.invoice_schedule_score = invoice_schedule_score 
        self.cost_control_score = cost_control_score 
        self.compliance_score = compliance_score 
        self.schedule_control_score = schedule_control_score
        self.total_score = total_score
    day_process_score = fields.Float(string="Day Process Score",compute="_kpi_score")
    invoice_schedule_score = fields.Float(string="Invoice Schedule Score",compute="_kpi_score")
    cost_control_score = fields.Float(string="Cost Control Score",compute="_kpi_score")
    compliance_score = fields.Float(string="Compliance Score",compute="_kpi_score")
    total_score = fields.Float(string="Total Score",compute="_kpi_score")
    schedule_control_score = fields.Float(string="Compliance Score",compute="_kpi_score")
    
    
    
        

    
    
    def get_initiation_line(self):
        data = [
            (0,0,{'name':'Project Charter'}),
            (0,0,{'name':'Sales Handover'}),
            
            ]
        return data
    
    def get_planning_line(self):
        data = [
            (0,0,{'name':'High Level Design (HLD) & Its Approval'}),
            (0,0,{'name':'Project Scope Document & Its Approval'}),
            (0,0,{'name':'Low Level Design (LLD) & Its Approval'}),
            (0,0,{'name':'Project Plan & Its Approval'}),
            (0,0,{'name':'Migration Plans & Their Approvals'}),
            (0,0,{'name':'User Acceptance Test Document (UAT) & Its Approval'}),
            (0,0,{'name':'Technical Drawings'}),
            ]
        return data
    def get_execution_line(self):
        data = [
            (0,0,{'name':' Customer Invoices'}),
            (0,0,{'name':'Delivery Notes'}),
            (0,0,{'name':'Supplier Purchases'}),
            (0,0,{'name':'Correspondence'}),
           
            ]
        return data
    
    def get_monitor_line(self):
        data = [
            (0,0,{'name':'Change Management (Change Requests)'}),
            (0,0,{'name':'Project Logs (Issues & Risks)'}),
            (0,0,{'name':'Progress / Status Reports'}),
            (0,0,{'name':'Updated Project Plans'}),
           
            ]
        return data
    
    def get_closing_line(self):
        data = [
            (0,0,{'name':'Completion Certificates'}),
            (0,0,{'name':'Final Project Documentation'}),
            (0,0,{'name':'Serial Numbers'}),
            (0,0,{'name':'Backup Configuration'}),
            (0,0,{'name':'Lessons Learn'}),
            (0,0,{'name':'Handover to Service Desk (Signed SLA)'}),
           
            ]
        return data
    
    def get_handover_line(self):
        data = [
            (0,0,{'name':'Final Project Documentation'}),
            (0,0,{'name':'Serial Numbers'}),
            (0,0,{'name':'Backup Configuration'}),
            (0,0,{'name':'Signed SLA'}),
           
           
            ]
        return data
    
    def get_maint_line(self):
        data = [
            (0,0,{'name':'Reports (Preventive, RMA, etc.)'}),
            (0,0,{'name':'Issue Updates'}),
            ]
        return data
    start_project_comp = fields.Boolean(string="Start Project Compliance")
    start_amc_comp = fields.Boolean(string="Start AMC Compliance")
    od_comp_initiation_line  = fields.One2many('od.compliance.initiation','analytic_id',string="Detail Line",default=get_initiation_line)
    od_comp_planning_line  = fields.One2many('od.compliance.planning','analytic_id',string="Detail Line",default=get_planning_line)
    od_comp_excecution_line  = fields.One2many('od.compliance.execution','analytic_id',string="Detail Line",default=get_execution_line)
    od_comp_monitor_line  = fields.One2many('od.compliance.monitor','analytic_id',string="Detail Line",default=get_monitor_line)
    od_comp_closing_line  = fields.One2many('od.compliance.closing','analytic_id',string="Detail Line",default=get_closing_line)
    od_comp_handover_line  = fields.One2many('od.compliance.handover','analytic_id',string="Detail Line",default=get_handover_line)
    od_comp_maint_line  = fields.One2many('od.compliance.maint','analytic_id',string="Detail Line",default=get_maint_line)
    preventive_maint_line = fields.One2many('preventive.maint.schedule','analytic_id',string="Detail Line")
    
    od_proj_resol_time_ctc = fields.Float(digits=(16,2))
    od_proj_resol_time_maj = fields.Float(digits=(16,2))
    od_proj_resol_time_min = fields.Float(digits=(16,2))
    od_proj_respons_time_ctc = fields.Float(digits=(16,2))
    od_proj_respons_time_maj = fields.Float(digits=(16,2))
    od_proj_respons_time_min = fields.Float(digits=(16,2))
   
    

class od_compliance_initiation(models.Model):
    _name = "od.compliance.initiation"
    analytic_id  = fields.Many2one('account.analytic.account',string="Analytic Account")
    name = fields.Char(string="Name",required=True)
    add_score = fields.Boolean(string="Add Score")
    score = fields.Float(string="Score")
class od_compliance_planning(models.Model):
    _name = "od.compliance.planning"
    analytic_id  = fields.Many2one('account.analytic.account',string="Analytic Account")
    name = fields.Char(string="Name",required=True)
    score = fields.Float(string="Score")
    add_score = fields.Boolean(string="Add Score")
class od_compliance_execution(models.Model):
    _name = "od.compliance.execution"
    analytic_id  = fields.Many2one('account.analytic.account',string="Analytic Account")
    name = fields.Char(string="Name",required=True)
    score = fields.Float(string="Score")
    add_score = fields.Boolean(string="Add Score")
class od_compliance_monitor(models.Model):
    _name = "od.compliance.monitor"
    analytic_id  = fields.Many2one('account.analytic.account',string="Analytic Account")
    name = fields.Char(string="Name",required=True)
    score = fields.Float(string="Score")
    add_score = fields.Boolean(string="Add Score")
class od_compliance_closing(models.Model):
    _name = "od.compliance.closing"
    analytic_id  = fields.Many2one('account.analytic.account',string="Analytic Account")
    name = fields.Char(string="Name",required=True)
    score = fields.Float(string="Score")
    add_score = fields.Boolean(string="Add Score")
class od_compliance_handover(models.Model):
    _name = "od.compliance.handover"
    analytic_id  = fields.Many2one('account.analytic.account',string="Analytic Account")
    name = fields.Char(string="Name",required=True)
    score = fields.Float(string="Score")
    add_score = fields.Boolean(string="Add Score")
class od_compliance_maint(models.Model):
    _name = "od.compliance.maint"
    analytic_id  = fields.Many2one('account.analytic.account',string="Analytic Account")
    name = fields.Char(string="Name",required=True)
    score = fields.Float(string="Score")
    add_score = fields.Boolean(string="Add Score")



class od_analytic_invoice_dist(models.Model):
    _name = 'od.analytic.invoice.dist'
    
    @api.one
    @api.depends('invoice_percent','invoice_amt') 
    def _get_current_inv_amount(self):
        invoice_amount = self.invoice_amt 
        invoice_percent = self.invoice_percent 
        self.current_inv_planned = invoice_amount *(invoice_percent/100.0)
    
    @api.one 
    def _get_sale_value(self):
        self.sale_value =self.share_analytic_id and self.share_analytic_id.od_amended_sale_price
    @api.one
    def _get_invoice_allocated(self):
        self.invoice_allocated = self.share_analytic_id and self.share_analytic_id.invoice_planned
    
    @api.one
    def _get_invoice_accepted(self):
        self.invoice_accepted = self.share_analytic_id and self.share_analytic_id.invoice_accepted 
         
         
#         self.invoice_allocated = self.share_analytic_id and self.share_analytic_id.invoice_planned 
#         self.invoice_accepted = self.share_analytic_id and self.share_analytic_id.invoice_accepted 
    
#     @api.one 
#     def _get_invoice_allocated(self):
#         analytic_id = self.share_analytic_id and self.share_analytic_id.id
#         dist_line = self.env['od.analytic.invoice.dist']
#         dist_data=dist_line.search([('share_analytic_id','=',analytic_id)])
#         planned_amount =0.0
#         inv_accepted =0.0
#         print "analytic id>>>>>>>>>>>>>",analytic_id,dist_line
#         for dist in dist_data:
#             invoice_percent = dist.invoice_percent 
#             invoice_amount = dist.invoice_amt
#             planned_amount +=invoice_amount * (invoice_percent/100.0)
#             print "planned amount",planned_amount
#             invoice_status =  dist.invoice_root_id and dist.invoice_root_id.state 
#             if invoice_status in ('accept','paid'):
#                 inv_accepted +=invoice_amount * (invoice_percent/100.0)
# #         self.invoice_accepted = inv_accepted 
#         self.invoice_allocated = planned_amount 
    
    invoice_root_id  = fields.Many2one('od.analytic.root.invoice.schedule',string="Analytic Account",ondelete="cascade")
    name =fields.Char(string="Name")
    
    invoice_percent = fields.Float(string="Invoice Percent")
    current_inv_planned  =fields.Float(string="Current Invoice Planning",compute="_get_current_inv_amount")
    invoice_allocated = fields.Float(string="Invoice Planned",compute='_get_invoice_allocated')
    invoice_accepted = fields.Float(string="Invoice Accepted",compute="_get_invoice_accepted")
    sale_value = fields.Float(string="Order Value",compute='_get_sale_value')
    invoice_amt = fields.Float(string="Total Invoice Amount")
    share_analytic_id = fields.Many2one('account.analytic.account',string="Analytic Account")
    applied =fields.Boolean(string="Applied")
    

  
class od_analytic_root_invoice_schedule(models.Model):
    
    _name = "od.analytic.root.invoice.schedule"
    
    analytic_id  = fields.Many2one('account.analytic.account',string="Analytic Account")
    
    child_analytic_id =fields.Many2one('account.analytic.account',string="Analytic Account")
    name = fields.Char(string="Name",required=False)
    
    date = fields.Date(string="Planned Date",required=True)
    pmo_date = fields.Date(string="PMO Expected Invoice Date")
    invoice_id = fields.Many2one('account.invoice',string="Invoice")
    amount = fields.Float(string="Planned Amount",required=True)
    invoice_percentage = fields.Float(string="Invoice Percentage")
    invoice_amount = fields.Float(string="Invoice Amount",related="invoice_id.amount_total",readonly=True,store=True)
    date_invoice = fields.Date(string="Invoice Date",related="invoice_id.date_invoice",readonly=True,store=True)
    invoice_status = fields.Selection([('draft','Draft'),('proforma','Pro-forma'),('proforma2','Pro-forma'),('open','Open'),('accept','Accepted By Customer'),('paid','Paid'),('cancel','Cancelled')],related="invoice_id.state",raeadonly=True,string="Invoice Status",store=True)
    cust_date = fields.Date(string="Customer Accepted Date",related="invoice_id.cust_date",readonly=True,store=True)
    invoice_dist_line = fields.One2many('od.analytic.invoice.dist','invoice_root_id',string="Invoice Distribute")
    project_inv_sch_id = fields.Many2one('od.project.invoice.schedule',string="Project Invoice Schedule")
    amc_inv_sch_id = fields.Many2one('od.amc.invoice.schedule',string="AMC Invoice Schedule")
    om_inv_sch_id = fields.Many2one('od.om.invoice.schedule',string="OM Invoice Schedule")
    
    
    
    def inv_sch_create(self,vals):
        if vals.get('child_analytic_id'):
            a_id = vals.get('child_analytic_id')
            a_ob=self.env['account.analytic.account'].browse(a_id)
            type_of_project = a_ob.od_type_of_project
            p_vals = vals.copy()
            if type_of_project in ('amc'):
                p_vals['analytic_id'] = a_id 
                amc_inv_sch= self.env['od.amc.invoice.schedule'].create(p_vals)
                amc_inv_sch_id =amc_inv_sch.id
                vals['amc_inv_sch_id'] =amc_inv_sch_id
#             elif type_of_project in ('o_m'):
#                 p_vals['analytic_id'] = a_id 
#                 amc_inv_sch= self.env['od.om.invoice.schedule'].create(p_vals)
#                 amc_inv_sch_id =amc_inv_sch.id
#                 vals['om_inv_sch_id'] =amc_inv_sch_id
            else: 
                p_vals['analytic_id'] = a_id 
                amc_inv_sch= self.env['od.project.invoice.schedule'].create(p_vals)
                amc_inv_sch_id =amc_inv_sch.id
                vals['project_inv_sch_id'] =amc_inv_sch_id
        
    @api.model 
    def create(self,vals):
        self.inv_sch_create(vals)
        return super(od_analytic_root_invoice_schedule, self).create(vals)
    @api.multi
    def write(self,vals):
        
        r_vals ={}
        r_vals['name'] = vals.get('name') or self.name 
        r_vals['date'] = vals.get('date') or self.date
        r_vals['pmo_date'] = vals.get('pmo_date') or self.pmo_date
        r_vals['amount'] = vals.get('amount') or self.amount 
        r_vals['invoice_percentage'] = vals.get('invoice_percentage') or self.invoice_percentage 
        project_inv_sch_id = self.project_inv_sch_id and self.project_inv_sch_id.id or False
        amc_inv_sch_id = self.amc_inv_sch_id and self.amc_inv_sch_id.id or False
#         om_inv_sch_id = self.om_inv_sch_id and self.om_inv_sch_id.id or False
        if vals.get('child_analytic_id'):
            r_vals['analytic_id'] =vals.get('child_analytic_id')
           
            self.inv_sch_create(r_vals)
        if project_inv_sch_id:
            a_id = self.child_analytic_id and self.child_analytic_id.id
            r_vals['analytic_id'] = a_id 
            obj= self.env['od.project.invoice.schedule'].browse(project_inv_sch_id)
            obj.write(r_vals)
        if amc_inv_sch_id:
            a_id = self.child_analytic_id and self.child_analytic_id.id
            r_vals['analytic_id'] = a_id 
            obj= self.env['od.amc.invoice.schedule'].browse(amc_inv_sch_id)
            obj.write(r_vals)
        
#         if om_inv_sch_id:
#             a_id = self.child_analytic_id and self.child_analytic_id.id
#             r_vals['analytic_id'] = a_id 
#             obj= self.env['od.om.invoice.schedule'].browse(om_inv_sch_id)
#             obj.write(r_vals)
        return super(od_analytic_root_invoice_schedule, self).write(vals)
            
            
            
            
            
        
    
    @api.multi 
    def apply_dist(self):
        for line in self.invoice_dist_line:
            if line.current_inv_planned + line.invoice_allocated > line.sale_value:
                raise Warning("You Cant Plan More than Order Value")
            line.write({'applied':True})
            share_analytic_id = line.share_analytic_id
            share_analytic_id.write({'share_invoice':True})
    
    
    def _prepare_invoice_line(self, cr, uid, line,analytic_id, fiscal_position=False, context=None):
        fpos_obj = self.pool.get('account.fiscal.position')
        res = line.product_id
        account_id = res.property_account_income.id
        if not account_id:
            account_id = res.categ_id.property_account_income_categ.id
        account_id = fpos_obj.map_account(cr, uid, fiscal_position, account_id)

        taxes = line.tax_id or False
        tax_id = fpos_obj.map_tax(cr, uid, fiscal_position, taxes, context=context)
        values = {
            'name': line.name,
            'account_id': account_id,
            'account_analytic_id': analytic_id ,
            
            'price_unit': line.price_unit or 0.0,
            'quantity': line.product_uom_qty,
            'uos_id': line.product_uom.id or False,
            'product_id': line.product_id.id or False,
            'invoice_line_tax_id': [(6, 0, tax_id)],
        }
        return values
    
    
    def _check_od_analytic_invoice_project_amount(self,analytic,amount):
        """ Ensure the Invoice Amount Not Greater than Project Value"""
        if analytic:
            analytic_id  = analytic.id
            invoice_except =  analytic and analytic.od_create_inv_except
#             if not invoice_except:
#                 project_amount = analytic and analytic.od_amended_sale_price 
#                 already_invoiced  = self.env['account.invoice'].search([('od_analytic_account','=',analytic_id),('type','=','out_invoice'),('state','in',('accept','paid'))])
#                 already_invoiced_amt = sum([inv.amount_untaxed for inv in already_invoiced])  
#                 customer_refund = self.env['account.invoice'].search([('od_analytic_account','=',analytic_id),('type','=','out_refund'),('state','not in',('draft','cancel'))])
#                 customer_refund_amount = sum([inv.amount_untaxed for inv in customer_refund])
#                 current_inv_amount = amount
#                 collected = already_invoiced_amt + current_inv_amount -customer_refund_amount
#                 difference = collected - project_amount
#                 if difference > 1.0:
#                     raise Warning("Invoice Value Cannot Be Greater Than Project Value,Kindly Contact Admin")
           
                
    
    
    
    def od_create_invoice(self):
        invoice_amount =0.0
        analytic_pool =self.env['account.analytic.account']
        analytic_id = self.analytic_id and self.analytic_id.id or False
#         self._check_od_analytic_invoice_project_amount(self.analytic_id,self.amount)
        cr = self.env.cr
        uid = self.env.uid
        inv_line_vals =[]
        od_cost_sheet_id = self.analytic_id and self.analytic_id.od_cost_sheet_id and self.analytic_id.od_cost_sheet_id.id or False 
        od_branch_id  = self.analytic_id and self.analytic_id.od_branch_id and self.analytic_id.od_branch_id.id or False 
        od_cost_centre_id = self.analytic_id and self.analytic_id.od_cost_centre_id and self.analytic_id.od_cost_centre_id.id or False 
        od_division_id = self.analytic_id and self.analytic_id.od_division_id and self.analytic_id.od_division_id.id or False
        bt_po_ref = self.analytic_id and self.analytic_id.od_cost_sheet_id and self.analytic_id.od_cost_sheet_id.part_ref
        
        analytic_ids = analytic_pool.search([('parent_id','=',analytic_id),('type','=','contract')])
        grand_child_ids =analytic_pool.search([('grand_parent_id','=',analytic_id),('type','=','contract')])
        analytics = analytic_ids + grand_child_ids
        pr_ids = [an.id for an in analytics]
        
        if self.invoice_id:
            invoice_amount = self.invoice_id.amount_total
        
        if analytic_id and not self.invoice_id:
            so_ids = self.env['sale.order'].search([('project_id','in',pr_ids),('state','!=','cancel')])
#             if not so_id:
#                 parent_analytic_id = self.analytic_id and self.analytic_id.parent_id and  self.analytic_id.parent_id.id
#                 if parent_analytic_id:
#                     so_id = self.env['sale.order'].search([('project_id','=',parent_analytic_id),('state','!=','cancel')],limit=1)
            so_id = so_ids and so_ids[0]
            print "so ids>>>>>>>>>>>>>>>>>>>",so_ids,so_id
            inv_vals =  self.pool.get('sale.order')._prepare_invoice(cr,uid,so_id,[])
            inv_vals['date_invoice'] =str(dt.today())
            inv_vals.update({
                'od_analytic_account':analytic_id,
                'od_cost_sheet_id':od_cost_sheet_id,
                'od_branch_id':od_branch_id,
                'od_cost_centre_id':od_cost_centre_id,
                'od_division_id':od_division_id,
                'od_costing':False,
                'bt_po_ref':bt_po_ref,
                'od_inter_inc_acc_id':so_id.od_order_type_id and so_id.od_order_type_id.income_acc_id and so_id.od_order_type_id.income_acc_id.id,
                'od_inter_exp_acc_id':so_id.od_order_type_id and so_id.od_order_type_id.expense_acc_id and so_id.od_order_type_id.expense_acc_id.id,
                })
            for so_id in so_ids:
                for line in so_id.order_line:
#                     analytic_id = so_id.project_id and so_id.project_id.id
                    analytic_id = line.od_analytic_acc_id and line.od_analytic_acc_id.id or False
                    if not analytic_id:
                        analytic_id = so_id.project_id and so_id.project_id.id
                        
                    vals = self._prepare_invoice_line(line,analytic_id) 
                    inv_line_vals.append((0,0,vals))
            inv_vals['invoice_line'] = inv_line_vals
            inv =self.env['account.invoice'].create(inv_vals)
            inv.button_compute()
            self.invoice_id = inv.id
            invoice_amount = inv and inv.amount_total or 0.0
        return invoice_amount
    
    @api.multi 
    def create_invoice(self):
        analytic_pool =self.env['account.analytic.account']
        analytic_id = self.analytic_id and self.analytic_id.id or False
#         self._check_od_analytic_invoice_project_amount(self.analytic_id,self.amount)
        cr = self.env.cr
        uid = self.env.uid
        inv_line_vals =[]
        od_cost_sheet_id = self.analytic_id and self.analytic_id.od_cost_sheet_id and self.analytic_id.od_cost_sheet_id.id or False 
        od_branch_id  = self.analytic_id and self.analytic_id.od_branch_id and self.analytic_id.od_branch_id.id or False 
        od_cost_centre_id = self.analytic_id and self.analytic_id.od_cost_centre_id and self.analytic_id.od_cost_centre_id.id or False 
        od_division_id = self.analytic_id and self.analytic_id.od_division_id and self.analytic_id.od_division_id.id or False 
        bt_po_ref = self.analytic_id and self.analytic_id.od_cost_sheet_id and self.analytic_id.od_cost_sheet_id.part_ref
        
        analytic_ids = analytic_pool.search([('parent_id','=',analytic_id),('type','=','contract')])
        grand_child_ids =analytic_pool.search([('grand_parent_id','=',analytic_id),('type','=','contract')])
        analytics = analytic_ids + grand_child_ids
        pr_ids = [an.id for an in analytics]
        
        
        if analytic_id and not self.invoice_id:
            so_ids = self.env['sale.order'].search([('project_id','in',pr_ids),('state','!=','cancel')])
#             if not so_id:
#                 parent_analytic_id = self.analytic_id and self.analytic_id.parent_id and  self.analytic_id.parent_id.id
#                 if parent_analytic_id:
#                     so_id = self.env['sale.order'].search([('project_id','=',parent_analytic_id),('state','!=','cancel')],limit=1)
            so_id = so_ids and so_ids[0]
            print "so ids>>>>>>>>>>>>>>>>>>>",so_ids,so_id
            inv_vals =  self.pool.get('sale.order')._prepare_invoice(cr,uid,so_id,[])
            inv_vals['date_invoice'] =str(dt.today())
            inv_vals.update({
                'od_analytic_account':analytic_id,
                'od_cost_sheet_id':od_cost_sheet_id,
                'od_branch_id':od_branch_id,
                'od_cost_centre_id':od_cost_centre_id,
                'od_division_id':od_division_id,
                'bt_po_ref':bt_po_ref,
                'od_costing':False,
                'od_inter_inc_acc_id':so_id.od_order_type_id and so_id.od_order_type_id.income_acc_id and so_id.od_order_type_id.income_acc_id.id,
                'od_inter_exp_acc_id':so_id.od_order_type_id and so_id.od_order_type_id.expense_acc_id and so_id.od_order_type_id.expense_acc_id.id,
                })
            for so_id in so_ids:
                for line in so_id.order_line:
#                     analytic_id = so_id.project_id and so_id.project_id.id
                    analytic_id = line.od_analytic_acc_id and line.od_analytic_acc_id.id or False
                    if not analytic_id:
                        analytic_id = so_id.project_id and so_id.project_id.id
                    vals = self._prepare_invoice_line(line,analytic_id) 
                    inv_line_vals.append((0,0,vals))
            inv_vals['invoice_line'] = inv_line_vals
            inv =self.env['account.invoice'].create(inv_vals)
            inv.button_compute()
            self.invoice_id = inv.id
            model_data = self.env['ir.model.data']
            tree_view = model_data.get_object_reference('account', 'invoice_tree')
            form_view = model_data.get_object_reference('account', 'invoice_form')
            return {
                'res_id':inv.id,
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.invoice',
                'views': [(form_view and form_view[1] or False, 'form'),(tree_view and tree_view[1] or False, 'tree')], 
                'type': 'ir.actions.act_window',
            }
        return True
                                   
    @api.multi 
    def btn_open_inv_dist_view(self):
        analytic_pool =self.env['account.analytic.account']
        invoice_amount = self.od_create_invoice()
        if not self.invoice_dist_line:
            analytic_id = self.analytic_id and self.analytic_id.id or False
            analytic_ids = analytic_pool.search([('parent_id','=',analytic_id),('type','=','contract')])
            grand_child_ids =analytic_pool.search([('grand_parent_id','=',analytic_id),('type','=','contract')])
            analytics = analytic_ids + grand_child_ids
            res = [{'share_analytic_id':an.id,'invoice_amt':invoice_amount,'invoice_allocated':an.invoice_planned,'invoice_accepted':an.invoice_accepted} for an in analytics]
            self.invoice_dist_line  = res
            
        invoice_dist_pool = self.env['od.analytic.root.invoice.schedule']
        
        return {
                'res_id':self.id,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'od.analytic.root.invoice.schedule',
                'type': 'ir.actions.act_window',
                'target': 'new',
 
            }                            
                            
                                        

class od_project_invoice_schedule(models.Model):
    _name = "od.project.invoice.schedule"
    
    def od_get_company_id(self):
        return self.env.user.company_id
    
    analytic_id  = fields.Many2one('account.analytic.account',string="Analytic Account")
    name = fields.Char(string="Name",required=False)
    date = fields.Date(string="Planned Date",required=False)
    pmo_date = fields.Date(string="PMO Expected Invoice Date")
    finance_date = fields.Date(string="Finance Expected Invoice Date")
    invoice_id = fields.Many2one('account.invoice',string="Invoice")
    amount = fields.Float(string="Planned Amount",required=False)
    invoice_amount = fields.Float(string="Invoice Amount",related="invoice_id.amount_total",readonly=True,store=True)
    date_invoice = fields.Date(string="Invoice Date",related="invoice_id.date_invoice",readonly=True,store=True)
    invoice_status = fields.Selection([('draft','Draft'),('proforma','Pro-forma'),('proforma2','Pro-forma'),('open','Open'),('accept','Accepted By Customer'),('paid','Paid'),('cancel','Cancelled')],related="invoice_id.state",raeadonly=True,string="Invoice Status",store=True)
    cust_date = fields.Date(string="Customer Accepted Date",related="invoice_id.cust_date",readonly=True,store=True)
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id,readonly=True)
    
    def _prepare_invoice_line(self, cr, uid, line,analytic_id, fiscal_position=False, context=None):
        fpos_obj = self.pool.get('account.fiscal.position')
        res = line.product_id
        account_id = res.property_account_income.id
        if not account_id:
            account_id = res.categ_id.property_account_income_categ.id
        account_id = fpos_obj.map_account(cr, uid, fiscal_position, account_id)

        taxes = line.tax_id or False
        tax_id = fpos_obj.map_tax(cr, uid, fiscal_position, taxes, context=context)
        values = {
            'name': line.name,
            'account_id': account_id,
            'account_analytic_id': analytic_id,
            'price_unit': line.price_unit or 0.0,
            'quantity': line.product_uom_qty,
            'uos_id': line.product_uom.id or False,
            'product_id': line.product_id.id or False,
            'invoice_line_tax_id': [(6, 0, tax_id)],
            
        }
        return values
    
    
    def _check_od_analytic_invoice_project_amount(self,analytic,amount):
        """ Ensure the Invoice Amount Not Greater than Project Value"""
        if analytic:
            analytic_id  = analytic.id
            invoice_except =  analytic and analytic.od_create_inv_except
            if not invoice_except:
                project_amount = analytic and analytic.od_amended_sale_price 
                already_invoiced  = self.env['account.invoice'].search([('od_analytic_account','=',analytic_id),('type','=','out_invoice'),('state','in',('accept','paid'))])
                already_invoiced_amt = sum([inv.amount_untaxed for inv in already_invoiced])  
                customer_refund = self.env['account.invoice'].search([('od_analytic_account','=',analytic_id),('type','=','out_refund'),('state','not in',('draft','cancel'))])
                customer_refund_amount = sum([inv.amount_untaxed for inv in customer_refund])
                current_inv_amount = amount
                collected = already_invoiced_amt + current_inv_amount -customer_refund_amount
                difference = collected - project_amount
                if difference > 1.0:
                    raise Warning("Invoice Value Cannot Be Greater Than Project Value,Kindly Contact Admin")
           
                
    
    def get_involved_analytic_ids(self,analytic_id,inv_seq):
        rel_pool = self.env['od.inv.analytic.rel.per']
        re_ids=rel_pool.search([('inv_seq','=',inv_seq),('analytic_id','=',analytic_id)])        
        involved_ids = [rel.child_analytic_id.id for rel in re_ids]
        inv_share =[(rel.child_analytic_id.id,rel.value) for rel in re_ids]
        return involved_ids,inv_share
    
    
    def create_sub_inv_table(self,line_ob,grand_analytic_id,inv_id,inv_share):
        inv_seq=line_ob.inv_seq
        name = line_ob.name 
        date = line_ob.date
        pmo_date = line_ob.pmo_date
        invoice_id = inv_id
        amount = line_ob.amount
        vals ={'inv_seq':inv_seq,'name':name,'date':date,'pmo_date':pmo_date,'invoice_id':invoice_id,}
        for dat in inv_share:
            analytic_id =dat[0]
            value = dat[1]
            planned_amount = amount * (value/100.0)
            vals.update({
                'amount':planned_amount,
                'analytic_id':analytic_id,
                'grand_analytic_id':grand_analytic_id
                })
            self.create(vals)
        
        
        
    
    
    @api.multi 
    def create_invoice(self):
        context = self.env.context
        analytic_id = self.analytic_id and self.analytic_id.id or False
        grand_analytic_id = self.grand_analytic_id and self.grand_analytic_id.id or False
        inv_seq = self.inv_seq
        line_ob = self
        
        involved_an_ids,inv_sh = self.get_involved_analytic_ids(analytic_id,inv_seq)
        self._check_od_analytic_invoice_project_amount(self.analytic_id,self.amount)
        cr = self.env.cr
        uid = self.env.uid
        inv_line_vals =[]
        od_cost_sheet_id = self.analytic_id and self.analytic_id.od_cost_sheet_id and self.analytic_id.od_cost_sheet_id.id or False 
        od_branch_id  = self.analytic_id and self.analytic_id.od_branch_id and self.analytic_id.od_branch_id.id or False 
        od_cost_centre_id = self.analytic_id and self.analytic_id.od_cost_centre_id and self.analytic_id.od_cost_centre_id.id or False 
        od_division_id = self.analytic_id and self.analytic_id.od_division_id and self.analytic_id.od_division_id.id or False 
        bt_po_ref = self.analytic_id and self.analytic_id.od_cost_sheet_id and self.analytic_id.od_cost_sheet_id.part_ref
        if analytic_id and not self.invoice_id:
            so_id = self.env['sale.order'].search([('project_id','=',analytic_id),('state','!=','cancel')],limit=1)
            if not so_id:
                parent_analytic_id = self.analytic_id and self.analytic_id.parent_id and  self.analytic_id.parent_id.id
                if parent_analytic_id:
                    so_id = self.env['sale.order'].search([('project_id','=',parent_analytic_id),('state','!=','cancel')],limit=1)
            inv_vals =  self.pool.get('sale.order')._prepare_invoice(cr,uid,so_id,[])
            inv_vals['date_invoice'] =str(dt.today())
            inv_vals.update({
                'od_analytic_account':analytic_id,
                'grand_analytic_id':grand_analytic_id,
                'inv_seq':inv_seq,
                'od_cost_sheet_id':od_cost_sheet_id,
                'od_branch_id':od_branch_id,
                'od_cost_centre_id':od_cost_centre_id,
                'od_division_id':od_division_id,
                'od_costing':False,
                'bt_po_ref':bt_po_ref,
                'od_inter_inc_acc_id':so_id.od_order_type_id and so_id.od_order_type_id.income_acc_id and so_id.od_order_type_id.income_acc_id.id,
                'od_inter_exp_acc_id':so_id.od_order_type_id and so_id.od_order_type_id.expense_acc_id and so_id.od_order_type_id.expense_acc_id.id,
                })
            for line in so_id.order_line:
                an_id = line.od_analytic_acc_id and line.od_analytic_acc_id.id or False
                if an_id in involved_an_ids:
                    vals = self._prepare_invoice_line(line,an_id) 
                    inv_line_vals.append((0,0,vals))
            if context.get('old',False):
                for line in so_id.order_line:
                    vals = self._prepare_invoice_line(line,an_id) 
                    inv_line_vals.append((0,0,vals))
                    
                
            inv_vals['invoice_line'] = inv_line_vals
            inv =self.env['account.invoice'].create(inv_vals)
            inv.button_compute()
            inv.update_share()
            self.invoice_id = inv.id
            self.create_sub_inv_table(line_ob,grand_analytic_id,inv.id,inv_sh)
            
            
            model_data = self.env['ir.model.data']
            tree_view = model_data.get_object_reference('account', 'invoice_tree')
            form_view = model_data.get_object_reference('account', 'invoice_form')
            return {
                'res_id':inv.id,
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.invoice',
                'views': [(form_view and form_view[1] or False, 'form'),(tree_view and tree_view[1] or False, 'tree')], 
                'type': 'ir.actions.act_window',
            }
        return True

class od_amc_invoice_schedule(models.Model):
    _name = "od.amc.invoice.schedule"
    analytic_id  = fields.Many2one('account.analytic.account',string="Analytic Account")
    name = fields.Char(string="Name",required=True)
    date = fields.Date(string="Planned Date",required=True)
    pmo_date = fields.Date(string="PMO Expected Invoice Date")
    amount = fields.Float(string="Planned Amount",required=True)
    invoice_id = fields.Many2one('account.invoice',string="Invoice")
    invoice_amount = fields.Float(string="Invoice Amount",related="invoice_id.amount_total",readonly=True)
    date_invoice = fields.Date(string="Invoice Date",related="invoice_id.date_invoice",readonly=True)
    invoice_status = fields.Selection([('draft','Draft'),('proforma','Pro-forma'),('proforma2','Pro-forma'),('open','Open'),('accept','Accepted By Customer'),('paid','Paid'),('cancel','Cancelled')],related="invoice_id.state",raeadonly=True,string="Invoice Status")
    cust_date = fields.Date(string="Customer Accepted Date",related="invoice_id.cust_date",readonly=True)
    finance_date = fields.Date(string="Finance Expected Invoice Date")
    def _prepare_invoice_line(self, cr, uid, line,analytic_id, fiscal_position=False, context=None):
        fpos_obj = self.pool.get('account.fiscal.position')
        res = line.product_id
        account_id = res.property_account_income.id
        if not account_id:
            account_id = res.categ_id.property_account_income_categ.id
        account_id = fpos_obj.map_account(cr, uid, fiscal_position, account_id)

        taxes = line.tax_id or False
        tax_id = fpos_obj.map_tax(cr, uid, fiscal_position, taxes, context=context)
        values = {
            'name': line.name,
            'account_id': account_id,
            'account_analytic_id': analytic_id ,
            'price_unit': line.price_unit or 0.0,
            'quantity': line.product_uom_qty,
            'uos_id': line.product_uom.id or False,
            'product_id': line.product_id.id or False,
            'invoice_line_tax_id': [(6, 0, tax_id)],
        }
        return values
    
    
    def _check_od_analytic_invoice_project_amount(self,analytic,amount):
        """ Ensure the Invoice Amount Not Greater than Project Value"""
        if analytic:
            analytic_id  = analytic.id
            invoice_except =  analytic and analytic.od_create_inv_except
            if not invoice_except:
                project_amount = analytic and analytic.od_amended_sale_price 
                already_invoiced  = self.env['account.invoice'].search([('od_analytic_account','=',analytic_id),('state','in',('accept','paid'))])
                already_invoiced_amt = sum([inv.amount_untaxed for inv in already_invoiced])  
                customer_refund = self.env['account.invoice'].search([('od_analytic_account','=',analytic_id),('type','=','out_refund'),('state','not in',('draft','cancel'))])
                customer_refund_amount = sum([inv.amount_untaxed for inv in customer_refund])
                current_inv_amount = amount
                collected = already_invoiced_amt + current_inv_amount - customer_refund_amount
                if collected > project_amount:
                    raise Warning("Invoice Value Cannot Be Greater Than Project Value,Kindly Contact Admin")
    @api.multi 
    def create_invoice(self):
        analytic_id = self.analytic_id and self.analytic_id.id or False
#         self._check_od_analytic_invoice_project_amount(self.analytic_id,self.amount)
        cr = self.env.cr
        uid = self.env.uid
        inv_line_vals =[]
        od_cost_sheet_id = self.analytic_id and self.analytic_id.od_cost_sheet_id and self.analytic_id.od_cost_sheet_id.id or False 
        od_branch_id  = self.analytic_id and self.analytic_id.od_branch_id and self.analytic_id.od_branch_id.id or False 
        od_cost_centre_id = self.analytic_id and self.analytic_id.od_cost_centre_id and self.analytic_id.od_cost_centre_id.id or False 
        od_division_id = self.analytic_id and self.analytic_id.od_division_id and self.analytic_id.od_division_id.id or False 
        bt_po_ref = self.analytic_id and self.analytic_id.od_cost_sheet_id and self.analytic_id.od_cost_sheet_id.part_ref
        if analytic_id and not self.invoice_id:
            so_id = self.env['sale.order'].search([('project_id','=',analytic_id),('state','!=','cancel')],limit=1)
            if not so_id:
                parent_analytic_id = self.analytic_id and self.analytic_id.parent_id and  self.analytic_id.parent_id.id
                if parent_analytic_id:
                    so_id = self.env['sale.order'].search([('project_id','=',parent_analytic_id),('state','!=','cancel')],limit=1)
            inv_vals =  self.pool.get('sale.order')._prepare_invoice(cr,uid,so_id,[])
            inv_vals['date_invoice'] =str(dt.today())
            inv_vals.update({
                'od_analytic_account':analytic_id,
                'od_cost_sheet_id':od_cost_sheet_id,
                'od_branch_id':od_branch_id,
                'od_cost_centre_id':od_cost_centre_id,
                'od_division_id':od_division_id,
                'od_costing':False,
                'bt_po_ref':bt_po_ref,
                'od_inter_inc_acc_id':so_id.od_order_type_id and so_id.od_order_type_id.income_acc_id and so_id.od_order_type_id.income_acc_id.id,
                'od_inter_exp_acc_id':so_id.od_order_type_id and so_id.od_order_type_id.expense_acc_id and so_id.od_order_type_id.expense_acc_id.id,
                })
            for line in so_id.order_line:
                vals = self._prepare_invoice_line(line,analytic_id) 
                inv_line_vals.append((0,0,vals))
            inv_vals['invoice_line'] = inv_line_vals
            inv =self.env['account.invoice'].create(inv_vals)
            inv.button_compute()
            self.invoice_id = inv.id
            model_data = self.env['ir.model.data']
            tree_view = model_data.get_object_reference('account', 'invoice_tree')
            form_view = model_data.get_object_reference('account', 'invoice_form')
            return {
                'res_id':inv.id,
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.invoice',
                'views': [(form_view and form_view[1] or False, 'form'),(tree_view and tree_view[1] or False, 'tree')], 
                'type': 'ir.actions.act_window',
            }
        return True
class od_om_invoice_schedule(models.Model):
    _name = "od.om.invoice.schedule"
    analytic_id  = fields.Many2one('account.analytic.account',string="Analytic Account")
    name = fields.Char(string="Name",required=True)
    date = fields.Date(string="Planned Date",required=True)
    pmo_date = fields.Date(string="PMO Expected Invoice Date")
    amount = fields.Float(string="Amount",required=True)

class preventive_maint_schedule(models.Model):
    _name = "preventive.maint.schedule"
    analytic_id  = fields.Many2one('account.analytic.account',string="Analytic Account")
    name = fields.Char(string="Name",required=True)
    date = fields.Date(string="Date",required=True)
    help_desk_id = fields.Many2one('crm.helpdesk',string="Help Desk")
    
