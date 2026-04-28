# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from pprint import pprint
from datetime import datetime
class project_bulk_activity_wiz(models.TransientModel):
    _name = 'project.bulk.activity.wiz'

    project_id = fields.Many2one('project.project',string="Project")
    def get_project_ob(self):
        context = self._context
        project_id = context.get('active_id',False)
        project_obj = self.env['project.project'].browse(project_id)
        return project_obj
    
    def default_get(self, cr, uid, fields, context=None):
        """
        This function gets default values
        """
        res = super(project_bulk_activity_wiz, self).default_get(cr, uid, fields, context=context)
        if context is None:
            context = {}
        record_id = context and context.get('active_id', False) or False
#         context['project_id'] =record_id
        res['project_id'] = record_id
        return res


    def od_create_activities(self,wiz_line):
        project_obj = self.get_project_ob()
        project_task = self.env['project.task']
        project_id = project_obj.id
        owner_id = project_obj.od_owner_id and project_obj.od_owner_id.id or False
        partner_id = project_obj.partner_id and project_obj.partner_id.id or False
        
        for line in wiz_line:
            imp_id = line.implementation_line_id and line.implementation_line_id.id or False
            #vals = project_task.onchange_imp_id(imp_id)
            date_start = line.start_date
            date_end = line.end_date
            od_type = 'activities'
            #Calling onchange functions of project task to get planned hour and end time
            #planned_hour = vals['value']['planned_hours']
            planned_hour = project_task.get_time_diff2(date_start, date_end)
            #end_time = project_task.onchange_date_start_end(date_start,od_type,planned_hour)
            #date_end = end_time['value']['date_end']
            vals ={
                'name':line.name,
                'od_parent_id':line.parent_id and line.parent_id.id or False,
                'od_type':od_type,
                'od_state':line.parent_id and line.parent_id.od_state.id or False,
                'project_id':line.project_id and line.project_id.id or False,
                'od_owner_id':line.owner_id and line.owner_id.id or False,
                'od_common_partner_id': line.project_id and line.project_id.partner_id.id or False,
                'od_opp_id': line.opp_id and line.opp_id.id or False,
                'user_id': line.assigned_to and line.assigned_to.id or False,
                'reviewer_id': line.reviewer_id and line.reviewer_id.id or False,
                'od_implementation_id': imp_id,
                'date_start': date_start,
                'date_end': date_end,
                'planned_hours': planned_hour,
                'b_plan_hr':planned_hour,
                'od_access_method': line.access_method,
                'od_activity_technical_obj': line.activity_obj,
                'od_eqp_application': line.equipment,
                'od_prior_arrangement': line.prior_arragmnt,
                'od_help_desk_issue_id':line.help_desk_id and line.help_desk_id.id or False
            }
            project_task.create(vals)
            
        
        return True
            
    
    @api.one
    def generate_bulk_activities(self):
        wiz_line = self.wiz_line
        self.od_create_activities(wiz_line)

    

    def od_get_company_id(self):
        return self.env.user.company_id
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    wiz_line = fields.One2many('project.bulk.activity.wiz.line','wiz_id')


class project_bulk_activity_wiz_line(models.TransientModel):
    _name = 'project.bulk.activity.wiz.line'
    
#     def od_get_default_proj_id(self):
#         context = self._context
#         print " line context>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",context
#         project_id = self.wiz_id.project_id.id
#         return project_id
    
    
    def default_get(self, cr, uid, fields, context=None):
        """
        This function gets default values
        """
        res = super(project_bulk_activity_wiz_line, self).default_get(cr, uid, fields, context=context)
        if context is None:
            context = {}
        res['reviewer_id'] = uid
        return res

    
    wiz_id = fields.Many2one('project.bulk.activity.wiz',string="Wizard")
    project_id = fields.Many2one('project.project',string="Project")
    parent_id = fields.Many2one('project.task',string="Milestone")
    name = fields.Char(string='Name')
    assigned_to = fields.Many2one('res.users',string='Assigned to')
    reviewer_id = fields.Many2one('res.users',string='Reviewer')
    owner_id =fields.Many2one('res.users',string='Owner')
    access_method = fields.Selection([('onsite','On Site'),('remote','Remote'),('phone_support','Phone Support')],string='Access Method')
    opp_id = fields.Many2one('crm.lead',string='Opportunity')
    implementation_line_id  =fields.Many2one('od.implementation', string="Implementation Code")
    start_date = fields.Datetime('Starting Date')
    end_date = fields.Datetime('Ending Date')
    activity_obj = fields.Text(string='Activity Technical Objective')
    equipment = fields.Text(string='Equipment/Applications')
    prior_arragmnt = fields.Text(string='Prior Arrangements Required')
    help_desk_id= fields.Many2one('crm.helpdesk',string="Help Desk")
    
class project_project(models.Model):
    _inherit ='project.project'
    
    @api.multi
    def project_bulk_activities_issue(self):
        return {
              'name': _('Create Bulk Activities'),
              'view_type': 'form',
              "view_mode": 'form',
              'res_model': 'project.bulk.activity.wiz',
              'type': 'ir.actions.act_window',
              'target':'new',
              }
