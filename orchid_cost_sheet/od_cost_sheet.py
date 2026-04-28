# -*- coding: utf-8 -*-
from openerp.tools.translate import _
from openerp.tools import float_round, float_is_zero, float_compare
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from dateutil.relativedelta import relativedelta
from datetime import date, timedelta,datetime
import openerp.addons.decimal_precision as dp
from collections import defaultdict,Counter
from math import exp,log10
from pprint import pprint
from openerp.osv import expression
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
import logging
import time
from __builtin__ import False
from pickle import FALSE

_logger = logging.getLogger(__name__)

class od_beta_closing_conditions(models.Model):
    _name ="od.beta.closing.conditions"
    name = fields.Char(string="Name")

class od_cost_sheet(models.Model):
    _name = 'od.cost.sheet'
    _description = 'Cost Sheet'
    _inherit = ['mail.thread']
    _order = 'id desc'
    
    @api.multi 
    def open_import_wiz(self):
        ctx = self.env.context.copy()
        ctx['sheet_id'] = self.id
#         ctx['active_model_line'] ='od.cost.mat.main.pro.line'
        return {
              'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'wiz.import.export',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context':ctx,
            }
        
    @api.multi 
    def open_import_ren_wiz(self):
        ctx = self.env.context.copy()
        ctx['sheet_id'] = self.id
#         ctx['active_model_line'] ='od.cost.mat.main.pro.line'
        return {
              'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'wiz.import.export.ren',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context':ctx,
            }
    
    @api.one 
    def swith_status(self):
        if self.state in ('draft','design_ready','submitted','commit'):
            if self.status =='revision':
                self.write({'status':'active'})
            elif self.status =='active':
                self.write({'status':'revision'})
     
     
    def get_project_id(self):
        
        if self.select_a1:
            return self.analytic_a1 and self.analytic_a1.id 
        elif self.select_a2:
            return self.analytic_a2 and self.analytic_a2.id
        elif self.select_a3:
            return self.analytic_a3 and self.analytic_a3.id
        elif self.select_a4:
            for line in self.amc_analytic_line:
                return line.analytic_id and line.analytic_id.id 
        elif self.select_a5:
            for line in self.om_analytic_line:
                return line.analytic_id and line.analytic_id.id 
        else:
            return False
                
            
    def create_pre_opne_cost_move(self):
        company_id = self.company_id and self.company_id.id or False
        period_obj = self.env['account.period']
        move_obj = self.env['account.move']
        date = fields.Date.today()
        period_ids = period_obj.find(date).id
        ref = self.name
        journal_id = self.get_product_id_from_param('pre_op_journal_id')
        debit_account = self.get_product_id_from_param('pre_op_wip_account_id')
        credit_account = self.get_product_id_from_param('pre_op_account_id')
        if company_id ==6:
            journal_id = self.get_product_id_from_param('pre_op_journal_id_ksa')
            debit_account = self.get_product_id_from_param('pre_op_wip_account_id_ksa')
            credit_account = self.get_product_id_from_param('pre_op_account_id_ksa')
            
        project_id = self.get_project_id()
        partner_id =self.od_customer_id and self.od_customer_id.id or False
        od_opp_id = self.lead_id and self.lead_id.id or False
        amount = self.pre_opn_cost
        move_lines =[]

        
        vals1={
                'name': ref,
                'ref': ref,
                'period_id': period_ids ,
                'journal_id': journal_id,
                'date': date,
                'account_id': credit_account,
                'debit': 0.0,
                'od_opp_id':od_opp_id,
                'credit': abs(amount),
                'partner_id':partner_id,
                'analytic_account_id': project_id,

            }
        vals2={
                'name': ref,
                'ref': ref,
                'period_id': period_ids ,
                'journal_id': journal_id,
                'date': date,
                'account_id': debit_account,
                'credit': 0.0,
                'od_opp_id':od_opp_id,
                'debit': abs(amount),
                'partner_id':partner_id,
                'analytic_account_id': project_id,

            }
        move_lines.append([0,0,vals1])
        move_lines.append([0,0,vals2])
           
        move_vals = {

                'date': date,
                'ref': ref,
                'period_id': period_ids ,
                'journal_id': journal_id,
                'line_id':move_lines

                }
        move_id = move_obj.create(move_vals).id
        self.pre_opn_move_id = move_id
        
        return True
    
    def cron_od_cost_sheet(self, cr, uid, context=None):
        context = dict(context or {})
        remind = []

        def fill_remind( domain):
            base_domain = []
            base_domain.extend(domain)
            cost_sheet_ids = self.search(cr, uid, base_domain, context=context)
            
            for costsheet in self.browse(cr,uid,cost_sheet_ids,context=context):
                if costsheet.state not in ('cancel','draft','submitted','design_ready'):
                    val = {'name':costsheet.name,'number':costsheet.number,
                           'branch':costsheet.od_branch_id and costsheet.od_branch_id.name or '',
                           'customer':costsheet.od_customer_id and costsheet.od_customer_id.name or '',
                           'po_status':costsheet.po_status,'sale_person':costsheet.sales_acc_manager and costsheet.sales_acc_manager.name or '',
                           'owner':costsheet.reviewed_id and costsheet.reviewed_id.name or ''
                        }
                    br_email = costsheet.od_branch_id and costsheet.od_branch_id.email
                    if br_email:
                        branch_managers.append(br_email)
                    remind.append(val)
                    
        for company_id in [1,6]:
            remind = []
            branch_managers =[]
            fill_remind([('status','=','active'), ('po_status', '=', 'waiting_po'),('company_id','=',company_id),('state','not in',('draft','submitted','cancel','design_ready'))])
            template = 'od_cost_sheet_cron_email_template'
            if company_id == 6:
                template = template + '_saudi'
            template_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'orchid_cost_sheet', template)[1]
            branch_managers = list(set(branch_managers))
            br_emails = ','.join(branch_managers)
            context['branch_managers'] = br_emails
            context['subject'] = "Waiting PO Reminder"
            context['title'] = "The following Cost Sheet is Waiting for PO:"
            remind = sorted(remind, key=lambda k: k['branch']) 
            context['data'] = remind
            if remind:
                self.pool.get('email.template').send_mail(cr, uid, template_id, uid, force_send=True, context=context)
        return True
    
    def cron_od_cost_sheet_spcl_apprv(self, cr, uid, context=None):
        context = dict(context or {})
        remind = []

        def fill_remind( domain):
            base_domain = []
            base_domain.extend(domain)
            cost_sheet_ids = self.search(cr, uid, base_domain, context=context)
            
            for costsheet in self.browse(cr,uid,cost_sheet_ids,context=context):
                if costsheet.state not in ('cancel','draft','submitted','design_ready'):
                    val = {'name':costsheet.name,'number':costsheet.number,
                           'branch':costsheet.od_branch_id and costsheet.od_branch_id.name or '',
                        'customer':costsheet.od_customer_id and costsheet.od_customer_id.name or '',
                        'po_status':costsheet.po_status,'sale_person':costsheet.sales_acc_manager and costsheet.sales_acc_manager.name or '',
                        'owner':costsheet.reviewed_id and costsheet.reviewed_id.name or ''
                        }
                    br_email = costsheet.od_branch_id and costsheet.od_branch_id.email
                    if br_email:
                        branch_managers.append(br_email)
                    remind.append(val)
                    
        for company_id in [1,6]:
            remind = []
            branch_managers =[]
            fill_remind([('status','=','active'),('po_status', '=', 'special_approval'),('company_id','=',company_id),('state','not in',('draft','submitted','cancel','design_ready'))])
            template = 'od_cost_sheet_cron_email_template'
            if company_id == 6:
                template = template + '_saudi'
            template_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'orchid_cost_sheet', template)[1]
            branch_managers = list(set(branch_managers))
            br_emails = ','.join(branch_managers)
            context['branch_managers'] = br_emails
            context['subject'] = "Special Approval from GM Reminder"
            context['title'] = "The following Cost Sheet is Special Approved from GM and Waiting for PO:"
            remind = sorted(remind, key=lambda k: k['branch']) 
            context['data'] = remind
            if remind:
                self.pool.get('email.template').send_mail(cr, uid, template_id, uid, force_send=True, context=context)
        return True

    @api.multi
    def od_btn_open_timsheet_for_opp(self):

        task_pool = self.env['project.task']
        work_pool = self.env['project.task.work']
        lead_id = self.lead_id and self.lead_id.id
        if lead_id:
            task_search_dom = [('od_opp_id','=',lead_id)]
            task_ids = [task.id for task in task_pool.search(task_search_dom)]
            work_search_dom = [('task_id','in',task_ids)]
            all_timesheet_ids = [work.hr_analytic_timesheet_id for work in work_pool.search(work_search_dom)]
            timesheet_ids = []
            for timesheet in all_timesheet_ids:
                if timesheet:
                    timesheet_ids.append(timesheet.id)
            domain = [('id','in',timesheet_ids)]
            return {
                'domain':domain,
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'hr.analytic.timesheet',
                'type': 'ir.actions.act_window',
            }

    @api.one
    def od_get_timesheet_amount(self):
        task_pool = self.env['project.task']
        work_pool = self.env['project.task.work']
        lead_id = self.lead_id and self.lead_id.id
        if lead_id:
            task_search_dom = [('od_opp_id','=',lead_id)]
            task_ids = [task.id for task in task_pool.search(task_search_dom)]
            work_search_dom = [('task_id','in',task_ids)]
            all_timesheet_ids = [work.hr_analytic_timesheet_id for work in work_pool.search(work_search_dom)]
            timesheet_amounts = []
            for timesheet in all_timesheet_ids:
                if timesheet:
                    timesheet_amounts.append(timesheet.amount)
            amount = sum(timesheet_amounts)
            self.od_timesheet_amount = amount
            
    @api.one
    def od_get_no_of_change_mgmt(self):
        cm_recs = self.env['change.management'].search([('cost_sheet_id','=', self.id)])
        self.count_change_mgmt = len(cm_recs)
            
    @api.one 
    def _get_pre_opn_cost(self):
        pre_cost =0.0 
        if self.od_journal_amount:
            pre_cost += self.od_journal_amount 
#         if self.od_timesheet_amount:
#             pre_cost += self.od_timesheet_amount 
        self.pre_opn_cost = pre_cost
    
    @api.one    
    def _get_prn_ven_reb_cost(self):
        prn_ven_reb_cost = 0.0
        for line in self.vendor_rebate_line:
            prn_ven_reb_cost += line.value
        self.prn_ven_reb_cost = prn_ven_reb_cost
        
    @api.multi
    def od_btn_open_account_move_lines(self):
        account_move_line = self.env['account.move.line']
        lead_id = self.lead_id and self.lead_id.id
        if lead_id:
            domain = [('od_opp_id','=',lead_id),('move_id.state', '<>', 'draft')]
            return {
                'domain':domain,
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.move.line',
                'type': 'ir.actions.act_window',
            }
    
    @api.multi
    def od_open_lg_request(self):
        cost_sheet_id = self.id
        partner_id = self.lead_id.partner_id and self.lead_id.partner_id.id or False
        sale_val = self.lead_id.planned_revenue
        context = self.env.context
        ctx = context.copy()
        ctx['default_cost_sheet_id'] = cost_sheet_id
        ctx['default_partner_id'] = partner_id
        ctx['default_job_amt'] = sale_val
        ctx['default_guarantee_name'] = 'performance_bond'
        if cost_sheet_id:
            domain = [('cost_sheet_id','=',cost_sheet_id)]
            return {
                'domain':domain,
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'od.lg.request.form',
                'type': 'ir.actions.act_window',
                'context':ctx,
            }
            
    @api.multi
    def od_btn_open_change_mgmt(self):
        cs_id = self.id
#         company_id =self.env.user.company_id
#         pmo_user =19 
#         if company_id ==6:
#             pmo_user =142  
        context = self.env.context
        ctx = context.copy()
        ctx['change'] = True
        ctx['default_cost_sheet_id'] = cs_id
#         ctx['default_branch_id'] = self.od_branch_id and self.od_branch_id.id or False
#         ctx['default_first_approval_manager_id'] = pmo_user

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
            
    
    @api.one
    def od_get_lead_journal_amount(self):
        account_ids = []
        account_move_line = self.env['account.move.line']
        lead_id = self.lead_id and self.lead_id.id
        company_id = self.company_id and self.company_id.id or False
        account_id = self.get_product_id_from_param('pre_op_account_id')
        if company_id ==1:
            account_ids.append(account_id)
            adh_account_id = self.get_product_id_from_param('pre_op_account_id_adh')
            account_ids.append(adh_account_id)
        if company_id ==6:
            account_id = self.get_product_id_from_param('pre_op_account_id_ksa')
            account_ids.append(account_id)
        domain = [('account_id', 'in', account_ids),('od_opp_id','=',lead_id),('move_id.state', '<>', 'draft')]
        journal_lines = account_move_line.search(domain)
        amount = sum([mvl.debit for mvl in journal_lines])
        self.od_journal_amount = amount
        
    def default_get(self, cr, uid, fields, context=None):
        res = super(od_cost_sheet,self).default_get(cr,uid,fields,context=context)
        if res:
            if not res.get('pre_sales_engineer'):
                raise Warning("Kindly Fill Pre Sale Engineer In Opportunity")
        company_pool = self.pool.get('res.company')
        company_id = res.get('company_id')
        proposal_validity = "Proposal Validity Starting from its Date: 30 Days\nProposal Sales Currency: "
        if company_id:
            company_obj = company_pool.browse(cr,uid,company_id)
            currency_name = company_obj.currency_id and company_obj.currency_id.name or ''
            proposal_validity = proposal_validity + currency_name
            res['proposal_validity_duration'] = proposal_validity
        return res

    @api.multi
    def od_open_hr_expense_claim(self):
        hr_exp_line = self.env['hr.expense.line']
        lead_id = self.lead_id and self.lead_id.id
        domain = [('od_opp_id','=',lead_id),('od_state','not in',('draft','cancelled','confirm','second_approval'))]
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
        lead_id = self.lead_id and self.lead_id.id
        domain = [('od_opp_id','=',lead_id),('od_state','not in',('draft','cancelled','confirm','second_approval'))]
        hr_exp_obj =hr_exp_line.search(domain)
        amount  = sum([hr.total_amount for hr in hr_exp_obj])
        self.od_hr_claim_amount = amount


    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        reads = self.read(cr, uid, ids, ['name','number'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['number']:
                name = '[' + record['number'] +'] ' + name
            res.append((record['id'], name))
        return res
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if operator in expression.NEGATIVE_TERM_OPERATORS:
            domain = [('number', operator, name), ('name', operator, name)]
        else:
            domain = ['|', ('number', operator, name), ('name', operator, name)]
        ids = self.search(cr, user, expression.AND([domain, args]), limit=limit, context=context)
        return self.name_get(cr, user, ids, context=context)
    # @api.multi
    # @api.depends('name', 'number')
    # def name_get(self):
    #     result = []
    #     for sheet in self:
    #         number = self.number
    #         name = self.name
    #         result.append((sheet.id, '[%s]%s' % (number, name)))
    #     return result

    def grouped_brand_weight(self,res,all_brand_cost):
        disc = (abs(self.special_discount)/(self.sum_tot_sale or 1.0))*100.0
        result = []
        for item in res :
            check = False
            for r_item in result :
                if item['manufacture_id'] == r_item['manufacture_id'] :
                    check = True
                    total_sale = r_item['total_sale']
                    total_sale += item['total_sale']
                    r_item['total_sale'] = total_sale
                    r_item['total_sale_after_disc'] = total_sale * (1-(disc/100.0))
                    total_cost = r_item['total_cost']
                    total_cost += item['total_cost']
                    r_item['total_cost'] = total_cost
                    
                    sup_cost = r_item['sup_cost']
                    sup_cost += item['sup_cost']
                    r_item['sup_cost'] = sup_cost
                    
            if check == False :
                item['all_brand_cost'] = all_brand_cost
                result.append( item )
        return result

    def get_brand_vals(self):
        trn_included = self.included_trn_in_quotation
        mat_incuded = self.included_in_quotation
        disc = (abs(self.special_discount)/(self.sum_tot_sale or 1.0))*100.0
        res = []
        all_brand_cost = 0.0
        for line in self.mat_main_pro_line:
            if mat_incuded:
                res.append({'manufacture_id':line.manufacture_id and line.manufacture_id.id or False,
                    'total_sale':line.line_price,
                    'total_sale_after_disc': line.line_price * (1-(disc/100.0)),
                    'total_cost': line.line_cost_local_currency,
                    'sup_cost':line.discounted_total_supplier_currency,
                    })
                all_brand_cost += line.line_cost_local_currency
        for line in self.trn_customer_training_line:
            if trn_included:
                res.append({'manufacture_id':line.manufacture_id and line.manufacture_id.id or False,
                    'total_sale':line.line_price,
                    'total_sale_after_disc': line.line_price * (1-(disc/100.0)),
                    'total_cost': line.line_cost_local_currency,
                    'sup_cost':line.discounted_total_supplier_currency,
                    #'sup_cost':0.0 Commented by aslam and above line added by aslam because it is manually making zero instead of supplier cost currency 
                    })
                all_brand_cost += line.line_cost_local_currency
        result = self.grouped_brand_weight(res,all_brand_cost)
        return result
    
    
    @api.one
    def generate_brand_weight(self):
        vals = self.get_brand_vals()
        self.mat_brand_weight_line.unlink()
        self.mat_brand_weight_line = vals
        
        
    def grouped_prdgrp_weight(self,res,all_group_cost,all_group_sale=0.0):
        result = []
        for item in res :
            check = False
            for r_item in result :
                if item['pdt_grp_id'] == r_item['pdt_grp_id'] :
                    check = True
                    total_sale = r_item['total_sale']
                    total_sale += item['total_sale']
                    r_item['total_sale'] = total_sale
                    total_cost = r_item['total_cost']
                    total_cost += item['total_cost']
                    r_item['total_cost'] = total_cost
                    
                  
            if check == False :
                item['all_group_cost'] = all_group_cost
                item['all_group_sale'] = all_group_sale
                result.append( item )
        return result
    
    def grouped_tech_weight(self,res,all_group_cost):
        result = []
        for item in res :
            check = False
            for r_item in result :
                if item['pdt_grp_id'] == r_item['pdt_grp_id'] :
                    check = True
                    total_sale = r_item['total_sale']
                    total_sale += item['total_sale']
                    r_item['total_sale'] = total_sale
                    total_cost = r_item['total_cost']
                    total_cost += item['total_cost']
                    r_item['total_cost'] = total_cost
                    vat = r_item['vat']
                    vat += item['vat']
                    r_item['vat'] = vat
                  
            if check == False :
                item['all_group_cost'] = all_group_cost
                result.append( item )
        return result
    
    
    def get_pdtgrp_vals(self):
        res = []
        all_group_cost = 0.0
        all_group_sale = 0.0
        disc = 0.0
#         disc =abs(self.sp_disc_percentage)
        if self.included_in_quotation:
            for line in self.mat_main_pro_line:
                res.append({'pdt_grp_id':line.part_no and line.part_no.od_pdt_group_id and line.part_no.od_pdt_group_id.id,
                    'total_sale':line.line_price,
                  
                    'total_cost': line.line_cost_local_currency,
                    })
                all_group_cost += line.line_cost_local_currency
                all_group_sale +=line.line_price
        if self.included_trn_in_quotation:
            for line in self.trn_customer_training_line:
                res.append({'pdt_grp_id':line.part_no and line.part_no.od_pdt_group_id and line.part_no.od_pdt_group_id.id,
                    'total_sale':line.line_price,
                    'total_cost': line.line_cost_local_currency,
                    })
                all_group_cost += line.line_cost_local_currency
                all_group_sale +=line.line_price
        
        if self.included_bim_in_quotation:
            for line in self.ps_vendor_line:
                res.append({'pdt_grp_id':line.part_no and line.part_no.od_pdt_group_id and line.part_no.od_pdt_group_id.id,
                    'total_sale':line.line_price,
                    'total_cost': line.line_cost_local_currency,
                    })
                all_group_cost += line.line_cost_local_currency
                all_group_sale +=line.line_price
        
        if self.included_info_sec_in_quotation:
            for line in self.info_sec_vendor_line:
                res.append({'pdt_grp_id':line.part_no and line.part_no.od_pdt_group_id and line.part_no.od_pdt_group_id.id,
                    'total_sale':line.line_price,
                    'total_cost': line.line_cost_local_currency,
                    })
                all_group_cost += line.line_cost_local_currency
                all_group_sale +=line.line_price
        
        if self.included_om_in_quotation:
            for line in self.om_tech_line:
                res.append({'pdt_grp_id':line.part_no and line.part_no.od_pdt_group_id and line.part_no.od_pdt_group_id.id,
                    'total_sale':line.line_price,
                    'total_cost': line.line_cost_local_currency,
                    })
                all_group_cost += line.line_cost_local_currency
                all_group_sale +=line.line_price
            for line in self.om_eqpmentreq_line:
                res.append({'pdt_grp_id':line.part_no and line.part_no.od_pdt_group_id and line.part_no.od_pdt_group_id.id,
                    'total_sale':line.line_price,
                    'total_cost': line.line_cost_local_currency,
                    })
                all_group_cost += line.line_cost_local_currency
                all_group_sale +=line.line_price
            
            
        result = self.grouped_prdgrp_weight(res,all_group_cost,all_group_sale)
        
        for val in result:
            val['disc'] = disc
            sale = val.get('total_sale')
            sal_aftr_disc = sale * (1-(disc/100.0))
            val['sale_aftr_disc'] =sal_aftr_disc
        return result
    
    
    
    def get_tech_pdtgrp_vals(self):
        res = []
        all_group_cost = 0.0
        disc =abs(self.sp_disc_percentage)
        if self.included_bim_in_quotation:
            for line in self.imp_tech_line:
                res.append({'pdt_grp_id':line.part_no and line.part_no.od_pdt_group_id and line.part_no.od_pdt_group_id.id,
                    'total_sale':line.line_price,
                  
                    'total_cost': line.line_cost_local_currency,
                    'vat':line.vat_value
                    })
                all_group_cost += line.line_cost_local_currency
        if self.included_info_sec_in_quotation:
            for line in self.info_sec_tech_line:
                res.append({'pdt_grp_id':line.part_no and line.part_no.od_pdt_group_id and line.part_no.od_pdt_group_id.id,
                    'total_sale':line.line_price,
                  
                    'total_cost': line.line_cost_local_currency,
                    'vat':line.vat_value
                    })
                all_group_cost += line.line_cost_local_currency
        if self.included_bmn_in_quotation:
            for line in self.amc_tech_line:
                res.append({'pdt_grp_id':line.part_no and line.part_no.od_pdt_group_id and line.part_no.od_pdt_group_id.id,
                    'total_sale':line.line_price,
                    'total_cost': line.line_cost_local_currency,
                      'vat':line.vat_value
                    })
                all_group_cost += line.line_cost_local_currency
        
            
        result = self.grouped_tech_weight(res,all_group_cost)
        return result
    
    @api.one
    def generate_group_weight(self):
        vals = self.get_pdtgrp_vals()
        self.mat_group_weight_line.unlink()
        self.mat_group_weight_line = vals
    
    def generate_tech_mp_products(self):
        vals = self.get_tech_pdtgrp_vals()
        self.mp_tech_summary_line.unlink()
        self.mp_tech_summary_line = vals
    
    
    def get_tot_sale_cost(self,line_id):
        tot_sale =0.0
        tot_cost =0.0
        for line in line_id:
            tot_sale += line.line_price 
            tot_cost += line.line_cost_local_currency 
        profit = tot_sale - tot_cost 
        return tot_sale,tot_cost,profit

    
    def get_tot_sale_cost2(self,line_id):
        tot_sale =0.0
        tot_cost =0.0
        for line in line_id:
            tot_sale += line.line_price 
            tot_cost += line.line_cost
        profit = tot_sale - tot_cost 
        return tot_sale,tot_cost,profit
    
    
    def get_imp_vals(self):
        result = []
        if (self.bim_tot_sale1 != 0.0 or self.bim_tot_cost1 != 0.0):
            tech_sale,tech_cost,tech_profit = self.get_tot_sale_cost(self.imp_tech_line)
            result.append({'sale': self.bim_tot_sale1 - tech_sale,
                            'cost':self.bim_tot_cost1 - tech_cost,'profit':self.bim_profit1 - tech_profit,'tab':'bim'})
        if (self.oim_tot_sale1 != 0.0 or self.oim_tot_cost1 != 0.0):
            tech_sale1,tech_cost1,tech_profit1 = self.get_tot_sale_cost(self.ps_vendor_line)
            result.append({'sale':self.oim_tot_sale1 - tech_sale1,
                           'cost':self.oim_tot_cost1 - tech_cost1,'profit':self.oim_profit1 - tech_profit1,'tab':'oim'})
        return result
    
    def get_info_sec_vals(self):
        result = []
        if (self.bis_tot_sale1 != 0.0 or self.bis_tot_cost1 != 0.0):
            tech_sale,tech_cost,tech_profit = self.get_tot_sale_cost(self.info_sec_tech_line)
            result.append({'sale': self.bis_tot_sale1 - tech_sale,
                            'cost':self.bis_tot_cost1 - tech_cost,'profit':self.bis_profit1 - tech_profit,'tab':'bis'})
        if (self.ois_tot_sale1 != 0.0 or self.ois_tot_cost1 != 0.0):
            tech_sale1,tech_cost1,tech_profit1 = self.get_tot_sale_cost(self.info_sec_vendor_line)
            result.append({'sale':self.ois_tot_sale1 - tech_sale1,
                           'cost':self.ois_tot_cost1 - tech_cost1,'profit':self.ois_profit1 - tech_profit1,'tab':'ois'})
        return result
    
    def get_amc_vals(self):
        result = []
        tech_sale,tech_cost,tech_profit = self.get_tot_sale_cost(self.amc_tech_line)
        if (self.bmn_tot_sale1 != 0.0 or self.bmn_tot_cost1 != 0.0):
            result.append({'sale':self.bmn_tot_sale1 -tech_sale,'cost':self.bmn_tot_cost1 - tech_cost,'profit':self.bmn_profit1 - tech_profit,'tab':'bmn'})
        if (self.omn_tot_sale1 != 0.0 or self.omn_tot_cost1 != 0.0):
            result.append({'sale':self.omn_tot_sale1,'cost':self.omn_tot_cost1,'profit':self.omn_profit1,'tab':'omn'})
        return result
    
    def get_om_vals(self):
        result = []
        redist_re_manual= self.redist_re_manual
        if (self.o_m_tot_sale1 != 0.0 or self.o_m_tot_cost1 != 0.0):
            sale,cost,profit = self.get_tot_sale_cost2(self.om_residenteng_line) 
            if redist_re_manual:
                sale,cost,profit   = 0.0,0.0,0.0
            sale2,cost2,profit2= self.get_tot_sale_cost2(self.om_extra_line)
            sale += sale2 
            cost += cost2 
            profit += profit2
            result.append({'sale':sale,'cost':cost,'profit':profit,'tab':'om'})
        return result
    
    def get_extra_vals(self):
        result = []
        sale = cost = 0.0
        if self.included_in_quotation:
            for line in self.mat_extra_expense_line:
                sale += line.line_price2
                cost += line.line_cost_local
            
            if sale or cost:
                result.append({'sale':sale,'cost':cost,'profit':sale-cost,'tab':'mat' })
        sale = cost = 0.0
        if self.included_trn_in_quotation:
            for line in self.trn_customer_training_extra_expense_line:
                sale += line.line_price2
                cost += line.line_cost_local
            if sale or cost:
                result.append({'sale':sale,'cost':cost,'profit':sale-cost,'tab':'trn' })
        return result

    def generate_impl_weight(self):
        res = []
        if self.included_bim_in_quotation:
            vals = self.get_pdtgrp_vals()
            imp_vals = self.get_imp_vals()
    #         disc =  abs(self.sp_disc_percentage)
            disc =0.0
            for imp_val in imp_vals:
                tab = imp_val.get('tab')
                sale = imp_val.get('sale')
                cost = imp_val.get('cost')
                profit = imp_val.get('profit')
                for val in vals:
                    weight = val.get('total_cost')/(val.get('all_group_cost',1.0) or 1.0)
                    pdt_grp_id = val.get('pdt_grp_id')
                    total_sale = sale * weight
                    total_cost =  cost * weight 
                    
                    sale_aftr_disc = total_sale * (1-(disc/100.0))
                    total_profit = (sale_aftr_disc - total_cost) 
                    res.append({'pdt_grp_id':pdt_grp_id,
                                'tab':tab,
                                'total_sale':total_sale,
                                'disc':disc,
                                'sale_aftr_disc': sale_aftr_disc,
                                'total_cost':total_cost,
                                'profit':total_profit})
            
        self.imp_weight_line.unlink()
        self.imp_weight_line = res
        
    def generate_info_sec_weight(self):
        res = []
        if self.included_info_sec_in_quotation:
            vals = self.get_pdtgrp_vals()
            info_sec_vals = self.get_info_sec_vals()
    #         disc =  abs(self.sp_disc_percentage)
            disc =0.0
            for info_sec_val in info_sec_vals:
                tab = info_sec_val.get('tab')
                sale = info_sec_val.get('sale')
                cost = info_sec_val.get('cost')
                profit = info_sec_val.get('profit')
                for val in vals:
                    weight = val.get('total_cost')/(val.get('all_group_cost',1.0) or 1.0)
                    pdt_grp_id = val.get('pdt_grp_id')
                    total_sale = sale * weight
                    total_cost =  cost * weight 
                    
                    sale_aftr_disc = total_sale * (1-(disc/100.0))
                    total_profit = (sale_aftr_disc - total_cost) 
                    res.append({'pdt_grp_id':pdt_grp_id,
                                'tab':tab,
                                'total_sale':total_sale,
                                'disc':disc,
                                'sale_aftr_disc': sale_aftr_disc,
                                'total_cost':total_cost,
                                'profit':total_profit})
            
        self.info_sec_weight_line.unlink()
        self.info_sec_weight_line = res
    
    def generate_amc_weight(self):
        res = []
        if self.included_bmn_in_quotation:
            vals = self.get_pdtgrp_vals()
            imp_vals = self.get_amc_vals()
    #         disc = abs(self.sp_disc_percentage)
            disc =0.0
            for imp_val in imp_vals:
                tab = imp_val.get('tab')
                sale = imp_val.get('sale')
                cost = imp_val.get('cost')
                profit = imp_val.get('profit')
                for val in vals:
                    weight = val.get('total_cost')/(val.get('all_group_cost',1.0) or 1.0)
                    pdt_grp_id = val.get('pdt_grp_id')
                    total_sale = sale * weight 
                    total_cost =  cost * weight 
                    sale_aftr_disc = total_sale * (1-(disc/100.0))
                    total_profit = (sale_aftr_disc - total_cost) 
                    res.append({'pdt_grp_id':pdt_grp_id,
                                'tab':tab,
                                'total_sale':total_sale,
                                'disc':disc,
                                'sale_aftr_disc': sale_aftr_disc,
                                'total_cost':total_cost,
                                'profit':total_profit})
            
        self.amc_weight_line.unlink()
        self.amc_weight_line = res
    
    def generate_om_weight(self):
        res = []
        if self.included_om_in_quotation:
            vals = self.get_pdtgrp_vals()
            imp_vals = self.get_om_vals()
            disc =0.0
    #         disc = abs(self.sp_disc_percentage)
            for imp_val in imp_vals:
                tab = imp_val.get('tab')
                sale = imp_val.get('sale')
                cost = imp_val.get('cost')
                profit = imp_val.get('profit')
                for val in vals:
                    weight = val.get('total_cost')/(val.get('all_group_cost',1.0) or 1.0)
                    if not weight:
                        weight = val.get('total_sale')/(val.get('all_group_sale',1.0) or 1.0)
                    pdt_grp_id = val.get('pdt_grp_id')
                    total_sale = sale * weight 
                    total_cost =  cost * weight 
                    sale_aftr_disc = total_sale * (1-(disc/100.0))
                    total_profit = (sale_aftr_disc - total_cost) 
                    res.append({'pdt_grp_id':pdt_grp_id,
                                'tab':tab,
                                'total_sale':total_sale,
                                'disc':disc,
                                'sale_aftr_disc': sale_aftr_disc,
                                'total_cost':total_cost,
                                'profit':total_profit})
            
        
        
        
        
        self.om_weight_line.unlink()
        self.om_weight_line = res
        
    
    def generate_extra_weight(self):
        res = []
        vals = self.get_pdtgrp_vals()
        imp_vals = self.get_extra_vals()
        disc =0.0
#         disc = abs(self.sp_disc_percentage)
        for imp_val in imp_vals:
            tab = imp_val.get('tab')
            sale = imp_val.get('sale')
            cost = imp_val.get('cost')
            profit = imp_val.get('profit')
            for val in vals:
                weight = val.get('total_cost')/(val.get('all_group_cost',1.0) or 1.0)
                pdt_grp_id = val.get('pdt_grp_id')
                total_sale = sale * weight 
                total_cost =  cost * weight 
                sale_aftr_disc = total_sale * (1-(disc/100.0))
                total_profit = (sale_aftr_disc - total_cost) 
                
                res.append({'pdt_grp_id':pdt_grp_id,
                            'tab':tab,
                            'total_sale':total_sale,
                             'disc':disc,
                            'sale_aftr_disc': sale_aftr_disc,
                            'total_cost':total_cost,
                            'profit':total_profit})
            
        self.extra_weight_line.unlink()
        self.extra_weight_line = res




    def od_get_company_id(self):
        return self.env.user.company_id

    def default_dead_line_data(self):
        line = [
           
            {'deadline_type':"project_start"},
           
            {'deadline_type':"maint_start"},
            {'deadline_type':"maint_close"},
            {'deadline_type':"availability"},
            {'deadline_type':"start"},
        ]
        return line
    
    def default_payement_term_data(self):
        line = [
            {'payment_name':"Advanced Payment with PO",'payment_percentage':'100%'},
           
        ]
        return line

#     @api.one
#     def btn_freeze(self):
#         self.update_cost_sheet()
#         self.freeze = True
# 
#     @api.one
#     def btn_unfreeze(self):
# 
#         self.freeze = False
#         self.update_cost_sheet()

    @api.one
    def copy_from_mat(self):
        for line in self.mat_copy_cost_sheet_id.mat_main_pro_line:
            line.copy({'cost_sheet_id':self.id,'group':False,'section_id':False})
    @api.one
    def copy_from_opt(self):
        for line in self.opt_copy_cost_sheet_id.mat_optional_item_line:
            line.copy({'cost_sheet_id':self.id,'group_id':False,'section_id':False})

    @api.one
    def copy_from_trn(self):
        for line in self.trn_copy_cost_sheet_id.trn_customer_training_line:
            line.copy({'cost_sheet_id':self.id,'group':False,'section_id':False,})

    @api.one
    def copy_from_bmn_spare_parts(self):
        for line in self.bmn_copy_spareparts_cs_id.bmn_spareparts_beta_it_maintenance_line:
            line.copy({'cost_sheet_id':self.id,'group':False,'section_id':False,})

    @api.one
    def copy_from_bmn_eqpcoverd(self):
        for line in self.bmn_copy_eqpcoverd_cs_id.bmn_eqp_cov_line:
            line.copy({'cost_sheet_id':self.id})

    @api.one
    def copy_from_omn_spare_parts(self):
        for line in self.omn_copy_spareparts_cs_id.omn_spare_parts_line:
            line.copy({'cost_sheet_id':self.id,'group':False,'section_id':False,})

    @api.one
    def copy_from_omn_eqpcoverd(self):
        for line in self.omn_copy_spareparts_cs_id.omn_eqp_cov_line:
            line.copy({'cost_sheet_id':self.id})
    @api.one
    def copy_from_om_required_parts(self):
        for line in self.om_copy_eqp_required_cs_id.om_eqpmentreq_line:
            line.copy({'cost_sheet_id':self.id,'group':False,'section_id':False,})

    @api.one
    def copy_from_om_eqpcoverd(self):
        for line in self.om_copy_eqpcoverd_cs_id.o_m_eqp_cov_line:
            line.copy({'cost_sheet_id':self.id})

    @api.multi
    def quick_create_analytic(self):
        template_id = False
        if self.is_saudi_comp():
            template_id = 2451
        else:
            template_id = 2449
        owner_id = self.reviewed_id and self.reviewed_id.id or False
        type = 'contract'
        date = self.project_closing_date
        account_manager = self.sales_acc_manager and self.sales_acc_manager.id
        partner_id = self.od_customer_id and self.od_customer_id.id
        ctx = {'default_type':type,'default_od_owner_id':owner_id,'default_template_id':template_id,'default_date':date,
        'default_manager_id':account_manager,'partner_id':partner_id,
        'default_od_project_owner_id':owner_id,'default_od_amc_owner_id':owner_id,
        }
        return {
                    'view_type': 'form',
                    "view_mode": 'form',
                    'res_model': 'account.analytic.account',
                    'type': 'ir.actions.act_window',
                    'target':'new',
                    'context':ctx,
                    'flags': {'form': {'action_buttons': True}}
            }


    @api.one
    @api.depends('po_date')
    def get_po_date(self):
        self.po_date_kpi = self.po_date

    @api.one
    @api.depends('submitted_date','financial_proposal_date')
    def get_presale_kpi(self):
        submitted_date = self.submitted_date
        financial_proposal_date = self.financial_proposal_date
        if not financial_proposal_date:
            self.presale_kpi = 'not_available'
            
        if not submitted_date:
            self.presale_kpi = 'not_ok'
        else:
            if submitted_date[:10] > financial_proposal_date:
                self.presale_kpi = 'not_ok'
            else:
                self.presale_kpi = "ok"

    def days_between(self,date1, date2):
        d1 = datetime.strptime(date1, "%Y-%m-%d")
        d2 = datetime.strptime(date2, "%Y-%m-%d")
        return (d2 - d1).days
    
    
    
    
    def send_sales_kpi_not_ok_mail(self):
        po_date = self.po_date
        handover_date  = fields.Date.today()
        if handover_date and po_date:
            days = self.days_between(po_date,handover_date)
            if days >3:
                self.od_send_mail('cst_sheet_three_day_rule_not_ok_mail')
    
    
    @api.one
    @api.depends('po_date','handover_date')
    def get_sales_kpi(self):
        po_date = self.po_date
        handover_date = self.handover_date
        if not (handover_date and po_date):
            self.sales_kpi = 'not_available'
        else:
            handover_date = handover_date[:10]
            days = self.days_between(po_date,handover_date)
            if days >3:
                self.sales_kpi = 'not_ok'
            else:
                self.sales_kpi = 'ok'
    @api.one
    @api.depends('processed_date','handover_date')
    def get_owner_kpi(self):
        process_date = self.processed_date
        handover_date = self.handover_date
        if not (handover_date and process_date):
            self.owner_kpi = 'not_available'
        else:
            handover_date = handover_date[:10]
            process_date  = process_date[:10]
            days = self.days_between(handover_date,process_date)
            if days >5:
                self.owner_kpi = 'not_ok'
            else:
                self.owner_kpi = 'ok'
    @api.one
    @api.depends('pmo_date','approved_date')
    def get_finance_kpi(self):
        #Modified by Aslam as Processed date should also be Waiting PO date now
        process_date = self.pmo_date
        approved_date = self.approved_date
        if not (process_date and approved_date):
            self.finance_kpi = 'not_available'
        else:
            process_date = process_date[:10]
            approved_date  = approved_date[:10]
            days = self.days_between(process_date,approved_date)
            if days >2:
                self.finance_kpi = 'not_ok'
            else:
                self.finance_kpi = 'ok'
    def default_material_summary(self):
        res = """
        <h5 style="color: blue; text-align: center;"><strong><span>Material&nbsp;-&nbsp;المواد</span></strong></h5>
<h5 style="text-align: left;">Covers all types of Material, in case requested in this proposal, such as: Hardware, Software, Warranty, Subscriptions, Licenses, &amp; Training Centers</h5>
<h5 style="text-align: right;">تغطي كل أنواع المواد، في حال طلبها في هذا العرض، وهي على سبيل المثال: القطع، البرمجيات، الضمان، الاشتراكات، الرخص، والتدريب في المراكز</h5>
        """
        return res
    
    def default_optional_summary(self):
        res = """
        <h5 style="color: blue; text-align: center;"><strong><span>Optional Material&nbsp;-&nbsp;المواد</span></strong></h5>
    <h5 style="text-align: left;">Covers optional material, in case the customer requires them.</h5>
    <h5 style="text-align: right;">يشمل المواد الاختيارية في حال طلبها العميل</h5>
    """
        return res
    
    def default_implementation_summary(self):
        res = """
        <h5 style="color: blue; text-align: center;"><span><strong>Implementation -&nbsp;خدمات التركيب</strong></span></h5>
<h5 style="text-align: left;">Implementation &amp; Configuration Services for Devices &amp; Systems</h5>
<h5 style="text-align: right;">الخدمة الفنية للتركيب والتعريف للأجهزة والأنظمة</h5>
        """
        return res
    
    def default_info_sec_summary(self):
        
        res = """
        <h5 style="color: blue; text-align: center;"><span><strong>Information Security &amp; GRC -&nbsp; استشارات أمن المعلومات</strong></span></h5>
<h5 style="text-align: left;">Information Security, Governance, Risk Assessment, &amp; Compliance (GRC)</h5>
<h5 style="text-align: right;">استشارات أمن المعلومات  الحوكمة، تقييم المخاطر، والامتثال</h5>
        """
        return res
        
    def default_amc_summary(self):
        res = """
        <h5 style="color: blue; text-align: center;"><strong><span>Maintenance -&nbsp;الصيانة</span></strong></h5>
<h5 style="text-align: left;">Maintenance Services (Such as Preventive Maintenance, Remedial Maintenance, etc.). These services do not include manufacturer warranty or subscriptions. Refer to Material Section for warranty and subscription.</h5>
<h5 style="direction: rtl; text-align: right;">خدمة الصيانة (كالصيانة الوقائية الدورية، أو إصلاح المشاكل، أو غيرها). لا تشمل هذه الخدمة الضمان أو الاشتراكات المقدمة من قبل طرف الشركة المصنعة. يرجى الرجوع إلى قسم الضمان أوالاشتراكات في المواد</h5>
        """
        return res
    def default_operation_summary(self):

        res = """
        <h5 style="color: blue; text-align: center;"><strong><span>Operation -&nbsp;التشغيل</span></strong></h5>
<h5 style="text-align: left;">O&amp;M Service for Resident Engineers / Employees at Customer Site</h5>
<h5 style="direction: rtl; text-align: right;">خدمات التشغيل بواسطة مهندسين / موظفين مقيمين لدى العميل</h5>
        """
        return res

    @api.onchange('mat_select_all')
    def onchange_check_all(self):
        if self.mat_select_all:
            for x in self.mat_main_pro_line:
                x.check = True
        else:
            for x in self.mat_main_pro_line:
                x.check = False

    def gen_line_check(self,trg,line_id):
        if trg:
            for x in line_id:
                x.check = True
        else:
            for x in line_id:
                x.check = False

    @api.onchange('mat_opt_select_all')
    def onchange_mat_check_all(self):
        self.gen_line_check(self.mat_opt_select_all,self.mat_optional_item_line)

    @api.onchange('mat_ext_sel')
    def onchange_mat_ext_check_all(self):
        self.gen_line_check(self.mat_ext_sel,self.mat_extra_expense_line)

    @api.onchange('ren_main_select')
    def onchange_ren_main_check_all(self):
        self.gen_line_check(self.ren_main_select,self.ren_main_pro_line)

    @api.onchange('ren_opt_select')
    def onchange_ren_opt_check_all(self):
        self.gen_line_check(self.ren_opt_select,self.ren_optional_item_line)

    @api.onchange('trn_sel')
    def onchange_trn_check_all(self):
        self.gen_line_check(self.trn_sel,self.trn_customer_training_line)

    @api.onchange('trn_ext_sel')
    def onchange_trn_ext_check_all(self):
        self.gen_line_check(self.trn_ext_sel,self.trn_customer_training_extra_expense_line)

    @api.one
    def delete_mat_line(self):
        for line in self.mat_main_pro_line:
            if line.check:
                line.unlink()

    def delete_general_line(self,line_id):
        for line in line_id:
            if line.check:
                line.unlink()

    @api.one 
    def btn_del_mat_opt_line(self):
        self.delete_general_line(self.mat_optional_item_line)

    @api.one 
    def btn_del_mat_ext_line(self):
        self.delete_general_line(self.mat_extra_expense_line)

    @api.one 
    def btn_del_ren_main_line(self):
        self.delete_general_line(self.ren_main_pro_line)


    @api.one 
    def btn_del_ren_opt_line(self):
        self.delete_general_line(self.ren_optional_item_line)

    @api.one 
    def btn_del_trn_line(self):
        self.delete_general_line(self.trn_customer_training_line)

    @api.one 
    def btn_del_trn_ext_line(self):
        self.delete_general_line(self.trn_customer_training_extra_expense_line)

    
    @api.onchange('included_bmn_in_quotation')
    def onchange_included_amc(self):
        amc_include = self.included_bmn_in_quotation 
        if amc_include:
            self.select_a4 = True
            self.tabs_a4 = [[6,False,[4]]]
        else:
            self.select_a4 = False
            self.tabs_a4 = [[6,0,[False]]]
            
    
    @api.onchange('included_om_in_quotation')
    def onchange_included_om(self):
        amc_include = self.included_om_in_quotation 
        if amc_include:
            self.select_a5 = True
            self.tabs_a5 = [[6,0,[5]]]
        else:
            self.select_a5 = False
            self.tabs_a5 = [[6,0,[False]]]
    
    
    
   
#     @api.depends('select_a1','select_a2','select_a3','select_a4','select_a5',
#                  'tabs_a1','tabs_a2','tabs_a3','tabs_a4','tabs_a5',)
    
    
    @api.one
    def _compute_tab_sale(self):
        profit_vals = {1:self.mat_profit1,2:self.trn_profit1,3:self.bim_profit1 + self.oim_profit1,
                     4:self.bmn_profit1 + self.omn_profit1,5:self.o_m_profit1,6:self.bis_profit1 + self.ois_profit1,
                     }
        
        sale_vals = {1:self.mat_tot_sale1,2:self.trn_tot_sale1,3:self.bim_tot_sale1 + self.oim_tot_sale1,
                     4:self.bmn_tot_sale1 + self.omn_tot_sale1,5:self.o_m_tot_sale1,6:self.bis_tot_sale1 + self.ois_tot_sale1,
                     }

        cost_vals = {
        1:self.mat_tot_cost1,2:self.trn_tot_cost1,3:self.bim_tot_cost1 + self.oim_tot_cost1,
                     4:self.bmn_tot_cost1 + self.omn_tot_cost1,5:self.o_m_tot_cost1,6:self.bis_tot_cost1 + self.ois_tot_cost1,

        }
        
        total_sale = self.sum_tot_sale
        special_discount = self.special_discount
        tot_rebate = self.prn_ven_reb_cost
        #Training rebate added as per elayyan instruction
        mat_trn_cost = self.mat_tot_cost1
        
        if self.select_a1:
            sale =0.0 
            profit =0.0
            cost =0.0
            reb_cost = 0.0
            for tab in self.tabs_a1:
                sale += sale_vals.get(tab.id,0.0)
                cost +=cost_vals.get(tab.id,0.0)
                profit += profit_vals.get(tab.id,0.0)
                if tab.id != 3 :
                    reb_cost += cost_vals.get(tab.id,0.0)
            pre_opn_cost = self.pre_opn_cost or 0.0
            profit_a1 = profit - pre_opn_cost 
            self.profit_a1 = profit_a1
            self.sales_a1 = sale
            cost_a1 = cost + pre_opn_cost
            self.cost_a1 = cost_a1
            disc=(sale/(total_sale or 1.0)) * abs(special_discount)
            disc_sale= sale - disc 
            self.disc_sales_a1 = disc_sale
            
            rebate_a1 = tot_rebate
            self.rebate_a1 = rebate_a1
            self.profit_with_rebate_a1 = rebate_a1 + profit_a1
            
        if self.select_a2:
            sale =0.0 
            profit =0.0
            cost =0.0
            reb_cost = 0.0
            for tab in self.tabs_a2:
                sale += sale_vals.get(tab.id,0.0)
                cost +=cost_vals.get(tab.id,0.0)
                profit += profit_vals.get(tab.id,0.0)
                if tab.id != 3 :
                    reb_cost += cost_vals.get(tab.id,0.0)
            self.profit_a2 = profit 
            self.sales_a2 = sale
            self.cost_a2 = cost
            disc=(sale/(total_sale or 1.0)) * abs(special_discount)
            disc_sale= sale - disc 
            self.disc_sales_a2 = disc_sale
            
            rebate_a2 = 0.0
            self.rebate_a2 = rebate_a2
            self.profit_with_rebate_a2 = rebate_a2 + profit
            
        if self.select_a3:
            sale =0.0 
            profit =0.0
            cost =0.0
            reb_cost = 0.0
            for tab in self.tabs_a3:
                sale += sale_vals.get(tab.id,0.0)
                profit += profit_vals.get(tab.id,0.0)
                cost +=cost_vals.get(tab.id,0.0)
                if tab.id != 3 :
                    reb_cost += cost_vals.get(tab.id,0.0)
            self.profit_a3 = profit 
            self.sales_a3 = sale
            self.cost_a3 = cost
            disc=(sale/(total_sale or 1.0)) * abs(special_discount)
            disc_sale= sale - disc 
            self.disc_sales_a3 = disc_sale
            
            rebate_a3 = 0.0
            self.rebate_a3 = rebate_a3
            self.profit_with_rebate_a3 = rebate_a3 + profit
            
        if self.select_a4:
            sale =0.0 
            profit =0.0
            cost =0.0
            for tab in self.tabs_a4:
                sale += sale_vals.get(tab.id,0.0)
                profit += profit_vals.get(tab.id,0.0)
                cost +=cost_vals.get(tab.id,0.0)
            self.profit_a4 = profit 
            self.sales_a4 = sale
            self.cost_a4 = cost
            disc=(sale/(total_sale or 1.0)) * abs(special_discount)
            disc_sale= sale - disc 
            self.disc_sales_a4 = disc_sale
            
            rebate_a4 = 0.0
            self.rebate_a4 = rebate_a4
            self.profit_with_rebate_a4 = rebate_a4 + profit
        
        if self.select_a5:
            sale =0.0 
            profit =0.0
            cost =0.0
            for tab in self.tabs_a5:
                sale += sale_vals.get(tab.id,0.0)
                profit += profit_vals.get(tab.id,0.0)
                cost +=cost_vals.get(tab.id,0.0)
            self.profit_a5 = profit 
            self.sales_a5 = sale
            self.cost_a5 = cost
            disc=(sale/(total_sale or 1.0)) * abs(special_discount)
            disc_sale= sale - disc 
            self.disc_sales_a5 = disc_sale
            
            rebate_a5 = 0.0
            self.rebate_a5 = rebate_a5
            self.profit_with_rebate_a5 = rebate_a5 + profit
            
        if self.special_discount:
            self.select_a6 = True
 
        if self.select_a6:
            profit = self.sum_profit
            sale = self.sum_total_sale
            self.disc_tot_profit = profit 
            self.disc_tot_sale = sale
    
    @api.one        
    def od_get_sla_metrics_vals(self):
        x=self.od_resol_time_ctc
        y=self.od_resol_time_maj
        z=self.od_resol_time_min
        x1=self.od_respons_time_ctc
        y1=self.od_respons_time_maj
        z1=self.od_respons_time_min
        if x:
            self.od_resol_time_ctc_rel = x
        if y:
            self.od_resol_time_maj_rel = y
        if z:
            self.od_resol_time_min_rel = z
        if x1:
            self.od_respons_time_ctc_rel = x1
        if y1:
            self.od_respons_time_maj_rel = y1
        if z1:
            self.od_respons_time_min_rel = z1
    
    open_req_count = fields.Integer(string="Open Request Count")
    sam_req_for_modify = fields.Boolean(string="Is Requested by SAM?")
    # Revenue Structure
    analytic_a0 = fields.Many2one('account.analytic.account',string="Analytic A0",copy=False)
    analytic_a1 = fields.Many2one('account.analytic.account',string="Analytic A1",copy=False)
    analytic_a2 = fields.Many2one('account.analytic.account',string="Analytic A2",copy=False)
    analytic_a3 = fields.Many2one('account.analytic.account',string="Analytic A3",copy=False)
    analytic_a4 = fields.Many2one('account.analytic.account',string="Analytic A4",copy=False)
    analytic_a5 = fields.Many2one('account.analytic.account',string="Analytic A5",copy=False)
     
    #Analytic states: Related field added by Aslam on 16-Oct-2019
    analytic_a0_state = fields.Selection(string="State",related='analytic_a0.state')
    analytic_a1_state = fields.Selection(string="State",related='analytic_a1.state')
    analytic_a2_state = fields.Selection(string="State",related='analytic_a2.state')
    analytic_a3_state = fields.Selection(string="State",related='analytic_a3.state')
    analytic_a4_state = fields.Selection(string="State",related='analytic_a4.state')
    analytic_a5_state = fields.Selection(string="State",related='analytic_a5.state')
    
    
    tabs_a1 = fields.Many2many('od.cost.tabs','rel_cost_a1_tabs','cost_id','tab_id',string="Tabs A1",domain=[('id','not in',(4,5))])
    tabs_a2 = fields.Many2many('od.cost.tabs','rel_cost_a2_tabs','cost_id','tab_id',string="Tabs A2",domain=[('id','not in',(4,5))])
    tabs_a3 = fields.Many2many('od.cost.tabs','rel_cost_a3_tabs','cost_id','tab_id',string="Tabs A3",domain=[('id','not in',(4,5))] )
    tabs_a4 = fields.Many2many('od.cost.tabs','rel_cost_a4_tabs','cost_id','tab_id',string="Tabs A4",domain=[('id','=',4)])
    tabs_a5 = fields.Many2many('od.cost.tabs','rel_cost_a5_tabs','cost_id','tab_id',string="Tabs A5",domain=[('id','=',5)])
    
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
    select_a6 = fields.Boolean(string="Special Discount",readonly=True,compute='_compute_tab_sale')
    
    sales_a1 = fields.Float(string="Sales A1",compute='_compute_tab_sale')
    sales_a2 = fields.Float(string="Sales A2",compute='_compute_tab_sale')
    sales_a3 = fields.Float(string="Sales A3",compute='_compute_tab_sale')
    sales_a4 = fields.Float(string="Sales A4",compute='_compute_tab_sale')
    sales_a5 = fields.Float(string="Sales A5",compute='_compute_tab_sale')

    cost_a1 = fields.Float(string="Cost A1",compute='_compute_tab_sale')
    cost_a2 = fields.Float(string="Cost A2",compute='_compute_tab_sale')
    cost_a3 = fields.Float(string="Cost A3",compute='_compute_tab_sale')
    cost_a4 = fields.Float(string="Cost A4",compute='_compute_tab_sale')
    cost_a5 = fields.Float(string="Cost A5",compute='_compute_tab_sale')
    disc_tot_sale = fields.Float(string="Total Sale after Special Disc.",compute='_compute_tab_sale')
    
    disc_sales_a1 = fields.Float(string="Sales A1",compute='_compute_tab_sale')
    disc_sales_a2 = fields.Float(string="Sales A2",compute='_compute_tab_sale')
    disc_sales_a3 = fields.Float(string="Sales A3",compute='_compute_tab_sale')
    disc_sales_a4 = fields.Float(string="Sales A4",compute='_compute_tab_sale')
    disc_sales_a5 = fields.Float(string="Sales A5",compute='_compute_tab_sale')
    
    
    
    profit_a1 = fields.Float(string="Profit A1",compute='_compute_tab_sale')
    profit_a2 = fields.Float(string="Profit A2",compute='_compute_tab_sale')
    profit_a3 = fields.Float(string="Profit A3",compute='_compute_tab_sale')
    profit_a4 = fields.Float(string="Profit A4",compute='_compute_tab_sale')
    profit_a5 = fields.Float(string="Profit A5",compute='_compute_tab_sale')
    rebate_a1 = fields.Float(string="Rebate A1",compute='_compute_tab_sale')
    profit_with_rebate_a1 = fields.Float(string="Profit with Rebate A1",compute='_compute_tab_sale')
    rebate_a2 = fields.Float(string="Rebate A2",compute='_compute_tab_sale')
    profit_with_rebate_a2 = fields.Float(string="Profit with Rebate A2",compute='_compute_tab_sale')
    rebate_a3 = fields.Float(string="Rebate A3",compute='_compute_tab_sale')
    profit_with_rebate_a3 = fields.Float(string="Profit with Rebate A3",compute='_compute_tab_sale')
    rebate_a4 = fields.Float(string="Rebate A4",compute='_compute_tab_sale')
    profit_with_rebate_a4 = fields.Float(string="Profit with Rebate A4",compute='_compute_tab_sale')
    rebate_a5 = fields.Float(string="Rebate A5",compute='_compute_tab_sale')
    profit_with_rebate_a5 = fields.Float(string="Profit with Rebate A5",compute='_compute_tab_sale')
    disc_tot_profit = fields.Float(string="Profit A5",compute='_compute_tab_sale')
    
    
    
    periodicity_amc = fields.Selection([('weekly','Weekly'),('monthly','Monthly'),('quarterly','Quarterly'),('half_yearly','Half Yearly'),('yearly','Yearly')],string="Periodicity")
    no_of_l2_accounts_amc = fields.Integer(string="No.of L2 Accounts")
    l2_start_date_amc = fields.Date(string="Start Date")
    
    
    
    periodicity_om = fields.Selection([('weekly','Weekly'),('monthly','Monthly'),('quarterly','Quarterly'),('yearly','Yearly')],string="Periodicity")
    no_of_l2_accounts_om = fields.Integer(string="No.of L2 Accounts")
    l2_start_date_om = fields.Date(string="Start Date")
    
    
    
    mat_select_all = fields.Boolean(string="Select All")
    mat_opt_select_all = fields.Boolean(string="Select All")
    mat_ext_sel = fields.Boolean(string="Select All")

    ren_main_select = fields.Boolean(string="Select All")
    ren_opt_select = fields.Boolean(string="Select All")

    trn_sel = fields.Boolean(string="Select All")
    trn_ext_sel = fields.Boolean(string="Select All")

    bim_sel = fields.Boolean(string="Select All")

    pre_opn_move_id = fields.Many2one('account.move',string="Pre Opn Move")
    od_cost_centre_id =fields.Many2one('od.cost.centre',string='Cost Centre')
    od_branch_id =fields.Many2one('od.cost.branch',string='Branch')
    od_division_id =fields.Many2one('od.cost.division',string='Division')
    sale_team_id = fields.Many2one('crm.case.section',string="Sale Team",related="lead_id.section_id",readonly=True)
    op_stage_id = fields.Many2one('crm.case.stage',string="Opp Stage",related="lead_id.stage_id",readonly=True,store=True)    
    op_expected_booking = fields.Date(string="Opp Expected Booking",related="lead_id.date_action",readonly=True,store=True)
    other_division_ids = fields.Many2many('od.cost.division', 'od_cost_sheet_cost_division', 'cost_sheet_id', 'division_id', 'Other Technology Unit', \
             help="Other technology units associated with this cost sheet")  
   
    material_summary = fields.Html(string="Material Summary",default=default_material_summary)
    optional_summary = fields.Html(string="Optional Summary",default=default_optional_summary)
    implementation_summary = fields.Html(string="Implementation Summary",default=default_implementation_summary)
    info_sec_summary = fields.Html(string="Information security Summary",default=default_info_sec_summary)
    amc_summary = fields.Html(string="Amc Summary",default=default_amc_summary)
    operation_summary = fields.Html(string="Operation Summary",default=default_operation_summary)
    od_timesheet_amount = fields.Float(string="Timesheet Amount",compute="od_get_timesheet_amount",digits=dp.get_precision('Account'))
    count_change_mgmt = fields.Integer(string="Change Management Count",compute="od_get_no_of_change_mgmt")
    pre_opn_cost = fields.Float(string="Pre-Operation Cost",compute="_get_pre_opn_cost",digits=dp.get_precision('Account'))
    prn_ven_reb_cost = fields.Float(string="Principle Vendors Rebate",compute="_get_prn_ven_reb_cost",digits=dp.get_precision('Account'))
    od_journal_amount = fields.Float(string="Journal Amount",compute="od_get_lead_journal_amount",digits=dp.get_precision('Account'))
    finance_kpi = fields.Selection([('ok','OK'),('not_ok','Not Ok!!!'),('not_available','Not Available')],string="Finance KPI",compute="get_finance_kpi")
    ignore_vat =fields.Boolean(string="Ignore VAT")
    ignore_mp_sale =fields.Boolean(string="Ignore Manpower", copy=False)
    owner_kpi = fields.Selection([('ok','OK'),('not_ok','Not Ok!!!'),('not_available','Not Available')],string="Owner KPI",compute="get_owner_kpi")
    sales_kpi = fields.Selection([('ok','OK'),('not_ok','Not Ok!!!'),('not_available','Not Available')],string="Sales KPI",compute="get_sales_kpi")
    presale_kpi = fields.Selection([('ok','OK'),('not_ok','Not Ok!!!'),('not_available','Not Available')],string="Presale KPI",compute="get_presale_kpi")
    name = fields.Char(string='Name',required=True,track_visibility='always')
    project_closing_date = fields.Date(string="Project Closing Date")
    od_hr_claim_amount = fields.Float(string="Hr Exp Claim Amount",compute="od_get_hr_exp_claim_amount",digits=dp.get_precision('Account'))
    saved = fields.Boolean(string='Saved')
    freeze = fields.Boolean(string="Freezed Unit Price")
    mat_copy_cost_sheet_id = fields.Many2one('od.cost.sheet',string="Material Copy Sheet",states={'draft':[('readonly',False)]},readonly=True)
    opt_copy_cost_sheet_id = fields.Many2one('od.cost.sheet',string="Optional Copy Sheet",states={'draft':[('readonly',False)]},readonly=True)
    trn_copy_cost_sheet_id = fields.Many2one('od.cost.sheet',string="Training Copy Sheet",states={'draft':[('readonly',False)]},readonly=True)
    bmn_copy_spareparts_cs_id = fields.Many2one('od.cost.sheet',string="Bmn Spare Parts Copy Sheet",states={'draft':[('readonly',False)]},readonly=True)
    bmn_copy_eqpcoverd_cs_id = fields.Many2one('od.cost.sheet',string="Bmn Eqpment Covered Cost Sheet",states={'draft':[('readonly',False)]},readonly=True)
    omn_copy_spareparts_cs_id = fields.Many2one('od.cost.sheet',string="Omn Spare Parts Copy Sheet",states={'draft':[('readonly',False)]},readonly=True)
    omn_copy_eqpcoverd_cs_id = fields.Many2one('od.cost.sheet',string="Omn Eqpment Covered Cost Sheet",states={'draft':[('readonly',False)]},readonly=True)
    om_copy_eqp_required_cs_id = fields.Many2one('od.cost.sheet',string="OM Eqpment Required Cost Sheet",states={'draft':[('readonly',False)]},readonly=True)
    om_copy_eqpcoverd_cs_id = fields.Many2one('od.cost.sheet',string="OM Eqpment Covered Cost Sheet",states={'draft':[('readonly',False)]},readonly=True)

    od_version = fields.Char(string="Version",states={'draft':[('readonly',False)],'submitted':[('readonly',False)],'commit':[('readonly',False)],'design_ready':[('readonly',False)],'returned_by_pmo':[('readonly',False)]},readonly=True)
    project_manager = fields.Many2one('res.users','Project Manager',states={'submitted':[('readonly',False)],'commit':[('readonly',False)],'design_ready':[('readonly',False)],'returned_by_pmo':[('readonly',False)]},readonly=True,track_visibility='always')
    support_doc_line = fields.One2many('od.support.doc.line','cost_sheet_id',string='Support Doc Lin',copy=True,states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'commit':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'waiting_po_open':[('readonly',False)],'change':[('readonly',False)],'analytic_change':[('readonly',False)]},readonly=True)
    deadlines = fields.One2many('od.deadlines','cost_sheet_id',string='Deadlines',copy=True,default=default_dead_line_data,states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'commit':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'waiting_po_open':[('readonly',False)],'waiting_po':[('readonly',False)],'change':[('readonly',False)],'change_processed':[('readonly',False)],'waiting_po_processed':[('readonly',False)],'processed':[('readonly',False)],'analytic_change':[('readonly',False)],'pmo':[('readonly',False)]},readonly=True)
    payment_schedule_line = fields.One2many('od.payment.schedule','cost_sheet_id',string='Payment Schedule',copy=True,states={'pmo':[('readonly',False)],'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'commit':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'waiting_po_open':[('readonly',False)],'processed':[('readonly',False)],'change_processed':[('readonly',False)],'waiting_po_processed':[('readonly',False)],'waiting_po':[('readonly',False)],'analytic_change':[('readonly',False)],'change':[('readonly',False)]},readonly=True)
    comm_matrix_line = fields.One2many('od.comm.matrix','cost_sheet_id',string='Communication Matrix',copy=True,states={'pmo':[('readonly',False)],'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'commit':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'waiting_po_open':[('readonly',False)],'processed':[('readonly',False)],'change_processed':[('readonly',False)],'waiting_po_processed':[('readonly',False)],'waiting_po':[('readonly',False)],'change':[('readonly',False)],'analytic_change':[('readonly',False)]},readonly=True)
    date_log_history_line = fields.One2many('od.date.log.history','cost_sheet_id',strint="Date Log History",readonly=True,copy=False)
    gp_approval_log_line = fields.One2many('gp.approval.log','cost_sheet_id',strint="GP Approval History",readonly=True,copy=False)
    change_management_line = fields.One2many('change.management','cost_sheet_id',strint="Change Request",readonly=True,copy=False)
    sale_order_original_line = fields.One2many('sale.order','od_cost_sheet_id',strint="Original",readonly=True,copy=False)
    
    bid_bond_submit = fields.Selection([('yes','Yes'),('no','No')],'Bid Bond Submit')
    peromance_bond = fields.Selection([('yes','Yes'),('no','No')],'Perfomance Bond')
    penalty_clause = fields.Selection([('yes','Yes'),('no','No')],'Penalty Clause')
    insurance_req = fields.Selection([('yes','Yes'),('no','No')],'Insurance Required')
    po_status = fields.Selection([('waiting_po','Waiting P.O'),('special_approval','Special Approval From GM'),('available','Available'),('credit','Customer Credit')],'Customer PO Status')
    adv_payment_status = fields.Selection([('not_required','Not Required'),('required','Required,Not Paid'),('paid','Paid'),('gm',' Waived by G.M.')],'Advance Payment Status')

    po_date = fields.Date("Customer PO Date")
    po_date_kpi = fields.Date("PO Date",compute="get_po_date")
    part_ref = fields.Char(string="Customer PO / Contract Number")
    
    bid_bond_rev_comment_id = fields.Many2one('od.reviewer.comment',string="Bid Bond Reviewer Comment")
    perfomance_rev_comment_id = fields.Many2one('od.reviewer.comment',string="Perfomance Bond Reviewer Comment")
    penalty_rev_comment_id = fields.Many2one('od.reviewer.comment',string="Penalty Clause Reviewer Comment")
    insurance_rev_comment_id = fields.Many2one('od.reviewer.comment',string="Insurance Reviewer Comment")
    po_status_rev_comment_id = fields.Many2one('od.reviewer.comment',string="PO Status Reviewer Comment")
    po_date_rev_comment_id = fields.Many2one('od.reviewer.comment',string="PO Date Reviewer Comment")
    adv_payment_rev_comment_id = fields.Many2one('od.reviewer.comment',string="Advance Payment Reviewer Comment")

    bid_bond_fin_comment_id = fields.Many2one('od.finance.comment',string="Bid Bond Finance Comment")
    perfomance_fin_comment_id = fields.Many2one('od.finance.comment',string="Performance Bond Finance Comment")
    penalty_fin_comment_id = fields.Many2one('od.finance.comment',string="Penalty Clause Finance Comment")
    insurance_fin_comment_id = fields.Many2one('od.finance.comment',string="Insurance Finance Comment")
    po_status_fin_comment_id = fields.Many2one('od.finance.comment',string="PO Status Finance Comment")
    po_date_fin_comment_id = fields.Many2one('od.finance.comment',string="PO Date Finance Comment")
    adv_payment_fin_comment_id = fields.Many2one('od.finance.comment',string="Advance Payment Finance Comment")

    project_closing_fin_comment_id = fields.Many2one('od.finance.comment',string="Project Closing Finance Comment")
    customer_reg_id = fields.Many2one('od.customer.reg',string='Customer Registration')
    handover_reviewer = fields.Many2one('res.users','Projects / Service Desk Review')
    finance_reviewer = fields.Many2one('res.users','Finance Review')
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    submitted_date = fields.Datetime('Design Ready Date',readonly=True)
    submit_to_customer_date = fields.Datetime("Submit To Customer Date")
    handover_date = fields.Datetime('Hand-Over Date',readonly=True)
    processed_date = fields.Datetime('Processed Date',readonly=True)
    pmo_date = fields.Datetime('PMO Director Date')
    approved_date = fields.Datetime('Approved Date',readonly=False)
    #hand over tab
    sales_acc_manager = fields.Many2one('res.users',string='Customer AM')
    lead_acc_manager = fields.Many2one('res.users',string='Lead AM')
    business_development = fields.Many2one('res.users',string='Business Development')
    pre_sales_engineer = fields.Many2one('res.users',string='Pre-Sales Engineer',related="lead_id.od_responsible_id",store=True,readonly=True)
    technical_consultant1 = fields.Many2one('res.users',string='Technical Consultant 1')
    technical_consultant2 = fields.Many2one('res.users',string='Technical Consultant 2')
    accountant = fields.Many2one('res.users',string='Accountant')
    sales_order_generated = fields.Boolean(string="Sales Order Generated",default=False,copy=False)
    lock_fin_struct = fields.Boolean(string="Lock Finance Structure",default=False,copy=False)
    return_reason =fields.Text(string="Return Reason?")
    
    cust_req1=fields.Text(string="Customer Requirement")
    cust_req2=fields.Text(string="Customer Requirement")
    cust_req3=fields.Text(string="Customer Requirement")
    cust_req4=fields.Text(string="Customer Requirement")
    cust_req5=fields.Text(string="Customer Requirement")
    show_po_clause = fields.Boolean(string="Show To Customer",default=True)
    po_clause=fields.Text(string="Non-cancellable Clause", default="Once purchase order is placed by the customer, the PO will be a non-cancellable and non-revokable purchase order.")
    
    od_resol_time_ctc = fields.Float(string="Critical", default=6.0,digits=(16,2))
    od_resol_time_maj = fields.Float(string="Major", default=8.0,digits=(16,2))
    od_resol_time_min = fields.Float(string="Minor",default=24.0,digits=(16,2))
    od_respons_time_ctc = fields.Float(string="Response Critical", default=0.5,digits=(16,2))
    od_respons_time_maj = fields.Float(string="Response Major", default=4.0,digits=(16,2))
    od_respons_time_min = fields.Float(string="Response Minor",default=24.0,digits=(16,2))
    od_resol_time_ctc_rel = fields.Float(digits=(16,2), compute="od_get_sla_metrics_vals")
    od_resol_time_maj_rel = fields.Float(digits=(16,2),compute="od_get_sla_metrics_vals")
    od_resol_time_min_rel = fields.Float(digits=(16,2),compute="od_get_sla_metrics_vals")
    od_respons_time_ctc_rel = fields.Float(digits=(16,2), compute="od_get_sla_metrics_vals")
    od_respons_time_maj_rel = fields.Float(digits=(16,2),compute="od_get_sla_metrics_vals")
    od_respons_time_min_rel = fields.Float(digits=(16,2),compute="od_get_sla_metrics_vals")
    time_ctc_rev_comment_id = fields.Many2one('od.reviewer.comment',string="Critical Reviewer Comment")
    time_ctc_fin_comment_id = fields.Many2one('od.finance.comment',string="Critical maintenance Finance Comment")
    time_maj_rev_comment_id = fields.Many2one('od.reviewer.comment',string="Major Reviewer Comment")
    time_maj_fin_comment_id = fields.Many2one('od.finance.comment',string="Major Finance Comment")
    time_min_rev_comment_id = fields.Many2one('od.reviewer.comment',string="Minor Reviewer Comment")
    time_min_fin_comment_id = fields.Many2one('od.finance.comment',string="Minor Finance Comment")

               
    comp1=fields.Selection([('comply','Comply'),('not_comply','Do Not Comply'),('part_comply','Partially Comply')],string="Compliance")
    comp2=fields.Selection([('comply','Comply'),('not_comply','Do Not Comply'),('part_comply','Partially Comply')],string="Compliance")
    comp3=fields.Selection([('comply','Comply'),('not_comply','Do Not Comply'),('part_comply','Partially Comply')],string="Compliance")
    comp4=fields.Selection([('comply','Comply'),('not_comply','Do Not Comply'),('part_comply','Partially Comply')],string="Compliance")
    comp5=fields.Selection([('comply','Comply'),('not_comply','Do Not Comply'),('part_comply','Partially Comply')],string="Compliance")
             
    presale_note1 = fields.Text(string="Pre-Sale Note")
    presale_note2 = fields.Text(string="Pre-Sale Note")
    presale_note3 = fields.Text(string="Pre-Sale Note")
    presale_note4 = fields.Text(string="Pre-Sale Note")
    presale_note5 = fields.Text(string="Pre-Sale Note")
    
    mat_del_date = fields.Date(string="Material Delivery Date")
    mat_rev_comment_id = fields.Many2one('od.reviewer.comment',string="Reviewer Comment")      
    mat_fin_comment_id = fields.Many2one('od.finance.comment',string="Finance Comment") 
    mat_intvl_unit = fields.Selection([('days','Days'),('weeks','Weeks'),('months','Months'),('years','Years')],string="Interval Unit")
    mat_intvl = fields.Integer(string="Interval Numbers")
    
    pjct_close_rev_comment_id = fields.Many2one('od.reviewer.comment',string="Reviewer Comment")      
   
    pjct_close_intvl_unit = fields.Selection([('days','Days'),('weeks','Weeks'),('months','Months'),('years','Years')],string="Interval Unit")
    pjct_close_intvl = fields.Integer(string="Interval Numbers")
    
    ig_exception = fields.Boolean(string="Ignore Exception", copy=False)
    
    need_approval_1 = fields.Boolean(string="First Approval Needed", copy=False)
    need_approval_2 = fields.Boolean(string="Second Approval Needed", copy=False)
    need_approval_3 = fields.Boolean(string="Third Approval Needed", copy=False)
    need_approval_4 = fields.Boolean(string="Fourth Approval Needed", copy=False)
    done_approval_1 = fields.Boolean(string="First Approval Done")
    done_approval_2 = fields.Boolean(string="Second Approval Done")
    done_approval_3 = fields.Boolean(string="Third Approval Done")
    done_approval_4 = fields.Boolean(string="Fourth Approval Done")
    gp_approval_state = fields.Selection([('no_apprv','No Approval Needed'), ('first_apprv','First Approval'), ('second_apprv','Second Approval'), ('third_apprv','Third Approval'), ('final_apprv','Final Approval'),('approved','GP Approved')], default='no_apprv',string="GP Approval State")
    approved_gp = fields.Float(string="Approved Gp %",store=True,digits=dp.get_precision('Account'))
    exclude_frm_gp_apprv = fields.Boolean(string="Exclude From GP Approval")
    
    attach_file_po = fields.Binary('Attach Customer PO')
    attach_fname_po = fields.Char('Attach PO name')
    attach_file_fp = fields.Binary('Attach Latest Financial Proposal')
    attach_fname_fp = fields.Char('Attach PO name')
    attach_file_hlld = fields.Binary('Attach PO')
    attach_fname_hlld = fields.Char('Attach High Level Design Document')
    attach_file_tp = fields.Binary('Attach Technical Proposal')
    attach_fname_tp = fields.Char('Attach PO name')
    cust_tp_submit = fields.Selection([('yes','Yes'),('no','No')],'Answer')
    supplier_quotes_ids = fields.One2many('od.supplier.quotes','cost_sheet_id',string='Supplier Quotations',states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'commit':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'waiting_po_open':[('readonly',False)],'waiting_po':[('readonly',False)],'change':[('readonly',False)],'change_processed':[('readonly',False)],'waiting_po_processed':[('readonly',False)],'processed':[('readonly',False)],'analytic_change':[('readonly',False)],'pmo':[('readonly',False)]},readonly=True)

    
    @api.one
    @api.depends('od_customer_id')
    def _compute_cust_class(self):
        self.od_cust_class = self.od_customer_id and self.od_customer_id.od_class or False
    od_cust_class = fields.Selection([('a', 'A'), ('b', 'B'), ('c', 'C'), ('r', 'R')],string="Class",compute='_compute_cust_class')
    
    @api.onchange('part_ref')
    def onchange_part_ref(self):
        part_ref = self.part_ref
        costsheet_id = self.env.context.get('active_id',False)
        if part_ref and costsheet_id:
            invoices = self.env['account.invoice'].search([('od_cost_sheet_id','=',costsheet_id),('type', 'in', ('out_invoice','out_refund'))])
            for inv in invoices:
                inv.write({'name':part_ref})
    
    #Added by aslam: Auto Level 0 analytic name generation            
#     @api.onchange('date_end_a0')
#     def onchange_date_end_a0(self):
#         if not self.name_a0:
#             number = self.number or ''
#             name = self.name or ''
#             self.name_a0 = 'A0'+ ' ' + number + '; ' + name
    
    @api.onchange('approved_date')
    def onchange_approved(self):
        approved_date = self.approved_date
        if approved_date:
            expected_booking= approved_date[:10]
            self.lead_id.write({'date_action':expected_booking})

    @api.onchange('po_status')
    def onchange_po_status(self):
        if self.state in ['pmo', 'done']:
            if self.company_id.id == 6:
                if self.po_status:
                    if self.po_status == 'available':
                        if not self.env.user.has_group('__export__.res_groups_229'):
                            raise Warning("You don't have the access to change the PO status to 'Available'. Kindly please contact finance team")
    
    @api.one
    def check_payment_term(self):
        if not self.payment_terms_line:
            raise Warning("Enter Payment Terms")
        
    def get_applied_vat_perc(self):
        vat = .05
        if self.costgroup_material_line:
            for costgroup in self.costgroup_material_line[0]:
                vat = costgroup.tax_id and costgroup.tax_id.amount or 0.0
        if not self.costgroup_material_line:
            if self.costgroup_it_service_line:
                for costgroup in self.costgroup_it_service_line[0]:
                    vat = costgroup.tax_id and costgroup.tax_id.amount or 0.0
        return vat

    @api.one 
    def double_check_vat(self):
            #vat = .05
        vat_perc = self.get_applied_vat_perc()
        check_vat_amount =self.sum_total_sale * vat_perc 
        vat_amount = self.sum_vat
        if not self.ignore_vat and abs(vat_amount -check_vat_amount) >1:
            raise Warning("Please Double Check the VAT Amount")
    
    def print_cost_sheet(self, cr, uid, ids, context=None):
        self.update_cost_sheet(cr,uid,ids,context=context)
        self.double_check_vat(cr,uid,ids,context=context)
#         self.check_payment_term(cr,uid,ids,context=context)
        return self.pool['report'].get_action(cr, uid, ids, 'report.Beta_IT_Proposal', context=context)
    
    def print_new_cost_sheet(self, cr, uid, ids, context=None):
        self.update_cost_sheet(cr,uid,ids,context=context)
        self.double_check_vat(cr,uid,ids,context=context)
#         self.check_payment_term(cr,uid,ids,context=context)
        return self.pool['report'].get_action(cr, uid, ids, 'report.Beta_IT_Commercial_Proposal', context=context)


    def get_saudi_company_id(self):
        parameter_obj = self.env['ir.config_parameter']
        key =[('key', '=', 'od_beta_saudi_co')]
        company_param = parameter_obj.search(key)
        if not company_param:
            raise Warning(_('Settings Warning!'),_('No Company Parameter Not defined\nconfig it in System Parameters with od_beta_saudi_co!'))
        saudi_company_id = company_param.od_model_id and company_param.od_model_id.id or False
        return saudi_company_id

    def check_reviewer_comment(self,line_ids,detail):
        for line in line_ids:
            if line.rev_comment_id.id == False:
                raise Warning('Reviewer Comment Blank In Handover %s Record' %detail)

    def check_payment_schedule(self):
        for line in self.payment_schedule_line:
            if not line.milestone:
                raise Warning('Link To Milestone Missing in Handover Payment Schedule Record')
    def check_rev_exist(self):
        # self.check_reviewer_comment(self.support_doc_line, 'Supporting Documents')
        self.check_reviewer_comment(self.deadlines, 'Deadlines')
        self.check_reviewer_comment(self.comm_matrix_line, 'Communication Matrix Line')
        self.check_payment_schedule()
    def check_proof_cost(self):
        for line in self.costgroup_material_line:
            if not line.proof_of_cost:
                return True
        for line in self.costgroup_optional_line:
            if not line.proof_of_cost:
                return True
        for line in self.costgroup_it_service_line:
            if not line.proof_of_cost:
                return True
        return False

    def check_handover_min_docs(self):
        # if len(self.support_doc_line) < 1:
        #     raise Warning('At least One  Supporting Doc Line Required')
        if not self.po_status:
            raise Warning('Please Update the Customer PO Status & Upload the required Documents')
        if self.po_status=='available' and self.po_date >= '01-Mar-2024' and not self.attach_file_po:
            raise Warning('Please Upload Customer PO in Handover Supporting Documents Section')
        if self.po_date >= '01-Mar-2024' and not self.attach_file_fp:
            raise Warning('Please Upload Latest Version of Financial Proposal Submitted to Customer in Handover Supporting Documents Section')
        if not self.cust_tp_submit:
            raise Warning('Please Update the Technical Proposal Status')
        if self.included_in_quotation and len(self.supplier_quotes_ids) < 1:
            raise Warning('At least One Supplier Quotation Needed.')
        if not (self.mat_intvl or self.mat_intvl_unit):
            raise Warning("Please Update Material Delivery Deadline")
        if not (self.pjct_close_intvl or self.pjct_close_intvl_unit):
            raise Warning("Please Update Project Closing Deadline")
        if len(self.deadlines) <1 :
            raise Warning('At least One  Deadlines Record Required')
        if len(self.payment_schedule_line) <1 :
            raise Warning('At least One  Payment Schedule Line is Required')
        if len(self.comm_matrix_line) <1 :
            raise Warning('At least One  Communication Matrix Line is Required')
        for line in self.comm_matrix_line:
            if line.partner_id.id == False :
                raise Warning('At least One Customer Required in Matrix line')
            if line.customer_role_id.id == False:
                raise Warning('At least One Customer Role  Required in Matrix line')
        if not self.bid_bond_submit:
            raise Warning('All General Questionnaire Should Be Answered')
        if not self.peromance_bond:
            raise Warning('All General Questionnaire Should Be Answered')
        if not self.customer_reg_id:
            raise Warning('All General Questionnaire Should Be Answered')
        if not self.penalty_clause:
            raise Warning('All General Questionnaire Should Be Answered')
        if not self.comm_made_to_customer:
            raise Warning("Commitment Made to Customer is Blank")
        


    def check_process_min_docs(self):
        # if len(self.customer_closing_line) < 1:
        #     raise Warning('At least One  Customer Closing Line Record Required')
        # if len(self.beta_closing_line) <1:
        #     raise Warning('At least One  Beta Closing Condition Record Required')
        if not self.mat_rev_comment_id:
            raise Warning("Deadline Material Delivery Comment Needed")
        if not self.pjct_close_rev_comment_id:
            raise Warning("Deadline Project Closing Reviewer Comment Needed")
        if not self.mat_del_date:
            raise Warning("Material Delivery PMO Date Needed")
        if not self.project_closing_date:
            raise Warning("Project Closing Date Not Set")
        if not self.bid_bond_rev_comment_id:
            raise Warning("Bid Bond Reviewer Comment is not Set")
        if not self.perfomance_rev_comment_id:
            raise Warning("Perfomance Bond Reviewer Comment not Set")
        if not self.insurance_rev_comment_id:
            raise Warning("Penalty Close Reviewer Comment not Set")
        if not self.penalty_rev_comment_id:
            raise Warning("insurance Reviewer Comment Not set")
#         if not self.po_status_rev_comment_id:
#             raise Warning("Customer PO Status Reviewer Comment Not Set")
        if not self.closing_condition_ids:
            raise Warning("Update Closing Condition")
        amc = self.included_bmn_in_quotation
        if amc and not self.time_ctc_rev_comment_id:
            raise Warning("SLA Resolution Time Reviewer Comment Not set")
        if amc and not self.time_maj_rev_comment_id:
            raise Warning("SLA Resolution Time Reviewer Comment Not set")
        if amc and not self.time_min_rev_comment_id:
            raise Warning("SLA Resolution Time Reviewer Comment Not set")
    def common_check_fin(self,line_id,label):
        for line in line_id:
            if not line.fin_comment_id.id:
                raise Warning("%s Finance Comment Is Blank"%label)

    def check_finance_comment(self):
        # self.common_check_fin(self.support_doc_line,"Supporting Documents")
        self.common_check_fin(self.deadlines,"Deadlines Documents")
        self.common_check_fin(self.payment_schedule_line,"Payment Schedule Documents")
        self.common_check_fin(self.comm_matrix_line,"Communication Matrix Documents")
        # self.common_check_fin(self.customer_closing_line,"Customer Closing Line Documents")
        # self.common_check_fin(self.beta_closing_line,"Beta IT Closing Condition Line Documents")
        if not self.mat_fin_comment_id:
            raise Warning("Deadline Material Delivery Date Finance Comment Needed")
        if not self.project_closing_fin_comment_id:
            raise Warning("Deadline Project Closing Finance Comment Needed")
        if not self.closing_fin_comment_id:
            raise Warning("Finance Comment Needed in Closing Condition")
        if not self.project_closing_fin_comment_id:
            raise Warning("Finance Comment Needed in Project Closing Date")
        if not self.bid_bond_fin_comment_id:
            raise Warning("Bid Bond Finance Comment is not Set")
        if not self.perfomance_fin_comment_id:
            raise Warning("Perfomance Bond Finance Comment not Set")
        if not self.insurance_fin_comment_id:
            raise Warning("Penalty Close Finance Comment not Set")
        if not self.penalty_fin_comment_id:
            raise Warning("insurance Finance Comment Not set")
#         if not self.po_status_fin_comment_id:
#             raise Warning("Customer PO Status Finance Comment Not set")
        amc = self.included_bmn_in_quotation
        if amc and not self.time_ctc_fin_comment_id:
            raise Warning("SLA Resolution Time Finance Comment Not set")
        if amc and not self.time_maj_fin_comment_id:
            raise Warning("SLA Resolution Time Finance Comment Not set")
        if amc and not self.time_min_fin_comment_id:
            raise Warning("SLA Resolution Time Finance Comment Not set")

    def od_send_mail(self,template):
        ir_model_data = self.env['ir.model.data']
        email_obj = self.pool.get('email.template')
        saudi_comp =self.get_saudi_company_id()
        if self.company_id.id == saudi_comp:
            template = template +'_saudi'
        template_id = ir_model_data.get_object_reference('orchid_cost_sheet', template)[1]
        cost_sheet_id = self.id
        email_obj.send_mail(self.env.cr,self.env.uid,template_id,cost_sheet_id, force_send=True)
        return True
    

    

    def od_open_attachement(self,cr,uid,ids,context=None):

        model_name=self._name
        object_id = ids[0]
        domain = [('model_name','=',model_name),('object_id','=',object_id)]
        ctx = {'default_model_name':model_name,'default_object_id':object_id,'default_costsheet_doc':True}
        return {
            'domain': domain,
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'od.attachement',
            'type': 'ir.actions.act_window',
            'context':ctx
                }
    @api.one
    def _od_attachement_count(self):
        for obj in self:
            attachement_ids = self.env['od.attachement'].search([('model_name', '=', self._name),('object_id','=',obj.id)])
            if attachement_ids:
                self.od_attachement_count = len(attachement_ids)


    @api.one 
    @api.onchange('bim_log_group')
    def onchngage_bim_log_group(self):
        self.bim_tax_id = self.bim_log_group and self.bim_log_group.tax_id and self.bim_log_group.tax_id.id or False
    
    @api.one
    @api.depends('bim_log_cost','bim_log_group')
    def compute_bim_log_price(self):
        if self.bim_log_group:
            group = self.bim_log_group
            profit = group.profit /100
            if profit >=1:
                raise Warning("Profit value for the costgroup %s set 100 or above,it should be below 100"%group.name)
            discount = group.customer_discount/100
            unit_cost = self.bim_log_cost
#             unit_price = (unit_cost / (1-profit)) - (unit_cost * discount)
            unit_price = (unit_cost / (1-profit))
            unit_price = unit_price * (1-discount)
            self.bim_log_price = round(unit_price)
        if self.price_fixed:
            self.bim_log_price = round(self.bim_log_price_fixed)


    def set_trn_cost_group(self,res):
        costgroup_material_pool = self.env['od.cost.costgroup.material.line']
        for data in res:
            sheet_id = data.id
            for line in data.trn_customer_training_line:
                group_name = line.group and line.group.name or ''
                cst_grops = costgroup_material_pool.search([('cost_sheet_id','=',sheet_id),('name','=',group_name)])
                if len(cst_grops)  == 1:
                    line['group'] = cst_grops.id
                else:
                    line['group'] = False
    def set_trn_section(self,res):
        section_pool = self.env['od.cost.trn.section.line']
        for data in res:
            sheet_id = data.id
            for line in data.trn_customer_training_line:
                section_name = line.trn_section_id and line.trn_section_id.section or ''
                sections = section_pool.search([('cost_sheet_id','=',sheet_id),('section','=',section_name)])
                if len(sections)  == 1:
                    line['trn_section_id'] = sections.id
                else:
                    line['trn_section_id'] = False
    def set_trn_extra_cost_group(self,res):
        costgroup_opt_pool = self.env['od.cost.costgroup.extra.expense.line']
        for data in res:
            sheet_id = data.id
            for line in data.trn_customer_training_extra_expense_line:
                group_name = line.group2 and line.group2.name or ''
                cst_grops = costgroup_opt_pool.search([('cost_sheet_id','=',sheet_id),('name','=',group_name)])
                if len(cst_grops)  == 1:
                    line['group2'] = cst_grops.id
                else:
                    line['group2'] = False

    def set_mat_cost_group(self,res):
        costgroup_material_pool = self.env['od.cost.costgroup.material.line']
        for data in res:
            sheet_id = data.id
            for line in data.mat_main_pro_line:
                group_name = line.group and line.group.name or ''
                cst_grops = costgroup_material_pool.search([('cost_sheet_id','=',sheet_id),('name','=',group_name)])
                if len(cst_grops)  == 1:
                    line['group'] = cst_grops.id
                else:
                    line['group'] = False
    
    def set_imp_tech_group(self,res):
        costgroup_material_pool = self.env['od.cost.costgroup.it.service.line']
        for data in res:
            sheet_id = data.id
            for line in data.imp_tech_line:
                group_name = line.group and line.group.name or ''
                cst_grops = costgroup_material_pool.search([('cost_sheet_id','=',sheet_id),('name','=',group_name)])
                if len(cst_grops)  == 1:
                    line['group'] = cst_grops.id
                else:
                    line['group'] = False
    
    
    def set_amc_tech_group(self,res):
        costgroup_material_pool = self.env['od.cost.costgroup.it.service.line']
        for data in res:
            sheet_id = data.id
            for line in data.amc_tech_line:
                group_name = line.group and line.group.name or ''
                cst_grops = costgroup_material_pool.search([('cost_sheet_id','=',sheet_id),('name','=',group_name)])
                if len(cst_grops)  == 1:
                    line['group'] = cst_grops.id
                else:
                    line['group'] = False
    
    
    def set_mat_section(self,res):
        section_pool = self.env['od.cost.section.line']
        for data in res:
            sheet_id = data.id
            for line in data.mat_main_pro_line:
                section_name = line.section_id and line.section_id.section or ''
                sections = section_pool.search([('cost_sheet_id','=',sheet_id),('section','=',section_name)])
                if len(sections)  == 1:
                    line['section_id'] = sections.id
                else:
                    line['section_id'] = False

    def set_opt_cost_group(self,res):
        costgroup_opt_pool = self.env['od.cost.costgroup.optional.line.two']
        for data in res:
            sheet_id = data.id
            for line in data.mat_optional_item_line:
                group_name = line.group_id and line.group_id.name or ''
                cst_grops = costgroup_opt_pool.search([('cost_sheet_id','=',sheet_id),('name','=',group_name)])
                if len(cst_grops)  == 1:
                    line['group_id'] = cst_grops.id
                else:
                    line['group_id'] = False

    def set_opt_section(self,res):
        section_pool = self.env['od.cost.opt.section.line']
        for data in res:
            sheet_id = data.id
            for line in data.mat_optional_item_line:
                section_name = line.opt_section_id and line.opt_section_id.section or ''
                sections = section_pool.search([('cost_sheet_id','=',sheet_id),('section','=',section_name)])
                if len(sections)  == 1:
                    line['opt_section_id'] = sections.id
                else:
                    line['opt_section_id'] = False
    def set_mat_extra_cost_group(self,res):
        costgroup_opt_pool = self.env['od.cost.costgroup.extra.expense.line']
        for data in res:
            sheet_id = data.id
            for line in data.mat_extra_expense_line:
                group_name = line.group2 and line.group2.name or ''
                cst_grops = costgroup_opt_pool.search([('cost_sheet_id','=',sheet_id),('name','=',group_name)])
                if len(cst_grops)  == 1:
                    line['group2'] = cst_grops.id
                else:
                    line['group2'] = False

    def set_imp_extra_cost_group(self,res):
        costgroup_opt_pool = self.env['od.cost.costgroup.it.service.line']
        for data in res:
            sheet_id = data.id
            for line in data.implimentation_extra_expense_line:
                group_name = line.group and line.group.name or ''
                cst_grops = costgroup_opt_pool.search([('cost_sheet_id','=',sheet_id),('name','=',group_name)])
                if len(cst_grops)  == 1:
                    line['group'] = cst_grops.id
                else:
                    line['group'] = False

    def set_imp_manpower_cost_group(self,res):
        costgroup_opt_pool = self.env['od.cost.costgroup.it.service.line']
        for data in res:
            sheet_id = data.id
            for line in data.manpower_manual_line:
                group_name = line.cost_group_id and line.cost_group_id.name or ''
                cst_grops = costgroup_opt_pool.search([('cost_sheet_id','=',sheet_id),('name','=',group_name)])
                if len(cst_grops)  == 1:
                    line['cost_group_id'] = cst_grops.id
                else:
                    line['cost_group_id'] = False

    def set_imp_man_imp_code_cost_group(self,res):
        costgroup_opt_pool = self.env['od.cost.costgroup.it.service.line']
        for data in res:
            sheet_id = data.id
            for line in data.bim_implementation_code_line:
                group_name = line.group and line.group.name or ''
                cst_grops = costgroup_opt_pool.search([('cost_sheet_id','=',sheet_id),('name','=',group_name)])
                if len(cst_grops)  == 1:
                    line['group'] = cst_grops.id
                else:
                    line['group'] = False
    def set_oim_price_calculation_cost_group(self,res):
        costgroup_opt_pool = self.env['od.cost.costgroup.it.service.line']
        for data in res:
            sheet_id = data.id
            for line in data.oim_implimentation_price_line:
                group_name = line.group and line.group.name or ''
                cst_grops = costgroup_opt_pool.search([('cost_sheet_id','=',sheet_id),('name','=',group_name)])
                if len(cst_grops)  == 1:
                    line['group'] = cst_grops.id
                else:
                    line['group'] = False
    def set_oim_extra_exp_cost_group(self,res):
        costgroup_opt_pool = self.env['od.cost.costgroup.it.service.line']
        for data in res:
            sheet_id = data.id
            for line in data.oim_extra_expenses_line:
                group_name = line.group and line.group.name or ''
                cst_grops = costgroup_opt_pool.search([('cost_sheet_id','=',sheet_id),('name','=',group_name)])
                if len(cst_grops)  == 1:
                    line['group'] = cst_grops.id
                else:
                    line['group'] = False
    def set_ps_vendor_line_cost_group(self,res):
        costgroup_opt_pool = self.env['od.cost.costgroup.it.service.line']
        for data in res:
            sheet_id = data.id
            for line in data.ps_vendor_line:
                group_name = line.group and line.group.name or ''
                cst_grops = costgroup_opt_pool.search([('cost_sheet_id','=',sheet_id),('name','=',group_name)])
                if len(cst_grops)  == 1:
                    line['group'] = cst_grops.id
                else:
                    line['group'] = False
    def set_bim_log_group(self,res):
        costgroup_pool = self.env['od.cost.costgroup.it.service.line']
        for data in res:
            sheet_id = data.id
            group_name = data.bim_log_group and data.bim_log_group.name or ''
            cst_grops = costgroup_pool.search([('cost_sheet_id','=',sheet_id),('name','=',group_name)])
            if len(cst_grops)  == 1:
                data.bim_log_group = cst_grops.id
            else:
                data.bim_log_group = False
                
    def set_info_sec_tech_line_cost_group(self,res):
        costgroup_opt_pool = self.env['od.cost.costgroup.it.service.line']
        for data in res:
            sheet_id = data.id
            for line in data.info_sec_tech_line:
                group_name = line.group and line.group.name or ''
                cst_grops = costgroup_opt_pool.search([('cost_sheet_id','=',sheet_id),('name','=',group_name)])
                if len(cst_grops)  == 1:
                    line['group'] = cst_grops.id
                else:
                    line['group'] = False
    def set_info_sec_extra_expense_line_cost_group(self,res):
        costgroup_opt_pool = self.env['od.cost.costgroup.it.service.line']
        for data in res:
            sheet_id = data.id
            for line in data.info_sec_extra_expense_line:
                group_name = line.group and line.group.name or ''
                cst_grops = costgroup_opt_pool.search([('cost_sheet_id','=',sheet_id),('name','=',group_name)])
                if len(cst_grops)  == 1:
                    line['group'] = cst_grops.id
                else:
                    line['group'] = False
    def set_info_sec_subcontractor_line_cost_group(self,res):
        costgroup_opt_pool = self.env['od.cost.costgroup.it.service.line']
        for data in res:
            sheet_id = data.id
            for line in data.info_sec_subcontractor_line:
                group_name = line.group and line.group.name or ''
                cst_grops = costgroup_opt_pool.search([('cost_sheet_id','=',sheet_id),('name','=',group_name)])
                if len(cst_grops)  == 1:
                    line['group'] = cst_grops.id
                else:
                    line['group'] = False
    def set_info_sec_vendor_line_cost_group(self,res):
        costgroup_opt_pool = self.env['od.cost.costgroup.it.service.line']
        for data in res:
            sheet_id = data.id
            for line in data.info_sec_vendor_line:
                group_name = line.group and line.group.name or ''
                cst_grops = costgroup_opt_pool.search([('cost_sheet_id','=',sheet_id),('name','=',group_name)])
                if len(cst_grops)  == 1:
                    line['group'] = cst_grops.id
                else:
                    line['group'] = False
        
    def set_amc_preventive_mnt_cost_group(self,res):
        costgroup_opt_pool = self.env['od.cost.costgroup.it.service.line']
        for data in res:
            sheet_id = data.id
            for line in data.bmn_it_preventive_line:
                group_name = line.group and line.group.name or ''
                cst_grops = costgroup_opt_pool.search([('cost_sheet_id','=',sheet_id),('name','=',group_name)])
                if len(cst_grops)  == 1:
                    line['group'] = cst_grops.id
                else:
                    line['group'] = False

    def set_amc_remedial_mnt_cost_group(self,res):
        costgroup_opt_pool = self.env['od.cost.costgroup.it.service.line']
        for data in res:
            sheet_id = data.id
            for line in data.bmn_it_remedial_line:
                group_name = line.group and line.group.name or ''
                cst_grops = costgroup_opt_pool.search([('cost_sheet_id','=',sheet_id),('name','=',group_name)])
                if len(cst_grops)  == 1:
                    line['group'] = cst_grops.id
                else:
                    line['group'] = False
    def set_amc_spareparts_cost_group(self,res):
        costgroup_material_pool = self.env['od.cost.costgroup.material.line']
        for data in res:
            sheet_id = data.id
            for line in data.bmn_spareparts_beta_it_maintenance_line:
                group_name = line.group and line.group.name or ''
                cst_grops = costgroup_material_pool.search([('cost_sheet_id','=',sheet_id),('name','=',group_name)])
                if len(cst_grops)  == 1:
                    line['group'] = cst_grops.id
                else:
                    line['group'] = False
    def set_amc_spareparts_section(self,res):
        section_pool = self.env['od.cost.section.line']
        for data in res:
            sheet_id = data.id
            for line in data.bmn_spareparts_beta_it_maintenance_line:
                section_name = line.section_id and line.section_id.section or ''
                sections = section_pool.search([('cost_sheet_id','=',sheet_id),('section','=',section_name)])
                if len(sections)  == 1:
                    line['section_id'] = sections.id
                else:
                    line['section_id'] = False
    def set_amc_bmn_extra_exp_cost_group(self,res):
        costgroup_opt_pool = self.env['od.cost.costgroup.it.service.line']
        for data in res:
            sheet_id = data.id
            for line in data.bmn_beta_it_maintenance_extra_expense_line:
                group_name = line.group and line.group.name or ''
                cst_grops = costgroup_opt_pool.search([('cost_sheet_id','=',sheet_id),('name','=',group_name)])
                if len(cst_grops)  == 1:
                    line['group'] = cst_grops.id
                else:
                    line['group'] = False
    def set_amc_omn_preventive_cost_group(self,res):
        costgroup_opt_pool = self.env['od.cost.costgroup.it.service.line']
        for data in res:
            sheet_id = data.id
            for line in data.omn_out_preventive_maintenance_line:
                group_name = line.group and line.group.name or ''
                cst_grops = costgroup_opt_pool.search([('cost_sheet_id','=',sheet_id),('name','=',group_name)])
                if len(cst_grops)  == 1:
                    line['group'] = cst_grops.id
                else:
                    line['group'] = False
    def set_amc_omn_remedial_cost_group(self,res):
        costgroup_opt_pool = self.env['od.cost.costgroup.it.service.line']
        for data in res:
            sheet_id = data.id
            for line in data.omn_out_remedial_maintenance_line:
                group_name = line.group and line.group.name or ''
                cst_grops = costgroup_opt_pool.search([('cost_sheet_id','=',sheet_id),('name','=',group_name)])
                if len(cst_grops)  == 1:
                    line['group'] = cst_grops.id
                else:
                    line['group'] = False
    def set_amc_omn_spareparts_section(self,res):
        section_pool = self.env['od.cost.section.line']
        for data in res:
            sheet_id = data.id
            for line in data.omn_spare_parts_line:
                section_name = line.section_id and line.section_id.section or ''
                sections = section_pool.search([('cost_sheet_id','=',sheet_id),('section','=',section_name)])
                if len(sections)  == 1:
                    line['section_id'] = sections.id
                else:
                    line['section_id'] = False
    def set_amc_omn_spareparts_cost_group(self,res):
        costgroup_material_pool = self.env['od.cost.costgroup.material.line']
        for data in res:
            sheet_id = data.id
            for line in data.omn_spare_parts_line:
                group_name = line.group and line.group.name or ''
                cst_grops = costgroup_material_pool.search([('cost_sheet_id','=',sheet_id),('name','=',group_name)])
                if len(cst_grops)  == 1:
                    line['group'] = cst_grops.id
                else:
                    line['group'] = False
    def set_amc_omn_extra_exp_cost_group(self,res):
        costgroup_opt_pool = self.env['od.cost.costgroup.it.service.line']
        for data in res:
            sheet_id = data.id
            for line in data.omn_maintenance_extra_expense_line:
                group_name = line.group and line.group.name or ''
                cst_grops = costgroup_opt_pool.search([('cost_sheet_id','=',sheet_id),('name','=',group_name)])
                if len(cst_grops)  == 1:
                    line['group'] = cst_grops.id
                else:
                    line['group'] = False
    def set_om_resident_eng_cost_group(self,res):
        costgroup_opt_pool = self.env['od.cost.costgroup.it.service.line']
        for data in res:
            sheet_id = data.id
            for line in data.om_residenteng_line:
                group_name = line.group and line.group.name or ''
                cst_grops = costgroup_opt_pool.search([('cost_sheet_id','=',sheet_id),('name','=',group_name)])
                if len(cst_grops)  == 1:
                    line['group'] = cst_grops.id
                else:
                    line['group'] = False
    def set_om_material_section(self,res):
        section_pool = self.env['od.cost.section.line']
        for data in res:
            sheet_id = data.id
            for line in data.om_eqpmentreq_line:
                section_name = line.section_id and line.section_id.section or ''
                sections = section_pool.search([('cost_sheet_id','=',sheet_id),('section','=',section_name)])
                if len(sections)  == 1:
                    line['section_id'] = sections.id
                else:
                    line['section_id'] = False
    def set_om_material_cost_group(self,res):
        costgroup_material_pool = self.env['od.cost.costgroup.material.line']
        for data in res:
            sheet_id = data.id
            for line in data.om_eqpmentreq_line:
                group_name = line.group and line.group.name or ''
                cst_grops = costgroup_material_pool.search([('cost_sheet_id','=',sheet_id),('name','=',group_name)])
                if len(cst_grops)  == 1:
                    line['group'] = cst_grops.id
                else:
                    line['group'] = False
    def set_om_extra_exp_cost_group(self,res):
        costgroup_opt_pool = self.env['od.cost.costgroup.it.service.line']
        for data in res:
            sheet_id = data.id
            for line in data.om_extra_line:
                group_name = line.group and line.group.name or ''
                cst_grops = costgroup_opt_pool.search([('cost_sheet_id','=',sheet_id),('name','=',group_name)])
                if len(cst_grops)  == 1:
                    line['group'] = cst_grops.id
                else:
                    line['group'] = False


    @api.one
    def copy(self,defaults):
        context = self._context
        lead_id = self.lead_id.id
        pre_sales_engineer = self.pre_sales_engineer and self.pre_sales_engineer.id or False
        costsheets = self.search([('lead_id','=',lead_id)])
        lead_obj = self.env['crm.lead'].browse(lead_id)
        lead_number = lead_obj.od_number
        cst_sheet_count = len(costsheets) + 1
        #defaults['pre_sales_engineer'] = pre_sales_engineer
        if not defaults:
            defaults['name'] = self.name + '[copy]'
            defaults['status'] = 'revision'
        defaults['number'] = lead_number + '-' + str(cst_sheet_count)
        defaults['sales_order_generated'] = False
        defaults['bim_log_select'] = True
        res = super(od_cost_sheet,self).copy(defaults)
        self.set_mat_cost_group(res)
        self.set_opt_cost_group(res)
        self.set_mat_extra_cost_group(res)

        self.set_mat_section(res)
        self.set_opt_section(res)

        self.set_trn_cost_group(res)
        self.set_trn_section(res)
        self.set_trn_extra_cost_group(res)

        self.set_bim_log_group(res)
        self.set_imp_extra_cost_group(res)
        self.set_imp_manpower_cost_group(res)
        self.set_imp_man_imp_code_cost_group(res)
        self.set_oim_price_calculation_cost_group(res)
        self.set_oim_extra_exp_cost_group(res)
        self.set_ps_vendor_line_cost_group(res)
        
        self.set_info_sec_tech_line_cost_group(res)
        self.set_info_sec_extra_expense_line_cost_group(res)
        self.set_info_sec_subcontractor_line_cost_group(res)
        self.set_info_sec_vendor_line_cost_group(res)
        
        self.set_amc_preventive_mnt_cost_group(res)
        self.set_amc_remedial_mnt_cost_group(res)
        self.set_amc_spareparts_cost_group(res)
        self.set_amc_spareparts_section(res)
        self.set_amc_bmn_extra_exp_cost_group(res)
        self.set_amc_omn_preventive_cost_group(res)
        self.set_amc_omn_remedial_cost_group(res)
        self.set_amc_omn_spareparts_section(res)
        self.set_amc_omn_spareparts_cost_group(res)
        self.set_amc_omn_extra_exp_cost_group(res)

        self.set_om_resident_eng_cost_group(res)
        self.set_om_material_section(res)
        self.set_om_material_cost_group(res)
        self.set_om_extra_exp_cost_group(res)
        
        self.set_imp_tech_group(res)
        self.set_amc_tech_group(res)
        
        return res

           
    def update_opp_stage_design_ready(self):
        
        opp_design_ready_state_id =4
        check_ids = [6,12,5,14]#won pipeline commit stage ids
        if self.lead_id.stage_id.id not in check_ids:
            self.lead_id.write({'stage_id':opp_design_ready_state_id})
    
    def update_opp_stage_submitted(self):
        if self.status =='active':
            pipe_stage_id =12
            check_ids = [1,4] #approved, design ready stage
            if self.lead_id.stage_id.id in check_ids:
                self.lead_id.write({'stage_id':pipe_stage_id})
        
    def update_opp_stage_committed(self):
        if self.status =='active':
            commit_stage_id =5
            self.lead_id.write({'stage_id':commit_stage_id})
            
    def check_tabs_in_loss(self):
        if not self.ignore_mp_sale:
            #MAT &TRN &OM
            included = self.included_in_quotation
            mat_sale = self.mat_tot_sale1_ds
            mat_cost = self.mat_tot_cost1
            trn_included = self.included_trn_in_quotation
            trn_sale = self.trn_tot_sale1_ds
            trn_cost = self.trn_tot_cost1
            om_included = self.included_om_in_quotation
            om_sale = self.o_m_tot_sale1_ds
            om_cost = self.o_m_tot_cost1
            mc_included = self.included_bmn_in_quotation
            mc_sale = self.bmn_tot_sale1_ds + self.omn_tot_sale1_ds
            mc_cost = self.bmn_tot_cost1 + self.omn_tot_cost1
            ps_included = self.included_bim_in_quotation
            ps_sale = self.bim_tot_sale1_ds + self.oim_tot_sale1_ds
            ps_cost = self.bim_tot_cost1 + self.oim_tot_cost1
            mp_sale = self.a_total_manpower_sale
            mp_cost = self.returned_mp
            info_sec_included = self.included_info_sec_in_quotation
            infosec_sale = self.bis_tot_sale1_ds + self.ois_tot_sale1_ds
            infosec_cost = self.bis_tot_cost1 + self.ois_tot_cost1
            if included and mat_sale < mat_cost:
                raise Warning("MAT Sales cannot be in loss. Please secure GM approval before moving forward.")
            if trn_included and trn_sale < trn_cost:
                raise Warning("TRN Sales cannot be in loss. Please secure GM approval before moving forward.")
#             if self.a_bim_sale < self.a_bim_cost:
#                 raise Warning("Beta IT Manpower Sales (Implementation) CANNOT be less than Beta IT Manpower Cost (Implementation)")
#             if self.a_bmn_sale < self.a_bmn_cost:
#                 raise Warning("Beta IT Manpower Sales (SLA) CANNOT be less than Beta IT Manpower Cost (SLA)")
            if ps_included and ps_sale < ps_cost:
                raise Warning("PS Sales cannot be in loss. Please secure GM approval before moving forward.")
            if info_sec_included and infosec_sale < infosec_cost:
                raise Warning("IS Sales cannot be in loss. Please secure GM approval before moving forward.")
            if mc_included and mc_sale < mc_cost:
                raise Warning("MC Sales cannot be in loss. Please secure GM approval before moving forward.")
            if om_included and om_sale < om_cost:
                raise Warning("OM Sales cannot be in loss. Please secure GM approval before moving forward.")
#             if mp_sale < mp_cost:
#                 raise Warning("Beta IT Manpower Sales (Implementation or SLA) CANNOT be less than Beta IT Manpower Cost (Implementation or SLA)")

        return True
            
                
    @api.one 
    def btn_design_ready(self):
        defaults ={}
        self.update_cost_sheet()
        #self.check_tabs_in_loss()
        self.submitted_date = str(datetime.now())
        if self.status == 'active':
            date =str(datetime.now())
            self.lead_id.finished_on_7 =date[:10]
            self.update_opp_stage_design_ready()
        self.state ='design_ready'
        self.date_log_history_line = [{'name':'Design Ready','date':str(datetime.now())}]
        branch_id = self.lead_id and self.lead_id.od_branch_id and self.lead_id.od_branch_id.id or False 
        if branch_id == 2:
            for line in self.costgroup_material_line:
                if line.tax_id and line.tax_id.id not in (33,34):
                    raise Warning("VAT used is different\nKindly Use SVAT - ADH for Abu Dhabi Customers. Please update on all Tables and Tabs")
        defaults['name'] = 'LOCKED Cost Sheet of Version : ' + self.number + ' - ' + self.name
        defaults['status'] = 'baseline'
        self.copy(defaults)
        self.od_send_mail('cst_sheet_submit_mail')
                
            
        
    @api.one 
    def btn_overruled_by_gm(self):
        date_now =str(datetime.now())
        self.is_over_rule = True
        self.over_rule ='over_rule'
        self.over_rule_uid = self.env.uid 
        self.over_rule_date =date_now
    
    
    def update_submited(self):
        date_now =str(datetime.now())
        self.submit_to_customer_date = date_now
        self.date_log_history_line = [{'name':'Submit To Customer','date':date_now}]
        self.write({'state':'submitted'})
        
    def check_user_approval_access(self,user_id):
        uid = self._uid
        user_pool =self.env['res.users']
        user_obj = user_pool.browse(user_id)
        admin_ids = [1,154,268]
        if uid in admin_ids:
            return True
        if  uid != user_id:
            raise Warning("You are not allowed to do this action on this Cost Sheet, Please ask %s to do this."%user_obj.name)
        return uid == user_id
    
    def complete_cost_sheet_submit(self):
        if self.state == 'submitted':
            return { 'type': 'ir.actions.client', 'tag': 'reload'}
        self.update_submited()
        self.update_opp_stage_submitted()
        self.refresh()
        return self.print_cost_sheet()
    
    def complete_cost_sheet_handover(self):
        self.state ='handover'
        self.update_price_fix()
        self.update_cost_sheet()
        self.date_log_history_line = [{'name':'Handover Date','date':str(datetime.now())}]
        self.od_send_mail('cst_sheet_handover_mail')
        
    def complete_cost_sheet_locking(self):
        self.state ='waiting_po'
        self.change_date = str(datetime.now())
        self.date_log_history_line = [{'name':'Waiting PO Locked Modification','date':str(datetime.now())}]

    def complete_process(self):
        state = self.state
        if state== 'design_ready':
            gp_perc = self.total_gp_percent
            self.gp_approval_state = 'approved'
            self.complete_cost_sheet_submit()
        if state =='commit':
            self.approved_gp = gp_perc
            self.gp_approval_state = 'approved'
            self.complete_cost_sheet_handover()
        if state =='waiting_po_open':
            self.approved_gp = gp_perc
            self.gp_approval_state = 'approved'
            self.complete_cost_sheet_locking()
        
    @api.one
    def btn_gp_first_approval(self):
        branch_id = self.od_branch_id
        ap_user_id = branch_id.user_id_1 and branch_id.user_id_1.id or False
        self.check_user_approval_access(ap_user_id)
        gp_perc = self.total_gp_percent
        self.update_cost_sheet()
        self.done_approval_1 = True
        self.gp_approval_log_line = [{'name':'First Approval','date':str(datetime.now()), 'gp_perc': gp_perc,'user_id': self.env.user and self.env.user.id or False}]
        if self.need_approval_2:
            self.gp_approval_state = 'second_apprv'
            self.od_send_mail('cst_sheet_gp_approval2_mail')
        else:
            self.complete_process()

    @api.one
    def btn_gp_second_approval(self):
        branch_id = self.od_branch_id
        ap_user_id = branch_id.user_id_2 and branch_id.user_id_2.id or False
        self.check_user_approval_access(ap_user_id)
        gp_perc = self.total_gp_percent
        self.update_cost_sheet()
        self.done_approval_2 = True
        self.gp_approval_log_line = [{'name':'Second Approval','date':str(datetime.now()), 'gp_perc': gp_perc,'user_id': self.env.user and self.env.user.id or False}]
        if self.need_approval_3:
            self.gp_approval_state = 'third_apprv'
            self.od_send_mail('cst_sheet_gp_approval3_mail')
        else:
            self.complete_process()

    @api.one
    def btn_gp_third_approval(self):
        branch_id = self.od_branch_id
        ap_user_id = branch_id.user_id_3 and branch_id.user_id_3.id or False 
        self.check_user_approval_access(ap_user_id)
        gp_perc = self.total_gp_percent
        self.update_cost_sheet()
        self.done_approval_3 = True
        self.gp_approval_log_line = [{'name':'Third Approval','date':str(datetime.now()), 'gp_perc': gp_perc,'user_id': self.env.user and self.env.user.id or False}]
        if self.need_approval_4:
            self.gp_approval_state = 'final_apprv'
            self.od_send_mail('cst_sheet_gp_approval4_mail')
        else:
            self.complete_process()

    @api.one
    def btn_gp_fourth_approval(self):
        branch_id = self.od_branch_id
        ap_user_id = branch_id.user_id_4 and branch_id.user_id_4.id or False
        self.check_user_approval_access(ap_user_id)
        gp_perc = self.total_gp_percent
        self.update_cost_sheet()
        self.done_approval_4 = True
        self.gp_approval_log_line = [{'name':'Fourth Approval','date':str(datetime.now()), 'gp_perc': gp_perc,'user_id': self.env.user and self.env.user.id or False}]
        self.complete_process()
        
    def check_last_leg(self):
        res = [0]
        branch_id = self.od_branch_id
        if  branch_id.enab_1:
            res.append(1)
        if  branch_id.enab_2:
            res.append(2)
        if  branch_id.enab_3:
            res.append(3)
        if  branch_id.enab_4:
            res.append(4)
        return max(res)

    def get_approvals(self,approv_num,last):
        branch_id = self.od_branch_id
        gp_perc = self.total_gp_percent
        check =eval('branch_id.'+'enab_'+ str(approv_num)) and eval('branch_id.'+'range_fr_'+str(approv_num)) <= gp_perc < eval('branch_id.'+'range_to_'+str(approv_num))
        if approv_num == last:
            check = eval('branch_id.'+'enab_'+ str(approv_num)) and gp_perc < eval('branch_id.'+'range_to_'+str(approv_num))
        return check
    
    def check_gp_approval(self):
        branch_id = self.od_branch_id
        if not branch_id:
            raise Warning("Please update the Cost sheet Branch")
        gp_perc = self.total_gp_percent
        
        #Checking the level for GP Approval
#         need_approval_11 = branch_id.enab_1 and branch_id.range_fr_1 <= gp_perc < branch_id.range_to_1
#         need_approval_22 = branch_id.enab_2 and branch_id.range_fr_2 <= gp_perc < branch_id.range_to_2
#         need_approval_33 = branch_id.enab_3 and branch_id.range_fr_3 <= gp_perc < branch_id.range_to_3
#         need_approval_44 = branch_id.enab_4 and gp_perc < branch_id.range_to_4
                        
        last = self.check_last_leg()
        need_approval_1 = self.get_approvals(1,last=last)
        need_approval_2 = self.get_approvals(2,last=last)
        need_approval_3 = self.get_approvals(3,last=last)
        need_approval_4 = self.get_approvals(4,last=last)
                
        if need_approval_1:
            self.need_approval_1 = True
            self.need_approval_2 = False
            self.need_approval_3 = False
            self.need_approval_4 = False
        if need_approval_2:
            self.need_approval_1 = True
            self.need_approval_2 = True
            self.need_approval_3 = False
            self.need_approval_4 = False
        if need_approval_3:
            self.need_approval_1 = True
            self.need_approval_2 = True
            self.need_approval_3 = True
            self.need_approval_4 = False
        if need_approval_4:
            self.need_approval_1 = True
            self.need_approval_2 = True
            self.need_approval_3 = True
            self.need_approval_4 = True
            
        if need_approval_1 or need_approval_2 or need_approval_3 or need_approval_4 :
            self.gp_approval_state = 'first_apprv'
            self.od_send_mail('cst_sheet_gp_approval1_mail')
            return True
        else:
            self.gp_approval_state = 'no_apprv'
            return False

    @api.multi
    def btn_submit(self):
        self.update_cost_sheet()
        self.check_tabs_in_loss()
        res = self.check_gp_approval() #Check if GP Approval needed
        if not res:
            self.complete_cost_sheet_submit()

    def update_opp_stage_from_cm_pip(self):
        if self.status =='active':
            pipe_stage_id =12
            self.lead_id.write({'stage_id':pipe_stage_id})
    
    @api.multi 
    def btn_commit(self):
        if not self.status =='active':
            raise Warning("Only Active Cost Sheet Can be Committed")
        self.update_cost_sheet()
        self.check_tabs_in_loss()
        date_now =str(datetime.now())
        self.date_log_history_line = [{'name':'Commit','date':date_now}]
        self.update_opp_stage_committed()
        self.write({'state':'commit'})
        
    @api.multi 
    def btn_return_pipeline(self):
        self.update_cost_sheet()
        date_now =str(datetime.now())
        self.date_log_history_line = [{'name':'Return to Pipeline','date':date_now}]
        self.update_opp_stage_from_cm_pip()
        self.write({'state':'submitted'})
        
    
    @api.multi
    def button_cancel(self):
        ctx = {'method':'btn_cancel'}
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'gen.wiz.confirm',
                'context':ctx,
                'type': 'ir.actions.act_window',
                'target': 'new',
            }
        
    def cancel_all_analytic_accounts(self):
        analytic_pool = self.env['account.analytic.account']
        so_tab_map,so_analyti_map = self.get_so_tab_map()
        #Canceling A1,A2 & A3 Analytic accounts
        for tab,analytic_id in so_analyti_map.iteritems():
            if analytic_id:
                analytic_obj = analytic_pool.browse(analytic_id)
                analytic_obj.set_cancel()
        #Canceling View Accounts and their child accounts        
        parent_view = self.analytic_a0
        amc_view = self.analytic_a4
        om_view = self.analytic_a5
        if amc_view:
            child_analytics = analytic_pool.search([('parent_id', '=', amc_view.id), ('od_cost_sheet_id', '=', self.id)])
            for analytic in child_analytics:
                analytic.set_cancel()
            amc_view.set_cancel()
        if om_view:
            child_analytics = analytic_pool.search([('parent_id', '=', om_view.id), ('od_cost_sheet_id', '=', self.id)])
            for analytic in child_analytics:
                analytic.set_cancel()
            om_view.set_cancel()
        if parent_view:
            parent_view.set_cancel()
        return True

    @api.one 
    def btn_cancel(self):
        self.update_cost_sheet()
        if self.state == 'done':
            self.cancel_all_analytic_accounts()     
        self.write({'state':'cancel'})

    @api.one
    def btn_reset_draft(self):
        self.update_cost_sheet()
        self.state ='draft'
        self.date_log_history_line = [{'name':'Submit to Draft','date':str(datetime.now())}]

    def check_any_tab_include(self):
        tab_include = [self.included_in_quotation, self.included_trn_in_quotation, self.included_bim_in_quotation, self.included_info_sec_in_quotation, self.included_bmn_in_quotation, self.included_om_in_quotation]
        if not any(tab_include) == True:
            return False
        return True
    
    
    
    def update_price_fix(self):
        
        price_fixed = self.price_fixed 
        if not price_fixed:
            
            self.bim_log_price_fixed = round(self.bim_log_price)
            self.price_fix_line(self.mat_main_pro_line)
            self.price_fix_line(self.mat_extra_expense_line,2)
            self.price_fix_line(self.mat_optional_item_line )
            self.price_fix_line(self.trn_customer_training_line)
            self.price_fix_line(self.trn_customer_training_extra_expense_line, 2)
            self.price_fix_line(self.implimentation_extra_expense_line)
            self.price_fix_line(self.manpower_manual_line)
            self.price_fix_line(self.bim_implementation_code_line)
            self.price_fix_line(self.oim_implimentation_price_line)
            self.price_fix_line(self.oim_extra_expenses_line)
            self.price_fix_line(self.bmn_it_preventive_line)
            self.price_fix_line(self.bmn_it_remedial_line)
            self.price_fix_line(self.bmn_spareparts_beta_it_maintenance_line)
            self.price_fix_line(self.bmn_beta_it_maintenance_extra_expense_line)
            self.price_fix_line(self.omn_out_preventive_maintenance_line)
            self.price_fix_line(self.omn_out_remedial_maintenance_line)
            self.price_fix_line(self.omn_spare_parts_line)
            self.price_fix_line(self.omn_maintenance_extra_expense_line)
            self.price_fix_line(self.om_residenteng_line)
            self.price_fix_line(self.om_eqpmentreq_line)
            self.price_fix_line(self.om_extra_line)
            self.price_fix_line(self.imp_tech_line)
            self.price_fix_line(self.amc_tech_line)
            self.price_fix_line(self.om_tech_line)
            self.price_fix_line(self.ps_vendor_line)
            self.price_fix_line(self.info_sec_tech_line)
            self.price_fix_line(self.info_sec_extra_expense_line)
            self.price_fix_line(self.info_sec_subcontractor_line)
            self.price_fix_line(self.info_sec_vendor_line)
            self.write({'price_fixed':True})
            
            
    @api.one
    def btn_handover(self):
        self.update_cost_sheet()
        self.check_tabs_in_loss()
        if self.status != 'active':
            raise Warning('Only Active Cost Sheet Can Be Hand overed.')
        if not self.check_any_tab_include():
            raise Warning("Nothing is Included to Handover")
        #Commented as requested by Elayyan on 04/04/23
#         check_proof_cost = self.check_proof_cost()
#          if check_proof_cost:
#              raise Warning('Proof Of Cost field is Empty,Which Will Not Allow To Handover Cost Sheet!!!!')
        self.check_handover_min_docs()
        if not self.handover_date:
            self.od_send_mail('cst_sheet_handover_mail')
        else:
            self.od_send_mail('cst_sheet_handover_mail_after_proj_return')
        self.handover_date = str(datetime.now())
        approved_gp = self.approved_gp
        current_gp = self.total_gp_percent
        gp_approved_state = self.gp_approval_state
        if gp_approved_state=='approved' and current_gp < approved_gp:
            res = self.check_gp_approval()
        else:    
            self.state ='handover'
            self.update_price_fix()
            self.update_cost_sheet()
            self.date_log_history_line = [{'name':'Handover Date','date':str(datetime.now())}]
            #self.od_send_mail('cst_sheet_handover_mail')
            self.send_sales_kpi_not_ok_mail()

    @api.one
    def btn_reset_submit(self):
        self.update_cost_sheet()
        self.od_send_mail('cst_sheet_reset_submit_mail')
        self.date_log_history_line = [{'name':'Return By PMO','date':str(datetime.now())}]
        self.state = 'returned_by_pmo'

    @api.one
    def btn_waiting_po(self):
#         self.update_cost_sheet()
        if not self.processed_date:
                self.processed_date = str(datetime.now())
        self.date_log_history_line = [{'name':'Waiting PO','date':str(datetime.now())}]
        self.state = 'waiting_po'

    @api.one
    def btn_waiting_to_handover(self):
        self.update_cost_sheet()
        self.date_log_history_line = [{'name':'Waiting to Handover','date':str(datetime.now())}]
        self.state = 'handover'
    
    def check_po_cred(self):
        if not self.po_select_1:
            raise Warning("No PO Procurement Plan!!!")
        for da in range(1,13):
            st ='self.po_select_' + str(da)
            if eval(st):
                cr = 'self.po_cred_' + str(da)
                if not eval(cr):
                    raise Warning("Credit Days Should be Entered in PO Procurement Plan")
    
    def check_inv_cred(self):
        
        for da in range(1,13):
            st ='self.inv_select_' + str(da)
            if eval(st):
                cr = 'self.inv_cred_' + str(da)
                if not eval(cr):
                    raise Warning("Credit Days Should be Entered in Invoice Plan")
        
    
    
    @api.one
    def btn_process(self):
#         self.update_cost_sheet()
        self.check_rev_exist()
        if not self.processed_date:
            self.processed_date = str(datetime.now())
        self.check_process_min_docs()
        self.od_send_mail('cst_sheet_process_mail')
        self.date_log_history_line = [{'name':'Processed Date','date':str(datetime.now())}]
        self.state = 'processed'
        if not self.ignore_inv_plan:
            self.update_inv_relation()
        self.check_po_cred()
        self.check_inv_cred()
    
    
    
    def action_pmo_director(self):
        if self.select_a4 and not (self.tabs_a4 and self.date_start_a4 and self.date_end_a4 and self.name_a4 and self.owner_id_a4 and self.type_of_project_a4 and self.periodicity_amc and self.l2_start_date_amc and self.no_of_l2_accounts_amc):
            raise Warning("Please Fill all AMC Details in Revenue Structure")
        
        if self.select_a5 and not (self.tabs_a5 and self.date_start_a5 and self.date_end_a5 and self.name_a5 and self.owner_id_a5 and self.type_of_project_a5 and self.periodicity_om and self.l2_start_date_om and self.no_of_l2_accounts_om):
            raise Warning("Please Fill all O&M Details in Revenue Structure")
        self.od_send_mail('cst_sheet_pmo_mail')
        self.date_log_history_line = [{'name':'PMO Date','date':str(datetime.now())}]
        self.pmo_date = str(datetime.now())
        self.state = 'pmo'
    
    @api.multi 
    def btn_pmo_director(self):
        #line 2766 Added by Aslam to update the cost sheet finally before Finance Approves
        self.update_cost_sheet()
        self.check_tabs_in_loss()
        profit_vals = []
        for seq in range(1,6):
            select_seq = eval('self.'+'select_a'+ str(seq))
            if select_seq:
                dat =eval('self.'+'profit_a'+ str(seq)) >= 0.0
                profit_vals.append(dat)
        
        if all(profit_vals):
            self.action_pmo_director()
        else:
            if self.ig_exception:
                self.action_pmo_director()
            else:
                raise Warning("Analytic Account cannot be in loss !")
        if self.disc_tot_profit < 0:
            if self.ig_exception:
                pass
            else:
                raise Warning("Analytic Account cannot be in loss !")

        
#             return {
#                 'view_type': 'form',
#                 'view_mode': 'form',
#                 'res_model': 'pmo.wiz',
#                 'type': 'ir.actions.act_window',
#                 'target': 'new',
# 
#             }
        
    
    @api.one
    def btn_process_change(self):
        self.update_cost_sheet()
        self.check_tabs_in_loss()
        self.check_rev_exist()
        self.check_process_min_docs()
        self.od_send_mail('cst_sheet_change_processed_mail')
        self.date_log_history_line = [{'name':'Change Processed Date','date':str(datetime.now())}]
        self.state = 'change_processed'
        if not self.ignore_inv_plan:
            self.update_inv_relation()
        
    
    def amend_btn_process_change(self):
        self.update_cost_sheet()
#         self.check_rev_exist()
#         self.check_process_min_docs()
        self.od_send_mail('cst_sheet_change_processed_mail')
        self.date_log_history_line = [{'name':'Change Processed Date','date':str(datetime.now())}]
        self.state = 'change_processed'
#         self.update_inv_relation()
    
    
    
    @api.one
    def btn_process_waiting_po(self):
#         self.update_cost_sheet()
        self.check_rev_exist()
        self.check_process_min_docs()
        handover_date = self.handover_date
        if not self.processed_date:
            self.processed_date = handover_date
        self.od_send_mail('cst_sheet_process_mail')
        self.date_log_history_line = [{'name':'Waiting PO Processed Date','date':str(datetime.now())}]
        self.state = 'waiting_po_processed'
        if not self.ignore_inv_plan:
            self.update_inv_relation()
        
    
    @api.one
    def btn_process_redistribution(self):
        self.update_cost_sheet()
        self.check_rev_exist()
        self.check_process_min_docs()
        self.od_send_mail('cst_sheet_pmo_mail')
        self.date_log_history_line = [{'name':'Redistribution Processed Date','date':str(datetime.now())}]
        self.state = 'redistribution_processed'
        if not self.ignore_inv_plan:
            self.update_inv_relation()
    
    @api.one
    def btn_reset_handover(self):
        self.update_cost_sheet()
        self.od_send_mail('cst_sheet_reset_handover_mail')
        self.date_log_history_line = [{'name':'Return By Finance','date':str(datetime.now())}]
        self.state = 'returned_by_fin'
        
    
    @api.one
    def btn_reset_change(self):
        
        self.date_log_history_line = [{'name':'Return to Change','date':str(datetime.now())}]
        self.state = 'change'
    
    
    def update_opp_stage(self):
        stage_pool = self.env['crm.case.stage']
        stage_ob = stage_pool.search([('name','=','Won')],limit =1)
        if not stage_ob:
            raise Warning("Won Stage Not Available Please Create One for Opportunity")
        stage_id = stage_ob.id
        self.lead_id.write({'stage_id':stage_id})

    def check_adv_payment(self):
        if self.adv_payment_status == 'required':
            raise Warning("Advance Payment Not Collected Yet")
        return True
    
    
    def get_lvl_1_an(self):
        res =[]
        a1= self.analytic_a1 and self.analytic_a1.id or False
        if a1:
            res.append(a1)
        a2=self.analytic_a2 and self.analytic_a2.id or False
        if a2:
            res.append(a2)
        a3=self.analytic_a3 and self.analytic_a3.id or False
        if a3:
            res.append(a3)
        return res
    def get_lvl_2_an(self):
        res =[]
        for line in self.amc_analytic_line:
            analytic_id = line.analytic_id and line.analytic_id.id or False
            if analytic_id:
                res.append(analytic_id)
        
        for line in self.om_analytic_line:
            analytic_id = line.analytic_id and line.analytic_id.id or False
            if analytic_id:
                res.append(analytic_id)
        return res
    
    
     
    
    def get_all_generated_analytic(self):
        level_1= self.get_lvl_1_an()
        level_2 = self.get_lvl_2_an()
        return level_1+level_2
    
    def update_analytic_sale_cost_value(self):
        analytic_ids = self.get_all_generated_analytic()
        pool = self.env['account.analytic.account']
        for analytic_id in analytic_ids:
            analytic = pool.browse(analytic_id)
            amended_sale= analytic.od_amended_sale_price
            amended_cost = analytic.od_amended_sale_cost
            analytic.write({'od_amended_sale_rg':amended_sale,'od_amended_cost_rg':amended_cost })
            
            
    
    def update_analytic_from_tag(self,line_id):
        sheet_id = self.id 
        analytic_a0 = self.analytic_a0 and self.analytic_a0.id or False
        for line in line_id:
            analytic_tag = line.analytic_tag
            an =self.env['account.analytic.account'].search([('od_cost_sheet_id','=',sheet_id),('analytic_tag','=',analytic_tag)],limit=1)
            line.write({'child_analytic_id':an.id,'analytic_id':analytic_a0})
    
    
    
    def map_tag_analytic(self):
        self.update_analytic_from_tag(self.od_plan_dist_line)
        self.update_analytic_from_tag(self.od_an_inv_rel_line)
    
    
        
    def create_sch(self):
        if self.schedule_created:
            return True
        for num in range(1,13):
            if eval('self.'+'inv_select_'+str(num)):
                self.sch_inv(num)
            
        self.schedule_created = True
    
    def create_po_schedule(self):
        if self.po_schedule_created:
            return True
        for num in range(1,13):
            if eval('self.'+'po_select_'+str(num)):
                self.sch_po(num)
            
        self.po_schedule_created = True
        
        
    def update_a0_inv_plan(self):
        inv_sch = self.env['od.project.invoice.schedule']
        analyic_a0 = self.analytic_a0
        if self.inv_select_1:
            inv1 = inv_sch.search([('name','=','INV1'),('analytic_id','=', analyic_a0.id)],limit=1)
            if inv1:
                    inv1.write({'date': self.planned_date_1, 'pmo_date': self.planned_date_1, 'amount':self.inv_amount_1})
                
            else:
                inv_sch.create({'date': self.planned_date_1, 'pmo_date': self.planned_date_1, 'amount':self.inv_amount_1,
                                'inv_seq': 'inv1', 
                                'name':'INV1',
                                'analytic_id':analyic_a0.id, 
                                'grand_analytic_id':analyic_a0.id})
                        
        if self.inv_select_2:
            inv2 = inv_sch.search([('name','=','INV2'),('analytic_id','=', analyic_a0.id)],limit=1)
            if inv2:
                inv2.write({'date': self.planned_date_2, 'pmo_date': self.planned_date_2, 'amount':self.inv_amount_2})
                
            else:
                inv_sch.create({'date': self.planned_date_2, 'pmo_date': self.planned_date_2, 'amount':self.inv_amount_2,
                                'inv_seq': 'inv2', 
                                'name':'INV2',
                                'analytic_id':analyic_a0.id, 
                                'grand_analytic_id':analyic_a0.id})
        else:
            inv2 = inv_sch.search([('name','=','INV2'),('analytic_id','=', analyic_a0.id)],limit=1)
            if inv2:
                inv2.unlink()
                        
        if self.inv_select_3:
            inv3 = inv_sch.search([('name','=','INV3'),('analytic_id','=', analyic_a0.id)],limit=1)
            if inv3:
                inv3.write({'date': self.planned_date_3, 'pmo_date': self.planned_date_3, 'amount':self.inv_amount_3})
            else:
                inv_sch.create({'date': self.planned_date_3, 'pmo_date': self.planned_date_3, 'amount':self.inv_amount_3,
                                'inv_seq': 'inv3', 
                                'name':'INV3',
                                'analytic_id':analyic_a0.id, 
                                'grand_analytic_id':analyic_a0.id})
        
        else:
            inv3 = inv_sch.search([('name','=','INV3'),('analytic_id','=', analyic_a0.id)],limit=1)
            if inv3:
                inv3.unlink()
                
        if self.inv_select_4:
            inv4 = inv_sch.search([('name','=','INV4'),('analytic_id','=', analyic_a0.id)],limit=1)
            if inv4:
                inv4.write({'date': self.planned_date_4, 'pmo_date': self.planned_date_4, 'amount':self.inv_amount_4})
            else:
                inv_sch.create({'date': self.planned_date_4, 'pmo_date': self.planned_date_4, 'amount':self.inv_amount_4,
                                'inv_seq': 'inv4', 
                                'name':'INV4',
                                'analytic_id':analyic_a0.id, 
                                'grand_analytic_id':analyic_a0.id})                
        else:
            inv4 = inv_sch.search([('name','=','INV4'),('analytic_id','=', analyic_a0.id)],limit=1)
            if inv4:
                inv4.unlink()
        
        if self.inv_select_5:
            inv5 = inv_sch.search([('name','=','INV5'),('analytic_id','=', analyic_a0.id)],limit=1)
            if inv5:
                inv5.write({'date': self.planned_date_5, 'pmo_date': self.planned_date_5, 'amount':self.inv_amount_5})
            else:
                inv_sch.create({'date': self.planned_date_5, 'pmo_date': self.planned_date_5, 'amount':self.inv_amount_5,
                                'inv_seq': 'inv5', 
                                'name':'INV5',
                                'analytic_id':analyic_a0.id, 
                                'grand_analytic_id':analyic_a0.id})
        else:
            inv5 = inv_sch.search([('name','=','INV5'),('analytic_id','=', analyic_a0.id)],limit=1)
            if inv5:
                inv5.unlink()
        
        if self.inv_select_6:
            inv6 = inv_sch.search([('name','=','INV6'),('analytic_id','=', analyic_a0.id)],limit=1)
            if inv6:
                inv6.write({'date': self.planned_date_6, 'pmo_date': self.planned_date_6, 'amount':self.inv_amount_6})
            else:
                inv_sch.create({'date': self.planned_date_6, 'pmo_date': self.planned_date_6, 'amount':self.inv_amount_6,
                                'inv_seq': 'inv6', 
                                'name':'INV6',
                                'analytic_id':analyic_a0.id, 
                                'grand_analytic_id':analyic_a0.id})
        else:
            inv6 = inv_sch.search([('name','=','INV6'),('analytic_id','=', analyic_a0.id)],limit=1)
            if inv6:
                inv6.unlink()
        
        if self.inv_select_7:
            inv7 = inv_sch.search([('name','=','INV7'),('analytic_id','=', analyic_a0.id)],limit=1)
            if inv7:
                inv7.write({'date': self.planned_date_7, 'pmo_date': self.planned_date_7, 'amount':self.inv_amount_7})
            else:
                inv_sch.create({'date': self.planned_date_7, 'pmo_date': self.planned_date_7, 'amount':self.inv_amount_7,
                                'inv_seq': 'inv7', 
                                'name':'INV7',
                                'analytic_id':analyic_a0.id, 
                                'grand_analytic_id':analyic_a0.id})
        else:
            inv7 = inv_sch.search([('name','=','INV7'),('analytic_id','=', analyic_a0.id)],limit=1)
            if inv7:
                inv7.unlink()
        
        if self.inv_select_8:
            inv8 = inv_sch.search([('name','=','INV8'),('analytic_id','=', analyic_a0.id)],limit=1)
            if inv8:
                inv8.write({'date': self.planned_date_8, 'pmo_date': self.planned_date_8, 'amount':self.inv_amount_8})
            else:
                inv_sch.create({'date': self.planned_date_8, 'pmo_date': self.planned_date_8, 'amount':self.inv_amount_8,
                                'inv_seq': 'inv8', 
                                'name':'INV8',
                                'analytic_id':analyic_a0.id, 
                                'grand_analytic_id':analyic_a0.id})
        
        else:
            inv8 = inv_sch.search([('name','=','INV8'),('analytic_id','=', analyic_a0.id)],limit=1)
            if inv8:
                inv8.unlink()
        
        if self.inv_select_9:
            inv9 = inv_sch.search([('name','=','INV9'),('analytic_id','=', analyic_a0.id)],limit=1)
            if inv9:
                inv9.write({'date': self.planned_date_9, 'pmo_date': self.planned_date_9, 'amount':self.inv_amount_9})
            else:
                inv_sch.create({'date': self.planned_date_9, 'pmo_date': self.planned_date_9, 'amount':self.inv_amount_9,
                                'inv_seq': 'inv9', 
                                'name':'INV9',
                                'analytic_id':analyic_a0.id, 
                                'grand_analytic_id':analyic_a0.id})
        else:
            inv9 = inv_sch.search([('name','=','INV9'),('analytic_id','=', analyic_a0.id)],limit=1)
            if inv9:
                inv9.unlink()
        
        if self.inv_select_10:
            inv10 = inv_sch.search([('name','=','INV10'),('analytic_id','=', analyic_a0.id)],limit=1)
            if inv10:
                inv10.write({'date': self.planned_date_10, 'pmo_date': self.planned_date_10, 'amount':self.inv_amount_10})
            else:
                inv_sch.create({'date': self.planned_date_10, 'pmo_date': self.planned_date_10, 'amount':self.inv_amount_10,
                                'inv_seq': 'inv10', 
                                'name':'INV10',
                                'analytic_id':analyic_a0.id, 
                                'grand_analytic_id':analyic_a0.id})
        
        else:
            inv10 = inv_sch.search([('name','=','INV10'),('analytic_id','=', analyic_a0.id)],limit=1)
            if inv10:
                inv10.unlink()
                
        if self.inv_select_11:
            inv11= inv_sch.search([('name','=','INV11'),('analytic_id','=', analyic_a0.id)],limit=1)
            if inv11:
                inv11.write({'date': self.planned_date_11, 'pmo_date': self.planned_date_11, 'amount':self.inv_amount_11})
            else:
                inv_sch.create({'date': self.planned_date_11, 'pmo_date': self.planned_date_11, 'amount':self.inv_amount_11,
                                'inv_seq': 'inv11', 
                                'name':'INV11',
                                'analytic_id':analyic_a0.id, 
                                'grand_analytic_id':analyic_a0.id})
        else:
            inv11 = inv_sch.search([('name','=','INV11'),('analytic_id','=', analyic_a0.id)],limit=1)
            if inv11:
                inv11.unlink()
        
        if self.inv_select_12:
            inv12 = inv_sch.search([('name','=','INV12'),('analytic_id','=', analyic_a0.id)],limit=1)
            if inv12:
                inv12.write({'date': self.planned_date_12, 'pmo_date': self.planned_date_12, 'amount':self.inv_amount_12})
            else:
                inv_sch.create({'date': self.planned_date_12, 'pmo_date': self.planned_date_12, 'amount':self.inv_amount_12,
                                'inv_seq': 'inv12', 
                                'name':'INV12',
                                'analytic_id':analyic_a0.id, 
                                'grand_analytic_id':analyic_a0.id})
        else:
            inv12 = inv_sch.search([('name','=','INV12'),('analytic_id','=', analyic_a0.id)],limit=1)
            if inv12:
                inv12.unlink()
        
        return True
    
    #Added by Aslam on Nov 22 to update invoice plan date change in child analytic to effect pm kpi
    def update_child_analytic_inv_plan(self):
        analyic_a0 = self.analytic_a0
        for inv_plan in analyic_a0.prj_inv_sch_line:
            projects = self.env['account.analytic.account'].search([('parent_id','=',analyic_a0.id), ('od_cost_sheet_id','=',self.id), ('od_type_of_project','not in',('amc_view', 'o_m_view'))])
            for project in projects:
                if project.od_project_invoice_schedule_line:
                    for line in project.od_project_invoice_schedule_line:
                        if line.name == inv_plan.name:
                            line.write({'date': inv_plan.date})
                        
                        
    def update_draft_tickets_to_wip(self):
        task_obj = self.env['project.task']
        opp_id = self.lead_id and self.lead_id.id or False
        tasks = task_obj.search([('od_opp_id','=',opp_id), ('od_stage','=','draft')])
        for task in tasks:
            analytic_account_id = self.analytic_a1 and self.analytic_a1.id or False
            project_id = self.env['project.project'].search([('analytic_account_id','=',analytic_account_id)],limit=1)
            if project_id:
                p_milestone = self.env['project.task'].search([('name','=','Initiation'),('project_id','=',project_id.id), ('od_type','not in',('activities', 'workpackage'))],limit=1)
                if p_milestone:
                    task.write({'od_opp_id':False, 'project_id': project_id.id, 'od_parent_id':p_milestone.id, 'od_state': p_milestone.od_state.id})
                else:
                    raise Warning("Kindly Unlink the Opportunity from Pending Tasks with ID %s, After Approval link the Tasks to a Project" % task.id)
            else: 
                raise Warning("Kindly Unlink the Opportunity from Pending Tasks with ID %s, After Approval link the Tasks to a Project" % task.id)
    
    @api.one
    def btn_approved(self):
        
#         self.od_send_mail('cst_sheet_approve_mail')
# this mail wiil be sent when assign an accountant
#         self.double_check_vat()
        appr_date =str(datetime.now())
        if not self.approved_date:
            self.approved_date =appr_date
#         self.update_cost_sheet()
        self.check_adv_payment()
        self.check_finance_comment()
#         if not self.approved_date:
#             self.approved_date = str(datetime.now())
        self.date_log_history_line = [{'name':'Button Approved Log Date','date':appr_date}]
        # self.status = 'baseline'
        self.create_analytic()
        self.analytic_a0 and self.analytic_a0.get_inv_plan()
#         self.generate_sale_order()
        if not self.ignore_inv_plan:
            #Added by aslam and commented to check later sami issue
            #self.update_inv_relation()
            self.check_plan_dist_condition()
        #Added by aslam inorder to prevent breakage of sale order if contains same part number in multiple lines.    
        if not self.inv_schedule_change:
            self.generate_sale_order_v3()
        self.update_opp_stage()
        # self.state = 'approved'
        if not self.lock_fin_struct:
            self.lock_fin_struct = True
        self.update_analytic_sale_cost_value()
        self.map_tag_analytic()
        self.create_sch()
        self.create_po_schedule()
        self.update_draft_tickets_to_wip()
        self.od_send_mail('cst_sheet_approve_mail')
        if self.inv_schedule_change:
            self.update_a0_inv_plan()
            self.update_child_analytic_inv_plan()
            self.inv_schedule_change = False
            self.sales_order_generated = True
            self.state = 'done'
            
            
        
        

    @api.one
    def btn_reset_process(self):
        self.update_cost_sheet()
        self.state = 'processed'
        self.date_log_history_line = [{'name':'Approved To Process','date':str(datetime.now())}]
        self.od_send_mail('cst_sheet_reset_process_mail')
        if not self.ignore_inv_plan:
            self.update_inv_relation()
    @api.one
    def btn_allow_change(self):
        self.update_cost_sheet()
        self.sales_order_generated = True
        self.state = 'change'
        self.change_date = str(datetime.now())
        self.date_log_history_line = [{'name':'Allow Change','date':str(datetime.now())}]
#         self.od_send_mail('cst_sheet_allow_change_mail')

    @api.one
    def btn_redistribute_analytic(self):
        self.update_cost_sheet()
        self.sales_order_generated = True
        self.state = 'analytic_change'
        self.lock_fin_struct=False
        self.change_date = str(datetime.now())
        self.date_log_history_line = [{'name':'Redistribute Analytic',
                                       'date':str(datetime.now())}
                                      ]

    @api.one
    def btn_modify(self):
        self.update_cost_sheet()
        self.sales_order_generated = True
        self.state = 'modify'
        self.change_date = str(datetime.now())
        self.date_log_history_line = [{'name':'Modify','date':str(datetime.now())}]

    
    
    
    def get_imp_cost(self):
        cost =0.0
        
        if self.included_bim_in_quotation:
            cost = sum([x.line_cost for x in self.manpower_manual_line ]) 
            if self.bim_log_select:
                cost += self.bim_log_cost
               
            if self.bim_imp_select:
                cost += sum([x.line_cost for x in self.bim_implementation_code_line])
               
        return cost
    
    def get_bmn_cost(self):
        cost =0.0
        if self.included_bmn_in_quotation:
            cost =sum([x.line_cost for x in self.bmn_it_preventive_line ])+sum([x.line_cost for x in self.bmn_it_remedial_line]) 
        return cost
    
     
    def get_imp_sale(self):
        sale=0.0
        if self.included_bim_in_quotation:
            sale = sum([x.line_price for x in self.manpower_manual_line ])
            if self.bim_log_select:
                sale += self.bim_log_price
            if self.bim_imp_select:
                sale += sum([x.line_price for x in self.bim_implementation_code_line])
        return sale
    
    def get_bmn_sale(self):
        sale =0.0
        if self.included_bmn_in_quotation:
            sale =sum([x.line_price for x in self.bmn_it_preventive_line ])+sum([x.line_price for x in self.bmn_it_remedial_line]) 
        return sale
    
    
    def calculate_imp(self):
        sale =cost =profit=profit_per=0.0
        bim_vat  = 0.0
        if self.included_bim_in_quotation:
            cost = sum([x.line_cost for x in self.manpower_manual_line ])
            sale = sum([x.line_price for x in self.manpower_manual_line ])
            bim_vat += self.get_vat_total(self.manpower_manual_line)
            if self.bim_log_select:
                cost += self.bim_log_cost
                sale += self.bim_log_price
                bim_vat += self.bim_log_vat_value
            if self.bim_imp_select:
                cost += sum([x.line_cost for x in self.bim_implementation_code_line])
                sale += sum([x.line_price for x in self.bim_implementation_code_line])
                bim_vat += self.get_vat_total(self.bim_implementation_code_line)
            profit = sale - cost 
            profit_per =0.0 
            if sale:
                profit_per = (profit/sale) * 100
        bim_tech_cost,bim_tech_sale = self.get_tech_bim()
        
        self.a_bim_cost = cost  + bim_tech_cost
        self.a_bim_sale = sale + bim_tech_sale 
        self.a_bim_profit = profit 
        self.a_bim_profit_percentage = profit_per
        self.a_bim_vat = bim_vat
        return {'cost':cost,'sale':sale,'vat':bim_vat}
    
    def calculate_bis(self):
        sale =cost =0.0
        bis_vat  = 0.0
        if self.included_info_sec_in_quotation:
            cost += sum([line.line_cost_local_currency for line in self.info_sec_tech_line])
            sale +=  sum([line.line_price for line in self.info_sec_tech_line])
            bis_vat += self.get_vat_total(self.info_sec_tech_line)
        profit = sale - cost 
        profit_per =0.0 
        if sale:
            profit_per = (profit/sale) * 100
        self.a_bis_cost = cost
        self.a_bis_sale = sale 
        self.a_bis_profit = profit 
        self.a_bis_profit_percentage = profit_per
        self.a_bis_vat = bis_vat
        return {'cost':cost,'sale':sale,'vat':bis_vat}
    
    def calculate_bmn(self):
        sale =cost =profit=profit_per=bmn_vat =0.0
        if self.included_bmn_in_quotation:
            cost =sum([x.line_cost for x in self.bmn_it_preventive_line ])+sum([x.line_cost for x in self.bmn_it_remedial_line])
            sale =sum([x.line_price for x in self.bmn_it_preventive_line ])+sum([x.line_price for x in self.bmn_it_remedial_line])
            bmn_vat += self.get_vat_total(self.bmn_it_preventive_line) + self.get_vat_total(self.bmn_it_remedial_line)
            profit = sale - cost 
            profit_per =0.0 
            if sale:
                profit_per = (profit/sale) * 100
        bmn_tech_cost,bmn_tech_sale = self.get_tech_bmn()
        self.a_bmn_cost = cost  + bmn_tech_cost
        self.a_bmn_sale = sale + bmn_tech_sale
        self.a_bmn_profit = profit 
        self.a_bmn_profit_percentage = profit_per
        self.a_bmn_vat = bmn_vat
        return {'cost':cost,'sale':sale,'vat':bmn_vat}
    def calculate_total_manpower_cost(self):
        cost= self.a_bim_cost + self.a_bmn_cost + self.a_bis_cost
        sale= self.a_bim_sale + self.a_bmn_sale + self.a_bis_sale
        vat = self.a_bim_vat + self.a_bmn_vat + self.a_bis_vat
        profit = sale -cost
        profit_per = 0.0
        if sale:
            profit_per = (profit/sale) * 100
        self.a_total_manpower_cost = cost 
        self.a_total_manpower_sale = sale
        self.a_total_manpower_profit = profit
        self.a_total_manpower_profit_percentage = profit_per
        self.a_total_manpower_vat = vat
        return cost
        
        

    
    def calculate_om(self):
        sale =cost =profit=profit_per=vat =0.0
        if self.included_om_in_quotation:
            cost =sum([x.line_cost for x in self.om_residenteng_line ])
            sale =sum([x.line_price for x in self.om_residenteng_line ])
            vat += self.get_vat_total(self.om_residenteng_line)
            profit = sale - cost 
            profit_per =0.0 
            if sale:
                profit_per = (profit/sale) * 100
        self.a_om_cost = cost 
        self.a_om_sale = sale 
        self.a_om_profit = profit 
        self.a_om_profit_percentage = profit_per
#         self.o_m_vat = vat
        return {'cost':cost,'sale':sale,'vat':vat}
    def calculate_bim_analy(self):
        result =[]
        result.append(self.calculate_imp())
        result.append(self.calculate_bis())
        result.append(self.calculate_bmn())
        result.append(self.calculate_om())
        cost = sum([x['cost']for x in result])
        sale = sum([x['sale']for x in result])
        vat = sum([x['vat']for x in result])
        profit = sale - cost 
        profit_per =0.0
        if sale:
            profit_per = (profit/sale) * 100
        self.a_tot_cost = cost
        self.a_tot_sale = sale
        self.a_tot_profit = profit 
        self.a_tot_profit_percentage = profit_per
        self.a_tot_vat = vat
    
    def get_revenue_total(self,line_ids):
        sale = cost = 0.0
        for line in line_ids:
            sale += line.total_sale 
            cost += line.total_cost
        return sale,cost
            
    
    def summarize_revenue(self):
        sale =self.get_revenue_total(self.mat_group_weight_line)[0] + self.get_revenue_total(self.imp_weight_line)[0] + self.get_revenue_total(self.info_sec_weight_line)[0] + self.get_revenue_total(self.amc_weight_line)[0] + self.get_revenue_total(self.om_weight_line)[0]
        cost =self.get_revenue_total(self.mat_group_weight_line)[1] + self.get_revenue_total(self.imp_weight_line)[1] + self.get_revenue_total(self.info_sec_weight_line)[1] + self.get_revenue_total(self.amc_weight_line)[1] + self.get_revenue_total(self.om_weight_line)[1]
        profit = sale - cost
        profit_perc  =0.0 
        if sale:
            profit_perc = (profit /sale) *100 
        self.rev_tot_sale1 = sale 
        self.rev_tot_cost1 = cost 
        self.rev_profit1 = profit 
        self.rev_profit_percentage1 = profit_perc
    
    
    def get_weight_summary(self):
        res = {}
        mat_res = {}
        total_mat_cost =0.0
        for line in self.mat_group_weight_line:
            res[line.pdt_grp_id.id] = {'sale':line.total_sale,'sale_aftr_disc':line.sale_aftr_disc,'cost':line.total_cost,'manpower_cost':0.0,'manpower_sale':0.0}
            mat_res[line.pdt_grp_id.id] = line.total_cost
            total_mat_cost += line.total_cost
        for line in self.extra_weight_line:
            data = res.get(line.pdt_grp_id.id,{})
            if data:
                data['sale'] += line.total_sale
                data['sale_aftr_disc'] += line.sale_aftr_disc 
                data['cost'] += line.total_cost
        for line in self.imp_weight_line:
            data = res.get(line.pdt_grp_id.id,{})
            if data:
                data['sale'] += line.total_sale
                data['sale_aftr_disc'] += line.sale_aftr_disc 
                data['cost'] += line.total_cost
                
        for line in self.info_sec_weight_line:
            data = res.get(line.pdt_grp_id.id,{})
            if data:
                data['sale'] += line.total_sale
                data['sale_aftr_disc'] += line.sale_aftr_disc 
                data['cost'] += line.total_cost
                

        
        for line in self.amc_weight_line:
            data = res.get(line.pdt_grp_id.id,{})
            if data:
                data['sale'] += line.total_sale
                data['sale_aftr_disc'] += line.sale_aftr_disc 
                data['cost'] += line.total_cost
               
                
        
        for line in self.om_weight_line:
            data = res.get(line.pdt_grp_id.id,{})
            if data:
                data['sale'] += line.total_sale
                data['sale_aftr_disc'] += line.sale_aftr_disc 
                data['cost'] += line.total_cost
#         if self.bim_log_select and self.bim_log_cost:
#             data = res.get(False,{})
#             data['sale'] += self.bim_log_price
#             data['sale_aftr_disc'] += self.bim_log_price
#             data['cost'] += self.bim_log_cost
            
#         tech_lines = self.get_tech_pdtgrp_vals()
#        
#         for tech_dat in tech_lines:
#             pdt_grp_id = tech_dat.get('pdt_grp_id')
#             data =  res.get(pdt_grp_id)
#             if data:
#                 data['sale'] += tech_dat.get('total_sale') 
#                 data['sale_aftr_disc'] += tech_dat.get('total_sale') 
#                 data['cost'] += tech_dat.get('total_cost')
#             else:
#                 res[pdt_grp_id] = {'sale':tech_dat.get('total_sale'),'sale_aftr_disc': tech_dat.get('total_sale') ,'cost':tech_dat.get('total_cost'),'manpower_cost':0.0}
#         
        return res,mat_res,total_mat_cost
    
    
    
    def generate_summary_weight(self):
        result,mat_res,total_mat_cost = self.get_weight_summary()
        data = []
        total_cost =0.0
        total_sale =0.0
        distribute_cost =0.0
        disc  = (self.special_discount)
        tech_vals = self.get_tech_pdtgrp_vals()
        tech_sale = sum([val.get('total_sale') for val in tech_vals])
        tech_cost = sum([val.get('total_cost') for val in tech_vals])
        redist_tech_manual = self.redist_tech_manual
        redist_re_manual= self.redist_re_manual
        if self.included_om_in_quotation and redist_re_manual:
            om_sale,om_cost,om_profit = self.get_tot_sale_cost2(self.om_residenteng_line) 
            for line in self.dist_re_line:
                pdt_grp_id = line.pdt_grp_id and line.pdt_grp_id.id
                value = line.value/100.0
                result_data = result.get(pdt_grp_id,{})
                if result_data:
                    sale =result_data.get('sale',0.0)
                    sale += om_sale * value
                    cost = result_data.get('cost',0.0)
                    cost += om_cost * value
                    result_data['sale'] = sale 
                    result_data['cost'] = cost 
                    
                else:
                    result[pdt_grp_id] = {'sale':om_sale  * value,'cost':om_cost  * value,'manpower_cost':0.0,'manpower_sale':0.0,'no_distribute':True}
            
            
          
        
        if not result and  redist_tech_manual:
            sale = self.sum_tot_sale - tech_sale 
            #added by aslam to decrease preopn if no mat values
            cost = self.sum_tot_cost -tech_cost - self.pre_opn_cost
            total_manpower_cost = self.get_imp_cost() + self.get_bmn_cost()
            total_manpower_sale = self.get_imp_sale() + self.get_bmn_sale()
            for line in self.dist_tech_line:
                pdt_grp_id = line.pdt_grp_id.id 
                value = line.value
                sale_p = sale * (value/100.0)
                cost_p = cost * (value/100.0)
                mp_c =total_manpower_cost * (value/100.0)
                mp_s =total_manpower_sale * (value/100.0)
                result[pdt_grp_id]= {'sale':sale_p,'cost':cost_p,'manpower_cost':mp_c,'manpower_sale':mp_s}
        
        
            
        if not result and not redist_tech_manual:
            sale = self.sum_tot_sale - tech_sale 
            #added by aslam to decrease preopn if no mat values
            cost = self.sum_tot_cost -tech_cost - self.pre_opn_cost
            total_manpower_cost = self.get_imp_cost() + self.get_bmn_cost()
            total_manpower_sale = self.get_imp_sale() + self.get_bmn_sale()
            result[21]= {'sale':sale,'cost':cost,'manpower_cost':total_manpower_cost,'manpower_sale':total_manpower_sale}
        
        #Added by aslam to update pre-operation cost to general (revenue tab to fix sale in)
        #Commented by Aslam to remove general product group from revenue for pre-oprn and include on other prd grps
#         if self.pre_opn_cost:
#             if result.get(21, False):
#                 result[21]['cost']= result[21]['cost'] + self.pre_opn_cost
#             else:
#                 result[21] = {'sale':0.0,'cost':self.pre_opn_cost,'manpower_cost':0.0,'manpower_sale':0.0}
            
        for val in tech_vals:
            pdt_grp_id = val.get('pdt_grp_id')
            total_sale1 = val.get('total_sale')
            total_cost1 = val.get('total_cost')
            profit = total_sale1 - total_cost1
            result_data = result.get(pdt_grp_id,{})
            if result_data:
                sale =result_data.get('sale',0.0)
                sale += total_sale1
                cost = result_data.get('cost',0.0)
                cost += total_cost1
                result_data['sale'] = sale 
                result_data['cost'] = cost 
                result_data['manpower_cost'] = total_cost1
                result_data['manpower_sale'] = total_sale1
            else:
                result[pdt_grp_id] = {'sale':total_sale1,'cost':total_cost1,'manpower_cost':total_cost1,'manpower_sale':total_sale1,'no_distribute':True}
        
        
        for key,val in result.iteritems():
            pdt_grp_id = key 
            sale = val.get('sale')
            total_sale += sale
            sale_aftr_disc = sale 
            cost = val.get('cost')
            if not val.get('no_distribute',False):
                distribute_cost += cost
            manpower_cost = val.get('manpower_cost',0.0)
            manpower_sale = val.get('manpower_sale',0.0)
            total_cost += cost
            profit = sale_aftr_disc- cost
            gp = profit + manpower_cost
            data.append({'pdt_grp_id':pdt_grp_id,'total_sale':sale,'total_cost':cost,'sale_aftr_disc':sale_aftr_disc,'profit':profit,
                         'total_gp':gp,'manpower_cost':manpower_cost,'manpower_sale':manpower_sale,'no_distribute':val.get('no_distribute',False)})
        
        if total_sale:
            for val in data:
                sale = val.get('total_sale')
                discount = disc *(sale/total_sale)
                discount = -1 * discount
                sale_aftr_disc = sale - (discount)
                cost = val.get('total_cost')
                #Modified by Aslam to add pre-operation cost to other product groups based on their cost
                pre_cost = self.pre_opn_cost
                if pre_cost:
                    pre_weight = (cost/total_cost) * pre_cost
                    val['total_cost'] = cost + pre_weight
                profit = sale_aftr_disc- val.get('total_cost')
                val['sale_aftr_disc'] = sale_aftr_disc
                val['profit'] = profit
                val['total_gp'] = profit
                
                
        if total_mat_cost:
            total_manpower_cost = self.get_imp_cost() + self.get_bmn_cost()
            total_manpower_sale =self.get_imp_sale() + self.get_bmn_sale()
#             total_manpower_cost = self.a_bim_cost + self.a_bmn_cost
            
            for val in data:
                pdt_grp_id = val.get('pdt_grp_id')
                manpower_cost =0.0
                if not val.get('no_distribute'):
                    manpower_cost = total_manpower_cost *(mat_res.get(pdt_grp_id,0.0)/(total_mat_cost or 1.0))
                    manpower_sale = total_manpower_sale * (mat_res.get(pdt_grp_id,0.0)/(total_mat_cost or 1.0))
                mp = val.get('manpower_cost',0.0)
                mp_sale = val.get('manpower_sale',0.0)
                val['manpower_cost'] = manpower_cost +mp
                val['manpower_sale'] = manpower_sale +mp_sale
                profit = val.get('profit')
                total_gp = profit + manpower_cost +mp
                val['total_gp'] = total_gp
        for val in data:
            mp = val.get('manpower_cost',0.0)
            profit = val.get('profit')
            total_gp = profit  +mp
            val['total_gp'] = total_gp
        if not data:
#             total_manpower_cost = self.get_imp_cost() + self.get_bmn_cost()
            total_manpower_cost = self.a_bim_cost + self.a_bmn_cost + self.a_bis_cost
            if total_manpower_cost and not redist_tech_manual:
                data.append({
                    'pdt_grp_id':21,
                    'manpower_cost':total_manpower_cost,
                    'manpower_sale':total_manpower_sale,
                    'total_gp':total_manpower_cost,
                    })
            if total_manpower_cost and redist_tech_manual:
                for line in self.dist_tech_line:
                    pdt_grp_id = line.pdt_grp_id.id 
                    value = line.value
                    mp_c =total_manpower_cost * (value/100.0)
                    total_gp = total_manpower_cost  * (value/100.0)
                    mp_s =total_manpower_sale * (value/100.0)
                    result[pdt_grp_id]= {'manpower_cost':mp_c,'manpower_sale':mp_s,'total_gp':total_gp}
        #Added by Aslam to reflect rebate to revenue of each product groups Mar/2022
        if self.prn_ven_reb_cost:
            for rebate_line in self.vendor_rebate_line:
                rebate_pdt_grp = rebate_line.tech_unit_id and rebate_line.tech_unit_id.id or False
                for val in data:
                    if val['pdt_grp_id'] == rebate_pdt_grp:
                        new_gp = val['total_gp'] + rebate_line.value
                        val['total_gp'] = new_gp
                      
        self.summary_weight_line.unlink()
        self.summary_weight_line = data
        
        
                
            #data[0]['total_gp'] = data[0]['total_gp'] + self.prn_ven_reb_cost
    
    def pull_branch_div(self):
        if not self.od_branch_id:
            self.od_branch_id = self.lead_id and self.lead_id.od_branch_id and self.lead_id.od_branch_id.id or False
        if not self.od_division_id:
            self.od_division_id = self.lead_id and self.lead_id.od_division_id and self.lead_id.od_division_id.id or False
    
    def update_submit_date(self):
        if self.status == 'active' and self.submitted_date:
            self.lead_id.finished_on_7 =self.submitted_date[:10]
    
    def calculate_section_sale(self):
        for mat_line in self.cost_section_line:
            sale1 = float(sum([ml.line_price for ml in self.mat_main_pro_line if ml.section_id.id==mat_line.id]))
            cost1 = float(sum([ml.line_cost_local_currency for ml in self.mat_main_pro_line if ml.section_id.id==mat_line.id]))
            mat_line.write({'sale': sale1, 'cost': cost1})
            
        for opt_line in self.cost_section_option_line:
            sale2 = float(sum([ol.line_price for ol in self.mat_optional_item_line if ol.opt_section_id.id==opt_line.id]))
            cost2 = float(sum([ol.line_cost_local_currency for ol in self.mat_optional_item_line if ol.opt_section_id.id==opt_line.id]))
            opt_line.write({'sale': sale2, 'cost': cost2})
        
        for trn_line in self.cost_section_trn_line:
            sale3 = float(sum([tl.line_price for tl in self.trn_customer_training_line if tl.trn_section_id.id==trn_line.id]))
            cost3 = float(sum([tl.line_cost_local_currency for tl in self.trn_customer_training_line if tl.trn_section_id.id==trn_line.id]))
            trn_line.write({'sale': sale3, 'cost': cost3})
    
    @api.one
    def update_cost_sheet(self):
        self.recalculate()
        self.compute_value()
        self.compute_value_optional()
        self.summarize()
        self.log_calculate_cost()
        self.update_bim_summary()
        self.calculate_bim_analy()
        self.calculate_total_manpower_cost()
        self.update_opportunity()
        self.generate_group_weight()
        self.generate_tech_mp_products()
        self.generate_brand_weight()
        self.generate_impl_weight()
        self.generate_info_sec_weight()
        self.generate_amc_weight()
        self.generate_om_weight()
        self.generate_extra_weight()
        self.summarize_revenue()
        self.generate_summary_weight()
        self.pull_branch_div()
        self._check_full_tech()
        self.calculate_section_sale()
#         self.update_submit_date()
    
    def price_fix_line(self,line_id,xno=1):
        for line in line_id:
            unit_price = line.unit_price
            if xno ==2:
                unit_price = line.unit_price2
            
#             if not line.new_unit_price:
            line['new_unit_price'] = unit_price
            line['temp_unit_price'] = unit_price 
            line['fixed'] = True
    
    def price_unfix_line(self,line_id):
        for line in line_id:
            unit_price = line.new_unit_price
            line['temp_unit_price'] = unit_price 
            line['fixed'] = False
            
    
    @api.one
    def btn_freez_price(self):
        price_fixed = self.price_fixed 
        if not price_fixed:
            
            self.bim_log_price_fixed = round(self.bim_log_price)
            self.price_fix_line(self.mat_main_pro_line)
            self.price_fix_line(self.mat_extra_expense_line,2)
            self.price_fix_line(self.mat_optional_item_line )
            self.price_fix_line(self.trn_customer_training_line)
            self.price_fix_line(self.trn_customer_training_extra_expense_line, 2)
            self.price_fix_line(self.implimentation_extra_expense_line)
            self.price_fix_line(self.manpower_manual_line)
            self.price_fix_line(self.bim_implementation_code_line)
            self.price_fix_line(self.oim_implimentation_price_line)
            self.price_fix_line(self.oim_extra_expenses_line)
            self.price_fix_line(self.bmn_it_preventive_line)
            self.price_fix_line(self.bmn_it_remedial_line)
            self.price_fix_line(self.bmn_spareparts_beta_it_maintenance_line)
            self.price_fix_line(self.bmn_beta_it_maintenance_extra_expense_line)
            self.price_fix_line(self.omn_out_preventive_maintenance_line)
            self.price_fix_line(self.omn_out_remedial_maintenance_line)
            self.price_fix_line(self.omn_spare_parts_line)
            self.price_fix_line(self.omn_maintenance_extra_expense_line)
            self.price_fix_line(self.om_residenteng_line)
            self.price_fix_line(self.om_eqpmentreq_line)
            self.price_fix_line(self.om_extra_line)
            self.price_fix_line(self.imp_tech_line)
            self.price_fix_line(self.amc_tech_line)
            self.price_fix_line(self.om_tech_line)
            self.price_fix_line(self.ps_vendor_line)
            self.price_fix_line(self.info_sec_tech_line)
            self.price_fix_line(self.info_sec_extra_expense_line)
            self.price_fix_line(self.info_sec_subcontractor_line)
            self.price_fix_line(self.info_sec_vendor_line)
            self.write({'price_fixed':True})
            self.update_cost_sheet()
    
    @api.one
    def btn_unfreez_price(self):
        
        price_fixed = self.price_fixed 
        if price_fixed:
            self.bim_log_price_fixed =0.0
            self.price_unfix_line(self.mat_main_pro_line)
            self.price_unfix_line(self.mat_extra_expense_line)
            self.price_unfix_line(self.mat_optional_item_line )
            self.price_unfix_line(self.trn_customer_training_line)
            self.price_unfix_line(self.trn_customer_training_extra_expense_line)
            self.price_unfix_line(self.implimentation_extra_expense_line)
            self.price_unfix_line(self.manpower_manual_line)
            self.price_unfix_line(self.bim_implementation_code_line)
            self.price_unfix_line(self.oim_implimentation_price_line)
            self.price_unfix_line(self.oim_extra_expenses_line)
            self.price_unfix_line(self.bmn_it_preventive_line)
            self.price_unfix_line(self.bmn_it_remedial_line)
            self.price_unfix_line(self.bmn_spareparts_beta_it_maintenance_line)
            self.price_unfix_line(self.bmn_beta_it_maintenance_extra_expense_line)
            self.price_unfix_line(self.omn_out_preventive_maintenance_line)
            self.price_unfix_line(self.omn_out_remedial_maintenance_line)
            self.price_unfix_line(self.omn_spare_parts_line)
            self.price_unfix_line(self.omn_maintenance_extra_expense_line)
            self.price_unfix_line(self.om_residenteng_line)
            self.price_unfix_line(self.om_eqpmentreq_line)
            self.price_unfix_line(self.om_extra_line)
            self.price_unfix_line(self.imp_tech_line)
            self.price_unfix_line(self.amc_tech_line)
            self.price_unfix_line(self.om_tech_line)
            self.price_unfix_line(self.ps_vendor_line)
            self.price_unfix_line(self.info_sec_tech_line)
            self.price_unfix_line(self.info_sec_extra_expense_line)
            self.price_unfix_line(self.info_sec_subcontractor_line)
            self.price_unfix_line(self.info_sec_vendor_line)
            self.write({'price_fixed':False})
            self.update_cost_sheet()
            
    
    
    
    
        
    
    def check_open_req_count(self):
        if self.open_req_count >4:
            raise Warning("​You are Exceeded 5 times Open, You Cannot Open Further​ !")
    
    def update_open_req_count(self):
        count =self.open_req_count 
        self.write({'open_req_count':count+1})
    
    @api.one
    def btn_req_for_modification(self):
        #btn to request modification in waiting po State / for the purpose without returning the costsheet
        self.check_open_req_count()
        self.sam_req_for_modify=True
        self.od_send_mail('cst_sheet_modification_req_mail')
        self.change_date = str(datetime.now())
        self.date_log_history_line = [{'name':'Request for Modification (Waiting PO)','date':str(datetime.now())}]
    
    
    @api.one
    def btn_open_modification(self):
        if self.sam_req_for_modify:
            #btn to open modification in waiting po State / for the purpose without returning the costsheet
            self.update_open_req_count()
            self.state ='waiting_po_open'
            self.od_send_mail('cst_sheet_modification_open_mail')
            self.change_date = str(datetime.now())
            self.date_log_history_line = [{'name':'Costsheet Opened for Modification in Waiting PO','date':str(datetime.now())}]
            self.sam_req_for_modify = False
        else:
            raise Warning("Account Manager do not requested you to Open, Cannot Open without Request")

    
    @api.one
    def btn_finished_modification(self):
        #btn to open modification in waiting po State / for the purpose without returning the costsheet
        
        self.od_send_mail('cst_sheet_modification_finished_mail')
        self.change_date = str(datetime.now())
        self.date_log_history_line = [{'name':'Waiting PO - Finished Modification','date':str(datetime.now())}]
        
    
    @api.one
    def btn_locked_modification(self):
        #btn to open modification in waiting po State / for the purpose without returning the costsheet
        approved_gp = self.approved_gp
        current_gp = self.total_gp_percent
        gp_approved_state = self.gp_approval_state
        if gp_approved_state=='approved' and current_gp < approved_gp:
            res = self.check_gp_approval()
        else:
            self.state ='waiting_po'
            self.change_date = str(datetime.now())
            self.date_log_history_line = [{'name':'Waiting PO Locked Modification','date':str(datetime.now())}]
    
    
    
    
    def line_update_tax_id(self,line_ids):
        for line in line_ids:
            tax_id = line.group and line.group.tax_id and line.group.tax_id.id or False
            line.tax_id = tax_id
    
    def line_update_tax_id_1(self,line_ids):
        for line in line_ids:
            tax_id = line.group_id and line.group_id.tax_id and line.group_id.tax_id.id or False
            line.tax_id = tax_id
    
    def line_update_tax_id_2(self,line_ids):
        for line in line_ids:
            tax_id = line.group2 and line.group2.tax_id and line.group2.tax_id.id or False
            line.tax_id = tax_id
    
    def line_update_tax_id_costgroup(self,line_ids):
        for line in line_ids:
            tax_id = line.cost_group_id and line.cost_group_id.tax_id and line.cost_group_id.tax_id.id or False
            line.tax_id = tax_id

    def update_bim_tax_id(self):
        self.bim_tax_id = self.bim_log_group and self.bim_log_group.tax_id and self.bim_log_group.tax_id.id or False
    @api.one 
    def update_vat(self):
        self.line_update_tax_id(self.mat_main_pro_line)
        self.line_update_tax_id_1(self.mat_optional_item_line)
        self.line_update_tax_id_2(self.mat_extra_expense_line)
        
        self.line_update_tax_id(self.trn_customer_training_line)
        self.line_update_tax_id_2(self.trn_customer_training_extra_expense_line)
        
        self.line_update_tax_id(self.implimentation_extra_expense_line)
        self.line_update_tax_id_costgroup(self.manpower_manual_line)
        self.line_update_tax_id(self.bim_implementation_code_line)
        self.line_update_tax_id(self.oim_implimentation_price_line)
        self.line_update_tax_id(self.oim_extra_expenses_line)
        
        self.line_update_tax_id(self.bmn_it_preventive_line)
        self.line_update_tax_id(self.bmn_it_remedial_line)
        self.line_update_tax_id(self.bmn_spareparts_beta_it_maintenance_line)
        self.line_update_tax_id(self.bmn_beta_it_maintenance_extra_expense_line)
        self.line_update_tax_id(self.omn_out_preventive_maintenance_line)
        self.line_update_tax_id(self.omn_out_remedial_maintenance_line)
        self.line_update_tax_id(self.omn_spare_parts_line)
        self.line_update_tax_id(self.omn_maintenance_extra_expense_line)
        
        self.line_update_tax_id(self.om_residenteng_line)
        self.line_update_tax_id(self.om_eqpmentreq_line)
        self.line_update_tax_id(self.om_extra_line)
        
        self.update_bim_tax_id()
       
    
    
    
    
    @api.one
    def update_opportunity(self):
        if self.status == 'active':
            lead_id = self.lead_id and self.lead_id.id or False
            manpower_cost =self.calculate_total_manpower_cost()
            new_profit = self.sum_profit + manpower_cost
            sale = self.sum_total_sale
            profit_per =0.0
            if sale:
                profit_per = (new_profit/sale) * 100.0

            if lead_id:
                lead = self.lead_id
                vals ={
                      'planned_revenue':self.sum_total_sale,
                      'od_costsheet_manpower_cost':manpower_cost,
                      'od_costsheet_new_profit':new_profit,
                      'od_costsheet_new_profit_percent':profit_per,
                       }
                lead.write(vals)


    def get_min_max_manpower_percent(self,param):
        parameter_obj = self.env['ir.config_parameter']
        if self.is_saudi_comp():
            param = param + '_ksa'
        key =[('key', '=', param)]
        param_obj = parameter_obj.search(key)
        if not param_obj:
            raise Warning(_('Settings Warning!'),_('NoParameter Not defined\nconfig it in System Parameters with %s'%param))
        result = param_obj.value
        return result
    
    def get_mat_tot_cost_without_ren(self,line_id):
        tot_cost =0.0
        for line in line_id:
            
            if not line.ren:
                tot_cost +=  line.line_cost_local_currency
        return tot_cost
    
    @api.one
    def log_calculate_cost(self):
        cost =0.0
        bim_extra_exp=self.material_extra_cost(self.implimentation_extra_expense_line)
        bis_extra_exp=self.material_extra_cost(self.info_sec_extra_expense_line)
        mat_tot_cost = self.get_mat_tot_cost_without_ren(self.mat_main_pro_line)
        total_cost = mat_tot_cost + self.trn_tot_cost + self.oim_tot_cost + self.ois_tot_cost + bim_extra_exp + bis_extra_exp
        cost_factor = self.company_id.od_cost_factor
        if not cost_factor:
            raise Warning('Manpower Implementation Cost Factor Not Set in Your Company ,Please Configure It First')

        log_factor = self.company_id.od_log_factor
        if not log_factor:
            raise Warning('Manpower Implementation Log Factor Not Set in Your Company ,Please Configure It First')
        cost_fact = cost_factor/100
        cost_perc_value = 0.0
        if total_cost:
            cost_perc_value = (exp(log10(log_factor/(total_cost)))*cost_fact)
        cost_perc_min_val = float(self.get_min_max_manpower_percent('od_beta_it_min_manpower_percentage'))/100
        cost_perc_max_val = float(self.get_min_max_manpower_percent('od_beta_it_max_manpower_percentage'))/100
        if cost_perc_value > cost_perc_max_val :
            cost_perc_value =  cost_perc_max_val
        if cost_perc_value < cost_perc_min_val:
            cost_perc_value = cost_perc_min_val
        if total_cost:
            if self.bim_full_outsource:
                cost = (cost_perc_value * (total_cost)/2)
            else:
                cost = (cost_perc_value * total_cost)
        self.bim_log_cost = cost
    @api.one
    def update_bim_summary(self):
        bim_total_cost = self.bim_tot_cost1
        bim_tot_sale = self.bim_tot_sale1
        imp_cost = self.line_single(self.bim_implementation_code_line)
        
        sp_disc = self.special_discount
        if self.bim_log_select:
            bim_total_cost += self.bim_log_cost
            bim_tot_sale += self.bim_log_price
        if self.bim_imp_select:
            bim_tot_sale += imp_cost.get('tot_sale')
            bim_total_cost += imp_cost.get('tot_cost')
        if self.included_bim_in_quotation:
            self.bim_tot_cost = bim_total_cost
            self.bim_tot_sale = bim_tot_sale
        else:
            self.bim_tot_cost = 0
            self.bim_tot_sale = 0
            
        self.bim_tot_cost1 = bim_total_cost
        self.bim_tot_sale1 = bim_tot_sale
        
        profit = bim_tot_sale - bim_total_cost
        profit_per = 0.0
        
        
        
        
        
        
        if bim_tot_sale:
            profit_per = (profit/bim_tot_sale) * 100
        if self.included_bim_in_quotation:
            self.bim_profit = profit
            self.bim_profit_percentage = profit_per
        else:
            self.bim_profit = 0
            self.bim_profit_percentage = 0
        
        
        
        sheet_total =self.sum_tot_sale or 1.0 
        disc = (bim_tot_sale/sheet_total) * abs(sp_disc)
        disc_sale = bim_tot_sale - disc
        
        
        self.bim_tot_sale1_ds = disc_sale
        profit = disc_sale - bim_total_cost
        self.bim_profit1 = profit
        self.bim_profit_percentage1 = (profit/(disc_sale or 1.0))*100.0
        
        #Added by Aslam : Rebate value distribution to each tabs 
#         tot_rebate = self.prn_ven_reb_cost
#         summary_tot_cost1 = self.sum_tot_cost
#         bim_rebate = (bim_total_cost/summary_tot_cost1) * abs(tot_rebate)
#         self.bim_rebate = bim_rebate
#         bim_profit_with_rebate =  profit + bim_rebate
#         self.bim_profit_with_rebate = bim_profit_with_rebate
#         self.bim_profit_with_rebate_perc = (bim_profit_with_rebate/(disc_sale or 1.0)) *100.0
        
    @api.one
    def fill_renewal(self):
        self.fill_line()
        self.fill_line_optional()
        self.ren_filled = True

    @api.one
    def order_seq(self,lines):
        count = 0
        for line in lines:
            count += 1
            line.item = count
            line.item_int = count

    @api.one
    def mat_order(self):
        self.order_seq(self.mat_main_pro_line)
        self.order_seq(self.mat_optional_item_line)
        self.order_seq(self.mat_extra_expense_line)
    @api.one
    def trn_order(self):
        self.order_seq(self.trn_customer_training_line)
        self.order_seq(self.trn_customer_training_extra_expense_line)
    @api.one
    def reorder_seq(self):

        count = 0
        if self.env.context.get('optional'):
            line_id = self.ren_optional_item_line
        else:
            line_id = self.ren_main_pro_line
        for ren in line_id:
            count += 1
            ren.item = count
            ren.item_int = count
    @api.one
    def fill_line(self):
        vals = []
        for mat in self.mat_main_pro_line:
            if mat.ren:
                qty = int(mat.qty)
                for i in range(qty):
                    print i
                    vals.append([0,0,{
                                 'cost_sheet_id':self.id,
                                 'manufacture_id':mat.manufacture_id.id,
                                 'renewal_package_no':mat.part_no.id
                                 }])
        self.ren_main_pro_line =  vals

    @api.one
    def fill_line_optional(self):
        vals = []
        for mat in self.mat_optional_item_line:
            if mat.ren:
                qty = int(mat.qty)
                for i in range(qty):
                    print i
                    vals.append([0,0,{
                                 'cost_sheet_id':self.id,
                                 'manufacture_id':mat.manufacture_id.id,
                                 'renewal_package_no':mat.part_no.id
                                 }])
        self.ren_optional_item_line =  vals


    def line_two(self,line_id,lines):
        tot_sale =0.0
        tot_cost =0.0
        for line1 in lines:
            tot_cost += line1.line_cost
            tot_sale += line1.line_price
        for line in line_id:
            tot_sale += line.line_price
            tot_cost += line.line_cost_local_currency

        res={
             'tot_sale':tot_sale or 0.0,
             'tot_cost':tot_cost or 0.0,
             }
        return res


    
    def get_vat_total(self,line_id):
        return sum([line.vat_value for line in line_id])
    def get_vat_total2(self,line_id):
        return sum([line.vat_value2 for line in line_id])
    
    def line_summarize(self,line_id):
        tot_sale =0.0
        tot_cost =0.0
        for line in line_id:
            tot_sale += line.line_price
            tot_cost += line.line_cost_local_currency
        res = {
                'tot_sale':tot_sale or 0.0,
                'tot_cost':tot_cost or 0.0,
             }


        return res
    def line_summarize_optional(self,line_id):
        tot_sale =0.0
        tot_cost =0.0
        for line in line_id:
            tot_sale += line.line_price
            tot_cost += line.line_cost_local_currency
        res={
             'tot_sale':tot_sale or 0.0,
             'tot_cost':tot_cost or 0.0,
             }


        return res

    def line_capture(self,first_line,second_line):
        tot_sale =0.0
        tot_cost =0.0
        for line in first_line:
            tot_cost += line.line_cost
        for line2 in second_line:
            tot_cost += line2.line_cost
            tot_sale += line2.line_price
        res = {
             'tot_sale':tot_sale or 0.0,
             'tot_cost':tot_cost or 0.0,
               }
        return res


    def line_single(self,lines):
        tot_sale =0.0
        tot_cost =0.0
        for line2 in lines:
            tot_cost += line2.line_cost
            tot_sale += line2.line_price
        res = {
             'tot_sale':tot_sale or 0.0,
             'tot_cost':tot_cost or 0.0,
               }
        return res

    def material_extra_cost(self,line_id):
        tot_cost =0.0
        for line in line_id:
            tot_cost += line.line_cost
        return tot_cost

    def material_extra_cost2(self,line_id):
        tot_cost =0.0
        for line in line_id:
            tot_cost += line.line_cost_local
        return tot_cost

    def material_extra_sale(self,line_id):
        tot_sale =0.0
        for line in line_id:
            tot_sale += line.line_price2
        return tot_sale


    @api.one
    def summarize(self):
        mat_res=self.line_summarize(self.mat_main_pro_line)
        mat_extra_cost = self.material_extra_cost2(self.mat_extra_expense_line) or 0.0
        mat_extra_sale = self.material_extra_sale(self.mat_extra_expense_line) or 0.0
        total_sale = mat_res.get('tot_sale') + mat_extra_sale
        total_cost = mat_res.get('tot_cost') + mat_extra_cost
        profit =  round(total_sale) - round(total_cost)
       
        profit_per =0.0
#         mat_vat = self.get_vat_total(self.mat_main_pro_line) + self.get_vat_total(self.mat_optional_item_line) + self.get_vat_total(self.mat_extra_expense_line)
        mat_main_vat = self.get_vat_total(self.mat_main_pro_line)  + self.get_vat_total2(self.mat_extra_expense_line)
        self.mat_vat1 = mat_main_vat
        sheet_total =self.sum_tot_sale or 1.0
        sp_disc = self.special_discount
        tot_rebate = self.prn_ven_reb_cost
        
        if total_sale:
            profit_per = (profit/total_sale) * 100

        if self.included_in_quotation:
            self.mat_tot_sale = total_sale
            self.mat_tot_cost = total_cost
            self.mat_profit = profit
            self.mat_profit_percentage = profit_per
            self.mat_vat = mat_main_vat
        else:
            self.mat_tot_sale = 0
            self.mat_tot_cost = 0
            self.mat_profit = 0
            self.mat_vat =0.0
            self.mat_profit_percentage = 0

        #duplicate vals
        self.mat_tot_sale1 = total_sale
        self.mat_tot_cost1 = total_cost
        
        disc = (total_sale/sheet_total) * abs(sp_disc)
        disc_sale = total_sale - disc
        material_disc_sale = disc_sale
        self.mat_tot_sale1_ds = disc_sale
        profit = disc_sale - total_cost
        self.mat_profit1 = profit
        self.mat_profit_percentage1 = (profit/(disc_sale or 1.0)) *100.0
        
       
        
        
        mat_optional = self.line_summarize_optional(self.mat_optional_item_line)
        opt_total_sale = mat_optional.get('tot_sale')
        opt_total_cost = mat_optional.get('tot_cost')
        opt_profit =  opt_total_sale - opt_total_cost
        opt_profit_per = 0.0
        opt_mat_vat = self.get_vat_total(self.mat_optional_item_line)
        if opt_total_sale:
            opt_profit_per = (opt_profit/opt_total_sale) * 100

        if self.included_in_quotation:
            self.mat_tot_sale_opt = opt_total_sale
            self.mat_tot_cost_opt = opt_total_cost
            self.mat_profit_opt = opt_profit
            self.mat_profit_percentage_opt = opt_profit_per
            self.mat_vat_opt = opt_mat_vat
        else:
            self.mat_tot_sale_opt = 0
            self.mat_tot_cost_opt = 0
            self.mat_profit_opt = 0
            self.mat_profit_percentage_opt = 0
            self.mat_vat_opt = 0.0

        trn_res = self.line_summarize(self.trn_customer_training_line)
        trn_extra =self.material_extra_cost2(self.trn_customer_training_extra_expense_line) or 0.0
        trn_extra_sale = self.material_extra_sale(self.trn_customer_training_extra_expense_line) or 0.0
        trn_total_sale = trn_res.get('tot_sale') + trn_extra_sale
        trn_total_cost = trn_res.get('tot_cost') + trn_extra
        trn_profit =  trn_total_sale - trn_total_cost
        trn_profit_per =0.0
        trn_vat = self.get_vat_total(self.trn_customer_training_line) + self.get_vat_total2(self.trn_customer_training_extra_expense_line) 

        if trn_total_sale:
            trn_profit_per = (trn_profit/trn_total_sale) * 100
        if self.included_trn_in_quotation:
            self.trn_tot_sale = trn_total_sale
            self.trn_tot_cost = trn_total_cost
            self.trn_profit = trn_profit
            self.trn_profit_percentage = trn_profit_per
            self.trn_vat = trn_vat
        else:
            self.trn_tot_sale = 0
            self.trn_tot_cost = 0
            self.trn_profit = 0
            self.trn_profit_percentage = 0
            self.trn_vat =0
        self.trn_tot_sale1 = trn_total_sale
        self.trn_tot_cost1 = trn_total_cost
        self.trn_vat1 =trn_vat
         
        disc = (trn_total_sale/sheet_total) * abs(sp_disc)
        disc_sale = trn_total_sale - disc 
        self.trn_tot_sale1_ds = disc_sale 
        trn_profit = disc_sale - trn_total_cost
        self.trn_profit1 = trn_profit        
        self.trn_profit_percentage1 = (trn_profit/(disc_sale or 1.0)) *100.0
        
        #Added by Aslam : Rebate value distribution to MAT tab ,
        mat_trn_cost = total_cost
        mat_rebate = (total_cost/(mat_trn_cost or 1.0)) * abs(tot_rebate)
        self.mat_rebate = mat_rebate
        mat_profit_with_rebate =  profit + mat_rebate
        self.mat_profit_with_rebate = mat_profit_with_rebate
        mat_profit_with_rebate_perc = (mat_profit_with_rebate/(material_disc_sale or 1.0)) *100.0
        self.mat_profit_with_rebate_perc = mat_profit_with_rebate_perc
        
        #Added by Aslam : Rebate value distribution to TRN tab (Removed by Aslam) 
        trn_rebate = 0.0
        self.trn_rebate = trn_rebate
        trn_profit_with_rebate =  trn_profit + trn_rebate
        self.trn_profit_with_rebate = trn_profit_with_rebate
        self.trn_profit_with_rebate_perc = (trn_profit_with_rebate/(disc_sale or 1.0)) *100.0
        
        
        bim_res = self.line_single(self.manpower_manual_line)
        bim_extra = self.line_single(self.implimentation_extra_expense_line)
        imp_tech_res=self.line_summarize(self.imp_tech_line)
        bim_total_sale = bim_res.get('tot_sale',0.0) + bim_extra.get('tot_sale',0.0) + imp_tech_res.get('tot_sale',0.0)
        bim_total_cost = bim_res.get('tot_cost',0.0) + bim_extra.get('tot_cost',0.0) + imp_tech_res.get('tot_cost',0.0)
        bim_profit =  bim_total_sale - bim_total_cost
        bim_profit_per = 0.0
        bim_vat = self.get_vat_total(self.imp_tech_line) +self.get_vat_total(self.implimentation_extra_expense_line) + self.get_vat_total(self.manpower_manual_line) + self.get_vat_total(self.bim_implementation_code_line) 
        if self.bim_log_select:
            bim_vat +=self.bim_log_vat_value
        if bim_total_sale:
            bim_profit_per = (bim_profit/bim_total_sale) * 100
        if self.included_bim_in_quotation:
            self.bim_tot_sale = bim_total_sale
            self.bim_tot_cost = bim_total_cost
            self.bim_profit = bim_profit
            self.bim_profit_percentage = bim_profit_per
            self.bim_vat = bim_vat
        else:
            self.bim_tot_sale = 0
            self.bim_tot_cost = 0
            self.bim_profit = 0
            self.bim_profit_percentage = 0
            self.bim_vat =0
        
        self.bim_tot_sale1 = bim_total_sale
        self.bim_tot_cost1 = bim_total_cost
        
        
        self.bim_vat1 = bim_vat
        
        disc = (bim_total_sale/sheet_total) * abs(sp_disc)
        disc_sale = bim_total_sale - disc
        
        self.bim_tot_sale1_ds = disc_sale    
        
        bim_profit = disc_sale -  bim_total_cost
        self.bim_profit1 = bim_profit
        self.bim_profit_percentage1 = (bim_profit/(disc_sale or 1.0)) *100.0
        
#         #Added by Aslam : Rebate value distribution to each tabs 
#         bim_rebate = (bim_total_cost/sheet_tot_cost) * abs(tot_rebate)
#         self.bim_rebate = bim_rebate
#         bim_profit_with_rebate =  bim_profit + bim_rebate
#         self.bim_profit_with_rebate = bim_profit_with_rebate
#         self.bim_profit_with_rebate_perc = (bim_profit_with_rebate/(disc_sale or 1.0)) *100.0

        oim_res = self.line_single(self.oim_implimentation_price_line)
        oim_extra = self.line_single(self.oim_extra_expenses_line)
        oim_extra_ps = self.line_summarize(self.ps_vendor_line)
        oim_total_sale = oim_res.get('tot_sale',0.0) + oim_extra.get('tot_sale',0.0) + oim_extra_ps.get('tot_sale',0.0)
        oim_total_cost = oim_res.get('tot_cost') + oim_extra.get('tot_cost',0.0) + oim_extra_ps.get('tot_cost',0.0)
        oim_profit =  oim_total_sale - oim_total_cost
        oim_profit_per = 0.0
        oim_vat = self.get_vat_total(self.oim_implimentation_price_line) +  self.get_vat_total(self.oim_extra_expenses_line) + self.get_vat_total(self.ps_vendor_line) 
        
        if oim_total_sale:
            oim_profit_per = (oim_profit/oim_total_sale) * 100
        if self.included_bim_in_quotation:
            self.oim_tot_sale = oim_total_sale
            self.oim_tot_cost = oim_total_cost
            self.oim_profit = oim_profit
            self.oim_profit_percentage =  oim_profit_per
            self.oim_vat = oim_vat
        else:
            self.oim_tot_sale = 0
            self.oim_tot_cost = 0
            self.oim_profit = 0
            self.oim_profit_percentage =  0
            self.oim_vat =0

        self.oim_tot_sale1 = oim_total_sale
        self.oim_tot_cost1 = oim_total_cost
        
        
        self.oim_vat1 = oim_vat
        
        disc = (oim_total_sale/sheet_total) * abs(sp_disc)
        disc_sale = oim_total_sale - disc 
        self.oim_tot_sale1_ds = disc_sale    
        oim_profit = disc_sale - oim_total_cost
        self.oim_profit1 = oim_profit
        self.oim_profit_percentage1 =  (oim_profit/(disc_sale or 1.0)) *100.0
        
        #beta info sec new code starting

        bis_extra = self.line_single(self.info_sec_extra_expense_line)
        info_sec_tech_res=self.line_summarize(self.info_sec_tech_line)
        bis_total_sale = bis_extra.get('tot_sale',0.0) + info_sec_tech_res.get('tot_sale',0.0)
        bis_total_cost = bis_extra.get('tot_cost',0.0) + info_sec_tech_res.get('tot_cost',0.0)
        bis_profit =  bis_total_sale - bis_total_cost
        bis_profit_per = 0.0
        bis_vat = self.get_vat_total(self.info_sec_tech_line) +self.get_vat_total(self.info_sec_extra_expense_line)
        if bis_total_sale:
            bis_profit_per = (bis_profit/bis_total_sale) * 100
        if self.included_info_sec_in_quotation:
            self.bis_tot_sale = bis_total_sale
            self.bis_tot_cost = bis_total_cost
            self.bis_profit = bis_profit
            self.bis_profit_percentage = bis_profit_per
            self.bis_vat = bis_vat
        else:
            self.bis_tot_sale = 0
            self.bis_tot_cost = 0
            self.bis_profit = 0
            self.bis_profit_percentage = 0
            self.bis_vat =0
        
        self.bis_tot_sale1 = bis_total_sale
        self.bis_tot_cost1 = bis_total_cost
        
        
        self.bis_vat1 = bis_vat
        
        disc = (bis_total_sale/sheet_total) * abs(sp_disc)
        disc_sale = bis_total_sale - disc
        self.bis_tot_sale1_ds = disc_sale    
        
        bis_profit = disc_sale -  bis_total_cost
        self.bis_profit1 = bis_profit
        self.bis_profit_percentage1 = (bis_profit/(disc_sale or 1.0)) *100.0
        
        #OIS 

        ois_extra = self.line_single(self.info_sec_subcontractor_line)
        ois_extra_ps = self.line_summarize(self.info_sec_vendor_line)
        ois_total_sale = ois_extra.get('tot_sale',0.0) + ois_extra_ps.get('tot_sale',0.0)
        ois_total_cost = ois_extra.get('tot_cost',0.0) + ois_extra_ps.get('tot_cost',0.0)
        ois_profit =  ois_total_sale - ois_total_cost
        ois_profit_per = 0.0
        ois_vat = self.get_vat_total(self.info_sec_subcontractor_line) + self.get_vat_total(self.info_sec_vendor_line)
        
        if ois_total_sale:
            ois_profit_per = (ois_profit/ois_total_sale) * 100
        if self.included_info_sec_in_quotation:
            self.ois_tot_sale = ois_total_sale
            self.ois_tot_cost = ois_total_cost
            self.ois_profit = ois_profit
            self.ois_profit_percentage =  ois_profit_per
            self.ois_vat = ois_vat
        else:
            self.ois_tot_sale = 0
            self.ois_tot_cost = 0
            self.ois_profit = 0
            self.ois_profit_percentage =  0
            self.ois_vat =0

        self.ois_tot_sale1 = ois_total_sale
        self.ois_tot_cost1 = ois_total_cost
        
        
        self.ois_vat1 = ois_vat
        
        disc = (ois_total_sale/sheet_total) * abs(sp_disc)
        disc_sale = ois_total_sale - disc 
        self.ois_tot_sale1_ds = disc_sale    
        ois_profit = disc_sale - ois_total_cost
        self.ois_profit1 = ois_profit
        self.ois_profit_percentage1 =  (ois_profit/(disc_sale or 1.0)) *100.0
        
#         #Added by Aslam : Rebate value distribution to each tabs 
#         oim_rebate = (oim_total_cost/sheet_tot_cost) * abs(tot_rebate)
#         self.oim_rebate = oim_rebate
#         oim_profit_with_rebate =  oim_profit + oim_rebate
#         self.oim_profit_with_rebate = oim_profit_with_rebate
#         self.oim_profit_with_rebate_perc = (oim_profit_with_rebate/(disc_sale or 1.0)) *100.0

        bmn_res = self.line_single(self.bmn_it_preventive_line)
        bmn_rem = self.line_single(self.bmn_it_remedial_line)
        bmn_tech_res = self.line_summarize(self.amc_tech_line)
        
        bmn_ext = self.line_two(self.bmn_spareparts_beta_it_maintenance_line, self.bmn_beta_it_maintenance_extra_expense_line)
        bmn_total_sale = bmn_res.get('tot_sale',0.0) + bmn_rem.get('tot_sale',0.0) + bmn_ext.get('tot_sale',0.0) + bmn_tech_res.get('tot_sale',0.0)
        bmn_total_cost = bmn_res.get('tot_cost') + bmn_rem.get('tot_cost',0.0) + bmn_ext.get('tot_cost',0.0) + bmn_tech_res.get('tot_cost',0.0)
        bmn_profit =  bmn_total_sale - bmn_total_cost
        bmn_profit_per = 0.0
        bmn_vat = self.get_vat_total(self.amc_tech_line) + self.get_vat_total(self.bmn_it_preventive_line) + self.get_vat_total(self.bmn_it_remedial_line) + self.get_vat_total(self.bmn_spareparts_beta_it_maintenance_line) + self.get_vat_total(self.bmn_beta_it_maintenance_extra_expense_line)

        if bmn_total_sale:
            bmn_profit_per = (bmn_profit/bmn_total_sale) * 100

        if self.included_bmn_in_quotation:
            self.bmn_tot_sale = bmn_total_sale
            self.bmn_tot_cost = bmn_total_cost
            self.bmn_profit = bmn_profit
            self.bmn_profit_percentage = bmn_profit_per
            self.bmn_vat = bmn_vat
        else:
            self.bmn_tot_sale = 0
            self.bmn_tot_cost = 0
            self.bmn_profit = 0
            self.bmn_profit_percentage = 0
            self.bmn_vat =0

        self.bmn_tot_sale1 = bmn_total_sale
        self.bmn_tot_cost1 = bmn_total_cost
        
        
        self.bmn_vat1 = bmn_vat
        
         
        disc = (bmn_total_sale/sheet_total) * abs(sp_disc)
        disc_sale = bmn_total_sale - disc 
        self.bmn_tot_sale1_ds = disc_sale    
        bmn_profit = disc_sale - bmn_total_cost
        self.bmn_profit1 = bmn_profit
        self.bmn_profit_percentage1 = (bmn_profit/(disc_sale or 1.0)) *100.0
        
#         #Added by Aslam : Rebate value distribution to each tabs 
#         bmn_rebate = (bmn_total_cost/sheet_tot_cost) * abs(tot_rebate)
#         self.bmn_rebate = bmn_rebate
#         bmn_profit_with_rebate =  bmn_profit + bmn_rebate
#         self.bmn_profit_with_rebate = bmn_profit_with_rebate
#         self.bmn_profit_with_rebate_perc = (bmn_profit_with_rebate/(disc_sale or 1.0)) *100.0
        
        omn_res = self.line_single(self.omn_out_preventive_maintenance_line)
        omn_res_rm = self.line_single(self.omn_out_remedial_maintenance_line)
        omn_extra = self.line_two(self.omn_spare_parts_line,self.omn_maintenance_extra_expense_line)
        omn_total_sale = omn_res.get('tot_sale',0.0) + omn_res_rm.get('tot_sale',0.0) + omn_extra.get('tot_sale',0.0)
        omn_total_cost = omn_res.get('tot_cost',0.0) + omn_res_rm.get('tot_cost',0.0) + omn_extra.get('tot_cost',0.0)
        omn_profit =  omn_total_sale - omn_total_cost
        omn_profit_per = 0.0
        omn_vat = self.get_vat_total(self.omn_out_preventive_maintenance_line) + self.get_vat_total(self.omn_out_remedial_maintenance_line) + self.get_vat_total(self.omn_spare_parts_line) + self.get_vat_total(self.omn_maintenance_extra_expense_line)

        if omn_total_sale:
            omn_profit_per = (omn_profit/omn_total_sale) * 100
        if self.included_bmn_in_quotation:
            self.omn_tot_sale = omn_total_sale
            self.omn_tot_cost = omn_total_cost
            self.omn_profit = omn_profit
            self.omn_profit_percentage = omn_profit_per
            self.omn_vat = omn_vat
        else:
            self.omn_tot_sale = 0
            self.omn_tot_cost = 0
            self.omn_profit = 0
            self.omn_profit_percentage = 0
            self.omn_vat = 0
            
        self.omn_tot_sale1 = omn_total_sale
        self.omn_tot_cost1 = omn_total_cost
        self.omn_vat1 = omn_vat
        disc = (omn_total_sale/sheet_total) * abs(sp_disc)
        disc_sale = omn_total_sale - disc 
        self.omn_tot_sale1_ds = disc_sale  
        omn_profit = disc_sale - omn_total_cost
        self.omn_profit1 = omn_profit
        self.omn_profit_percentage1 = (omn_profit/(disc_sale or 1.0)) *100.0
        
#         #Added by Aslam : Rebate value distribution to each tabs 
#         omn_rebate = (omn_total_cost/sheet_tot_cost) * abs(tot_rebate)
#         self.omn_rebate = omn_rebate
#         omn_profit_with_rebate =  omn_profit + omn_rebate
#         self.omn_profit_with_rebate = omn_profit_with_rebate
#         self.omn_profit_with_rebate_perc = (omn_profit_with_rebate/(disc_sale or 1.0)) *100.0
        
        om_res = self.line_two(self.om_eqpmentreq_line, self.om_extra_line)
        om_eng = self.line_single(self.om_residenteng_line)
        om_tech_res = self.line_summarize(self.om_tech_line)
        om_total_sale = om_res.get('tot_sale') + om_eng.get('tot_sale') + om_tech_res.get('tot_sale',0.0)
        om_total_cost = om_res.get('tot_cost') + om_eng.get('tot_cost') + om_tech_res.get('tot_cost',0.0)
        om_profit =  om_total_sale - om_total_cost
        om_profit_per = 0.0
        o_m_vat = self.get_vat_total(self.om_tech_line) + self.get_vat_total(self.om_residenteng_line) + self.get_vat_total(self.om_eqpmentreq_line) +self.get_vat_total(self.om_extra_line)

        if om_total_sale:
            om_profit_per = (om_profit/om_total_sale) * 100
        if self.included_om_in_quotation:
            self.o_m_tot_sale = om_total_sale
            self.o_m_tot_cost = om_total_cost
            self.o_m_profit = om_profit
            self.o_m_profit_percentage = om_profit_per
            self.o_m_vat = o_m_vat
        else:
            self.o_m_tot_sale = 0
            self.o_m_tot_cost = 0
            self.o_m_profit = 0
            self.o_m_profit_percentage = 0
            self.o_m_vat = 0

        self.o_m_tot_sale1 = om_total_sale
        self.o_m_tot_cost1 = om_total_cost
        
        
        
        self.o_m_vat1 = o_m_vat
        
        
        disc = (om_total_sale/sheet_total) * abs(sp_disc)
        disc_sale = om_total_sale - disc 
        self.o_m_tot_sale1_ds = disc_sale
        om_profit = disc_sale - om_total_cost
        self.o_m_profit1 = om_profit 
        self.o_m_profit_percentage1 = (om_profit/(disc_sale or 1.0)) *100.0
        
#         #Added by Aslam : Rebate value distribution to each tabs 
#         o_m_rebate = (om_total_cost/sheet_tot_cost) * abs(tot_rebate)
#         self.o_m_rebate = o_m_rebate
#         o_m_profit_with_rebate =  om_profit + o_m_rebate
#         self.o_m_profit_with_rebate = o_m_profit_with_rebate
#         self.o_m_profit_with_rebate_perc = (o_m_profit_with_rebate/(disc_sale or 1.0)) *100.0

    @api.one
    @api.depends('mat_tot_cost','trn_tot_cost','mat_tot_cost','bim_tot_cost',
                 'oim_tot_cost','bis_tot_cost','ois_tot_cost','bmn_tot_cost','omn_tot_cost','o_m_tot_cost')
    def _get_sum_total_cost(self):
        self.summary_tot_cost = self.mat_tot_cost + self.trn_tot_cost + self.bim_tot_cost + \
        self.oim_tot_cost + self.bis_tot_cost + self.ois_tot_cost + self.bmn_tot_cost + self.omn_tot_cost + self.o_m_tot_cost

    @api.one
    @api.depends('summary_tot_cost','mat_tot_cost')
    def _get_weight(self):
        if self.summary_tot_cost:
            self.mat_weight = 100 * self.mat_tot_cost /(self.summary_tot_cost or 1.0)
            self.trn_weight = 100 * self.trn_tot_cost / (self.summary_tot_cost or 1.0)
            self.bim_weight = 100 * self.bim_tot_cost / (self.summary_tot_cost or 1.0)
            self.oim_weight = 100 * self.oim_tot_cost / (self.summary_tot_cost or 1.0)
            self.bmn_weight = 100 * self.bmn_tot_cost / (self.summary_tot_cost or 1.0)
            self.omn_weight = 100 * self.omn_tot_cost / (self.summary_tot_cost or 1.0)
            self.o_m_weight = 100 * self.o_m_tot_cost /(self.summary_tot_cost or 1.0)
            self.bis_weight = 100 * self.bis_tot_cost /(self.summary_tot_cost or 1.0)
            self.ois_weight = 100 * self.ois_tot_cost /(self.summary_tot_cost or 1.0)
#     Summary total
    @api.one
    @api.depends('mat_tot_sale','trn_tot_sale','bim_tot_sale',
                 'oim_tot_sale','bis_tot_sale','ois_tot_sale','bmn_tot_sale','omn_tot_sale','o_m_tot_sale'
                 )
    def _get_total_sum_price(self):
        self.mat_price = self.mat_tot_sale + self.trn_tot_sale
        self.imp_price = self.bim_tot_sale + self.oim_tot_sale
        self.info_sec_price = self.bis_tot_sale + self.ois_tot_sale
        self.maint_price = self.bmn_tot_sale + self.omn_tot_sale + self.o_m_tot_sale

    @api.one
    @api.depends('mat_tot_sale','mat_tot_cost','mat_weight',
                 'trn_tot_sale','trn_tot_cost','trn_weight',
                 'bim_tot_sale','bim_tot_cost','bim_weight',
                 'oim_tot_sale','oim_tot_cost','oim_weight',
                 'bmn_tot_sale','bmn_tot_cost','bmn_weight',
                 'omn_tot_sale','omn_tot_cost','omn_weight',
                 'o_m_tot_sale','o_m_tot_cost','o_m_weight',
                 'special_discount'
                 )
    def _get_total_summary(self):
        total_sale = self.mat_tot_sale + self.trn_tot_sale + self.bim_tot_sale + self.oim_tot_sale + self.bis_tot_sale + self.ois_tot_sale + self.bmn_tot_sale + self.omn_tot_sale + self.o_m_tot_sale
        sum_total_sale = total_sale + self.special_discount
        total_cost = self.mat_tot_cost + self.trn_tot_cost + self.bim_tot_cost + self.oim_tot_cost + self.bis_tot_cost + self.ois_tot_cost + self.bmn_tot_cost + self.omn_tot_cost + self.o_m_tot_cost + self.pre_opn_cost
        profit = sum_total_sale - total_cost
        profit_per = 0.0
        if total_sale:
            profit_per = profit/sum_total_sale
        total_weight = self.mat_weight + self.trn_weight + self.bim_weight + self.oim_weight + self.bis_weight + self.ois_weight + self.bmn_weight + self.omn_weight + self.o_m_weight
        self.sum_tot_sale = total_sale
        self.sum_total_sale = sum_total_sale
        special_discount_vat =0.0
        #Added by aslam for calculating special discount vat as per cost sheet vat
        vat_perc = self.get_applied_vat_perc()       
        special_discount = self.special_discount 
        if not self.ignore_vat:
            special_discount = self.special_discount 
            special_discount_vat = special_discount * vat_perc
            self.special_discount_vat = special_discount_vat
        total_vat = self.mat_vat + self.trn_vat + self.bim_vat + self.oim_vat + self.bis_vat + self.ois_vat + self.bmn_vat + self.omn_vat + self.o_m_vat + special_discount_vat
        self.sum_vat = total_vat
        self.sum_total_with_vat = sum_total_sale + total_vat
        if special_discount and total_sale:
            disc_per = (special_discount/total_sale) *100
            self.sp_disc_percentage = disc_per
        self.sum_tot_cost = total_cost
        self.sum_profit = profit
        
#         total_manpower_cost = self.a_total_manpower_cost 
# #         new_profit = total_manpower_cost +profit
#         self.sum_od_new_profit = new_profit
        self.sum_profit_per = profit_per * 100
        self.sum_total_weight = total_weight


    def default_bmn_it_preventive_line(self):
        line = [{'item':"1",'description':'Beta IT Preventive Maintenance','qty':1}]
        return line
    def default_bmn_it_remedial_line(self):
        line = [{'item':"1",'name':'Beta IT Remedial Maintenance','qty':1}]
        return line
    def default_omn_preventive_line(self):
        line = [{'item':"1",'name':'Outsourced Preventive Maintenance','qty':1}]
        return line
    def default_omn_remedial_line(self):
        line = [{'item':"1",'name':'Outsourced Remedial Maintenance','qty':1}]
        return line
    
    def get_default_vat(self):
        vat = self.env.user.company_id.od_tax_id or False
        context = self._context
        branch_id = context.get('default_od_branch_id')
        if branch_id == 2:
            vat = 33
        return vat


    def default_beta_service_line(self):
        
        currency = self.env.user.company_id.currency_id
        currency2 = self.env.user.company_id.currency_id
        tax_id = self.get_default_vat()
        rate=self.env['res.currency']._get_conversion_rate(currency, currency2)
        exchange_fact = 1/rate
        exchange_fact= float_round(exchange_fact, precision_rounding=currency2.rounding)
        line = [
                {'name':'PS-BIT','sales_currency_id':currency.id,
                 'round_up':1,
                 'supplier_currency_id':currency.id,
                 'currency_exchange_factor':1.0,
                 'shipping':0.0,
                 'customs':0.0,
                 'stock_provision':0.0,
                 'conting_provision':0.500,
                 'tax_id':tax_id},
                {'name':'BMN','sales_currency_id':currency.id,
                 'round_up':1,
                 'supplier_currency_id':currency.id,
                 'currency_exchange_factor':1.0,
                 'shipping':0.0,
                 'customs':0.0,
                 'stock_provision':0.0,
                 'conting_provision':0.500,
                 'tax_id':tax_id},
                {'name':'PS-SUB','sales_currency_id':currency.id,'round_up':1,
                 'supplier_currency_id':currency.id,
                 'currency_exchange_factor':1.0,
                 'shipping':0.0,
                 'customs':0.0,
                 'stock_provision':0.0,
                 'conting_provision':0.500,
                 'tax_id':tax_id},
                {'name':'IS-BIT','sales_currency_id':currency.id,
                 'round_up':1,
                 'supplier_currency_id':currency.id,
                 'currency_exchange_factor':1.0,
                 'shipping':0.0,
                 'customs':0.0,
                 'stock_provision':0.0,
                 'conting_provision':0.500,
                 'tax_id':tax_id},
                {'name':'IS-SUB','sales_currency_id':currency.id,'round_up':1,
                 'supplier_currency_id':currency.id,
                 'currency_exchange_factor':1.0,
                 'shipping':0.0,
                 'customs':0.0,
                 'stock_provision':0.0,
                 'conting_provision':0.500,
                 'tax_id':tax_id},
                {'name':'OMN','sales_currency_id':currency.id,'round_up':1,
                 'supplier_currency_id':currency.id,
                 'currency_exchange_factor':1.0,
                 'shipping':0.0,
                 'customs':0.0,
                 'stock_provision':0.0,
                 'conting_provision':0.500,
                 'tax_id':tax_id},
                {'name':'O&M','sales_currency_id':currency.id,'round_up':1,
                 'supplier_currency_id':currency.id,
                 'currency_exchange_factor':1.0,
                 'shipping':0.0,
                 'customs':0.0,
                 'stock_provision':0.0,
                 'conting_provision':0.500,
                 'tax_id':tax_id},
                ]
        return line





    def is_saudi_comp(self):
        res = False
        saudi_comp_id = self.get_saudi_company_id()
        user_comp_id = self.env.user.company_id.id
        if user_comp_id == saudi_comp_id:
            res = True
        return res

    def my_value(self,uae_val,saudi_val):
        res = uae_val
        if self.is_saudi_comp():
            res =saudi_val
        return res

    def get_shipping_value(self):
        res = self.my_value(5, 2)
        return res

    def get_custom(self):
        res = self.my_value(1, 5)
        return res

    def get_stock_provision(self):
        res = self.my_value(0.50,0.50)
        return res

    def default_costgroup_material_line(self):

        currency = self.env.user.company_id.currency_id
        currency2 = self.env.user.company_id and self.env.user.company_id.od_supplier_currency_id
        if not currency2:
            raise Warning("Please Configure Cost Group Default Supplier Currency In Company")
        # currency2 = self.env['res.currency'].search([('name','=','USM')]).id
        #commented by aslam for getting abu dhabi branch tax loaded automatically
        #tax_id  = self.env.user.company_id.od_tax_id or False
        tax_id = self.get_default_vat()
        rate=self.env['res.currency']._get_conversion_rate(currency, currency2)
        exchange_fact = 1/rate
        exchange_fact= float_round(exchange_fact, precision_rounding=currency2.rounding)
        line = [{
                 'name':'Main',
                 'sales_currency_id':currency.id,
                 'round_up':1,
                 'supplier_currency_id':currency2.id,
                 'currency_exchange_factor':exchange_fact,
                 'shipping':self.get_shipping_value(),
                 'customs':self.get_custom(),
                 'stock_provision':self.get_stock_provision(),
                 'conting_provision':0.50,
                 'tax_id':tax_id
                 }]
        return line
    def default_costgroup_extra_expense_line(self):

        currency = self.env.user.company_id.currency_id
        currency2 = self.env.user.company_id and self.env.user.company_id.od_supplier_currency_id
        if not currency2:
            raise Warning("Please Configure Cost Group Default Supplier Currency In Company")
        # currency2 = self.env['res.currency'].search([('name','=','USM')]).id

        rate=self.env['res.currency']._get_conversion_rate(currency, currency2)
        exchange_fact = 1/rate
        exchange_fact= float_round(exchange_fact, precision_rounding=currency2.rounding)
        tax_id  = self.get_default_vat()
        line = [{
                 'name':'Extra Expense',
                 'sales_currency_id':currency.id,
                 'round_up':1,
                 'customer_discount':100,
                 'supplier_currency_id':currency2.id,
                 'currency_exchange_factor':exchange_fact,
                 'shipping':self.get_shipping_value(),
                 'customs':self.get_custom(),
                 'stock_provision':self.get_stock_provision(),
                 'conting_provision':0.50,
                 'tax_id':tax_id
                 }]
        return line
    def default_costgroup_optional_line(self):
        currency = self.env.user.company_id.currency_id
        currency2 = self.env.user.company_id and self.env.user.company_id.od_supplier_currency_id
        if not currency2:
            raise Warning("Please Configure Cost Group Default Supplier Currency In Company")
        # from_currency,to_currency = self.env.user.company_id.currency_id,self.env['res.currency'].search([('name','=','USM')])
        rate= self.env['res.currency']._get_conversion_rate(currency, currency2)
        exchange_fact = 1/rate
        exchange_fact= float_round(exchange_fact, precision_rounding=currency2.rounding)
        tax_id  = self.get_default_vat()
        line = [{
                 'name':'Optional',
                 'sales_currency_id':currency.id,
                  'round_up':1,
                 'supplier_currency_id':currency2.id,
                 'currency_exchange_factor':exchange_fact,
                 'shipping':self.get_shipping_value(),
                 'customs':self.get_custom(),
                 'stock_provision':self.get_stock_provision(),
                 'conting_provision':0.50,
                  'tax_id':tax_id
                 }]
        return line
    
    def get_tech_cost(self):
        cost =0.0
        if self.included_bim_in_quotation:
            cost += sum([line.line_cost_local_currency for line in self.imp_tech_line])
        if self.included_bmn_in_quotation:
            cost += sum([line.line_cost_local_currency for line in self.amc_tech_line])
        return cost
    
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
    
    @api.one 
    @api.depends('sum_profit','a_bim_cost','a_bmn_cost', 'a_bis_cost')
    def _get_total_gp(self):
        tech_cost =0.0
#         tech_cost = self.get_tech_cost()
        tot_gp = self.sum_profit + self.a_bim_cost + self.a_bmn_cost + self.a_bis_cost
        self.total_gp = tot_gp
        self.returned_mp =self.a_bim_cost + self.a_bmn_cost + self.a_bis_cost
        total_sale = self.sum_total_sale 
#         if total_sale:
#             self.total_gp_percent = (tot_gp/total_sale) *100.0
        rebate = self.prn_ven_reb_cost
        total_gp_with_rebate = tot_gp + rebate
        self.total_gp_with_rebate = total_gp_with_rebate
        if total_sale:
            self.total_gp_percent = (tot_gp/total_sale) *100.0
            self.total_gp_percent_with_rebate = (total_gp_with_rebate/total_sale) *100.0
        
    
    
  
    
    is_over_rule = fields.Boolean(string="Over Ruled?")
    over_rule = fields.Selection([('over_rule','Over Ruled By GM')],string="Over Rule")
    over_rule_uid = fields.Many2one('res.users',string="Over Rule By")
    over_rule_date = fields.Datetime(string="Over Ruled Date")
    
    summary_tot_cost = fields.Float(string='Total Cost',compute='_get_sum_total_cost',store=True,digits=dp.get_precision('Account'))
    sum_tot_sale = fields.Float(string="Total Sale",compute="_get_total_summary",store=True,digits=dp.get_precision('Account'))
    sum_tot_cost = fields.Float(string='Total Cost',compute="_get_total_summary",store=True,digits=dp.get_precision('Account'))
    sum_profit = fields.Float(string="Total Profit",compute="_get_total_summary",store=True,digits=dp.get_precision('Account'))
    total_gp = fields.Float(string="Total GP",compute="_get_total_gp",store=True,digits=dp.get_precision('Account'))
    total_gp_percent = fields.Float(string="Total Gp %",compute="_get_total_gp",store=True,digits=dp.get_precision('Account'))
    total_gp_with_rebate = fields.Float(string="Total GP",compute="_get_total_gp",store=True,digits=dp.get_precision('Account'))
    total_gp_percent_with_rebate = fields.Float(string="Total Gp %",compute="_get_total_gp",store=True,digits=dp.get_precision('Account'))
    returned_mp =fields.Float(string="Returned MP",compute="_get_total_gp",store=True,digits=dp.get_precision('Account'))
    original_mp = fields.Float(string="Original Returned MP",digits=dp.get_precision('Account'))
#     sum_od_new_profit = fields.Float(string="New Profit",compute="_get_total_summary",store=True)
    sum_profit_per = fields.Float(string="Total Profit Percentage",compute="_get_total_summary",store=True,digits=dp.get_precision('Account'))
    sum_total_weight = fields.Float(string="Total Weight",compute="_get_total_summary",store=True,digits=dp.get_precision('Account'))
    special_discount = fields.Float(string="Special Discount",digits=dp.get_precision('Account')) 
    special_discount_vat = fields.Float(string="Discount VAT",compute="_get_total_summary",store=True,digits=dp.get_precision('Account'))
    sum_total_sale =fields.Float(string="Total Sale Final",compute="_get_total_summary",store=True,digits=dp.get_precision('Account'))
    sum_total_with_vat =  fields.Float(string="Total Sale With VAT",compute="_get_total_summary",store=True,digits=dp.get_precision('Account'))
    sum_vat = fields.Float(string="Total VAT",compute="_get_total_summary",store=True,digits=dp.get_precision('Account'))
    sp_disc_percentage = fields.Float(string="Special Discount",compute="_get_total_summary",store=True,digits=dp.get_precision('Account'))
    
    @api.onchange('bim_log_select')
    def onchange_bim_log_select(self):
        if self.bim_log_select:
            self.bim_imp_select = False
            
    @api.onchange('included_bim_in_quotation')
    def onchange_included_bim_in_quotation(self):
        if self.included_bim_in_quotation:
            self.bim_log_select = True

    @api.onchange('bim_imp_select')
    def onchange_bim_imp_select(self):
        if self.bim_imp_select:
            self.bim_log_select = False
            
    def default_section_material(self):
        line = [{'section':'M','name':'Main Material'}]
        return line
    def default_section_optional(self):
        line = [{'section':'O','name':'Optional Material'}]
        return line
    def default_section_training(self):
        line = [{'section':'T','name':'Training'}]
        return line
    def default_resident_eng_line(self):
        line = [{'name':'Resident Engineer'}]
        return line
    def default_exclusion_note(self):
        res = """
        <h4>* Work on any equipment not covered by this proposal</h4>
<h4>* Obtaining any required 3rd Party NOCs (No Objection Certificates: Municipality, Telecom, etc.), if any is required</h4>
<h4>* Electrical, Mechanical, and Civil Works</h4>
        """

        return res
    def default_amc_scope(self):
        template = """
        <h2><strong><span style="text-decoration: underline; color: blue;">Scope of Maintenance</span></strong></h2>
<table width="576">
<tbody>
<tr>
<td colspan="4" width="256">Note: This section represents maintenance services. They are different from the manufacturer services (such as warranty, subscriptions, and licenses renewals)</td>
<td width="64">&nbsp;</td>
<td style="text-align: right;" colspan="4" width="256">ملاحظة: يمثل هذا القسم الخدمات الفنية في الصيانة. هذه الخدمات تختلف عن خدمات الشركة المصنعة التي تتمثل في الضمان، الاشتراكات، وتجديد الرخص.</td>
</tr>
<tr>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
</tr>
<tr>
<td colspan="2" width="128"><strong>Start Date of Maintenance</strong></td>
<td style="text-align: center;" colspan="5" width="320">After Project Completion and Satisfaction of its Payments<br /> بعد انتهاء أعمال المشروع واتمام دفعاته</td>
<td style="text-align: right;" colspan="2" width="128"><strong>تاريخ بداية أعمال الصيانة</strong></td>
</tr>
<tr>
<td colspan="2"><strong>Duration of Maint.</strong></td>
<td style="text-align: center;" colspan="5">One Year - سنة واحدة</td>
<td style="text-align: right;" colspan="2"><strong>مدة أعمال الصيانة</strong></td>
</tr>
<tr>
<td colspan="2" rowspan="2"><strong>Maintenance Level</strong></td>
<td style="text-align: center;" colspan="5">8x5</td>
<td style="text-align: right;" colspan="2" rowspan="2"><strong>مستوى الصيانة</strong></td>
</tr>
<tr>
<td style="text-align: center;" colspan="5">Excluding Public Holidays <br /> غير شاملة للعطل الرسمية</td>
</tr>
<tr>
<td colspan="2"><strong>Preventive Maint.</strong></td>
<td style="text-align: center;" colspan="5">Quarterly - كل ربع سنة</td>
<td style="text-align: right;" colspan="2"><strong>الصيانة الوقائية الدورية</strong></td>
</tr>
<tr>
<td colspan="2" width="128"><strong>No. of Preventive </strong><br /><strong> Maintenances / Year</strong></td>
<td style="text-align: center;" colspan="5" width="320">4 Each Year</td>
<td style="text-align: right;" colspan="2" width="128"><strong>عدد مرات الصيانة الوقائية الدورية في السنة</strong></td>
</tr>
<tr>
<td colspan="2" width="128"><strong>Scope of Services </strong></td>
<td style="text-align: left;" colspan="5" width="320">&nbsp;Maintenance</td>
<td style="text-align: right;" colspan="2" width="128"><strong>نطاق الخدمات</strong></td>
</tr>
<tr>
<td colspan="2" rowspan="4" width="128"><strong>Remedial Maintenances</strong><br /> <br /><strong> Devices covered by this service must be covered by manufacturer warranty</strong></td>
<td style="text-align: center;" colspan="5" width="320"><strong>Level 1 Support</strong> - Customer Responsibility: <br /> (مسؤولية العميل)<br /> Problem Reporting and Basic Information<br /> الابلاغ عن الأعطال وجمع المعلومات الأولية</td>
<td style="text-align: right;" colspan="2" rowspan="4" width="128"><strong>الصيانة العلاجية</strong><br /> <br /><strong> يجب أن تكون الأجهزة المشمولة بهذه الخدمات خاضعة للضمان لدى الشركة المصنعة</strong></td>
</tr>
<tr>
<td style="text-align: center;" colspan="5" width="320"><strong>Level 2 Support</strong> - Beta IT Responsibility:<br /> (مسؤولية بيتا) <br /> Troubleshooting and Workaround<br /> العمل على حل الأعطال</td>
</tr>
<tr>
<td style="text-align: center;" colspan="5" width="320"><strong>Level 3 Support</strong> - Beta IT / Manufacturer Responsibility:<br /> (مسؤولية بيتا والشركة المصنعة)<br /> Root Cause Analysis (Provided that Customer has valid warranty and support with manufacturer)<br /> إيجاد جذور المشكلة للعطل ومنع تكرارها <br /> (يتطلب ذلك من العميل أن يبقي الأجهزة خاضعة لضمان الشركة المصنعة)</td>
</tr>
<tr>
<td style="text-align: center;" colspan="5" width="320"><strong>Level 4 Support</strong> - Manufacturer Responsibility:<br /> (مسؤولية الشركة المصنعة) <br /> Root access, Engineering, and Development (Requires customer to have valid warranty and support from manufacturer)<br /> هندسة البرامج والوصول إلى جوهر البرمجيات العاملة على الأجهزة وتطويرها لحل الأعطال المستعصية <br /> &nbsp;(يتطلب ذلك من العميل أن يبقي الأجهزة خاضعة لضمان الشركة المصنعة)</td>
</tr>
<tr>
<td colspan="2" rowspan="2" width="128"><strong>Warranty</strong><br /> <br /><strong> Devices covered by this service must be covered by manufacturer warranty</strong></td>
<td colspan="5" width="320">Beta IT will process RMA process on behalf of customer for malfunctioning devices provided that customer has a valid support contract with manufacturer and as per manufacturer terms and conditions.<br /> <br /> Material, covered by manufacturer warranty services, is subject to manufacturer warranty and RMA policies, procedures, and RMA repair periods. RMA and Manufactures' support conditions are provided by each manufacturer on its own web site.</td>
<td style="text-align: right;" colspan="2" rowspan="2" width="128"><strong>الضمان</strong><br /> <br /><strong> يجب أن تكون الأجهزة المشمولة بهذه الخدمات خاضعة للضمان لدى الشركة المصنعة</strong></td>
</tr>
<tr>
<td style="text-align: right;" colspan="5" width="320">ستقوم بيتا بالعمل على شحن الأجهزة المتعطلة للشركة المصنعة باسم العميل بشرط توفر عقد الضمان بين العميل والشركة المصنعة وحسب شروط الشركة المصنعة.<br /> <br /> تخضع المواد، المغطاة بخدمات الضمان من الشركات المصنعة، لشروط هذه الشركات فيما يتعلق لشروط الإصلاح وآلياته والزمن المطلوب لذلك. يمكن للعميل مراجعة هذه الشروط والآليات على المواقع الإلكترونية للشركات المصنعة للمواد المعروضة.</td>
</tr>
<tr>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
</tr>
<tr>
<td colspan="4">
<h3><span style="text-decoration: underline;"><strong>Fault Classification / Response Times</strong></span></h3>
</td>
<td>&nbsp;</td>
<td style="text-align: right;" colspan="4">
<h3><span style="text-decoration: underline;"><strong>جدول تصنيف أحداث الصيانة / أوقات الاستجابة</strong></span></h3>
</td>
</tr>
<tr>
<td colspan="3"><strong>A. Critical - Service Affecting</strong></td>
<td colspan="3" width="192">Any highly critical system or service outage in a live environment that results in severe degradation of overall on-line/off-line network performance.</td>
<td style="text-align: right;" colspan="3"><strong>أ. حرجة - تؤثر على سير العمل</strong></td>
</tr>
<tr>
<td colspan="3">Response Mean: Phone &amp; Email</td>
<td style="text-align: center;" colspan="3" width="192">One Business Hour<br /> خلال ساعة عمل واحدة</td>
<td style="text-align: right;" colspan="3">آلية الاستجابة: التلفون والبريد الاكتروني</td>
</tr>
<tr>
<td colspan="3">Response Mean: Remote Access</td>
<td style="text-align: center;" colspan="3" width="192">2 Business Hours<br /> خلال 2 ساعة عمل</td>
<td style="text-align: right;" colspan="3">آلية الاستجابة: الاتصال بالأنظمة عن بعد</td>
</tr>
<tr>
<td colspan="3">Response Mean: On-Site</td>
<td style="text-align: center;" colspan="3" width="192">4 Business Hours + Travelling Time<br /> &nbsp;خلال 4 ساعات عمل + وقت السفر والانتقال</td>
<td style="text-align: right;" colspan="3">آلية الاستجابة: الوصول إلى موقع العمل</td>
</tr>
<tr>
<td colspan="3"><strong>B. Major - Service Affecting</strong></td>
<td colspan="3" width="192">Any major degradation of system or service performance that impacts end user service quality or significantly impairs network operator control or operational effectiveness.</td>
<td style="text-align: right;" colspan="3"><strong>ب. كبيرة - تؤثر على سير العمل</strong></td>
</tr>
<tr>
<td colspan="3">Response Mean: Phone &amp; Email</td>
<td style="text-align: center;" colspan="3" width="192">One Business Hour<br /> خلال ساعة عمل واحدة</td>
<td style="text-align: right;" colspan="3">آلية الاستجابة: التلفون والبريد الاكتروني</td>
</tr>
<tr>
<td colspan="3">Response Mean: Remote Access</td>
<td style="text-align: center;" colspan="3" width="192">4 Business Hours<br /> خلال 4 ساعات عمل</td>
<td style="text-align: right;" colspan="3">آلية الاستجابة: الاتصال بالأنظمة عن بعد</td>
</tr>
<tr>
<td colspan="3">Response Mean: On-Site</td>
<td style="text-align: center;" colspan="3" width="192">7 Business Hours + Travelling Time<br /> &nbsp;خلال 7 ساعات عمل + وقت السفر والانتقال</td>
<td style="text-align: right;" colspan="3">آلية الاستجابة: الوصول إلى موقع العمل</td>
</tr>
<tr>
<td colspan="3"><strong>C. Minor - Not-Service Affecting</strong></td>
<td colspan="3" width="192">Any minor degradation of system or service performance that does not have any impact on end user service quality and minimal impact on network operations.</td>
<td style="text-align: right;" colspan="3"><strong>ج. صغيرة - لا تؤثر على سير العمل</strong></td>
</tr>
<tr>
<td colspan="3">Response Mean: Phone &amp; Email</td>
<td style="text-align: center;" colspan="3" width="192">24 Business Hour<br /> خلال 24 ساعة عمل</td>
<td style="text-align: right;" colspan="3">آلية الاستجابة: التلفون والبريد الاكتروني</td>
</tr>
<tr>
<td colspan="3">Response Mean: Remote Access</td>
<td style="text-align: center;" colspan="3" width="192">48 Business Hours<br /> خلال 48 ساعة عمل</td>
<td style="text-align: right;" colspan="3">آلية الاستجابة: الاتصال بالأنظمة عن بعد</td>
</tr>
<tr>
<td colspan="3">Response Mean: On-Site</td>
<td style="text-align: center;" colspan="3" width="192">72 Business Hours + Travelling Time<br /> &nbsp;خلال 72 ساعة عمل + وقت السفر والانتقال</td>
<td style="text-align: right;" colspan="3">آلية الاستجابة: الوصول إلى موقع العمل</td>
</tr>
<tr>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
</tr>
<tr>
<td colspan="4">
<h3><strong><span style="text-decoration: underline;">Escalation Sequence / Matrix</span></strong></h3>
</td>
<td>&nbsp;</td>
<td style="text-align: right;" colspan="4">
<h3><span style="text-decoration: underline;"><strong>إجراء العمل للإبلاغ عن أعمال الصيانة</strong></span></h3>
</td>
</tr>

<tr>
<td colspan="2" rowspan="2" >Beta IT Helpdesk Contact Information</td>
<td colspan="4">T:920006069 <br>Email:<a href="mailto:support.ksa@betait.net">support.ksa@betait.net</a></td>
<td style="text-align: right;" colspan="4">معلومات الاتصال بقسم الصيانة - مكتب خدمات ما بعد البيع</td>
</tr>


<tr></tr>

<tr>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
</tr>
<tr>
<td colspan="4" width="256">Any new configuration and configuration changes or additions to configuration will not be covered by this proposal. Moving systems is not covered by this proposal.</td>
<td>&nbsp;</td>
<td style="text-align: right;" colspan="4" width="256">لا تشمل هذه الخدمات أية تعريفات إضافية أو تغييرات في التعريفات على الأجهزة. كذلك لا تشمل هذه الخدمات نقل الأجهزة من مكان إلى آخر.</td>
</tr>
<tr>
<td colspan="4" width="256">Customer DOES NOT have access to Beta IT stock spare parts for workaround solutions during RMA periods.</td>
<td>&nbsp;</td>
<td style="text-align: right;" colspan="4" width="256">ليس للعميل الحق في استخدام أجهزة أخرى في مستودعات بيتا خلال فترة شحن الأجهزة المتعطلة تحت خدمة الضمان كبديل مؤقت إلى حين اتمام إعادة الأجهزة المتعطلة.</td>
</tr>
<tr>
<td colspan="4" width="256">If the customer requests a job that is not related to the AMC material or services mentioned in this document, then Beta IT reserves the right to not respond to this request and this shall not affect the progress or the due payments.</td>
<td>&nbsp;</td>
<td style="text-align: right;" colspan="4" width="256">إذا طلب العميل خدمة صيانة على أجهزة غير مشمولة في هذا العرض، فإنه يحق لشركة بيتا أن لا تستجيب لهذا الطلب ولا ينبغي أن يؤثر ذلك على مستحقات شركة بيتا.</td>
</tr>
<tr>
<td colspan="4" width="256">Beta IT reserves the right to assign, terminate, and re-assign subcontractors in a manner that allows Beta IT to perform the Services as described in the statement of work and in accordance with the terms of this agreement.</td>
<td>&nbsp;</td>
<td style="text-align: right;" colspan="4" width="256">يحق لشركة بيتا أن تستعين بمقاولين بالباطن لتقديم الخدمات المطلوبة المشروحة في نطاق الخدمة أعلاه وحسب شروط هذه الخدمات.</td>
</tr>
<tr>
<td colspan="4" width="256">Customer shall use and operate the Hardware and/or Software component(s) under this service agreement in accordance with manufacturer&rsquo;s operating manuals and promptly and regularly carry out all operation maintenance routine as and when specified.</td>
<td>&nbsp;</td>
<td style="text-align: right;" colspan="4" width="256">ينبغي أن يقوم العميل بتشغيل الأجهزة والبرمجيات الخاضعة لهذه الخدمات حسب شروط الشركات المصنعة للتشغيل كالتبريد، والكهرباء وغيرها. كما ينبغي أن يجري عليها الصيانة المطلوبة لضمان تشغيلها.</td>
</tr>
</tbody>
</table>

        """
        
        template1 = """
<h2><strong><span style="text-decoration: underline; color: blue;">Scope of Maintenance</span></strong></h2>
<table width="576">
<tbody>
<tr>
<td colspan="4" width="256">Note: This section represents maintenance services. They are different from the manufacturer services (such as warranty, subscriptions, and licenses renewals)</td>
<td width="64">&nbsp;</td>
<td style="text-align: right;" colspan="4" width="256">ملاحظة: يمثل هذا القسم الخدمات الفنية في الصيانة. هذه الخدمات تختلف عن خدمات الشركة المصنعة التي تتمثل في الضمان، الاشتراكات، وتجديد الرخص.</td>
</tr>
<tr>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
</tr>
<tr>
<td colspan="2" width="128"><strong>Start Date of Maintenance</strong></td>
<td style="text-align: center;" colspan="5" width="320">After Project Completion and Satisfaction of its Payments<br /> بعد انتهاء أعمال المشروع واتمام دفعاته</td>
<td style="text-align: right;" colspan="2" width="128"><strong>تاريخ بداية أعمال الصيانة</strong></td>
</tr>
<tr>
<td colspan="2"><strong>Duration of Maint.</strong></td>
<td style="text-align: center;" colspan="5">One Year - سنة واحدة</td>
<td style="text-align: right;" colspan="2"><strong>مدة أعمال الصيانة</strong></td>
</tr>
<tr>
<td colspan="2" rowspan="2"><strong>Maintenance Level</strong></td>
<td style="text-align: center;" colspan="5">24x7</td>
<td style="text-align: right;" colspan="2" rowspan="2"><strong>مستوى الصيانة</strong></td>
</tr>
<tr>
<td style="text-align: center;" colspan="5">Including Public Holidays <br /> شاملة للعطل الرسمية</td>
</tr>
<tr>
<td colspan="2"><strong>Preventive Maint.</strong></td>
<td style="text-align: center;" colspan="5">Quarterly - كل ربع سنة</td>
<td style="text-align: right;" colspan="2"><strong>الصيانة الوقائية الدورية</strong></td>
</tr>
<tr>
<td colspan="2" width="128"><strong>No. of Preventive </strong><br /><strong> Maintenances / Year</strong></td>
<td style="text-align: center;" colspan="5" width="320">4 Each Year</td>
<td style="text-align: right;" colspan="2" width="128"><strong>عدد مرات الصيانة الوقائية الدورية في السنة</strong></td>
</tr>
<tr>
<td colspan="2" width="128"><strong>Scope of Services </strong></td>
<td style="text-align: left;" colspan="5" width="320">1. Preventative Maintenance.<br>2. Remedial Maintenance.<br>3. Software/OS Updates &amp; upgrades.<br>4. Additional operational level configurations are excluded from BetaIT SLA Scope of Work.<br>5. RMA as per the purchased principal vendor support/warranty terms &amp; conditions.</td>
<td style="text-align: right;" colspan="2" width="128"><strong>نطاق الخدمات</strong></td>
</tr>
<tr>
<td colspan="2" rowspan="4" width="128"><strong>Remedial Maintenances</strong><br /> <br /><strong> Devices covered by this service must be covered by manufacturer warranty</strong></td>
<td style="text-align: center;" colspan="5" width="320"><strong>Level 1 Support</strong> - Customer Responsibility: <br /> (مسؤولية العميل)<br /> Problem Reporting and Basic Information<br /> الابلاغ عن الأعطال وجمع المعلومات الأولية</td>
<td style="text-align: right;" colspan="2" rowspan="4" width="128"><strong>الصيانة العلاجية</strong><br /> <br /><strong> يجب أن تكون الأجهزة المشمولة بهذه الخدمات خاضعة للضمان لدى الشركة المصنعة</strong></td>
</tr>
<tr>
<td style="text-align: center;" colspan="5" width="320"><strong>Level 2 Support</strong> - Beta IT Responsibility:<br /> (مسؤولية بيتا) <br /> Troubleshooting and Workaround<br /> العمل على حل الأعطال</td>
</tr>
<tr>
<td style="text-align: center;" colspan="5" width="320"><strong>Level 3 Support</strong> - Beta IT / Manufacturer Responsibility:<br /> (مسؤولية بيتا والشركة المصنعة)<br /> Root Cause Analysis (Provided that Customer has valid warranty and support with manufacturer)<br /> إيجاد جذور المشكلة للعطل ومنع تكرارها <br /> (يتطلب ذلك من العميل أن يبقي الأجهزة خاضعة لضمان الشركة المصنعة)</td>
</tr>
<tr>
<td style="text-align: center;" colspan="5" width="320"><strong>Level 4 Support</strong> - Manufacturer Responsibility:<br /> (مسؤولية الشركة المصنعة) <br /> Root access, Engineering, and Development (Requires customer to have valid warranty and support from manufacturer)<br /> هندسة البرامج والوصول إلى جوهر البرمجيات العاملة على الأجهزة وتطويرها لحل الأعطال المستعصية <br /> &nbsp;(يتطلب ذلك من العميل أن يبقي الأجهزة خاضعة لضمان الشركة المصنعة)</td>
</tr>
<tr>
<td colspan="2" rowspan="2" width="128"><strong>Warranty</strong><br /> <br /><strong> Devices covered by this service must be covered by manufacturer warranty</strong></td>
<td colspan="5" width="320">Beta IT will process RMA process on behalf of customer for malfunctioning devices provided that customer has a valid support contract with manufacturer and as per manufacturer terms and conditions.<br /> <br /> Material, covered by manufacturer warranty services, is subject to manufacturer warranty and RMA policies, procedures, and RMA repair periods. RMA and Manufactures' support conditions are provided by each manufacturer on its own web site.</td>
<td style="text-align: right;" colspan="2" rowspan="2" width="128"><strong>الضمان</strong><br /> <br /><strong> يجب أن تكون الأجهزة المشمولة بهذه الخدمات خاضعة للضمان لدى الشركة المصنعة</strong></td>
</tr>
<tr>
<td style="text-align: right;" colspan="5" width="320">ستقوم بيتا بالعمل على شحن الأجهزة المتعطلة للشركة المصنعة باسم العميل بشرط توفر عقد الضمان بين العميل والشركة المصنعة وحسب شروط الشركة المصنعة.<br /> <br /> تخضع المواد، المغطاة بخدمات الضمان من الشركات المصنعة، لشروط هذه الشركات فيما يتعلق لشروط الإصلاح وآلياته والزمن المطلوب لذلك. يمكن للعميل مراجعة هذه الشروط والآليات على المواقع الإلكترونية للشركات المصنعة للمواد المعروضة.</td>
</tr>
<tr>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
</tr>
<tr>
<td colspan="4">
<h3><span style="text-decoration: underline;"><strong>Fault Classification / Response Times</strong></span></h3>
</td>
<td>&nbsp;</td>
<td style="text-align: right;" colspan="4">
<h3><span style="text-decoration: underline;"><strong>جدول تصنيف أحداث الصيانة / أوقات الاستجابة</strong></span></h3>
</td>
</tr>
<tr>
<td colspan="3"><strong>A. Critical - Service Affecting</strong></td>
<td colspan="3" width="192">Any highly critical system or service outage in a live environment that results in severe degradation of overall on-line/off-line network performance.</td>
<td style="text-align: right;" colspan="3"><strong>أ. حرجة - تؤثر على سير العمل</strong></td>
</tr>
<tr>
<td colspan="3">Response Mean: Phone &amp; Email</td>
<td style="text-align: center;" colspan="3" width="192">One Business Hour<br /> خلال ساعة عمل واحدة</td>
<td style="text-align: right;" colspan="3">آلية الاستجابة: التلفون والبريد الاكتروني</td>
</tr>
<tr>
<td colspan="3">Response Mean: Remote Access</td>
<td style="text-align: center;" colspan="3" width="192">2 Business Hours<br /> خلال 2 ساعة عمل</td>
<td style="text-align: right;" colspan="3">آلية الاستجابة: الاتصال بالأنظمة عن بعد</td>
</tr>
<tr>
<td colspan="3">Response Mean: On-Site</td>
<td style="text-align: center;" colspan="3" width="192">4 Business Hours + Travelling Time<br /> &nbsp;خلال 4 ساعات عمل + وقت السفر والانتقال</td>
<td style="text-align: right;" colspan="3">آلية الاستجابة: الوصول إلى موقع العمل</td>
</tr>
<tr>
<td colspan="3"><strong>B. Major - Service Affecting</strong></td>
<td colspan="3" width="192">Any major degradation of system or service performance that impacts end user service quality or significantly impairs network operator control or operational effectiveness.</td>
<td style="text-align: right;" colspan="3"><strong>ب. كبيرة - تؤثر على سير العمل</strong></td>
</tr>
<tr>
<td colspan="3">Response Mean: Phone &amp; Email</td>
<td style="text-align: center;" colspan="3" width="192">One Business Hour<br /> خلال ساعة عمل واحدة</td>
<td style="text-align: right;" colspan="3">آلية الاستجابة: التلفون والبريد الاكتروني</td>
</tr>
<tr>
<td colspan="3">Response Mean: Remote Access</td>
<td style="text-align: center;" colspan="3" width="192">4 Business Hours<br /> خلال 4 ساعات عمل</td>
<td style="text-align: right;" colspan="3">آلية الاستجابة: الاتصال بالأنظمة عن بعد</td>
</tr>
<tr>
<td colspan="3">Response Mean: On-Site</td>
<td style="text-align: center;" colspan="3" width="192">7 Business Hours + Travelling Time<br /> &nbsp;خلال 7 ساعات عمل + وقت السفر والانتقال</td>
<td style="text-align: right;" colspan="3">آلية الاستجابة: الوصول إلى موقع العمل</td>
</tr>
<tr>
<td colspan="3"><strong>C. Minor - Not-Service Affecting</strong></td>
<td colspan="3" width="192">Any minor degradation of system or service performance that does not have any impact on end user service quality and minimal impact on network operations.</td>
<td style="text-align: right;" colspan="3"><strong>ج. صغيرة - لا تؤثر على سير العمل</strong></td>
</tr>
<tr>
<td colspan="3">Response Mean: Phone &amp; Email</td>
<td style="text-align: center;" colspan="3" width="192">24 Business Hour<br /> خلال 24 ساعة عمل</td>
<td style="text-align: right;" colspan="3">آلية الاستجابة: التلفون والبريد الاكتروني</td>
</tr>
<tr>
<td colspan="3">Response Mean: Remote Access</td>
<td style="text-align: center;" colspan="3" width="192">48 Business Hours<br /> خلال 48 ساعة عمل</td>
<td style="text-align: right;" colspan="3">آلية الاستجابة: الاتصال بالأنظمة عن بعد</td>
</tr>
<tr>
<td colspan="3">Response Mean: On-Site</td>
<td style="text-align: center;" colspan="3" width="192">72 Business Hours + Travelling Time<br /> &nbsp;خلال 72 ساعة عمل + وقت السفر والانتقال</td>
<td style="text-align: right;" colspan="3">آلية الاستجابة: الوصول إلى موقع العمل</td>
</tr>
<tr>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
</tr>
<tr>
<td colspan="4">
<h3><strong><span style="text-decoration: underline;">Escalation Sequence / Matrix</span></strong></h3>
</td>
<td>&nbsp;</td>
<td style="text-align: right;" colspan="4">
<h3><span style="text-decoration: underline;"><strong>إجراء العمل للإبلاغ عن أعمال الصيانة</strong></span></h3>
</td>
</tr>

<tr>
<td colspan="2" rowspan="2" >Beta IT Helpdesk Contact Information</td>
<td colspan="4">T:+971 4 250 0111 <br>Email:<a href="mailto:support@betait.net">support@betait.net</a></td>
<td style="text-align: right;" colspan="4">معلومات الاتصال بقسم الصيانة - مكتب خدمات ما بعد البيع</td>
</tr>


<tr></tr>

<tr>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
</tr>
<tr>
<td colspan="4" width="256">Any new configuration and configuration changes or additions to configuration will not be covered by this proposal. Moving systems is not covered by this proposal.</td>
<td>&nbsp;</td>
<td style="text-align: right;" colspan="4" width="256">لا تشمل هذه الخدمات أية تعريفات إضافية أو تغييرات في التعريفات على الأجهزة. كذلك لا تشمل هذه الخدمات نقل الأجهزة من مكان إلى آخر.</td>
</tr>
<tr>
<td colspan="4" width="256">Customer DOES NOT have access to Beta IT stock spare parts for workaround solutions during RMA periods.</td>
<td>&nbsp;</td>
<td style="text-align: right;" colspan="4" width="256">ليس للعميل الحق في استخدام أجهزة أخرى في مستودعات بيتا خلال فترة شحن الأجهزة المتعطلة تحت خدمة الضمان كبديل مؤقت إلى حين اتمام إعادة الأجهزة المتعطلة.</td>
</tr>
<tr>
<td colspan="4" width="256">If the customer requests a job that is not related to the AMC material or services mentioned in this document, then Beta IT reserves the right to not respond to this request and this shall not affect the progress or the due payments.</td>
<td>&nbsp;</td>
<td style="text-align: right;" colspan="4" width="256">إذا طلب العميل خدمة صيانة على أجهزة غير مشمولة في هذا العرض، فإنه يحق لشركة بيتا أن لا تستجيب لهذا الطلب ولا ينبغي أن يؤثر ذلك على مستحقات شركة بيتا.</td>
</tr>
<tr>
<td colspan="4" width="256">Beta IT reserves the right to assign, terminate, and re-assign subcontractors in a manner that allows Beta IT to perform the Services as described in the statement of work and in accordance with the terms of this agreement.</td>
<td>&nbsp;</td>
<td style="text-align: right;" colspan="4" width="256">يحق لشركة بيتا أن تستعين بمقاولين بالباطن لتقديم الخدمات المطلوبة المشروحة في نطاق الخدمة أعلاه وحسب شروط هذه الخدمات.</td>
</tr>
<tr>
<td colspan="4" width="256">Customer shall use and operate the Hardware and/or Software component(s) under this service agreement in accordance with manufacturer&rsquo;s operating manuals and promptly and regularly carry out all operation maintenance routine as and when specified.</td>
<td>&nbsp;</td>
<td style="text-align: right;" colspan="4" width="256">ينبغي أن يقوم العميل بتشغيل الأجهزة والبرمجيات الخاضعة لهذه الخدمات حسب شروط الشركات المصنعة للتشغيل كالتبريد، والكهرباء وغيرها. كما ينبغي أن يجري عليها الصيانة المطلوبة لضمان تشغيلها.</td>
</tr>
</tbody>
</table>
        """
        
        if self.is_saudi_comp():
            res = template
        else:
            res = template1
        return res
    
    def default_amc_scope_en(self):
        template = """ 
        <h2><strong><span style="text-decoration-line: underline; color: blue;">Scope of Maintenance</span></strong></h2>
<table>
<tbody>
<tr>
<td colspan="12" style="text-align: justify;">Note: This section represents maintenance services. They are different from the manufacturer services (such as warranty, subscriptions, and licenses renewals)</td>
</tr>
<tr>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<!-- <td>&nbsp;</td> -->
</tr>
<tr><td colspan="2"><strong>Start Date of Maintenance</strong></td>
<td style="text-align: left;" colspan="10">After Project Completion and Satisfaction of its Payments.<br><br></td></tr>

<tr><td colspan="2"><strong>Duration of Maint.</strong></td>
<td style="text-align: left;" colspan="10">One Year</td></tr>

<tr><td colspan="2" rowspan="2"><strong>Maintenance Level</strong></td>
<td style="text-align: left;" colspan="10">8x5</td></tr>

<tr><td style="text-align: left;" colspan="10">Excluding Public Holidays <br><br></td></tr>

<tr><td colspan="2"><strong>Preventive Maint.</strong></td>
<td style="text-align: left;" colspan="10">Quarterly</td></tr>

<tr><td colspan="2"><strong>No. of Preventive </strong><br><span style="font-weight: 700;">Maintenance</span><span style="font-weight: bold;">&nbsp;/ Year</span></td>
<td style="text-align: left;" colspan="10">4 Each Year</td></tr>

<tr><td colspan="2"><strong>Scope of Services </strong></td>
<td style="text-align: left;" colspan="10">&nbsp;Maintenance</td></tr>

<tr><td colspan="2" rowspan="4"><strong>Remedial&nbsp;</strong><span style="font-weight: 700;">Maintenance</span><br> <br><strong> Devices covered by this service must be covered by manufacturer warranty</strong></td>
<td style="text-align: left;" colspan="10"><strong>Level 1 Support</strong> - Customer Responsibility: <br><br>Problem Reporting and Basic Information<br><br></td></tr>

<tr><td style="text-align: left;" colspan="10"><strong>Level 2 Support</strong> - Beta IT Responsibility:<br><br>Troubleshooting and Workaround<br><br></td></tr>

<tr><td style="text-align: left;" colspan="10"><strong>Level 3 Support</strong> - Beta IT / Manufacturer Responsibility:<br><br>Root Cause Analysis (Provided that Customer has valid warranty and support with manufacturer)<br><br></td></tr>

<tr><td style="text-align: left;" colspan="10"><strong>Level 4 Support</strong> - Manufacturer Responsibility:<br><br> Root access, Engineering, and Development (Requires customer to have valid warranty and support from manufacturer)<br><br></td></tr>

<tr><td colspan="2" rowspan="1"><strong>Warranty</strong><br> <br><strong><br>&nbsp;Devices covered by this service must be covered by manufacturer warranty</strong></td>
<td style="text-align: left;" colspan="10">Beta IT will process RMA process on behalf of customer for malfunctioning devices provided that customer has a valid support contract with manufacturer and as per manufacturer terms and conditions.<br> <br> Material, covered by manufacturer warranty services, is subject to manufacturer warranty and RMA policies, procedures, and RMA repair periods. RMA and Manufactures' support conditions are provided by each manufacturer on its own web site.</td></tr>

<tr><td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
</tr>

<tr>
<td colspan="12">
<h3><span style="text-decoration-line: underline;"><strong>Fault Classification / Response Times</strong></span></h3>
</td>
<!-- <td>&nbsp;</td> -->
</tr>
<br><br>
<tr><td colspan="2"><strong>A. Critical - Service Affecting</strong></td>
<td style="text-align: left;" colspan="10">Any highly critical system or service outage in a live environment that results in severe degradation of overall on-line/off-line network performance.<br><br></td>
</tr>

<tr><td colspan="2">Response Mean: Phone &amp; Email</td>
<td style="text-align: left;" colspan="10">One Business Hour<br><br></td></tr>

<tr><td colspan="2">Response Mean: Remote Access</td>
<td style="text-align: left;" colspan="10">2 Business Hours<br><br></td></tr>

<tr><td colspan="2">Response Mean: On-Site</td>
<td style="text-align: left;" colspan="10">4 Business Hours + Travelling Time<br><br></td></tr>

<tr><td colspan="2"><strong>B. Major - Service Affecting</strong></td>
<td colspan="10">Any major degradation of system or service performance that impacts end user service quality or significantly impairs network operator control or operational effectiveness.<br><br></td>
</tr>

<tr><td colspan="2">Response Mean: Phone &amp; Email</td>
<td style="text-align: left;" colspan="10">One Business Hour<br><br></td></tr>

<tr><td colspan="2">Response Mean: Remote Access</td>
<td style="text-align: left;" colspan="10">4 Business Hours<br><br></td></tr>

<tr><td colspan="2">Response Mean: On-Site</td>
<td style="text-align: left;" colspan="10">7 Business Hours + Travelling Time<br><br></td></tr>

<tr><td colspan="2"><strong>C. Minor - Not-Service Affecting</strong></td>
<td colspan="10">Any minor degradation of system or service performance that does not have any impact on end user service quality and minimal impact on network operations.<br><br></td>
</tr>
<tr><td colspan="2">Response Mean: Phone &amp; Email</td>
<td style="text-align: left;" colspan="10">24 Business Hour<br><br></td></tr>
<tr><td colspan="2">Response Mean: Remote Access</td>
<td style="text-align: left;" colspan="10">48 Business Hour<br><br></td></tr>
<tr><td colspan="2">Response Mean: On-Site</td>
<td style="text-align: left;" colspan="10">72 Business Hours + Travelling Time</td></tr>
<tr><td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
</tr>
<tr>
<td colspan="12">
<h3><strong><span style="text-decoration-line: underline;">Escalation Sequence / Matrix</span></strong></h3>
</td>
</tr>
<tr><td colspan="2" rowspan="2" width="128">Beta IT Helpdesk Contact Information</td>
    <td rowspan="2">Tel: 920006069 <br> Email: <a href="mailto:support.ksa@betait.net">support.ksa@betait.net</a></td>
</tr>
<tr></tr>
<tr>
<td>&nbsp;<br><br></td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
</tr>
<tr>
<td colspan="12"><p style="text-align: justify;"></p>&nbsp;- Any new configuration and configuration changes or additions to configuration will not be covered by this proposal. Moving systems is not covered by this proposal.<br><br></td>
</tr>
<tr><td colspan="12"><p style="text-align: justify;"></p>&nbsp;- Customer DOES NOT have access to Beta IT stock spare parts for workaround solutions during RMA periods.<br><br></td>
</tr>
<tr><td colspan="12"><p style="text-align: justify;"></p>&nbsp;- If the customer requests a job that is not related to the AMC material or services mentioned in this document, then Beta IT reserves the right to not respond to this request and this shall not affect the progress or the due payments.<br><br></td>
</tr>
<tr><td colspan="12"><p style="text-align: justify;"></p>&nbsp;- Beta IT reserves the right to assign, terminate, and re-assign subcontractors in a manner that allows Beta IT to perform the Services as described in the statement of work and in accordance with the terms of this agreement.<br><br></td>
</tr>
<tr><td colspan="12"><p style="text-align: justify;"></p>&nbsp;- Customer shall use and operate the Hardware and/or Software component(s) under this service agreement in accordance with manufacturer’s operating manuals and promptly and regularly carry out all operation maintenance routine as and when specified.</td>
</tr>
</tbody></table>

        """
        
        template1 = """ 
<h2><strong><span style="text-decoration-line: underline; color: blue;">Scope of Maintenance</span></strong></h2>
<table>
<tbody>
<tr>
<td colspan="12" style="text-align: justify;">Note: This section represents maintenance services. They are different from the manufacturer services (such as warranty, subscriptions, and licenses renewals)</td>
</tr>
<tr>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<!-- <td>&nbsp;</td> -->
</tr>
<tr><td colspan="2"><strong>Start Date of Maintenance</strong></td>
<td style="text-align: left;" colspan="10">After Project Completion and Satisfaction of its Payments.<br><br></td></tr>

<tr><td colspan="2"><strong>Duration of Maint.</strong></td>
<td style="text-align: left;" colspan="10">One Year</td></tr>

<tr><td colspan="2" rowspan="2"><strong>Maintenance Level</strong></td>
<td style="text-align: left;" colspan="10">24x7</td></tr>

<tr><td style="text-align: left;" colspan="10">Including Public Holidays <br><br></td></tr>

<tr><td colspan="2"><strong>Preventive Maint.</strong></td>
<td style="text-align: left;" colspan="10">Quarterly</td></tr>

<tr><td colspan="2"><strong>No. of Preventive </strong><br><span style="font-weight: 700;">Maintenance</span><span style="font-weight: bold;">&nbsp;/ Year</span></td>
<td style="text-align: left;" colspan="10">4 Each Year</td></tr>

<tr><td colspan="2"><strong>Scope of Services </strong></td>
<td style="text-align: left;" colspan="10">1. Preventative Maintenance.<br>2. Remedial Maintenance.<br>3. Software/OS Updates &amp; upgrades.<br>4. Additional operational level configurations are excluded from BetaIT SLA Scope of Work.<br>5.&nbsp;RMA as per the purchased principal vendor support/warranty terms &amp; conditions.<br><br></td>

<tr><td colspan="2" rowspan="4"><strong>Remedial&nbsp;</strong><span style="font-weight: 700;">Maintenance</span><br> <br><strong> Devices covered by this service must be covered by manufacturer warranty</strong></td>
<td style="text-align: left;" colspan="10"><strong>Level 1 Support</strong> - Customer Responsibility: <br><br>Problem Reporting and Basic Information<br><br></td></tr>

<tr><td style="text-align: left;" colspan="10"><strong>Level 2 Support</strong> - Beta IT Responsibility:<br><br>Troubleshooting and Workaround<br><br></td></tr>

<tr><td style="text-align: left;" colspan="10"><strong>Level 3 Support</strong> - Beta IT / Manufacturer Responsibility:<br><br>Root Cause Analysis (Provided that Customer has valid warranty and support with manufacturer)<br><br></td></tr>

<tr><td style="text-align: left;" colspan="10"><strong>Level 4 Support</strong> - Manufacturer Responsibility:<br><br> Root access, Engineering, and Development (Requires customer to have valid warranty and support from manufacturer)<br><br></td></tr>

<tr><td colspan="2" rowspan="1"><strong>Warranty</strong><br> <br><strong><br>&nbsp;Devices covered by this service must be covered by manufacturer warranty</strong></td>
<td style="text-align: left;" colspan="10">Beta IT will process RMA process on behalf of customer for malfunctioning devices provided that customer has a valid support contract with manufacturer and as per manufacturer terms and conditions.<br> <br> Material, covered by manufacturer warranty services, is subject to manufacturer warranty and RMA policies, procedures, and RMA repair periods. RMA and Manufactures' support conditions are provided by each manufacturer on its own web site.</td></tr>

<tr><td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
</tr>

<tr>
<td colspan="12">
<h3><span style="text-decoration-line: underline;"><strong>Fault Classification / Response Times</strong></span></h3>
</td>
<!-- <td>&nbsp;</td> -->
</tr>
<br><br>
<tr><td colspan="2"><strong>A. Critical - Service Affecting</strong></td>
<td style="text-align: left;" colspan="10">Any highly critical system or service outage in a live environment that results in severe degradation of overall on-line/off-line network performance.<br><br></td>
</tr>

<tr><td colspan="2">Response Mean: Phone &amp; Email</td>
<td style="text-align: left;" colspan="10">One Business Hour<br><br></td></tr>

<tr><td colspan="2">Response Mean: Remote Access</td>
<td style="text-align: left;" colspan="10">2 Business Hours<br><br></td></tr>

<tr><td colspan="2">Response Mean: On-Site</td>
<td style="text-align: left;" colspan="10">4 Business Hours + Travelling Time<br><br></td></tr>

<tr><td colspan="2"><strong>B. Major - Service Affecting</strong></td>
<td colspan="10">Any major degradation of system or service performance that impacts end user service quality or significantly impairs network operator control or operational effectiveness.<br><br></td>
</tr>

<tr><td colspan="2">Response Mean: Phone &amp; Email</td>
<td style="text-align: left;" colspan="10">One Business Hour<br><br></td></tr>

<tr><td colspan="2">Response Mean: Remote Access</td>
<td style="text-align: left;" colspan="10">4 Business Hours<br><br></td></tr>

<tr><td colspan="2">Response Mean: On-Site</td>
<td style="text-align: left;" colspan="10">7 Business Hours + Travelling Time<br><br></td></tr>

<tr><td colspan="2"><strong>C. Minor - Not-Service Affecting</strong></td>
<td colspan="10">Any minor degradation of system or service performance that does not have any impact on end user service quality and minimal impact on network operations.<br><br></td>
</tr>
<tr><td colspan="2">Response Mean: Phone &amp; Email</td>
<td style="text-align: left;" colspan="10">24 Business Hour<br><br></td></tr>
<tr><td colspan="2">Response Mean: Remote Access</td>
<td style="text-align: left;" colspan="10">48 Business Hour<br><br></td></tr>
<tr><td colspan="2">Response Mean: On-Site</td>
<td style="text-align: left;" colspan="10">72 Business Hours + Travelling Time</td></tr>
<tr><td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
</tr>
<tr>
<td colspan="12">
<h3><strong><span style="text-decoration-line: underline;">Escalation Sequence / Matrix</span></strong></h3>
</td>
</tr>
<tr><td colspan="2" rowspan="2" width="128">Beta IT Helpdesk Contact Information</td>
    <td rowspan="2">Tel: +971 42500111 <br> Email: <a href="mailto:support@betait.net">support@betait.net</a></td>
</tr>
<tr></tr>
<tr>
<td>&nbsp;<br><br></td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
</tr>
<tr>
<td colspan="12"><p style="text-align: justify;"></p>&nbsp;- Any new configuration and configuration changes or additions to configuration will not be covered by this proposal. Moving systems is not covered by this proposal.<br><br></td>
</tr>
<tr><td colspan="12"><p style="text-align: justify;"></p>&nbsp;- Customer DOES NOT have access to Beta IT stock spare parts for workaround solutions during RMA periods.<br><br></td>
</tr>
<tr><td colspan="12"><p style="text-align: justify;"></p>&nbsp;- If the customer requests a job that is not related to the AMC material or services mentioned in this document, then Beta IT reserves the right to not respond to this request and this shall not affect the progress or the due payments.<br><br></td>
</tr>
<tr><td colspan="12"><p style="text-align: justify;"></p>&nbsp;- Beta IT reserves the right to assign, terminate, and re-assign subcontractors in a manner that allows Beta IT to perform the Services as described in the statement of work and in accordance with the terms of this agreement.<br><br></td>
</tr>
<tr><td colspan="12"><p style="text-align: justify;"></p>&nbsp;- Customer shall use and operate the Hardware and/or Software component(s) under this service agreement in accordance with manufacturer’s operating manuals and promptly and regularly carry out all operation maintenance routine as and when specified.</td>
</tr>
</tbody></table>

        """
        
        if self.is_saudi_comp():
            res = template
        else:
            res = template1
        return res
        
        return res
    # def payment_d efaults(self):
    #     line = [{
    #              'payment_name':'Advanced Payment With Order',
    #              'payment_percentage':'40 %'
    #              },
    #             {
    #              'payment_name':'Upon Material Delivery',
    #              'payment_percentage':'40 %'
    #              },
    #               {
    #              'payment_name':'Upon Project Completion',
    #              'payment_percentage':'20 %'
    #              },
    #             {
    #              'payment_name':'Maintenance Contract / AMC',
    #              'payment_percentage':'60% Upon Start of Maintenance, Remaining to be paid on equal values periodically at the beginning of each quarter'
    #              },
    #              {
    #              'payment_name':'Warranty / Subscriptions / Licenses',
    #              'payment_percentage':'In case Warranty Contract / Subscription Licenses are supplied independently then, 100% of its value to be paid advanced'
    #              },
    #             ]
    #     return line

    state = fields.Selection([('draft','Opportunity'),('design_ready','Design Ready'),('submitted','Pipeline'),('commit','Commit'),('returned_by_pmo','Returned By PMO'),
                              ('handover','Hand-Over'),('waiting_po','Waiting PO Locked'),('waiting_po_open','Waiting PO Open'),('returned_by_fin','Returned By Finance'),
                              ('change','Change'),('analytic_change','Redistribute Analytic'),('processed','Processed'),('pmo','Pending Approval'),
                              ('change_processed','Change Processed'),('waiting_po_processed','Waiting PO Processed'),('redistribution_processed','Redistribution Processed'),
                              ('modify','Modify'),('approved','Approved'),('done','Won'),('cancel','Cancelled')],string="Status",default='draft',track_visibility='always')
    ren_filled = fields.Boolean('Ren Filled')
    od_attachement_count = fields.Integer(string="Attachement Count",compute="_od_attachement_count"
                                          )

    #detailed summary Material
    mat_tot_sale = fields.Float('Material Total Sales',readonly=True,track_visibility='always',digits=dp.get_precision('Account'))
    mat_tot_cost = fields.Float('Material Total Cost',readonly=True,digits=dp.get_precision('Account'))
    mat_profit = fields.Float('Material Profit',readonly=True,digits=dp.get_precision('Account'))
    mat_profit_percentage = fields.Float('Material Profit %',readonly=True,digits=dp.get_precision('Account'))
    mat_weight = fields.Float('Material Weight %',compute='_get_weight',store=True,digits=dp.get_precision('Account'))
    mat_vat = fields.Float(string="Material VAT",readonly=True,digits=dp.get_precision('Account'))
    
    
    mat_tot_sale1 = fields.Float('Material Total Sales',readonly=True,digits=dp.get_precision('Account'))
    mat_tot_sale1_ds = fields.Float('Material Total Sales Disc',readonly=True,digits=dp.get_precision('Account'))
    mat_tot_cost1 = fields.Float('Material Total Cost',readonly=True,digits=dp.get_precision('Account'))
    mat_profit1 = fields.Float('Material Profit',readonly=True,digits=dp.get_precision('Account'))
    mat_vat1 = fields.Float(string="Material VAT",readonly=True,digits=dp.get_precision('Account'))
    mat_profit_percentage1 = fields.Float('Material Profit %',readonly=True,digits=dp.get_precision('Account'))
    mat_rebate = fields.Float('Rebate',readonly=True,digits=dp.get_precision('Account'))
    mat_profit_with_rebate = fields.Float('Profit with Rebate',readonly=True,digits=dp.get_precision('Account'))
    mat_profit_with_rebate_perc = fields.Float('Profit with Rebate Percentage',readonly=True,digits=dp.get_precision('Account'))

#detailed summary Material optional
    mat_tot_sale_opt = fields.Float('Material Total Sales',readonly=True,digits=dp.get_precision('Account'))
    mat_tot_cost_opt = fields.Float('Material Total Cost',readonly=True,digits=dp.get_precision('Account'))
    mat_profit_opt = fields.Float('Material Profit',readonly=True,digits=dp.get_precision('Account'))
    mat_profit_percentage_opt = fields.Float('Material Profit %',readonly=True,digits=dp.get_precision('Account'))
    mat_weight_opt = fields.Float('Material Weight %',digits=dp.get_precision('Account'))
    mat_vat_opt = fields.Float(string="Material VAT OPT",readonly=True,digits=dp.get_precision('Account'))

    trn_tot_sale = fields.Float('Training Total Sales',readonly=True,digits=dp.get_precision('Account'))
    trn_tot_cost = fields.Float('Training Total Cost',readonly=True,digits=dp.get_precision('Account'))
    trn_profit = fields.Float('Training Profit',readonly=True,digits=dp.get_precision('Account'))
    trn_profit_percentage = fields.Float('Training Profit %',readonly=True,digits=dp.get_precision('Account'))
    trn_weight = fields.Float('Training Weight %',compute='_get_weight',store=True,digits=dp.get_precision('Account'))
    trn_vat = fields.Float(string="Training Vat",readonly=True,digits=dp.get_precision('Account'))

    trn_tot_sale1 = fields.Float('Training Total Sales',readonly=True,digits=dp.get_precision('Account'))
    trn_tot_sale1_ds = fields.Float('Training Total Sales Disc',readonly=True,digits=dp.get_precision('Account'))
    trn_tot_cost1 = fields.Float('Training Total Cost',readonly=True,digits=dp.get_precision('Account'))
    trn_profit1 = fields.Float('Training Profit',readonly=True,digits=dp.get_precision('Account'))
    trn_profit_percentage1 = fields.Float('Training Profit %',readonly=True,digits=dp.get_precision('Account'))
    trn_vat1 = fields.Float(string="Training Vat",readonly=True,digits=dp.get_precision('Account'))
    trn_rebate = fields.Float('Rebate',readonly=True,digits=dp.get_precision('Account'))
    trn_profit_with_rebate = fields.Float('Profit with Rebate',readonly=True,digits=dp.get_precision('Account'))
    trn_profit_with_rebate_perc = fields.Float('Profit with Rebate Percentage',readonly=True,digits=dp.get_precision('Account'))
    #detailed summary Beta It Manpower Calculation

    bim_tot_sale = fields.Float('Bim Total Sales',readonly=True,digits=dp.get_precision('Account'))
    bim_tot_cost = fields.Float('Bim Total Cost',readonly=True,digits=dp.get_precision('Account'))
    bim_profit = fields.Float('Bim Profit',readonly=True,digits=dp.get_precision('Account'))
    bim_profit_percentage = fields.Float('Bim Profit %',readonly=True,digits=dp.get_precision('Account'))
    bim_weight = fields.Float('Bim Weight %',compute='_get_weight',store=True,digits=dp.get_precision('Account'))
    bim_vat = fields.Float(string="Bim Vat",readonly=True,digits=dp.get_precision('Account'))

    bim_tot_sale1 = fields.Float('Bim Total Sales',readonly=True,digits=dp.get_precision('Account'))
    bim_tot_sale1_ds = fields.Float('Bim Total Sales',readonly=True,digits=dp.get_precision('Account'))
    bim_tot_cost1 = fields.Float('Bim Total Cost',readonly=True,digits=dp.get_precision('Account'))
    bim_profit1 = fields.Float('Bim Profit',readonly=True,digits=dp.get_precision('Account'))
    bim_profit_percentage1 = fields.Float('Bim Profit %',readonly=True,digits=dp.get_precision('Account'))
    bim_vat1 = fields.Float(string="Bim Vat",readonly=True,digits=dp.get_precision('Account'))
    bim_rebate = fields.Float('Rebate',readonly=True,digits=dp.get_precision('Account'))
    bim_profit_with_rebate = fields.Float('Profit with Rebate',readonly=True,digits=dp.get_precision('Account'))
    bim_profit_with_rebate_perc = fields.Float('Profit with Rebate Percentage',readonly=True,digits=dp.get_precision('Account'))
    #detailed summary Outsourced Implementation Service

    oim_tot_sale = fields.Float('Oim Total Sales',readonly=True,digits=dp.get_precision('Account'))
    oim_tot_cost = fields.Float('Oim Total Cost',readonly=True,digits=dp.get_precision('Account'))
    oim_profit = fields.Float('Oim Profit',readonly=True,digits=dp.get_precision('Account'))
    oim_profit_percentage = fields.Float('Oim Profit %',readonly=True,digits=dp.get_precision('Account'))
    oim_weight = fields.Float('Oim Weight %',compute='_get_weight',store=True,digits=dp.get_precision('Account'))
    oim_vat = fields.Float(string="Oim Vat",readonly=True,digits=dp.get_precision('Account'))

    oim_tot_sale1 = fields.Float('Oim Total Sales',readonly=True,digits=dp.get_precision('Account'))
    oim_tot_sale1_ds = fields.Float('Oim Total Sales',readonly=True,digits=dp.get_precision('Account'))
    oim_tot_cost1 = fields.Float('Oim Total Cost',readonly=True,digits=dp.get_precision('Account'))
    oim_profit1 = fields.Float('Oim Profit',readonly=True,digits=dp.get_precision('Account'))
    oim_profit_percentage1 = fields.Float('Oim Profit %',readonly=True,digits=dp.get_precision('Account'))
    oim_vat1 = fields.Float(string="Oim Vat",readonly=True,digits=dp.get_precision('Account'))
    oim_rebate = fields.Float('Rebate',readonly=True,digits=dp.get_precision('Account'))
    oim_profit_with_rebate = fields.Float('Profit with Rebate',readonly=True,digits=dp.get_precision('Account'))
    oim_profit_with_rebate_perc = fields.Float('Profit with Rebate Percentage',readonly=True,digits=dp.get_precision('Account'))
    #detailed summary Beta IT Maintenance Services

    bmn_tot_sale = fields.Float('Bmn Total Sales',readonly=True,digits=dp.get_precision('Account'))
    bmn_tot_cost = fields.Float('Bmn Total Cost',readonly=True,digits=dp.get_precision('Account'))
    bmn_profit = fields.Float('Bmn Profit',readonly=True,digits=dp.get_precision('Account'))
    bmn_profit_percentage = fields.Float('Bmn Profit %',readonly=True,digits=dp.get_precision('Account'))
    bmn_weight = fields.Float('Bmn Weight %',compute='_get_weight',store=True,digits=dp.get_precision('Account'))
    bmn_vat = fields.Float(string="Bmn Vat",readonly=True,digits=dp.get_precision('Account'))

    bmn_tot_sale1 = fields.Float('Bmn Total Sales',readonly=True,digits=dp.get_precision('Account'))
    bmn_tot_sale1_ds = fields.Float('Bmn Total Sales',readonly=True,digits=dp.get_precision('Account'))
    bmn_tot_cost1 = fields.Float('Bmn Total Cost',readonly=True,digits=dp.get_precision('Account'))
    bmn_profit1 = fields.Float('Bmn Profit',readonly=True,digits=dp.get_precision('Account'))
    bmn_profit_percentage1 = fields.Float('Bmn Profit %',readonly=True,digits=dp.get_precision('Account'))
    bmn_vat1 = fields.Float(string="Bmn Vat",readonly=True,digits=dp.get_precision('Account'))
    bmn_rebate = fields.Float('Rebate',readonly=True,digits=dp.get_precision('Account'))
    bmn_profit_with_rebate = fields.Float('Profit with Rebate',readonly=True,digits=dp.get_precision('Account'))
    bmn_profit_with_rebate_perc = fields.Float('Profit with Rebate Percentage',readonly=True,digits=dp.get_precision('Account'))
    #detailed summary Out Sourced Maintenance Service

    omn_tot_sale = fields.Float('Omn Total Sales',readonly=True,digits=dp.get_precision('Account'))
    omn_tot_cost = fields.Float('Omn Total Cost',readonly=True,digits=dp.get_precision('Account'))
    omn_profit = fields.Float('Omn Profit',readonly=True,digits=dp.get_precision('Account'))
    omn_profit_percentage = fields.Float('Omn Profit %',readonly=True,digits=dp.get_precision('Account'))
    omn_weight = fields.Float('Omn Weight %',compute='_get_weight',store=True,digits=dp.get_precision('Account'))
    omn_vat = fields.Float(string="Omn Vat",readonly=True,digits=dp.get_precision('Account'))

    omn_tot_sale1 = fields.Float('Omn Total Sales',readonly=True,digits=dp.get_precision('Account'))
    omn_tot_sale1_ds = fields.Float('Omn Total Sales',readonly=True,digits=dp.get_precision('Account'))
    omn_tot_cost1 = fields.Float('Omn Total Cost',readonly=True,digits=dp.get_precision('Account'))
    omn_profit1 = fields.Float('Omn Profit',readonly=True,digits=dp.get_precision('Account'))
    omn_profit_percentage1 = fields.Float('Omn Profit %',readonly=True,digits=dp.get_precision('Account'))
    omn_vat1 = fields.Float(string="Omn Vat",readonly=True,digits=dp.get_precision('Account'))
    omn_rebate = fields.Float('Rebate',readonly=True,digits=dp.get_precision('Account'))
    omn_profit_with_rebate = fields.Float('Profit with Rebate',readonly=True,digits=dp.get_precision('Account'))
    omn_profit_with_rebate_perc = fields.Float('Profit with Rebate Percentage',readonly=True,digits=dp.get_precision('Account'))
    #detailed summary Operation And Maintenance Service

    o_m_tot_sale = fields.Float('Op Total Sales',readonly=True,digits=dp.get_precision('Account'))
    o_m_tot_cost = fields.Float('Op Total Cost',readonly=True,digits=dp.get_precision('Account'))
    o_m_profit = fields.Float('Op Profit',readonly=True,digits=dp.get_precision('Account'))
    o_m_profit_percentage = fields.Float('Op Profit %',readonly=True,digits=dp.get_precision('Account'))
    o_m_weight = fields.Float('Op Weight %',compute='_get_weight',store=True,digits=dp.get_precision('Account'))
    o_m_vat = fields.Float(string="Op Vat",readonly=True,digits=dp.get_precision('Account'))

    o_m_tot_sale1 = fields.Float('Op Total Sales',readonly=True,digits=dp.get_precision('Account'))
    o_m_tot_sale1_ds = fields.Float('Op Total Sales Disc',readonly=True,digits=dp.get_precision('Account'))
    o_m_tot_cost1 = fields.Float('Op Total Cost',readonly=True,digits=dp.get_precision('Account'))
    o_m_profit1 = fields.Float('Op Profit',readonly=True,digits=dp.get_precision('Account'))
    o_m_profit_percentage1 = fields.Float('Op Profit %',readonly=True,digits=dp.get_precision('Account'))
    o_m_vat1 = fields.Float(string="Op Vat",readonly=True,digits=dp.get_precision('Account'))
    o_m_rebate = fields.Float('Rebate',readonly=True,digits=dp.get_precision('Account'))
    o_m_profit_with_rebate = fields.Float('Profit with Rebate',readonly=True,digits=dp.get_precision('Account'))
    o_m_profit_with_rebate_perc = fields.Float('Profit with Rebate Percentage',readonly=True,digits=dp.get_precision('Account'))
    #revenu
    rev_tot_sale1 = fields.Float('Rev Total Sales',readonly=True,digits=dp.get_precision('Account'))
    rev_tot_cost1 = fields.Float('Rev Total Cost',readonly=True,digits=dp.get_precision('Account'))
    rev_profit1 = fields.Float('Rev Profit',readonly=True,digits=dp.get_precision('Account'))
    rev_profit_percentage1 = fields.Float('Rev Profit %',readonly=True,digits=dp.get_precision('Account'))
    rev_vat1 = fields.Float(string="Op Vat",readonly=True,digits=dp.get_precision('Account'))
    
    #Material11
    des_mat_e = fields.Char(string='Description')
    des_mat_a = fields.Char(string='Description')
    mat_price = fields.Float(string='Total Price',compute='_get_total_sum_price',store=True,digits=dp.get_precision('Account'))
    #implementation
    des_imp_e = fields.Char(string='Description')
    des_imp_a = fields.Char(string='Description')
    imp_price = fields.Float(string='Total Price',compute='_get_total_sum_price',store=True,digits=dp.get_precision('Account'))
    #information secuirity
    info_sec_price = fields.Float(string='Total Price',compute='_get_total_sum_price',store=True,digits=dp.get_precision('Account'))

    #maintanance
    des_maint_e = fields.Char(string='Description')
    des_maint_a = fields.Char(string='Description')
    maint_price = fields.Float(string='Total Price',compute='_get_total_sum_price',store=True,digits=dp.get_precision('Account'))
    #operation and maintance
    des_op_e = fields.Char(string='Description')
    des_op_a = fields.Char(string='Description')
    op_price = fields.Float(string='Total Price',digits=dp.get_precision('Account'))
    


    #Bim Log function Cost Fields
    bim_log_price = fields.Float('Price',compute='compute_bim_log_price',digits=dp.get_precision('Account'))
    bim_log_price_fixed = fields.Float('Price Fixed',digits=dp.get_precision('Account'))
    
    bim_log_cost = fields.Float('Cost',readonly=True,digits=dp.get_precision('Account'))
    bim_log_group = fields.Many2one('od.cost.costgroup.it.service.line',string='Group',copy=True,digits=dp.get_precision('Account'))
    bim_tax_id  = fields.Many2one('account.tax',string="Tax",digits=dp.get_precision('Account'))
    bim_log_vat = fields.Float(string="VAT %",compute="_compute_bim_vat",digits=dp.get_precision('Account'))
    bim_log_vat_value = fields.Float(string="VAT Value",compute="_compute_bim_vat",digits=dp.get_precision('Account'))

    #Default True added by Aslam on 21 Nov 2019 and hide field in view as requested by Elayyan
    bim_log_select = fields.Boolean('Select', default=True)
    bim_imp_select = fields.Boolean('Select')
    bim_full_outsource = fields.Boolean('Full Outsource')
    design_v3= fields.Boolean(string ="Design V3",default=True)
   
    
    
#     @api.onchange('bim_tax_id','bim_log_price')
#     def onchange_vat(self):
#         bim_tax_id = self.bim_tax_id
#         if bim_tax_id:
#             self.bim_log_vat = bim_tax_id.amount
#             self.bim_log_vat_value = self.bim_log_price * bim_tax_id.amount
    @api.one
    @api.depends('bim_tax_id','bim_log_price')
    def _compute_bim_vat(self):
        bim_tax_id = self.bim_tax_id
        if bim_tax_id:
            self.bim_log_vat = bim_tax_id.amount *100
            self.bim_log_vat_value = self.bim_log_price * bim_tax_id.amount
            
    
    #analysis purpose for mamoun
    a_bim_sale = fields.Float('Bim  Sales',readonly=True,digits=dp.get_precision('Account'))
    a_bim_cost = fields.Float('Bim Cost',readonly=True,digits=dp.get_precision('Account'))
    a_bim_cost_original = fields.Float('Bim Cost Original',readonly=True,digits=dp.get_precision('Account'))
    a_bim_profit = fields.Float('Bim Profit',readonly=True,digits=dp.get_precision('Account'))
    a_bim_profit_percentage = fields.Float('Bim Profit %',readonly=True,digits=dp.get_precision('Account'))
    a_bim_vat = fields.Float(string="Bim Vat",readonly=True,digits=dp.get_precision('Account'))
    
    #BIS Added by aslam
    a_bis_sale = fields.Float('Bis  Sales',readonly=True,digits=dp.get_precision('Account'))
    a_bis_cost = fields.Float('Bis Cost',readonly=True,digits=dp.get_precision('Account'))
    a_bis_cost_original = fields.Float('Bis Cost Original',readonly=True,digits=dp.get_precision('Account'))
    a_bis_profit = fields.Float('Bis Profit',readonly=True,digits=dp.get_precision('Account'))
    a_bis_profit_percentage = fields.Float('Bis Profit %',readonly=True,digits=dp.get_precision('Account'))
    a_bis_vat = fields.Float(string="Bis Vat",readonly=True,digits=dp.get_precision('Account'))
    
    #Bmn
    a_bmn_sale = fields.Float('Bmn  Sales',readonly=True,digits=dp.get_precision('Account'))
    a_bmn_cost = fields.Float('Bmn Cost',readonly=True,digits=dp.get_precision('Account'))
    a_bmn_cost_original = fields.Float('Bim Cost Original',readonly=True,digits=dp.get_precision('Account'))
    a_bmn_profit = fields.Float('Bmn Profit',readonly=True,digits=dp.get_precision('Account'))
    a_bmn_profit_percentage = fields.Float('Bmn Profit %',readonly=True,digits=dp.get_precision('Account'))
    a_bmn_vat = fields.Float(string="Bmn Vat",readonly=True,digits=dp.get_precision('Account'))
    
    #
   
    a_total_manpower_sale = fields.Float('Manpower Sales',readonly=True,digits=dp.get_precision('Account'))
    a_total_manpower_cost = fields.Float('Manpower Cost',readonly=True,digits=dp.get_precision('Account'))
    a_total_manpower_profit = fields.Float('Manpower Profit',readonly=True,digits=dp.get_precision('Account'))
    a_total_manpower_profit_percentage= fields.Float('Manpower Profit %',readonly=True,digits=dp.get_precision('Account'))
    a_total_manpower_vat = fields.Float(string="Manpower Vat",readonly=True,digits=dp.get_precision('Account'))
    #O&M
    a_om_sale = fields.Float('Om  Sales',readonly=True,digits=dp.get_precision('Account'))
    a_om_cost = fields.Float('Om Cost',readonly=True,digits=dp.get_precision('Account'))
    a_om_profit = fields.Float('Om Profit',readonly=True,digits=dp.get_precision('Account'))
    a_om_profit_percentage = fields.Float('Om Profit %',readonly=True,digits=dp.get_precision('Account'))
    a_om_vat = fields.Float(string="OM Vat",readonly=True,digits=dp.get_precision('Account'))
    
    #total
    a_tot_sale = fields.Float('Total Sales',readonly=True,digits=dp.get_precision('Account'))
    a_tot_cost = fields.Float('Total Cost',readonly=True,digits=dp.get_precision('Account'))
    a_tot_profit = fields.Float('Total Profit',readonly=True,digits=dp.get_precision('Account'))
    a_tot_profit_percentage = fields.Float('Total Profit %',readonly=True,digits=dp.get_precision('Account'))
    a_tot_vat = fields.Float(string="Total Vat",readonly=True,digits=dp.get_precision('Account'))
    #end
    
    status = fields.Selection([('active','Active'),('revision','Revision'),('cancel','Cancel'),('baseline','Locked')],'Status',required=True,default='active')
    proposal_validity_duration = fields.Text(string="Proposal Validity Starting from its Date")
    show_proposal_validity = fields.Boolean(string="Show To Customer",default=True)
    baseline_sheet_ref = fields.Char("Baseline Cost Sheet Reference",readonly=True)
    date = fields.Date(string="Submission Date",default=fields.Date.today)
    lead_id = fields.Many2one('crm.lead',string='Opportunity',readonly="1",copy=True,required=True)
    lead_created_by = fields.Many2one('res.users',string="Lead Created By",related="lead_id.create_uid",store=True)
    financial_proposal_date = fields.Date(string="Financial Proposal Required On",related="lead_id.od_req_on_7",readonly=True)
    change_date = fields.Datetime(string="Latest Change Date",readonly=True)
    number = fields.Char(string='Number',default='/',readonly="1")
    reviewed_id = fields.Many2one('res.users',string='Owner',readonly=True,track_visibility='always')
    prepared_by = fields.Many2one('res.users',string='Prepared By',required="1",states={'draft':[('readonly',False)]},readonly=True,track_visibility='always')
    od_customer_id = fields.Many2one('res.partner',string='Customer',domain=[('customer','=',True),('is_company','=',True)],required=True,readonly=True,track_visibility='always',related="lead_id.partner_id",store=True)
    od_mat_sale_id = fields.Many2one('sale.order',string="Quotation",readonly=True,copy=False)
    od_ren_sale_id = fields.Many2one('sale.order',string="Quotation",readonly=True,copy=False)
    od_trn_sale_id = fields.Many2one('sale.order',string="Quotation",readonly=True,copy=False)
    od_bim_sale_id = fields.Many2one('sale.order',string="Quotation",readonly=True,copy=False)
    od_oim_sale_id = fields.Many2one('sale.order',string="Quotation",readonly=True,copy=False)
    od_bmn_sale_id = fields.Many2one('sale.order',string="Quotation",readonly=True,copy=False)
    od_omn_sale_id = fields.Many2one('sale.order',string="Quotation",readonly=True,copy=False)
    od_om_res_sale_id = fields.Many2one('sale.order',string="Quotation",readonly=True,copy=False)
    cost_summary_line = fields.One2many('od.cost.summary.line','cost_sheet_id',string='Cost Summary Line',help="Cost Summary",copy=True)
    cost_summary_manufacture_line = fields.One2many('od.cost.summary.manufacture.line','cost_sheet_id',string='Cost Summary Manufacture Line',states={'draft':[('readonly',False)]},readonly=True,copy=True)
    cost_summary_extra_line = fields.One2many('od.cost.summary.extra.line','cost_sheet_id',string='Cost Summary Extra Line',states={'draft':[('readonly',False)]},copy=True)
    cost_summary_version_line = fields.One2many('od.cost.summary.version.line','cost_sheet_id',string='Cost Summary Version Line',states={'draft':[('readonly',False)]},copy=True)
    payment_terms_line = fields.One2many('od.cost.terms.payment.terms.line','cost_sheet_id',string='Payment Terms Line',copy=True,states={'draft':[('readonly',False)]},default=default_payement_term_data)
    credit_terms_line = fields.One2many('od.cost.terms.credit.terms.line','cost_sheet_id',string='Creation Terms Line',copy=True,states={'draft':[('readonly',False)]})
    remarks1 = fields.Text('Remarks')
    remarks2 = fields.Text('Remarks')
    cost_section_line = fields.One2many('od.cost.section.line','cost_sheet_id',string='Cost Section Line',copy=True,states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'commit':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'waiting_po_open':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,default=default_section_material)
    cost_section_option_line = fields.One2many('od.cost.opt.section.line','cost_sheet_id',string='Cost Section Line',copy=True,states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'commit':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'waiting_po_open':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,default=default_section_optional)
    cost_section_trn_line = fields.One2many('od.cost.trn.section.line','cost_sheet_id',string='Cost Section Line',copy=True,states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'commit':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'waiting_po_open':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,default=default_section_training)
    costgroup_it_service_line = fields.One2many('od.cost.costgroup.it.service.line','cost_sheet_id',string='Cost Costgroup It Service Line',copy=True,default=default_beta_service_line,states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'commit':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'waiting_po_open':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True)
    costgroup_material_line = fields.One2many('od.cost.costgroup.material.line','cost_sheet_id',string='Cost Costgroup Material Line',copy=True,states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'commit':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'waiting_po_open':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,default=default_costgroup_material_line)
    costgroup_extra_expense_line = fields.One2many('od.cost.costgroup.extra.expense.line','cost_sheet_id',string='Cost Costgroup Material Line',copy=True,states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'commit':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'waiting_po_open':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,default=default_costgroup_extra_expense_line)
    costgroup_optional_line = fields.One2many('od.cost.costgroup.optional.line.two','cost_sheet_id',string='Cost Costgroup Optional Line',copy=True,states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'commit':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'waiting_po_open':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,default=default_costgroup_optional_line)
    
    
    amc_tech_line = fields.One2many('od.cost.amc.tech.line','cost_sheet_id',string='AMC Technology Line',states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'commit':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'waiting_po_open':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,copy=True)
    imp_tech_line = fields.One2many('od.cost.imp.tech.line','cost_sheet_id',string='Professional Services - Vendors',states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'commit':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'waiting_po_open':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,copy=True)
    om_tech_line = fields.One2many('od.cost.om.tech.line','cost_sheet_id',string='OM Technology Line',states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'commit':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'waiting_po_open':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,copy=True)
    
    ps_vendor_line = fields.One2many('od.cost.ps.vendor.line','cost_sheet_id',string='IMP Technology Line',states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'commit':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'waiting_po_open':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,copy=True)

    
    mp_tech_summary_line = fields.One2many('od.mp.tech.summary.line','cost_sheet_id',string='MP Tech Summary Line',readonly=True)
    
    
    mat_main_pro_line = fields.One2many('od.cost.mat.main.pro.line','cost_sheet_id',string='Mat Main Proposal Line',states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'commit':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'waiting_po_open':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,copy=True)
    mat_optional_item_line = fields.One2many('od.cost.mat.optional.item.line','cost_sheet_id',string='Mat Optional Line',states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'commit':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'waiting_po_open':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,copy=True)
    mat_brand_weight_line = fields.One2many('od.cost.mat.brand.weight','cost_sheet_id',string='Brand Weight',readonly=True)
    mat_group_weight_line = fields.One2many('od.cost.mat.group.weight','cost_sheet_id',string='Group Weight',readonly=True)
    imp_weight_line = fields.One2many('od.cost.impl.group.weight','cost_sheet_id',string='Implementation Weight',readonly=True)
    info_sec_weight_line = fields.One2many('od.cost.bis.group.weight','cost_sheet_id',string='Information Security Weight',readonly=True)
    amc_weight_line = fields.One2many('od.cost.amc.group.weight','cost_sheet_id',string='Implementation Weight',readonly=True)
    om_weight_line = fields.One2many('od.cost.om.group.weight','cost_sheet_id',string='OM Weight',readonly=True)
    extra_weight_line = fields.One2many('od.cost.extra.group.weight','cost_sheet_id',string='Extra Weight',readonly=True)
    summary_weight_line = fields.One2many('od.cost.summary.group.weight','cost_sheet_id',string='Summary Weight',readonly=True)
    original_summary_weight_line = fields.One2many('od.cost.original.summary.group.weight','cost_sheet_id',string='Summary Weight',readonly=True)

    
    mat_extra_expense_line = fields.One2many('od.cost.mat.extra.expense.line','cost_sheet_id',string='Mat Extra Expense Line',states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'commit':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'waiting_po_open':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,copy=True)
    
    
    vendor_rebate_line = fields.One2many('principle.vendor.rebate','cost_sheet_id',string='Principle Vendors Rebate',states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'commit':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'waiting_po_open':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,copy=True)

    amc_analytic_line = fields.One2many('od.amc.analytic.lines','cost_sheet_id',string='AMC Analytic Lines',readonly=True,copy=False)
    om_analytic_line = fields.One2many('od.om.analytic.lines','cost_sheet_id',string='AMC Analytic Lines',readonly=True,copy=False)
    
    show_sec_sub_tot = fields.Boolean(string='Show Section Sub-total',default=True)
    show_to_customer_main_proposal = fields.Boolean(string='Show to Customer',default=True)
    show_to_opt = fields.Boolean(string='Show to Customer',default=False)
    show_mat_ext_exp =fields.Boolean(string='Show to Customer',default=False)
    show_to_customer_optional_proposal = fields.Boolean(string='Show to Customer',default=False)
    show_to_customer_mat_delivery = fields.Boolean(string='Show to Customer',default=True)
    show_to_customer_material_notes = fields.Boolean(string='Show to Customer',default=True)
    show_to_customer_bmn_eqp = fields.Boolean(string='Show to Customer',default=False)
    show_to_customer_omn_eqp = fields.Boolean(string='Show to Customer',default=False)
    show_to_customer_o_m_eqp = fields.Boolean(string='Show to Customer',default=False)
    show_to_customer_payment = fields.Boolean(string='Show to Customer',default=True)
    show_to_customer_credit = fields.Boolean(string='Show to Customer',default=False)
    material_delivery_terms = fields.Text(string='Material Delivery Terms',states={'draft':[('readonly',False)]},default="*Expected Delivery Period for Proposed Items is 4-6 Weeks\n* Default Warranty starts from the shipment date (from vendor factories) and not from installation date. Vendors Default warranty terms & conditions apply during this period. For extended warranty Terms & conditions, Vendors service contracts/certificates to be purchased. For Local Support, Beta IT Support Services should be purchased (such as Preventive Maintenance and Remedial Maintenance). \
\n* Electronic Licenses and Manufacturer Services will not be delivered as part of the material because they only represent codes which will be activated at the vendor site.")
    # material_notes = fields.Text(string='Material Notes',states={'draft':[('readonly',False)]},default="Expected Delivery Period for Proposed Items is 4-6 Weeks")
    included_in_quotation = fields.Boolean(string='Included In Quotation',default=False)
    ren_main_pro_line = fields.One2many('od.cost.ren.main.pro.line','cost_sheet_id',string='Ren Main Proposal Line',copy=True,states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'commit':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'waiting_po_open':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True)
    ren_optional_item_line = fields.One2many('od.cost.ren.optional.item.line','cost_sheet_id',string='Ren Optional Line',copy=True,states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'commit':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'waiting_po_open':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True)
    bmn_eqp_cov_line = fields.One2many('od.bmn.eqp.cov.line','cost_sheet_id',string='BMN Equipment Covered by The Scope of Service',copy=True,states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'commit':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'waiting_po_open':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True)
    omn_eqp_cov_line = fields.One2many('od.omn.eqp.cov.line','cost_sheet_id',string='OMN Equipment Covered by The Scope of Service',copy=True,states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'commit':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'waiting_po_open':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True)
    o_m_eqp_cov_line = fields.One2many('od.o_m.eqp.cov.line','cost_sheet_id',string='OM Equipment Covered by The Scope of Service',copy=True,states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'commit':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'waiting_po_open':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True)
    bim_implementation_code_line = fields.One2many('od.cost.bim.beta.implementation.code','cost_sheet_id',string='Bim Implementation Code Line',copy=True,states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'commit':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'waiting_po_open':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True)



    included_in_quotation_ren = fields.Boolean(string='Included In Quotation',default=False)
    renewal_quotes = fields.Html(string='Notes')
    show_to_customer_ren_main = fields.Boolean(string='Show to Customer',default=True)
    show_to_customer_ren_optional = fields.Boolean(string='Show to Customer',default=False)
    show_to_customer_ren_notes = fields.Boolean(string='Show to Customer',default=True)

    #trn
    trn_customer_training_line = fields.One2many('od.cost.trn.customer.training.line','cost_sheet_id',string='Trn Customer Training Line',states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'commit':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'waiting_po_open':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,copy=True)
    # trn_customer_training_optional_line = fields.One2many('od.cost.trn.optional.line','cost_sheet_id',string='Trn Customer Optional Training Line',readonly=True, states={'draft':[('readonly',False)]})
    trn_customer_training_extra_expense_line = fields.One2many('od.cost.trn.customer.training.extra.expense.line','cost_sheet_id',string='Trn Customer Extra Expense Line',copy=True,states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'commit':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'waiting_po_open':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True)
    included_trn_in_quotation = fields.Boolean(string='Included In Quotation',default=False)
    show_customer_trn_training_details = fields.Boolean(string='Show to Customer',default=True)
    show_customer_trn_terms_condition = fields.Boolean(string='Show to Customer',default=True)
    show_trn_training_extra_expenses = fields.Boolean(string='Show to Customer',default=False,states={'draft':[('readonly',False)]})
    trn_terms_condition = fields.Html(string='Terms And Condition',states={'draft':[('readonly',False)]},default="Training Provided does not cover examination fees and it does not include travelling & accommodation expenses if required.")

    #bim
    included_bim_in_quotation = fields.Boolean(string='Included In Quotation',default=False)
    show_customer_bim_exclusion = fields.Boolean(string='Show to Customer',default=True)
    show_customer_bim_manpower_calc = fields.Boolean(string='Show to Customer',default=False)
    bim_exclusion_note = fields.Html(string='Remarks',default=default_exclusion_note)
    show_customer_bim_inclusion = fields.Boolean(string='Show to Customer',default=True)
    show_bim_log_eqn = fields.Boolean(string='Show to Customer')
    show_bim_extra_exp = fields.Boolean(string='Show to Customer')
    show_imp_code = fields.Boolean(string='Show to Customer')
    show_oim_extra_exp = fields.Boolean(string='Show to Customer')
    show_ps_vendor_exp = fields.Boolean(string='Show to Customer')
    bim_inclusion_note = fields.Html(string='Remarks',default=False)
    implimentation_extra_expense_line = fields.One2many('od.cost.bim.beta.implimentation.extra.expense.line','cost_sheet_id',string='Bim Extra Expense Line',states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'commit':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'waiting_po_open':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,copy=True)
    manpower_manual_line = fields.One2many('od.cost.bim.beta.manpower.manual.line','cost_sheet_id',string='Bim Manpower Manual Line',states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'commit':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'waiting_po_open':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,copy=True)
    #OIM
    included_oim_in_quotation = fields.Boolean(string='Included In Quotation',default=False)
    show_oim_ex_outsourced_scope = fields.Boolean(string='Show to Customer',default=True)
    oim_ex_outsourced_scope = fields.Text(string='Remarks',default=False)
    show_oim_in_outsourced_scope = fields.Boolean(string='Show to Customer',default=True)
    oim_in_outsourced_scope = fields.Text(string='Remarks',default=False)
    show_oim_outsourced_price = fields.Boolean(string='Show to Customer',default=False)
    oim_implimentation_price_line = fields.One2many('od.cost.oim.implimentation.price.line','cost_sheet_id',string='Oim Implimentation Price Line',states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'commit':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'waiting_po_open':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,copy=True)
    oim_extra_expenses_line = fields.One2many('od.cost.oim.extra.expenses.line','cost_sheet_id',string='Oim Extra Expense Line',states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'commit':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'waiting_po_open':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,copy=True)
    #o&m
    included_om_in_quotation = fields.Boolean(string='Included In Quotation',default=False)
    show_om_residenteng_cust = fields.Boolean(string='Show to Customer')
    om_residenteng_line = fields.One2many('od.cost.om.residenteng.line','cost_sheet_id',string='Om Resident Eng Line',states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'commit':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'waiting_po_open':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,copy=True,default=default_resident_eng_line)
    show_om_eqpmntreqst_cust = fields.Boolean(string='Show to Customer',default=False)
    om_eqpmentreq_line = fields.One2many('od.cost.om.eqpmentreq.line','cost_sheet_id',string='Om Equipment Request Line',states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'commit':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'waiting_po_open':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,copy=True)
    show_om_exclusion_cust = fields.Boolean(string='Show to Customer',default=True)
    om_ex_works_note = fields.Html(string='Remarks',default=False)
    show_om_extra_exp = fields.Boolean(string='Show to Customer')
    show_om_inclusion_cust = fields.Boolean(string='Show to Customer',default=True)
    om_in_works_note = fields.Html(string='Remarks',default=False)
    om_extra_line = fields.One2many('od.cost.om.extra.line','cost_sheet_id',string='Om Extra Line',states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'commit':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'waiting_po_open':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,copy=True)
    #OMN
    included_omn_in_quotation = fields.Boolean(string='Included In Quotation',default=False)
    show_to_cust_omn_maintanance = fields.Boolean(string='Show to Customer',default=False)

    omn_level = fields.Char(string='Level')
    omn_year_month = fields.Selection([('week','Week'),('month','Month'),('year','Year')],'Week, Month or Year') #FA
    omn_number = fields.Integer('Number')
    omn_public_holiday = fields.Boolean('Public Holidays')
    omn_start_date = fields.Date('Omn Start Date')
    omn_end_date = fields.Date('Omn End Date')
    omn_comment = fields.Char('Omn Comment')
    #O_M
    o_m_level = fields.Char(string='Level')
    o_m_year_month = fields.Selection([('week','Week'),('month','Month'),('year','Year')],'Week, Month or Year') #FA
    o_m_number = fields.Integer('Number')
    o_m_public_holiday = fields.Boolean('Public Holidays')
    o_m_start_date = fields.Date('Om Start Date')
    o_m_end_date = fields.Date('Om End Date')
    o_m_comment = fields.Char('Om Comment')
#     omn_year = fields.Selection([(num, str(num)) for num in range(1990, (datetime.now().year)+1 )], 'Year')
    show_to_cust_omn_maintance_price = fields.Boolean(string='Show to Customer',default=False)
    omn_out_preventive_maintenance_line = fields.One2many('od.cost.omn.out.preventive.maintenance.line','cost_sheet_id',string='Omn Preventive Maintenance Line',states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'commit':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'waiting_po_open':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,copy=True)
    show_to_cust_omn_remedial_maintenance = fields.Boolean(string='Show to Customer',default=False)
    omn_out_remedial_maintenance_line = fields.One2many('od.cost.omn.out.remedial.maintenance.line','cost_sheet_id',string='Omn Remedial Maintenance Line',states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'commit':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'waiting_po_open':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,copy=True)
    show_to_cust_remarks = fields.Boolean(string='Show to Customer',default=True)
    omn_remarks = fields.Text(string='Remarks',default="* Devices covered by Beta IT maintenance services must be covered by valid manufacturer warranty & TAC support\n\n* Level 1 Support - Customer Responsibility (Problem Reporting and Basic Information)\n* Level 2 Support - Beta IT Responsibility (Troubleshooting and Workaround)\n* Level 3 Support - Beta IT / Manufacturer Responsibility (Root Cause Analysis)\n* Level 4 Support - Manufacturer Responsibility (Root access, Engineering, and Development)\n* Warranty - Devices covered by this service must be covered by manufacturer warranty: Beta IT will process RMA process on behalf of customer for malfunctioning devices provided that customer has a valid support contract with manufacturer and as per manufacturer terms and conditions. Material, covered by manufacturer warranty services, is subject to manufacturer warranty and RMA policies, procedures, and RMA repair periods. RMA and Manufactures' support conditions are provided by each manufacturer on its own web site.\n* Fault Classification / Response Times:\n\t\tA. Critical (service affecting) - Response Means: Phone & Email (One Business Hour), Response Means: Remote Access (2 Business Hours), Response Means: On-Site (4 Business Hours + Travelling Time)\n\t\tB. Major (service affecting): Response Means: Phone & Email (One Business Hour), Response Means: Remote Access (4 Business Hours), Response Means: On-Site (7 Business Hours + Travelling Time)\n\t\tC. Minor (non-service affecting): Response Means: Phone & Email (24 Business Hour), Response Means: Remote Access (48 Business Hours), Response Means: On-Site (72 Business Hours + Travelling Time)\n\n* Escalation Sequence / Matrix\n\t\tLevel A. Beta IT Helpdesk (United Arab Emirates: +971 4 250 0111 support@betait.net / Saudi Arabia: 920006069 support@sa.betait.net)\n\t\tLevel B. Beta IT Technical Department (United Arab Emirates:  +971 4 706 1111 td@betait.net / Saudi Arabia: +966 11 200 6066 td@sa.betait.net)\n\t\tLevel C. Head of Operations (United Arab Emirates:  +971 4 706 1111 mohd.elayyan@betait.net / Saudi Arabia: +966 11 200 6066 fakhri.amaireh@sa.betait.net) ")
    show_to_cust_spare_parts = fields.Boolean(string='Show to Customer',default=False)
    omn_spare_parts_line = fields.One2many('od.cost.omn.spare.parts.line','cost_sheet_id',string='Omn Spare Parts Line',states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'commit':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'waiting_po_open':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,copy=True)
    omn_maintenance_extra_expense_line = fields.One2many('od.cost.omn.maintenance.extra.expense.line','cost_sheet_id',string='Omn Extra Expense Line',states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'commit':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'waiting_po_open':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,copy=True)
    #BMN
    included_bmn_in_quotation = fields.Boolean(string='Included In Quotation',default=False)
    show_to_cust_bmn_maintanance = fields.Boolean(string='Show to Customer',default=False)


    bmn_level = fields.Char(string='Level')
    bmn_year_month = fields.Selection([('week','Week'),('month','Month'),('year','Year')],'Week, Month or Year') #FA
    bmn_public_holiday = fields.Boolean('Public Holidays')
    bmn_number = fields.Integer('Number')
    bmn_start_date = fields.Date('Bmn Start Date')
    bmn_end_date = fields.Date('Bmn End Date')
    bmn_comment = fields.Char('Bmn Comment')
#     bmn_year = fields.Selection([(num, str(num)) for num in range(1990, (datetime.now().year)+1 )], 'Year')
    show_bmn_it_preventive_line = fields.Boolean(string='Show to Customer',default=False)
    bmn_it_preventive_line = fields.One2many('od.cost.bmn.it.preventive.line','cost_sheet_id',string='Bmn It Preventive Line',states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'commit':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'waiting_po_open':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,copy=True)
    show_bmn_it_remedial_line = fields.Boolean(string='Show to Customer',default=False)
    bmn_it_remedial_line = fields.One2many('od.cost.bmn.it.remedial.line','cost_sheet_id',string='Bmn It Remedial Line',states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'commit':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'waiting_po_open':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,copy=True)
    show_bmn_scope_maintanance = fields.Boolean(string='Show to Customer',default=True)
    bmn_beta_it_maintanance = fields.Html(string='Remarks',default=default_amc_scope)
    bmn_beta_it_maintanance_en = fields.Html(string='Remarks',default=default_amc_scope_en)
    show_to_cust_bmn_beta_spareparts = fields.Boolean(string='Show to Customer',default=False)
    bmn_spareparts_beta_it_maintenance_line = fields.One2many('od.cost.bmn.spareparts.beta.it.maintenance.line','cost_sheet_id',string='Bmn Spareparts Line',states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'commit':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'waiting_po_open':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,copy=True)
    bmn_beta_it_maintenance_extra_expense_line = fields.One2many('od.cost.bmn.beta.it.maintenance.extra.expense.line','cost_sheet_id',string='Bmn Extra Expense Line',states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'commit':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'waiting_po_open':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,copy=True)
    # customer_closing_line = fields.One2many('od.customer.closing.line','cost_sheet_id',string='Customer Closing Condition Line',copy=True,states={'draft':[('readonly',False)],'submitted':[('readonly',False)],'commit':[('readonly',False)],'handover':[('readonly',False)],'processed':[('readonly',False)]},readonly=True)
    # beta_closing_line = fields.One2many('od.beta.closing.line','cost_sheet_id',string='Customer Closing Condition Line',copy=True,states={'draft':[('readonly',False)],'submitted':[('readonly',False)],'commit':[('readonly',False)],'handover':[('readonly',False)],'processed':[('readonly',False)]},readonly=True)
    closing_condition_ids = fields.Many2many('od.beta.closing.conditions','rel_costsheet_condition','costsheet_id','condition_id',string="Closing Conditions")
    closing_fin_comment_id  = fields.Many2one('od.finance.comment','Finance Comment')
    od_order_type_id = fields.Many2one('od.order.type',string='Order Type',domain=[('type','=','so')])
    type_mat = fields.Many2one('od.order.type',string='Order Type',domain=[('type','=','so')])
    type_ren = fields.Many2one('od.order.type',string='Order Type',domain=[('type','=','so')])
    type_trn = fields.Many2one('od.order.type',string='Order Type',domain=[('type','=','so')])
    type_bim = fields.Many2one('od.order.type',string='Order Type',domain=[('type','=','so')])
    type_oim = fields.Many2one('od.order.type',string='Order Type',domain=[('type','=','so')])
    type_bmn = fields.Many2one('od.order.type',string='Order Type',domain=[('type','=','so')])
    type_omn = fields.Many2one('od.order.type',string='Order Type',domain=[('type','=','so')])
    type_o_m = fields.Many2one('od.order.type',string='Order Type',domain=[('type','=','so')])

#project fields

    project_mat  = fields.Many2one('account.analytic.account',string='Project',domain=[('type','=','contract'),('state','=','open')])
    project_ren  = fields.Many2one('account.analytic.account',string='Project',domain=[('type','=','contract'),('state','=','open')])
    project_trn  = fields.Many2one('account.analytic.account',string='Project',domain=[('type','=','contract'),('state','=','open')])
    project_bim  = fields.Many2one('account.analytic.account',string='Project',domain=[('type','=','contract'),('state','=','open')])
    project_oim  = fields.Many2one('account.analytic.account',string='Project',domain=[('type','=','contract'),('state','=','open')])
    project_bmn  = fields.Many2one('account.analytic.account',string='Project',domain=[('type','=','contract'),('state','=','open')])
    project_omn  = fields.Many2one('account.analytic.account',string='Project',domain=[('type','=','contract'),('state','=','open')])
    project_o_m  = fields.Many2one('account.analytic.account',string='Project',domain=[('type','=','contract'),('state','=','open')])
    
    price_fixed = fields.Boolean(string="Price Fixed")
    
#IS FIELDS
    info_sec_tech_line = fields.One2many('od.cost.is.tech.line','cost_sheet_id',string='Information Secuirity - Additional Services',states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'commit':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'waiting_po_open':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,copy=True)
    info_sec_extra_expense_line = fields.One2many('od.cost.is.extra.expense.line','cost_sheet_id',string='Bim Extra Expense Line',states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'commit':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'waiting_po_open':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,copy=True)
    info_sec_subcontractor_line = fields.One2many('od.cost.is.subcontractor.line','cost_sheet_id',string='Oim Extra Expense Line',states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'commit':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'waiting_po_open':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,copy=True)
    info_sec_vendor_line = fields.One2many('od.cost.is.vendor.line','cost_sheet_id',string='IMP Technology Line',states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'commit':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'waiting_po_open':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,copy=True)
    
    included_info_sec_in_quotation = fields.Boolean(string='Included In Quotation',default=False)
    show_customer_info_sec_exclusion = fields.Boolean(string='Show to Customer',default=True)
    info_sec_exclusion_note = fields.Html(string='Remarks',default=default_exclusion_note)
    show_customer_info_sec_inclusion = fields.Boolean(string='Show to Customer',default=True)
    info_sec_inclusion_note = fields.Html(string='Remarks',default=False)
    show_info_sec_vendor_exp = fields.Boolean(string='Show to Customer')
    
    #Detailed summary Beta IT Information Secuirity
    bis_tot_sale = fields.Float('Bis Total Sales',readonly=True,digits=dp.get_precision('Account'))
    bis_tot_cost = fields.Float('Bis Total Cost',readonly=True,digits=dp.get_precision('Account'))
    bis_profit = fields.Float('Bis Profit',readonly=True,digits=dp.get_precision('Account'))
    bis_profit_percentage = fields.Float('Bis Profit %',readonly=True,digits=dp.get_precision('Account'))
    bis_weight = fields.Float('Bis Weight %',compute='_get_weight',store=True,digits=dp.get_precision('Account'))
    bis_vat = fields.Float(string="Bis Vat",readonly=True,digits=dp.get_precision('Account'))

    bis_tot_sale1 = fields.Float('Bis Total Sales',readonly=True,digits=dp.get_precision('Account'))
    bis_tot_sale1_ds = fields.Float('Bis Total Sales',readonly=True,digits=dp.get_precision('Account'))
    bis_tot_cost1 = fields.Float('Bis Total Cost',readonly=True,digits=dp.get_precision('Account'))
    bis_profit1 = fields.Float('Bis Profit',readonly=True,digits=dp.get_precision('Account'))
    bis_profit_percentage1 = fields.Float('Bim Profit %',readonly=True,digits=dp.get_precision('Account'))
    bis_vat1 = fields.Float(string="Bis Vat",readonly=True,digits=dp.get_precision('Account'))
    bis_rebate = fields.Float('Bis Rebate',readonly=True,digits=dp.get_precision('Account'))
    bis_profit_with_rebate = fields.Float('Bis Profit with Rebate',readonly=True,digits=dp.get_precision('Account'))
    bis_profit_with_rebate_perc = fields.Float('Bis Profit with Rebate Percentage',readonly=True,digits=dp.get_precision('Account'))
    #Detailed summary Outsourced Information Secuirity

    ois_tot_sale = fields.Float('Ois Total Sales',readonly=True,digits=dp.get_precision('Account'))
    ois_tot_cost = fields.Float('Ois Total Cost',readonly=True,digits=dp.get_precision('Account'))
    ois_profit = fields.Float('Ois Profit',readonly=True,digits=dp.get_precision('Account'))
    ois_profit_percentage = fields.Float('Ois Profit %',readonly=True,digits=dp.get_precision('Account'))
    ois_weight = fields.Float('Ois Weight %',compute='_get_weight',store=True,digits=dp.get_precision('Account'))
    ois_vat = fields.Float(string="Ois Vat",readonly=True,digits=dp.get_precision('Account'))

    ois_tot_sale1 = fields.Float('Ois Total Sales',readonly=True,digits=dp.get_precision('Account'))
    ois_tot_sale1_ds = fields.Float('Ois Total Sales',readonly=True,digits=dp.get_precision('Account'))
    ois_tot_cost1 = fields.Float('Ois Total Cost',readonly=True,digits=dp.get_precision('Account'))
    ois_profit1 = fields.Float('Ois Profit',readonly=True,digits=dp.get_precision('Account'))
    ois_profit_percentage1 = fields.Float('Ois Profit %',readonly=True,digits=dp.get_precision('Account'))
    ois_vat1 = fields.Float(string="Ois Vat",readonly=True,digits=dp.get_precision('Account'))
    ois_rebate = fields.Float('Ois Rebate',readonly=True,digits=dp.get_precision('Account'))
    ois_profit_with_rebate = fields.Float('Ois Profit with Rebate',readonly=True,digits=dp.get_precision('Account'))
    ois_profit_with_rebate_perc = fields.Float('Ois Profit with Rebate Percentage',readonly=True,digits=dp.get_precision('Account'))
    

    
    
    def get_analytic_state(self):
        return      [             
             ('template', 'Template'),
             ('draft','New'),
             ('open','In Progress'),
            ('pending','To Renew'),
             ('close','Closed'),
            ('cancelled', 'Cancelled')
                    ]

 #Related Analytic_state
    
    
    
    project_mat_state  = fields.Selection(get_analytic_state,string='Mat Analtyic State',related="project_mat.state" ,readonlyt=True)
    project_ren_state  = fields.Selection(get_analytic_state,string='Ren Analtyic State',related="project_ren.state",readonlyt=True)
    project_trn_state  = fields.Selection(get_analytic_state,string='Trn Analtyic State',related="project_trn.state",readonlyt=True)
    project_bim_state  = fields.Selection(get_analytic_state,string='Bim Analtyic State',related="project_bim.state",readonlyt=True)
    project_oim_state  = fields.Selection(get_analytic_state,string='Oim Analtyic State',related="project_oim.state",readonlyt=True)
    project_bmn_state  = fields.Selection(get_analytic_state,string='Bmn Analtyic State',related="project_bmn.state",readonlyt=True)
    project_omn_state  = fields.Selection(get_analytic_state,string='Omn Analtyic State',related="project_omn.state",readonlyt=True)
    project_o_m_state  = fields.Selection(get_analytic_state,string='OM Analtyic State',related="project_o_m.state",readonlyt=True)
    
    x_bim_tech_show = fields.Boolean(string="Show To Customer")

# fields for comm
    comm_made_to_customer = fields.Text('Commitments I Made Customer or Suppliers')
    # comm_made_to_me = fields.Text('Commitments Made to Me by Customer or Suppliers')

    
    
        
    def write_analytic_map_sale_order_v3(self,anal_maped_dict,so_vals,so_line_map,so_line_val):
        if self.design_v3:
            order_line = so_line_val
            sale_id = self.od_mat_sale_id
            self.write_sale_order_line(sale_id,order_line)
        else:
            self.write_analytic_map_sale_order(anal_maped_dict, so_vals, so_line_map,so_line_val)
    
    
    def apply_discount_create_v3(self,so_line_val,discount):
        total_selling_price =0.0
        discount_to_apply=0.0
        for _,_,item in so_line_val:
            price = item.get('price_unit',0.0)
            qty = item.get('product_uom_qty',0.0)
            total_selling_price += price * qty
       
        for _,_,res in so_line_val:
            price_unit = res.get('price_unit',0.0)
            discount_to_apply = 0
            if total_selling_price:
                discount_to_apply = (price_unit/total_selling_price)*discount
            new_price = price_unit + discount_to_apply
            res['price_unit'] = new_price
            res['od_original_price'] = new_price
        return so_line_val



    @api.model
    def create(self,vals):
        lead_id = self.env.context.get('default_lead_id')
        costsheets = self.search([('lead_id','=',lead_id)])
        lead_obj = self.env['crm.lead'].browse(lead_id)
        lead_number = lead_obj.od_number
        cst_sheet_count = len(costsheets) + 1
        if lead_id:
            if vals.get('status') == 'active':
                old_cost_sheets = self.search([('status','=','active'),('lead_id','=',lead_id)])
                if len(old_cost_sheets) > 0:
                    raise Warning('Active Cost Sheet for Each Lead Must Be Unique')
        if vals.get('number','/')=='/':
#             vals['number'] = self.env['ir.sequence'].get('od.cost.sheet') or '/'
            vals['number'] = lead_number + '-' + str(cst_sheet_count)
        presale = vals.get('pre_sales_engineer')
        return super(od_cost_sheet, self).create( vals)

    @api.multi
    def write(self,vals):

        if vals.get('status') == 'active':
            lead_id = self.lead_id and self.lead_id.id
            old_cost_sheets = self.search([('status','=','active'),('lead_id','=',lead_id)])
            if len(old_cost_sheets) > 0:
                raise Warning('Active Cost Sheet for Each Lead Must Be Unique')            
        return super(od_cost_sheet,self).write(vals)
    @api.one
    def recalculate(self):
        for line in self.mat_main_pro_line:
            line._compute_currency_supp_discount()
            line._compute_supplier_discount()
            line._compute_unit_price()
#             line.onchange_vat()
        for line in self.trn_customer_training_line:
            line._compute_currency_supp_discount()
            line._compute_supplier_discount()
            line._compute_unit_price()
#             line.onchange_vat()


    def check_order_type(self):
        if not self.included_in_quotation:
            raise Warning("MAT tab Included In Quotation Not Ticked")
        if not self.type_mat.id:
            raise Warning("MAT tab Order Type Not Selected")
        if not self.project_mat:
            raise Warning("MAT tab Project Not Selected")

    def map_analytic_acc(self,anal_dict):
        res = {}
        result = {}
        for key,value in anal_dict.iteritems():
            res.setdefault(value,[]).append(key)
        for key,value in res.iteritems():
            if key:
                result[key] = value
        return result

    def sum_grouped_pdt(self,result):
        res = []
        for vals in result:
            prices =sum(vals['prices'])
            costs =sum(vals['costs'])
            qty = sum(vals['quants'])
            sup_prices = sum(vals['sup_prices'])
            unit_sup_price = sup_prices/(qty or 1.0)
            unit_price = prices/qty
            unit_cost = costs/qty
            vals['product_uom_qty'] = qty
            vals['od_original_qty'] = qty
            vals['price_unit'] = unit_price
            vals['od_original_price'] = unit_price
            vals['purchase_price'] = unit_cost
            vals['od_original_unit_cost'] = unit_cost
            vals['od_sup_unit_cost'] =unit_sup_price
            vals['od_sup_line_cost'] =sup_prices
            if vals.get('tax_id') == [[6,False,[False]]]:
                vals['tax_id'] = False
            res.append((0,0,vals))
        return res

    def od_deduplicate_pdt(self,l):
        '''
        group same products  to single items,price_unit sum and and divid by qty
         '''
        result = []
        for _,_,item in l :
            check = False
            for r_item in result :
                if item['product_id'] == r_item['product_id'] :
                    check = True
                    sup_prices = r_item['sup_prices']
                    sup_prices.append(item['od_sup_unit_cost'] * item['product_uom_qty'])
                    prices = r_item['prices']
                    prices.append(item['price_unit']*item['product_uom_qty'])
                    r_item['prices'] =prices
                    costs = r_item['costs']
                    costs.append(item['purchase_price']*item['product_uom_qty'])
                    r_item['costs'] = costs
                    quants = r_item['quants']
                    quants.append(item['product_uom_qty'])
                    r_item['quants'] = quants
            if check == False :
                item['prices'] = [item['price_unit'] * item['product_uom_qty']]
                item['costs'] = [item['purchase_price']  * item['product_uom_qty']]
                item['quants'] =[item['product_uom_qty']]
                item['sup_prices'] = [item['od_sup_unit_cost'] * item['product_uom_qty']]
                result.append( item )
        result = self.sum_grouped_pdt(result)
        return result


    def get_so_tab_map(self):
        so_analyti_map = {}
        od_mat_sale_id =  self.od_mat_sale_id and self.od_mat_sale_id.id or False
        if od_mat_sale_id:
            mat_analytic = self.od_mat_sale_id and self.od_mat_sale_id.project_id and self.od_mat_sale_id.project_id.id
            so_analyti_map[od_mat_sale_id] = mat_analytic
        od_trn_sale_id =  self.od_trn_sale_id and self.od_trn_sale_id.id or False
        if od_trn_sale_id:
            trn_analytic = self.od_trn_sale_id and self.od_trn_sale_id.project_id and self.od_trn_sale_id.project_id.id
            so_analyti_map[od_trn_sale_id] = trn_analytic
        od_bim_sale_id =  self.od_bim_sale_id and self.od_bim_sale_id.id or False
        if od_bim_sale_id:
            imp_analytic = self.od_bim_sale_id and self.od_bim_sale_id.project_id and self.od_bim_sale_id.project_id.id
            so_analyti_map[od_bim_sale_id] = imp_analytic
        od_bmn_sale_id =  self.od_bmn_sale_id and self.od_bmn_sale_id.id or False
        if od_bmn_sale_id:
            amc_analytic = self.od_bmn_sale_id and self.od_bmn_sale_id.project_id and self.od_bmn_sale_id.project_id.id
            so_analyti_map[od_bmn_sale_id] = amc_analytic
        od_om_res_sale_id = self.od_om_res_sale_id and self.od_om_res_sale_id.id or False
        if od_om_res_sale_id:
            o_m_analytic = self.od_om_res_sale_id and self.od_om_res_sale_id.project_id and self.od_om_res_sale_id.project_id.id
            so_analyti_map[od_om_res_sale_id] = o_m_analytic
        so_tab_map = {'mat':od_mat_sale_id,'trn':od_trn_sale_id,'imp':od_bim_sale_id,'amc':od_bmn_sale_id,'o_m':od_om_res_sale_id}
        return so_tab_map,so_analyti_map

    def update_tab_sale_order_link(self,new_tab_so_map):
        for tab,so_id in new_tab_so_map.iteritems():
            if tab == 'mat':
                self.od_mat_sale_id = so_id
            elif tab == 'trn':
                self.od_trn_sale_id = so_id
            elif tab == 'imp':
                self.od_bim_sale_id = so_id
            elif tab == 'amc':
                self.od_bmn_sale_id = so_id
            elif tab == 'o_m':
                self.od_om_res_sale_id = so_id
    
    
    
    def write_sale_order_line(self,sale_id,order_vals):
        # print "order vals>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",order_vals
        sale_line = self.env['sale.order.line']
        old_lines = sale_id.order_line
        current_line = self.env['sale.order.line']
        # pprint(order_vals)
        discount = self.special_discount
#         sale_id.write({'od_discount':discount})
        for _,_,line in order_vals:
            sale_order_line = sale_line.search([('order_id','=',sale_id.id),('product_id','=',line.get('product_id')),('od_inactive','=',False)])
            if sale_order_line:
                sale_order_line.write({
                    'product_uom_qty':line.get('product_uom_qty'),
                    'price_unit':line.get('price_unit'),
                    'purchase_price':line.get('purchase_price'),
                    'od_sup_unit_cost':line.get('od_sup_unit_cost'),
                    'od_sup_line_cost':line.get('od_sup_unit_cost',0) *line.get('product_uom_qty',0),
                     'tax_id':line.get('tax_id',[[6,False,[]]]),
                    
                })
                current_line |= sale_order_line
            else:
                line.update({'order_id':sale_id.id,'od_original_price':0.0,'od_original_qty':0.0,'od_original_unit_cost':0.0})
                sale_line.create(line)
        (old_lines - current_line).write({'product_uom_qty':0,'price_unit':0.0,'purchase_price':0.0,'od_inactive':True})

    
    
    
    def write_analytic_map_sale_order(self,anal_maped_dict,so_vals,so_line_map,so_line_val):
        od_discount = so_vals.get('x_discount',0)
        new_sale_ob = False
        if od_discount:
            discount = od_discount
            so_line_map = self.apply_discount_write(so_line_map,discount)
        new_analytic_so_map = {}
        second_analytic_so_map = {}
        new_tab_so_map ={}
        so_need_to_update = []
        sale_line_pool = self.env['sale.order.line']
        sale_pool = self.env['sale.order']
        analytic = self.env['account.analytic.account']
        so_tab_map,so_analyti_map = self.get_so_tab_map()
        analytic_so_map = {v: k for k, v in so_analyti_map.items()}
        for analytic_id,tabs in anal_maped_dict.iteritems():
            analytic_ob = analytic.browse(analytic_id)
            analytic_ob.write({'od_cost_sheet_id':self.id,
                               'od_cost_centre_id':self.od_cost_centre_id and self.od_cost_centre_id.id ,
                               'od_branch_id':self.od_branch_id and self.od_branch_id.id,
                               'od_division_id':self.od_division_id and self.od_division_id.id,
                              'od_project_owner_id':self.reviewed_id and self.reviewed_id.id,
                               'od_amc_owner_id':self.reviewed_id and self.reviewed_id.id,
                               'od_om_owner_id':self.reviewed_id and self.reviewed_id.id,

                                
                               })
            
            so_vals['project_id'] = analytic_id
            so_vals['name'] = '/'
            order_line = []
            for tab in tabs:
                order_line += so_line_map[tab]
            order_line = self.od_deduplicate_pdt(order_line)
            for tab in tabs:
                so_id = so_tab_map.get(tab,False)
                if so_id:
                    so_analytic_id =so_analyti_map.get(so_id,False)
                    if so_analytic_id and so_analytic_id != analytic_id:
                        sale_lines = sale_line_pool.search([('order_id','=',so_id),('od_tab_type','=',tab)])
                        if not sale_lines:
                            raise Warning("Tab Type Not Linked in Sale Order With Id = %s"%so_id)
                        new_sale_id = analytic_so_map.get(analytic_id,False)
                        if not new_sale_id:
                            new_sale_id = new_analytic_so_map.get(analytic_id,False)
                        if not new_sale_id:
                            new_sale_id = sale_pool.create(so_vals)
                            new_sale_ob = new_sale_id
#                             new_sale_id.od_action_approve()
                            new_sale_id = new_sale_id.id
                            new_analytic_so_map[analytic_id] = new_sale_id
                        sale_lines.write({'order_id':new_sale_id})
                        if new_sale_ob:
                            new_sale_ob.od_action_approve()
                        new_tab_so_map[tab] = new_sale_id
                        so_need_to_update.append(new_sale_id)
                    else:
                        so_need_to_update.append(so_id)
                        # self.write_sale_order_line(sale_id,order_line)
                else:
                    so_id = analytic_so_map.get(analytic_id,False)
                    if not so_id:

                        so_vals['order_line'] = order_line
                        so_id = self.env['sale.order'].create(so_vals)
                        so_id.od_action_approve()
                        so_id = so_id.id
                        analytic_so_map[analytic_id] = so_id
                    new_tab_so_map[tab] = so_id

            so_need_to_update = list(set(so_need_to_update))
            if so_need_to_update:
                for so in so_need_to_update:
                    sale_id = sale_pool.browse(so)
                    self.write_sale_order_line(sale_id,order_line)
                    so_need_to_update.remove(so)
            if new_tab_so_map:
                self.update_tab_sale_order_link(new_tab_so_map)

 
    def divide_order_line(self,order_line,no_of_l2):
        if not no_of_l2:
            raise Warning("Zero Level 2 AMC or O&M Accounts Defined ,kindly Check Revenue Structure Tab")
        new_order_line = [ ]
        for _,_,val in order_line:
            
            od_original_price = val.get('od_original_price',0.0)
            val['od_original_price'] = od_original_price/no_of_l2
            
            od_original_unit_cost =val.get('od_original_unit_cost',0.0)
            val['od_original_unit_cost'] = od_original_unit_cost/no_of_l2
            
            price_unit = val.get('price_unit',0.0)
            val['price_unit'] = price_unit/no_of_l2
            
            purchase_price = val.get('purchase_price',0.0)
            val['purchase_price'] = purchase_price/no_of_l2
            
            od_sup_unit_cost = val.get('od_sup_unit_cost',0.0)
            val['od_sup_unit_cost'] = od_sup_unit_cost/no_of_l2
            
            od_sup_line_cost = val.get('od_sup_line_cost',0.0)
            val['od_sup_line_cost'] = od_sup_line_cost/no_of_l2 
        return order_line   
            
    def create_multiple_level2_so(self,so_vals,order_line,group='amc'):
        if group =='amc':
            no_of_l2 = self.no_of_l2_accounts_amc
            order_line = self.divide_order_line(order_line, no_of_l2)
            so_vals['order_line'] =  order_line
            
            company_id = self.company_id and self.company_id.id
            so_vals['company_id'] =company_id
            for line in self.amc_analytic_line:
                analytic_id = line.analytic_id and line.analytic_id.id
                so_vals['name'] = '/' 
                so_vals['project_id'] = analytic_id
                so_id = self.env['sale.order'].create(so_vals)
                so_id.write({'project_id':analytic_id})
                so_id.od_action_approve()
                line['so_id'] = so_id.id
        
        if group =='om':
            no_of_l2 = self.no_of_l2_accounts_om
            order_line = self.divide_order_line(order_line, no_of_l2)
            so_vals['order_line'] =  order_line
            
            company_id = self.company_id and self.company_id.id
            so_vals['company_id'] =company_id
            for line in self.om_analytic_line:
                analytic_id = line.analytic_id and line.analytic_id.id
                so_vals['name'] = '/' 
                so_vals['project_id'] = analytic_id
                so_id = self.env['sale.order'].create(so_vals)
                so_id.write({'project_id':analytic_id})
                so_id.od_action_approve()
                line['so_id'] = so_id.id
        

    def create_analytic_map_sale_order(self,anal_maped_dict,so_vals,so_line_map):
        od_discount = so_vals.get('x_discount',0)
        if od_discount:
            discount = od_discount
            so_line_map = self.apply_discount_create(so_line_map,discount)
        analytic = self.env['account.analytic.account']
        for analytic_id,tabs in anal_maped_dict.iteritems():
            so_vals['project_id'] = analytic_id
            analytic_ob = analytic.browse(analytic_id)
            analytic_ob.write({'od_cost_sheet_id':self.id,
                               'od_cost_centre_id':self.od_cost_centre_id and self.od_cost_centre_id.id ,
                               'od_branch_id':self.od_branch_id and self.od_branch_id.id,
                               'od_division_id':self.od_division_id and self.od_division_id.id,
                               'od_project_owner_id':self.reviewed_id and self.reviewed_id.id,
                               'od_amc_owner_id':self.reviewed_id and self.reviewed_id.id,
                               'od_om_owner_id':self.reviewed_id and self.reviewed_id.id,
                               'bim_profit':self.a_bim_cost or 0.0,
                               'bmn_profit':self.a_bmn_cost or 0.0
                               })
            
            order_line = []
            for tab in tabs:
#                 if self.select_a0 and tab in ('amc','om'):
#                     continue
                    
                order_line += so_line_map[tab]
            
            order_line = self.od_deduplicate_pdt(order_line)
            
            if not order_line:
                raise Warning("No Order Line to Create Sale Order")
            
            
            # pprint(order_line)
            if not order_line:
                raise Warning("No Order Line to Create Sale Order")
            so_vals['order_line'] =  order_line
            so_vals['name'] = '/'
            company_id = self.company_id and self.company_id.id
            so_vals['company_id'] =company_id
            # sdfsfsfs
            pprint(so_vals)
            if self.select_a0 and tab == 'amc':
                self.create_multiple_level2_so(so_vals, order_line, group='amc')
                continue
            if self.select_a0 and tab == 'o_m':
                self.create_multiple_level2_so(so_vals, order_line, group='om')
                continue
            so_id = self.env['sale.order'].create(so_vals)
            so_id.od_action_approve()
            for tab in tabs:
                if tab == 'mat':
                    if not self.od_mat_sale_id:
                        self.od_mat_sale_id = so_id.id
                elif tab == 'imp':
                    if not self.od_bim_sale_id:
                        self.od_bim_sale_id = so_id.id

                elif tab == 'o_m':
                    if not self.od_om_res_sale_id:
                        self.od_om_res_sale_id = so_id.id
                elif tab == 'trn':
                    if not self.od_trn_sale_id:
                        self.od_trn_sale_id = so_id.id
                elif tab == 'amc':
                    if not self.od_bmn_sale_id:
                        self.od_bmn_sale_id = so_id.id
            
            
        return True

    def get_product_id_from_param(self,product_param):
        parameter_obj = self.env['ir.config_parameter']
        key =[('key', '=', product_param)]
        product_param_obj = parameter_obj.search(key)
        if not product_param_obj:
            raise Warning(_('Settings Warning!'),_('NoParameter Not defined\nconfig it in System Parameters with %s'%product_param))
        product_id = product_param_obj.od_model_id and product_param_obj.od_model_id.id or False
        return product_id


    def get_product_name(self,product_id):
        product = self.env['product.product']
        product_obj = product.browse(product_id)
        return product_obj.description_sale or product_obj.name
    def get_product_brand(self,product_id):
        product = self.env['product.product']
        product_obj = product.browse(product_id)
        return product_obj.od_pdt_brand_id and product_obj.od_pdt_brand_id.id or False
    
    def get_product_tax(self):
        ksa = self.is_saudi_comp()
        param ='default_product_tax'
        if ksa:
            param =param+'_saudi'
        parameter_obj = self.env['ir.config_parameter']
        key =[('key', '=', param)]
        tax_param_obj = parameter_obj.search(key)
        if not tax_param_obj:
            raise Warning(_('Settings Warning!'),_('NoParameter Not defined\nconfig it in System Parameters with %s'%key))

        
        return tax_param_obj.od_model_id and tax_param_obj.od_model_id.id or False


    def apply_discount_create(self,so_line_map,discount):
        all_sale_order_line = []
        total_selling_price = 0.0
        for key,val in so_line_map.iteritems():
            all_sale_order_line += val
        for _,_,item in all_sale_order_line:
            price = item.get('price_unit',0.0)
            qty = item.get('product_uom_qty',0.0)
            total_selling_price += price * qty
        for key,val in so_line_map.iteritems():
            for _,_,res in val:
                price_unit = res.get('price_unit',0.0)
                discount_to_apply = 0
                if total_selling_price:
                    discount_to_apply = (price_unit/total_selling_price)*discount
                new_price = price_unit + discount_to_apply
                res['price_unit'] = new_price
                res['od_original_price'] = new_price
        return so_line_map
    def apply_discount_write(self,so_line_map,discount):
        all_sale_order_line = []
        total_selling_price = 0.0
        for key,val in so_line_map.iteritems():
            all_sale_order_line += val
        for _,_,item in all_sale_order_line:
            price = item.get('price_unit',0.0)
            qty = item.get('product_uom_qty',0.0)
            total_selling_price += price * qty
        for key,val in so_line_map.iteritems():
            for _,_,res in val:
                price_unit = res.get('price_unit',0.0)
                discount_to_apply = 0
                if total_selling_price:
                    discount_to_apply = (price_unit/total_selling_price)*discount
                new_price = price_unit + discount_to_apply
                res['price_unit'] = new_price
        return so_line_map


    
    def create_analyti_a0(self):
        company_id = self.company_id and self.company_id.id or False
        name_a0= self.name_a0 
        date_start_a0 = self.date_start_a0 
        date_end_a0 = self.date_end_a0
        type_project_a0= 'parent_level0'
        analytic_level = 'level0'
        owner_id = self.reviewed_id and self.reviewed_id.id or False
        analytic_a0_id =self.analytic_a0  and self.analytic_a0.id 
        analytic_id = False
        
        account_manager = self.sales_acc_manager and self.sales_acc_manager.id
        partner_id = self.od_customer_id and self.od_customer_id.id
        
        od_cost_centre_id = self.od_cost_centre_id and self.od_cost_centre_id.id or False
        od_branch_id = self.od_branch_id and self.od_branch_id.id or False
        od_division_id = self.od_division_id and self.od_division_id.id or False
        code = self.number + '-' + 'A0'
        if not analytic_a0_id:
            analytic_a0 = self.env['account.analytic.account'].create({
                    'name':name_a0,
                    'date_start':date_start_a0,
                    'date':date_end_a0,
                    'od_date_end_original':date_end_a0,
                    'od_analytic_pmo_closing':date_end_a0,
                    'type':'view',
                    'code':code,
                    'company_id':company_id,
                    'od_owner_id':owner_id,
                    'od_type_of_project':type_project_a0,
                    'od_analytic_level':analytic_level,
                    'manager_id':account_manager,
                    'partner_id':partner_id,
                    'od_cost_sheet_id':self.id,
                    'od_cost_centre_id':od_cost_centre_id,
                    'od_branch_id':od_branch_id,
                    'od_division_id':od_division_id
                    
                    })
            analytic_id = analytic_a0.id
        else:
            analytic_id = analytic_a0_id
            analytic_ob =self.env['account.analytic.account'].browse(analytic_id)
            analytic_ob.write({
                    #'name':name_a0,
                    #'date_start':date_start_a0,
                    #'date':date_end_a0,
                    #'od_date_end_original':date_end_a0,
                    #'od_analytic_pmo_closing':date_end_a0,
                    'company_id':company_id,
                    #'od_owner_id':owner_id,
                    'od_type_of_project':type_project_a0,
                    'od_analytic_level':analytic_level,
                    'manager_id':account_manager,
                    'partner_id':partner_id,
                    'od_cost_sheet_id':self.id,
                    'od_cost_centre_id':od_cost_centre_id,
                    'od_branch_id':od_branch_id,
                    'od_division_id':od_division_id
                })
            
        return analytic_id
    
    
    def create_analytic_level1_template(self,parent_id,seq):
        
        company_id = self.company_id and self.company_id.id or False
        
        account_manager = self.sales_acc_manager and self.sales_acc_manager.id
        partner_id = self.od_customer_id and self.od_customer_id.id
        
        od_cost_centre_id = self.od_cost_centre_id and self.od_cost_centre_id.id or False
        od_branch_id = self.od_branch_id and self.od_branch_id.id or False
        od_division_id = self.od_division_id and self.od_division_id.id or False
        select_seq = eval('self.'+'select_a'+ str(seq))
        analytic_seq = eval('self.'+'analytic_a'+ str(seq))
        analytic_seq_id = analytic_seq and analytic_seq.id or False
        template_id = False
        if self.is_saudi_comp():
            template_id = 2451
        else:
            template_id = 2449
        
        if select_seq:
            analytic_id = False
            name= eval('self.'+'name_a'+ str(seq))
            date_start = eval('self.'+'date_start_a'+ str(seq))
            date_end = eval('self.'+'date_end_a'+ str(seq))
            type_project= eval('self.'+'type_of_project_a'+ str(seq))
            analytic_level = 'level1'
            owner_id = eval('self.'+'owner_id_a'+ str(seq))
            code = self.number + '-' + 'A'+ str(seq)
            analytic_tag = 'a'+str(seq)
            type = 'normal'
            use_timesheets = True
            use_tasks = True
            tabs = eval('self.'+'tabs_a'+ str(seq))
            
            if seq in (4,5):
                type ='view'
                use_timesheets = False
                use_tasks = False
            if not analytic_seq_id:
                
                
                        
                
                analytic = self.env['account.analytic.account'].create({
                    'name':name,
                    'date_start':date_start,
                    'date':date_end,
                    'od_date_end_original':date_end,
                    'od_analytic_pmo_closing':date_end,
                    'code':code,
                    'type':type,
                    'analytic_tag':analytic_tag,
                    'company_id':company_id,
                    'template_id':template_id,
                    'od_owner_id':owner_id and owner_id.id or False,
                    'od_type_of_project':type_project,
                    'od_analytic_level':analytic_level,
                    'parent_id':parent_id,
                    'manager_id':account_manager,
                    'partner_id':partner_id,
                    'od_cost_sheet_id':self.id,
                    'od_cost_centre_id':od_cost_centre_id,
                    'od_branch_id':od_branch_id,
                    'od_division_id':od_division_id,
                    'use_timesheets':use_timesheets,
                    'use_tasks':use_tasks
                    
                    })
                analytic_id = analytic.id
                mp_amend = 0.0
                mp_original = 0.0
                #Added by Aslam to reflect returned mp to each analytics
                for tab in tabs:
                    if tab.id==3:
                        mp_amend += self.a_bim_cost
                        mp_original += self.a_bim_cost
                    if tab.id==6:
                        mp_amend += self.a_bis_cost
                        mp_original += self.a_bis_cost
                    analytic.write({
                        'check_amend_mp':True,
                        'mp_amend': mp_amend,
                        'od_original_mp': mp_original
                        })
            else:
                analytic_id = analytic_seq_id
                analytic_ob =self.env['account.analytic.account'].browse(analytic_id)
                analytic = analytic_ob.write({
                    #'name':name,
                    #'date_start':date_start,
                    #'date':date_end,
                    #'od_date_end_original':date_end,
                    #'od_analytic_pmo_closing':date_end,
                    'company_id':company_id,
                    #'od_owner_id':owner_id and owner_id.id or False,
                    'od_type_of_project':type_project,
                    'od_analytic_level':analytic_level,
                    'parent_id':parent_id,
                    'manager_id':account_manager,
                    'partner_id':partner_id,
                    'od_cost_sheet_id':self.id,
                    'od_cost_centre_id':od_cost_centre_id,
                    'od_branch_id':od_branch_id,
                    'od_division_id':od_division_id,
                    'use_timesheets':use_timesheets,
                    'use_tasks':use_tasks
                    
                    })
                
            a_field = 'analytic_a' + str(seq)
            self.write({a_field:analytic_id})
    
    def create_analytic_level1(self,parent_id):
        for seq in range(1,6):
            self.create_analytic_level1_template(parent_id, seq)
            
    
    
    def create_analytic_level2(self,grand_parent_id,parent_id,group='amc'):
        mp =0.0
        
        if group== 'amc' and self.amc_analytic_line:
            return True 
        if group== 'om' and self.om_analytic_line:
            return True 
        company_id = self.company_id and self.company_id.id or False
        
        account_manager = self.sales_acc_manager and self.sales_acc_manager.id
        partner_id = self.od_customer_id and self.od_customer_id.id
        
        od_cost_centre_id = self.od_cost_centre_id and self.od_cost_centre_id.id or False
        od_branch_id = self.od_branch_id and self.od_branch_id.id or False
        od_division_id = self.od_division_id and self.od_division_id.id or False
        resol_time_ctc = self.od_resol_time_ctc or 6.00
        resol_time_maj = self.od_resol_time_maj or 8.00
        resol_time_min = self.od_resol_time_min or 24.00
        respons_time_ctc = self.od_respons_time_ctc or 0.50
        respons_time_maj = self.od_respons_time_maj or 4.00
        respons_time_min = self.od_respons_time_min or 24.00
        template_id = False
        if self.is_saudi_comp():
            template_id = 2451
        else:
            template_id = 2449
        
        periodicity = self.periodicity_amc 
        start_date = self.l2_start_date_amc
        no_of_l2 = self.no_of_l2_accounts_amc
        if group =='amc':
            mp = self.a_bmn_cost/no_of_l2 
        name = parent_id.name + '-AMC'
        code =parent_id.code + '-AMC'
        owner_id = parent_id.od_owner_id and parent_id.od_owner_id.id or False
        type_project ='amc'
        type ='normal'
        analytic_level ='level2'
        date_end = False
        if group == 'om':
            periodicity = self.periodicity_om 
            start_date = self.l2_start_date_om
            no_of_l2 = self.no_of_l2_accounts_om 
            name = parent_id.name + '-O&M'
            code = parent_id.code + '-O&M'
            type_project ='o_m'
       
        
        
        start_date =datetime.strptime(start_date,'%Y-%m-%d') 
                
        vals =[]
        
        for i in range(no_of_l2):
            
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
            use_timesheets = True
            use_tasks = True

#             analytic=self.env['account.analytic.account'].create({
#                     'name':name +'-' +str(i+1),
#                     'date_start':str(start_date),
#                     'date':str(date_end),
#                     'od_date_end_original':str(date_end),
#                     'od_analytic_pmo_closing':str(date_end),
#                     'code':code+'-' +str(i+1),
#                     'type':type,
#                     'company_id':company_id,
#                     'template_id':template_id,
#                     'od_owner_id':owner_id ,
#                     'od_type_of_project':type_project,
#                     'od_analytic_level':analytic_level,
#                     'parent_id':parent_id and parent_id.id or False,
#                     'grand_parent_id':grand_parent_id,
#                     'manager_id':account_manager,
#                     'partner_id':partner_id,
#                     'od_cost_sheet_id':self.id,
#                     'od_cost_centre_id':od_cost_centre_id,
#                     'od_branch_id':od_branch_id,
#                     'od_division_id':od_division_id,
#                     'use_timesheets':use_timesheets,
#                     'use_tasks':use_tasks,
#                     'od_proj_no_of_prvntv_visit':resol_time_ctc,
#                     'od_proj_first_response_time':resol_time_maj,
#                     'od_proj_resolution_time':resol_time_min
#                     })

            if group == 'amc':
                analytic=self.env['account.analytic.account'].create({
                        'name':name +'-' +str(i+1),
                        'date_start':str(start_date),
                        'date':str(date_end),
                        'od_date_end_original':str(date_end),
                        'od_analytic_pmo_closing':str(date_end),
                        'code':code+'-' +str(i+1),
                        'analytic_tag':'child_amc'+str(i+1),
                        'type':type,
                        'company_id':company_id,
                        'template_id':template_id,
                        'od_owner_id':owner_id ,
                        'od_type_of_project':type_project,
                        'od_analytic_level':analytic_level,
                        'parent_id':parent_id and parent_id.id or False,
                        'grand_parent_id':grand_parent_id,
                        'manager_id':account_manager,
                        'partner_id':partner_id,
                        'od_cost_sheet_id':self.id,
                        'od_cost_centre_id':od_cost_centre_id,
                        'od_branch_id':od_branch_id,
                        'od_division_id':od_division_id,
                        'use_timesheets':use_timesheets,
                        'use_tasks':use_tasks,
                         'od_proj_resol_time_ctc':resol_time_ctc,
                        'od_proj_resol_time_maj':resol_time_maj,
                        'od_proj_resol_time_min':resol_time_min, 
                        'od_proj_respons_time_ctc':respons_time_ctc,
                        'od_proj_respons_time_maj':respons_time_maj,
                        'od_proj_respons_time_min':respons_time_min,    
                         
                        })
            else:
                analytic=self.env['account.analytic.account'].create({
                        'name':name +'-' +str(i+1),
                        'date_start':str(start_date),
                        'date':str(date_end),
                        'od_date_end_original':str(date_end),
                        'od_analytic_pmo_closing':str(date_end),
                        'code':code+'-' +str(i+1),
                        'analytic_tag':'child_om'+str(i+1),
                        'type':type,
                        'company_id':company_id,
                        'template_id':template_id,
                        'od_owner_id':owner_id ,
                        'od_type_of_project':type_project,
                        'od_analytic_level':analytic_level,
                        'parent_id':parent_id and parent_id.id or False,
                        'grand_parent_id':grand_parent_id,
                        'manager_id':account_manager,
                        'partner_id':partner_id,
                        'od_cost_sheet_id':self.id,
                        'od_cost_centre_id':od_cost_centre_id,
                        'od_branch_id':od_branch_id,
                        'od_division_id':od_division_id,
                        'use_timesheets':use_timesheets,
                        'use_tasks':use_tasks,
                        'od_proj_resol_time_ctc':respons_time_ctc,
                        'od_proj_resol_time_maj':respons_time_maj,
                        'od_proj_resol_time_min':respons_time_min                         
                        })
                

            analytic_id = analytic.id
            if group =='amc' and mp:
                analytic.write({
                     'check_amend_mp':True,
                            'mp_amend':mp,
                            'od_original_mp':mp,
                        
                    })
            vals.append({'start_date':start_date,'end_date':date_end,'analytic_id':analytic_id})
            start_date = date_end 
            
        if group =='amc':
            self.amc_analytic_line = vals
        if group == 'om':
            self.om_analytic_line = vals
    
    def check_duplicate_tabs(self,rev_tabs):
        result =[item for item, count in Counter(rev_tabs).items() if count > 1]
        if result:
            raise Warning("Duplicate Tabs Found linked in Multiple Analytic in Revenue Structure ")
    
    def match_tabs(self,rev_tabs):
        tabs_inclued = []
        model_data = self.env['ir.model.data']
        tab_mat =model_data.get_object_reference('orchid_cost_sheet', 'tab_mat')[1]
        tab_trn =model_data.get_object_reference('orchid_cost_sheet', 'tab_trn')[1]
        tab_imp =model_data.get_object_reference('orchid_cost_sheet', 'tab_imp')[1]
        tab_amc =model_data.get_object_reference('orchid_cost_sheet', 'tab_amc')[1]
        tab_o_m =model_data.get_object_reference('orchid_cost_sheet', 'tab_o_m')[1]
        tab_i_s =model_data.get_object_reference('orchid_cost_sheet', 'tab_i_s')[1]
        
        if self.included_in_quotation:
            tabs_inclued.append(tab_mat)
        if self.included_trn_in_quotation:
            tabs_inclued.append(tab_trn)
        if self.included_bim_in_quotation:
            tabs_inclued.append(tab_imp)
        if self.included_bmn_in_quotation:
            tabs_inclued.append(tab_amc)
        if self.included_om_in_quotation:
            tabs_inclued.append(tab_o_m)
        if self.included_info_sec_in_quotation:
            tabs_inclued.append(tab_i_s)
        if not (sorted(tabs_inclued) == sorted(rev_tabs)):
            raise Warning("Tabs Included in the Costsheet and Revenue Structure Linked Tabs are Not Matching ,Kindly Check it")
        
    def tab_validations(self):
        rev_tabs =[]
        for seq in range(1,6):
            select_seq = eval('self.'+'select_a'+ str(seq))
            if select_seq:
                tabs_ids = eval('self.'+'tabs_a'+ str(seq))
                tabs = [tab.id for tab in tabs_ids]
                rev_tabs += tabs
        self.check_duplicate_tabs(rev_tabs)
        self.match_tabs(rev_tabs)    
    
    @api.one
    def create_analytic(self):
        if self.select_a0:
            self.tab_validations()
            analytic_a0_id =self.create_analyti_a0()
            self.write({'analytic_a0':analytic_a0_id})
            self.create_analytic_level1(analytic_a0_id)
        if self.select_a4 and self.analytic_a4:
            self.create_analytic_level2(analytic_a0_id,self.analytic_a4, 'amc')
        
        if self.select_a5 and self.analytic_a5:
            self.create_analytic_level2(analytic_a0_id,self.analytic_a5, 'om')
    
    
    def get_analytic_dict(self):
        res = {}
        model_data = self.env['ir.model.data']
        tab_mat =model_data.get_object_reference('orchid_cost_sheet', 'tab_mat')[1]
        tab_trn =model_data.get_object_reference('orchid_cost_sheet', 'tab_trn')[1]
        tab_imp =model_data.get_object_reference('orchid_cost_sheet', 'tab_imp')[1]
        tab_amc =model_data.get_object_reference('orchid_cost_sheet', 'tab_amc')[1]
        tab_o_m =model_data.get_object_reference('orchid_cost_sheet', 'tab_o_m')[1]
        tab_i_s =model_data.get_object_reference('orchid_cost_sheet', 'tab_i_s')[1]
        
        
        for seq in range(1,6):
            select_seq = eval('self.'+'select_a'+ str(seq))
            analytic =eval('self.'+'analytic_a'+ str(seq))
            analytic_id = analytic and analytic.id or False
            if select_seq:
                tabs_ids = eval('self.'+'tabs_a'+ str(seq))
                for tab in tabs_ids:
                    if tab.id == tab_mat:
                        res['mat'] = analytic_id 
                    if tab.id == tab_trn:
                        res['trn'] = analytic_id
                    if tab.id == tab_imp:
                        res['imp'] = analytic_id  
                    if tab.id == tab_amc:
                        res['amc'] = analytic_id
                    if tab.id == tab_o_m:
                        res['o_m'] = analytic_id
                    if tab.id == tab_i_s:
                        res['i_s'] = analytic_id
                        
        return res    
        
    
    def copy_revenue_summary(self):
        res = []
        for line in self.summary_weight_line:
            res.append(({
                'cost_sheet_id':self.id,
                'pdt_grp_id':line.pdt_grp_id and line.pdt_grp_id.id or False,
                'total_sale':line.total_sale,
                'disc':line.disc,
                'sale_aftr_disc':line.sale_aftr_disc,
                'total_cost':line.total_cost,
                'profit':line.profit,
                'manpower_cost':line.manpower_cost,
                'manpower_sale':line.manpower_sale,
                'total_gp':line.total_gp,
                'profit_percent':line.profit_percent,
                }))
        self.original_summary_weight_line =res
    
    
        
    
    def generate_sale_order_v3(self):
        customer_id = self.od_customer_id.id
        order_type_id = self.od_order_type_id and self.od_order_type_id.id or False
        default_svat = self.get_product_tax()
        tsvat = [[6,False,[default_svat]]]
        branch_id = self.lead_id and self.lead_id.od_branch_id and self.lead_id.od_branch_id.id or False 
        if branch_id == 2:
            tsvat = [[6,False,[33]]]
        bdm_user_id = self.lead_id and self.lead_id.od_bdm_user_id and self.lead_id.od_bdm_user_id.id or False
        presale_user_id = self.lead_id and self.lead_id.od_responsible_id and self.lead_id.od_responsible_id.id or False


        project_mat = self.project_mat and self.project_mat.id
        project_ren = self.project_ren and self.project_ren.id
        project_bim = self.project_bim and self.project_bim.id
        project_oim = self.project_oim and self.project_oim.id
        project_omn = self.project_omn and self.project_omn.id
        project_o_m = self.project_o_m and self.project_o_m.id
        project_trn = self.project_trn and self.project_trn.id
        project_bmn = self.project_bmn and self.project_bmn.id

        material_lines = []
        b_lines = []
        o_lines = []
        om_lines = []
        om_r_lines = []
        trn_lines = []
        bm_lines = []

#         anal_dict = {'mat':project_mat,'imp':project_bim,'oim':project_oim,'omn':project_omn,'o_m':project_o_m,'trn':project_trn,'amc':project_bmn}
        
        anal_dict = {'mat':project_mat,'imp':project_bim,'oim':project_oim,'omn':project_omn,'o_m':project_o_m,'trn':project_trn,'amc':project_bmn}
        
        if self.select_a0:
            anal_dict = self.get_analytic_dict()
        
            
        #mat sales
        if self.included_in_quotation:
            if not (project_mat or self.select_a0):
                raise Warning("Analytic Account Not Selected In MAT Tab, Which is Enabled Included In Quotation,Please Select It")
            material_lines =[]
            mat_expense = 0.0
            mat_ext_sale = 0.0
            for line in self.mat_main_pro_line:
                material_lines.append((0,0,{
                                            'od_manufacture_id':line.manufacture_id and line.manufacture_id.id or False,
                                             'product_id':line.part_no.id,
                                             'name':line.name or line.part_no.description_sale or line.part_no.name,
                                             'od_original_qty':line.qty,
                                             'od_original_price':line.new_unit_price if line.locked else line.unit_price,
                                             'od_original_unit_cost':line.unit_cost_local,
                                             'product_uom_qty':line.qty,
                                             'price_unit':line.new_unit_price if line.locked else line.unit_price,
                                             'purchase_price':line.unit_cost_local,
                                             'od_analytic_acc_id':anal_dict.get('mat'),
                                             'od_cost_sheet_id':self.id,
                                             'od_tab_type':'mat',
                                             'od_sup_unit_cost':line.discounted_unit_supplier_currency,
                                             'od_sup_line_cost':line.discounted_total_supplier_currency,
                                             'tax_id':[[6,False,[line.tax_id.id]]] 
                                             }))
                
                    

            for line in self.mat_extra_expense_line:
                mat_expense += line.qty * line.unit_cost_local
                mat_ext_sale += line.qty * (line.new_unit_price if line.locked else line.unit_price2)
            mat_exp_product_id = self.get_product_id_from_param('product_mat_extra_expense')
            material_lines.append((0,0,{
                                    'name':self.get_product_name(mat_exp_product_id),
                                    'od_manufacture_id':self.get_product_brand(mat_exp_product_id),
                                    'product_id':mat_exp_product_id,
                                    'product_uom_qty':1,
                                    'price_unit':mat_ext_sale,
                                     'od_original_qty':1,
                                     'od_original_unit_cost':mat_expense,
                                     'purchase_price':mat_expense,
                                     'od_original_price':mat_ext_sale,
                                      'od_cost_sheet_id':self.id,
                                      'od_tab_type':'mat',
                                     'od_analytic_acc_id':anal_dict.get('mat'),
                                     'tax_id':tsvat,
#                                      'tax_id':[[6,False,[line.tax_id.id]]],
                                     'od_sup_unit_cost':0,
                                            
                                    }))
            if not material_lines:
                raise Warning('NO lines to Create Quotation for MAT Tab')
        if self.pre_opn_cost:
            pre_opn_cost =self.pre_opn_cost
            pre_opn_cost_product_id = self.get_product_id_from_param('product_pre_opn_expense')
            material_lines.append((0,0,{
                                    'name':self.get_product_name(pre_opn_cost_product_id),
                                    'od_manufacture_id':self.get_product_brand(pre_opn_cost_product_id),
                                    'product_id':pre_opn_cost_product_id,
                                    'product_uom_qty':1,
                                    'price_unit':0.0,
                                     'od_original_qty':1,
                                     'od_original_unit_cost':pre_opn_cost,
                                     'purchase_price':pre_opn_cost,
                                     'od_original_price':0.0,
                                      'od_cost_sheet_id':self.id,
                                      'od_tab_type':'mat',
                                     'od_analytic_acc_id':anal_dict.get('mat'),
#                                      'tax_id':[[6,False,[line.tax_id.id]]],
                                     'od_sup_unit_cost':0,
                                            
                                    }))
            
        # Training Sale Order
        if self.included_trn_in_quotation:

            trn_lines =[]
            trn_expense = 0.0
            trn_extra_sale = 0.0
            for line in self.trn_customer_training_line:
                if not (project_trn or self.select_a0):
                    raise Warning("Analytic Account Not Selected In TRN Tab, Which is Enabled Included In Quotation,Please Select It")
                trn_lines.append((0,0,{
                                            'od_manufacture_id':line.manufacture_id and line.manufacture_id.id or False,
                                            'product_id':line.part_no.id,
                                            'name':line.name or line.part_no.description_sale or line.part_no.name,
                                            'od_original_qty':line.qty,
                                            'od_original_price':line.new_unit_price if line.locked else line.unit_price,
                                            'od_original_unit_cost':line.unit_cost_local,
                                            'purchase_price':line.unit_cost_local,
                                            'product_uom_qty':line.qty,
                                            'price_unit':line.new_unit_price if line.locked else line.unit_price,
                                            'od_cost_sheet_id':self.id,
                                            'od_tab_type':'trn',
                                            'od_analytic_acc_id':anal_dict.get('trn'),
                                            'tax_id':[[6,False,[line.tax_id.id]]],
                                            'od_sup_unit_cost':line.discounted_unit_supplier_currency,
                                            'od_sup_line_cost':line.discounted_total_supplier_currency,
                                             }))
            for line in self.trn_customer_training_extra_expense_line:
                trn_expense += line.qty * line.unit_cost_local
                trn_extra_sale += line.qty * (line.new_unit_price if line.locked else line.unit_price2)
            trn_exp_product_id = self.get_product_id_from_param('product_trn_extra_expense')
            trn_lines.append((0,0,{
                                    'name':self.get_product_name(trn_exp_product_id),
                                    'od_manufacture_id':self.get_product_brand(trn_exp_product_id),
                                    'product_id':trn_exp_product_id,
                                    'product_uom_qty':1,
                                    'od_original_qty':1,
                                    'od_original_price':trn_extra_sale,
                                    'od_original_unit_cost':trn_expense,
                                    'purchase_price':trn_expense,
                                    'price_unit':trn_extra_sale,
                                    'od_cost_sheet_id':self.id,
                                    'od_tab_type':'trn',
                                    'tax_id':tsvat,
#                                      'tax_id':[[6,False,[line.tax_id.id]]],
                                    'od_analytic_acc_id':anal_dict.get('trn'),
                                    'od_sup_unit_cost':0,
                                    
                                }))

            if not trn_lines:
                raise Warning('NO lines to Create Quotation TRN Tab')

#         Bim sale order generation #Now PS tab

        bi_ext_exp = 0.0
        bi_ext_exp_cost = 0.0
        bim_price = bim_cost= 0
        b_lines = []
        oim_price = 0.0
        oim_cost  = 0.0
        oim_exp= 0.0
        oim_exp_cost = 0.0
        if self.bim_log_select:
            bim_price = self.bim_log_price
            bim_cost = self.bim_log_cost
        if self.included_bim_in_quotation:
            if not (project_bim or self.select_a0):
                raise Warning("Analytic Account Not Selected In IMP Tab, Which is Enabled Included In Quotation,Please Select It")

            
            for line in self.imp_tech_line:
                b_lines.append((0,0,{
                                            'od_manufacture_id':line.manufacture_id and line.manufacture_id.id or False,
                                             'product_id':line.part_no.id,
                                             'name':line.name or line.part_no.description_sale or line.part_no.name,
                                             'od_original_qty':line.qty,
                                             'od_original_price':line.new_unit_price if line.locked else line.unit_price,
                                             'od_original_unit_cost':line.unit_cost_local,
                                             'product_uom_qty':line.qty,
                                             'price_unit':line.new_unit_price if line.locked else line.unit_price,
                                             'purchase_price':line.unit_cost_local,
                                             'od_analytic_acc_id':anal_dict.get('imp'),
                                             'od_cost_sheet_id':self.id,
                                             'od_tab_type':'imp',
                                             'od_sup_unit_cost':line.discounted_unit_supplier_currency,
                                             'od_sup_line_cost':line.discounted_total_supplier_currency,
                                             'tax_id':[[6,False,[line.tax_id.id]]] 
                                             }))
            
            
            
            for oim_line in self.oim_extra_expenses_line:
                oim_exp += oim_line.qty * (oim_line.new_unit_price if oim_line.locked else oim_line.unit_price)
                oim_exp_cost += oim_line.qty * oim_line.unit_cost
            oim_exp_product_id = self.get_product_id_from_param('product_oim_extra_expense')
            b_lines.append((0,0,{'name':self.get_product_name(oim_exp_product_id),
                                'product_id':oim_exp_product_id,
                                'od_manufacture_id':self.get_product_brand(oim_exp_product_id),
                                'product_uom_qty':1,
                                'od_original_qty':1,
                                'od_original_price':oim_exp,
                                'od_original_unit_cost':oim_exp_cost,
                                'purchase_price':oim_exp_cost,
                                'price_unit':oim_exp,
                                'od_cost_sheet_id':self.id,
                                'od_tab_type':'imp',
                                'od_analytic_acc_id':anal_dict.get('imp'),
                                'tax_id':tsvat,
                                
#                                 'tax_id':[[6,False,[line.tax_id.id]]],
                                'od_sup_unit_cost':0,
                                }))
            for oim_line in self.oim_implimentation_price_line:
                oim_price += oim_line.qty * (oim_line.new_unit_price if oim_line.locked else oim_line.unit_price)
                oim_cost += oim_line.qty * oim_line.unit_cost
            oim_product_id = self.get_product_id_from_param('product_oim')
            b_lines.append((0,0,{'name':self.get_product_name(oim_product_id),
                                'od_manufacture_id':self.get_product_brand(oim_product_id),
                                'product_id':oim_product_id,
                                'product_uom_qty':1,
                                'od_original_qty':1,
                                'od_original_price':oim_price,
                                'od_original_unit_cost':oim_cost,
                                'purchase_price':oim_cost,
                                'price_unit':oim_price,
                                'od_cost_sheet_id':self.id,
                                'tax_id':tsvat,
#                                 'tax_id':[[6,False,[line.tax_id.id]]],
                                'od_tab_type':'imp',
                                'od_analytic_acc_id':anal_dict.get('imp'),
                                'od_sup_unit_cost':0,
                                }))


            for bim_line in self.implimentation_extra_expense_line:
                bi_ext_exp += bim_line.qty * ( bim_line.new_unit_price if bim_line.locked else bim_line.unit_price)
                bi_ext_exp_cost +=  bim_line.qty * bim_line.unit_cost
            bim_exp_product_id = self.get_product_id_from_param('product_bim_extra_expense')
            b_lines.append((0,0,{
                            'name':self.get_product_name(bim_exp_product_id),
                            'od_manufacture_id':self.get_product_brand(bim_exp_product_id),
                            'product_id':bim_exp_product_id,
                            'product_uom_qty':1,
                            'od_original_qty':1,
                            'od_original_price':bi_ext_exp,
                            'od_original_unit_cost':bi_ext_exp_cost,
                            'purchase_price':bi_ext_exp_cost,
                            'price_unit':bi_ext_exp,
                            'od_cost_sheet_id':self.id,
                            'od_tab_type':'imp',
                            'tax_id':tsvat,
#                             'tax_id':[[6,False,[line.tax_id.id]]],
                            'od_analytic_acc_id':anal_dict.get('imp'),
                            'od_sup_unit_cost':0,
                                }))
            for bim_line in self.manpower_manual_line:
                bim_price +=  bim_line.qty * ( bim_line.new_unit_price if bim_line.locked else  bim_line.unit_price)
                bim_cost += bim_line.qty * bim_line.unit_cost
            if self.bim_imp_select:
                for bim_line in self.bim_implementation_code_line:
                    bim_price +=  bim_line.qty *( bim_line.new_unit_price if bim_line.locked else  bim_line.unit_price)
                    bim_cost += bim_line.qty * bim_line.unit_cost
            bim_product_id = self.get_product_id_from_param('product_bim')
            b_lines.append((0,0,{'name':self.get_product_name(bim_product_id),
                                 'product_id':bim_product_id,
                                 'od_manufacture_id':self.get_product_brand(bim_product_id),
                                'product_uom_qty':1,
                                'od_original_qty':1,
                                'od_original_price':bim_price,
                                'od_original_unit_cost':bim_cost,
                                'purchase_price':bim_cost,
                                'price_unit':bim_price,
                                'od_cost_sheet_id':self.id,
                                'od_tab_type':'imp',
                                 'tax_id':tsvat,
#                             'tax_id':[[6,False,[line.tax_id.id]]],
                                'od_analytic_acc_id':anal_dict.get('imp'),
                                'od_sup_unit_cost':0,
            }))
            
            for line in self.ps_vendor_line:
                b_lines.append((0,0,{
                                    'od_manufacture_id':line.manufacture_id and line.manufacture_id.id or False,
                                     'product_id':line.part_no.id,
                                     'name':line.name or line.part_no.description_sale or line.part_no.name,
                                     'od_original_qty':line.qty,
                                     'od_original_price':line.new_unit_price if line.locked else line.unit_price,
                                     'od_original_unit_cost':line.unit_cost_local,
                                     'product_uom_qty':line.qty,
                                     'price_unit':line.new_unit_price if line.locked else line.unit_price,
                                     'purchase_price':line.unit_cost_local,
                                     'od_analytic_acc_id': anal_dict.get('imp'),
                                     'od_cost_sheet_id':self.id,
                                     'od_tab_type':'imp',
                                     'od_sup_unit_cost':line.discounted_unit_supplier_currency,
                                     'od_sup_line_cost':line.discounted_total_supplier_currency,
                                     'tax_id':[[6,False,[line.tax_id.id]]] 
                                     }))
            
            if not b_lines:
                raise Warning('NO lines to Create Quotation IMP Tab')
            
        #         Info Sec sale order generation

        bis_ext_exp = 0.0
        bis_ext_exp_cost = 0.0
        info_sec_lines = []
        ois_exp= 0.0
        ois_exp_cost = 0.0
        
        if self.included_info_sec_in_quotation:
            if not (project_bim or self.select_a0):
                raise Warning("Analytic Account Not Selected In IMP Tab, Which is Enabled Included In Quotation,Please Select It")
            
            for line in self.info_sec_tech_line:
                info_sec_lines.append((0,0,{
                                            'od_manufacture_id':line.manufacture_id and line.manufacture_id.id or False,
                                             'product_id':line.part_no.id,
                                             'name':line.name or line.part_no.description_sale or line.part_no.name,
                                             'od_original_qty':line.qty,
                                             'od_original_price':line.new_unit_price if line.locked else line.unit_price,
                                             'od_original_unit_cost':line.unit_cost_local,
                                             'product_uom_qty':line.qty,
                                             'price_unit':line.new_unit_price if line.locked else line.unit_price,
                                             'purchase_price':line.unit_cost_local,
                                             'od_analytic_acc_id':anal_dict.get('i_s'),
                                             'od_cost_sheet_id':self.id,
                                             'od_tab_type':'i_s',
                                             'od_sup_unit_cost':line.discounted_unit_supplier_currency,
                                             'od_sup_line_cost':line.discounted_total_supplier_currency,
                                             'tax_id':[[6,False,[line.tax_id.id]]] 
                                             }))
            
            
            
            for ois_line in self.info_sec_subcontractor_line:
                ois_exp += ois_line.qty * (ois_line.new_unit_price if ois_line.locked else ois_line.unit_price)
                ois_exp_cost += ois_line.qty * ois_line.unit_cost
            ois_exp_product_id = self.get_product_id_from_param('product_ois_extra_expense')
            info_sec_lines.append((0,0,{'name':self.get_product_name(ois_exp_product_id),
                            'product_id':ois_exp_product_id,
                            'od_manufacture_id':self.get_product_brand(ois_exp_product_id),
                            'product_uom_qty':1,
                            'od_original_qty':1,
                            'od_original_price':ois_exp,
                            'od_original_unit_cost':ois_exp_cost,
                            'purchase_price':ois_exp_cost,
                            'price_unit':ois_exp,
                            'od_cost_sheet_id':self.id,
                            'od_tab_type':'i_s',
                            'od_analytic_acc_id':anal_dict.get('i_s'),
                            'tax_id':tsvat,

#                                 'tax_id':[[6,False,[line.tax_id.id]]],
                            'od_sup_unit_cost':0,
                            }))


            for bis_line in self.info_sec_extra_expense_line:
                bis_ext_exp += bis_line.qty * ( bis_line.new_unit_price if bis_line.locked else bis_line.unit_price)
                bis_ext_exp_cost +=  bis_line.qty * bis_line.unit_cost
            bis_exp_product_id = self.get_product_id_from_param('product_bis_extra_expense')
            info_sec_lines.append((0,0,{
                        'name':self.get_product_name(bis_exp_product_id),
                        'od_manufacture_id':self.get_product_brand(bis_exp_product_id),
                        'product_id':bis_exp_product_id,
                        'product_uom_qty':1,
                        'od_original_qty':1,
                        'od_original_price':bis_ext_exp,
                        'od_original_unit_cost':bis_ext_exp_cost,
                        'purchase_price':bis_ext_exp_cost,
                        'price_unit':bis_ext_exp,
                        'od_cost_sheet_id':self.id,
                        'od_tab_type':'i_s',
                        'tax_id':tsvat,
#                            'tax_id':[[6,False,[line.tax_id.id]]],
                        'od_analytic_acc_id':anal_dict.get('i_s'),
                        'od_sup_unit_cost':0,
                            }))

            
            for line in self.info_sec_vendor_line:
                info_sec_lines.append((0,0,{
                                    'od_manufacture_id':line.manufacture_id and line.manufacture_id.id or False,
                                     'product_id':line.part_no.id,
                                     'name':line.name or line.part_no.description_sale or line.part_no.name,
                                     'od_original_qty':line.qty,
                                     'od_original_price':line.new_unit_price if line.locked else line.unit_price,
                                     'od_original_unit_cost':line.unit_cost_local,
                                     'product_uom_qty':line.qty,
                                     'price_unit':line.new_unit_price if line.locked else line.unit_price,
                                     'purchase_price':line.unit_cost_local,
                                     'od_analytic_acc_id': anal_dict.get('i_s'),
                                     'od_cost_sheet_id':self.id,
                                     'od_tab_type':'i_s',
                                     'od_sup_unit_cost':line.discounted_unit_supplier_currency,
                                     'od_sup_line_cost':line.discounted_total_supplier_currency,
                                     'tax_id':[[6,False,[line.tax_id.id]]] 
                                     }))
            
            if not info_sec_lines:
                raise Warning('NO lines to Create Quotation IS Tab')
        
#             Bmn Sale order Generation #Now Amc
        bm_lines = []
        
        if self.included_bmn_in_quotation:
            if not (project_bmn or self.select_a0):
                    raise Warning("Analytic Account Not Selected In AMC Tab, Which is Enabled Included In Quotation,Please Select It")
            amc_parent_analtyic = self.analytic_a4 and self.analytic_a4.id
            amc_child_ids = self.env['account.analytic.account'].search([('parent_id','=',amc_parent_analtyic)])
            amc_count = float(len(amc_child_ids))
            for amc in amc_child_ids:
                bmn_price = 0.0
                bmn_cost = 0.0
                bmn_exp = 0.0
                bmn_exp_cost = 0.0
                omn_price = 0.0
                omn_cost = 0.0
                omn_exp = 0.0
                omn_exp_cost = 0.0
                
                for line in self.amc_tech_line:
                    bm_lines.append((0,0,{
                                                'od_manufacture_id':line.manufacture_id and line.manufacture_id.id or False,
                                                 'product_id':line.part_no.id,
                                                 'name':line.name or line.part_no.description_sale or line.part_no.name,
                                                 'od_original_qty':line.qty/amc_count,
                                                 'od_original_price':line.new_unit_price if line.locked else line.unit_price,
                                                 'od_original_unit_cost':line.unit_cost_local,
                                                 'product_uom_qty':line.qty/amc_count,
                                                 'price_unit':line.new_unit_price if line.locked else line.unit_price,
                                                 'purchase_price':line.unit_cost_local,
                                                 'od_analytic_acc_id':amc.id,
                                                 'od_cost_sheet_id':self.id,
                                                 'od_tab_type':'amc',
                                                 'od_sup_unit_cost':line.discounted_unit_supplier_currency,
                                                 'od_sup_line_cost':line.discounted_total_supplier_currency,
                                                 'tax_id':[[6,False,[line.tax_id.id]]] 
                                                 }))
                
                
                
                
                
               
                for omn_line in self.omn_out_preventive_maintenance_line:
                    omn_price += omn_line.qty * (omn_line.new_unit_price if omn_line.locked else omn_line.unit_price)
                    omn_cost += omn_line.qty * omn_line.unit_cost
                for omn_line in self.omn_out_remedial_maintenance_line:
                    omn_price += omn_line.qty * (omn_line.new_unit_price if omn_line.locked else omn_line.unit_price)
                    omn_cost += omn_line.qty * omn_line.unit_cost
                
                
                
                
                
                
                omn_product_id = self.get_product_id_from_param('product_omn')
                bm_lines.append((0,0,{'name':self.get_product_name(omn_product_id),
                                     'product_id':omn_product_id,
                                     'od_manufacture_id':self.get_product_brand(omn_product_id),
                                    'product_uom_qty':1.0/amc_count,
                                    'od_original_qty':1.0/amc_count,
                                    'od_original_price':omn_price,
                                    'od_original_unit_cost':omn_cost,
                                    'purchase_price':omn_cost,
                                    'price_unit':omn_price,
                                    'od_cost_sheet_id':self.id,
                                    'od_tab_type':'amc',
                                    'tax_id':tsvat,
                                    'od_analytic_acc_id':amc.id,
                                    'od_sup_unit_cost':0,
                                    }))
                for line in self.omn_spare_parts_line:
                    bm_lines.append((0,0,{
                                                'od_manufacture_id':line.manufacture_id and line.manufacture_id.id or False,
                                                 'product_id':line.part_no.id,
                                                 'name':line.name or line.part_no.description_sale or line.part_no.name,
                                                 'product_uom_qty':line.qty/amc_count,
                                                 'od_original_qty':line.qty/amc_count,
                                                 'od_original_price':line.new_unit_price if line.locked else line.unit_price,
                                                 'od_original_unit_cost':line.unit_cost_local,
                                                 'purchase_price':line.unit_cost_local,
                                                 'price_unit':line.new_unit_price if line.locked else line.unit_price,
                                                  'od_cost_sheet_id':self.id,
                                                 'od_tab_type':'amc',
                                                 'tax_id':[[6,False,[line.tax_id.id]]],
                                                 'od_analytic_acc_id':amc.id,
                                                 'od_sup_unit_cost':0,
    
                                                 }))
                for line in self.omn_maintenance_extra_expense_line:
                    omn_exp += line.qty * (line.new_unit_price if line.locked else line.unit_price)
                    omn_exp_cost += line.qty * line.unit_cost
                omn_exp_product_id = self.get_product_id_from_param('product_omn_extra_expense')
                bm_lines.append((0,0,{'name':self.get_product_name(omn_exp_product_id),
                                    'product_id':omn_exp_product_id,
                                    'od_manufacture_id':self.get_product_brand(omn_exp_product_id),
                                    'product_uom_qty':1.0/amc_count,
                                    'od_original_qty':1.0/amc_count,
                                    'od_original_price':omn_exp,
                                    'od_original_unit_cost':omn_exp_cost,
                                    'purchase_price':omn_exp_cost,
                                    'price_unit':omn_exp,
                                    'od_cost_sheet_id':self.id,
                                    'od_tab_type':'amc',
                                     'tax_id':tsvat,
    #                                 'tax_id':[[6,False,[line.tax_id.id]]],
                                    'od_analytic_acc_id':amc.id,
                                    'od_sup_unit_cost':0,
                                    }))
    
                for bmn_line in self.bmn_it_preventive_line:
                    bmn_price += bmn_line.qty * (bmn_line.new_unit_price if bmn_line.locked else bmn_line.unit_price)
                    bmn_cost += bmn_line.qty * bmn_line.unit_cost
                for bmn_line in self.bmn_it_remedial_line:
                    bmn_price += bmn_line.qty * (bmn_line.new_unit_price if bmn_line.locked else bmn_line.unit_price)
                    bmn_cost += bmn_line.qty * bmn_line.unit_cost
                bmn_product_id = self.get_product_id_from_param('product_bmn')
                bm_lines.append((0,0,{'name':self.get_product_name(bmn_product_id),
                                    'product_id':bmn_product_id,
                                    'od_manufacture_id':self.get_product_brand(bmn_product_id),
                                    'product_uom_qty':1.0/amc_count,
                                    'od_original_qty':1.0/amc_count,
                                    'od_original_price':bmn_price,
                                    'od_original_unit_cost':bmn_cost,
                                    'purchase_price':bmn_cost,
                                    'price_unit':bmn_price,
                                    'od_cost_sheet_id':self.id,
                                    'od_tab_type':'amc',
                                     'tax_id':tsvat,
    #                                 'tax_id':[[6,False,[line.tax_id.id]]],
                                    'od_analytic_acc_id':amc.id,
                                    'od_sup_unit_cost':0,
                                    }))
                for line in self.bmn_spareparts_beta_it_maintenance_line:
                    bm_lines.append((0,0,{
                                                'od_manufacture_id':line.manufacture_id and line.manufacture_id.id or False,
                                                 'product_id':line.part_no.id,
                                                  'name':line.name or line.part_no.description_sale or line.part_no.name,
                                                  'od_original_qty':line.qty/amc_count,
                                                  'od_original_price':(line.new_unit_price if line.locked else line.unit_price),
                                                  'od_original_unit_cost':line.unit_cost_local,
                                                  'purchase_price':line.unit_cost_local,
                                                  'product_uom_qty':line.qty/amc_count,
                                                  'price_unit':(line.new_unit_price if line.locked else line.unit_price),
                                                  'od_cost_sheet_id':self.id,
                                                  'od_tab_type':'amc',
                                                  'tax_id':[[6,False,[line.tax_id.id]]],
                                                  'od_analytic_acc_id':amc.id,
                                                  'od_sup_unit_cost':0,
                                                 }))
                for line in self.bmn_beta_it_maintenance_extra_expense_line:
                    bmn_exp += line.qty * (line.new_unit_price if line.locked else line.unit_price)
                    bmn_exp_cost += line.qty * line.unit_cost
                bmn_exp_product_id = self.get_product_id_from_param('product_bmn_extra_expense')
                bm_lines.append((0,0,{'name':self.get_product_name(bmn_exp_product_id),
                                    'product_id':bmn_exp_product_id,
                                    'od_manufacture_id':self.get_product_brand(bmn_exp_product_id),
                                    'product_uom_qty':1.0/amc_count,
                                    'od_original_qty':1.0/amc_count,
                                    'od_original_price':bmn_exp,
                                    'od_original_unit_cost':bmn_exp_cost,
                                    'purchase_price':bmn_exp_cost,
                                    'price_unit':bmn_exp,
                                    'od_cost_sheet_id':self.id,
                                    'od_tab_type':'amc',
                                    'tax_id':tsvat,
    #                                 'tax_id':[[6,False,[line.tax_id.id]]],
                                    'od_analytic_acc_id':amc.id,
                                    'od_sup_unit_cost':0,
                                    }))
                                    
            if not bm_lines:
                raise Warning('NO lines to Create Quotation MNT Tab')



#             O&m Sale Generation
        om_r_lines = []
        
        if self.included_om_in_quotation:
            if not (project_o_m or self.select_a0):
                raise Warning("Analytic Account Not Selected In O&amp;M Tab, Which is Enabled Included In Quotation,Please Select It")
            
            
            om_parent_analtyic = self.analytic_a5 and self.analytic_a5.id 
            om_child_ids = self.env['account.analytic.account'].search([('parent_id','=',om_parent_analtyic)])
            om_count = float(len(om_child_ids))
            for om in om_child_ids:
                om_price = 0.0
                om_cost = 0.0
                om_exp = 0.0
                om_exp_cost = 0.0
                
                for line in self.om_tech_line:
                    om_r_lines.append((0,0,{
                                                'od_manufacture_id':line.manufacture_id and line.manufacture_id.id or False,
                                                 'product_id':line.part_no.id,
                                                 'name':line.name or line.part_no.description_sale or line.part_no.name,
                                                 'od_original_qty':line.qty/om_count,
                                                 'od_original_price':line.new_unit_price if line.locked else line.unit_price,
                                                 'od_original_unit_cost':line.unit_cost_local,
                                                 'product_uom_qty':line.qty/om_count,
                                                 'price_unit':line.new_unit_price if line.locked else line.unit_price,
                                                 'purchase_price':line.unit_cost_local,
                                                 'od_analytic_acc_id':om.id,
                                                 'od_cost_sheet_id':self.id,
                                                 'od_tab_type':'o_m',
                                                 'od_sup_unit_cost':line.discounted_unit_supplier_currency,
                                                 'od_sup_line_cost':line.discounted_total_supplier_currency,
                                                 'tax_id':[[6,False,[line.tax_id.id]]] 
                                                 }))
                
                
                for om_res_line in self.om_residenteng_line:
                    om_price +=  om_res_line.qty * (om_res_line.new_unit_price if om_res_line.locked else om_res_line.unit_price)
                    om_cost +=  om_res_line.qty * om_res_line.unit_cost
                o_m_product_id = self.get_product_id_from_param('product_o_m')
                om_r_lines.append((0,0,{'name':self.get_product_name(o_m_product_id),
                                    'product_id':o_m_product_id,
                                    'od_manufacture_id':self.get_product_brand(o_m_product_id),
                                    'product_uom_qty':1.0/om_count,
                                    'od_original_qty':1.0/om_count,
                                    'od_original_price':om_price,
                                    'od_original_unit_cost':om_cost,
                                    'purchase_price':om_cost,
                                    'price_unit':om_price,
                                    'od_cost_sheet_id':self.id,
                                    'od_tab_type':'o_m',
                                    'od_analytic_acc_id':om.id,
                                    'tax_id':tsvat,
    #                                 'tax_id':[[6,False,[line.tax_id.id]]],
                                    'od_sup_unit_cost':0,
                                    }))
                for line in self.om_eqpmentreq_line:
                    om_r_lines.append((0,0,{
                                                'od_manufacture_id':line.manufacture_id and line.manufacture_id.id or False,
                                                 'product_id':line.part_no.id,
                                                  'name':line.name or line.part_no.description_sale or line.part_no.name,
                                                  'od_original_qty':line.qty/om_count,
                                                  'od_original_price':line.new_unit_price if line.locked else line.unit_price,
                                                  'od_original_unit_cost':line.unit_cost_local,
                                                  'purchase_price':line.unit_cost_local,
                                                  'product_uom_qty':line.qty/om_count,
                                                  'price_unit':line.new_unit_price if line.locked else line.unit_price,
                                                  'od_cost_sheet_id':self.id,
                                                  'od_tab_type':'o_m',
                                                  'tax_id':[[6,False,[line.tax_id.id]]],
                                                  'od_analytic_acc_id':om.id,
                                                  'od_sup_unit_cost':0,
                                                 }))
                for line in self.om_extra_line:
                    om_exp += line.qty * (line.new_unit_price if line.locked else line.unit_price)
                    om_exp_cost += line.qty * line.unit_cost
                o_m_exp_product_id = self.get_product_id_from_param('product_o_m_extra_expense')
                om_r_lines.append((0,0,{'name':self.get_product_name(o_m_exp_product_id),
                                    'product_id':o_m_exp_product_id,
                                    'od_manufacture_id':self.get_product_brand(o_m_exp_product_id),
                                    'product_uom_qty':1.0/om_count,
                                    'od_original_qty':1.0/om_count,
                                    'od_original_price':om_exp,
                                    'od_original_unit_cost':om_exp_cost,
                                    'purchase_price':om_exp_cost,
                                    'price_unit':om_exp,
                                    'od_cost_sheet_id':self.id,
                                    'od_tab_type':'o_m',
                                     'tax_id':tsvat,
    #                                 'tax_id':[[6,False,[line.tax_id.id]]],
                                    'od_analytic_acc_id':om.id,
                                    'od_sup_unit_cost':0,
                                    }))
            if not om_r_lines:
                raise Warning('NO lines to Create Quotation O&amp;M Tab')
        od_order_type_id = self.od_order_type_id and self.od_order_type_id.id
        
        if not od_order_type_id:
            raise Warning("Please Select Order Type")
        section_id = self.lead_id and self.lead_id.section_id and self.lead_id.section_id.id or False
        discount = self.special_discount
        so_vals = {
            'partner_id':customer_id,
            'bdm_user_id':bdm_user_id,
            'presale_user_id':presale_user_id,
            'od_order_type_id':od_order_type_id,
            'od_cost_sheet_id':self.id,
            'section_id':section_id,
            'x_discount':discount,
            'od_approved_date':self.approved_date,
            'project_id':self.analytic_a0 and self.analytic_a0.id
        }
        if od_order_type_id in (12,26):
            so_vals['order_policy'] = 'picking'
        so_line_map = {'mat':material_lines,'imp':b_lines,'o_m':om_r_lines,'trn':trn_lines,'amc':bm_lines, 'i_s': info_sec_lines}
        so_line_val = material_lines + b_lines + om_r_lines + trn_lines + bm_lines + info_sec_lines
        anal_maped_dict = self.map_analytic_acc(anal_dict)
        discount = self.special_discount
        if discount:
            so_line_val = self.apply_discount_create_v3(so_line_val, discount)
        if not self.sales_order_generated:
#             so_line_val = material_lines + b_lines + om_r_lines + trn_lines + bm_lines
            self.copy_revenue_summary()
            so_vals['order_line'] = so_line_val
            so_id=self.env['sale.order'].create(so_vals)
            self.od_mat_sale_id = so_id.id
            so_id.od_action_approve()
            self.design_v3=True
            self.write({'original_mp':self.returned_mp,'a_bim_cost_original':self.a_bim_cost,'a_bmn_cost_original':self.a_bmn_cost, 'a_bis_cost_original': self.a_bis_cost})
            if self.pre_opn_cost:
                self.create_pre_opne_cost_move() 
            
            
            
#             self.create_analytic_map_sale_order(anal_maped_dict,so_vals,so_line_map)
#             self.write({'original_mp':self.returned_mp})
#             if self.pre_opn_cost:
#                 self.create_pre_opne_cost_move()
                
        else:
            self.write_analytic_map_sale_order_v3(anal_maped_dict,so_vals,so_line_map,so_line_val)
            self.update_a0_inv_plan()
        self.sales_order_generated = True
        self.state = 'done'
        
    
    
    
    @api.one
    def generate_sale_order(self):
        # self.check_order_type()
#         material_line_pool = self.env['od.cost.mat.main.pro.line']
        customer_id = self.od_customer_id.id
#         project_id = self.project_id and self.project_id.id or False
#         order_type = self.order_type and self.order_type.id or False
#         if not project_id:
#             raise Warning('No Project Selected')
#         if not order_type:
#             raise Warning('No Order Type Selected')

        default_svat = self.get_product_tax()
        tsvat = [[6,False,[default_svat]]] 

        bdm_user_id = self.lead_id and self.lead_id.od_bdm_user_id and self.lead_id.od_bdm_user_id.id or False
        presale_user_id = self.lead_id and self.lead_id.od_responsible_id and self.lead_id.od_responsible_id.id or False

        type_mat = self.type_mat.id
        type_ren = self.type_ren.id
        type_bim = self.type_bim.id
        type_oim = self.type_oim.id
        type_omn = self.type_omn.id
        type_o_m = self.type_o_m.id
        type_trn = self.type_trn.id
        type_bmn = self.type_bmn.id

        project_mat = self.project_mat and self.project_mat.id
        project_ren = self.project_ren and self.project_ren.id
        project_bim = self.project_bim and self.project_bim.id
        project_oim = self.project_oim and self.project_oim.id
        project_omn = self.project_omn and self.project_omn.id
        project_o_m = self.project_o_m and self.project_o_m.id
        project_trn = self.project_trn and self.project_trn.id
        project_bmn = self.project_bmn and self.project_bmn.id

        material_lines = []
        b_lines = []
        o_lines = []
        om_lines = []
        om_r_lines = []
        trn_lines = []
        bm_lines = []

        anal_dict = {'mat':project_mat,'imp':project_bim,'oim':project_oim,'omn':project_omn,'o_m':project_o_m,'trn':project_trn,'amc':project_bmn}
        if self.select_a0:
            anal_dict = self.get_analytic_dict()
        #mat sales
        if self.included_in_quotation:
            if not (project_mat or self.select_a0):
                raise Warning("Analytic Account Not Selected In MAT Tab, Which is Enabled Included In Quotation,Please Select It")
            material_lines =[]
            mat_expense = 0.0
            mat_ext_sale = 0.0
            for line in self.mat_main_pro_line:
                material_lines.append((0,0,{
                                            'od_manufacture_id':line.manufacture_id and line.manufacture_id.id or False,
                                             'product_id':line.part_no.id,
                                             'name':line.part_no.description_sale or line.part_no.name,
                                             'od_original_qty':line.qty,
                                             'od_original_price':line.new_unit_price if line.locked else line.unit_price,
                                             'od_original_unit_cost':line.unit_cost_local,
                                             'product_uom_qty':line.qty,
                                             'price_unit':line.new_unit_price if line.locked else line.unit_price,
                                             'purchase_price':line.unit_cost_local,
                                             'od_analytic_acc_id':project_mat,
                                             'od_cost_sheet_id':self.id,
                                             'od_tab_type':'mat',
                                             'od_sup_unit_cost':line.discounted_unit_supplier_currency,
                                             'od_sup_line_cost':line.discounted_total_supplier_currency,
                                             'tax_id':[[6,False,[line.tax_id.id]]] 
                                             }))
                
                    

            for line in self.mat_extra_expense_line:
                mat_expense += line.qty * line.unit_cost_local
                mat_ext_sale += line.qty * (line.new_unit_price if line.locked else line.unit_price2)
            mat_exp_product_id = self.get_product_id_from_param('product_mat_extra_expense')
            material_lines.append((0,0,{
                                    'name':self.get_product_name(mat_exp_product_id),
                                    'od_manufacture_id':self.get_product_brand(mat_exp_product_id),
                                    'product_id':mat_exp_product_id,
                                    'product_uom_qty':1,
                                    'price_unit':mat_ext_sale,
                                     'od_original_qty':1,
                                     'od_original_unit_cost':mat_expense,
                                     'purchase_price':mat_expense,
                                     'od_original_price':mat_ext_sale,
                                      'od_cost_sheet_id':self.id,
                                      'od_tab_type':'mat',
                                     'od_analytic_acc_id':project_mat,
                                     'tax_id':tsvat,
#                                      'tax_id':[[6,False,[line.tax_id.id]]],
                                     'od_sup_unit_cost':0,
                                            
                                    }))
            if not material_lines:
                raise Warning('NO lines to Create Quotation for MAT Tab')
        if self.pre_opn_cost:
            pre_opn_cost =self.pre_opn_cost
            pre_opn_cost_product_id = self.get_product_id_from_param('product_pre_opn_expense')
            material_lines.append((0,0,{
                                    'name':self.get_product_name(pre_opn_cost_product_id),
                                    'od_manufacture_id':self.get_product_brand(pre_opn_cost_product_id),
                                    'product_id':pre_opn_cost_product_id,
                                    'product_uom_qty':1,
                                    'price_unit':0.0,
                                     'od_original_qty':1,
                                     'od_original_unit_cost':pre_opn_cost,
                                     'purchase_price':pre_opn_cost,
                                     'od_original_price':0.0,
                                      'od_cost_sheet_id':self.id,
                                      'od_tab_type':'mat',
                                     'od_analytic_acc_id':project_mat,
#                                      'tax_id':[[6,False,[line.tax_id.id]]],
                                     'od_sup_unit_cost':0,
                                            
                                    }))
            
        # Training Sale Order
        if self.included_trn_in_quotation:

            trn_lines =[]
            trn_expense = 0.0
            trn_extra_sale = 0.0
            for line in self.trn_customer_training_line:
                if not (project_trn or self.select_a0):
                    raise Warning("Analytic Account Not Selected In TRN Tab, Which is Enabled Included In Quotation,Please Select It")
                trn_lines.append((0,0,{
                                            'od_manufacture_id':line.manufacture_id and line.manufacture_id.id or False,
                                            'product_id':line.part_no.id,
                                            'name':line.part_no.description_sale or line.part_no.name,
                                            'od_original_qty':line.qty,
                                            'od_original_price':line.new_unit_price if line.locked else line.unit_price,
                                            'od_original_unit_cost':line.unit_cost_local,
                                            'purchase_price':line.unit_cost_local,
                                            'product_uom_qty':line.qty,
                                            'price_unit':line.new_unit_price if line.locked else line.unit_price,
                                            'od_cost_sheet_id':self.id,
                                            'od_tab_type':'trn',
                                            'od_analytic_acc_id':project_trn,
                                            'tax_id':[[6,False,[line.tax_id.id]]],
                                            'od_sup_unit_cost':line.discounted_unit_supplier_currency,
                                            'od_sup_line_cost':line.discounted_total_supplier_currency,
                                             }))
            for line in self.trn_customer_training_extra_expense_line:
                trn_expense += line.qty * line.unit_cost_local
                trn_extra_sale += line.qty * (line.new_unit_price if line.locked else line.unit_price2)
            trn_exp_product_id = self.get_product_id_from_param('product_trn_extra_expense')
            trn_lines.append((0,0,{
                                    'name':self.get_product_name(trn_exp_product_id),
                                    'od_manufacture_id':self.get_product_brand(trn_exp_product_id),
                                    'product_id':trn_exp_product_id,
                                    'product_uom_qty':1,
                                    'od_original_qty':1,
                                    'od_original_price':trn_extra_sale,
                                    'od_original_unit_cost':trn_expense,
                                    'purchase_price':trn_expense,
                                    'price_unit':trn_extra_sale,
                                    'od_cost_sheet_id':self.id,
                                    'od_tab_type':'trn',
                                    'tax_id':tsvat,
#                                      'tax_id':[[6,False,[line.tax_id.id]]],
                                    'od_analytic_acc_id':project_trn,
                                    'od_sup_unit_cost':0,
                                    
                                }))

            if not trn_lines:
                raise Warning('NO lines to Create Quotation TRN Tab')

#         Bim sale order generation #Now Imp tab

        bi_ext_exp = 0.0
        bi_ext_exp_cost = 0.0
        bim_price = bim_cost= 0
        b_lines = []
        oim_price = 0.0
        oim_cost  = 0.0
        oim_exp= 0.0
        oim_exp_cost = 0.0
        if self.bim_log_select:
            bim_price = self.bim_log_price
            bim_cost = self.bim_log_cost
        if self.included_bim_in_quotation:
            if not (project_bim or self.select_a0):
                raise Warning("Analytic Account Not Selected In IMP Tab, Which is Enabled Included In Quotation,Please Select It")

            
            for line in self.imp_tech_line:
                b_lines.append((0,0,{
                                            'od_manufacture_id':line.manufacture_id and line.manufacture_id.id or False,
                                             'product_id':line.part_no.id,
                                             'name':line.part_no.description_sale or line.part_no.name,
                                             'od_original_qty':line.qty,
                                             'od_original_price':line.new_unit_price if line.locked else line.unit_price,
                                             'od_original_unit_cost':line.unit_cost_local,
                                             'product_uom_qty':line.qty,
                                             'price_unit':line.new_unit_price if line.locked else line.unit_price,
                                             'purchase_price':line.unit_cost_local,
                                             'od_analytic_acc_id':project_bim,
                                             'od_cost_sheet_id':self.id,
                                             'od_tab_type':'imp',
                                             'od_sup_unit_cost':line.discounted_unit_supplier_currency,
                                             'od_sup_line_cost':line.discounted_total_supplier_currency,
                                             'tax_id':[[6,False,[line.tax_id.id]]] 
                                             }))
            
            
            
            for oim_line in self.oim_extra_expenses_line:
                oim_exp += oim_line.qty * (oim_line.new_unit_price if oim_line.locked else oim_line.unit_price)
                oim_exp_cost += oim_line.qty * oim_line.unit_cost
            oim_exp_product_id = self.get_product_id_from_param('product_oim_extra_expense')
            b_lines.append((0,0,{'name':self.get_product_name(oim_exp_product_id),
                                'product_id':oim_exp_product_id,
                                'od_manufacture_id':self.get_product_brand(oim_exp_product_id),
                                'product_uom_qty':1,
                                'od_original_qty':1,
                                'od_original_price':oim_exp,
                                'od_original_unit_cost':oim_exp_cost,
                                'purchase_price':oim_exp_cost,
                                'price_unit':oim_exp,
                                'od_cost_sheet_id':self.id,
                                'od_tab_type':'imp',
                                'od_analytic_acc_id':project_bim,
                                'tax_id':tsvat,
                                
#                                 'tax_id':[[6,False,[line.tax_id.id]]],
                                'od_sup_unit_cost':0,
                                }))
            for oim_line in self.oim_implimentation_price_line:
                oim_price += oim_line.qty * (oim_line.new_unit_price if oim_line.locked else oim_line.unit_price)
                oim_cost += oim_line.qty * oim_line.unit_cost
            oim_product_id = self.get_product_id_from_param('product_oim')
            b_lines.append((0,0,{'name':self.get_product_name(oim_product_id),
                                'od_manufacture_id':self.get_product_brand(oim_product_id),
                                'product_id':oim_product_id,
                                'product_uom_qty':1,
                                'od_original_qty':1,
                                'od_original_price':oim_price,
                                'od_original_unit_cost':oim_cost,
                                'purchase_price':oim_cost,
                                'price_unit':oim_price,
                                'od_cost_sheet_id':self.id,
                                'tax_id':tsvat,
#                                 'tax_id':[[6,False,[line.tax_id.id]]],
                                'od_tab_type':'imp',
                                'od_analytic_acc_id':project_bim,
                                'od_sup_unit_cost':0,
                                }))


            for bim_line in self.implimentation_extra_expense_line:
                bi_ext_exp += bim_line.qty * ( bim_line.new_unit_price if bim_line.locked else bim_line.unit_price)
                bi_ext_exp_cost +=  bim_line.qty * bim_line.unit_cost
            bim_exp_product_id = self.get_product_id_from_param('product_bim_extra_expense')
            b_lines.append((0,0,{
                            'name':self.get_product_name(bim_exp_product_id),
                            'od_manufacture_id':self.get_product_brand(bim_exp_product_id),
                            'product_id':bim_exp_product_id,
                            'product_uom_qty':1,
                            'od_original_qty':1,
                            'od_original_price':bi_ext_exp,
                            'od_original_unit_cost':bi_ext_exp_cost,
                            'purchase_price':bi_ext_exp_cost,
                            'price_unit':bi_ext_exp,
                            'od_cost_sheet_id':self.id,
                            'od_tab_type':'imp',
                            'tax_id':tsvat,
#                             'tax_id':[[6,False,[line.tax_id.id]]],
                            'od_analytic_acc_id':project_bim,
                            'od_sup_unit_cost':0,
                                }))
            for bim_line in self.manpower_manual_line:
                bim_price +=  bim_line.qty * ( bim_line.new_unit_price if bim_line.locked else  bim_line.unit_price)
                bim_cost += bim_line.qty * bim_line.unit_cost
            if self.bim_imp_select:
                for bim_line in self.bim_implementation_code_line:
                    bim_price +=  bim_line.qty *( bim_line.new_unit_price if bim_line.locked else  bim_line.unit_price)
                    bim_cost += bim_line.qty * bim_line.unit_cost
            bim_product_id = self.get_product_id_from_param('product_bim')
            b_lines.append((0,0,{'name':self.get_product_name(bim_product_id),
                                 'product_id':bim_product_id,
                                 'od_manufacture_id':self.get_product_brand(bim_product_id),
                                'product_uom_qty':1,
                                'od_original_qty':1,
                                'od_original_price':bim_price,
                                'od_original_unit_cost':bim_cost,
                                'purchase_price':bim_cost,
                                'price_unit':bim_price,
                                'od_cost_sheet_id':self.id,
                                'od_tab_type':'imp',
                                 'tax_id':tsvat,
#                             'tax_id':[[6,False,[line.tax_id.id]]],
                                'od_analytic_acc_id':project_bim,
                                'od_sup_unit_cost':0,
            }))
            
            for line in self.ps_vendor_line:
                b_lines.append((0,0,{
                                            'od_manufacture_id':line.manufacture_id and line.manufacture_id.id or False,
                                             'product_id':line.part_no.id,
                                             'name':line.part_no.description_sale or line.part_no.name,
                                             'od_original_qty':line.qty,
                                             'od_original_price':line.new_unit_price if line.locked else line.unit_price,
                                             'od_original_unit_cost':line.unit_cost_local,
                                             'product_uom_qty':line.qty,
                                             'price_unit':line.new_unit_price if line.locked else line.unit_price,
                                             'purchase_price':line.unit_cost_local,
                                             'od_analytic_acc_id':project_bim,
                                             'od_cost_sheet_id':self.id,
                                             'od_tab_type':'imp',
                                             'od_sup_unit_cost':line.discounted_unit_supplier_currency,
                                             'od_sup_line_cost':line.discounted_total_supplier_currency,
                                             'tax_id':[[6,False,[line.tax_id.id]]] 
                                             }))
            if not b_lines:
                raise Warning('NO lines to Create Quotation IMP Tab')
#             Bmn Sale order Generation #Now Amc
        bm_lines = []
        bmn_price = 0.0
        bmn_cost = 0.0
        bmn_exp = 0.0
        bmn_exp_cost = 0.0
        omn_price = 0.0
        omn_cost = 0.0
        omn_exp = 0.0
        omn_exp_cost = 0.0
        if self.included_bmn_in_quotation:
            
            
            
            for line in self.amc_tech_line:
                bm_lines.append((0,0,{
                                            'od_manufacture_id':line.manufacture_id and line.manufacture_id.id or False,
                                             'product_id':line.part_no.id,
                                             'name':line.part_no.description_sale or line.part_no.name,
                                             'od_original_qty':line.qty,
                                             'od_original_price':line.new_unit_price if line.locked else line.unit_price,
                                             'od_original_unit_cost':line.unit_cost_local,
                                             'product_uom_qty':line.qty,
                                             'price_unit':line.new_unit_price if line.locked else line.unit_price,
                                             'purchase_price':line.unit_cost_local,
                                             'od_analytic_acc_id':project_bmn,
                                             'od_cost_sheet_id':self.id,
                                             'od_tab_type':'amc',
                                             'od_sup_unit_cost':line.discounted_unit_supplier_currency,
                                             'od_sup_line_cost':line.discounted_total_supplier_currency,
                                             'tax_id':[[6,False,[line.tax_id.id]]] 
                                             }))
            
            
            
            
            
            if not (project_bmn or self.select_a0):
                raise Warning("Analytic Account Not Selected In AMC Tab, Which is Enabled Included In Quotation,Please Select It")
            for omn_line in self.omn_out_preventive_maintenance_line:
                omn_price += omn_line.qty * (omn_line.new_unit_price if omn_line.locked else omn_line.unit_price)
                omn_cost += omn_line.qty * omn_line.unit_cost
            for omn_line in self.omn_out_remedial_maintenance_line:
                omn_price += omn_line.qty * (omn_line.new_unit_price if omn_line.locked else omn_line.unit_price)
                omn_cost += omn_line.qty * omn_line.unit_cost
            
            
            
            
            
            
            omn_product_id = self.get_product_id_from_param('product_omn')
            bm_lines.append((0,0,{'name':self.get_product_name(omn_product_id),
                                 'product_id':omn_product_id,
                                 'od_manufacture_id':self.get_product_brand(omn_product_id),
                                'product_uom_qty':1,
                                'od_original_qty':1,
                                'od_original_price':omn_price,
                                'od_original_unit_cost':omn_cost,
                                'purchase_price':omn_cost,
                                'price_unit':omn_price,
                                'od_cost_sheet_id':self.id,
                                'od_tab_type':'amc',
                                'tax_id':tsvat,
                                'od_analytic_acc_id':project_bmn,
                                'od_sup_unit_cost':0,
                                }))
            for line in self.omn_spare_parts_line:
                bm_lines.append((0,0,{
                                            'od_manufacture_id':line.manufacture_id and line.manufacture_id.id or False,
                                             'product_id':line.part_no.id,
                                             'name':line.part_no.description_sale or line.part_no.name,
                                             'product_uom_qty':line.qty,
                                             'od_original_qty':line.qty,
                                             'od_original_price':line.new_unit_price if line.locked else line.unit_price,
                                             'od_original_unit_cost':line.unit_cost_local,
                                             'purchase_price':line.unit_cost_local,
                                             'price_unit':line.new_unit_price if line.locked else line.unit_price,
                                              'od_cost_sheet_id':self.id,
                                             'od_tab_type':'amc',
                                             'tax_id':[[6,False,[line.tax_id.id]]],
                                             'od_analytic_acc_id':project_bmn,
                                             'od_sup_unit_cost':0,

                                             }))
            for line in self.omn_maintenance_extra_expense_line:
                omn_exp += line.qty * (line.new_unit_price if line.locked else line.unit_price)
                omn_exp_cost += line.qty * line.unit_cost
            omn_exp_product_id = self.get_product_id_from_param('product_omn_extra_expense')
            bm_lines.append((0,0,{'name':self.get_product_name(omn_exp_product_id),
                                'product_id':omn_exp_product_id,
                                'od_manufacture_id':self.get_product_brand(omn_exp_product_id),
                                'product_uom_qty':1,
                                'od_original_qty':1,
                                'od_original_price':omn_exp,
                                'od_original_unit_cost':omn_exp_cost,
                                'purchase_price':omn_exp_cost,
                                'price_unit':omn_exp,
                                'od_cost_sheet_id':self.id,
                                'od_tab_type':'amc',
                                 'tax_id':tsvat,
#                                 'tax_id':[[6,False,[line.tax_id.id]]],
                                'od_analytic_acc_id':project_bmn,
                                'od_sup_unit_cost':0,
                                }))

            for bmn_line in self.bmn_it_preventive_line:
                bmn_price += bmn_line.qty * (bmn_line.new_unit_price if bmn_line.locked else bmn_line.unit_price)
                bmn_cost += bmn_line.qty * bmn_line.unit_cost
            for bmn_line in self.bmn_it_remedial_line:
                bmn_price += bmn_line.qty * (bmn_line.new_unit_price if bmn_line.locked else bmn_line.unit_price)
                bmn_cost += bmn_line.qty * bmn_line.unit_cost
            bmn_product_id = self.get_product_id_from_param('product_bmn')
            bm_lines.append((0,0,{'name':self.get_product_name(bmn_product_id),
                                'product_id':bmn_product_id,
                                'od_manufacture_id':self.get_product_brand(bmn_product_id),
                                'product_uom_qty':1,
                                'od_original_qty':1,
                                'od_original_price':bmn_price,
                                'od_original_unit_cost':bmn_cost,
                                'purchase_price':bmn_cost,
                                'price_unit':bmn_price,
                                'od_cost_sheet_id':self.id,
                                'od_tab_type':'amc',
                                 'tax_id':tsvat,
#                                 'tax_id':[[6,False,[line.tax_id.id]]],
                                'od_analytic_acc_id':project_bmn,
                                'od_sup_unit_cost':0,
                                }))
            for line in self.bmn_spareparts_beta_it_maintenance_line:
                bm_lines.append((0,0,{
                                            'od_manufacture_id':line.manufacture_id and line.manufacture_id.id or False,
                                             'product_id':line.part_no.id,
                                              'name':line.part_no.description_sale or line.part_no.name,
                                              'od_original_qty':line.qty,
                                              'od_original_price':(line.new_unit_price if line.locked else line.unit_price),
                                              'od_original_unit_cost':line.unit_cost_local,
                                              'purchase_price':line.unit_cost_local,
                                              'product_uom_qty':line.qty,
                                              'price_unit':(line.new_unit_price if line.locked else line.unit_price),
                                              'od_cost_sheet_id':self.id,
                                              'od_tab_type':'amc',
                                              'tax_id':[[6,False,[line.tax_id.id]]],
                                              'od_analytic_acc_id':project_bmn,
                                              'od_sup_unit_cost':0,
                                             }))
            for line in self.bmn_beta_it_maintenance_extra_expense_line:
                bmn_exp += line.qty * (line.new_unit_price if line.locked else line.unit_price)
                bmn_exp_cost += line.qty * line.unit_cost
            bmn_exp_product_id = self.get_product_id_from_param('product_bmn_extra_expense')
            bm_lines.append((0,0,{'name':self.get_product_name(bmn_exp_product_id),
                                'product_id':bmn_exp_product_id,
                                'od_manufacture_id':self.get_product_brand(bmn_exp_product_id),
                                'product_uom_qty':1,
                                'od_original_qty':1,
                                'od_original_price':bmn_exp,
                                'od_original_unit_cost':bmn_exp_cost,
                                'purchase_price':bmn_exp_cost,
                                'price_unit':bmn_exp,
                                'od_cost_sheet_id':self.id,
                                'od_tab_type':'amc',
                                'tax_id':tsvat,
#                                 'tax_id':[[6,False,[line.tax_id.id]]],
                                'od_analytic_acc_id':project_bmn,
                                'od_sup_unit_cost':0,
                                }))
            if not bm_lines:
                raise Warning('NO lines to Create Quotation MNT Tab')



#             O&m Sale Generation
        om_r_lines = []
        om_price = 0.0
        om_cost = 0.0
        om_exp = 0.0
        om_exp_cost = 0.0
        if self.included_om_in_quotation:
            if not (project_o_m or self.select_a0):
                raise Warning("Analytic Account Not Selected In O&amp;M Tab, Which is Enabled Included In Quotation,Please Select It")
            
            
            
            
            for line in self.om_tech_line:
                om_r_lines.append((0,0,{
                                            'od_manufacture_id':line.manufacture_id and line.manufacture_id.id or False,
                                             'product_id':line.part_no.id,
                                             'name':line.part_no.description_sale or line.part_no.name,
                                             'od_original_qty':line.qty,
                                             'od_original_price':line.new_unit_price if line.locked else line.unit_price,
                                             'od_original_unit_cost':line.unit_cost_local,
                                             'product_uom_qty':line.qty,
                                             'price_unit':line.new_unit_price if line.locked else line.unit_price,
                                             'purchase_price':line.unit_cost_local,
                                             'od_analytic_acc_id':project_bmn,
                                             'od_cost_sheet_id':self.id,
                                             'od_tab_type':'o_m',
                                             'od_sup_unit_cost':line.discounted_unit_supplier_currency,
                                             'od_sup_line_cost':line.discounted_total_supplier_currency,
                                             'tax_id':[[6,False,[line.tax_id.id]]] 
                                             }))
            
            
            for om_res_line in self.om_residenteng_line:
                om_price +=  om_res_line.qty * (om_res_line.new_unit_price if om_res_line.locked else om_res_line.unit_price)
                om_cost +=  om_res_line.qty * om_res_line.unit_cost
            o_m_product_id = self.get_product_id_from_param('product_o_m')
            om_r_lines.append((0,0,{'name':self.get_product_name(o_m_product_id),
                                'product_id':o_m_product_id,
                                'od_manufacture_id':self.get_product_brand(o_m_product_id),
                                'product_uom_qty':1,
                                'od_original_qty':1,
                                'od_original_price':om_price,
                                'od_original_unit_cost':om_cost,
                                'purchase_price':om_cost,
                                'price_unit':om_price,
                                'od_cost_sheet_id':self.id,
                                'od_tab_type':'o_m',
                                'od_analytic_acc_id':project_o_m,
                                'tax_id':tsvat,
#                                 'tax_id':[[6,False,[line.tax_id.id]]],
                                'od_sup_unit_cost':0,
                                }))
            for line in self.om_eqpmentreq_line:
                om_r_lines.append((0,0,{
                                            'od_manufacture_id':line.manufacture_id and line.manufacture_id.id or False,
                                             'product_id':line.part_no.id,
                                              'name':line.part_no.description_sale or line.part_no.name,
                                              'od_original_qty':line.qty,
                                              'od_original_price':line.new_unit_price if line.locked else line.unit_price,
                                              'od_original_unit_cost':line.unit_cost_local,
                                              'purchase_price':line.unit_cost_local,
                                              'product_uom_qty':line.qty,
                                              'price_unit':line.new_unit_price if line.locked else line.unit_price,
                                              'od_cost_sheet_id':self.id,
                                              'od_tab_type':'o_m',
                                              'tax_id':[[6,False,[line.tax_id.id]]],
                                              'od_analytic_acc_id':project_o_m,
                                              'od_sup_unit_cost':0,
                                             }))
            for line in self.om_extra_line:
                om_exp += line.qty * (line.new_unit_price if line.locked else line.unit_price)
                om_exp_cost += line.qty * line.unit_cost
            o_m_exp_product_id = self.get_product_id_from_param('product_o_m_extra_expense')
            om_r_lines.append((0,0,{'name':self.get_product_name(o_m_exp_product_id),
                                'product_id':o_m_exp_product_id,
                                'od_manufacture_id':self.get_product_brand(o_m_exp_product_id),
                                'product_uom_qty':1,
                                'od_original_qty':1,
                                'od_original_price':om_exp,
                                'od_original_unit_cost':om_exp_cost,
                                'purchase_price':om_exp_cost,
                                'price_unit':om_exp,
                                'od_cost_sheet_id':self.id,
                                'od_tab_type':'o_m',
                                 'tax_id':tsvat,
#                                 'tax_id':[[6,False,[line.tax_id.id]]],
                                'od_analytic_acc_id':project_o_m,
                                'od_sup_unit_cost':0,
                                }))
            if not om_r_lines:
                raise Warning('NO lines to Create Quotation O&amp;M Tab')
        od_order_type_id = self.od_order_type_id and self.od_order_type_id.id
        pprint(om_r_lines)
        if not od_order_type_id:
            raise Warning("Please Select Order Type")
        section_id = self.lead_id and self.lead_id.section_id and self.lead_id.section_id.id or False
        discount = self.special_discount
        so_vals = {
            'partner_id':customer_id,
            'bdm_user_id':bdm_user_id,
            'presale_user_id':presale_user_id,
            'od_order_type_id':od_order_type_id,
            'od_cost_sheet_id':self.id,
            'section_id':section_id,
            'x_discount':discount,
            'od_approved_date':self.approved_date,
        }
        if od_order_type_id in (12,26):
            so_vals['order_policy'] = 'picking'
        so_line_map = {'mat':material_lines,'imp':b_lines,'o_m':om_r_lines,'trn':trn_lines,'amc':bm_lines}

        anal_maped_dict = self.map_analytic_acc(anal_dict)
        if not self.sales_order_generated:
            self.copy_revenue_summary()
            self.create_analytic_map_sale_order(anal_maped_dict,so_vals,so_line_map)
            self.write({'original_mp':self.returned_mp})
            if self.pre_opn_cost:
                self.create_pre_opne_cost_move()
                
        else:
            self.write_analytic_map_sale_order(anal_maped_dict,so_vals,so_line_map)
        self.sales_order_generated = True
        self.state = 'done'

    @api.one
    def recreate_sale(self):
        pass
    
    @api.one
    def unlink(self):
        if self.state != 'draft':
            raise Warning("You Can Only Delete Draft Cost Sheet")
        return super(od_cost_sheet,self).unlink()
    
    @api.one
    def compute_value(self):
        curr_fluct = []
        shipping_list =[]
        customs_list =[]
        stock_provision_list = []
        conting_provision_list = []
        group_pool =self.env['od.cost.costgroup.material.line']
        for material in self.mat_main_pro_line:
            unit_amount = material.discounted_unit_supplier_currency * material.qty
            for group in material.group:
                ex_rate =group.currency_exchange_factor
                base_factor = unit_amount * ex_rate
                currency_fluct = base_factor * group.currency_fluctation_provision/100
                shipping = base_factor * group.shipping/100
                customs = base_factor * group.customs/100
                stock_provision = base_factor * group.stock_provision/100
                conting_provision = base_factor * group.conting_provision/100
                curr_fluct.append({'group_id':group.id,'currency_fluct':currency_fluct})
                shipping_list.append({'group_id':group.id,'shipping':shipping})
                customs_list.append({'group_id':group.id,'customs':customs})
                stock_provision_list.append({'group_id':group.id,'stock_provision':stock_provision})
                conting_provision_list.append({'group_id':group.id,'conting_provision':conting_provision})
                
        for material in self.trn_customer_training_line:
            unit_amount = material.discounted_unit_supplier_currency * material.qty
            for group in material.group:
                ex_rate =group.currency_exchange_factor
                base_factor = unit_amount * ex_rate
                currency_fluct = base_factor * group.currency_fluctation_provision/100
                shipping = base_factor * group.shipping/100
                customs = base_factor * group.customs/100
                stock_provision = base_factor * group.stock_provision/100
                conting_provision = base_factor * group.conting_provision/100
                curr_fluct.append({'group_id':group.id,'currency_fluct':currency_fluct})
                shipping_list.append({'group_id':group.id,'shipping':shipping})
                customs_list.append({'group_id':group.id,'customs':customs})
                stock_provision_list.append({'group_id':group.id,'stock_provision':stock_provision})
                conting_provision_list.append({'group_id':group.id,'conting_provision':conting_provision})
        
        for material in self.bmn_spareparts_beta_it_maintenance_line:
            unit_amount = material.discounted_unit_supplier_currency * material.qty
            for group in material.group:
                ex_rate =group.currency_exchange_factor
                base_factor = unit_amount * ex_rate
                currency_fluct = base_factor * group.currency_fluctation_provision/100
                shipping = base_factor * group.shipping/100
                customs = base_factor * group.customs/100
                stock_provision = base_factor * group.stock_provision/100
                conting_provision = base_factor * group.conting_provision/100
                curr_fluct.append({'group_id':group.id,'currency_fluct':currency_fluct})
                shipping_list.append({'group_id':group.id,'shipping':shipping})
                customs_list.append({'group_id':group.id,'customs':customs})
                stock_provision_list.append({'group_id':group.id,'stock_provision':stock_provision})
                conting_provision_list.append({'group_id':group.id,'conting_provision':conting_provision})

        
        # computing currency_fluct value
        c = defaultdict(int)
        for d in curr_fluct:
            c[d['group_id']] += d['currency_fluct']
        currency_fluct_dict=[{'group_id': group_id, 'currency_fluct': currency_fluct} for group_id, currency_fluct in c.items()]
        for val in currency_fluct_dict:
            group_id = val.get('group_id',False)
            curr_amnt = val.get('currency_fluct',0.0)
            group_obj = group_pool.browse(group_id)
            group_obj.currency_fluct_value = curr_amnt

        # computing shipping value
        c = defaultdict(int)
        for d in shipping_list:
            c[d['group_id']] += d['shipping']
        shipping_dict=[{'group_id': group_id, 'shipping': shipping} for group_id, shipping in c.items()]
        for val in shipping_dict:
            group_id = val.get('group_id',False)
            shipping_amnt = val.get('shipping',0.0)
            group_obj = group_pool.browse(group_id)
            group_obj.shipping_value = shipping_amnt


        # computing Customs value
        c = defaultdict(int)
        for d in customs_list:
            c[d['group_id']] += d['customs']
        customs_dict=[{'group_id': group_id, 'customs': customs} for group_id, customs in c.items()]
        for val in customs_dict:
            group_id = val.get('group_id',False)
            customs_amnt = val.get('customs',0.0)
            group_obj = group_pool.browse(group_id)
            group_obj.customs_value = customs_amnt

        # computing stock provision value
        c = defaultdict(int)
        for d in stock_provision_list:
            c[d['group_id']] += d['stock_provision']
        stock_dict=[{'group_id': group_id, 'stock_provision': stock_provision} for group_id, stock_provision in c.items()]
        for val in stock_dict:
            group_id = val.get('group_id',False)
            stock_amnt = val.get('stock_provision',0.0)
            group_obj = group_pool.browse(group_id)
            group_obj.stock_provision_value = stock_amnt

        # computing Conting provision value
        c = defaultdict(int)
        for d in conting_provision_list:
            c[d['group_id']] += d['conting_provision']
        cont_dict=[{'group_id': group_id, 'conting_provision': conting_provision} for group_id, conting_provision in c.items()]
        for val in cont_dict:
            group_id = val.get('group_id',False)
            conting_amnt = val.get('conting_provision',0.0)
            group_obj = group_pool.browse(group_id)
            group_obj.conting_provision_value = conting_amnt

    ###completed this func
    @api.one
    def compute_value_optional(self):
        curr_fluct = []
        shipping_list =[]
        customs_list =[]
        stock_provision_list = []
        conting_provision_list = []
        group_pool =self.env['od.cost.costgroup.optional.line.two']
        for material in self.mat_optional_item_line:
            unit_amount = material.discounted_unit_supplier_currency * material.qty
            for group in material.group_id:
                ex_rate =group.currency_exchange_factor
                base_factor = unit_amount * ex_rate
                currency_fluct = base_factor * group.currency_fluctation_provision/100
                shipping = base_factor * group.shipping/100
                customs = base_factor * group.customs/100
                stock_provision = base_factor * group.stock_provision/100
                conting_provision = base_factor * group.conting_provision/100
                curr_fluct.append({'group_id':group.id,'currency_fluct':currency_fluct})
                shipping_list.append({'group_id':group.id,'shipping':shipping})
                customs_list.append({'group_id':group.id,'customs':customs})
                stock_provision_list.append({'group_id':group.id,'stock_provision':stock_provision})
                conting_provision_list.append({'group_id':group.id,'conting_provision':conting_provision})

        # computing currency_fluct value
        c = defaultdict(int)
        for d in curr_fluct:
            c[d['group_id']] += d['currency_fluct']
        currency_fluct_dict=[{'group_id': group_id, 'currency_fluct': currency_fluct} for group_id, currency_fluct in c.items()]
        for val in currency_fluct_dict:
            group_id = val.get('group_id',False)
            curr_amnt = val.get('currency_fluct',0.0)
            group_obj = group_pool.browse(group_id)
            group_obj.currency_fluct_value = curr_amnt

        # computing shipping value
        c = defaultdict(int)
        for d in shipping_list:
            c[d['group_id']] += d['shipping']
        shipping_dict=[{'group_id': group_id, 'shipping': shipping} for group_id, shipping in c.items()]
        for val in shipping_dict:
            group_id = val.get('group_id',False)
            shipping_amnt = val.get('shipping',0.0)
            group_obj = group_pool.browse(group_id)
            group_obj.shipping_value = shipping_amnt


        # computing Customs value
        c = defaultdict(int)
        for d in customs_list:
            c[d['group_id']] += d['customs']
        customs_dict=[{'group_id': group_id, 'customs': customs} for group_id, customs in c.items()]
        for val in customs_dict:
            group_id = val.get('group_id',False)
            customs_amnt = val.get('customs',0.0)
            group_obj = group_pool.browse(group_id)
            group_obj.customs_value = customs_amnt

        # computing stock provision value
        c = defaultdict(int)
        for d in stock_provision_list:
            c[d['group_id']] += d['stock_provision']
        stock_dict=[{'group_id': group_id, 'stock_provision': stock_provision} for group_id, stock_provision in c.items()]
        for val in stock_dict:
            group_id = val.get('group_id',False)
            stock_amnt = val.get('stock_provision',0.0)
            group_obj = group_pool.browse(group_id)
            group_obj.stock_provision_value = stock_amnt

        # computing Conting provision value
        c = defaultdict(int)
        for d in conting_provision_list:
            c[d['group_id']] += d['conting_provision']
        cont_dict=[{'group_id': group_id, 'conting_provision': conting_provision} for group_id, conting_provision in c.items()]
        for val in cont_dict:
            group_id = val.get('group_id',False)
            conting_amnt = val.get('conting_provision',0.0)
            group_obj = group_pool.browse(group_id)
            group_obj.conting_provision_value = conting_amnt
    # completed


class od_amc_analytic_lines(models.Model):
    _name = 'od.amc.analytic.lines'
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet')
    
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    analytic_id = fields.Many2one('account.analytic.account',string="Analytic Account")
    state = fields.Selection(string ='State', related='analytic_id.state')
    so_id = fields.Many2one('sale.order',string="Sales Order")

class od_om_analytic_lines(models.Model):
    _name = 'od.om.analytic.lines'
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet')
    
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    analytic_id = fields.Many2one('account.analytic.account',string="Analytic Account")
    state = fields.Selection(string ='State', related='analytic_id.state')
    so_id = fields.Many2one('sale.order',string="Sales Order")

class od_date_log_history(models.Model):
    _name = 'od.date.log.history'
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet')
    name = fields.Char(string='Name')
    date = fields.Datetime(string="Date")
    
class od_gp_approval_log(models.Model):
    _name = 'gp.approval.log'
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet')
    name = fields.Char(string='Name')
    date = fields.Datetime(string="Date")
    gp_perc = fields.Float(string="GP Percent", digits=(16,3))
    user_id = fields.Many2one('res.users', string="Approved by")
    
class od_customer_reg(models.Model):
    _name ='od.customer.reg'
    name = fields.Char('Customer Registration')

class od_doc_type(models.Model):
    _name ='od.doc.type'
    name = fields.Char(string='Name')

class od_deadline_type(models.Model):
    _name ='od.deadline.type'
    name = fields.Char(string='Name')

class od_reviewer_comment(models.Model):
    _name = 'od.reviewer.comment'
    name = fields.Char('Comment')

class od_support_doc_line(models.Model):
    _name ='od.support.doc.line'
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet')
    doc_type_id = fields.Many2one('od.doc.type',string='Document Type')
    date = fields.Date(string='Date')
    ref = fields.Char(string='Reference')
    rev_comment_id = fields.Many2one('od.reviewer.comment',string="Reviewer Comment")
    fin_comment_id  = fields.Many2one('od.finance.comment','Finance Comment')
class od_deadlines(models.Model):
    _name = 'od.deadlines'
    _inherit = 'od.support.doc.line'
    deadline_type_id = fields.Many2one('od.deadline.type',string='Deadline Type')
    DOM = [
        ('mat','Material Delivery Deadline'),
        ('project_start','Project Start Deadline'),
        ('project_close','Project Closing Deadline'),
        ('maint_start','Maintenance Start Deadline'),
        ('maint_close','Maintenance Closing Deadline'),
        ('availability','Availability of Resident Engineers Deadline'),
        ('start','Start of Operations Deadline'),
        ('end','End of Operations Deadline'),
 
    ]
    
    deadline_type = fields.Selection(DOM,string="Deadline Type")
    fin_comment_id  = fields.Many2one('od.finance.comment','Finance Comment')
class od_payment_type(models.Model):
    _name='od.payment.type'
    name = fields.Char('Payment Type')
    
class od_supplier_quotes(models.Model):
    _name='od.supplier.quotes'
    DOM = [
        ('lpo','Supplier Quotation')
    ]
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet')
    name = fields.Selection(DOM,string="Name", default="lpo")
    partner_id = fields.Many2one('res.partner','Supplier Name')
    vendor_id = fields.Many2one('od.product.brand','Vendor Name')
    attach_file_sq = fields.Binary('Attach Quote')
    attach_fname_sq = fields.Char('Quote name')
    
class od_payment_schedule(models.Model):
    _name = 'od.payment.schedule'
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    payment_type_id = fields.Many2one('od.payment.type','Payment Type')
    value = fields.Float('Value',digits=dp.get_precision('Account'))
    milestone = fields.Char('Link to Milestone/Workpackage')
    fin_comment_id  = fields.Many2one('od.finance.comment','Finance Comment')

class od_cost_summary_line(models.Model):
    _name = 'od.cost.summary.line'
    _order = "item_int ASC"
    item_int = fields.Integer(string="Item Seq",default=1)
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    item = fields.Char(string='Item')
    description = fields.Char(string='Description')
    arabic_description = fields.Char(string='Description')
    total_price = fields.Float(string='Total Price',digits=dp.get_precision('Account'))
    



class od_cost_summary_manufacture_line(models.Model):
    _name = 'od.cost.summary.manufacture.line'
    _order = "item_int ASC"
    item_int = fields.Integer(string="Item Seq",default=1)
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    manufacture_id = fields.Many2one('od.product.brand',string='Manufacture',required="1")
    cost = fields.Float(string='Cost',digits=dp.get_precision('Account'))
    weight = fields.Float(string='Weight(%)',digits=dp.get_precision('Account'))
    profit = fields.Float(string='Profit',digits=dp.get_precision('Account'))
    profit_percentage = fields.Float(string='Profit(%)',digits=dp.get_precision('Account'))

class od_customer_role(models.Model):
    _name ='od.customer.role'
    name = fields.Char('Customer Role')
class od_customer_closing_cond(models.Model):
    _name ='od.customer.closing.cond'
    name = fields.Char('Customer Closing Condition')
class od_beta_closing_cond(models.Model):
    _name ='od.beta.closing.cond'
    name = fields.Char('Beta Closing Condition')
class od_finance_comment(models.Model):
    _name ='od.finance.comment'
    name = fields.Char('Finance Comment')
# class od_customer_closing_line(models.Model):
#     _name = 'od.customer.closing.line'
#     cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
#     customer_close_cond_id  = fields.Many2one('od.customer.closing.cond','Customer Closing Condition')
#     fin_comment_id  = fields.Many2one('od.finance.comment','Finance Comment')
# class od_beta_closing_line(models.Model):
#     _name ='od.beta.closing.line'
#     _inherit = 'od.customer.closing.line'
#     beta_close_cond_id =fields.Many2one('od.beta.closing.cond','Beta Closing Condition')

class od_comm_matrix(models.Model):
    _name = 'od.comm.matrix'
    _order = "item_int ASC"
    item_int = fields.Integer(string="Item Seq",default=1)
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    partner_id = fields.Many2one('res.partner',string='Customer',domain=[('is_company','=',False)])
    customer_role_id = fields.Many2one('od.customer.role',string='Customer Role')
    rev_comment_id = fields.Many2one('od.reviewer.comment',string="Reviewer Comment")
    fin_comment_id  = fields.Many2one('od.finance.comment','Finance Comment')

class od_cost_summary_extra_line(models.Model):
    _name = 'od.cost.summary.extra.line'
    _order = "item_int ASC"
    item_int = fields.Integer(string="Item Seq",default=1)
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    material = fields.Char(string='Material',required="1")
    total_sales = fields.Float(string='Total Sales',digits=dp.get_precision('Account'))
    total_cost = fields.Float(string='Total cost',digits=dp.get_precision('Account'))
    profit = fields.Float(string='Profit',digits=dp.get_precision('Account'))
    profit_percentage = fields.Float(string='Profit(%)',digits=dp.get_precision('Account'))
    weight = fields.Float(string='Weight(%)',digits=dp.get_precision('Account'))
    full_outsource = fields.Boolean(string='Full Outsource',default=False)
    do_not_use_equations = fields.Boolean(string='Do Not Use Equations',default=False)

class od_cost_summary_version_line(models.Model):
    _name = 'od.cost.summary.version.line'
    _order = "item_int ASC"
    item_int = fields.Integer(string="Item Seq",default=1)
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    version = fields.Char(string='Version',required="1")
    date = fields.Date(string='Date')


class od_cost_terms_payment_terms_line(models.Model):
    _name = 'od.cost.terms.payment.terms.line'
    _order = "item_int ASC"
    item_int = fields.Integer(string="Item Seq",default=1)
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    number = fields.Char(string='Number')
    payment_name = fields.Char(string='Payment Name',required="1")
    payment_percentage = fields.Char(string='Payment(%)')


class od_cost_terms_credit_terms_line(models.Model):
    _name = 'od.cost.terms.credit.terms.line'
    _order = "item_int ASC"
    item_int = fields.Integer(string="Item Seq",default=1)
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    number = fields.Char(string='Number')
    credit_period = fields.Char(string='Credit Period',required="1")
    max_credit_amount = fields.Float(string='Maximum Credit Amount')
    minimum_credit_amount = fields.Float(string='Minimum Credit Amount')

class od_cost_section_line(models.Model):
    _name = 'od.cost.section.line'
    _order = "item_int ASC"
    item_int = fields.Integer(string="Item Seq",default=1)
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    section = fields.Char(string='Section')
    name = fields.Char(string='Description')
    sale = fields.Float(string='Section Sale')
    cost = fields.Float(string='Section Cost')
    
    _rec_name = 'section'
    @api.multi
    def link_section(self):
        context = self.env.context
        cost_sheet_id = self.cost_sheet_id and self.cost_sheet_id.id or False
        ctx =  context.copy()
        ctx['cost_sheet_id'] = cost_sheet_id
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'section.mat.add.wiz',
            'context':ctx,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
    @api.multi
    def unlink_section(self):
        context = self.env.context
        cost_sheet_id = self.cost_sheet_id and self.cost_sheet_id.id or False
        section_id = self.id
        ctx =  context.copy()
        ctx['cost_sheet_id'] = cost_sheet_id
        ctx['section_id'] = section_id
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'section.mat.remove.wiz',
            'context':ctx,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }


class od_cost_opt_section_line(models.Model):
    _name = "od.cost.opt.section.line"
    _inherit = 'od.cost.section.line'
    @api.multi
    def link_section(self):
        context = self.env.context
        cost_sheet_id = self.cost_sheet_id and self.cost_sheet_id.id or False
        ctx =  context.copy()
        ctx['cost_sheet_id'] = cost_sheet_id
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'section.opt.add.wiz',
            'context':ctx,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
    @api.multi
    def unlink_section(self):
        context = self.env.context
        cost_sheet_id = self.cost_sheet_id and self.cost_sheet_id.id or False
        opt_section_id = self.id
        ctx =  context.copy()
        ctx['cost_sheet_id'] = cost_sheet_id
        ctx['opt_section_id'] = opt_section_id
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'section.opt.remove.wiz',
            'context':ctx,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }


class od_cost_trn_section_line(models.Model):
    _name = "od.cost.trn.section.line"
    _inherit = 'od.cost.section.line'
    @api.multi
    def link_section(self):
        context = self.env.context
        cost_sheet_id = self.cost_sheet_id and self.cost_sheet_id.id or False
        ctx =  context.copy()
        ctx['cost_sheet_id'] = cost_sheet_id
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'section.trn.add.wiz',
            'context':ctx,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
    @api.multi
    def unlink_section(self):
        context = self.env.context
        cost_sheet_id = self.cost_sheet_id and self.cost_sheet_id.id or False
        trn_section_id = self.id
        ctx =  context.copy()
        ctx['cost_sheet_id'] = cost_sheet_id
        ctx['trn_section_id'] = trn_section_id
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'section.trn.remove.wiz',
            'context':ctx,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

class od_proof_cost(models.Model):
    _name = 'od.proof.cost'
    name = fields.Char('Proof Of Cost')


class od_cost_costgroup_material_line(models.Model):
    _name = 'od.cost.costgroup.material.line'
    _order = "item_int ASC"
    item_int = fields.Integer(string="Item Seq",default=1)

    @api.multi
    def link_costgroup(self):
        context = self.env.context
        cost_sheet_id = self.cost_sheet_id and self.cost_sheet_id.id or False
        ctx =  context.copy()
        ctx['cost_sheet_id'] = cost_sheet_id
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'costgroup.wiz',
            'context':ctx,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
    @api.multi
    def unlink_costgroup(self):
        context = self.env.context
        cost_sheet_id = self.cost_sheet_id and self.cost_sheet_id.id or False
        costgroup_id = self.id
        ctx =  context.copy()
        ctx['cost_sheet_id'] = cost_sheet_id
        ctx['group_id'] = costgroup_id
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'costgroup.remove.wiz',
            'context':ctx,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    def name_get(self, cr, uid, ids, context=None):
        
        res = []
        for inst in self.browse(cr, uid, ids, context=context):
            name = inst.name or '/'
            cost_sheet_number = inst.cost_sheet_id.number
            if name and cost_sheet_number:
                name='['+ cost_sheet_number +']' + name
            res.append((inst.id, name))
        return res

    def od_get_currency(self):
        return self.env.user.company_id.currency_id.id
    
    def get_vat(self):
        return self.env.user.company_id.od_tax_id 
    
    def od_supplier_currency(self):
        currency2 = self.env.user.company_id and self.env.user.company_id.od_supplier_currency_id
        if not currency2:
            raise Warning("Please Configure CostGroup Default Supplier Currency")
        return currency2

    def od_get_company_id(self):
        return self.env.user.company_id

    def get_saudi_company_id(self):
        parameter_obj = self.env['ir.config_parameter']
        key =[('key', '=', 'od_beta_saudi_co')]
        company_param = parameter_obj.search(key)
        if not company_param:
            raise Warning(_('Settings Warning!'),_('No Company Parameter Not defined\nconfig it in System Parameters with od_beta_saudi_co!'))
        saudi_company_id = company_param.od_model_id and company_param.od_model_id.id or False
        return saudi_company_id


    def is_saudi_comp(self):
        res = False
        saudi_comp_id = self.get_saudi_company_id()
        user_comp_id = self.env.user.company_id.id
        if user_comp_id == saudi_comp_id:
            res = True
        return res

    def my_value(self,uae_val,saudi_val):
        res = uae_val
        if self.is_saudi_comp():
            res =saudi_val
        return res

    def get_shipping_value(self):
        res = self.my_value(5, 2)
        return res

    def get_custom(self):
        res = self.my_value(1, 5)
        return res

    def get_stock_provision(self):
        res = self.my_value(0.50,0.50)
        return res
    @api.one
    @api.depends('tax_id')
    def _compute_vat_group(self):
        vat = self.tax_id and self.tax_id.amount or 0.0
        vat = vat * 100
        self.vat = vat

    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id,readonly=True)
    supplier_id = fields.Many2one('res.partner',domain=[('supplier','=',True)],string="Manufacturer")
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    round_up = fields.Selection([(1,'0'),(2,'1'),(3,'2'),(4,'No Round')],string="Round Up",default=1)
    cost_group_number = fields.Char(string='Number')
    name = fields.Char(string='Description',required="1")
    sales_currency_id = fields.Many2one('res.currency',string='Sales Currency',default=od_get_currency)
    customer_discount = fields.Float(string='Customer Discount(%)')
    profit = fields.Float(string='Profit(%)',digits=dp.get_precision('Account'))
    supplier_discount = fields.Float(string='Supplier Discount(%)',digits=dp.get_precision('Account'))
    supplier_currency_id = fields.Many2one('res.currency',string='Supplier Currency',default=od_supplier_currency)
    currency_exchange_factor = fields.Float(string='Currency Exchange Factor',digits=dp.get_precision('Account'))
    currency_fluctation_provision = fields.Float(string='Currency Fluctuation Provision',digits=dp.get_precision('Account'))
    currency_fluct_value = fields.Float(string='Currency Fluct.Value',readonly=True,digits=dp.get_precision('Account'))
    shipping = fields.Float(string='Shipping(%)',default=get_shipping_value,digits=dp.get_precision('Account'))
    shipping_value = fields.Float(string="Shipping Value",readonly=True,digits=dp.get_precision('Account'))
    customs = fields.Float(string='Customs(%)',default=get_custom,digits=dp.get_precision('Account'))
    customs_value = fields.Float(string='Customs Value',readonly=True,digits=dp.get_precision('Account'))
    stock_provision = fields.Float(string='Stock Provision',default=get_stock_provision,digits=dp.get_precision('Account'))
    stock_provision_value = fields.Float(string='Stock Provision Value',readonly=True,digits=dp.get_precision('Account'))
    conting_provision = fields.Float(string='Conting Provision',default=0.50,digits=dp.get_precision('Account'))
    conting_provision_value = fields.Float(string='Conting Provision Value',readonly=True,digits=dp.get_precision('Account'))
    proof_of_cost  = fields.Many2one('od.proof.cost','Proof Of Cost')
    tax_id = fields.Many2one('account.tax',string="Tax",default=get_vat)
    vat = fields.Float(string="Vat %",compute='_compute_vat_group',digits=dp.get_precision('Account'))
    
    
        
    
#     @api.onchange('supplier_currency_id')
#     def onchange_supp_currency(self):
#         if self.supplier_currency_id:
#             rate = self.supplier_currency_id.rate_silent
#             self.currency_exchange_factor =1/rate

    @api.onchange('sales_currency_id','supplier_currency_id')
    def onchange_currency_rate(self):
        if self.sales_currency_id and self.supplier_currency_id:
            curr = self.env['res.currency']

            from_currency, to_currency = self.sales_currency_id,self.supplier_currency_id
            rate = curr._get_conversion_rate(from_currency, to_currency)

            exchange_fact = 1/rate
            exchange_fact= float_round(exchange_fact, precision_rounding=to_currency.rounding)
            self.currency_exchange_factor =exchange_fact
    @api.onchange('supplier_id')
    def onchange_partner_id(self):
        if self.supplier_id:
            part = self.supplier_id
            currency_id = part.property_product_pricelist_purchase and part.property_product_pricelist_purchase.currency_id and part.property_product_pricelist_purchase.currency_id.id
            self.supplier_currency_id = currency_id




class od_cost_costgroup_optional_line_two(models.Model):

    _name = 'od.cost.costgroup.optional.line.two'
    _inherit = 'od.cost.costgroup.material.line'
    @api.multi
    def link_costgroup(self):
        context = self.env.context
        cost_sheet_id = self.cost_sheet_id and self.cost_sheet_id.id or False
        ctx =  context.copy()
        ctx['cost_sheet_id'] = cost_sheet_id
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'costgroup.opt.wiz',
            'context':ctx,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
    @api.multi
    def unlink_costgroup(self):
        context = self.env.context
        cost_sheet_id = self.cost_sheet_id and self.cost_sheet_id.id or False
        costgroup_id = self.id
        ctx =  context.copy()
        ctx['cost_sheet_id'] = cost_sheet_id
        ctx['group_id'] = costgroup_id
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'costgroup.opt.remove.wiz',
            'context':ctx,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }



class od_cost_costgroup_extra_expenase_line(models.Model):

    _name = 'od.cost.costgroup.extra.expense.line'
    _inherit = 'od.cost.costgroup.material.line'
    @api.multi
    def link_costgroup(self):
        context = self.env.context
        cost_sheet_id = self.cost_sheet_id and self.cost_sheet_id.id or False
        ctx =  context.copy()
        ctx['cost_sheet_id'] = cost_sheet_id
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'costgroup.extra.wiz',
            'context':ctx,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
    @api.multi
    def unlink_costgroup(self):
        context = self.env.context
        cost_sheet_id = self.cost_sheet_id and self.cost_sheet_id.id or False
        costgroup_id = self.id
        ctx =  context.copy()
        ctx['cost_sheet_id'] = cost_sheet_id
        ctx['group_id'] = costgroup_id
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'costgroup.extra.remove.wiz',
            'context':ctx,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }



class od_cost_costgroup_it_service_line(models.Model):
    _name = 'od.cost.costgroup.it.service.line'
    _inherit = 'od.cost.costgroup.material.line'
    
    
    def od_get_currency(self):
        return self.env.user.company_id.currency_id.id
    
    def get_vat(self):
        return self.env.user.company_id.od_tax_id 
    stock_provision = fields.Float(string='Stock Provision',default=0.0,digits=dp.get_precision('Account'))
   
    supplier_currency_id = fields.Many2one('res.currency',string='Supplier Currency',default=od_get_currency)
   
    conting_provision = fields.Float(string='Conting Provision',default=0.00,digits=dp.get_precision('Account'))
    conting_provision_value = fields.Float(string='Conting Provision Value',readonly=True,digits=dp.get_precision('Account'))
    proof_of_cost  = fields.Many2one('od.proof.cost','Proof Of Cost')
    tax_id = fields.Many2one('account.tax',string="Tax",default=get_vat)
    vat = fields.Float(string="Vat %",compute='_compute_vat_group',digits=dp.get_precision('Account'))
   
    
    
    ### copy End
        
    
    
    
    
    
    
    


class od_cost_mat_main_pro_line(models.Model):
    _name = 'od.cost.mat.main.pro.line'
    _order = 'item_int ASC'


    @api.one
    @api.depends('qty','unit_cost_local','group')
    def _compute_unit_price(self):
        self.line_cost_local_currency = self.qty * self.unit_cost_local
       
        if self.group:
            group_obj = self.group
            profit = group_obj.profit/100
            
            if profit >=1:
                raise Warning("Profit value for the costgroup %s set 100 or above,it should be below 100"%group_obj.name)
            round_up_val = group_obj.round_up or 3
            round_up_val -=1
            customer_discount = group_obj.customer_discount/100
            unit_cost_local = self.unit_cost_local
#             unit_price = (unit_cost_local / (1-profit)) - (unit_cost_local * customer_discount)
            unit = unit_cost_local/(1-profit)
            unit_price = unit *(1-customer_discount)
            if round_up_val < 3:
                unit_price = round(unit_price,round_up_val)
            self.unit_price = unit_price
         

    @api.one
    @api.depends('unit_cost_supplier_currency','supplier_discount')
    def _compute_supplier_discount(self):
        
        if self.is_unit_cost_amend:
                self.unit_cost_local = self.unit_cost_amend
        
        if self.unit_cost_supplier_currency and not self.is_unit_cost_amend:
            
            unit_cost_supplier_currency = self.unit_cost_supplier_currency
            supplier_discount = self.supplier_discount/100
            discount_value = unit_cost_supplier_currency * supplier_discount
            discounted_unit_price = unit_cost_supplier_currency - discount_value
            group_obj = self.group
            ex_rate = group_obj.currency_exchange_factor
            min_qty =self.min_order
            sale_qty = self.qty
            if min_qty <= sale_qty:
                base_factor = discounted_unit_price * ex_rate
            else:
                if sale_qty:
                    base_factor = ((discounted_unit_price*min_qty)/sale_qty)* ex_rate
                else:
                    base_factor = 0
            currency_fluct = group_obj.currency_fluctation_provision/100
            shipping = group_obj.shipping/100
            customs = group_obj.customs/100
            stock_provision = group_obj.stock_provision/100
            conting_provision = group_obj.conting_provision/100
            unit_cost_local = base_factor + base_factor * currency_fluct + base_factor * shipping + base_factor * customs + base_factor * stock_provision + base_factor * conting_provision
            round_up_val = group_obj.round_up or 3
            round_up_val -=1
#             if round_up_val <3:
#                 unit_cost_local = round(unit_cost_local,round_up_val)


            self.unit_cost_local = unit_cost_local
            
            self.discounted_unit_supplier_currency = discounted_unit_price


    @api.one
    @api.depends('discounted_unit_supplier_currency','qty','min_order')
    def _discounted_total_unit(self):
        qty = self.qty
        min_order = self.min_order
        if qty > min_order:
            self.discounted_total_supplier_currency = self.discounted_unit_supplier_currency * qty
        else:
            self.discounted_total_supplier_currency = self.discounted_unit_supplier_currency * min_order
    @api.one
    @api.depends('group')
    def _compute_currency_supp_discount(self):
        if self.group:
            group_obj = self.group
            self.supplier_currency_id = group_obj.supplier_currency_id and group_obj.supplier_currency_id.id
            sales_currency_id = group_obj.sales_currency_id and group_obj.sales_currency_id.id
            supplier_discount = group_obj.supplier_discount
            self.sales_currency_id = sales_currency_id
            self.supplier_discount = supplier_discount
#             if not self.tax_id:
#                 self.tax_id = group_obj.tax_id and group_obj.tax_id.id

    @api.one
    @api.depends('qty','unit_price','new_unit_price')
    def _compute_line_price(self):
        fixed = self.fixed
        locked = self.locked
        if not (fixed or locked):
            self.line_price = self.qty * self.unit_price
        else:
            self.line_price = self.qty * self.new_unit_price
    @api.one
    @api.depends('line_price','line_cost_local_currency')
    def _compute_profit(self):
        self.profit = round(self.line_price )- round(self.line_cost_local_currency)
    @api.one
    @api.depends('line_price','profit')
    def _compute_profit_percentage(self):
        if self.line_price:
            self.profit_percentage = (self.profit/self.line_price)*100

    
    
    @api.one 
    @api.depends('tax_id','line_price','qty')
    def _compute_vat(self):
        if self.tax_id:
            vat = self.tax_id.amount 
            self.vat = vat  * 100
            vat_value = self.line_price * vat
            self.vat_value = vat_value
            
            
#     
#     @api.one 
#     @api.onchange('vat','line_price')
#     def onchange_vat(self):
#         vat = self.vat
#         line_price = self.line_price
#         vat_value = line_price * (vat/100.0)
#         self.vat_value = vat_value

    
    
    
    def get_vat(self):
        return self.env.user.company_id.od_tax_id
    
    def get_fix(self):
        return self.cost_sheet_id.price_fixed 
    
    
    @api.one
    def _get_locked_status(self):
        
        if self.cost_sheet_id and self.cost_sheet_id.price_fixed and self.cost_sheet_id.state not in ('draft','design_ready','committed','submitted','returned_by_pmo','waiting_po_open'):
            self.locked = True
    
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    check = fields.Boolean(string="Check")
    item = fields.Char(string='Item')
    item_int = fields.Integer(string="Item Number")
    manufacture_id = fields.Many2one('od.product.brand',string='Manufacturer',required=True)
    part_no = fields.Many2one('product.product',string='Part No',required=True)
    product_group_id = fields.Many2one('od.product.group',string="Product Group",related="part_no.od_pdt_group_id",readonly=True)
    name = fields.Text(string='_________Description_______',required="1")
    types = fields.Many2one('od.product.type',string='Type',required=True)
    uom_id = fields.Many2one('product.uom',string='UOM',required=True)
    qty = fields.Integer(string='Qty',default=1)
    unit_price = fields.Float(string="Unit Sale",compute="_compute_unit_price",digits=dp.get_precision('Account'))
    temp_unit_price = fields.Float(string="Temp Unit Price",digits=dp.get_precision('Account'))
    new_unit_price = fields.Float(string="Fixed Unit Sale",digits=dp.get_precision('Account'))
    fixed = fields.Boolean(string="Price Fix")
    locked = fields.Boolean(string="Locked",compute='_get_locked_status')
    
    line_price = fields.Float(string='Total Sale', compute='_compute_line_price',digits=dp.get_precision('Account'))
    group = fields.Many2one('od.cost.costgroup.material.line',string='Group',copy=True)
    section_id = fields.Many2one('od.cost.section.line',string='Section',copy=True)
    sales_currency_id = fields.Many2one('res.currency',string='Sales Currency',compute='_compute_currency_supp_discount')
    unit_cost_local = fields.Float(string='Unit Cost Local', compute='_compute_supplier_discount',digits=dp.get_precision('Account'))
    unit_cost_amend = fields.Float(string="Unit Cost Amended",copy=False)
    is_unit_cost_amend = fields.Boolean(string="Unit Cost Amended",copy=False)
    line_cost_local_currency = fields.Float(string='Line Cost Local Currency',compute="_compute_unit_price",digits=dp.get_precision('Account'))
    profit = fields.Float(string='Profit', compute='_compute_profit',digits=dp.get_precision('Account'))
    profit_percentage = fields.Float(string='Profit(%)', compute='_compute_profit_percentage',digits=dp.get_precision('Account'))
    supplier_currency_id = fields.Many2one('res.currency',string='Supplier Currency',compute="_compute_currency_supp_discount")
    min_order = fields.Integer(string='Min Order',default=1)
    unit_cost_supplier_currency = fields.Float(string='List Price',digits=dp.get_precision('Account'))
    supplier_discount = fields.Float(string='Supplier Discount',compute='_compute_currency_supp_discount',digits=dp.get_precision('Account'))
    discounted_unit_supplier_currency = fields.Float(string='Discounted Unit Supplier Currency',compute='_compute_supplier_discount',digits=dp.get_precision('Account'))
    discounted_total_supplier_currency = fields.Float(string='Discounted Total Supplier Currency',compute='_discounted_total_unit',digits=dp.get_precision('Account'))
    show_main_pro_line = fields.Boolean(string='Show to Customer',default=False)
    ren = fields.Boolean(string='REN')
    tax_id = fields.Many2one('account.tax',string="Tax",default=get_vat)
    vat = fields.Float(string="VAT %",compute='_compute_vat',digits=dp.get_precision('Account'))
    vat_value = fields.Float(string="VAT Value",compute='_compute_vat',digits=dp.get_precision('Account'))


    @api.onchange('part_no')
    def onchange_product_id(self):
        if self.cost_sheet_id and self.cost_sheet_id.price_fixed:
            self.fixed = True
        if self.part_no.id:
            part_no = self.part_no.id
            prod = self.env['product.product'].browse(part_no)
            self.name = prod.description
            if not prod.description:
                self.name = prod.name
            self.types = prod.od_pdt_type_id.id
            self.uom_id = prod.uom_id.id
    
    #Added by Aslam on 25/Feb/2022 to load vat when cost group is linked        
    @api.one
    @api.onchange('group')
    def onchange_product_group(self):
        if self.group:
            self.tax_id = self.group and self.group.tax_id and self.group.tax_id.id or False

class od_cost_mat_optional_item_line(models.Model):

    _name = 'od.cost.mat.optional.item.line'
    _order = "item_int ASC"




    


    @api.one
    @api.depends('qty','unit_cost_local','group_id')
    def _compute_unit_price(self):
        self.line_cost_local_currency = self.qty * self.unit_cost_local
        # prev_unit_price = self.temp_unit_price
        if self.group_id:
            group_obj = self.group_id
            profit = group_obj.profit/100
            if profit >=1:
                raise Warning("Profit value for the costgroup %s set 100 or above,it should be below 100"%group_obj.name)
            round_up_val = group_obj.round_up or 3
            round_up_val -=1
            customer_discount = group_obj.customer_discount/100
            unit_cost_local = self.unit_cost_local
#             unit_price = (unit_cost_local / (1-profit)) - (unit_cost_local * customer_discount)
            unit_price = (unit_cost_local / (1-profit)) 
            unit_price = unit_price * (1-customer_discount)
            if round_up_val < 3:
                unit_price = round(unit_price,round_up_val)
            # freeze = self.cost_sheet_id and self.cost_sheet_id.freeze
            self.unit_price = unit_price
            # if not freeze:
            #     self.unit_price = unit_price
            #     self.temp_unit_price = unit_price
            # else:
            #     self.unit_price = prev_unit_price

    @api.one
    @api.depends('unit_cost_supplier_currency','supplier_discount')
    def _compute_supplier_discount(self):
        
        
        if self.is_unit_cost_amend:
                self.unit_cost_local = self.unit_cost_amend
        
        if self.unit_cost_supplier_currency and not self.is_unit_cost_amend:
            
            unit_cost_supplier_currency = self.unit_cost_supplier_currency
            supplier_discount = self.supplier_discount/100
            discount_value = unit_cost_supplier_currency * supplier_discount
            discounted_unit_price = unit_cost_supplier_currency - discount_value
            group_obj = self.group_id
            ex_rate = group_obj.currency_exchange_factor
            min_qty =self.min_order
            sale_qty = self.qty
            if min_qty <= sale_qty:
                base_factor = discounted_unit_price * ex_rate
            else:
                if sale_qty:
                    base_factor = ((discounted_unit_price*min_qty)/sale_qty)* ex_rate
                else:
                    base_factor = 0
            currency_fluct = group_obj.currency_fluctation_provision/100
            shipping = group_obj.shipping/100
            customs = group_obj.customs/100
            stock_provision = group_obj.stock_provision/100
            conting_provision = group_obj.conting_provision/100
            unit_cost_local = base_factor + base_factor * currency_fluct + base_factor * shipping + base_factor * customs + base_factor * stock_provision + base_factor * conting_provision
            round_up_val = group_obj.round_up or 3
            round_up_val -=1
#             if round_up_val < 3:
#                 unit_cost_local = round(unit_cost_local,round_up_val)

            self.unit_cost_local = unit_cost_local
            self.discounted_unit_supplier_currency = discounted_unit_price


    @api.one
    @api.depends('discounted_unit_supplier_currency','qty','min_order')
    def _discounted_total_unit(self):
        qty = self.qty
        min_order = self.min_order
        if qty > min_order:
            self.discounted_total_supplier_currency = self.discounted_unit_supplier_currency * qty
        else:
            self.discounted_total_supplier_currency = self.discounted_unit_supplier_currency * min_order
    @api.one
    @api.depends('group_id')
    def _compute_currency_supp_discount(self):
        if self.group_id:
            group_obj = self.group_id
            self.supplier_currency_id = group_obj.supplier_currency_id and group_obj.supplier_currency_id.id
            sales_currency_id = group_obj.sales_currency_id and group_obj.sales_currency_id.id
            supplier_discount = group_obj.supplier_discount
            self.sales_currency_id = sales_currency_id
            self.supplier_discount = supplier_discount
            self.vat = group_obj.vat

    @api.one
    @api.depends('qty','unit_price')
    def _compute_line_price(self):
        fixed = self.fixed
        locked = self.locked
        if not (fixed or locked):
            self.line_price = self.qty * self.unit_price
        else:
            self.line_price = self.qty * self.new_unit_price

    @api.one
    @api.depends('line_price','line_cost_local_currency')
    def _compute_profit(self):
        self.profit = round(self.line_price )- round(self.line_cost_local_currency)
    @api.one
    @api.depends('line_price','profit')
    def _compute_profit_percentage(self):
        if self.line_price and self.profit:
            self.profit_percentage = (self.profit/(self.line_price or 1))*100

#     @api.one
#     @api.depends('supplier_currency_id')
#     def compute_supp_currency(self):
#         if self.supplier_currency_id:
#             from_currency = self.env.user.company_id.currency_id
#             converted_amount = from_currency.compute(self.unit_cost_supplier_currency, self.supplier_currency_id)
#             self.unit_cost_supplier_currency = converted_amount


    @api.one 
    @api.depends('tax_id','line_price','qty')
    def _compute_vat(self):
        if self.tax_id:
            vat = self.tax_id.amount 
            self.vat = vat  * 100
            vat_value = self.line_price * vat
            self.vat_value = vat_value
    
    def get_vat(self):
        return self.env.user.company_id.od_tax_id
    
    def get_fix(self):
        return self.cost_sheet_id.price_fixed 
    
    @api.one
    def _get_locked_status(self):
        
        if self.cost_sheet_id and self.cost_sheet_id.price_fixed and self.cost_sheet_id.state not in ('draft','design_ready','committed','submitted','returned_by_pmo','waiting_po_open'):
            self.locked = True

    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade')
    item = fields.Char(string='Item')
    item_int = fields.Integer(string="Item Number")
    check = fields.Boolean(string="Check")
    manufacture_id = fields.Many2one('od.product.brand',string='Manufacturer',required=True)
    part_no = fields.Many2one('product.product',string='Part No',required=True)
    name = fields.Char(string='_________Description_______',required="1")
    types = fields.Many2one('od.product.type',string='Type',required=True)
    uom_id = fields.Many2one('product.uom',string='UOM',required=True)
    qty = fields.Integer(string='Qty',default=1)
    unit_price = fields.Float(string="Unit Sale",compute="_compute_unit_price",digits=dp.get_precision('Account'))
    temp_unit_price = fields.Float(string="Temp Unit Price",digits=dp.get_precision('Account'))
    new_unit_price = fields.Float(string="Fixed Unit Sale",digits=dp.get_precision('Account'))
    fixed = fields.Boolean(string="Price Fix",)
    locked = fields.Boolean(string="Locked",compute='_get_locked_status')
    
    line_price = fields.Float(string='Total Sale',readonly=True, compute='_compute_line_price',digits=dp.get_precision('Account'))
    group_id = fields.Many2one('od.cost.costgroup.optional.line.two',string='Group',copy=True)
    opt_section_id = fields.Many2one('od.cost.opt.section.line',string='Section',copy=True)
    sales_currency_id = fields.Many2one('res.currency',string='Sales Currency',readonly=True, compute='_compute_currency_supp_discount')
    unit_cost_local = fields.Float(string='Unit Cost Local',readonly=True, compute='_compute_supplier_discount',digits=dp.get_precision('Account'))
    unit_cost_amend = fields.Float(string="Unit Cost Amended",copy=False)
    is_unit_cost_amend = fields.Boolean(string="Unit Cost Amended",copy=False)
    line_cost_local_currency = fields.Float(string='Line Cost Local Currency',compute="_compute_unit_price",digits=dp.get_precision('Account'))
    profit = fields.Float(string='Profit',readonly=True, compute='_compute_profit',digits=dp.get_precision('Account'))
    profit_percentage = fields.Float(string='Profit(%)',readonly=True, compute='_compute_profit_percentage',digits=dp.get_precision('Account'))
    supplier_currency_id = fields.Many2one('res.currency',string='Supplier Currency',readonly=True,compute="_compute_currency_supp_discount")
    min_order = fields.Integer(string='Min Order',default=1)
    unit_cost_supplier_currency = fields.Float(string='List Price',digits=dp.get_precision('Account'))
    supplier_discount = fields.Float(string='Supplier Discount',readonly=True, compute='_compute_currency_supp_discount',digits=dp.get_precision('Account'))
    discounted_unit_supplier_currency = fields.Float(string='Discounted Unit Supplier Currency', readonly=True, compute='_compute_supplier_discount',digits=dp.get_precision('Account'))
    discounted_total_supplier_currency = fields.Float(string='Discounted Total Supplier Currency', readonly=True, compute='_discounted_total_unit',digits=dp.get_precision('Account'))
    show_main_pro_line = fields.Boolean(string='Show to Customer',default=False)
    ren = fields.Boolean(string='REN')
    tax_id = fields.Many2one('account.tax',string="Tax" ,default=get_vat)
    vat = fields.Float(string="VAT %",compute="_compute_vat",digits=dp.get_precision('Account'))
    vat_value = fields.Float(string="VAT Value",compute='_compute_vat',digits=dp.get_precision('Account'))
    
#     @api.one 
#     @api.onchange('vat','line_price')
#     def onchange_vat(self):
#         vat = self.vat
#         line_price = self.line_price
#         vat_value = line_price * (vat/100.0)
#         self.vat_value = vat_value


  

#     @api.onchange('unit_cost_supplier_currency','supplier_discount')
#     def onchange_supplier_discount(self):
#         if self.unit_cost_supplier_currency:
#             unit_cost_supplier_currency =self.unit_cost_supplier_currency
#             supplier_discount = self.supplier_discount/100
#             discount_value = unit_cost_supplier_currency * supplier_discount
#             discounted_unit_price = unit_cost_supplier_currency - discount_value
#             group_obj = self.group_id
#             ex_rate = group_obj.currency_exchange_factor
#
#             min_qty =self.min_order
#             sale_qty = self.qty
#             if min_qty <= sale_qty:
#                 base_factor = discounted_unit_price * ex_rate
#             else:
#                 base_factor = ((discounted_unit_price*min_qty)/sale_qty)* ex_rate
#             currency_fluct = group_obj.currency_fluctation_provision/100
#             shipping = group_obj.shipping/100
#             customs = group_obj.customs/100
#             stock_provision = group_obj.stock_provision/100
#             conting_provision = group_obj.conting_provision/100
#             unit_cost_local = base_factor + base_factor * currency_fluct + base_factor * shipping + base_factor * customs + base_factor * stock_provision + base_factor * conting_provision
#             self.unit_cost_local = unit_cost_local
#             self.discounted_unit_supplier_currency = discounted_unit_price


#     @api.onchange('min_order','discounted_unit_supplier_currency','qty')
#     def onchange_discounted_single_unit(self):
#         qty = self.qty
#         min_order = self.min_order
#         print "qtyuyyyy",qty,min_order
#         if qty > min_order:
#             self.discounted_total_supplier_currency = self.discounted_unit_supplier_currency * qty
#         else:
#             self.discounted_total_supplier_currency = self.discounted_unit_supplier_currency * min_order
#     @api.onchange('min_order','qty','discounted_unit_supplier_currency')
#     def onchange_min_order(self):
#         if self.min_order:
#             if self.min_order > self.qty:
#                 self.discounted_total_supplier_currency = self.discounted_unit_supplier_currency * self.min_order
#
#
#
#     @api.onchange('group_id')
#     def onchange_cost_group(self):
#         if self.group_id:
#             group_obj = self.group_id
#             self.supplier_currency_id = group_obj.supplier_currency_id and group_obj.supplier_currency_id.id
#             sales_currency_id = group_obj.sales_currency_id and group_obj.sales_currency_id.id
#             supplier_discount = group_obj.supplier_discount
#             self.sales_currency_id = sales_currency_id
#             self.supplier_discount = supplier_discount
#     @api.onchange('supplier_currency_id')
#     def onchange_supp_currency(self):
#         if self.supplier_currency_id:
#             from_currency = self.env.user.company_id.currency_id
#             converted_amount = from_currency.compute(self.unit_cost_supplier_currency, self.supplier_currency_id)
#             self.unit_cost_supplier_currency = converted_amount

    @api.onchange('part_no')
    def onchange_product_id(self):
        if self.cost_sheet_id and self.cost_sheet_id.price_fixed:
            self.fixed = True
        if self.part_no.id:
            part_no = self.part_no.id
            prod = self.env['product.product'].browse(part_no)
            self.name = prod.description
            if not prod.description:
                self.name = prod.name
            self.types = prod.od_pdt_type_id.id
            self.uom_id = prod.uom_id.id
#             price = prod.list_price
#             self.unit_cost_supplier_currency = price
#     @api.onchange('qty','unit_price')
#     def onchange_qty(self):
#         self.line_price = self.qty * self.unit_price
#
#     @api.onchange('line_price','line_cost_local_currency')
#     def onchange_prices_to_profit(self):
#         self.profit = self.line_price - self.line_cost_local_currency
#         print "profit>>>>>>>>>>>>>>.oonchange>>>>>>>>>>>>>>>>>>>>>>",self.line_price,self.line_cost_local_currency
#     @api.onchange('line_price','profit')
#     def onchange_profit_per(self):
#         if self.line_price:
#             self.profit_percentage = (self.profit/self.line_price)*100

    #Added by Aslam on 25/Feb/2022 to load vat when cost group is linked
    @api.one
    @api.onchange('group_id')
    def onchange_product_group(self):
        if self.group_id:
            self.tax_id = self.group_id and self.group_id.tax_id and self.group_id.tax_id.id or False


class od_cost_mat_brand_weight(models.Model):
    _name = 'od.cost.mat.brand.weight'

    _order = "item_int ASC"
    item_int = fields.Integer(string="Item Seq",default=1)


    @api.one
    @api.depends('total_sale_after_disc','total_cost')
    def _compute_vals(self):
        total_sale = round(self.total_sale_after_disc)
        total_cost = round(self.total_cost)
        profit = total_sale- total_cost
        self.profit = profit
        all_brand_cost = self.all_brand_cost
        if total_sale:
            self.profit_percent =  (profit /(total_sale or 1.0)) * 100
        if all_brand_cost:
            self.weight = (total_cost /(all_brand_cost or 1.0)) * 100


    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    manufacture_id = fields.Many2one('od.product.brand',string='Brand')
    total_sale = fields.Float(string="Total Brand Sales",digits=dp.get_precision('Account'))
    total_sale_after_disc = fields.Float(string="Total Brand Sales After Discount",digits=dp.get_precision('Account'))
    total_cost = fields.Float(string="Total Brand cost",digits=dp.get_precision('Account'))
    sup_cost = fields.Float(string="Supplier Discounted Price",digits=dp.get_precision('Account'))
    all_brand_cost = fields.Float(string="All Brand Cost",digits=dp.get_precision('Account'))
    profit = fields.Float(string="Profit",compute="_compute_vals",digits=dp.get_precision('Account'))
    profit_percent = fields.Float(string="Profit %",compute="_compute_vals",digits=dp.get_precision('Account'))
    weight  = fields.Float(string="Weight",compute="_compute_vals",digits=dp.get_precision('Account'))
    

class od_cost_mat_group_weight(models.Model):
    _name = 'od.cost.mat.group.weight'

    _order = "item_int ASC"
    item_int = fields.Integer(string="Item Seq",default=1)


    @api.one
    @api.depends('total_sale','total_cost')
    def _compute_vals(self):
        total_sale = round(self.sale_aftr_disc)
        total_cost = round(self.total_cost)
        profit = total_sale- total_cost
        self.profit = profit
        all_group_cost = self.all_group_cost
        if total_sale:
            self.profit_percent =  (profit /(total_sale or 1.0)) * 100
        if all_group_cost:
            self.weight = (total_cost /(all_group_cost or 1.0)) * 100


    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    pdt_grp_id = fields.Many2one('od.product.group',string='Product Group')
    total_sale = fields.Float(string="Sales Before Disc",digits=dp.get_precision('Account'))
    disc = fields.Float(string="Disc %",digits=dp.get_precision('Account'))
    sale_aftr_disc = fields.Float(string="Sales After Disc",digits=dp.get_precision('Account'))
    total_cost = fields.Float(string="Total Group cost",digits=dp.get_precision('Account'))
    all_group_cost = fields.Float(string="All Group Cost",digits=dp.get_precision('Account'))
    profit = fields.Float(string="Profit",compute="_compute_vals",digits=dp.get_precision('Account'))
    profit_percent = fields.Float(string="Profit %",compute="_compute_vals",digits=dp.get_precision('Account'))
    weight  = fields.Float(string="Weight",compute="_compute_vals",digits=dp.get_precision('Account'))




class od_mp_tech_summary_line(models.Model):
    _name = 'od.mp.tech.summary.line'
    @api.one
    @api.depends('total_sale','total_cost')
    def _compute_vals(self):
        total_sale = round(self.total_sale)
        total_cost = round(self.total_cost)
        profit = total_sale- total_cost
        self.profit = profit
        if total_sale:
            self.profit_percent =  (profit /(total_sale or 1.0)) * 100
        

    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    pdt_grp_id = fields.Many2one('od.product.group',string='Product Group')
    total_sale = fields.Float(string="Sales Value",digits=dp.get_precision('Account'))
    total_cost = fields.Float(string="Cost Value",digits=dp.get_precision('Account'))
    vat = fields.Float(string="VAT",digits=dp.get_precision('Account'))
    profit = fields.Float(string="Profit",compute="_compute_vals",digits=dp.get_precision('Account'))
    profit_percent = fields.Float(string="Profit %",compute="_compute_vals",digits=dp.get_precision('Account'))
    




class od_cost_imp_weight(models.Model):
    _name = 'od.cost.impl.group.weight'
    _order = "item_int ASC"
    item_int = fields.Integer(string="Item Seq",default=1)
    tab = fields.Selection([('bim','BIM'),('oim','OIM')],string="PS")
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    pdt_grp_id = fields.Many2one('od.product.group',string='Product Group')
    total_sale = fields.Float(string="Sales",digits=dp.get_precision('Account'))
    disc = fields.Float(string="Disc %",digits=dp.get_precision('Account'))
    sale_aftr_disc = fields.Float(string="Sales After Disc",digits=dp.get_precision('Account'))
    total_cost = fields.Float(string="Cost",digits=dp.get_precision('Account'))
    profit = fields.Float(string="Profit",digits=dp.get_precision('Account'))
    
class od_cost_bis_weight(models.Model):
    _name = 'od.cost.bis.group.weight'
    _order = "item_int ASC"
    item_int = fields.Integer(string="Item Seq",default=1)
    tab = fields.Selection([('bis','BIS'),('ois','OIS')],string="IS")
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    pdt_grp_id = fields.Many2one('od.product.group',string='Product Group')
    total_sale = fields.Float(string="Sales",digits=dp.get_precision('Account'))
    disc = fields.Float(string="Disc %",digits=dp.get_precision('Account'))
    sale_aftr_disc = fields.Float(string="Sales After Disc",digits=dp.get_precision('Account'))
    total_cost = fields.Float(string="Cost",digits=dp.get_precision('Account'))
    profit = fields.Float(string="Profit",digits=dp.get_precision('Account'))


class od_cost_amc_weight(models.Model):
    _name = 'od.cost.amc.group.weight'
    _order = "item_int ASC"
    item_int = fields.Integer(string="Item Seq",default=1)
    tab = fields.Selection([('bmn','BMN'),('omn','OMN')],string="MC")
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    pdt_grp_id = fields.Many2one('od.product.group',string='Product Group')
    total_sale = fields.Float(string="Sales",digits=dp.get_precision('Account'))
    disc = fields.Float(string="Disc %",digits=dp.get_precision('Account'))
    sale_aftr_disc = fields.Float(string="Sales After Disc",digits=dp.get_precision('Account'))
    total_cost = fields.Float(string="Cost",digits=dp.get_precision('Account'))
    profit = fields.Float(string="Profit",digits=dp.get_precision('Account'))
    

class od_cost_om_weight(models.Model):
    _name = 'od.cost.om.group.weight'
    _order = "item_int ASC"
    item_int = fields.Integer(string="Item Seq",default=1)
    tab = fields.Selection([('om','O&M')],string="O&M")
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    pdt_grp_id = fields.Many2one('od.product.group',string='Product Group')
    total_sale = fields.Float(string="Sales",digits=dp.get_precision('Account'))
    disc = fields.Float(string="Disc %",digits=dp.get_precision('Account'))
    sale_aftr_disc = fields.Float(string="Sales After Disc",digits=dp.get_precision('Account'))
    total_cost = fields.Float(string="Cost",digits=dp.get_precision('Account'))
    profit = fields.Float(string="Profit",digits=dp.get_precision('Account'))

class od_cost_extra_expense_weight(models.Model):
    _name = 'od.cost.extra.group.weight'
    _order = "item_int ASC"
    item_int = fields.Integer(string="Item Seq",default=1)
    tab = fields.Selection([('mat','MAT'),('trn','TRN')],string="Extra Expense")
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    pdt_grp_id = fields.Many2one('od.product.group',string='Product Group')
    total_sale = fields.Float(string="Sales",digits=dp.get_precision('Account'))
    disc = fields.Float(string="Disc %",digits=dp.get_precision('Account'))
    sale_aftr_disc = fields.Float(string="Sales After Disc",digits=dp.get_precision('Account'))
    total_cost = fields.Float(string="Cost",digits=dp.get_precision('Account'))
    profit = fields.Float(string="Profit",digits=dp.get_precision('Account'))


class od_cost_summary_weight(models.Model):
    _name = 'od.cost.summary.group.weight'
    _order = "item_int ASC"
    item_int = fields.Integer(string="Item Seq",default=1)
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    pdt_grp_id = fields.Many2one('od.product.group',string='Product Group')
    total_sale = fields.Float(string="Sales",digits=dp.get_precision('Account'))
    disc = fields.Float(string="Disc %",digits=dp.get_precision('Account'))
    sale_aftr_disc = fields.Float(string="Sales After Disc",digits=dp.get_precision('Account'))
    total_cost = fields.Float(string="Cost",digits=dp.get_precision('Account'))
    profit = fields.Float(string="Profit",digits=dp.get_precision('Account'))
    manpower_cost = fields.Float(string="Manpower Cost",digits=dp.get_precision('Account'))
    manpower_sale = fields.Float(string="Manpower Sale",digits=dp.get_precision('Account'))
    total_gp = fields.Float(string="Total GP",digits=dp.get_precision('Account'))
    
    
    @api.one
    @api.depends('total_sale','total_cost')
    def _compute_vals(self):
        total_sale = round(self.sale_aftr_disc)
        total_cost = round(self.total_cost)
        profit = total_sale- total_cost
        if total_sale:
            self.profit_percent =  (profit /total_sale) * 100
       
    profit_percent = fields.Float(string="Profit %",compute="_compute_vals",digits=dp.get_precision('Account'))






class od_cost_original_summary_weight(models.Model):
    _name = 'od.cost.original.summary.group.weight'
    _order = "item_int ASC"
    item_int = fields.Integer(string="Item Seq",default=1)
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    pdt_grp_id = fields.Many2one('od.product.group',string='Product Group')
    total_sale = fields.Float(string="Sales",digits=dp.get_precision('Account'))
    disc = fields.Float(string="Disc %",digits=dp.get_precision('Account'))
    sale_aftr_disc = fields.Float(string="Sales After Disc",digits=dp.get_precision('Account'))
    total_cost = fields.Float(string="Cost",digits=dp.get_precision('Account'))
    profit = fields.Float(string="Profit",digits=dp.get_precision('Account'))
    manpower_cost = fields.Float(string="Manpower Cost",digits=dp.get_precision('Account'))
    manpower_sale = fields.Float(string="Manpower Sale",digits=dp.get_precision('Account'))
    total_gp = fields.Float(string="Total GP",digits=dp.get_precision('Account'))
    profit_percent = fields.Float(string="Profit %",digits=dp.get_precision('Account'))


class od_cost_mat_extra_expense_line(models.Model):
    _name = 'od.cost.mat.extra.expense.line'
    _order = "item_int ASC"
    @api.one
    @api.depends('qty','unit_cost','unit_price','new_unit_price','group')
    def compute_calculation(self):
        if self.group:
            profit = self.group.profit /100
            self.tax_id = self.group and self.group.tax_id and self.group.tax_id.id or False
            if profit >=1:
                raise Warning("Profit value for the costgroup %s set 100 or above,it should be below 100"%self.group.name)
            discount = self.group.customer_discount/100
            unit_cost = self.unit_cost
#             unit_price = (unit_cost / (1-profit)) - (unit_cost * discount)
            unit_price = (unit_cost / (1-profit))
            unit_price = unit_price * (1-discount)
            self.unit_price = round(unit_price)

        if self.qty or self.unit_cost:
            self.line_cost = self.qty * self.unit_cost
        fixed = self.fixed
        locked = self.locked
        
        if not (fixed or locked):
            self.line_price = self.qty * self.unit_price
        else:
            self.line_price = self.qty * self.new_unit_price 

    @api.one
    @api.depends('qty','list_price','unit_price2','new_unit_price','group2')
    def compute_calculation2(self):
        
        if self.is_unit_cost_amend:
                self.unit_cost_local = self.unit_cost_amend
        
        if self.group2 and not self.is_unit_cost_amend:
            
            self.tax_id = self.group2 and self.group2.tax_id and self.group2.tax_id.id or False
            profit = self.group2.profit /100
            if profit >=1:
                raise Warning("Profit value for the costgroup %s set 100 or above,it should be below 100"%self.group.name)
            discount = self.group2.customer_discount/100
            list_price = self.list_price
            supplier_discount = (self.group2.supplier_discount)/100
            discount_value = list_price * supplier_discount
            discounted_unit_cost = list_price - discount_value
            ex_rate = self.group2.currency_exchange_factor
            base_factor = discounted_unit_cost * ex_rate
            currency_fluct = self.group2.currency_fluctation_provision/100
            shipping = self.group2.shipping/100
            customs = self.group2.customs/100
            stock_provision = self.group2.stock_provision/100
            conting_provision = self.group2.conting_provision/100
            unit_cost_local = base_factor + base_factor * currency_fluct + base_factor * shipping + base_factor * customs + base_factor * stock_provision + base_factor * conting_provision
            round_up_val = self.group2.round_up or 3
            round_up_val -=1
#             if round_up_val <3:
#                 unit_cost_local = round(unit_cost_local,round_up_val)
            self.unit_cost_local = unit_cost_local
#             unit_price = (unit_cost_local / (1-profit)) - (unit_cost_local * discount)
            unit_price = (unit_cost_local / (1-profit))
            unit_price = unit_price * (1-discount)
            self.unit_price2 = round(unit_price)
#             self.vat = self.group2.vat
        fixed = self.fixed
        locked = self.locked
        if (fixed or locked):
            self.line_price2 = self.qty * self.new_unit_price 
        else:
            self.line_price2 = self.qty * self.unit_price2
        if self.qty and self.unit_cost_local:
            self.line_cost_local = self.qty * self.unit_cost_local
    
    @api.one 
    @api.depends('tax_id','line_price','qty','line_price2')
    def _compute_vat(self):
        if self.tax_id:
            vat = self.tax_id.amount 
            self.vat = vat  * 100
            vat_value1 = self.line_price * vat
            self.vat_value = vat_value1
            
            vat_value2 = self.line_price2 * vat
            self.vat_value2 = vat_value2
            
    
    @api.one
    def _get_locked_status(self):
        
        if self.cost_sheet_id and self.cost_sheet_id.price_fixed and self.cost_sheet_id.state not in ('draft','design_ready','committed','submitted','returned_by_pmo','waiting_po_open'):
            self.locked = True
    
    
        
    def get_vat(self):
        return self.env.user.company_id.od_tax_id
    
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    item = fields.Char(string='Item')
    item_int = fields.Integer(string="Item Number")
    check = fields.Boolean(string="Check")
    od_product_id = fields.Many2one('product.product',string='Expense',domain=[('type','=','consu')])
    name = fields.Char(string='Description')
    qty = fields.Float(string='Qty',default=1)
    unit_cost = fields.Float(string='Unit Cost',digits=dp.get_precision('Account'))
    line_cost = fields.Float(string='Line Cost',compute='compute_calculation',digits=dp.get_precision('Account'))
    group = fields.Many2one('od.cost.costgroup.it.service.line',string='Group',copy=True)
    group2 = fields.Many2one('od.cost.costgroup.extra.expense.line',string='Group',copy=True)
    unit_price = fields.Float(string='Unit Price',compute='compute_calculation',digits=dp.get_precision('Account'))
    
    temp_unit_price = fields.Float(string="Temp Unit Price",digits=dp.get_precision('Account'))
    new_unit_price = fields.Float(string="Fixed Unit Sale",digits=dp.get_precision('Account'))
    fixed = fields.Boolean(string="Price Fix")
    locked = fields.Boolean(string="Locked",compute='_get_locked_status')
    
    line_price = fields.Float(string='Line Price',compute='compute_calculation',digits=dp.get_precision('Account'))
    unit_cost_local = fields.Float(string="Unit Cost Local",compute='compute_calculation2',digits=dp.get_precision('Account'))
    unit_cost_amend = fields.Float(string="Unit Cost Amended",copy=False)
    is_unit_cost_amend = fields.Boolean(string="Unit Cost Amended",copy=False)
    
    line_cost_local = fields.Float(string="Line Cost Local",compute='compute_calculation2',digits=dp.get_precision('Account'))
    list_price = fields.Float(string="List Price",digits=dp.get_precision('Account'))
    unit_price2 = fields.Float(string='Unit Price',compute='compute_calculation2',digits=dp.get_precision('Account'))
    line_price2 = fields.Float(string='Line Price',compute='compute_calculation2',digits=dp.get_precision('Account'))
    show_to_customer = fields.Boolean(string='Show to Customer')
    tax_id = fields.Many2one('account.tax',string="Tax",default=get_vat)
    vat = fields.Float(string="VAT %",digits=dp.get_precision('Account'))
    vat_value = fields.Float(string="VAT Value",compute="_compute_vat",digits=dp.get_precision('Account'))
    vat_value2 = fields.Float(string="VAT Value",compute="_compute_vat",digits=dp.get_precision('Account'))
#     @api.one 
#     @api.onchange('vat','line_price2')
#     def onchange_vat(self):
#         vat = self.vat
#         line_price = self.line_price2
#         vat_value = line_price * (vat/100.0)
#         self.vat_value = vat_value
    
    @api.onchange('item')
    def onchange_item(self):
        if self.cost_sheet_id and self.cost_sheet_id.price_fixed:
            self.fixed = True
    
    @api.onchange('od_product_id')
    def onchange_product(self):
        if self.od_product_id:
            self.name = self.od_product_id.description



#     @api.onchange('qty','unit_cost','unit_price')
#     def onchange_qty(self):
#         if self.qty or self.unit_cost:
#             self.line_cost = self.qty * self.unit_cost
#         if self.qty and self.unit_price:
#             self.line_price = self.qty * self.unit_price
#
#     @api.onchange('group','unit_cost')
#     def onchange_group(self):
#         if self.group:
#             profit = self.group.profit /100
#             discount = self.group.customer_discount/100
#             unit_cost = self.unit_cost
#             unit_price = unit_cost + (unit_cost*profit - unit_cost*discount)
#             self.unit_price = unit_price

class od_cost_ren_main_pro_line(models.Model):

    _name = 'od.cost.ren.main.pro.line'
    _order = "item_int ASC"
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    item = fields.Char(string='Item')
    item_int = fields.Integer(string='Item Number')
    check = fields.Boolean(string="Check")
    manufacture_id = fields.Many2one('od.product.brand',string='Manufacture',required="1")
    renewal_package_no = fields.Many2one('product.product',string='Renewal Package No')
    product_p_n = fields.Many2one('product.product',string='Applicable To')
    serial_no = fields.Text(string='Serial No')
    city_id = fields.Many2one("res.country.state", 'City')
    notes = fields.Char('__________________Notes_______________')
    location = fields.Char(string='Location')
    start_date = fields.Date(string='Start Date')
    expiry_date = fields.Date(string='Expiry Date')
    show_main_line = fields.Boolean(string='Show to Customer',default=False)

class od_cost_ren_optional_item_line(models.Model):

    _name = 'od.cost.ren.optional.item.line'
    _inherit ='od.cost.ren.main.pro.line'
    show_optional_line = fields.Boolean(string='Show to Customer',default=False)

class od_bmn_eqp_cov_line(models.Model):
    _name = 'od.bmn.eqp.cov.line'
    _inherit ='od.cost.ren.main.pro.line'
class od_omn_eqp_cov_line(models.Model):
    _name = 'od.omn.eqp.cov.line'
    _inherit ='od.cost.ren.main.pro.line'
class od_o_m_eqp_cov_line(models.Model):
    _name = 'od.o_m.eqp.cov.line'
    _inherit ='od.cost.ren.main.pro.line'

class od_cost_trn_customer_training_line(models.Model):
    _name = 'od.cost.trn.customer.training.line'
    _inherit = 'od.cost.mat.main.pro.line'
    trn_section_id = fields.Many2one('od.cost.trn.section.line',string='Section',copy=True)
    
    
class od_cost_amc_technology(models.Model):
    _name = 'od.cost.amc.tech.line'
    _inherit = 'od.cost.mat.main.pro.line'
    manufacture_id = fields.Many2one('od.product.brand',string='Manufacture',required="1" ,default=1)
    group = fields.Many2one('od.cost.costgroup.it.service.line',string='Group',copy=True)



class od_cost_imp_technology(models.Model):
    _name = 'od.cost.imp.tech.line'
    _inherit = 'od.cost.mat.main.pro.line'
    manufacture_id = fields.Many2one('od.product.brand',string='Manufacture',required="1" ,default=1)
    group = fields.Many2one('od.cost.costgroup.it.service.line',string='Group',copy=True)

class od_ps_vendor_line(models.Model):
    _name = 'od.cost.ps.vendor.line'
    _inherit = 'od.cost.mat.main.pro.line'
    manufacture_id = fields.Many2one('od.product.brand',string='Manufacture',required="1" ,default=1)
    group = fields.Many2one('od.cost.costgroup.it.service.line',string='Group',copy=True)

class od_cost_om_technology(models.Model):
    _name = 'od.cost.om.tech.line'
    _inherit = 'od.cost.mat.main.pro.line'
    manufacture_id = fields.Many2one('od.product.brand',string='Manufacture',required="1" ,default=1)
    group = fields.Many2one('od.cost.costgroup.it.service.line',string='Group',copy=True)


class od_cost_trn_customer_training_extra_expense_line(models.Model):
    _name = 'od.cost.trn.customer.training.extra.expense.line'
    _inherit = 'od.cost.mat.extra.expense.line'



class od_cost_bim_beta_implimentation_extra_expense_line(models.Model):
    _name = 'od.cost.bim.beta.implimentation.extra.expense.line'
    _inherit = 'od.cost.mat.extra.expense.line'
    
    
#     @api.one 
#     @api.onchange('vat','line_price')
#     def onchange_vat(self):
#         vat = self.vat
#         line_price = self.line_price
#         vat_value = line_price * (vat/100.0)
#         self.vat_value = vat_value
    
    
    @api.one 
    @api.onchange('group')
    def onchange_group(self):
        group = self.group
        self.tax_id = group.tax_id and group.tax_id.id



#     cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
#     item = fields.Char(string='Item')
#     od_product_id = fields.Many2one('product.product',string='Product')
#     name = fields.Char(string='Description')
#     qty = fields.Float(string='Qty')
#     unit_cost = fields.Float(string='Unit Cost')
#     line_cost = fields.Float(string='Line Cost')
#     bim_show_to_customer = fields.Boolean(string='Show to Customer',default=False)
#
#     @api.onchange('od_product_id')
#     def onchange_product(self):
#         if self.od_product_id:
#             self.name = self.od_product_id.description
#
#     @api.onchange('qty','unit_cost')
#     def onchange_qty(self):
#         if self.qty or self.unit_cost:
#             self.line_cost = self.qty * self.unit_cost


class od_cost_bim_beta_manpower_manual_line(models.Model):
    _name = 'od.cost.bim.beta.manpower.manual.line'
    _order = "item_int ASC"
    item_int = fields.Integer(string="Item Seq",default=1)

    @api.one
    @api.depends('qty','unit_cost','unit_price','cost_group_id')
    def compute_calc(self):
        if self.cost_group_id:
            profit = self.cost_group_id.profit /100
            if profit >=1:
                raise Warning("Profit value for the costgroup %s set 100 or above,it should be below 100"%self.cost_group_id.name)
            discount = self.cost_group_id.customer_discount/100
            unit_cost = self.unit_cost
#             unit_price = (unit_cost / (1-profit)) - (unit_cost * discount)
            unit_price = (unit_cost / (1-profit))
            unit_price = unit_price * (1-discount)
            self.unit_price = unit_price
        if self.qty or self.unit_cost:
            self.line_cost = self.qty * self.unit_cost
        fixed = self.fixed
        locked = self.locked
        if not (fixed or locked):
            self.line_price = self.qty * self.unit_price
        else:
            self.line_price = self.qty * self.new_unit_price
    
    @api.one 
    @api.depends('tax_id','line_price','qty')
    def _compute_vat(self):
        if self.tax_id:
            vat = self.tax_id.amount 
            self.vat = vat  * 100
            vat_value1 = self.line_price * vat
            self.vat_value = vat_value1
           
    
    @api.one
    def _get_locked_status(self):
        
        if self.cost_sheet_id and self.cost_sheet_id.price_fixed and self.cost_sheet_id.state not in ('draft','design_ready','committed','submitted','returned_by_pmo','waiting_po_open'):
            self.locked = True
    
    
        
    def get_vat(self):
        return self.env.user.company_id.od_tax_id
            
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    sheet_id = fields.Many2one('od.cost.sheet',string='Sheet')
    item = fields.Char(string='Item')
    name = fields.Char(string='Description')
    qty = fields.Float(string='Qty',default=1)
    unit_price = fields.Float(string='Unit Price',compute='compute_calc',digits=dp.get_precision('Account'))
    temp_unit_price = fields.Float(string="Temp Unit Price",digits=dp.get_precision('Account'))
    new_unit_price = fields.Float(string="Fixed Unit Sale",digits=dp.get_precision('Account'))
    fixed = fields.Boolean(string="Price Fix")
    locked = fields.Boolean(string="Locked",compute='_get_locked_status')
    
    
    line_price = fields.Float(string='Line Price',compute='compute_calc',digits=dp.get_precision('Account'))
    unit_cost = fields.Float(string='Unit Cost',digits=dp.get_precision('Account'))
    line_cost = fields.Float(string='Line Cost',compute='compute_calc',digits=dp.get_precision('Account'))
    cost_group_id = fields.Many2one('od.cost.costgroup.it.service.line',string='Cost Group')
    bim_show_to_customer = fields.Boolean(string='Show to Customer',default=False)
    product_id = fields.Many2one('product.product',string='Expense',domain=[('type','=','service')])
    tax_id = fields.Many2one('account.tax',string="Tax",default=get_vat)
    vat = fields.Float(string="VAT %",compute='_compute_vat',digits=dp.get_precision('Account'))
    vat_value = fields.Float(string="VAT Value",compute='_compute_vat',digits=dp.get_precision('Account'))
    
    
    
    @api.one 
    @api.onchange('cost_group_id')
    def onchange_group(self):
        group = self.cost_group_id 
        self.tax_id = group.tax_id and group.tax_id.id
    
#     
#     @api.one 
#     @api.onchange('vat','line_price')
#     def onchange_vat(self):
#         vat = self.vat
#         line_price = self.line_price
#         vat_value = line_price * (vat/100.0)
#         self.vat_value = vat_value


#
#     @api.onchange('product_id')
#     def onchange_product(self):
#         if self.product_id:
#             self.name = self.product_id.description
#             self.unit_cost = self.product_id.standard_price
#     @api.onchange('qty','unit_cost')
#     def onchange_qty(self):
#         if self.qty or self.unit_cost:
#             self.line_cost = self.qty * self.unit_cost
#
#     @api.onchange('cost_group_id','unit_cost')
#     def onchange_group(self):
#
#         if self.cost_group_id:
#             profit = self.cost_group_id.profit /100
#             discount = self.cost_group_id.customer_discount/100
#             unit_cost = self.unit_cost
#             unit_price = unit_cost + (unit_cost*profit - unit_cost*discount)
#             self.unit_price = unit_price
#
#     @api.onchange('qty','unit_price')
#     def onchange_unitprice(self):
#         if self.qty or self.unit_price:
#             self.line_price = self.qty * self.unit_price


class od_cost_bim_beta_implementation_code(models.Model):
    _name = 'od.cost.bim.beta.implementation.code'
    _order = "item_int ASC"
    item_int = fields.Integer(string="Item Seq",default=1)
    @api.one
    @api.depends('imp_code','qty','unit_price','unit_cost','code_hours','cost_hour','group')
    def compute_calc(self):
        if self.group and self.imp_code and self.cost_hour:
            profit = self.group.profit /100
            if profit >=1:
                raise Warning("Profit value for the costgroup %s set 100 or above,it should be below 100"%self.group.name)
            discount = self.group.customer_discount/100
            unit_cost = self.imp_code.expected_act_duration * self.cost_hour
#             unit_price = (unit_cost / (1-profit)) - (unit_cost * discount)
            unit_price = (unit_cost / (1-profit))
            unit_price = unit_price * (1-discount)
            self.unit_price = unit_price
        if self.imp_code:
            self.code_hours = self.imp_code.expected_act_duration
        if self.qty and self.code_hours:
            self.total_hours = self.qty * self.code_hours
        if self.code_hours and self.cost_hour:
            self.unit_cost = self.code_hours * self.cost_hour
        if self.unit_cost and self.qty:
            self.line_cost = self.unit_cost * self.qty
        
        fixed = self.fixed
        locked = self.locked
        if (fixed or locked):
            self.line_price = self.new_unit_price * self.qty
        else:
            self.line_price = self.unit_price * self.qty
            
    
    @api.one 
    @api.depends('tax_id','line_price','qty')
    def _compute_vat(self):
        if self.tax_id:
            vat = self.tax_id.amount 
            self.vat = vat  * 100
            vat_value1 = self.line_price * vat
            self.vat_value = vat_value1
    
    
    
    @api.one
    def _get_locked_status(self):
        
        if self.cost_sheet_id and self.cost_sheet_id.price_fixed and self.cost_sheet_id.state not in ('draft','design_ready','committed','submitted','returned_by_pmo','waiting_po_open'):
            self.locked = True
    
    
        
    def get_vat(self):
        return self.env.user.company_id.od_tax_id
    
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    item = fields.Char(string='Item')
    imp_code = fields.Many2one('od.implementation',string='Implementation Code')
    qty = fields.Float('Qty',default=1)
    unit_price = fields.Float('Unit Sale',compute='compute_calc',digits=dp.get_precision('Account'))
    
    temp_unit_price = fields.Float(string="Temp Unit Price",digits=dp.get_precision('Account'))
    new_unit_price = fields.Float(string="Fixed Unit Sale",digits=dp.get_precision('Account'))
    fixed = fields.Boolean(string="Price Fix")
    locked = fields.Boolean(string="Locked",compute='_get_locked_status')
    
    line_price = fields.Float('Total Sale',compute='compute_calc',digits=dp.get_precision('Account'))
    unit_cost = fields.Float('Unit Cost',compute='compute_calc',digits=dp.get_precision('Account'))
    line_cost = fields.Float('Total Cost',compute='compute_calc',digits=dp.get_precision('Account'))
    group = fields.Many2one('od.cost.costgroup.it.service.line',string='Group')
    code_hours = fields.Float('Code Hours',compute='compute_calc',digits=dp.get_precision('Account'))
    total_hours = fields.Float('Total Hours',compute='compute_calc',digits=dp.get_precision('Account'))
    cost_hour = fields.Float('Cost / Hour',default=350.0,digits=dp.get_precision('Account'))
    tax_id = fields.Many2one('account.tax',string="Tax",default=get_vat)
    vat = fields.Float(string="VAT %",compute='_compute_vat',digits=dp.get_precision('Account'))
    vat_value = fields.Float(string="VAT Value",compute='_compute_vat',digits=dp.get_precision('Account'))
    
    
    
    
    @api.one 
    @api.onchange('group')
    def onchange_group(self):
        group = self.group
        self.tax_id = group.tax_id and group.tax_id.id    
    
#     @api.one 
#     @api.onchange('vat','line_price')
#     def onchange_vat(self):
#         vat = self.vat
#         line_price = self.line_price
#         vat_value = line_price * (vat/100.0)
#         self.vat_value = vat_value

    


#
#     @api.onchange('imp_code')
#     def onchange_imp_code(self):
#         if self.imp_code:
#             self.code_hours = self.imp_code.expected_act_duration
#     @api.onchange('qty','unit_price','unit_cost','code_hours','cost_hour')
#     def onchange_qty(self):
#         self.total_hours = self.qty * self.code_hours
#         self.unit_cost = self.code_hours * self.cost_hour
#         self.line_cost = self.unit_cost * self.qty
#         self.line_price = self.unit_price * self.qty
#     @api.onchange('group','unit_cost')
#     def onchange_group(self):
#         if self.group:
#             profit = self.group.profit /100
#             discount = self.group.customer_discount/100
#             unit_cost = self.unit_cost
#             unit_price = unit_cost + (unit_cost*profit - unit_cost*discount)
#             self.unit_price = unit_price

class od_cost_oim_implimentation_price_line(models.Model):
    _name = 'od.cost.oim.implimentation.price.line'
    _order = "item_int ASC"
    item_int = fields.Integer(string="Item Seq",default=1)

    @api.one
    @api.depends('qty','unit_price','unit_cost','group')
    def compute_calc(self):
        if self.group:
            profit = self.group.profit /100
            if profit >=1:
                raise Warning("Profit value for the costgroup %s set 100 or above,it should be below 100"%self.group.name)
            discount = self.group.customer_discount/100
            unit_cost = self.unit_cost
#             unit_price = (unit_cost / (1-profit)) - (unit_cost * discount)
            unit_price = (unit_cost / (1-profit))
            unit_price = unit_price * (1-discount)
            self.unit_price = unit_price
#         if self.unit_price and self.qty:
#             self.line_price = self.qty * self.unit_price
        fixed = self.fixed
        locked = self.locked
        if not (fixed or locked):
            self.line_price = self.qty * self.unit_price
        else:
            self.line_price = self.qty * self.new_unit_price   
        if self.unit_cost and self.qty:
            self.line_cost = self.qty * self.unit_cost
    
    
    @api.one 
    @api.depends('tax_id','line_price','qty')
    def _compute_vat(self):
        if self.tax_id:
            vat = self.tax_id.amount 
            self.vat = vat  * 100
            vat_value1 = self.line_price * vat
            self.vat_value = vat_value1
            
    
    @api.one
    def _get_locked_status(self):
        
        if self.cost_sheet_id and self.cost_sheet_id.price_fixed and self.cost_sheet_id.state not in ('draft','design_ready','committed','submitted','returned_by_pmo','waiting_po_open'):
            self.locked = True
    
    
        
    def get_vat(self):
        return self.env.user.company_id.od_tax_id
    
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    item = fields.Char(string='Item')
    partner_id = fields.Many2one('res.partner',string='Partner',domain=[('supplier','=',True),('is_company','=',True)])
    name = fields.Char(string='Description')
    qty = fields.Float(string='Qty',default=1,digits=dp.get_precision('Account'))
    unit_price = fields.Float(string='Unit Sale',compute='compute_calc',digits=dp.get_precision('Account'))
    
    temp_unit_price = fields.Float(string="Temp Unit Price",digits=dp.get_precision('Account'))
    new_unit_price = fields.Float(string="Fixed Unit Sale",digits=dp.get_precision('Account'))
    fixed = fields.Boolean(string="Price Fix")
    locked = fields.Boolean(string="Locked",compute='_get_locked_status')
    
    line_price = fields.Float(string='Total Sale',compute='compute_calc',digits=dp.get_precision('Account'))
    unit_cost = fields.Float(string='Unit Cost',digits=dp.get_precision('Account'))
    line_cost = fields.Float(string='Line Cost',compute='compute_calc',digits=dp.get_precision('Account'))
    group = fields.Many2one('od.cost.costgroup.it.service.line',string='Group')
    show_oim_price_cust = fields.Boolean(string='Show to Customer',default=False)
    tax_id = fields.Many2one('account.tax',string="Tax",default=get_vat)
    vat = fields.Float(string="VAT %",compute='_compute_vat',digits=dp.get_precision('Account'))
    vat_value = fields.Float(string="VAT Value",compute='_compute_vat',digits=dp.get_precision('Account'))
    
    
    
    
    @api.one 
    @api.onchange('group')
    def onchange_group(self):
        if self.cost_sheet_id and self.cost_sheet_id.price_fixed:
            self.fixed = True
        group = self.group
        self.tax_id = group.tax_id and group.tax_id.id
    
    
#     @api.one 
#     @api.onchange('vat','line_price')
#     def onchange_vat(self):
#         vat = self.vat
#         line_price = self.line_price
#         vat_value = line_price * (vat/100.0)
#         self.vat_value = vat_value



#     @api.onchange('od_product_id')
#     def onchange_product_id(self):
#         if self.od_product_id.id:
#             product_obj = self.od_product_id
#             self.name = product_obj.name
#             self.unit_price = product_obj.lst_price
#             self.unit_cost = product_obj.standard_price
#     @api.onchange('qty','unit_price')
#     def onchange_unit_price(self):
#         if self.unit_price:
#             self.line_price = self.qty * self.unit_price
#     @api.onchange('qty','unit_cost')
#     def onchange_unit_cost(self):
#         if self.unit_cost:
#             self.line_cost = self.qty * self.unit_cost
#     @api.onchange('group','unit_cost')
#     def onchange_group(self):
#         if self.group:
#             profit = self.group.profit /100
#             discount = self.group.customer_discount/100
#             unit_cost = self.unit_cost
#             unit_price = unit_cost + (unit_cost*profit - unit_cost*discount)
#             self.unit_price = unit_price
class od_cost_oim_extra_expenses_line(models.Model):
    _name = 'od.cost.oim.extra.expenses.line'
    _inherit = 'od.cost.mat.extra.expense.line'
    
    @api.one 
    @api.onchange('group')
    def onchange_group(self):
        group = self.group
        self.vat = group.vat
    
    @api.one 
    @api.onchange('vat','line_price')
    def onchange_vat(self):
        vat = self.vat
        line_price = self.line_price
        vat_value = line_price * (vat/100.0)
        self.vat_value = vat_value
#     cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
#     item = fields.Char(string='Item')
# #     product_id = fields.Many2one('product.product','Prouduct')
#     name = fields.Char(string='Description')
#     qty = fields.Float(string='Qty')
#     unit_cost = fields.Float(string='Unit Cost')
#     line_cost = fields.Float(string='Line Cost')
#     show_to_customer = fields.Boolean(string='Show to Customer',default=False)


#     @api.onchange('product_id')
#     def onchange_product_id(self):
#         if self.product_id.id:
#             product_obj = self.product_id
#             self.name = product_obj.name
#             self.unit_price = product_obj.lst_price
#             self.unit_cost = product_obj.standard_price
#     @api.onchange('qty','unit_cost')
#     def onchange_unit_cost(self):
#         if self.unit_cost:
#             self.line_cost = self.qty * self.unit_cost


class od_cost_om_residenteng_line(models.Model):
    _name = 'od.cost.om.residenteng.line'
    _order = "item_int ASC"
    item_int = fields.Integer(string="Item Number",default=1)
    
    @api.one
    @api.depends('qty','unit_price','unit_cost','line_price','line_cost','group')
    def compute_calc(self):
        if self.group:
            profit = self.group.profit /100
            if profit >=1:
                raise Warning("Profit value for the costgroup %s set 100 or above,it should be below 100"%self.group.name)
            discount = self.group.customer_discount/100
            unit_cost = self.unit_cost
#             unit_price = (unit_cost / (1-profit)) - (unit_cost * discount)
            unit_price = (unit_cost / (1-profit))
            unit_price = unit_price * (1-discount)
            self.unit_price = round(unit_price)
        fixed = self.fixed
        locked = self.locked
        if not (fixed or locked):
            self.line_price = self.qty * self.unit_price
        else:
            self.line_price = self.qty * self.new_unit_price
        if self.unit_cost and self.qty:
            self.line_cost = self.qty * self.unit_cost
        if self.line_price :
            self.profit = self.line_price - self.line_cost
            self.profit_percentage = (self.profit/self.line_price)*100

    @api.one 
    @api.depends('tax_id','line_price','qty')
    def _compute_vat(self):
        if self.tax_id:
            vat = self.tax_id.amount 
            self.vat = vat  * 100
            vat_value1 = self.line_price * vat
            self.vat_value = vat_value1
    
    
    @api.one
    def _get_locked_status(self):
        
        if self.cost_sheet_id and self.cost_sheet_id.price_fixed and self.cost_sheet_id.state not in ('draft','design_ready','committed','submitted','returned_by_pmo','waiting_po_open'):
            self.locked = True
    
        
    def get_vat(self):
        return self.env.user.company_id.od_tax_id
    
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    item = fields.Char(string='Item')
    od_product_id = fields.Many2one('product.product',string='Job Position',domain=[('type','=','service')])
    name = fields.Char(string='Description')
    qty = fields.Float(string='Qty',default=1,digits=dp.get_precision('Account'))
    unit_price = fields.Float(string='Unit Price',compute='compute_calc',digits=dp.get_precision('Account'))
    temp_unit_price = fields.Float(string="Temp Unit Price",digits=dp.get_precision('Account'))
    new_unit_price = fields.Float(string="Fixed Unit Sale",digits=dp.get_precision('Account'))
    fixed = fields.Boolean(string="Price Fix")
    locked = fields.Boolean(string="Locked",compute='_get_locked_status')
    
    line_price = fields.Float(string='Line Price',compute='compute_calc',digits=dp.get_precision('Account'))
    unit_cost = fields.Float(string='Unit Cost',digits=dp.get_precision('Account'))
    line_cost = fields.Float(string='Line Cost',compute='compute_calc',digits=dp.get_precision('Account'))
    profit = fields.Float(string='Profit',compute='compute_calc',digits=dp.get_precision('Account'))
    profit_percentage = fields.Float(string='Profit(%)',compute='compute_calc',digits=dp.get_precision('Account'))
    group = fields.Many2one('od.cost.costgroup.it.service.line',string='Group')
    show_to_customer = fields.Boolean(string='Show to Customer',default=False)
    tax_id = fields.Many2one('account.tax',string="Tax",default=get_vat)
    vat = fields.Float(string="VAT %",compute='_compute_vat',digits=dp.get_precision('Account'))
    vat_value = fields.Float(string="VAT Value",compute='_compute_vat',digits=dp.get_precision('Account'))
    
    
    
    @api.one 
    @api.onchange('group')
    def onchange_group(self):
        if self.cost_sheet_id and self.cost_sheet_id.price_fixed:
            self.fixed = True
        group = self.group
        self.tax_id = group.tax_id and group.tax_id
    
#     @api.one 
#     @api.onchange('vat','line_price')
#     def onchange_vat(self):
#         vat = self.vat
#         line_price = self.line_price
#         vat_value = line_price * (vat/100.0)
#         self.vat_value = vat_value
#     @api.onchange('od_product_id')
#     def onchange_product_id(self):
#         if self.od_product_id.id:
#             product_obj = self.od_product_id
#             self.name = product_obj.name
#             self.unit_price = product_obj.lst_price
#             self.unit_cost = product_obj.standard_price
#     @api.onchange('qty','unit_price')
#     def onchange_unit_price(self):
#         if self.unit_price:
#             self.line_price = self.qty * self.unit_price
#     @api.onchange('qty','unit_cost','group')
#     def onchange_unit_cost(self):
#         if self.unit_cost:
#             unit_cost = self.unit_cost
#             self.line_cost = self.qty * self.unit_cost
#             group = self.group
#             profit_per = group.profit/100
#             discount = group.customer_discount/100
#             unit_price = unit_cost + (unit_cost * profit_per - unit_cost* discount)
#             self.unit_price = unit_price
#     @api.onchange('line_price','line_cost')
#     def onchange_prices_to_profit(self):
#         self.profit = self.line_price - self.line_cost
#
#     @api.onchange('line_price','profit')
#     def onchange_profit_per(self):
#         if self.line_price:
#             self.profit_percentage = (self.profit/self.line_price)*100




class od_cost_om_eqpmentreq_line(models.Model):
    _name = 'od.cost.om.eqpmentreq.line'
    _inherit = 'od.cost.mat.main.pro.line'


class od_cost_om_extra_line(models.Model):
    _name = 'od.cost.om.extra.line'
    _inherit = 'od.cost.mat.extra.expense.line'

#     cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
#     item = fields.Char(string='Item')
#     name = fields.Char(string='Description')
#     qty = fields.Float(string='Qty')
#     unit_cost = fields.Float(string='Unit Cost')
#     line_cost = fields.Float(string='Line Cost')
#     show_to_customer = fields.Boolean(string='Show to Customer')



class od_cost_omn_out_preventive_maintenance_line(models.Model):
    _name = 'od.cost.omn.out.preventive.maintenance.line'
    _order = "item_int ASC"
    item_int = fields.Integer(string="Item Seq",default=1)
    @api.one
    @api.depends('qty','unit_price','unit_cost','line_price','line_cost','group')
    def compute_calc(self):
        if self.group:
            profit = self.group.profit /100
            if profit >=1:
                raise Warning("Profit value for the costgroup %s set 100 or above,it should be below 100"%self.group.name)
            discount = self.group.customer_discount/100
            unit_cost = self.unit_cost
#             unit_price = (unit_cost / (1-profit)) - (unit_cost * discount)
            unit_price = (unit_cost / (1-profit))
            unit_price = unit_price * (1-discount)
            self.unit_price = round(unit_price)
        fixed = self.fixed
        locked = self.locked 
        if not (fixed or locked):
            self.line_price = self.qty * self.unit_price
        else:
            self.line_price = self.qty * self.new_unit_price
        if self.unit_cost and self.qty:
            self.line_cost = self.qty * self.unit_cost
        if self.line_price :
            self.profit = self.line_price - self.line_cost
            self.profit_percentage = (self.profit/self.line_price)*100

    @api.one 
    @api.depends('tax_id','line_price','qty')
    def _compute_vat(self):
        if self.tax_id:
            vat = self.tax_id.amount 
            self.vat = vat  * 100
            vat_value1 = self.line_price * vat
            self.vat_value = vat_value1

    
    @api.one
    def _get_locked_status(self):
        
        if self.cost_sheet_id and self.cost_sheet_id.price_fixed and self.cost_sheet_id.state not in ('draft','design_ready','committed','submitted','returned_by_pmo','waiting_po_open'):
            self.locked = True
    
    
        
    def get_vat(self):
        return self.env.user.company_id.od_tax_id
    
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    sheet_id = fields.Many2one('od.cost.sheet',string="Sheet")
    item = fields.Char(string='Item')
    od_product_id = fields.Many2one('product.product',string='Product')
    name = fields.Char(string='Description')
    qty = fields.Float(string='Qty',default=1,digits=dp.get_precision('Account'))
    unit_price = fields.Float(string='Unit Price',compute='compute_calc',digits=dp.get_precision('Account'))
    
    
    temp_unit_price = fields.Float(string="Temp Unit Price",digits=dp.get_precision('Account'))
    new_unit_price = fields.Float(string="Fixed Unit Sale",digits=dp.get_precision('Account'))
    fixed = fields.Boolean(string="Price Fix")
    locked = fields.Boolean(string="Locked",compute='_get_locked_status')
    
    
    line_price = fields.Float(string='Line Price',compute='compute_calc',digits=dp.get_precision('Account'))
    unit_cost = fields.Float(string='Unit Cost',digits=dp.get_precision('Account'))
    line_cost = fields.Float(string='Line Cost',compute='compute_calc',digits=dp.get_precision('Account'))
    profit = fields.Float(string='Profit',compute='compute_calc',digits=dp.get_precision('Account'))
    profit_percentage = fields.Float(string='Profit(%)',compute='compute_calc',digits=dp.get_precision('Account'))
    group = fields.Many2one('od.cost.costgroup.it.service.line',string='Group',digits=dp.get_precision('Account'))
    show_to_customer = fields.Boolean(string='Show to Customer')
    tax_id = fields.Many2one('account.tax',string="Tax",default=get_vat)
    vat = fields.Float(string="VAT %",compute='_compute_vat',digits=dp.get_precision('Account'))
    vat_value = fields.Float(string="VAT Value",compute='_compute_vat',digits=dp.get_precision('Account'))
    

        
    @api.one 
    @api.onchange('group')
    def onchange_group(self):
        if self.cost_sheet_id and self.cost_sheet_id.price_fixed:
            self.fixed = True
        group = self.group
        self.tax_id = group.tax_id and group.tax_id.id
#     @api.one 
#     @api.onchange('vat','line_price')
#     def onchange_vat(self):
#         vat = self.vat
#         line_price = self.line_price
#         vat_value = line_price * (vat/100.0)
#         self.vat_value = vat_value

#     @api.onchange('od_product_id')
#     def onchange_product_id(self):
#         if self.od_product_id.id:
#             product_obj = self.od_product_id
#             self.name = product_obj.name
#             self.unit_cost = product_obj.standard_price
#     @api.onchange('qty','unit_price')
#     def onchange_unit_price(self):
#         if self.unit_price:
#             self.line_price = self.qty * self.unit_price
#     @api.onchange('qty','unit_cost')
#     def onchange_unit_cost(self):
#         if self.unit_cost:
#             self.line_cost = self.qty * self.unit_cost
#     @api.onchange('line_price','line_cost')
#     def onchange_prices_to_profit(self):
#         self.profit = self.line_price - self.line_cost
#
#     @api.onchange('line_price','profit')
#     def onchange_profit_per(self):
#         if self.line_price:
#             self.profit_percentage = (self.profit/self.line_price)*100
#
#     @api.onchange('group','unit_cost')
#     def onchange_group(self):
#
#         if self.group:
#             profit = self.group.profit /100
#             discount = self.group.customer_discount/100
#             unit_cost = self.unit_cost
#             unit_price = unit_cost + (unit_cost*profit - unit_cost*discount)
#             self.unit_price = unit_price


class od_cost_omn_out_remedial_maintenance_line(models.Model):
    _name = 'od.cost.omn.out.remedial.maintenance.line'
    _order = "item_int ASC"
    item_int = fields.Integer(string="Item Seq",default=1)
    @api.one
    @api.depends('qty','unit_price','unit_cost','line_price','line_cost','group')
    def compute_calc(self):
        if self.group:
            profit = self.group.profit /100
            if profit >=1:
                raise Warning("Profit value for the costgroup %s set 100 or above,it should be below 100"%self.group.name)
            discount = self.group.customer_discount/100
            unit_cost = self.unit_cost
#             unit_price = (unit_cost / (1-profit)) - (unit_cost * discount)
            unit_price = (unit_cost / (1-profit))
            unit_price = unit_price * (1-discount)
            self.unit_price = unit_price
        fixed = self.fixed
        locked = self.locked 
        if not (fixed or locked):
            self.line_price = self.qty * self.unit_price
        else:
            self.line_price = self.qty * self.new_unit_price
        if self.unit_cost and self.qty:
            self.line_cost = self.qty * self.unit_cost
        if self.line_price :
            self.profit = self.line_price - self.line_cost
            self.profit_percentage = (self.profit/self.line_price)*100

    
    
    @api.one 
    @api.depends('tax_id','line_price','qty')
    def _compute_vat(self):
        if self.tax_id:
            vat = self.tax_id.amount 
            self.vat = vat  * 100
            vat_value1 = self.line_price * vat
            self.vat_value = vat_value1

    
    
    @api.one
    def _get_locked_status(self):
        
        if self.cost_sheet_id and self.cost_sheet_id.price_fixed and self.cost_sheet_id.state not in ('draft','design_ready','committed','submitted','returned_by_pmo','waiting_po_open'):
            self.locked = True
    
    
        
    def get_vat(self):
        return self.env.user.company_id.od_tax_id
    
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    sheet_id = fields.Many2one('od.cost.sheet',string="Sheet")
    item = fields.Char(string='Item')
    name = fields.Char(string='Description')
    qty = fields.Float(string='Qty',default=1,digits=dp.get_precision('Account'))
    unit_price = fields.Float(string='Unit Price',compute='compute_calc',digits=dp.get_precision('Account'))
    
    
    temp_unit_price = fields.Float(string="Temp Unit Price",digits=dp.get_precision('Account'))
    new_unit_price = fields.Float(string="Fixed Unit Sale",digits=dp.get_precision('Account'))
    fixed = fields.Boolean(string="Price Fix")
    locked = fields.Boolean(string="Locked",compute='_get_locked_status')
    
    line_price = fields.Float(string='Line Price',compute='compute_calc',digits=dp.get_precision('Account'))
    unit_cost = fields.Float(string='Unit Cost',digits=dp.get_precision('Account'))
    line_cost = fields.Float(string='Line Cost',compute='compute_calc',digits=dp.get_precision('Account'))
    profit = fields.Float(string='Profit',compute='compute_calc',digits=dp.get_precision('Account'))
    profit_percentage = fields.Float(string='Profit(%)',compute='compute_calc',digits=dp.get_precision('Account'))
    group = fields.Many2one('od.cost.costgroup.it.service.line',string='Group',digits=dp.get_precision('Account'))
    show_to_customer = fields.Boolean(string='Show to Customer',digits=dp.get_precision('Account'))
    tax_id = fields.Many2one('account.tax',string="Tax",default=get_vat)
    vat = fields.Float(string="VAT %",compute='_compute_vat',digits=dp.get_precision('Account'))
    vat_value = fields.Float(string="VAT Value",compute='_compute_vat',digits=dp.get_precision('Account'))
    
    @api.one 
    @api.onchange('group')
    def onchange_group(self):
        if self.cost_sheet_id and self.cost_sheet_id.price_fixed:
            self.fixed = True
        group = self.group
        self.tax_id = group.tax_id and group.tax_id.id
    
#     @api.one 
#     @api.onchange('vat','line_price')
#     def onchange_vat(self):
#         vat = self.vat
#         line_price = self.line_price
#         vat_value = line_price * (vat/100.0)
#         self.vat_value = vat_value



#     @api.onchange('qty','unit_price')
#     def onchange_unit_price(self):
#         if self.unit_price:
#             self.line_price = self.qty * self.unit_price
#     @api.onchange('qty','unit_cost')
#     def onchange_unit_cost(self):
#         if self.unit_cost:
#             self.line_cost = self.qty * self.unit_cost
#     @api.onchange('line_price','line_cost')
#     def onchange_prices_to_profit(self):
#         self.profit = self.line_price - self.line_cost
#
#     @api.onchange('line_price','profit')
#     def onchange_profit_per(self):
#         if self.line_price:
#             self.profit_percentage = (self.profit/self.line_price)*100
#
#     @api.onchange('group','unit_cost')
#     def onchange_group(self):
#
#         if self.group:
#             profit = self.group.profit /100
#             discount = self.group.customer_discount/100
#             unit_cost = self.unit_cost
#             unit_price = unit_cost + (unit_cost*profit - unit_cost*discount)
#             self.unit_price = unit_price




class od_cost_omn_spare_parts_line(models.Model):
    _name = 'od.cost.omn.spare.parts.line'
    _inherit = 'od.cost.mat.main.pro.line'


class od_cost_omn_maintenance_extra_expense_line(models.Model):
    _name = 'od.cost.omn.maintenance.extra.expense.line'
    _inherit = 'od.cost.mat.extra.expense.line'
    
    @api.one 
    @api.onchange('group')
    def onchange_group(self):
        group = self.group
        self.vat = group.vat
    
    @api.one 
    @api.onchange('vat','line_price')
    def onchange_vat(self):
        vat = self.vat
        line_price = self.line_price
        vat_value = line_price * (vat/100.0)
        self.vat_value = vat_value
#     cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
#     item = fields.Char(string='Item')
#     name = fields.Char(string='Description')
#     qty = fields.Float(string='Qty')
#     unit_cost = fields.Float(string='Unit Cost')
#     line_cost = fields.Float(string='Line Cost')
#     show_to_customer = fields.Boolean(string='Show to Customer')




class od_cost_bmn_it_preventive_line(models.Model):
    _name = 'od.cost.bmn.it.preventive.line'
    _order = "item_int ASC"
    item_int = fields.Integer(string="Item Seq",default=1)

    @api.one
    @api.depends('qty','unit_price','unit_cost','line_price','line_cost','group')
    def compute_calc(self):
        if self.group:
            profit = self.group.profit /100
            if profit >=1:
                raise Warning("Profit value for the costgroup %s set 100 or above,it should be below 100"%self.group.name)
            discount = self.group.customer_discount/100
            unit_cost = self.unit_cost
#             unit_price = (unit_cost / (1-profit)) - (unit_cost * discount)
            unit_price = (unit_cost / (1-profit))
            unit_price = unit_price * (1-discount)
            self.unit_price = round(unit_price)
        fixed = self.fixed
        locked = self.locked
        if not (fixed or locked):
            self.line_price = self.qty * self.unit_price
        else:
            self.line_price = self.qty * self.new_unit_price
        if self.unit_cost and self.qty:
            self.line_cost = self.qty * self.unit_cost
        if self.line_price:
            self.profit = self.line_price - self.line_cost
            self.profit_percentage = (self.profit/self.line_price)*100
    
    

    @api.one 
    @api.depends('tax_id','line_price','qty')
    def _compute_vat(self):
        if self.tax_id:
            vat = self.tax_id.amount 
            self.vat = vat  * 100
            vat_value1 = self.line_price * vat
            self.vat_value = vat_value1
            
    
    @api.one
    def _get_locked_status(self):
        
        if self.cost_sheet_id and self.cost_sheet_id.price_fixed and self.cost_sheet_id.state not in ('draft','design_ready','committed','submitted','returned_by_pmo','waiting_po_open'):
            self.locked = True

        
    def get_vat(self):
        return self.env.user.company_id.od_tax_id
    
    
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    sheet_id = fields.Many2one('od.cost.sheet',string="sheet")
    item = fields.Char(string='Item')
    od_product_id = fields.Many2one('product.product',string='Product')
    name = fields.Char(string='Description')
#     imp_code = fields.Many2one('od.implementation',string="Description")
    imp_code = fields.Many2one('od.implementation',string="Description")
    description = fields.Char(string="Description")
    qty = fields.Float(string='Qty',default=1,digits=dp.get_precision('Account'))
    unit_price = fields.Float(string='Unit Price',compute='compute_calc',digits=dp.get_precision('Account'))
    
    temp_unit_price = fields.Float(string="Temp Unit Price",digits=dp.get_precision('Account'))
    new_unit_price = fields.Float(string="Fixed Unit Sale",digits=dp.get_precision('Account'))
    fixed = fields.Boolean(string="Price Fix")
    locked = fields.Boolean(string="Locked",compute='_get_locked_status')
    
    
    line_price = fields.Float(string='Line Price',compute='compute_calc',digits=dp.get_precision('Account'))
    unit_cost = fields.Float(string='Unit Cost',digits=dp.get_precision('Account'))
    line_cost = fields.Float(string='Line Cost',compute='compute_calc',digits=dp.get_precision('Account'))
    profit = fields.Float(string='Profit',compute='compute_calc',digits=dp.get_precision('Account'))
    profit_percentage = fields.Float(string='Profit(%)',compute='compute_calc',digits=dp.get_precision('Account'))
    group = fields.Many2one('od.cost.costgroup.it.service.line',string='Group',digits=dp.get_precision('Account'))
    show_to_customer = fields.Boolean(string='Show to Customer',digits=dp.get_precision('Account'))
    tax_id = fields.Many2one('account.tax',string="Tax",default=get_vat)
    vat = fields.Float(string="VAT %",compute='_compute_vat',digits=dp.get_precision('Account'))
    vat_value = fields.Float(string="VAT Value",compute='_compute_vat',digits=dp.get_precision('Account'))
    
    
    @api.one 
    @api.onchange('group')
    def onchange_group(self):
        group = self.group
        self.tax_id = group.tax_id and group.tax_id.id
    
#     @api.one 
#     @api.onchange('vat','line_price')
#     def onchange_vat(self):
#         vat = self.vat
#         line_price = self.line_price
#         vat_value = line_price * (vat/100.0)
#         self.vat_value = vat_value
#     @api.onchange('od_product_id')
#     def onchange_product_id(self):
#         if self.od_product_id.id:
#             product_obj = self.od_product_id
#             self.name = product_obj.name
#             self.unit_cost = product_obj.standard_price
#     @api.onchange('qty','unit_price')
#     def onchange_unit_price(self):
#         if self.unit_price:
#             self.line_price = self.qty * self.unit_price
#     @api.onchange('qty','unit_cost')
#     def onchange_unit_cost(self):
#         if self.unit_cost:
#             self.line_cost = self.qty * self.unit_cost
#     @api.onchange('line_price','line_cost')
#     def onchange_prices_to_profit(self):
#         self.profit = self.line_price - self.line_cost
#
#     @api.onchange('line_price','profit')
#     def onchange_profit_per(self):
#         if self.line_price:
#             self.profit_percentage = (self.profit/self.line_price)*100
#     @api.onchange('group','unit_cost')
#     def onchange_group(self):
#
#         if self.group:
#             profit = self.group.profit /100
#             discount = self.group.customer_discount/100
#             unit_cost = self.unit_cost
#             unit_price = unit_cost + (unit_cost*profit - unit_cost*discount)
#             self.unit_price = unit_price

class od_cost_bmn_it_remedial_line(models.Model):
    _name = 'od.cost.bmn.it.remedial.line'
    _order = "item_int ASC"
    item_int = fields.Integer(string="Item Seq",default=1)

    @api.one
    @api.depends('qty','unit_price','unit_cost','line_price','line_cost','group')
    def compute_calc(self):
        if self.group:
            profit = self.group.profit /100
            if profit >=1:
                raise Warning("Profit value for the costgroup %s set 100 or above,it should be below 100"%self.group.name)
            discount = self.group.customer_discount/100
            unit_cost = self.unit_cost
#             unit_price = (unit_cost / (1-profit)) - (unit_cost * discount)
            unit_price = (unit_cost / (1-profit))
            unit_price = unit_price * (1-discount)
            self.unit_price = round(unit_price)
        fixed = self.fixed
        locked = self.locked 
        if not (fixed or locked):
            self.line_price = self.qty * self.unit_price
        else:
            self.line_price = self.qty * self.new_unit_price
        
        if self.unit_cost and self.qty:
            self.line_cost = self.qty * self.unit_cost
        if self.line_price :
            self.profit = self.line_price - self.line_cost
            self.profit_percentage = (self.profit/self.line_price)*100
    
    @api.one 
    @api.depends('tax_id','line_price','qty')
    def _compute_vat(self):
        if self.tax_id:
            vat = self.tax_id.amount 
            self.vat = vat  * 100
            vat_value1 = self.line_price * vat
            self.vat_value = vat_value1
    
    
    @api.one
    def _get_locked_status(self):
        
        if self.cost_sheet_id and self.cost_sheet_id.price_fixed and self.cost_sheet_id.state not in ('draft','design_ready','committed','submitted','returned_by_pmo','waiting_po_open'):
            self.locked = True
    
        
    def get_vat(self):
        return self.env.user.company_id.od_tax_id
    
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    sheet_id = fields.Many2one('od.cost.sheet',string="sheet")
    item = fields.Char(string='Item')
    name = fields.Char(string='Description')
    qty = fields.Float(string='Qty',default=1,digits=dp.get_precision('Account'))
    unit_price = fields.Float(string='Unit Price',compute='compute_calc',digits=dp.get_precision('Account'))
    
    temp_unit_price = fields.Float(string="Temp Unit Price",digits=dp.get_precision('Account'))
    new_unit_price = fields.Float(string="Fixed Unit Sale",digits=dp.get_precision('Account'))
    fixed = fields.Boolean(string="Price Fix")
    locked = fields.Boolean(string="Locked",compute='_get_locked_status')
    
    line_price = fields.Float(string='Line Price',compute='compute_calc',digits=dp.get_precision('Account'))
    unit_cost = fields.Float(string='Unit Cost',digits=dp.get_precision('Account'))
    line_cost = fields.Float(string='Line Cost',compute='compute_calc',digits=dp.get_precision('Account'))
    profit = fields.Float(string='Profit',compute='compute_calc',digits=dp.get_precision('Account'))
    profit_percentage = fields.Float(string='Profit(%)',compute='compute_calc',digits=dp.get_precision('Account'))
    group = fields.Many2one('od.cost.costgroup.it.service.line',string='Group')
    show_to_customer = fields.Boolean(string='Show to Customer')
    tax_id = fields.Many2one('account.tax',string="Tax",default=get_vat)
    vat = fields.Float(string="VAT %",compute='_compute_vat',digits=dp.get_precision('Account'))
    vat_value = fields.Float(string="VAT Value",compute='_compute_vat',digits=dp.get_precision('Account'))
    
    

    @api.one 
    @api.onchange('group')
    def onchange_group(self):
        group = self.group
        self.tax_id = group.tax_id and group.tax_id.id    
#     @api.one 
#     @api.onchange('vat','line_price')
#     def onchange_vat(self):
#         vat = self.vat
#         line_price = self.line_price
#         vat_value = line_price * (vat/100.0)
#         self.vat_value = vat_value
#
#     @api.onchange('qty','unit_price')
#     def onchange_unit_price(self):
#         if self.unit_price:
#             self.line_price = self.qty * self.unit_price
#     @api.onchange('qty','unit_cost')
#     def onchange_unit_cost(self):
#         if self.unit_cost:
#             self.line_cost = self.qty * self.unit_cost
#     @api.onchange('line_price','line_cost')
#     def onchange_prices_to_profit(self):
#         self.profit = self.line_price - self.line_cost
#
#     @api.onchange('line_price','profit')
#     def onchange_profit_per(self):
#         if self.line_price:
#             self.profit_percentage = (self.profit/self.line_price)*100
#     @api.onchange('group','unit_cost')
#     def onchange_group(self):
#
#         if self.group:
#             profit = self.group.profit /100
#             discount = self.group.customer_discount/100
#             unit_cost = self.unit_cost
#             unit_price = unit_cost + (unit_cost*profit - unit_cost*discount)
#             self.unit_price = unit_price



class od_cost_bmn_spareparts_beta_it_maintenance_line(models.Model):
    _name = 'od.cost.bmn.spareparts.beta.it.maintenance.line'
    _inherit = 'od.cost.mat.main.pro.line'


class od_cost_bmn_beta_it_maintenance_extra_expense_line(models.Model):
    _name = 'od.cost.bmn.beta.it.maintenance.extra.expense.line'
    _inherit = 'od.cost.mat.extra.expense.line'
   
    
    
    @api.one 
    @api.onchange('group')
    def onchange_group(self):
        group = self.group
        self.vat = group.vat
    
    @api.one 
    @api.onchange('vat','line_price')
    def onchange_vat(self):
        vat = self.vat
        line_price = self.line_price
        vat_value = line_price * (vat/100.0)
        self.vat_value = vat_value
        
class principle_vendor_rebate(models.Model):
    _name = 'principle.vendor.rebate'
    
    @api.one
    def _get_locked_status(self):
        
        if self.cost_sheet_id and self.cost_sheet_id.price_fixed and self.cost_sheet_id.state not in ('draft','design_ready','committed','submitted','returned_by_pmo','waiting_po_open'):
            self.locked = True
    
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    rebate_product = fields.Many2one('product.product',string='Rebate Product', default=261059)
    manufacture_id = fields.Many2one('od.product.brand',string='Rebate Vendor')
    tech_unit_id = fields.Many2one('od.product.group',string='Technology Unit')
    value = fields.Float(string="Rebate Value",digits=dp.get_precision('Account'))
    terms = fields.Text(string='Terms & Condition')
    depo_withings = fields.Integer(string='Deposited within (Months) ')
    locked = fields.Boolean(string="Locked",compute='_get_locked_status')
    deal_info = fields.Text(string='Deal Registration Information / Reference')
    
class po_recieved_wiz(models.TransientModel):
    _name = 'po.recv.wiz'
    
    po_date= fields.Date(string="PO Date")
    attach_po = fields.Binary(string="Attach PO")
    file_name = fields.Char('Filename')
    po_no = fields.Char(string="Customer PO / Contract Number")


    
    @api.one
    def submit(self):
        context = self._context
        active_id = context.get('active_id')
        cost_sheet = self.env['od.cost.sheet']
        sheet_obj = cost_sheet.browse(active_id)
        vals = {'model_name': 'od.cost.sheet',
                'object_id': sheet_obj.id,
                'attach_file': self.attach_po,
                'attach_fname': self.file_name,
                'name': 'Customer PO'
            }
        self.env['od.attachement'].create(vals)
        sheet_obj.write({'po_date': self.po_date, 'po_status': 'available', 'part_ref': self.po_no })
        sheet_obj.date_log_history_line = [{'name':'Waiting PO To PO Available','date':str(datetime.now())}]
        sheet_obj.od_send_mail('cst_sheet_po_attached')
        return True
    
#Added by Aslam for Creating New Tab called Information Secuirity on 09/2024

class od_info_sec_services(models.Model):
    _name = 'od.cost.is.tech.line'
    _inherit = 'od.cost.mat.main.pro.line'
    manufacture_id = fields.Many2one('od.product.brand',string='Manufacture',required="1" ,default=1)
    group = fields.Many2one('od.cost.costgroup.it.service.line',string='Group',copy=True)
    
class od_info_sec_extra_expense_line(models.Model):
    _name = 'od.cost.is.extra.expense.line'
    _inherit = 'od.cost.mat.extra.expense.line'
    
    @api.one 
    @api.onchange('group')
    def onchange_group(self):
        group = self.group
        self.tax_id = group.tax_id and group.tax_id.id
    
class od_info_sec_subcontractor_line(models.Model):
    _name = 'od.cost.is.subcontractor.line'
    _inherit = 'od.cost.mat.extra.expense.line'
    
    @api.one 
    @api.onchange('group')
    def onchange_group(self):
        group = self.group
        self.vat = group.vat
    
    @api.one 
    @api.onchange('vat','line_price')
    def onchange_vat(self):
        vat = self.vat
        line_price = self.line_price
        vat_value = line_price * (vat/100.0)
        self.vat_value = vat_value

class od_info_sec_vendor_line(models.Model):
    _name = 'od.cost.is.vendor.line'
    _inherit = 'od.cost.mat.main.pro.line'
    manufacture_id = fields.Many2one('od.product.brand',string='Manufacture',required="1" ,default=1)
    group = fields.Many2one('od.cost.costgroup.it.service.line',string='Group',copy=True)
    
    
    

