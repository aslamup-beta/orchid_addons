# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import Warning
from openerp import SUPERUSER_ID
from math import exp,log10
import openerp.addons.decimal_precision as dp
from dateutil.relativedelta import relativedelta
from datetime import date, timedelta,datetime

class ChangeType(models.Model):
    _name = 'change.type'
    name = fields.Char(string="Name")
class ImpactSale(models.Model):
    _name = 'impact.sale'
    name = fields.Char(string="Name")
class ImpactCost(models.Model):
    _name = 'impact.cost'
    name = fields.Char(string="Name")
class ImpactProfit(models.Model):
    _name = 'impact.profit'
    name = fields.Char(string="Name")

class ChangeManagement(models.Model):
    _name = 'change.management'
    _description = 'Change'
    _inherit = ['mail.thread']
    _order = 'id desc'
    
    notes = fields.Text(string="Notes")
    
    def get_current_user(self):
        return self._uid
    
    
    @api.model
    def create(self,vals):
        vals['name'] =  '/'
        vals['v2'] =True
        ctx =self.env.context
        if ctx.get('change'):
            change = super(ChangeManagement, self).create(vals)
            change.import_cost_sheet()
            return change
        return super(ChangeManagement, self).create(vals)
    
    def od_send_mail(self,template):
        ir_model_data = self.env['ir.model.data']
        email_obj = self.pool.get('email.template')
        if self.company_id.id == 6:
            template = template +'_saudi'
        template_id = ir_model_data.get_object_reference('orchid_cost_sheet', template)[1]
        cost_sheet_id = self.id
        email_obj.send_mail(self.env.cr,self.env.uid,template_id,cost_sheet_id, force_send=True)
        return True
    
    
    @api.onchange('cost_sheet_id')
    def onchange_cost_sheet(self):
        if self.cost_sheet_id:
            branch_id = self.cost_sheet_id and self.cost_sheet_id.od_branch_id and self.cost_sheet_id.od_branch_id.id or False
            partner_id = self.cost_sheet_id and self.cost_sheet_id.od_customer_id and self.cost_sheet_id.od_customer_id.id or False
            self.branch_id = branch_id
            self.partner_id = partner_id
        
    
    
    @api.onchange('user_id')
    def onchange_user_id(self):
        hr = self.env['hr.employee']
        manager = False
        coach_id = False 
        if self.user_id:
            user_id = self.user_id.id
            users_list =hr.search([('user_id','=',user_id)])
            if users_list :
                manager = users_list.sudo().parent_id and users_list.sudo().parent_id.user_id and users_list.sudo().parent_id.user_id.id or False
                coach_id = users_list.sudo().coach_id and users_list.sudo().coach_id.user_id and users_list.sudo().coach_id.user_id.id or False
                branch_id = users_list.od_branch_id and users_list.od_branch_id.id  or False
        self.manager_id = manager
#         self.first_approval_manager_id = coach_id
#         self.branch_id = branch_id
    
    selection_list = [
            ('draft','Draft'),
            ('imported','Imported'),
            ('submit','Submitted'),
            ('first_approval','First Approval'),
            ('third_approval','Final Approval'),
            ('cancel','Cancel'),
            ('reject','Rejected')
            ]
    
    def od_get_company_id(self):
        return self.env.user.company_id
    
    
    def get_pmo_user(self):
        company_id =self.env.user.company_id
        pmo_user =19 
        if company_id.id ==6:
            pmo_user =135  
        return pmo_user
    
    child_am = fields.Selection([('add_amc','Add More Child AMC'),('add_om','Add More Child OM')],string="Addiontional Child Analytic")
    extra_child_no = fields.Integer(string="Extra/Additional No of Child")
    lock_fin_struct = fields.Boolean(string="Fin Sturct Lock",default=True)
     # Revenue Structure
    analytic_a0 = fields.Many2one('account.analytic.account',string="Analytic A0",copy=False)
    analytic_a1 = fields.Many2one('account.analytic.account',string="Analytic A1",copy=False)
    analytic_a2 = fields.Many2one('account.analytic.account',string="Analytic A2",copy=False)
    analytic_a3 = fields.Many2one('account.analytic.account',string="Analytic A3",copy=False)
    analytic_a4 = fields.Many2one('account.analytic.account',string="Analytic A4",copy=False)
    analytic_a5 = fields.Many2one('account.analytic.account',string="Analytic A5",copy=False)

    analytic_a0_state = fields.Selection(string="State",related='analytic_a0.state')
    analytic_a1_state = fields.Selection(string="State",related='analytic_a1.state')
    analytic_a2_state = fields.Selection(string="State",related='analytic_a2.state')
    analytic_a3_state = fields.Selection(string="State",related='analytic_a3.state')
    analytic_a4_state = fields.Selection(string="State",related='analytic_a4.state')
    analytic_a5_state = fields.Selection(string="State",related='analytic_a5.state')
    
    tabs_a1 = fields.Many2many('od.cost.tabs','rel_cost_a1_tabs_cm','cost_id','tab_id',string="Tabs A1",domain=[('id','not in',(4,5))])
    tabs_a2 = fields.Many2many('od.cost.tabs','rel_cost_a2_tabs_cm','cost_id','tab_id',string="Tabs A2",domain=[('id','not in',(4,5))])
    tabs_a3 = fields.Many2many('od.cost.tabs','rel_cost_a3_tabs_cm','cost_id','tab_id',string="Tabs A3",domain=[('id','not in',(4,5))] )
    tabs_a4 = fields.Many2many('od.cost.tabs','rel_cost_a4_tabs_cm','cost_id','tab_id',string="Tabs A4",domain=[('id','=',4)])
    tabs_a5 = fields.Many2many('od.cost.tabs','rel_cost_a5_tabs_cm','cost_id','tab_id',string="Tabs A5",domain=[('id','=',5)])
    
    date_start_a0 = fields.Date(string="Date Start A0")
    date_start_a1 = fields.Date(string="Date Start A1")
    date_start_a2 = fields.Date(string="Date Start A2")
    date_start_a3 = fields.Date(string="Date Start A3")
    date_start_a4 = fields.Date(string="Date Start A4")
    date_start_a5 = fields.Date(string="Date Start A5")
     
    date_end_a0 = fields.Date(string="Date End A0")
    date_end_a1 = fields.Date(string="Date End A1")
    date_end_a2 = fields.Date(string="Date End A2")
    date_end_a3 = fields.Date(string="Date End A3")
    date_end_a4 = fields.Date(string="Date End A4")
    date_end_a5 = fields.Date(string="Date End A5")
    
    name_a0 = fields.Char(string="Name of Analytic A0")
    name_a1 = fields.Char(string="Name of Analytic A1")
    name_a2 = fields.Char(string="Name of Analytic A2")
    name_a3 = fields.Char(string="Name of Analytic A3")
    name_a4 = fields.Char(string="Name of Analytic A4")
    name_a5 = fields.Char(string="Name of Analytic A5")
    
#     owner_id_a0 = fields.Many2one('res.users',string="Owner A0")
    owner_id_a1 = fields.Many2one('res.users',string="Owner A1")
    owner_id_a2 = fields.Many2one('res.users',string="Owner A2")
    owner_id_a3 = fields.Many2one('res.users',string="Owner A3")
    owner_id_a4 = fields.Many2one('res.users',string="Owner A4")
    owner_id_a5 = fields.Many2one('res.users',string="Owner A5")
    DOMAIN = [('credit','Credit'),('sup','Supply'),('imp','Implementation'),('sup_imp','Supply & Implementation'),('cust_trn','Customer Training'),('amc_view','AMC View'),('o_m_view','O&M View'),('amc','AMC'),('o_m','O&M'),('poc','(POC,Presales)')]
    
    type_of_project_a0 = fields.Selection(DOMAIN,string="Type Of Project A0")
    type_of_project_a1 = fields.Selection(DOMAIN,string="Type Of Project A1")
    type_of_project_a2 = fields.Selection(DOMAIN,string="Type Of Project A2")
    type_of_project_a3 = fields.Selection(DOMAIN,string="Type Of Project A3")
    type_of_project_a4 = fields.Selection([('amc_view','AMC View')],string="Type Of Project A4")
    type_of_project_a5 = fields.Selection([('o_m_view','O&M View'),],string="Type Of Project A5")
    
#     select_a0 = fields.Boolean(string="Select A0")
    select_a0 = fields.Boolean(string="Select A0",default=True,readonly=True)
    select_a1 = fields.Boolean(string="Select A1")
    select_a2 = fields.Boolean(string="Select A2")
    select_a3 = fields.Boolean(string="Select A3")
    select_a4 = fields.Boolean(string="Select A4")
    select_a5 = fields.Boolean(string="Select A5")
    

    #####
    periodicity_amc = fields.Selection([('weekly','Weekly'),('monthly','Monthly'),('quarterly','Quarterly'),('half_yearly','Half Yearly'),('yearly','Yearly')],string="Periodicity")
    no_of_l2_accounts_amc = fields.Integer(string="No.of L2 Accounts")
    l2_start_date_amc = fields.Date(string="Start Date")
    
    periodicity_om = fields.Selection([('weekly','Weekly'),('monthly','Monthly'),('quarterly','Quarterly'),('yearly','Yearly')],string="Periodicity")
    no_of_l2_accounts_om = fields.Integer(string="No.of L2 Accounts")
    l2_start_date_om = fields.Date(string="Start Date")

     
    amc_analytic_line = fields.One2many('od.amc.analytic.lines','cost_sheet_id',string='AMC Analytic Lines',readonly=True,copy=False)
    om_analytic_line = fields.One2many('od.om.analytic.lines','cost_sheet_id',string='AMC Analytic Lines',readonly=True,copy=False)
    
    
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id,readonly=True)
    state = fields.Selection(selection_list,string="Status",default='draft',track_visibility='always')
    name = fields.Char(string="Reference",readonly=True,track_visibility='always')
    manager_id = fields.Many2one('res.users',string="Direct Manager")
    first_approval_manager_id = fields.Many2one('res.users',string="First Approval Manager",track_visibility='always',default=get_pmo_user)
    branch_id = fields.Many2one('od.cost.branch',string="Branch",track_visibility='always')
    date = fields.Date(string="Requested Date",default=fields.Date.context_today,track_visibility='always')
    closing_date = fields.Date(string="Closing Date",track_visibility='always')
    so_id = fields.Many2one('sale.order',string="Sale Order")
    partner_id = fields.Many2one('res.partner',string="Customer")
    cost_sheet_id = fields.Many2one('od.cost.sheet',string="Cost Sheet",readonly=False)
    project_id = fields.Many2one('account.analytic.account',string="Project",readonly=False)
    change_type_id = fields.Many2one('change.type',string="Change Type")
    change_method = fields.Selection([('allow_change','Allow Change'),('redist','Redistribute Analytic')],string="Change Method",required=True)
    change_line = fields.One2many('change.order.line','change_id',string="Change line")
    change_mat_line = fields.One2many('change.mat.line','change_id',string="Change Main Proposal")
#     change_opt_mat_line = fields.One2many('change.mat.opt.line','change_id',string="Change Mat line")
    change_extra_mat_line =fields.One2many('change.mat.extra.line','change_id',string="Change Mat line")
    change_trn = fields.One2many('change.trn','change_id',string="Change Mat line")
    change_trn_extra = fields.One2many('change.trn.extra','change_id',string="Change Mat line")
    
    change_imp = fields.One2many('change.imp.tech','change_id',string="Change Mat line")
    change_imp_extra = fields.One2many('change.imp.tech.extra','change_id',string="Change Mat line")
    change_imp_out =fields.One2many('change.out.imp','change_id',string="Change Mat line")
    change_imp_out_extra =fields.One2many('change.out.imp.extra','change_id',string="Change Mat line")
    change_imp_manpower = fields.One2many('change.imp.manpower','change_id',string="Change Mat line")
    change_ps_vendor = fields.One2many('change.ps.vendor', 'change_id', string="Professional services - vendor")
    
    change_info_sec = fields.One2many('change.infosec.tech','change_id',string="Change Information Security line")
    change_info_sec_extra = fields.One2many('change.infosec.extra','change_id',string="Change Information Security line Extra")
    change_info_sec_sub =fields.One2many('change.infosec.sub','change_id',string="Change Information Security SubContractor")
    change_info_sec_vendor = fields.One2many('change.infosec.vendor', 'change_id', string="Information Security - vendor")
    
    amc_tech =fields.One2many('change.amc.tech','change_id',string="Change Mat line")
    amc_spare =fields.One2many('change.amc.spare','change_id',string="Change Mat line")
    amc_extra =fields.One2many('change.amc.extra','change_id',string="Change Mat line")
    amc_out_prevent =fields.One2many('change.amc.out.prevent','change_id',string="Change Mat line")
    amc_out_remed =fields.One2many('change.amc.out.remed','change_id',string="Change Mat line")
    amc_out_spare =fields.One2many('change.amc.out.spare','change_id',string="Change Mat line")
    amc_out_extra =fields.One2many('change.amc.out.extra','change_id',string="Change Mat line")
   
    amc_prevent =fields.One2many('change.amc.prevent','change_id',string="Change Mat line")
    amc_remed =fields.One2many('change.amc.remed','change_id',string="Change Mat line")
   
   
    om_tech =fields.One2many('change.om.tech','change_id',string="Change Mat line")
    om_resident =fields.One2many('change.om.resident','change_id',string="Change Mat line")
    om_tool =fields.One2many('change.om.tool','change_id',string="Change Mat line")
    om_extra =fields.One2many('change.om.extra','change_id',string="Change Mat line")
    
    v2= fields.Boolean(string="V2")
    
    total_price = fields.Float(string='Total Price',compute="compute_values",digits=dp.get_precision('Account'))
    total_cost = fields.Float(string='Total Cost',compute="compute_values",digits=dp.get_precision('Account'))
    profit = fields.Float(string="Profit",compute="compute_values",digits=dp.get_precision('Account'))
    profit_percent = fields.Float(string="Profit Percentage",compute="compute_values",digits=dp.get_precision('Account'))
    new_total_price = fields.Float(string="New Total Price",compute="compute_values",digits=dp.get_precision('Account'))
    new_total_cost = fields.Float(string="New Total Cost",compute="compute_values",digits=dp.get_precision('Account'))
    new_profit = fields.Float(string="New Total Profit",compute="compute_values",digits=dp.get_precision('Account'))
    new_profit_percent = fields.Float(string="New Profit Percentage",compute="compute_values",digits=dp.get_precision('Account'))
    
    
    total_price_v2 = fields.Float(string='Total Price',compute="compute_val_v2",digits=dp.get_precision('Account'))
    total_cost_v2 = fields.Float(string='Total Cost',compute="compute_val_v2",digits=dp.get_precision('Account'))
    profit_v2 = fields.Float(string="Profit",compute="compute_val_v2",digits=dp.get_precision('Account'))
    profit_percent_v2 = fields.Float(string="Profit Percentage",compute="compute_val_v2",digits=dp.get_precision('Account'))
    total_gp_v2= fields.Float(string="Profit With Returned MP")
    new_total_price_v2 = fields.Float(string="New Total Price",compute="compute_val_v2",digits=dp.get_precision('Account'),track_visibility='always')
    new_total_cost_v2 = fields.Float(string="New Total Cost",compute="compute_val_v2",digits=dp.get_precision('Account'),track_visibility='always')
    new_profit_v2 = fields.Float(string="New Total Profit",compute="compute_val_v2",digits=dp.get_precision('Account'),track_visibility='always')
    new_profit_percent_v2 = fields.Float(string="New Profit Percentage",compute="compute_val_v2",digits=dp.get_precision('Account'))
    new_rmp = fields.Float(string="New Returned MP",compute="compute_val_v2")
    new_gp = fields.Float(string="New Returned MP",compute="compute_val_v2")
    warn_string = fields.Char(string="Warning",compute="compute_val_v2")
    total_price = fields.Float(string='Total Price',compute="compute_values")
    total_cost = fields.Float(string='Total Cost',compute="compute_values")
    profit = fields.Float(string="Profit",compute="compute_values")
    profit_percent = fields.Float(string="Profit Percentage",compute="compute_values")
    new_total_price = fields.Float(string="New Total Price",compute="compute_values")
    new_total_cost = fields.Float(string="New Total Cost",compute="compute_values")
    new_profit = fields.Float(string="New Total Profit",compute="compute_values")
    new_profit_percent = fields.Float(string="New Profit Percentage",compute="compute_values")
    

    user_id = fields.Many2one('res.users',string="Requested By",default=get_current_user)
    first_approval_by =fields.Many2one('res.users',string="First Approval By")
    first_approval_date = fields.Date(string="First Approval Date")
    second_approval_by =fields.Many2one('res.users',string="Second Approval By")
    second_approval_date = fields.Date(string="Second Approval Date")
    third_approval_by =fields.Many2one('res.users',string="Third Approval By")
    third_approval_date = fields.Date(string="Third Approval Date")
    impact_sale_id = fields.Many2one('impact.sale',string="Impact On Sale")
    impact_cost_id = fields.Many2one('impact.cost',string="Impact On Cost")
    impact_profit_id = fields.Many2one('impact.profit',string="Impact On Profit")
    ignore_p = fields.Boolean(string="IG" ,copy=False)
    ignore_sell =fields.Boolean(string="Ignore Selling" ,copy=False)
    special_discount = fields.Float(string="Special Discount",digits=dp.get_precision('Account'),copy=False)
    sp_ch = fields.Boolean(string="Change Special Disc ?",copy=False)
    new_special_discount = fields.Float(string="New Special Discount",digits=dp.get_precision('Account'),copy=False)
    mat_inc = fields.Boolean(string="Mat Included",copy=False)
    trn_inc = fields.Boolean(string="TRN Included",copy=False)
    imp_inc = fields.Boolean(string="Imp Included",copy=False)
    amc_inc = fields.Boolean(string="AMC Included",copy=False)
    om_inc  =fields.Boolean(string="OM Included",copy=False)
    info_sec_inc  = fields.Boolean(string="IS Included",copy=False)
    bim_log_select = fields.Boolean(string="Bim Log Select",copy=False)
    bim_log_price = fields.Float(string="Bim Log Price",digits=dp.get_precision('Account'),copy=False)
    bim_log_cost = fields.Float(string="Bim Log Cost",digits=dp.get_precision('Account'),copy=False)
    display_bim_log_price = fields.Float(string="Bim Log Price",digits=dp.get_precision('Account'),copy=False,compute="compute_log_prices")
    display_bim_log_cost = fields.Float(string="Bim Log Cost",digits=dp.get_precision('Account'),copy=False,compute="compute_log_prices")

    pre_opn_cost = fields.Float(string="Pre-Operation Cost",digits=dp.get_precision('Account'),copy=False)
#     
#     @api.onchange('so_id')
#     def onchange_so(self):
#         if self.so_id:
#             sheet = self.so_id and self.so_id.od_cost_sheet_id and self.so_id.od_cost_sheet_id.id or False
#             self.cost_sheet_id = sheet
    
    
    @api.one 
    def unlink(self):
        if self.state not in ('draft','cancel','reject'):
            raise Warning("Cannot Delete This record on this state")
        return super(ChangeManagement,self).unlink()

    @api.one
    @api.depends('change_line')
    def compute_values(self):
        total_price = 0.0
        total_cost = 0.0
        new_total_price = 0.0
        new_total_cost = 0.0
        profit_percent = 0.0
        new_profit_percent = 0.0
        for line in self.change_line:
            total_price += line.total_price
            total_cost += line.od_amended_line_cost
            if not line.remove_item:
                new_total_price += line.new_total_price
                new_total_cost += line.new_total_cost
        profit = total_price -total_cost
        new_total_profit =  new_total_price - new_total_cost
        if total_price:
            profit_percent = profit/total_price
            self.profit_percent = profit_percent *100
        if  new_total_price:
            new_profit_percent = new_total_profit/new_total_price
            self.new_profit_percent = new_profit_percent * 100
        self.total_price = total_price
        self.total_cost = total_cost
        self.profit = profit
        self.new_total_price = new_total_price
        self.new_total_cost = new_total_cost
        self.new_profit = new_total_profit
        

        

    
    
    
    def calculate_values(self,line_id):
        total_price = 0.0
        total_cost = 0.0
        new_total_price = 0.0
        new_total_cost = 0.0
        profit_percent = 0.0
        new_profit_percent = 0.0
        for line in line_id:
            total_price += line.line_selling
            total_cost += line.line_cost
            if line.type !='remove':
                new_total_price += line.new_total_price
                new_total_cost += line.new_total_cost
       
        return total_price,total_cost,new_total_price,new_total_cost
        
    def iter_calc(self,datas):
        total_price = 0.0
        total_cost = 0.0
        new_total_price = 0.0
        new_total_cost = 0.0
        for data in datas:
            a,b,c,d = self.calculate_values(data)
            total_price +=a
            total_cost +=b 
            new_total_price +=c 
            new_total_cost +=d
        return total_price,total_cost,new_total_price,new_total_cost
    
    
    
    def get_line_datas(self):
        datas = []
        if self.mat_inc:
            datas.extend([self.change_mat_line,self.change_extra_mat_line])
        if self.trn_inc:
            datas.extend([self.change_trn,self.change_trn_extra])
        if self.imp_inc:
            datas.extend([self.change_imp,self.change_imp_extra,
               self.change_imp_out,self.change_imp_out_extra,self.change_imp_manpower,self.change_ps_vendor])
        if self.info_sec_inc:
            datas.extend([self.change_info_sec,self.change_info_sec_extra,
               self.change_info_sec_sub,self.change_info_sec_vendor])
        if self.amc_inc:
            datas.extend([ self.amc_tech,self.amc_spare,self.amc_extra,self.amc_out_prevent,
               self.amc_out_remed,self.amc_out_spare,self.amc_out_extra,  self.amc_remed,
               self.amc_prevent])
        if self.om_inc:
            datas.extend([ self.om_extra,self.om_resident,self.om_tech,self.om_tool])
        return datas
    
    
    
    def get_tech_bim(self):
        cost =0.0
        sale =0.0
        if self.included_bim_in_quotation:
            cost += sum([line.line_cost_local_currency for line in self.imp_tech_line])
            sale +=  sum([line.line_price for line in self.imp_tech_line])
        
        return cost,sale
    def get_tech_bmn(self):
        cost =0.0
        sale =0.0
        
       
        if self.included_bmn_in_quotation:
            cost += sum([line.line_cost_local_currency for line in self.amc_tech_line])
            sale += sum([line.line_price for line in self.amc_tech_line])
        return cost,sale
    def calculate_imp(self):
        sheet = self.cost_sheet_id
        cost =0.0
        if sheet.included_bim_in_quotation:
            cost += sum([x.new_total_cost for x in self.change_imp_manpower if x.type !='remove'])
            cost += sum([line.new_total_cost for line in self.change_imp if line.type !='remove'])
            if self.bim_log_select:
                cost += self.bim_log_cost
            if sheet.bim_imp_select:
                cost += sum([x.new_total_cost for x in sheet.bim_implementation_code_line])
        return cost
       
    def calculate_bmn(self):
        sheet = self.cost_sheet_id
        cost =0.0
        if sheet.included_bmn_in_quotation:
            cost += sum([x.new_total_cost for x in self.amc_prevent ])+sum([x.new_total_cost for x in self.amc_remed])
            cost += sum([line.new_total_cost for line in self.amc_tech if line.type !='remove'])
            
        return cost
    
    def calculate_info_sec(self):
        sheet = self.cost_sheet_id
        cost =0.0
        if sheet.included_info_sec_in_quotation:
            cost += sum([line.new_total_cost for line in self.change_info_sec if line.type !='remove'])
            
        return cost
        
    
    def get_rmp(self):
        amc = self.calculate_bmn()    
        imp = self.calculate_imp()
        info_sec = self.calculate_info_sec()
        return imp+amc+info_sec
    
    def line_total_cost_without_ren(self,line_id):
        tot_cost =0.0
        for line in line_id:
            if line.type !='remove':
                if not line.ren:
                    tot_cost += line.new_total_cost
        return tot_cost
    
    def line_total_cost(self,line_id):
        tot_cost =0.0
        for line in line_id:
            if line.type !='remove':
                tot_cost += line.new_total_cost
        return tot_cost
    
    def calculate_beta_it_mp_eqn(self):
        sheet = self.cost_sheet_id
        cost =0.0
        bim_extra_exp=self.line_total_cost(self.change_imp_extra)
        mat_cost=self.line_total_cost_without_ren(self.change_mat_line)
        mat_extra = self.line_total_cost_without_ren(self.change_extra_mat_line)
        mat_tot_cost = mat_cost + mat_extra
        
        trn_cost=self.line_total_cost(self.change_trn)
        trn_extra=self.line_total_cost(self.change_trn_extra)
        trn_tot_cost = trn_cost + trn_extra
        
        oim_cost=self.line_total_cost(self.change_imp_out)
        oim_tot_extra=self.line_total_cost(self.change_imp_out_extra)
        oim_vendor_cost = self.line_total_cost(self.change_ps_vendor)
        oim_tot_cost = oim_cost + oim_tot_extra + oim_vendor_cost
        
        bis_extra_exp = self.line_total_cost(self.change_info_sec_extra)
        ois_sub = self.line_total_cost(self.change_info_sec_sub)
        ois_vendor = self.line_total_cost(self.change_info_sec_vendor)
        infosec_tot_cost = bis_extra_exp + ois_sub + ois_vendor
        
        total_cost = mat_tot_cost + trn_tot_cost + oim_tot_cost + bim_extra_exp + infosec_tot_cost
        cost_factor = sheet.company_id.od_cost_factor
        if not cost_factor:
            raise Warning('Manpower Implementation Cost Factor Not Set in Your Company ,Please Configure It First')

        log_factor = sheet.company_id.od_log_factor
        if not log_factor:
            raise Warning('Manpower Implementation Log Factor Not Set in Your Company ,Please Configure It First')
        cost_fact = cost_factor/100
        cost_perc_value = 0.0
        if total_cost:
            cost_perc_value = (exp(log10(log_factor/(total_cost)))*cost_fact)
        cost_perc_min_val = float(sheet.get_min_max_manpower_percent('od_beta_it_min_manpower_percentage'))/100
        cost_perc_max_val = float(sheet.get_min_max_manpower_percent('od_beta_it_max_manpower_percentage'))/100
        if cost_perc_value > cost_perc_max_val :
            cost_perc_value =  cost_perc_max_val
        if cost_perc_value < cost_perc_min_val:
            cost_perc_value = cost_perc_min_val
        if total_cost:
            if sheet.bim_full_outsource:
                cost = (cost_perc_value * (total_cost)/2)
            else:
                cost = (cost_perc_value * total_cost)
        return cost
    
    @api.one
    @api.onchange('change_mat_line','change_extra_mat_line',
                 'change_trn','change_trn_extra', 'change_info_sec_extra',
                 'change_info_sec_sub', 'change_info_sec_vendor',
                 'change_imp_out','change_imp_out_extra','change_ps_vendor'
                 )
    def onchange_tables(self):
        #Added by aslam on 7 Nov 2019 - Calculate Beta it manpower equation
        if self.bim_log_select:
            log_cost = self.calculate_beta_it_mp_eqn()
            self.bim_log_cost = log_cost
            
    @api.one
    @api.onchange('bim_log_cost')
    def onchange_bim_log_cost(self):
        sheet = self.cost_sheet_id
        if sheet.bim_log_group:
            group = sheet.bim_log_group
            profit = group.profit /100
            if profit >=1:
                raise Warning("Profit value for the costgroup %s set 100 or above,it should be below 100"%group.name)
            discount = group.customer_discount/100
            unit_cost = self.bim_log_cost
#             unit_price = (unit_cost / (1-profit)) - (unit_cost * discount)
            unit_price = (unit_cost / (1-profit))
            unit_price = unit_price * (1-discount)
            self.bim_log_price = round(unit_price)
        if sheet.price_fixed:
            self.bim_log_price = sheet.bim_log_price_fixed
            
    @api.one
    @api.depends('bim_log_cost','bim_log_price'
                 )
    def compute_log_prices(self):
        if self.bim_log_cost:
            self.display_bim_log_cost = self.bim_log_cost
        if self.bim_log_price:
            self.display_bim_log_price = self.bim_log_price
    
    
    @api.one
    @api.depends('change_mat_line','change_extra_mat_line',
                 'change_trn','change_trn_extra','change_imp','change_imp_extra',
                 'change_imp_out','change_imp_out_extra','change_ps_vendor',
                 'change_info_sec', 'change_info_sec_extra', 'change_info_sec_sub','change_info_sec_vendor',
                 'amc_tech','amc_spare','amc_extra','amc_out_prevent',
                 'amc_out_remed','amc_out_spare','amc_out_extra',
                 'om_extra','om_resident','om_tech','om_tool',
                 'change_imp_manpower','amc_remed','amc_prevent',
                 )
    def compute_val_v2(self):
        datas = self.get_line_datas()
        total_price,total_cost,new_total_price,new_total_cost = self.iter_calc(datas)
        
        total_cost += self.pre_opn_cost
        new_total_cost += self.pre_opn_cost 
        
        total_price += self.special_discount
        sp_disc =self.special_discount
        if self.sp_ch:
            sp_disc = self.new_special_discount
        
        new_total_price +=sp_disc
            
        if self.imp_inc and self.bim_log_select:
            total_price += self.bim_log_price 
            total_cost += self.bim_log_cost
            new_total_price += self.bim_log_price 
            new_total_cost += self.bim_log_cost
            #Commented by aslam as already preopn cost adding above
            #new_total_cost += self.pre_opn_cost  
        
            
        
        profit = total_price -total_cost
        new_total_profit =  new_total_price - new_total_cost
        new_rmp = self.get_rmp()
        
        if total_price:
            profit_percent = profit/total_price
            self.profit_percent_v2 = profit_percent *100
        if  new_total_price:
            new_profit_percent = new_total_profit/new_total_price
            self.new_profit_percent_v2 = new_profit_percent * 100
        if abs(total_price - new_total_price) >=0.1:
            self.warn_string ="Warning: Sales Price Will Change After GM Approval !!!"
        
        self.total_price_v2 = total_price
        self.total_cost_v2 = total_cost
        self.profit_v2 = profit
        self.new_total_price_v2 = new_total_price
        self.new_total_cost_v2 = new_total_cost
        self.new_profit_v2 = new_total_profit
        self.new_rmp = new_rmp
        self.new_gp = new_total_profit + new_rmp
    def import_lines(self,line_ids):
        
        sheet = self.cost_sheet_id
        cost_sheet_id = self.cost_sheet_id and self.cost_sheet_id.id
        if not cost_sheet_id:
            raise Warning("Kindly Choose Costsheet")
        line_vals = []
        for line in line_ids:
            vals = {
                'item_int':line.item_int,
                'item':line.item,
                'line_id':line.id,
                'manufacture_id':line.manufacture_id and line.manufacture_id.id or False,
                'part_no':line.part_no and line.part_no.id or False,
                'types':line.types and line.types.id or False,
                'name':line.name,
#                 'vat':line.vat,
                'unit_cost_local':line.unit_cost_local,
                'line_cost':line.line_cost_local_currency,
                'unit_price':line.new_unit_price if sheet.price_fixed else line.unit_price,
                'line_selling':line.line_price,
                'qty':line.qty,
                'change_qty':line.qty,
                'change_price':line.new_unit_price if sheet.price_fixed else line.unit_price,
                'change_cost':line.unit_cost_local,
                'ren':line.ren
                
                }
            line_vals.append(vals)
        return line_vals
    
    def import_lines_extra(self,line_ids):
        sheet = self.cost_sheet_id
        cost_sheet_id = self.cost_sheet_id and self.cost_sheet_id.id
        if not cost_sheet_id:
            raise Warning("Kindly Choose Costsheet")
        line_vals = []
        for line in line_ids:
            vals = {
                'item_int':line.item_int,
                'item':line.item,
                'line_id':line.id,
                'name':line.name,
                'unit_cost_local':line.unit_cost_local,
                'line_cost':line.line_cost_local,
                'unit_price':line.new_unit_price if sheet.price_fixed else line.unit_price,
                'line_selling':line.line_price,
                'qty':line.qty,
                
                'change_qty':line.qty,
                'change_price':line.new_unit_price if sheet.price_fixed else line.unit_price,
                'change_cost':line.unit_cost_local,
                }
            line_vals.append(vals)
        return line_vals
    
    def import_lines_extra2(self,line_ids):
        sheet = self.cost_sheet_id
        cost_sheet_id = self.cost_sheet_id and self.cost_sheet_id.id
        if not cost_sheet_id:
            raise Warning("Kindly Choose Costsheet")
        line_vals = []
        for line in line_ids:
            vals = {
                'item_int':line.item_int,
                'item':line.item,
                'line_id':line.id,
                'name':line.name,
                'unit_cost_local':line.unit_cost,
                'line_cost':line.line_cost,
                'unit_price':line.new_unit_price if sheet.price_fixed else line.unit_price,
                'line_selling':line.line_price,
                'qty':line.qty,
               
                'change_qty':line.qty,
                'change_price':line.new_unit_price if sheet.price_fixed else line.unit_price,
                'change_cost':line.unit_cost,
                
                
                }
            line_vals.append(vals)
        return line_vals

    
    def create_seq(self):
        sheet =self.cost_sheet_id
        sheet_id = sheet.id
        sheet_num = sheet.number
        costsheets = self.search([('cost_sheet_id','=',sheet_id)])
        cst_sheet_count = len(costsheets) 
        self.name = sheet_num +'-CM-'+str(cst_sheet_count)
            
    
    def import_rev_struct(self):
        sheet = self.cost_sheet_id
        self.analytic_a0 = sheet.analytic_a0 and sheet.analytic_a0.id
        self.analytic_a1 = sheet.analytic_a1 and sheet.analytic_a1.id
        self.analytic_a2 = sheet.analytic_a2 and sheet.analytic_a2.id
        self.analytic_a3 = sheet.analytic_a3 and sheet.analytic_a3.id
        self.analytic_a4 = sheet.analytic_a4 and sheet.analytic_a4.id
        self.analytic_a5 = sheet.analytic_a5 and sheet.analytic_a5.id
        

        
        self.tabs_a1 = [[6, 0, [tab.id for tab in sheet.tabs_a1]]]
        self.tabs_a2 = [[6, 0, [tab.id for tab in sheet.tabs_a2]]]
        self.tabs_a3 = [[6, 0, [tab.id for tab in sheet.tabs_a3]]]
        self.tabs_a4 = [[6, 0, [tab.id for tab in sheet.tabs_a4]]]      
        self.tabs_a5 = [[6, 0, [tab.id for tab in sheet.tabs_a5]]]      
        
        self.date_start_a0 = sheet.date_start_a0 
        self.date_start_a1 = sheet.date_start_a1 
        self.date_start_a2 = sheet.date_start_a2 
        self.date_start_a3 = sheet.date_start_a3 
        self.date_start_a4 = sheet.date_start_a4 
        self.date_start_a5 = sheet.date_start_a5 
        
        self.date_end_a0 = sheet.date_end_a0
        self.date_end_a1 = sheet.date_end_a1
        self.date_end_a2 = sheet.date_end_a2
        self.date_end_a3 = sheet.date_end_a3
        self.date_end_a4 = sheet.date_end_a4
        self.date_end_a5 = sheet.date_end_a5
        
        self.name_a0 = sheet.name_a0
        self.name_a1 = sheet.name_a1
        self.name_a2 = sheet.name_a2
        self.name_a3 = sheet.name_a3
        self.name_a4 = sheet.name_a4
        self.name_a5 = sheet.name_a5
        
    #     owner_id_a0 = fields.Many2one('res.users',string="Owner A0")
        self.owner_id_a1 = sheet.owner_id_a1 and sheet.owner_id_a1.id 
        self.owner_id_a2 = sheet.owner_id_a2 and sheet.owner_id_a2.id 
        self.owner_id_a3 = sheet.owner_id_a3 and sheet.owner_id_a3.id 
        self.owner_id_a4 = sheet.owner_id_a4 and sheet.owner_id_a4.id 
        self.owner_id_a5 = sheet.owner_id_a5 and sheet.owner_id_a5.id 
        
        self.type_of_project_a0 = sheet.type_of_project_a0 
        self.type_of_project_a1 = sheet.type_of_project_a1 
        self.type_of_project_a2 = sheet.type_of_project_a2 
        self.type_of_project_a3 = sheet.type_of_project_a3 
        self.type_of_project_a4 = sheet.type_of_project_a4 
        self.type_of_project_a5 = sheet.type_of_project_a5 
        
    #     select_a0 = fields.Boolean(string="Select A0")
        self.select_a0 = sheet.select_a0
        self.select_a1 = sheet.select_a1
        self.select_a2 = sheet.select_a2
        self.select_a3 = sheet.select_a3
        self.select_a4 = sheet.select_a4
        self.select_a5 = sheet.select_a5
        
        self.periodicity_amc = sheet.periodicity_amc
        self.periodicity_om = sheet.periodicity_om
        
        self.l2_start_date_amc = sheet.l2_start_date_amc
        self.l2_start_date_om = sheet.l2_start_date_om 
        
        self.no_of_l2_accounts_amc = sheet.no_of_l2_accounts_amc 
        self.no_of_l2_accounts_om = sheet.no_of_l2_accounts_om
        



    @api.one 
    def import_cost_sheet(self):
        self.create_seq()
        sheet = self.cost_sheet_id
        if self.change_method == 'redist':
            self.import_rev_struct()
            self.state ='imported'
            return True
        self.special_discount = sheet.special_discount or 0.0
        self.total_gp_v2 = sheet.total_gp
        self.pre_opn_cost = sheet.pre_opn_cost or 0.0
        self.mat_inc = sheet.included_in_quotation or False
        self.trn_inc = sheet.included_trn_in_quotation or False
        self.imp_inc = sheet.included_bim_in_quotation or False
        self.amc_inc = sheet.included_bmn_in_quotation or False
        self.om_inc = sheet.included_om_in_quotation or False
        self.info_sec_inc = sheet.included_info_sec_in_quotation or False
        self.bim_log_select = sheet.bim_log_select 
        self.bim_log_price = sheet.bim_log_price
        self.bim_log_cost = sheet.bim_log_cost
#         cost_sheet_id = self.cost_sheet_id and self.cost_sheet_id.id
        mat_line= self.import_lines(sheet.mat_main_pro_line)
        
        self.change_mat_line.unlink()
        self.change_mat_line = mat_line
        
#         mat_opt_line=  self.import_lines(sheet.mat_optional_item_line)
#         self.change_opt_mat_line.unlink()
#         self.change_opt_mat_line = mat_opt_line
        
        mat_extra_line= self.import_lines_extra(sheet.mat_extra_expense_line)
        self.change_extra_mat_line.unlink()
        self.change_extra_mat_line = mat_extra_line
        
        change_trn=  self.import_lines(sheet.trn_customer_training_line)
        self.change_trn.unlink()
        self.change_trn = change_trn
        
        trn_extra_line= self.import_lines_extra(sheet.trn_customer_training_extra_expense_line)
        self.change_trn_extra.unlink()
        self.change_trn_extra = trn_extra_line
        #imp
        imp_line = self.import_lines(sheet.imp_tech_line)
        self.change_imp.unlink()
        self.change_imp = imp_line
        
        imp_line_extra = self.import_lines_extra2(sheet.implimentation_extra_expense_line)
        self.change_imp_extra.unlink()
        self.change_imp_extra =imp_line_extra
        
        imp_out = self.import_lines_extra2(sheet.oim_implimentation_price_line)
        self.change_imp_out.unlink()
        self.change_imp_out = imp_out
        
        imp_out_extra = self.import_lines_extra2(sheet.oim_extra_expenses_line)
        self.change_imp_out_extra.unlink()
        self.change_imp_out_extra = imp_out_extra
        
        imp_manpower = self.import_lines_extra2(sheet.manpower_manual_line)
        self.change_imp_manpower.unlink()
        self.change_imp_manpower = imp_manpower
        
        ps_vendor_line = self.import_lines(sheet.ps_vendor_line)
        self.change_ps_vendor.unlink()
        self.change_ps_vendor = ps_vendor_line
        
        #infosec
        info_sec_line = self.import_lines(sheet.info_sec_tech_line)
        self.change_info_sec.unlink()
        self.change_info_sec = info_sec_line
        
        info_sec_line_extra = self.import_lines_extra2(sheet.info_sec_extra_expense_line)
        self.change_info_sec_extra.unlink()
        self.change_info_sec_extra =info_sec_line_extra
        
        info_sec_sub = self.import_lines_extra2(sheet.info_sec_subcontractor_line)
        self.change_info_sec_sub.unlink()
        self.change_info_sec_sub = info_sec_sub
        
        info_sec_vendor_line = self.import_lines(sheet.info_sec_vendor_line)
        self.change_info_sec_vendor.unlink()
        self.change_info_sec_vendor = info_sec_vendor_line
        
        
        #amc
        amc_tech = self.import_lines(sheet.amc_tech_line)
        self.amc_tech.unlink()
        self.amc_tech = amc_tech
        
        amc_spare = self.import_lines(sheet.bmn_spareparts_beta_it_maintenance_line)
        self.amc_spare.unlink()
        self.amc_spare = amc_spare
        
        amc_extra = self.import_lines_extra2(sheet.bmn_beta_it_maintenance_extra_expense_line)
        self.amc_extra.unlink()
        self.amc_extra = amc_extra
        
        amc_out_prevent = self.import_lines_extra2(sheet.omn_out_preventive_maintenance_line)
        self.amc_out_prevent.unlink()
        self.amc_out_prevent = amc_out_prevent
        
        amc_remed = self.import_lines_extra2(sheet.omn_out_remedial_maintenance_line)
        self.amc_out_remed.unlink()
        self.amc_out_remed = amc_remed
        
        amc_spare_out = self.import_lines(sheet.omn_spare_parts_line)
        self.amc_out_spare.unlink()
        self.amc_out_spare = amc_spare_out
        
        amc_out_extra = self.import_lines_extra2(sheet.omn_maintenance_extra_expense_line)
        self.amc_out_extra.unlink()
        self.amc_out_extra = amc_out_extra
        
        amc_prevent =self.import_lines_extra2(sheet.bmn_it_preventive_line)
        self.amc_prevent.unlink()
        self.amc_prevent = amc_prevent 
        
        amc_remed  =self.import_lines_extra2(sheet.bmn_it_remedial_line)
        self.amc_remed.unlink()
        self.amc_remed =amc_remed
        
        #OMN
        om_tech = self.import_lines(sheet.om_tech_line)
        self.om_tech.unlink()
        self.om_tech = om_tech
        
        om_resident = self.import_lines_extra2(sheet.om_residenteng_line)
        self.om_resident.unlink()
        self.om_resident = om_resident
        
        om_tool = self.import_lines(sheet.om_eqpmentreq_line)
        self.om_tool.unlink()
        self.om_tool = om_tool
        
        om_extra = self.import_lines_extra2(sheet.om_extra_line)
        self.om_extra.unlink()
        self.om_extra = om_extra
        
        
        self.state ='imported'
    @api.one
    def import_sale(self):
        sale_id = self.so_id
        if not sale_id:
            raise Warning("Please Choose Sale Order")
        line_vals = []
        for line in sale_id.order_line:
            vals ={
                   'product_id':line.product_id and line.product_id.id or False,
                   'od_manufacture_id':line.od_manufacture_id and line.od_manufacture_id or False,
                   'name':line.name,
                   'product_uom_qty':line.product_uom_qty,
                   'price_unit':line.price_unit,
                   'purchase_price':line.purchase_price,
                   'change_qty':line.product_uom_qty,
                   'change_price':line.price_unit,
                   'change_cost':line.purchase_price,
                   
                   }
            line_vals.append(vals)
        self.change_line.unlink()
        self.change_line = line_vals
        self.state ='imported'
    
#     def check_prouduct_purchased(self):
#         for line in self.change_line:
#             rm_item = line.remove_item 
#             if rm_item:
#                 product_id = line.product_id and line.product_id.id or False
#                 #Commented by aslam as there is no attribute so_id in line
# #                 so_id = line.so_id and line.so_id.id
#                 so_id = self.so_id and self.so_id.id 
#                 if so_id and product_id:
#                     so_name = self.so_id.name
#                     po_pool  = self.env['purchase.order']
#                     po_ob = po_pool.search([('origin','=',so_name)])
#                     po_ids = [po.id for po in po_ob]
#                     if po_ids:
#                         po_line = self.env['purchase.order.line']
#                         po_line_ob = po_line.search([('order_id','in',po_ids),('product_id','=',product_id)])
#                         if po_line_ob:
#                             raise Warning("Purchase Order already generated for this Product %s"%line.product_id.name)
    
    
    def check_selling(self):
        if abs(self.total_price_v2 - self.new_total_price_v2) >=0.1:
            raise Warning("You Cant Submit a Change with New Selling Value")
    
    def check_any_tabs_closed(self):
        sheet = self.cost_sheet_id
        tabs_a1 = [tab.id for tab in sheet.tabs_a1]
        tabs_a2 = [tab.id for tab in sheet.tabs_a2]
        tabs_a3 = [tab.id for tab in sheet.tabs_a3]
        a1_state = self.cost_sheet_id.analytic_a1_state or False
        a2_state = self.cost_sheet_id.analytic_a2_state or False
        a3_state = self.cost_sheet_id.analytic_a3_state or False
        closed_tabs = []
        
        if tabs_a1 and a1_state == 'close':
            closed_tabs += tabs_a1
        if tabs_a2 and a2_state == 'close':
            closed_tabs += tabs_a2
        if tabs_a3 and a3_state == 'close':
            closed_tabs += tabs_a3
        print closed_tabs,"x"*88
        for line in self.change_mat_line:
            if line.add_new_item and 1 in closed_tabs:
                raise Warning("The material part of this project is already closed. You cannot add new items to the MAT tab. Please move to another tab that is still open.")
            if line.type in ('change','remove') and 1 in closed_tabs:
                raise Warning("The material part of this project is closed. Changes cannot be made to a closed tab.")
        for line in self.change_extra_mat_line:
            if line.add_new_item and 1 in closed_tabs:
                raise Warning("The material part of this project is already closed. You cannot add new items to the MAT tab. Please move to another tab that is still open.")
            if line.type in ('change','remove') and 1 in closed_tabs:
                raise Warning("The material part of this project is closed. Changes cannot be made to a closed tab.")
        for line in self.change_trn:
            if line.add_new_item and 2 in closed_tabs:
                raise Warning("The training part of this project is already closed. You cannot add new items to the TRN tab. Please move to another tab that is still open.")
            if line.type in ('change','remove') and 2 in closed_tabs:
                raise Warning("The training part of this project is closed. Changes cannot be made to a closed tab.")
        for line in self.change_trn_extra:
            if line.add_new_item and 2 in closed_tabs:
                raise Warning("The training part of this project is already closed. You cannot add new items to the TRN tab. Please move to another tab that is still open.")
            if line.type in ('change','remove') and 2 in closed_tabs:
                raise Warning("The training part of this project is closed. Changes cannot be made to a closed tab.")
        for line in self.change_imp:
            if line.add_new_item and 3 in closed_tabs:
                raise Warning("The PS part of this project is already closed. You cannot add new items to the PS tab. Please move to another tab that is still open.")
            if line.type in ('change','remove') and 3 in closed_tabs:
                raise Warning("The PS part of this project is closed. Changes cannot be made to a closed tab.")   
        for line in self.change_imp_extra:
            if line.add_new_item and 3 in closed_tabs:
                raise Warning("The PS part of this project is already closed. You cannot add new items to the PS tab. Please move to another tab that is still open.")
            if line.type in ('change','remove') and 3 in closed_tabs:
                raise Warning("The PS part of this project is closed. Changes cannot be made to a closed tab.")
        for line in self.change_imp_out_extra:
            if line.add_new_item and 3 in closed_tabs:
                raise Warning("The PS part of this project is already closed. You cannot add new items to the PS tab. Please move to another tab that is still open.")
            if line.type in ('change','remove') and 3 in closed_tabs:
                raise Warning("The PS part of this project is closed. Changes cannot be made to a closed tab.")
        for line in self.change_ps_vendor:
            if line.add_new_item and 3 in closed_tabs:
                raise Warning("The PS part of this project is already closed. You cannot add new items to the PS tab. Please move to another tab that is still open.")
            if line.type in ('change','remove') and 3 in closed_tabs:
                raise Warning("The PS part of this project is closed. Changes cannot be made to a closed tab.")
    
    def check_prouduct_purchased(self):
        for line in self.change_mat_line:
            type = line.type 
            if type =='remove':
                product_id = line.part_no and line.part_no.id or False
                #Commented by aslam as there is no attribute so_id in line
#                 so_id = line.so_id and line.so_id.id
#                 so_id = self.so_id and self.so_id.id 
                cost_sheet_id = self.cost_sheet_id and self.cost_sheet_id.id or False
                if cost_sheet_id and product_id:
#                     so_name = self.so_id.name
                    po_pool  = self.env['purchase.order']
                    po_ob = po_pool.search([('od_cost_sheet_id','=',cost_sheet_id), ('state','!=','cancel')])
                    po_ids = [po.id for po in po_ob]
                    if po_ids:
                        po_line = self.env['purchase.order.line']
                        po_line_ob = po_line.search([('order_id','in',po_ids),('product_id','=',product_id)])
                        if po_line_ob:
                            raise Warning("Purchase Order already generated for this Product %s"%line.part_no.name)
                
                
        
    
    
    
    
    @api.one 
    def button_submit(self):
        cost_sheet_id = self.cost_sheet_id
#         duplicate = cost_sheet_id.copy()
        cost_sheet_state = self.cost_sheet_id.state
        if cost_sheet_state != 'done':
            raise Warning("Cost Sheet Not in Done State ,Pls Check the Costsheet")
        self.check_any_tabs_closed()
        if not self.ignore_p:
            self.check_prouduct_purchased()
        
        if not self.ignore_sell:
            self.check_selling()
        self.state = 'submit'
        self.date = fields.Date.context_today(self)
        self.od_send_mail('cm_submit_mail')
    
    @api.one
    @api.multi
    def button_first_approval(self):
#         crm_lead = self.env['crm.lead']
        cs_id = self.cost_sheet_id.id
#         lead_id = self.cost_sheet_id.lead_id
#         duplicate = lead_id.search()
        cost_sheet_state = self.cost_sheet_id.state
        if cost_sheet_state != 'done':
            raise Warning("Cost Sheet Not in Done State ,Pls Check the Costsheet")
        self.first_approval_by = self._uid
        self.first_approval_date = fields.Date.context_today(self)
        self.state = 'first_approval'
        self.od_send_mail('cm_first_approval_mail')
    
    @api.one 
    def button_second_approval(self):
        cost_sheet_id = self.cost_sheet_id
        cost_sheet_state = self.cost_sheet_id.state
        if cost_sheet_state != 'done':
            raise Warning("Cost Sheet Not in Done State ,Pls Check the Costsheet")
        self.second_approval_by = self._uid
        self.second_approval_date = fields.Date.context_today(self)
        self.state = 'second_approval'
        self.od_send_mail('cm_second_approval_mail')
        
    
    
    def update_costsheet_table(self,line_ids,obj_name):
        for line in line_ids:
            type = line.type 
            if type and type =='change':
                line_id = line.line_id and line.line_id.id
                obj = self.env[obj_name].browse(line_id)
                vals = {
                    'item_int':line.item_int,
                    'item':line.item,
                    'name':line.name,
                    }
                if line.is_change_cost:
                    vals.update({
                        'unit_cost_amend':line.change_cost,
                        'is_unit_cost_amend':True,
                        })
                if line.is_change_price:
                    vals.update({
                        'new_unit_price':line.change_price,
                        'fixed':True,
                        })
                if line.is_change_qty:
                    vals.update({
                        'qty':int(line.change_qty),
                        })
                obj.write(vals)
            if type and type =='remove':
                line_id = line.line_id and line.line_id.id
                obj = self.env[obj_name].browse(line_id)
                obj.unlink()
            print line.add_new_item,line.item_int,"1"*88
            if line.add_new_item:
                line_id = line.line_id and line.line_id.id
                if line_id:
                    raise Warning("Add item Option Only to Add New Item, you cant choose this over already Present Item %s and part No %s"%(line.item_int,line.part_no.name))
                else:
                    
                    vals = {
                    'cost_sheet_id':self.cost_sheet_id and self.cost_sheet_id.id,
                    'part_no':line.part_no and line.part_no.id or False,
                    'item_int':line.item_int,
                    'item':line.item,
                    'manufacture_id':line.manufacture_id and line.manufacture_id.id or False,
                    'name':line.name,
                     'unit_cost_amend':line.change_cost,
                    'is_unit_cost_amend':True,
                    'new_unit_price':line.change_price,
                    'fixed':True,
                   
                     'qty':int(line.change_qty),
                     'uom_id':1,
                     'types':line.types and line.types.id or False,
                    }
                    
                    obj = self.env[obj_name]
                    obj.create(vals)


    
    
        
    def update_costsheet_table_extra(self,line_ids,obj_name):
        for line in line_ids:
            type = line.type 
            if type and type =='change':
                line_id = line.line_id and line.line_id.id
                obj = self.env[obj_name].browse(line_id)
                vals = {
                    'item_int':line.item_int,
                    'item':line.item,
                    'name':line.name,
                    }
                if line.is_change_cost:
                    vals.update({
                        'unit_cost_amend':line.change_cost,
                        'is_unit_cost_amend':True,
                        })
                if line.is_change_price:
                    vals.update({
                        'new_unit_price':line.change_price,
                        'fixed':True,
                        })
                if line.is_change_qty:
                    vals.update({
                        'qty':int(line.change_qty),
                        })
                obj.write(vals)
            if type and type =='remove':
                line_id = line.line_id and line.line_id.id
                obj = self.env[obj_name].browse(line_id)
                obj.unlink()
            if line.add_new_item:
                line_id = line.line_id and line.line_id.id
                if line_id:
                    raise Warning("Add item Option Only to Add New Item, you cant choose this over already Present Item %s and part No %s"%(line.item_int,line.part_no.name))
                else:
                    
                    vals = {
                    'cost_sheet_id':self.cost_sheet_id and self.cost_sheet_id.id,
#                     'part_no':line.part_no and line.part_no.id or False,
                    'item_int':line.item_int,
                    'item':line.item,
#                     'manufacture_id':line.manufacture_id and line.manufacture_id.id or False,
                    'name':line.name,
                     'unit_cost_amend':line.change_cost,
                    'is_unit_cost_amend':True,
                    'new_unit_price':line.change_price,
                    'fixed':True,
                     'qty':int(line.change_qty),
                     'uom_id':1,
                      
#                      'types':line.types and line.types.id or False,
                    }
                    
                    obj = self.env[obj_name]
                    obj.create(vals)
    
    
            
    def update_costsheet_table_extra2(self,line_ids,obj_name):
        for line in line_ids:
            type = line.type 
            if type and type =='change':
                line_id = line.line_id and line.line_id.id
                obj = self.env[obj_name].browse(line_id)
                vals = {
                    'item_int':line.item_int,
                    'item':line.item,
                    'name':line.name,
                    }
                if line.is_change_cost:
                    vals.update({
                        'unit_cost':line.change_cost,
                       
                        })
                if line.is_change_price:
                    vals.update({
                        'new_unit_price':line.change_price,
                        'fixed':True,
                        })
                if line.is_change_qty:
                    vals.update({
                        'qty':int(line.change_qty),
                        })
                obj.write(vals)
            if type and type =='remove':
                line_id = line.line_id and line.line_id.id
                obj = self.env[obj_name].browse(line_id)
                obj.unlink()
            if line.add_new_item:
                line_id = line.line_id and line.line_id.id
                if line_id:
                    raise Warning("Add item Option Only to Add New Item, you cant choose this over already Present Item %s and part No %s"%(line.item_int,line.part_no.name))
                else:
                    
                    vals = {
                    'cost_sheet_id':self.cost_sheet_id and self.cost_sheet_id.id,
#                     'part_no':line.part_no and line.part_no.id or False,
                    'item_int':line.item_int,
                    'item':line.item,
#                     'manufacture_id':line.manufacture_id and line.manufacture_id.id or False,
                    'name':line.name,
                     'unit_cost':line.change_cost,
                    
                    'new_unit_price':line.change_price,
                    'fixed':True,
                    
                     'qty':int(line.change_qty),
                     'uom_id':1,
#                      'types':line.types and line.types.id or False,
                    }
                    
                    obj = self.env[obj_name]
                    obj.create(vals)


    
    def update_amendement(self):
        
        
        if self.sp_ch:
            sp_disc= self.new_special_discount
            self.cost_sheet_id.write({'special_discount':sp_disc})
        #mat
        self.update_costsheet_table(self.change_mat_line,'od.cost.mat.main.pro.line')

        self.update_costsheet_table_extra(self.change_extra_mat_line,'od.cost.mat.extra.expense.line')
        
        #trn
        self.update_costsheet_table(self.change_trn, 'od.cost.trn.customer.training.line')
        self.update_costsheet_table_extra(self.change_trn_extra, 'od.cost.trn.customer.training.extra.expense.line')
        
        #imp
        self.update_costsheet_table(self.change_imp, 'od.cost.imp.tech.line')
        self.update_costsheet_table_extra2(self.change_imp_extra, 'od.cost.bim.beta.implimentation.extra.expense.line')
        self.update_costsheet_table_extra2(self.change_imp_out, 'od.cost.oim.implimentation.price.line')   
        self.update_costsheet_table_extra2(self.change_imp_out_extra, 'od.cost.oim.extra.expenses.line') 
        self.update_costsheet_table(self.change_ps_vendor, 'od.cost.ps.vendor.line')      
        
        #IS
        self.update_costsheet_table(self.change_info_sec, 'od.cost.is.tech.line')
        self.update_costsheet_table_extra2(self.change_info_sec_extra, 'od.cost.is.extra.expense.line')
        self.update_costsheet_table_extra2(self.change_info_sec_sub, 'od.cost.is.subcontractor.line')
        self.update_costsheet_table(self.change_info_sec_vendor, 'od.cost.is.vendor.line')
            
        
        #AMC
        self.update_costsheet_table(self.amc_tech, 'od.cost.amc.tech.line')
        self.update_costsheet_table(self.amc_spare, 'od.cost.bmn.spareparts.beta.it.maintenance.line')
        self.update_costsheet_table_extra2(self.amc_extra, 'od.cost.bmn.beta.it.maintenance.extra.expense.line')
        self.update_costsheet_table_extra2(self.amc_out_prevent, 'od.cost.omn.out.preventive.maintenance.line')
        self.update_costsheet_table_extra2(self.amc_out_remed, 'od.cost.omn.out.remedial.maintenance.line')
        self.update_costsheet_table(self.amc_out_spare, 'od.cost.omn.spare.parts.line')
        self.update_costsheet_table_extra2(self.amc_out_extra, 'od.cost.omn.maintenance.extra.expense.line')
        
        #omn
        self.update_costsheet_table(self.om_tech, 'od.cost.om.tech.line')
        self.update_costsheet_table_extra2(self.om_resident, 'od.cost.om.residenteng.line')
        self.update_costsheet_table_extra2(self.om_tool, 'od.cost.om.eqpmentreq.line')
        self.update_costsheet_table_extra2(self.om_extra, 'od.cost.om.extra.line')
                
    
    
    def add_child_analytic(self):
        sheet = self.cost_sheet_id
        sheet_id = sheet.id
        if self.child_am == 'add_amc':
            no_of_child = self.extra_child_no
            amc_childs = sheet.no_of_l2_accounts_amc
            new_amc_child = amc_childs + no_of_child
            sheet.write({'no_of_l2_accounts_amc':new_amc_child})
            amc_line=self.env['od.amc.analytic.lines'].search([('cost_sheet_id','=',sheet_id)],order="id desc", limit=1)
            analytic_samp = amc_line.analytic_id 
            periodicity = sheet.periodicity_amc 
            name = self.analytic_a4.name + '-AMC'
            code =self.analytic_a4.code + '-AMC'
            
            if analytic_samp:
                start_date = analytic_samp.date
                start_date =datetime.strptime(start_date,'%Y-%m-%d')
                for i in range(no_of_child):
                    counter = amc_childs +i +1
                    
                    
                    if periodicity =='weekly':
                        date_end = start_date + relativedelta(weeks=+1)
                    if periodicity =='monthly':
                        date_end = start_date + relativedelta(months=+1)
                    if periodicity =='quarterly':
                        date_end = start_date + relativedelta(months=+3)
                    if periodicity =='half_yearly':
                        date_end = start_date + relativedelta(months=+6)
                    if periodicity =='yearly':
                        date_end = start_date + relativedelta(years=+1)
                    vals ={
                     'name':name +'-' +str(counter),
                        'date_start':str(start_date),
                        'date':str(date_end),
                        'od_date_end_original':str(date_end),
                        'od_analytic_pmo_closing':str(date_end),
                        'code':code+'-' +str(counter),
                        'mp_amend':False

                    } 
                    an_dat=analytic_samp.copy(vals)
                    an_name=name +'-' +str(counter),
                    an_dat.write({'name':str(an_name)})
                    an_id = an_dat.id
                    line_vals={'start_date':start_date,'end_date':date_end,'analytic_id':an_id,'cost_sheet_id':sheet_id}
                    start_date = date_end 
                    self.env['od.amc.analytic.lines'].create(line_vals)      
        if self.child_am == 'add_om':
            no_of_child = self.extra_child_no
            childs = sheet.no_of_l2_accounts_om
            new_child = childs + no_of_child
            sheet.write({'no_of_l2_accounts_amc':new_child})
            amc_line=self.env['od.om.analytic.lines'].search([('cost_sheet_id','=',sheet_id)],order="id desc", limit=1)
            analytic_samp = amc_line.analytic_id 
            periodicity = sheet.periodicity_amc 
            name = self.analytic_a5.name + '-OM'
            code =self.analytic_a5.code + '-OM'
            
            if analytic_samp:
                start_date = analytic_samp.date
                start_date =datetime.strptime(start_date,'%Y-%m-%d')
                for i in range(no_of_child):
                    counter = amc_childs +i +1
                    
                    
                    if periodicity =='weekly':
                        date_end = start_date + relativedelta(weeks=+1)
                    if periodicity =='monthly':
                        date_end = start_date + relativedelta(months=+1)
                    if periodicity =='quarterly':
                        date_end = start_date + relativedelta(months=+3)
                    if periodicity =='half_yearly':
                        date_end = start_date + relativedelta(months=+6)
                    if periodicity =='yearly':
                        date_end = start_date + relativedelta(years=+1)
                    vals ={
                     'name':name +'-' +str(counter),
                        'date_start':str(start_date),
                        'date':str(date_end),
                        'od_date_end_original':str(date_end),
                        'od_analytic_pmo_closing':str(date_end),
                        'code':code+'-' +str(counter),
                        'mp_amend':False

                    } 
                    an_dat=analytic_samp.copy(vals)
                    an_name=name +'-' +str(counter),
                    an_dat.write({'name':str(an_name)})
                    an_id = an_dat.id
                    line_vals={'start_date':start_date,'end_date':date_end,'analytic_id':an_id,'cost_sheet_id':sheet_id}
                    start_date = date_end 
                    self.env['od.om.analytic.lines'].create(line_vals) 
    
    
    def approve_dist_analytic(self):
        sheet = self.cost_sheet_id
        write_vals ={
            'tabs_a1':[[6,0,[tab.id for tab in self.tabs_a1]]],
            'tabs_a2':[[6,0,[tab.id for tab in self.tabs_a2]]],
            'tabs_a3':[[6,0,[tab.id for tab in self.tabs_a3]]],
            'tabs_a4':[[6,0,[tab.id for tab in self.tabs_a4]]],
            'tabs_a5':[[6,0,[tab.id for tab in self.tabs_a5]]],
            
        }
        sheet.write(write_vals)
        self.add_child_analytic()


    
    @api.one 
    def button_third_approval(self):
        self.third_approval_by = self._uid
        self.third_approval_date = fields.Date.context_today(self)
        method= self.change_method
        cost_sheet_id = self.cost_sheet_id
        cost_sheet_state = self.cost_sheet_id.state
        self.closing_date = fields.Date.context_today(self)
        if cost_sheet_state != 'done':
            raise Warning("Cost Sheet Not in Done State ,Pls Check the Costsheet")
        
        if method == 'redist':
            self.approve_dist_analytic()
            self.state = 'third_approval'
            self.od_send_mail('cm_third_approval_mail')
            return True
        
        self.update_amendement()
        if method == 'allow_change':
            cost_sheet_id.amend_btn_process_change()
        # elif method == 'redist':
        #     self.approve_dist_analytic()
        if abs(self.total_price_v2 - self.new_total_price_v2) >=0.1:
            for line in cost_sheet_id.od_plan_dist_line:
                line.write({'locked': False})
            
        self.state = 'third_approval'
        self.od_send_mail('cm_third_approval_mail')
    @api.one 
    def button_cancel(self):
        self.state= 'cancel'
        self.od_send_mail('cm_cancel_mail')
    
    @api.one 
    def button_reject(self):
        self.state= 'reject'
        self.od_send_mail('cm_reject_mail')
            
    
class ChangeOrderLine(models.Model):
    _name = "change.order.line"
    _inherit = "sale.order.line"
    change_id = fields.Many2one('change.management',string="Change")
    order_id = fields.Many2one('sale.order',required=False)
    total_price = fields.Float(string="Total Price",compute="_od_get_total_price",digits=dp.get_precision('Account'))
    change_qty = fields.Float(string="Change Qty",digits=dp.get_precision('Account'))
    change_price = fields.Float(string="Change Price",digits=dp.get_precision('Account'))
    new_total_price = fields.Float(string="New Total Price",compute="_od_get_total_price",digits=dp.get_precision('Account'))
    change_cost = fields.Float(string="Change Cost",digits=dp.get_precision('Account'))
    new_total_cost = fields.Float(string="New Total Cost",compute="_od_get_total_price",digits=dp.get_precision('Account'))
    remove_item = fields.Boolean(string="Remove Item")
    
    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            desc = (self.product_id and self.product_id.description_sale) or (self.product_id and self.product_id.description) or (self.product_id and self.product_id.name)
            self.name = desc
            self.types = self.product_id and self.product_id.od_pdt_type_id and self.product_id.od_pdt_type_id.id or False
            
    @api.one
    @api.depends('product_uom_qty','price_unit','change_qty','change_price','change_cost','remove_item')
    def _od_get_total_price(self):
        self.total_price = self.get_line_price(self.product_uom_qty,self.price_unit)
        if self.remove_item:
            self.new_total_price = 0.0
            self.new_total_cost = 0.0
        else:
            self.new_total_price = self.get_line_price(self.change_qty,self.change_price)
            self.new_total_cost = self.get_line_price(self.change_qty,self.change_cost)



class ChangeMatLine(models.Model):
    _name = "change.mat.line"
    add_new_item = fields.Boolean(string="Add New Item")
    type = fields.Selection([('change','Change'),('remove','Remove Item')],string="Change Type")
    is_change_cost = fields.Boolean(string="Change Cost?")
    is_change_price = fields.Boolean(string="Change Price?")
    is_change_qty = fields.Boolean(string="Change Qty?")
    change_id = fields.Many2one('change.management',string="Change")
    line_id = fields.Many2one('od.cost.mat.main.pro.line',required=False)
    total_price = fields.Float(string="Total Price",compute="_od_get_total_price",digits=dp.get_precision('Account'))
    change_qty = fields.Float(string="Change Qty",digits=dp.get_precision('Account'), default=1.0)
    change_price = fields.Float(string="Change Selling",digits=dp.get_precision('Account'))
    new_total_price = fields.Float(string="New Total Selling",compute="_od_get_total_price",digits=dp.get_precision('Account'))
    change_cost = fields.Float(string="Change Cost",digits=dp.get_precision('Account'))
    new_total_cost = fields.Float(string="New Total Cost",compute="_od_get_total_price",digits=dp.get_precision('Account'))
    remove_item = fields.Boolean(string="Remove Item")
    ren = fields.Boolean(string="REN")
   
    item_int = fields.Integer('Item Number')
    item = fields.Char(string="Item") 
    manufacture_id = fields.Many2one('od.product.brand',string='Manufacturer')
    part_no = fields.Many2one('product.product',string='Part No')
    types = fields.Many2one('od.product.type',string='Type')
    name = fields.Char(string="Description")
    vat = fields.Float(string="Vat %",readonly=True,digits=dp.get_precision('Account'))
    
    qty = fields.Float(string="Qty",digits=dp.get_precision('Account'))
    unit_cost_local = fields.Float(string="Current Unit Cost",readonly=True,digits=dp.get_precision('Account'))
    unit_price = fields.Float(string="Current Unit Selling",readonly=True,digits=dp.get_precision('Account'))
    line_cost = fields.Float(string="Current Total Cost",readonly=True,digits=dp.get_precision('Account'))
    line_selling = fields.Float(string="Current Total Selling",readonly=True,digits=dp.get_precision('Account'))
    
    
    @api.onchange('add_new_item')
    def onchange_add_new_item(self):
        if self.add_new_item:
            self.is_change_cost = True
            self.is_change_price = True
            self.is_change_qty = True
    def get_line_price(self,qty,amount):
        return qty * amount
     
    @api.onchange('part_no')
    def onchange_product_id(self):
        if self.part_no:
            desc = (self.part_no and self.part_no.description_sale) or (self.part_no and self.part_no.description) or (self.part_no and self.part_no.name)
            self.name = desc
            self.types = self.part_no and self.part_no.od_pdt_type_id and self.part_no.od_pdt_type_id.id or False
      
    @api.onchange('change_qty')
    def onchange_change_qty(self):
        if self.change_qty <= 0.0:
            raise Warning("Change Qty cannot be zero. To remove a product choose 'Remove' option")   
                
    @api.one
    @api.depends('qty','unit_price','change_qty','change_price','change_cost','remove_item')
    def _od_get_total_price(self):
        self.total_price = self.get_line_price(self.qty,self.unit_price)
        if self.remove_item:
            self.new_total_price = 0.0
            self.new_total_cost = 0.0
        else:
            self.new_total_price = self.get_line_price(self.change_qty,self.change_price)
            self.new_total_cost = self.get_line_price(self.change_qty,self.change_cost)
    

# class ChangeMatOptLine(models.Model):
#     _name ='change.mat.opt.line'
#     _inherit = "change.mat.line" 
#     line_id = fields.Many2one('od.cost.mat.optional.item.line',required=False)       

class ChangeMatExtraLine(models.Model):
    _name ='change.mat.extra.line'
    _inherit = "change.mat.line"
    line_id = fields.Many2one('od.cost.mat.extra.expense.line',required=False)
    
class ChangeTrn(models.Model):
    _name ='change.trn'
    _inherit = "change.mat.line"
    line_id = fields.Many2one('od.cost.trn.customer.training.line',required=False)

class ChangeTrnExtra(models.Model):
    _name ='change.trn.extra'
    _inherit = "change.mat.line"
    line_id = fields.Many2one('od.cost.trn.customer.training.extra.expense.line',required=False)

class ImpTechLine(models.Model):
    _name ='change.imp.tech'
    _inherit = "change.mat.line"
    line_id = fields.Many2one('od.cost.imp.tech.line',required=False)
    
class ImpTechLineExtra(models.Model):
    _name ='change.imp.tech.extra'
    _inherit = "change.mat.line"
    line_id = fields.Many2one('od.cost.bim.beta.implimentation.extra.expense.line',required=False)
    
class OutImp(models.Model):
    _name ='change.out.imp'
    _inherit = "change.mat.line"
    line_id = fields.Many2one('od.cost.oim.implimentation.price.line',required=False)

class OutImpExtra(models.Model):
    _name ='change.out.imp.extra'
    _inherit = "change.mat.line"
    line_id = fields.Many2one('od.cost.oim.extra.expenses.line',required=False)
    
class PsVendor(models.Model):
    _name ='change.ps.vendor'
    _inherit = "change.mat.line"
    line_id = fields.Many2one('od.cost.ps.vendor.line',required=False)
    
class InfoSecTechline(models.Model):
    _name ='change.infosec.tech'
    _inherit = "change.mat.line"
    line_id = fields.Many2one('od.cost.is.tech.line',required=False)
    
class InfoSecTechExtraline(models.Model):
    _name ='change.infosec.extra'
    _inherit = "change.mat.line"
    line_id = fields.Many2one('od.cost.is.extra.expense.line',required=False)
    
class InfoSecSubline(models.Model):
    _name ='change.infosec.sub'
    _inherit = "change.mat.line"
    line_id = fields.Many2one('od.cost.is.subcontractor.line',required=False)
    
class InfoSecVendorline(models.Model):
    _name ='change.infosec.vendor'
    _inherit = "change.mat.line"
    line_id = fields.Many2one('od.cost.is.vendor.line',required=False)
    

class ImpManpower(models.Model):
    _name ='change.imp.manpower'
    _inherit = "change.mat.line"
    line_id = fields.Many2one('od.cost.bim.beta.manpower.manual.line',required=False)
    
class AmcTech(models.Model):
    _name ='change.amc.tech'
    _inherit = "change.mat.line"
    line_id = fields.Many2one('od.cost.amc.tech.line',required=False)

class AmcSpare(models.Model):
    _name ='change.amc.spare'
    _inherit = "change.mat.line"
    line_id = fields.Many2one('od.cost.bmn.spareparts.beta.it.maintenance.line',required=False)

class AmcExtra(models.Model):
    _name ='change.amc.extra'
    _inherit = "change.mat.line"
    line_id = fields.Many2one('od.cost.bmn.beta.it.maintenance.extra.expense.line',required=False)

class AmcOutPrevent(models.Model):
    _name ='change.amc.out.prevent'
    _inherit = "change.mat.line"
    line_id = fields.Many2one('od.cost.omn.out.preventive.maintenance.line',required=False)

class AmcOutRemed(models.Model):
    _name ='change.amc.out.remed'
    _inherit = "change.mat.line"
        
    line_id = fields.Many2one('od.cost.omn.out.remedial.maintenance.line',required=False)

class AmcPrevent(models.Model):
    _name ='change.amc.prevent'
    _inherit = "change.mat.line"
    line_id = fields.Many2one('od.cost.bmn.it.preventive.line',required=False)

class AmcRemed(models.Model):
    _name ='change.amc.remed'
    _inherit = "change.mat.line"
    line_id = fields.Many2one('od.cost.bmn.it.remedial.line',required=False)

class AmcOutSpare(models.Model):
    _name ='change.amc.out.spare'
    _inherit = "change.mat.line"
    line_id = fields.Many2one('od.cost.omn.spare.parts.line',required=False)



class AmcOutExtra(models.Model):
    _name ='change.amc.out.extra'
    _inherit = "change.mat.line"
    line_id = fields.Many2one('od.cost.omn.maintenance.extra.expense.line',required=False)


class OmTech(models.Model):
    _name ='change.om.tech'
    _inherit = "change.mat.line"
    line_id = fields.Many2one('od.cost.om.tech.line',required=False)

class OmResident(models.Model):
    _name ='change.om.resident'
    _inherit = "change.mat.line"
    line_id = fields.Many2one('od.cost.om.residenteng.line',required=False)

class OmTool(models.Model):
    _name ='change.om.tool'
    _inherit = "change.mat.line"
    line_id = fields.Many2one('od.cost.om.eqpmentreq.line',required=False)

class OmExtra(models.Model):
    _name ='change.om.extra'
    _inherit = "change.mat.line"
    line_id = fields.Many2one('od.cost.om.extra.line',required=False)
    



