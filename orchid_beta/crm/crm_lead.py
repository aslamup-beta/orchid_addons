# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import Warning
from datetime import datetime
class crm_lead(models.Model):
    _inherit = "crm.lead"
    
    @api.one
    def _compute_cust_user_id(self):
        self.user_id_dummy = self.user_id and self.user_id.id or False
        
        
    user_id_dummy = fields.Many2one('res.users', compute='_compute_cust_user_id', string="Customer AM")
    od_partner_class = fields.Selection([('a', 'A'), ('b', 'B'), ('c', 'C'), ('r', 'R')],string="Class",related='partner_id.od_class',store=True)
    
    def get_saudi_company_id(self):
        parameter_obj = self.env['ir.config_parameter']
        key =[('key', '=', 'od_beta_saudi_co')]
        company_param = parameter_obj.search(key)
        if not company_param:
            raise Warning(_('Settings Warning!'),_('No Company Parameter Not defined\nconfig it in System Parameters with od_beta_saudi_co!'))
        saudi_company_id = company_param.od_model_id and company_param.od_model_id.id or False
        return saudi_company_id

    def od_send_mail(self,template):
        ir_model_data = self.env['ir.model.data']
        email_obj = self.pool.get('email.template')
        saudi_comp =self.get_saudi_company_id()
        user_company_id = self.env.user.company_id.id
        if user_company_id == saudi_comp:
            template = template +'_saudi'
        template_id = ir_model_data.get_object_reference('orchid_beta', template)[1]
        crm_id = self.id
        email_obj.send_mail(self.env.cr,self.env.uid,template_id,crm_id, force_send=True)
        return True
    
    def od_send_mail_to_approve(self):
        email_obj = self.pool.get('email.template')
        template_id = 73
        crm_id = self.id
        email_obj.send_mail(self.env.cr,self.env.uid,template_id,crm_id, force_send=True)
        return True
    
    #Added to send email to Yahya khorami ksa for his team when converting lead to opp
    def od_send_mail_to_y_approve(self):
        email_obj = self.pool.get('email.template')
        template_id = 326
        crm_id = self.id
        email_obj.send_mail(self.env.cr,self.env.uid,template_id,crm_id, force_send=True)
        return True
    
    #Added to send email to Shadi Hasan for his team when converting lead to opp
    def od_send_mail_to_shadi_approve(self):
        email_obj = self.pool.get('email.template')
        template_id = 342
        crm_id = self.id
        email_obj.send_mail(self.env.cr,self.env.uid,template_id,crm_id, force_send=True)
        return True
    
    #Added to cc osama for damam opp approval when converting lead to opp
    def od_send_mail_to_dmm_approve(self):
        email_obj = self.pool.get('email.template')
        template_id = 327
        crm_id = self.id
        email_obj.send_mail(self.env.cr,self.env.uid,template_id,crm_id, force_send=True)
        return True
        
    
    def check_date_change_access(self,user_id):
        uid = self._uid
        user_pool =self.env['res.users']
        user_obj = user_pool.browse(user_id)
        admin_ids = [1,154,268,5,2137,6,2280,101,8,2429,2663,2441,2536]
        if uid in admin_ids:
            return True
        if  uid != user_id:
            raise Warning("You are not allowed to change dates on this Opportunity, Please ask %s to do this."%user_obj.name)
        return uid == user_id
    
    def check_lead_user_change_access(self,user_id):
        uid = self._uid
        admin_ids = [1,154,268,5,2137,6,2280,101,8,134,2429,2663,2441,2536]
        if uid in admin_ids:
            return True
        if  uid != user_id:
            raise Warning("You are not allowed to change Lead AM on this Opportunity, Please contact Admin")
        return uid == user_id
    
    def find_yahya_sales_team(self):
        hr_pool = self.env['hr.employee']
        emp_ids = hr_pool.search([('od_branch_id', '=', 4),('parent_id', '=', 594),('job_id', 'in', (182,83))])
        user_ids = [2429]
        for employee in emp_ids:
            user_ids.append(employee.user_id.id)
        return user_ids
    
    @api.multi 
    def write(self,vals):
        lead_user_id = self.od_lead_user_id and self.od_lead_user_id.id or False
        yahya_team = self.find_yahya_sales_team()
        section_id = self.section_id and self.section_id.id or False
        if vals.get('od_req_on_7'):
            self.check_date_change_access(lead_user_id)
        if vals.get('od_budg_req_on'):
            self.check_date_change_access(lead_user_id)
        if vals.get('man_pre_date'):
            self.check_date_change_access(lead_user_id)
        if vals.get('tech_pre_date'):
            self.check_date_change_access(lead_user_id)
        if vals.get('rfp_date'):
            self.check_date_change_access(lead_user_id)
        if vals.get('proposal_date'):
            self.check_date_change_access(lead_user_id)
        if vals.get('hld_date'):
            self.check_date_change_access(lead_user_id)
        if vals.get('od_req_on_8'):
            self.check_date_change_access(lead_user_id)
        if vals.get('od_req_on_9'):
            self.check_date_change_access(lead_user_id)
        if vals.get('proof_date'):
            self.check_date_change_access(lead_user_id)
        if vals.get('financial_proposal') == False:
            self.check_date_change_access(lead_user_id)
        if vals.get('od_lead_user_id'):
            self.check_lead_user_change_access(lead_user_id)
        if self._uid !=1 and self.od_branch_id and vals.get('od_branch_id'):
            if self.od_branch_id.id != vals.get('od_branch_id'):
                raise Warning("You Cannot Change Branch,Please Contact Admin")
        if self._uid !=1 and self.partner_id and vals.get('partner_id'):
            if self.partner_id.id != vals.get('partner_id'):
                raise Warning("You Cannot change Customer/Organization,Please Contact Admin")
        if vals.get('type') == 'opportunity' and lead_user_id not in yahya_team and section_id != 15:
            self.od_send_mail_to_approve()
        if vals.get('type') == 'opportunity' and lead_user_id in yahya_team:
            self.od_send_mail_to_y_approve()
        if vals.get('type') == 'opportunity' and lead_user_id in (2507, 2640, 2546, 2434):
            self.od_send_mail_to_shadi_approve()    
        if vals.get('type') == 'opportunity' and section_id== 15:
            self.od_send_mail_to_dmm_approve()
        return super(crm_lead,self).write(vals)

    @api.one
    def od_approve(self):
        lead_user_id = self.od_lead_user_id and self.od_lead_user_id.id or False
        yahya_team = self.find_yahya_sales_team()
        # Restrict Yahya Khorami from Approving other Opportunities
        if self.env.user.id == 2429:
            if lead_user_id not in yahya_team:
                raise Warning("You are not able to Approve Opportunities outside your team, Please Discard")
        # Restrict Shadi from Approving other Opportunities
        if self.env.user.id == 2434:
            if lead_user_id not in (2434, 2446, 2511, 2583):
                raise Warning("You are not able to Approve Opportunities outside your team, Please Discard")
        self.od_approved_date = datetime.now().date()
        self.od_approved_by = self.env.user.id
        self.od_send_mail('od_crm_approve_mail')
        self.signal_workflow('approve')
        
    @api.one
    def od_reject(self):
        self.write({'stage_id': 13})
        self.od_send_mail('od_crm_reject_mail')
        self.signal_workflow('reject')
        
        