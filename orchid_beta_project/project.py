# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import datetime,timedelta
from dateutil import relativedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
import decimal
from openerp.exceptions import Warning
class od_project_phase(osv.osv):
    _name = 'od.project.phase'
    _columns = {
                'name':fields.char('Name',required=True),
                'groups_ids':fields.many2many('res.groups','project_status_group_rel','status_id','group_id','Groups')
                }

class od_project_category(osv.osv):
    _name = 'od.project.category'
    _columns = {
                'name':fields.char('Category'),
                'phase_id':fields.many2one('od.project.phase','Phase')
                }
class od_project_sub_category(osv.osv):
    _name = 'od.project.sub.category'
    _columns = {
                'name':fields.char('Category'),
                }
class od_task_checklist(osv.osv):
    _name= 'od.task.checklist'
    _columns = {
                'task_id':fields.many2one('project.task','Task'),
                'name':fields.char('Checklist'),
                # 'done':fields.boolean('Done'),
                'state': fields.selection([('done','Done'),('not_done','Not Done')],'Status')
                }

class issue(osv.osv):
    _inherit ='project.issue'
    _columns = {
                'od_log':fields.selection([('issue','Issue Log'),('change','Change Log'),('risk','Risk Log')],'Log'),
                'od_category_id':fields.many2one('od.project.category','Category'),
                }
class project_project(osv.osv):
    _inherit ='project.project'

    def od_map_all(self,cr,uid,ids,context=None):
        new_ids=self.search(cr,uid,[])
        for id in new_ids:
            self.od_map_analytic_account_state(cr,uid,[id],context)

    def od_map_analytic_account_state(self,cr,uid,ids,context=None):
        analytic = self.pool.get('account.analytic.account')
        for project in self.browse(cr,uid,ids,context=context):
            analytic_id = project.analytic_account_id and project.analytic_account_id.id or False
            if analytic_id:
                analytic_obj = analytic.browse(cr,uid,analytic_id)
                analytic_state = analytic_obj.state
                project.write({'state':analytic_state})
    def od_open_attachement(self,cr,uid,ids,context=None):
        model_name=self._name
        object_id = ids[0]
        domain = [('model_name','=',model_name),('object_id','=',object_id)]
        ctx = {'default_model_name':model_name,'default_object_id':object_id}
        return {
            'domain': domain,
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'od.attachement',
            'type': 'ir.actions.act_window',
            'context':ctx
        }
    def _od_attachement_count(self, cr, uid, ids, field_name, arg, context=None):
        res ={}
        for obj in self.browse(cr, uid, ids, context):
            attachement_ids = self.pool.get('od.attachement').search(cr, uid, [('model_name', '=', self._name),('object_id','=',ids[0])])
            if attachement_ids:
                res[obj.id] = len(attachement_ids)
        return res

    _columns = {
                'od_state':fields.many2one('od.project.phase','Project Phase',required=True),
                'od_attachement_count':fields.function(_od_attachement_count,type="integer",string="Total"),
#                 'od_branch_id':fields.many2one('od.cost.branch','Branch'),
                'od_quantity_max': fields.float("Prepaid Service Units"),
                }
    #Commented as not tested by aslam on 19/03/2025
#     def budget_comsumption_reminder(self, cr, uid, context=None):
#         template = 'od_budget_comsumption_reminder_mail'
#         ir_model_data = self.pool.get('ir.model.data')
#         proj_obj = self.pool.get('project.project')
#         user_obj = self.pool.get('res.users')
#         company_id = user_obj.browse(cr, uid, uid, context=context).company_id.id
#         if company_id == 6:
#             template = template +'_saudi'
#         template_id = ir_model_data.get_object_reference(cr,uid,'beta_customisation', template)[1]
#         open_projects  = proj_obj.search(cr,uid,[('state','not in',['cancelled', 'close']),('od_type_of_project','not in',['parent_level0','amc_view', 'o_m_view', 'credit', 'poc', 'comp_gen'])])
#         for proj_id in open_projects:
#             proj= proj_obj.browse(cr,uid,proj_id)
#             consumption = proj.r_budget_consumption
#             if 25.0 <consumption < 50.0 and not proj.od_consumed_25:
#                 self.pool.get('email.template').send_mail(cr, uid, template_id, proj_id, force_send=True, context=context)
#                 proj_obj.write(cr, uid, {'od_consumed_25': True}, context=context)
#             if 50.0 <consumption < 75.0 and not proj.od_consumed_50:
#                 self.pool.get('email.template').send_mail(cr, uid, template_id, proj_id, force_send=True, context=context)
#                 proj_obj.write(cr, uid, {'od_consumed_50': True}, context=context)
#             if 75.0 <consumption < 90.0 and not proj.od_consumed_75:
#                 self.pool.get('email.template').send_mail(cr, uid, template_id, proj_id, force_send=True, context=context)
#                 proj_obj.write(cr, uid, {'od_consumed_75': True}, context=context)
#             if consumption >90.0 and not proj.od_consumed_90:
#                 self.pool.get('email.template').send_mail(cr, uid, template_id, proj_id, force_send=True, context=context)
#                 proj_obj.write(cr, uid, {'od_consumed_90': True}, context=context)
#         return True
    
class od_product_sub_group(osv.osv):
    _inherit ="od.product.sub.group"
    _columns = {
                'phase_id':fields.many2one('od.project.phase','Phase')
                }
class task(osv.osv):
    _inherit = "project.task"
    def od_open_attachement(self,cr,uid,ids,context=None):
        model_name=self._name
        object_id = ids[0]
        domain = [('model_name','=',model_name),('object_id','=',object_id)]
        ctx = {'default_model_name':model_name,'default_object_id':object_id}
        return {
            'domain': domain,
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'od.attachement',
            'type': 'ir.actions.act_window',
            'context':ctx
        }
    def _od_attachement_count(self, cr, uid, ids, field_name, arg, context=None):
        res ={}
        for obj in self.browse(cr, uid, ids, context):
            attachement_ids = self.pool.get('od.attachement').search(cr, uid, [('model_name', '=', self._name),('object_id','=',ids[0])])
            if attachement_ids:
                res[obj.id] = len(attachement_ids)
        return res
    _columns = {

                'od_attachement_count':fields.function(_od_attachement_count,type="integer",string="Total"),
                'od_planned_time':fields.char('Planned Time'),
                # 'date_deadline':fields.datetime('Date'),
                'od_method':fields.text('Method'),
                'od_type':fields.selection([('milestone','Milestone'),('workpackage','Work Package'),('activities','Activities')],'Type',required=True,readonly=True),
                # 'od_costsheet_tab':fields.selection([('mat','MAT'),('ren','REN'),('trn','TRN'),('bim','BIM'),('oim','OIM'),('bmn','BMN'),('omn','OMN'),('om','OM')],'Tab Type'),
                'od_implementation_id':fields.many2one('od.implementation','Implementation Code'),
                'od_state':fields.many2one('od.project.phase','Phase'),
                'od_checklist_ids':fields.one2many('od.task.checklist','task_id','Check List'),
                'od_access_method':fields.selection([('onsite','On Site - Customer Site'),('remote','Remote'),('phone_support','Phone Support'),('beta_ofc','In Beta IT Office')],'Access Method'),
                'od_child_ids':fields.one2many('project.task','od_parent_id','Od Delegated Task'),
                }
    _defaults = {
                'od_type':'milestone'
                 }
    def od_delegate_wp(self,cr,uid,ids,context=None):
        task = self.browse(cr,uid,ids)
        project_id = task.project_id  and task.project_id.id
        date_start = task.date_start
        date_end = task.date_end
        context['default_date_start'] = date_start
        context['default_date_end'] = date_end
        context['default_od_parent_id'] = ids[0]
        context['default_od_by_delegate'] = True
        context['default_od_type'] = 'workpackage'
        context['default_project_id'] = project_id
        context['od_popup'] = True
#         context['form_view_ref']='orchid_beta_project.view1_od_task_form3'
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'project.task',
                'type': 'ir.actions.act_window',
                'context':context,
                'target': 'new',
                'flags': {'form': {'action_buttons': True}}
            }
    def od_delegate_act(self,cr,uid,ids,context=None):
        task = self.browse(cr,uid,ids)
        project_id = task.project_id  and task.project_id.id
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'project.task',
                'type': 'ir.actions.act_window',
                'context':{'default_od_parent_id':ids[0],
                           'default_od_by_delegate':True,
                           'default_od_type':'activities',
                           'default_project_id':project_id,
                           'od_popup':True,
                           },
                'target': 'new',
                'flags': {'form': {'action_buttons': True}}
            }


    def onchange_od_type(self,cr,uid,ids,od_type,context=None):
        domain={}
#         if od_type == 'activities':
#             domain = {'od_parent_id': [('od_type','!=','activities')]}
        if od_type == 'workpackage':
            domain = {'od_parent_id': [('od_type','!=','activities')]}
#         if od_type == 'activities' and project_id:
#             domain = {'od_parent_id': [('od_type','=','milestone'),('name','=','Maintenance'),('project_id','=',project_id)]}
        return {'domain':domain}

    
    
    
    def onchange_imp_id(self,cr,uid,ids,imp_id,context=None):
        res = {}
        imp_pool = self.pool.get('od.implementation')
        val = '00:00'
        if imp_id:
            imp_obj = imp_pool.browse(cr,uid,imp_id)
            duration = imp_obj.expected_act_duration
            categ_id = imp_obj.categ_id and imp_obj.categ_id.id
            sub_categ_id = imp_obj.sub_categ_id and imp_obj.sub_categ_id.id
            minutes = decimal.Decimal(duration * 60)
            if minutes:
                val ='{:02f}:{:02f}'.format(*divmod(minutes, 60))
            method = imp_obj.method
            check_line = []
            for line in imp_obj.check_list:
                check_line.append((0,0,{'name':line.name,
                                       'done':False,
                                       }))
            res['value'] = {'planned_hours':duration,
                            'od_planned_time':val,
                            'od_checklist_ids': check_line,
                            'od_method':method,
                            'od_categ_id':categ_id,
                            'od_sub_categ_id':sub_categ_id,
                            }
        return res

    def onchange_date_end(self,cr,uid,ids,date_end,od_type,context=None):
        res = {}
        vals = {}
        if od_type == 'milestone':
            task = self.browse(cr,uid,ids)
            project = task.project_id
            if project:
                project_date_end = project.od_analytic_pmo_closing
                end_date,time = date_end.split(' ')
                if project_date_end < end_date:
                    raise Warning("Selected Date/Time Cannot be After %s"%project_date_end)
        if od_type in ('workpackage','activities') and date_end:
            task = self.browse(cr,uid,ids)
            parent_end = task.od_parent_id.date_end
            if not parent_end:
                parent_id = context.get('default_od_parent_id')
                task_obj = self.browse(cr,uid,parent_id)
                parent_end = task_obj.date_end
            if parent_end:
                parent_end,time = parent_end.split(' ')
                end,time = date_end.split(' ')
                if parent_end < end :
                    raise Warning("Selected Date/Time Cannot be After %s"%parent_end)
            
        
    def onchange_date_start_end(self,cr,uid,ids,date_start,od_type,planned_hours,context=None):
        res = {}
        vals ={}
        if od_type == 'milestone':
            task = self.browse(cr,uid,ids)
            project = task.project_id
            if project:
                project_date_start = project.date_start
                start,time = date_start.split(' ')
                if project_date_start > start:
                    raise Warning("Selected Date/Time Cannot be Before Project Start Date %s"%project_date_start)
        if od_type in ('workpackage','activities') and date_start:
            task = self.browse(cr,uid,ids,context)
            parent_start = task.od_parent_id.date_start
            
            if not parent_start:
                parent_id = context.get('default_od_parent_id')
                task_obj = self.browse(cr,uid,parent_id)
                parent_start = task_obj.date_start
                
            if parent_start:
                parent_start,time = parent_start.split(' ')
                start,time = date_start.split(' ')
                if parent_start > start:
                    raise Warning("Selected Date/Time Cannot be Before Parent Task Start Date %s"%parent_start)
        if od_type == 'activities' and date_start and planned_hours:
            date_start = datetime.strptime(date_start, DEFAULT_SERVER_DATETIME_FORMAT)
            # date_end = datetime.strptime(date_end, DEFAULT_SERVER_DATETIME_FORMAT)
            # diff = (date_end - date_start)
            # days = diff.days * 24
            # seconds = diff.seconds
            # hour =  days + float(seconds)/3600
            dt = date_start + timedelta(hours=planned_hours or 0.0)
            dt_s = dt.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            vals.update({'date_end':dt_s})
            res['value'] = vals
        return res


    # def onchange_date_deadline(self,cr,uid,ids,date,context=None):
    #     res = {}
    #     if date:
    #         print "date>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",date
    #         res['value'] = {'date_start':date}
    #     return res

class project_work(osv.osv):
    _inherit = "project.task.work"
    _description = "Project Task Work"
    _columns = {
                'od_start_date':fields.datetime('Start Date'),
                'od_complete_date':fields.datetime('Complete Date'),
                'state':fields.selection([('completed','Completed Entirely'),('partial','Partially Completed')],'Status',required=True),
                'locked':fields.boolean('Locked',default=False),
                
                }


    def onchange_time(self,cr,uid,ids,start_date,complete_date,context=None):
        res = {}
        if start_date and complete_date:
            start_time = datetime.strptime(start_date, DEFAULT_SERVER_DATETIME_FORMAT)
            complete_time = datetime.strptime(complete_date, DEFAULT_SERVER_DATETIME_FORMAT)
            diff = (complete_time - start_time)
            days = diff.days * 24
            seconds = diff.seconds
            hour= days + float(seconds)/3600.0
            hours= float("{0:.2f}".format(hour))
            res['value'] = {'hours':hours}
        return res
