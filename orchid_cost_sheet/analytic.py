# -*- coding: utf-8 -*-
from openerp import models, fields, api, _

class account_analytic_account(models.Model):
    _inherit = "account.analytic.account"
       
    od_cost_sheet_id = fields.Many2one('od.cost.sheet',string="Cost Sheet",readonly=True)

    od_cost_centre_id =fields.Many2one('od.cost.centre',string='Cost Centre')
    od_branch_id =fields.Many2one('od.cost.branch',string='Branch',)
    od_division_id = fields.Many2one('od.cost.division',string='Division')
    lead_id = fields.Many2one('crm.lead',string="Opportunity",related="od_cost_sheet_id.lead_id",readonly=True)
    
    od_manual = fields.Boolean("Manual Link")
    cost_centre_id =fields.Many2one('od.cost.centre',string='M Cost Centre')
    branch_id =fields.Many2one('od.cost.branch',string='M Branch')
    division_id = fields.Many2one('od.cost.division',string='M Division')
   
    op_stage_id = fields.Many2one('crm.case.stage',string="Opp Stage",related="lead_id.stage_id",readonly=True)    
    op_expected_booking = fields.Date(string="Opp Expected Booking",related="lead_id.date_action",readonly=True)    
    sale_team_id = fields.Many2one('crm.case.section',string="Sale Team",related="lead_id.section_id",readonly=True)
    op_stage_id = fields.Many2one('crm.case.stage',string="Opp Stage",related="lead_id.stage_id",readonly=True)    
    fin_approved_date = fields.Datetime(string="Finance Approved Date",related="od_cost_sheet_id.approved_date",readonly=True)
    od_closing_date = fields.Date(string="Closing Date")
    

class project_project(models.Model):
    _inherit ='project.project'


    @api.one
    def od_get_sales_order_count(self):
        sale_order = self.env['sale.order']
        analytic_id = self.analytic_account_id and self.analytic_account_id.id
        domain =[('project_id','=',analytic_id)]
        count =len(sale_order.search(domain))
        self.od_sale_count = count
            
    @api.one
    def od_get_no_of_change_mgmt(self):
        cost_sheet_id = self.od_cost_sheet_id and self.od_cost_sheet_id.id or False
        cm_recs = self.env['change.management'].search([('cost_sheet_id','=', cost_sheet_id)])
        self.count_change_mgmt = len(cm_recs)

        
    @api.one
    def od_get_activity_count(self):
        activity_obj = self.env['project.task']
        domain =[('od_type','=','activities'),('project_id','=',self.id)]
        count =len(activity_obj.search(domain))
        self.activity_count = count
    @api.one
    def od_get_milestone_count(self):
        activity_obj = self.env['project.task']
        domain =[('od_type','=','milestone'),('project_id','=',self.id)]
        count =len(activity_obj.search(domain))
        self.milestone_count = count
    @api.one
    def od_get_workpackage_count(self):
        activity_obj = self.env['project.task']
        domain =[('od_type','=','workpackage'),('project_id','=',self.id)]
        count =len(activity_obj.search(domain))
        self.workpackage_count = count
        
    od_sale_count = fields.Integer(string="Sales Orders",compute="od_get_sales_order_count")
    od_cost_sheet_id = fields.Many2one('od.cost.sheet',string="Cost Sheet",readonly=True,related="analytic_account_id.od_cost_sheet_id")
    count_change_mgmt = fields.Integer(string="Change Management Count",compute="od_get_no_of_change_mgmt")
    
    technical_consultant1_id = fields.Many2one('res.users',string="Technical Consultant 1")
    technical_consultant2_id = fields.Many2one('res.users',string="Technical Consultant 2")
    activity_count = fields.Integer(string="Activities",compute="od_get_activity_count")
    milestone_count = fields.Integer(string="Milestone",compute="od_get_milestone_count")
    workpackage_count = fields.Integer(string="Work Package",compute="od_get_workpackage_count")
    
    @api.multi
    def od_open_sales_order(self):
        sales_order = self.env['sale.order']
        analytic_id = self.analytic_account_id and self.analytic_account_id.id
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
        cs_id = self.od_cost_sheet_id and self.od_cost_sheet_id.id or False
        context = self.env.context
        ctx = context.copy()
        ctx['change'] = True
        ctx['default_cost_sheet_id'] = cs_id
        ctx['default_branch_id'] = self.od_branch_id and self.od_branch_id.id or False
        
        if cs_id:
            domain = [('cost_sheet_id','=',cs_id)]
            return {
                'domain':domain,
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'change.management',
                'type': 'ir.actions.act_window',
                'context':ctx,
            }

    
    @api.multi
    def od_open_activities(self):
        activity_obj = self.env['project.task']
        domain =[('od_type','=','activities'),('project_id','=',self.id)]
        activities = activity_obj.search(domain)
        activity_ids = [activity.id for activity in activities]
        dom = [('id','in',activity_ids)]
        return {
            'domain':dom,
            'view_type': 'form',
            'view_mode': 'kanban,tree,form',
            'res_model': 'project.task',
            'context':{'default_project_id':self.id,
                       'default_od_type':'activities'
                       
                       },
            'type': 'ir.actions.act_window',
        }
    @api.multi
    def od_open_milestone(self):
        activity_obj = self.env['project.task']
        domain =[('od_type','=','milestone'),('project_id','=',self.id)]
        activities = activity_obj.search(domain)
        activity_ids = [activity.id for activity in activities]
        dom = [('id','in',activity_ids)]
        return {
            'domain':dom,
            'view_type': 'form',
            'view_mode': 'kanban,tree,form',
            'res_model': 'project.task',
            'context':{'default_project_id':self.id,
                       'default_od_type':'activities',
                       },
            'type': 'ir.actions.act_window',
        }
    @api.multi
    def od_open_workpackage(self):
        activity_obj = self.env['project.task']
        domain =[('od_type','=','workpackage'),('project_id','=',self.id)]
        activities = activity_obj.search(domain)
        activity_ids = [activity.id for activity in activities]
        dom = [('id','in',activity_ids)]
        return {
            'domain':dom,
            'view_type': 'form',
            'view_mode': 'kanban,tree,form',
            'res_model': 'project.task',
            'context':{'default_project_id':self.id,
                       'default_od_type':'activities'
                       },
            'type': 'ir.actions.act_window',
        }
