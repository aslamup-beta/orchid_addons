# -*- coding: utf-8 -*-
from od_default_task_list import od_task_vals
from od_default_milestone import od_project_vals,od_om_vals,od_amc_vals
from openerp import models, fields, api,_
from datetime import datetime,timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
import decimal
from openerp.exceptions import Warning
from pprint import pprint
from openerp import tools
from openerp.osv import fields as field2
from openerp import SUPERUSER_ID
class project_work(models.Model):
    _inherit = 'project.task.work'

    
    
    def _create_analytic_entries(self, cr, uid, vals, context):
        """Create the hr analytic timesheet from project task work"""
        
        import datetime
        timesheet_obj = self.pool['hr.analytic.timesheet']
        task_obj = self.pool['project.task']

        vals_line = {}
        timeline_id = False
        acc_id = False

        task_obj = task_obj.browse(cr, uid, vals['task_id'], context=context)
        result = self.get_user_related_details(cr, SUPERUSER_ID, vals.get('user_id', uid))
        
        vals_line['name'] = '%s: %s' % (tools.ustr(task_obj.name), tools.ustr(vals['name'] or '/'))
        vals_line['user_id'] = vals['user_id']
        vals_line['product_id'] = result['product_id']
        if vals.get('date'):
            if len(vals['date']) > 10:
                timestamp = datetime.datetime.strptime(vals['date'], tools.DEFAULT_SERVER_DATETIME_FORMAT)
                ts = field2.datetime.context_timestamp(cr, uid, timestamp, context)
                vals_line['date'] = ts.strftime(tools.DEFAULT_SERVER_DATE_FORMAT)
            else:
                vals_line['date'] = vals['date']

        # Calculate quantity based on employee's product's uom
        vals_line['unit_amount'] = vals.get('hours',0.0)
        vals_line['cancelled_by_owner'] = vals.get('cancelled_by_owner',False)
        vals_line['cancelled_by_id'] = vals.get('cancelled_by_id',False)
        vals_line['narration'] = vals.get('narration','')
        

        default_uom = self.pool['res.users'].browse(cr, SUPERUSER_ID, uid, context=context).company_id.project_time_mode_id.id
        if result['product_uom_id'] != default_uom:
            vals_line['unit_amount'] = self.pool['product.uom']._compute_qty(cr, SUPERUSER_ID, default_uom, vals['hours'], result['product_uom_id'])
        acc_id = task_obj.project_id and task_obj.project_id.analytic_account_id.id or acc_id
        if acc_id:
            vals_line['account_id'] = acc_id
            res = timesheet_obj.on_change_account_id(cr, SUPERUSER_ID, False, acc_id)
            if res.get('value'):
                vals_line.update(res['value'])
            vals_line['general_account_id'] = result['general_account_id']
            vals_line['journal_id'] = result['journal_id']
            vals_line['amount'] = 0.0
            vals_line['product_uom_id'] = result['product_uom_id']
            vals_line['overtime_type'] = vals.get('overtime_type',False)
            amount = vals_line['unit_amount']
            prod_id = vals_line['product_id']
            unit = False
            timeline_id = timesheet_obj.create(cr, SUPERUSER_ID, vals=vals_line, context=context)
            # Compute based on pricetype
#             amount_unit = timesheet_obj.on_change_unit_amount(cr, uid, timeline_id,
#                 prod_id, amount, False, unit, vals_line['journal_id'], context=context)
            hourly_rate = timesheet_obj.od_get_hourly_rate(cr,SUPERUSER_ID,vals['user_id'])
            timesheet_obj.write(cr, SUPERUSER_ID, [timeline_id],{'hourly_rate':hourly_rate,}, context=context)
            timesheet_data = timesheet_obj.browse(cr,SUPERUSER_ID,timeline_id)
            normal_amount = timesheet_data.normal_amount
            overtime_amount = timesheet_data.overtime_amount
            amount =  normal_amount + overtime_amount
            timesheet_obj.write(cr, SUPERUSER_ID, [timeline_id],{'amount':amount}, context=context)
        return timeline_id
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(project_work, self).default_get(cr, uid, fields, context=context)
        # res['user_id'] = False
        return res
    def get_employee_id(self,user_id):
        emp_pool = self.env['hr.employee']
        emp_obj = emp_pool.search([('user_id','=',user_id)],limit=1)
        return emp_obj and emp_obj.id

    @api.multi
    def unlink(self):
        if self.ot_line_id:
            self.ot_line_id.unlink()
            return True
        return super(project_work, self).unlink()
    def edit_overtime(self,vals,ot_line_id):
        write_vals ={}
        if vals.get('hours',False):
            write_vals.update({'hour':vals['hours']})
        if vals.get('overtime_type',False):
            write_vals.update({'over_time_type':vals['overtime_type']})
        if vals.get('user_id',False):
            employee_id = self.get_employee_id(vals['user_id'])
            write_vals.update({'employee_id':employee_id})
        ot_line_id.write(write_vals)

    def create_overtime(self,vals):
        overtime_type = vals.get('overtime_type',False)
        if overtime_type:
            period_obj = self.env['account.period']
            overtime_obj = self.env['od.hr.over.time']
            overtime_line_obj = self.env['od.hr.over.time.line']
            date = vals.get('od_complete_date')
            user_id = vals.get('user_id',False)
            date = date[:10]
            period_id = period_obj.find(date).id
            hours =vals.get('hours')
            overtime_id = overtime_obj.search([('period_id','=',period_id)],limit=1)

            if not overtime_id:
                overtime_id = overtime_obj.create({'period_id':period_id,'date':date,'state':'confirm'})
            employee_id = self.get_employee_id(user_id)
            if not employee_id:
                raise Warning("No Employee Linked for this User")
            overtime_line_vals = {'hr_over_time_id':overtime_id.id,'employee_id':employee_id,
            'hour':hours,'over_time_type':overtime_type
            }
            ot_line_id = overtime_line_obj.create(overtime_line_vals)
            return ot_line_id.id
        return False


    @api.multi
    def write(self, vals):
        if self.ot_line_id:
            self.edit_overtime(vals,self.ot_line_id)
        timeline_id = self.hr_analytic_timesheet_id
        if vals.get('overtime_type') and timeline_id:
            
            timeline_id.write({'overtime_type':vals.get('overtime_type')})
            normal_amount = timeline_id.normal_amount
            overtime_amount = timeline_id.overtime_amount
            amount =  normal_amount + overtime_amount
            timeline_id.write({'amount':amount})
            
        return super(project_work, self).write(vals)
    @api.model
    def create(self,vals):
        ot_line_id = self.create_overtime(vals)
        vals.update({'ot_line_id':ot_line_id})
        return super(project_work,self).create(vals)
    @api.constrains('date','od_complete_date')
    def check_date_order(self):
        if self.date and self.od_complete_date:
            if not self.od_complete_date > self.date:
                raise Warning('Complete Date Should Be greater than Start Date')
    
    
    @api.one 
    @api.depends('hours')
    def get_show_time_spent(self):
        self.b_hours = self.hours
    
    overtime = fields.Boolean(string="Overtime")
    overtime_type = fields.Many2one('hr.salary.rule',string="Overtime Type")
    ot_line_id = fields.Many2one('od.hr.over.time.line',string='Overtime Line')
    b_hours = fields.Float(string="Time Spent",help="To Show Time Spent by User For the Task",compute='get_show_time_spent')
class project_project(models.Model):
    _inherit ='project.project'
    _od_project_types =[('credit','Credit'),('sup','Supply'),('imp','Implementation'),('sup_imp','Supply & Implementation'),('amc','AMC'),('o_m','O&M'), ('comp_gen','Company General -(POC,Training,Trips,etc.)')]
    state = fields.Selection([('template','Template'),('draft','New'),('open','In Progress'),('pending','To Renew'),('sign_off','Sign Off'),('close','Closed'),('cancelled','Cancelled')],string="Status")
    
    @api.multi
    def project_material_issue(self):
        return {
              'name': _('Material Issue Request'),
              'view_type': 'form',
              "view_mode": 'form',
              'res_model': 'project.material.issue.wiz',
              'type': 'ir.actions.act_window',
              'target':'new',
              }
    
    def get_root_id(self):
        
        root_id = False
        analytic = self.analytic_account_id
        if analytic.grand_parent_id and analytic.grand_parent_id.od_analytic_level =='level0':
            root_id = analytic.grand_parent_id.id
            return root_id 
        if analytic.parent_id and analytic.parent_id.od_analytic_level =='level0':
            root_id = analytic.parent_id.id
            return root_id 
        return root_id
            
    
    
    @api.multi
    def project_proc_issue(self):
        root_id  = self.get_root_id()
        return {
              'name': _('Procurment Issue Request'),
              'view_type': 'form',
              "view_mode": 'form',
              'res_model': 'project.proc.wiz',
              'type': 'ir.actions.act_window',
              'target':'new',
              'context':{'root_id':root_id}
              }
    
    @api.multi
    def project_inv_issue(self):
        root_id  = self.get_root_id()
        return {
              'name': _('Generate Invoice'),
              'view_type': 'form',
              "view_mode": 'form',
              'res_model': 'project.inv.wiz',
              'type': 'ir.actions.act_window',
              'target':'new',
              'context':{'root_id':root_id}
              }
    
    
    def send_mail_to_finance(self,template):
        ir_model_data = self.env['ir.model.data']
        email_obj = self.pool.get('email.template')
        if self.company_id.id == 6:
            template = template +'_saudi'
        template_id = ir_model_data.get_object_reference('orchid_beta_project', template)[1]
        rec_id = self.id
        email_obj.send_mail(self.env.cr,self.env.uid,template_id,rec_id, force_send=True)
        return True
    
    def _check_sup_inv_pending(self):
        analytic_id = self.analytic_account_id and self.analytic_account_id.id or False
        invoice = self.env['account.invoice'].search([('od_analytic_account','=',analytic_id),('state','=','draft'),('type','=','in_invoice')])
        invoice_names = [inv.name for inv in invoice]
        if invoice_names:
            raise Warning("Pending Supplier Invoice to Validate %s"%invoice_names)
    
    def _check_pending(self):
        analytic_id = self.analytic_account_id and self.analytic_account_id.id or False
        picking = self.env['stock.picking'].search([('od_analytic_id','=',analytic_id),('state','not in',('cancel','done'))])
        picking_names = [pick.name for pick in picking]
        if picking_names:
            raise Warning("Pending Material Transfer %s"%picking_names)
        
    def _check_sign_off(self):
        project_id = self.id
        tasks= self.env['project.task'].search([('project_id','=',project_id),('od_type','=','activities'),('od_stage','=','draft')])
        task_ids = [ta.id for ta in tasks]
        if task_ids:
            raise Warning("Some of the task are still in Progress, kindly check the task with these ids %s"%task_ids)
    
    @api.multi
    def od_set_sign_off(self):
        self._check_sign_off()
        self._check_pending()
        self._check_sup_inv_pending()
        project_type = self.analytic_account_id.od_type_of_project
        if not project_type in ('parent_level0','amc_view','o_m_view'):
            self.send_mail_to_finance('od_project_signoff_email_template')
        self.analytic_account_id.write({'state':'sign_off'})
        self.write({'state':'sign_off'})

#     def od_create_default_tasks(self,project):
#         task_pool = self.env['project.task']
#         project_id = project.id
#         user_id = project.user_id and project.user_id.id
#         type_of_project = project.od_type_of_project
#         partner_ids = [(6,0,[user_id])],
#         date_start = project.date_start
#         date_end = project.date
#         task_vals = od_task_vals()
#         parent_task ={}
#         for val in task_vals:
# 
#             val.update({
#             'project_id':project_id,
#             'user_id':user_id,
#             'partner_ids':partner_ids,
#             'date_start':date_start,
#             'date_end':date_end
#             })
#             if type_of_project in ('amc','o_m') and not val.get('amc',False):
#                 continue
#             if val['od_type'] == 'workpackage':
#                 od_parent_id = parent_task.get(val['val_parent_id'],False)
#                 val.update({'od_parent_id':od_parent_id})
#             val_id = val.pop('val_id')
#             val.pop('val_parent_id',None)
#             val.pop('amc',None)
#             task = task_pool.create(val)
#             task_id = task.id
#             parent_task[val_id] = task_id
# 
#         return True

    def create_maint_task(self):
        if self.od_type_of_project == 'amc':
            task_pool = self.env['project.task']
            task_vals = od_amc_vals()
            project_id = self.id
            user_id = self.user_id and self.user_id.id
            date_start = self.date_start 
            date_end = self.date
            partner_ids = [(6,0,[user_id])],
            for val in task_vals:
                val.update({
                'project_id':project_id,
                'user_id':user_id,
                'od_type':'milestone',
                'partner_ids':partner_ids,
                'date_start':date_start,
                'date_end':date_end,
                'no_delete':True
                })
                task = task_pool.create(val)
        return True

    
    def create_milestone_tasks(self,project,task_vals):
        task_pool = self.env['project.task']
        
        project_id = project.id
        user_id = project.user_id and project.user_id.id
        date_start = project.date_start 
        date_end = project.date
        partner_ids = [(6,0,[user_id])],
        for val in task_vals:
            val.update({
            'project_id':project_id,
            'user_id':user_id,
            'od_type':'milestone',
            'partner_ids':partner_ids,
            'date_start':date_start,
            'date_end':date_end,
            'no_delete':True
            })
            task = task_pool.create(val)
        return True
    
    def od_m_create_tasks(self,project):
        task_vals = od_project_vals()
        if project.od_type_of_project =='amc':
            task_vals = od_amc_vals()
        if project.od_type_of_project =='o_m':
            task_vals = od_om_vals()
        
        self.create_milestone_tasks(project,task_vals)
    

    @api.model
    def create(self,vals):

        if vals.get('analytic_account_id',False):
            analytic_account_id = vals.get('analytic_account_id')
            analytic_obj = self.env['account.analytic.account']
            analytic = analytic_obj.browse(analytic_account_id)
            owner_id = analytic.od_owner_id and analytic.od_owner_id.id or False
            type_of_project = analytic.od_type_of_project
            quantity_max = analytic.quantity_max
            vals['user_id'] = owner_id
            vals['od_quantity_max'] = quantity_max
            vals['od_type_of_project'] = type_of_project
        project = super(project_project,self).create(vals)
        self.od_m_create_tasks(project)
#         self.od_create_default_tasks(project)
        return project
    @api.one
    def od_get_total_invoice(self):
        invoice_line = self.env['account.invoice.line']
        analytic_id = self.analytic_account_id and self.analytic_account_id.id or False
        domain = [('account_analytic_id','=',analytic_id)]
        lines = invoice_line.search(domain)
        if lines:
            amount = sum([line.price_subtotal for line in lines])
            self.od_amnt_invoiced = amount

    @api.one
    def od_get_total_purchase(self):
        purchase_order = self.env['purchase.order']
        analytic_id = self.analytic_account_id and self.analytic_account_id.id or False
        domain = [('project_id','=',analytic_id),('state','in',('approved','done'))]
        pos = purchase_order.search(domain)
        if pos:
            amount = sum([po.bt_amount_total for po in pos])
            self.od_amnt_purchased = amount

    
    
    def get_invoice_untaxed_amount(self):
        analytic_id = self.analytic_account_id and self.analytic_account_id.id or False
        manual = self.analytic_account_id and self.analytic_account_id.od_manual_invoice
        if manual:
            amount = self.analytic_account_id and self.analytic_account_id.od_manual_invoice_amnt or 0.0
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
    
     
    @api.multi
    def od_btn_open_sup_refund(self):
        analytic_id = self.analytic_account_id and self.analytic_account_id.id or False
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
    
    
    @api.multi
    def od_btn_open_sup_invoice(self):
        analytic_id = self.analytic_account_id and self.analytic_account_id.id or False
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
    
    
    @api.multi
    def od_btn_open_customer_refund(self):
        analytic_id = self.analytic_account_id and self.analytic_account_id.id or False
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
    
    @api.multi
    def od_btn_open_customer_invoice(self):
        analytic_id = self.analytic_account_id and self.analytic_account_id.id or False
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

    
    @api.multi
    def od_btn_open_cost_revenue(self):
        analytic_id = self.analytic_account_id and self.analytic_account_id.id or False

        domain = [('account_id','child_of',analytic_id)]
        return {
            'domain':domain,
            'context':{'search_default_group_date': 1, 'search_default_group_journal': 1},
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.analytic.line',
            'type': 'ir.actions.act_window',
        }
    @api.multi
    def od_btn_open_invoice_lines(self):
        analytic_id = self.analytic_account_id and self.analytic_account_id.id or False
        domain = [('account_analytic_id','=',analytic_id)]
        return {
            'domain':domain,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice.line',
            'type': 'ir.actions.act_window',
        }
    @api.multi
    def od_btn_open_purchase_lines(self):
        analytic_id = self.analytic_account_id and self.analytic_account_id.id or False
        domain = [('project_id','=',analytic_id),('state','in',('approved','done'))]
        return {
            'domain':domain,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'purchase.order',
            'type': 'ir.actions.act_window',
        }

    def od_get_do(self):
        analytic_id = self.analytic_account_id and self.analytic_account_id.id or False
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
        analytic = self.browse(cr, uid, ids[0], context).analytic_account_id
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
        analytic_id = self.analytic_account_id and self.analytic_account_id.id or False
        domain = [('od_analytic_account_id','=',analytic_id)]
        meeting_count =0
        meeting_count = len(Event.search(domain))

        self.od_meeting_count = meeting_count
    def od_get_products(self,line_id):
        products =[]
        for line in line_id:
            products.append({'product_id':line.part_no.id,'planned':line.qty,'od_manufacture_id':line.manufacture_id and line.manufacture_id.id or False})
        return products
    def od_deduplicate(self,l):
        result = []
        for item in l :
            check = False
            for r_item in result :
                if item['product_id'] == r_item['product_id'] :
                    check = True
                    qty = r_item['planned']
                    r_item['qty'] = qty + item['planned']
            if check == False :
                result.append( item )

        return result
    @api.one
    def od_get_timesheet_amount(self):
        timesheet = self.env['hr.analytic.timesheet']
        analytic_id = self.analytic_account_id and self.analytic_account_id.id or False
        domain = [('account_id','=',analytic_id)]
        timesheet_obj = timesheet.search(domain)
        amount = sum([tm.normal_amount for tm in timesheet_obj])
        self.od_timesheet_amount = amount

    # @api.one
    # def od_get_timesheet_units(self):
    #     timesheet = self.env['hr.analytic.timesheet']
    #     analytic_id = self.id
    #     domain = [('account_id','=',analytic_id)]
    #     timesheet_obj = timesheet.search(domain)
    #     timesheet_units = sum([tm.unit_amount for tm in timesheet_obj])
    #     self.od_timesheet_units = timesheet_units
    @api.multi
    def od_open_hr_expense_claim(self):
        hr_exp_line = self.env['hr.expense.line']
        analytic_id = self.analytic_account_id and self.analytic_account_id.id or False
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
        analytic_id = self.analytic_account_id and self.analytic_account_id.id or False
        domain = [('analytic_account','=',analytic_id),('od_state','not in',('draft','cancelled','confirm','second_approval'))]
        hr_exp_obj =hr_exp_line.search(domain)
        amount  = sum([hr.total_amount for hr in hr_exp_obj])
        self.od_hr_claim_amount = amount

    @api.multi
    def od_open_hr_expense_claim_draft(self):
        hr_exp_line = self.env['hr.expense.line']
        analytic_id = self.analytic_account_id and self.analytic_account_id.id or False
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
        analytic_id = self.analytic_account_id and self.analytic_account_id.id or False
        domain = [('analytic_account','=',analytic_id),('od_state','in',('draft','cancelled','confirm','second_approval'))]
        hr_exp_obj =hr_exp_line.search(domain)
        amount  = sum([hr.total_amount for hr in hr_exp_obj])
        self.od_hr_claim_amount_draft = amount


    @api.multi
    def od_btn_open_account_move_lines(self):
        analytic_id = self.analytic_account_id and self.analytic_account_id.id or False
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
        analytic_id = self.analytic_account_id and self.analytic_account_id.id or False
        domain = [('analytic_account_id','=',analytic_id),('od_state','=','posted')]
        journal_lines = account_move_line.search(domain)
        amount = sum([mvl.debit for mvl in journal_lines])
        self.od_journal_amount = amount

    @api.multi
    def od_btn_open_account_move_lines_draft(self):
        analytic_id = self.analytic_account_id and self.analytic_account_id.id or False
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
        analytic_id = self.analytic_account_id and self.analytic_account_id.id or False
        domain = [('analytic_account_id','=',analytic_id),('od_state','!=','posted')]
        journal_lines = account_move_line.search(domain)
        amount = sum([mvl.debit for mvl in journal_lines])
        self.od_journal_amount_draft = amount

    @api.one
    @api.depends('od_cost_sheet_id')
    def od_get_po_status(self):
        if self.od_cost_sheet_id:
            self.od_po_status = self.od_cost_sheet_id.po_status


    @api.one
    def od_get_total_sale_value(self):
        sale_order = self.env['sale.order']
        analytic_id = self.analytic_account_id and self.analytic_account_id.id or False
        domain =[('project_id','=',analytic_id)]
        sales = sale_order.search(domain)
        total = sum([sal.amount_total for sal in sales])
        margin = sum([sal.margin for sal in sales])
        if total:
            margin_percent = (margin/total) * 100
            self.od_profit_percent = margin_percent
        self.od_total_sale_value = total
    # od_timesheet_units = fields.Float(string="Timesheet Units",compute="od_get_timesheet_units")
#     od_type_of_project = fields.Selection(_od_project_types,string="Type Of Project",related="account_analytic_id.od_type_of_project")
    od_profit_percent = fields.Float(string="Profit Percentage",compute="od_get_total_sale_value")
    od_total_sale_value = fields.Float(string="Total Sale Value",compute="od_get_total_sale_value")
    DOMAIN = [('parent_level0','Parent Level View'),('amc_view','AMC View'),('o_m_view','O&M View'),('credit','Credit'),('sup','Supply'),('imp','Implementation'),
              ('sup_imp','Supply & Implementation'),('amc','AMC'),
              ('o_m','O&M'),('cust_trn','Customer Training'),('poc','(POC,Presales)'), ('comp_gen','Company General -(Training,Labs,Trips,etc.)')]
    od_po_status = fields.Selection([('credit','Credit Customer'),('waiting_po','Waiting P.O'),('special_approval','Special Approval From GM'),('available','Available')],'Customer PO Status',compute="od_get_po_status")
    od_type_of_project = fields.Selection(DOMAIN,string="Type Of Project")
    od_journal_amount_draft = fields.Float(string="Journal Amount Draft",compute="od_get_analytic_journal_amount_draft")
#     od_journal_amount = fields.Float(string="Journal Amount",compute="od_get_analytic_journal_amount")
    od_hr_claim_amount = fields.Float(string="Hr Exp Claim Amount",compute="od_get_hr_exp_claim_amount")
    od_hr_claim_amount_draft = fields.Float(string="Hr Exp Claim Amount Draft",compute="od_get_hr_exp_claim_amount_draft")
    od_timesheet_amount = fields.Float(string="Timesheet Amount",compute="od_get_timesheet_amount")
    od_meeting_count = fields.Integer(string="Meeting Count",compute="_od_meeting_count")
#     od_amnt_invoiced = fields.Float(string="Customer Invoice Amount",compute="od_get_total_invoice")
    od_amnt_purchased = fields.Float(string="Supplier Purchase Amount",compute="od_get_total_purchase")
    od_material_budget_line = fields.One2many('od.project.material.budget','project_id',string="Material Budget Line")
    material_pulled = fields.Boolean("Material Pulled")
    od_territory_id = fields.Many2one('od.partner.territory',string='Territory',related="partner_id.od_territory_id",readonly=True)
    od_section_id = fields.Many2one('crm.case.section',string="Sales Team",related="partner_id.section_id",readonly=True)
class od_project_material_budget(models.Model):
    _name = 'od.project.material.budget'


    def get_balance_qty(self):
        return self.planned - self.requested

    @api.one
    @api.depends('planned','requested')
    def compute_balance(self):
        self.balance = self.planned - self.requested

    @api.one
    def unlink(self):

        if self.requested != 0:
            raise Warning("This Material Budget/Material Already Requested from some Task,You cant Delete it")
        return super(od_project_material_budget,self).unlink()

    project_id = fields.Many2one('project.project',string='Project')
    product_id = fields.Many2one('product.product',string='Product')
    od_manufacture_id = fields.Many2one('od.product.brand',string="Manufacture")
    planned = fields.Float(string="Planned")
    requested = fields.Float(string="Requested",readonly=True)
    balance = fields.Float(string="Balance",compute="compute_balance")
    po = fields.Float(string="PO",readonly=True)
    received = fields.Float(string='Received',readonly=True)
    delivered = fields.Float(string='Delivered',readonly=True)
