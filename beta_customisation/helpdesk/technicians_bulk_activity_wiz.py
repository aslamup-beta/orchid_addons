# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from pprint import pprint
from datetime import datetime
class technician_bulk_activity_wiz(models.TransientModel):
    _name = 'technician.bulk.activity.wiz'

    def od_create_activities(self,wiz_line):
        project_task = self.env['project.task']
        
        project_activity_dict = []
        for line in wiz_line:
            project_id = line.project_id and line.project_id.id or False
            project_obj = line.project_id
            owner_id = project_obj.od_owner_id and project_obj.od_owner_id.id or False
            partner_id = project_obj.partner_id and project_obj.partner_id.id or False
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
                'project_id':project_id,
                'od_owner_id':owner_id,
                'od_common_partner_id': partner_id,
                'od_opp_id': line.opp_id and line.opp_id.id or False,
                'user_id': line.assigned_to and line.assigned_to.id or False,
                'reviewer_id': owner_id,
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
            res = project_task.create(vals)
            project_activity_dict.append({project_id: [res.id]})
        return project_activity_dict
            
    @api.one
    def generate_bulk_activities(self):
        project_task = self.env['project.task']
        project = self.env['project.project']
        approval_form_obj = self.env['od.tech.ticket.approval']
        ticket_line_obj = self.env['od.tech.ticket.line']
        wiz_line = self.wiz_line
        dict_list = self.od_create_activities(wiz_line)
        #create approval form based on projects as 
        res = {k: [d.get(k) for d in dict_list] for k in set().union(*dict_list)}
        for key in res:
            ticket_ids = res[key]
            project_obj = project.search([('id','=',key)])
            approval_id = approval_form_obj.create({'name':project_obj.id,
                                              'user_id': project_obj.od_owner_id and project_obj.od_owner_id.id or False,
                                              'partner_id': project_obj.partner_id and project_obj.partner_id.id or False,
                                                })
            for ticket_id in ticket_ids:
                if ticket_id != None :
                    project_task_obj = project_task.search([('id','=',ticket_id)])
                    ticket_line_obj.create({'assigned_id': project_task_obj.user_id.id,
                                            'date_start': project_task_obj.date_start,
                                            'date_end': project_task_obj.date_end,
                                            'duration': project_task_obj.b_plan_hr,
                                            'status': project_task_obj.od_stage,
                                            'ticket_id': project_task_obj.id,
                                            'approval_form_id': approval_id.id
                        })
        
            approval_id.od1_send_mail('activity_approval_request_email_template')
        return True
                
                

            
    def od_get_company_id(self):
        return self.env.user.company_id
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    wiz_line = fields.One2many('technician.bulk.activity.wiz.line','wiz_id')


class technician_bulk_activity_wiz_line(models.TransientModel):
    _name = 'technician.bulk.activity.wiz.line'
    
    
    wiz_id = fields.Many2one('technician.bulk.activity.wiz',string="Wizard")
    project_id = fields.Many2one('project.project',string="Project")
    parent_id = fields.Many2one('project.task',string="Milestone")
    name = fields.Char(string='Name')
    assigned_to = fields.Many2one('res.users',string='Assigned to')
    reviewer_id = fields.Many2one('res.users',string='Reviewer')
    owner_id =fields.Many2one('res.users',string='Owner')
    access_method = fields.Selection([('onsite','On Site'),('remote','Remote'),('phone_support','Phone Support'), ('beta_ofc','In Beta IT Office')],string='Access Method')
    opp_id = fields.Many2one('crm.lead',string='Opportunity')
    start_date = fields.Datetime('Starting Date')
    end_date = fields.Datetime('Ending Date')
    activity_obj = fields.Text(string='Activity Technical Objective')
    equipment = fields.Text(string='Equipment/Applications')
    prior_arragmnt = fields.Text(string='Prior Arrangements Required')
    help_desk_id= fields.Many2one('crm.helpdesk',string="Help Desk")
    
