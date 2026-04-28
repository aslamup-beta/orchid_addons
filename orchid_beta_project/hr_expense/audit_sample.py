# -*- coding: utf-8 -*-
from openerp import models,fields,api,_
from openerp.exceptions import Warning
class audit_sample(models.Model):
    _name ="audit.sample"
    
    @api.one 
    @api.depends('post_sale_sample_line')
    def _get_avg_score(self):
#         if self.post_sale_sample_line and self.type=='post_sales':
#             self.avg_score = sum([x.score for x in self.post_sale_sample_line ])/float(len([x.score for x in self.post_sale_sample_line ]))
#         if self.type !='post_sales':
        avg_score = sum([x.final_score for x in self.comp_line])
        if avg_score >100.0 and self.type not in ('sales_acc_mgr','pmo','hoo','bdm_sec','bdm_net','bdm','sm'):
            avg_score =100.0
        self.avg_score = avg_score
        
        
    @api.one 
    @api.depends('commit_gp_line','achieved_gp_line')
    def _get_total(self):
        self.commit_total = sum([x.gp for x in self.commit_gp_line]) 
        self.achieved_total =  sum([x.gp for x in self.achieved_gp_line])  
    name = fields.Char(string="Name",required=True)
    date_start = fields.Date(string="Date Start")
    date_end = fields.Date(string="Date End")
    aud_temp_id = fields.Many2one('audit.template',string="Audit Template")
    type = fields.Selection([('post_sales','Post Sales'),('pre_sales','Pre-Sales Engineer'),
                             ('pre_sales_mgr','Pre-Sales Manager'),('sales_acc_mgr','Sales Account Manager'),
                             ('service_sale_spl','Service Sale Specialist'),
                             ('sm','Sales Manager'),
                             ('bdm','BDM'), ('bdm_sec','BDM-SEC'),('bdm_net','BDM-NET-DC'),('bdm_dc','BDM-DC'),('bdm_ksa','BDM-KSA'),('ttl','Technical Team Leader'),
                             ('pm','Project Manager'),('pmo','PMO Director'),('pdm','Project Department Manager'),
                             ('tc','Technology Consultant'),('tum','Technology Unit Manager'),('sde','Service Desk Engineer'),('sdm','Service Desk Manager'),
                             ('hoo','Head Of Operation'),
                             ('sde_ksa','Service Desk Engineer KSA'),
                             ('po_officer','Purchase Officer'),
                             
                             ],string="Type",required=True)
    
    employee_id = fields.Many2one('hr.employee',string="Employee")
    company_id = fields.Many2one('res.company',string="Company",related='employee_id.company_id',store=True)
    method = fields.Text(string="Method")
    avg_score = fields.Float(string="Monthly Avg Score",compute="_get_avg_score")
    post_sale_sample_line = fields.One2many('post.sales.comp.sample','sample_id',string="Post Sales Samples")
    utl_sample_line = fields.One2many('ttl.utl.sample','sample_id',string="Utilization Component")
    ttl_fot_line = fields.One2many('ttl.ontime.sample','sample_id',string="Utilization FOT")
    comp_line = fields.One2many('component.line','sample_id',string="Component Line")
    opp_sample_line = fields.One2many('presale.opp.sample','sample_id',string="Presales Opp Samples")
    team_line = fields.One2many('team.score.line','sample_id',string="Team Score")
    team_day_line = fields.One2many('team.day.line','sample_id',string="Team Score")
    team_hd_line = fields.One2many('team.hd.line','sample_id',string="Team Score")
    commit_gp_line = fields.One2many('commit.gp.sample.line','sample_id',string="Commit GP Samples")
    commit_gp_locked = fields.Boolean(string="Commit GP Sample Generation Locked")
    achieved_gp_line = fields.One2many('achieved.gp.sample.line','sample_id',string="Commit GP Samples")
    commit_total = fields.Float(string="Commit Total",compute="_get_total")
    achieved_total = fields.Float(string="Achieved Total",compute="_get_total")
    utilization = fields.Float(string="Utilization")
    target = fields.Float(string="Monthly Target")
    planned_invoice_line = fields.One2many('planned.analytic.invoice.line','sample_id',string="Planned Invoices")
    actual_invoice_line = fields.One2many('actual.analytic.invoice.line','sample_id',string="Actual Invoices")
    dayscore_line = fields.One2many('pm.dayscore.line','sample_id',string="Details")
    sde_day_score_line = fields.One2many('sde.dayscore.line','sample_id',string="Details")
    cost_control_line = fields.One2many('pm.cost.control.line','sample_id',string="Details")
    invoice_schedule_line = fields.One2many('pm.invoice.schedule.line','sample_id',string="Details")
    pm_sch_line = fields.One2many('pm.sch.control.line','sample_id',string="Details")
    
    compliance_line  =  fields.One2many('pm.compliance.line','sample_id',string="Details")
    bmd_costsheet_line = fields.One2many('bdm.costsheet.sample.line','sample_id',string="Details")
    bdm_sec_sample_line = fields.One2many('bdm.sec.sample.line','sample_id',string="Details")
    bdm_net_sample_line = fields.One2many('bdm.net.sample.line','sample_id',string="Details")
    bdm_net_sample_line_extra = fields.One2many('bdm.net.sample.line.extra','sample_id',string="Details")
    
    bdm_dc_sample_line = fields.One2many('bdm.dc.sample.line','sample_id',string="Details")
    
    bdm_sec_pip_sample_line = fields.One2many('bdm.sec.pip.sample.line','sample_id',string="Details")
    bdm_net_pip_sample_line = fields.One2many('bdm.net.pip.sample.line','sample_id',string="Details")
    bdm_dc_pip_sample_line = fields.One2many('bdm.dc.pip.sample.line','sample_id',string="Details")
    bdm_ksa_sample_line =  fields.One2many('bdm.ksa.sample.line','sample_id',string="Details")
    pmo_open_project_line = fields.One2many('pmo.open.project.sample','sample_id',string="Details")
    pmo_closed_project_line = fields.One2many('pmo.closed.project.sample','sample_id',string="Details")
    tc_tech_comp_line =  fields.One2many('tc.tech.component.line','sample_id',string="Details")
    tc_presale_comp_line =  fields.One2many('tc.presale.comp.line','sample_id',string="Details")
    my_comp_line = fields.One2many('my.component.line','sample_id',string="Details")
    hd_line = fields.One2many('help.desk.sample.line','sample_id',string="Details")
    tum_bdm_sample_line = fields.One2many('tum.bdm.sample.line','sample_id',string="Details")
    tum_bdm_comp_line =fields.One2many('tum.bdm.component.line','sample_id',string="Details")
    
    tum_mp_sale_line = fields.One2many('tum.mp.sample.line','sample_id',string="Details")
    tum_tc_comp_line = fields.One2many('tum.tc.component.line','sample_id',string="Details")
    tum_staff_data_line = fields.One2many('tum.staff.line','sample_id',string="Details")
    tum_staff_data_detail_line = fields.One2many('tum.staff.detail.line','sample_id',string="Details")
    tum_sale_enab_line = fields.One2many('tum.bdm.sale.enablement.session','sample_id',string="Details")
    tum_bdm_score = fields.Float(string="BDM Score")
    tum_sale_eanb_score = fields.Float(string="Sale Enablement Score")
    tum_mp_sale_detail_line = fields.One2many('tum.mp.sale.detail.line','sample_id',string="Details")
    tum_bdm_branch_line = fields.One2many('tum.bdm.branch.line','sample_id',string="Details")
    sm_cf_line = fields.One2many('sm.cf.data','sample_id',string="Details")
    sm_cf_summary = fields.One2many('sm.cf.summary','sample_id',string="Details")
    sm_cert_detail =fields.One2many('sm.certificate.data','sample_id',string="Details")
    sm_cert_summary =fields.One2many('sm.certificate.summary','sample_id',string="Details")
    
    sm_enab_detail =fields.One2many('sm.enab.data','sample_id',string="Details")
    sm_enab_summary =fields.One2many('sm.enab.summary','sample_id',string="Details")
    po_sample_line =fields.One2many('po.sample.line','sample_id',string="Details")
    
    
    def update_closed_project_data(self,vals):
        pmo_closed_project = self.env['pmo.closed.project.sample']
        sample_id = self.id 
        for _,_,val in vals:
            analytic_id = val.get('analytic_id')
            closed_data = pmo_closed_project.search([('sample_id','=',sample_id),('analytic_id','=',analytic_id)])
            if closed_data:
                closed_data.write(val)
            else:
                pmo_closed_project.create(val)
        return True




class HelpDeskSample(models.Model):
    _name ='help.desk.sample.line'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    hd_id = fields.Many2one('crm.helpdesk',string="Cost Sheet")
    score = fields.Float(string="Score")
     
    @api.multi
    def btn_open(self):
       
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'crm.helpdesk',
                'res_id':self.hd_id and self.hd_id.id or False,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }


class my_component_line(models.Model):
    _name = 'my.component.line'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    name = fields.Char(string="Component")
    weight = fields.Float(string="Weight")
    score = fields.Float(string="Score")
    final_score = fields.Float(string="Final Score")


class tc_tech_component_line(models.Model):
    _name = 'tc.tech.component.line'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    name = fields.Char(string="Component")
    weight = fields.Float(string="Weight")
    score = fields.Float(string="Score")
    final_score = fields.Float(string="Final Score")
    
class tc_presale_comp_line(models.Model):
    _name = 'tc.presale.comp.line'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    name = fields.Char(string="Component")
    weight = fields.Float(string="Weight")
    score = fields.Float(string="Score")
    final_score = fields.Float(string="Final Score")
    


class PmoOpenProjects(models.Model):
    _name ="pmo.open.project.sample"
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    analytic_id = fields.Many2one('account.analytic.account',string="Analytic/Project")
    paid = fields.Float(string="Paid to Supplier")
    collected = fields.Float(string="Collected From Customer")
    inv_amount = fields.Float(string="Invoice Value")
    project_value = fields.Float(string="Project Value")
    manpower_cost = fields.Float(string="Manpower Cost")
    general_cost =fields.Float(string="General Cost")
    actual_outsource =fields.Float(string="Actual Outsourced")
    @api.multi
    def btn_open(self):
       
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.analytic.account',
                'res_id':self.analytic_id and self.analytic_id.id or False,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }
    
class PmoClosedProjects(models.Model):
    _name ="pmo.closed.project.sample"
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    analytic_id = fields.Many2one('account.analytic.account',string="Analytic/Project")
    paid = fields.Float(string="Paid to Supplier")
    manpower_cost = fields.Float(string="Manpower Cost")
    general_cost =fields.Float(string="General Cost")
    collected = fields.Float(string="Collected From Customer")
    project_value = fields.Float(string="Project Value")
    inv_amount = fields.Float(string="Invoice Value")
    @api.multi
    def btn_open(self):
       
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.analytic.account',
                'res_id':self.analytic_id and self.analytic_id.id or False,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }
    
class BdmSecuritySample(models.Model):
    _name ='bdm.sec.sample.line'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    cost_sheet_id = fields.Many2one('od.cost.sheet',string="Cost Sheet")
    product_group_id = fields.Many2one('od.product.group',string="Product Group")
    sales = fields.Float(string="Sales")
    sales_aftr_disc = fields.Float(string="Sales After Discount")
    cost = fields.Float(string="Cost")
    profit = fields.Float(string="Profit")
    profit_percent = fields.Float(string="Profit Percentage")
    manpower_cost = fields.Float("Manpower Cost")
    gp = fields.Float(string="GP")
     
    @api.multi
    def btn_open(self):
       
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'od.cost.sheet',
                'res_id':self.cost_sheet_id and self.cost_sheet_id.id or False,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }

class BdmSecurityPipSample(models.Model):
    _name ='bdm.sec.pip.sample.line'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    cost_sheet_id = fields.Many2one('od.cost.sheet',string="Cost Sheet")
    product_group_id = fields.Many2one('od.product.group',string="Product Group")
    sales = fields.Float(string="Sales")
    sales_aftr_disc = fields.Float(string="Sales After Discount")
    cost = fields.Float(string="Cost")
    profit = fields.Float(string="Profit")
    profit_percent = fields.Float(string="Profit Percentage")
    manpower_cost = fields.Float("Manpower Cost")
    gp = fields.Float(string="GP")
    
     
    @api.multi
    def btn_open(self):
       
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'od.cost.sheet',
                'res_id':self.cost_sheet_id and self.cost_sheet_id.id or False,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }
    
class BdmNetwrokSample(models.Model):
    _name ='bdm.net.sample.line'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    cost_sheet_id = fields.Many2one('od.cost.sheet',string="Cost Sheet")
    product_group_id = fields.Many2one('od.product.group',string="Product Group")
    sales = fields.Float(string="Sales")
    sales_aftr_disc = fields.Float(string="Sales After Discount")
    cost = fields.Float(string="Cost")
    profit = fields.Float(string="Profit")
    profit_percent = fields.Float(string="Profit Percentage")
    manpower_cost = fields.Float("Manpower Cost")
    gp = fields.Float(string="GP")
    
     
    @api.multi
    def btn_open(self):
       
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'od.cost.sheet',
                'res_id':self.cost_sheet_id and self.cost_sheet_id.id or False,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }
    

class BdmNetwrokSampleExtra(models.Model):
    _name ='bdm.net.sample.line.extra'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    cost_sheet_id = fields.Many2one('od.cost.sheet',string="Cost Sheet")
    product_group_id = fields.Many2one('od.product.group',string="Product Group")
    sales = fields.Float(string="Sales")
    sales_aftr_disc = fields.Float(string="Sales After Discount")
    cost = fields.Float(string="Cost")
    profit = fields.Float(string="Profit")
    profit_percent = fields.Float(string="Profit Percentage")
    manpower_cost = fields.Float("Manpower Cost")
    gp = fields.Float(string="GP")
    brand_id =fields.Many2one('od.product.brand',string="Brand")
    part_no =fields.Many2one('product.product',string="Part No")
    
     
    @api.multi
    def btn_open(self):
       
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'od.cost.sheet',
                'res_id':self.cost_sheet_id and self.cost_sheet_id.id or False,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }
    

class BdmNetwrokPipSample(models.Model):
    _name ='bdm.net.pip.sample.line'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    cost_sheet_id = fields.Many2one('od.cost.sheet',string="Cost Sheet")
    product_group_id = fields.Many2one('od.product.group',string="Product Group")
    sales = fields.Float(string="Sales")
    sales_aftr_disc = fields.Float(string="Sales After Discount")
    cost = fields.Float(string="Cost")
    profit = fields.Float(string="Profit")
    profit_percent = fields.Float(string="Profit Percentage")
    manpower_cost = fields.Float("Manpower Cost")
    gp = fields.Float(string="GP")
     
    @api.multi
    def btn_open(self):
       
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'od.cost.sheet',
                'res_id':self.cost_sheet_id and self.cost_sheet_id.id or False,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }


class BdmDCSample(models.Model):
    _name ='bdm.dc.sample.line'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    cost_sheet_id = fields.Many2one('od.cost.sheet',string="Cost Sheet")
    product_group_id = fields.Many2one('od.product.group',string="Product Group")
    sales = fields.Float(string="Sales")
    sales_aftr_disc = fields.Float(string="Sales After Discount")
    cost = fields.Float(string="Cost")
    profit = fields.Float(string="Profit")
    profit_percent = fields.Float(string="Profit Percentage")
    manpower_cost = fields.Float("Manpower Cost")
    gp = fields.Float(string="GP")
    
     
    @api.multi
    def btn_open(self):
       
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'od.cost.sheet',
                'res_id':self.cost_sheet_id and self.cost_sheet_id.id or False,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }
    

class BdmDcPipSample(models.Model):
    _name ='bdm.dc.pip.sample.line'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    cost_sheet_id = fields.Many2one('od.cost.sheet',string="Cost Sheet")
    product_group_id = fields.Many2one('od.product.group',string="Product Group")
    sales = fields.Float(string="Sales")
    sales_aftr_disc = fields.Float(string="Sales After Discount")
    cost = fields.Float(string="Cost")
    profit = fields.Float(string="Profit")
    profit_percent = fields.Float(string="Profit Percentage")
    manpower_cost = fields.Float("Manpower Cost")
    gp = fields.Float(string="GP")
     
    @api.multi
    def btn_open(self):
       
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'od.cost.sheet',
                'res_id':self.cost_sheet_id and self.cost_sheet_id.id or False,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }
    


class BdmCostsheetSample(models.Model):
    _name ='bdm.costsheet.sample.line'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    cost_sheet_id = fields.Many2one('od.cost.sheet',string="Cost Sheet")
    gp = fields.Float(string="GP")
    
    
    @api.multi
    def btn_open(self):
       
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'od.cost.sheet',
                'res_id':self.cost_sheet_id and self.cost_sheet_id.id or False,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }

class BdmKSAsample(models.Model):
    _name ='bdm.ksa.sample.line'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    branch_id = fields.Many2one('od.cost.branch',string="Branch")
    gp_target = fields.Float(string="GP Target")
    gp = fields.Float(string="Achieved GP")
    branch_gp_point = fields.Float(string="Branch GP Point")
    month_incent = fields.Float(string="Monthly Incentive")
   
    
    


class compliance_line(models.Model):
    _name ="pm.compliance.line"
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    analytic_id = fields.Many2one('account.analytic.account',string="Analytic/Project")
    score = fields.Float("Score From Project")
    sale_value = fields.Float(string="Sale Value")
    sale_value_percent = fields.Float("%Sale Value")
    weight = fields.Float(string="Weight")
    form_wt = fields.Float(string="Form Weight")
    @api.multi
    def btn_open(self):
       
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.analytic.account',
                'res_id':self.analytic_id and self.analytic_id.id or False,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }


class invoice_schedule_line(models.Model):
    _name ="pm.invoice.schedule.line"
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    analytic_id = fields.Many2one('account.analytic.account',string="Analytic/Project")
    score = fields.Float("Score From Project")
    sale_value = fields.Float(string="Invoice Value")
    sale_value_percent = fields.Float("%Invoice Value")
    weight = fields.Float(string="Weight")
    form_wt = fields.Float(string="Form Weight")
    
    @api.multi
    def btn_open(self):
       
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.analytic.account',
                'res_id':self.analytic_id and self.analytic_id.id or False,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }



class cost_control_line(models.Model):
    _name ="pm.cost.control.line"
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    analytic_id = fields.Many2one('account.analytic.account',string="Analytic/Project")
    score = fields.Float("Score From Project")
    actual_gp = fields.Float(string="Actual Gp")
    original_gp = fields.Float(string="Original Gp")
    gp_value = fields.Float(string="Amended Gp (For Weight Calculation)")
    gp_value_percent = fields.Float("%GP Value")
    weight = fields.Float(string="Weight")
    form_wt = fields.Float(string="Form Weight")
    @api.multi
    def btn_open(self):
       
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.analytic.account',
                'res_id':self.analytic_id and self.analytic_id.id or False,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }

class PmScheduleControl(models.Model):
    _name ="pm.sch.control.line"
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    analytic_id = fields.Many2one('account.analytic.account',string="Analytic/Project")
    score = fields.Float("Score From Project")
    gp_value = fields.Float(string="GP Value")
    gp_value_percent = fields.Float("%GP Value")
    weight = fields.Float(string="Weight")
    form_wt = fields.Float(string="Form Weight")
    @api.multi
    def btn_open(self):
       
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.analytic.account',
                'res_id':self.analytic_id and self.analytic_id.id or False,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }


class pm_dayscore(models.Model):
    _name ="pm.dayscore.line"
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    analytic_id = fields.Many2one('account.analytic.account',string="Analytic/Project")
    cost_sheet_id = fields.Many2one('od.cost.sheet',string="Cost Sheet")
    score = fields.Float("Score From Project")
    sale_value = fields.Float(string="Sale Value")
    sale_value_percent = fields.Float("%Sale Value")
    weight = fields.Float(string="Weight")
    form_wt = fields.Float(string="Form Weight")
    @api.multi
    def btn_open(self):
       
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.analytic.account',
                'res_id':self.analytic_id and self.analytic_id.id or False,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }
        
    @api.multi
    def btn_open_cst(self):
       
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'od.cost.sheet',
                'res_id':self.cost_sheet_id and self.cost_sheet_id.id or False,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }


class sde_dayscore(models.Model):
    _name ="sde.dayscore.line"
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    analytic_id = fields.Many2one('account.analytic.account',string="Analytic/Project")
    cost_sheet_id = fields.Many2one('od.cost.sheet',string="Cost Sheet")
    score = fields.Float("Score From Project")
    sale_value = fields.Float(string="Sale Value")
    sale_value_percent = fields.Float("%Sale Value")
    weight = fields.Float(string="Weight")
    form_wt = fields.Float(string="Form Weight")
    @api.multi
    def btn_open(self):
       
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.analytic.account',
                'res_id':self.analytic_id and self.analytic_id.id or False,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }
        
    @api.multi
    def btn_open_cst(self):
       
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'od.cost.sheet',
                'res_id':self.cost_sheet_id and self.cost_sheet_id.id or False,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }






class PlannedInvoices(models.Model):
    _name ='planned.analytic.invoice.line'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    analytic_id = fields.Many2one('account.analytic.account',string="Analytic/Project")
    
    amount = fields.Float(string="Planned Amount")

class ActualInvoices(models.Model):
    _name ='actual.analytic.invoice.line'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    analytic_id = fields.Many2one('account.analytic.account',string="Analytic/Project")
    invoice_id = fields.Many2one('account.invoice',string="Invoice")
    amount = fields.Float(string="Invoice Amount")

class CommitGpSample(models.Model):
    _name ='commit.gp.sample.line'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    cost_sheet_id = fields.Many2one('od.cost.sheet',string="Cost Sheet")
    gp = fields.Float(string="GP")
    user_id = fields.Many2one('res.users',string="User")
    @api.multi
    def btn_open(self):
       
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'od.cost.sheet',
                'res_id':self.cost_sheet_id and self.cost_sheet_id.id or False,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }
    
class AchievedGpSample(models.Model):
    _name ='achieved.gp.sample.line'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    cost_sheet_id = fields.Many2one('od.cost.sheet',string="Cost Sheet")
    gp = fields.Float(string="GP")
    user_id = fields.Many2one('res.users',string="User")
    
    @api.multi
    def btn_open(self):
       
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'od.cost.sheet',
                'res_id':self.cost_sheet_id and self.cost_sheet_id.id or False,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }


class TeamScore(models.Model):
    _name ='team.score.line'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    user_id = fields.Many2one('res.users',string="User")
    score = fields.Float(string="Score")
    emp_score = fields.Float(string="Employee Score")
    

class TeamDayLine(models.Model):
    _name ='team.day.line'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    user_id = fields.Many2one('res.users',string="User")
    score = fields.Float(string="Score")

class TeamHDLine(models.Model):
    _name ='team.hd.line'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    user_id = fields.Many2one('res.users',string="User")
    score = fields.Float(string="Score")


class presale_opp_sample(models.Model):
    _name ='presale.opp.sample'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    opp_id = fields.Many2one('crm.lead',string="Opportunity",ondelete="cascade")
    required_date = fields.Date(string="Required On")
    user_id = fields.Many2one('res.users',string="User")
    score = fields.Float(string="Score")
    
    @api.multi
    def btn_open(self):
        model_data = self.env['ir.model.data']
        form_view = model_data.get_object_reference('crm', 'crm_case_form_view_oppor')
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'crm.lead',
                'res_id':self.opp_id and self.opp_id.id or False,
                'views': [(form_view and form_view[1] or False, 'form')],
                'type': 'ir.actions.act_window',
                'target': 'new',

            }

class post_sales_comp_sample(models.Model):
    _name ='post.sales.comp.sample'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    task_id = fields.Many2one('project.task',string="Activity",ondelete="cascade")
    score = fields.Float(string="Score")
    @api.multi
    def btn_open(self):
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'project.task',
                'res_id':self.task_id and self.task_id.id or False,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }
    
class ttl_utilization_sample(models.Model):
    _name ='ttl.utl.sample'
    user_id = fields.Many2one('res.users',string="User")
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    actual_time_spent = fields.Float(string="Actual Time Spent")
    available_time = fields.Float(string="Available Time")
    utl = fields.Float(string="Actual Utilization")
    planned_time = fields.Float(string="Planned Time")
    planned_utl = fields.Float(string="Planned Utilization")
class ttl_on_time_sample(models.Model):
    _name ='ttl.ontime.sample'
    user_id = fields.Many2one('res.users',string="User")
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    fot = fields.Float(string="Finished On Time")
    
    
class BdmTumSample(models.Model):
    _name ='tum.bdm.sample.line'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    branch_id = fields.Many2one('od.cost.branch',string="Branch")
    cost_sheet_id = fields.Many2one('od.cost.sheet',string="Cost Sheet")
    product_group_id = fields.Many2one('od.product.group',string="Product Group")
    sales = fields.Float(string="Sales")
    sales_aftr_disc = fields.Float(string="Sales After Discount")
    cost = fields.Float(string="Cost")
    profit = fields.Float(string="Profit")
    profit_percent = fields.Float(string="Profit Percentage")
    manpower_cost = fields.Float("Manpower Cost")
    manpower_sale = fields.Float("Manpower Sale")
    gp = fields.Float(string="GP")
    
    
    @api.multi
    def btn_open(self):
       
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'od.cost.sheet',
                'res_id':self.cost_sheet_id and self.cost_sheet_id.id or False,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }
    

class TumMpSaleSample(models.Model):
    _name ='tum.mp.sample.line'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    manpower_sale = fields.Float("MP Sale IN /Technology")
    target = fields.Float("Monthly Target")
    target_percent =  fields.Float("MP Sales IN/Monthly Target (%)")
    weight = fields.Float("Weight")
    score = fields.Float(string="Score")
    @api.multi
    def btn_open(self):
       
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'od.cost.sheet',
                'res_id':self.cost_sheet_id and self.cost_sheet_id.id or False,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }

class TumMPSaleDetail(models.Model):
    _name ='tum.mp.sale.detail.line'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    cost_sheet_id = fields.Many2one('od.cost.sheet',string="Cost Sheet")
    manpower_sale = fields.Float("Manpower Sale")
    approved_date = fields.Date(string="Approved Date")
    

class bdm_tum_component_line(models.Model):
    _name = 'tum.bdm.component.line'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    name = fields.Char(string="Component")
    weight = fields.Float(string="Weight")
    score = fields.Float(string="Submitted GP/ Monthly Target (%)")
    final_score = fields.Float(string="Score")


class tum_staff_line(models.Model):
    _name = 'tum.staff.line'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    branch_id = fields.Many2one('od.cost.branch',string="Branch")
    job_id = fields.Many2one('hr.job',string="Job")
    available = fields.Float(string="Available")
    required = fields.Float(string="Required")
    available= fields.Float(string="Available")
    req_avail =fields.Float(string="Required/Available")
    weight = fields.Float(string="Weight")
    score = fields.Float(string="Score")

class tum_staff_detail_line(models.Model):
    _name = 'tum.staff.detail.line'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    branch_id = fields.Many2one('od.cost.branch',string="Branch")
    job_id = fields.Many2one('hr.job',string="Job")
    user_id = fields.Many2one('res.users',string="Name")
    joining_date = fields.Date(string="Joining Date")
    termination_date = fields.Date(string="Termination Date")
    
class tum_tc_component_line(models.Model):
    _name = 'tum.tc.component.line'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    name = fields.Char(string="Component")
    weight = fields.Float(string="Weight")
    score = fields.Float(string="Score")
    final_score = fields.Float(string="Final Score")
    
    

class tum_bdm_branch_line(models.Model):
    _name = 'tum.bdm.branch.line'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    branch_id = fields.Many2one('od.cost.branch',string="Branch")
    branch_percent =fields.Float(string="Branch Percent")
    achieved_gp = fields.Float(string="Achieved GP")
    branch_target = fields.Float(string="Branch Target")
    ach_target = fields.Float(string="Achieved GP/Branch Target")
    score = fields.Float(string="Score")
    


class tum_bdm_sale_enablement_session(models.Model):
    _name = 'tum.bdm.sale.enablement.session'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    sale_enab_id = fields.Many2one('sale.enablement',string="Sale Enablement")
    score = fields.Float(string="Score")
    date = fields.Date(string="Date")
    user_id = fields.Many2one('res.users',string="Assigned By")
    division_id = fields.Many2one('od.cost.division',string="Technology Unit")
    
    
    @api.multi
    def btn_open(self):
       
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'sale.enablement',
                'res_id':self.sale_enab_id and self.sale_enab_id.id or False,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }
    
   


class sm_cf_data(models.Model):
    _name = 'sm.cf.data'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    user_id = fields.Many2one('res.users',string="User")
    month_target = fields.Float(string="Month Target")
    commit = fields.Float(string="Month Commit")
    achieved = fields.Float(string="Month Achieved")
    cf_fact = fields.Float(string="CF(%)")
    kpi_point = fields.Float(string="KPI Point")


class sm_cf_summary(models.Model):
    _name = 'sm.cf.summary'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    total_target = fields.Float(string="Total Month Target")
    total_commit = fields.Float(string="Total Month Commit")
    total_achieved = fields.Float(string="Total Month Achieved")
    cf = fields.Float(string="Average CF(%)")
    kpi_point = fields.Float(string="KPI Point")
    score = fields.Float(string="Score")


class sm_certificate_data(models.Model):
    _name = 'sm.certificate.data'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    user_id = fields.Many2one('res.users',string="User")
    required = fields.Boolean(string="Required")
    achieved = fields.Boolean(string="Achieved")
    kpi_point = fields.Float(string="KPI Point")
    score = fields.Float(string="Score")


class sm_certificate_summary(models.Model):
    _name = 'sm.certificate.summary'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    name = fields.Selection([('n_a','N/A'),('10','10')],string="Sales Manager Certificate KPI Point")
    score = fields.Float(string="Score")


class sm_enab_data(models.Model):
    _name = 'sm.enab.data'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    user_id = fields.Many2one('res.users',string="User")
    name = fields.Char(string="Name")
    achieved = fields.Boolean(string="Achieved")
    kpi_point = fields.Float(string="KPI Point")
    score = fields.Float(string="Score")

class sm_enab_summary(models.Model):
    _name = 'sm.enab.summary'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    name = fields.Selection([('n_a','N/A'),('10','10')],string="Sales Team Enablement Point")
    score = fields.Float(string="Score")

class po_sample_line(models.Model):
    _name = 'po.sample.line'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    po_id = fields.Many2one('purchase.order',string="PO")
    score = fields.Float(string="Score")

    


class component_line(models.Model):
    _name = 'component.line'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    name = fields.Char(string="Component")
    weight = fields.Float(string="Weight")
    score = fields.Float(string="Score")
    final_score = fields.Float(string="Final Score")


    