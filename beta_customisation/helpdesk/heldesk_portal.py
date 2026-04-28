
# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning
from datetime import date, timedelta,datetime
from __builtin__ import False



class helpdesk_portal(models.Model):
    _name = "helpdesk.portal"
    _description = "Portal Access Helpdesk Issue"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    
    def od_get_company_id(self):
        return self.env.user.company_id
    
    @api.model
    def default_get(self, vals):
        partner = self.env.user.partner_id
        result = super(helpdesk_portal, self).default_get(vals)
        result.update({
                'customer_id' : partner.parent_id.id,
                'mobile': partner.mobile,
                'contact_id': partner.id,
                'landline' : partner.phone,
                'email': partner.email
            })
        return result
    
    @api.one
    @api.depends('start_date','project_id')    
    def _compute_proj_details1(self):
        self.start_date_dummy = self.start_date or False
    @api.one
    @api.depends('end_date','project_id')    
    def _compute_proj_details2(self):
        self.end_date_dummy = self.end_date or False
    @api.one
    @api.depends('po_number','project_id')    
    def _compute_proj_details3(self):
        self.po_number_dummy = self.po_number or False
        
    def compute_warn_string(self):
        customer_id = self.customer_id and self.customer_id.id or False
        project = self.env['project.project']
        domain =[('od_type_of_project','=','amc'),('state','=','open'),('partner_id','=', customer_id)]
        projects = project.search(domain)
        if len(projects) < 1:
            self.warn_string ="Alert: %s currently has no active contracts with Beta IT." % (self.customer_id.name)
        
        
    
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    name = fields.Char(string="Query")
    od_responsible = fields.Many2one('res.users', string="Responsible")
    customer_id = fields.Many2one('res.partner', string="Organisation", )
    contact_id = fields.Many2one('res.partner', string="Contact Person")
    mobile = fields.Char(string="Mobile")
    landline = fields.Char(string="Landline")
    email = fields.Char(string="Email")
    priority = fields.Selection([('high', 'High'),('low', 'Low'),('medium', 'Medium')],string="Priority", default= 'low')
    state = fields.Selection([('draft', 'Draft'),('send', 'In Progress'),('reject', 'Rejected'),],
                                  string='State', readonly=True,
                                  track_visibility='always', copy=False,  default= 'draft')
    notes = fields.Text(string="Issue Details")
    note_frm_sd = fields.Text(string="Feedback from Service Desk")
    deadline = fields.Date(string="Deadline")
    project_id = fields.Many2one('project.project', string="Select Agreement", domain=[('od_type_of_project','=','amc'),('state','=','open')])
    od_brand_ids = fields.Many2many('od.product.brand','rel_portal_helpdesk_product_brand1','p_hd_id','brand_id',string="Brands")
    od_summary_lines = fields.One2many('od.phd.summary.log','phd_id',string="Summary")
    od_categ_id = fields.Many2one('crm.case.categ', string="Category")
    od_channel_id = fields.Many2one('crm.tracking.medium', string="Channel")
    od_hd_issue_seq = fields.Char(string="Email")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    po_number = fields.Char(string="PO Number")
    start_date_dummy = fields.Date(string="Start Date" ,compute='_compute_proj_details1')
    end_date_dummy = fields.Date(string="End Date" ,compute='_compute_proj_details2')
    po_number_dummy = fields.Char(string="PO Number" ,compute='_compute_proj_details3')
    warn_string = fields.Char(string="Warning",compute="compute_warn_string")
    
    
    @api.onchange('project_id')
    def onchange_project_id(self):
        project_id = self.project_id or False
        if project_id:
            self.start_date= project_id.date_start or False
            self.end_date= project_id.od_date_end_original or False
            self.po_number = project_id.od_cost_sheet_id and project_id.od_cost_sheet_id.part_ref or False
    
    def od_send_mail(self,template):
        ir_model_data = self.env['ir.model.data']
        email_obj = self.pool.get('email.template')
        saudi_comp =6
        emp_company_id = self.company_id.id
        if emp_company_id == saudi_comp:
            template = template +'_saudi'    
        template_id = ir_model_data.get_object_reference('beta_customisation', template)[1]
        crm_id = self.id
        email_obj.send_mail(self.env.cr, self.env.uid, template_id,crm_id, force_send=True)
        return True
    
    @api.model
    def btn_confirm(self):
        self.write({'state':'send'})
        self.od_send_mail('send_mail_hd_service_desk')
        
        
            
    @api.model
    def create(self,vals):
        res = super(helpdesk_portal, self).create(vals)
        res.btn_confirm()
        return res
    
    def od_get_priority(self):
        if self.priority == 'low':
            return '0'
        if self.priority == 'medium':
            return '1'
        if self.priority == 'high':
            return '2'
        
    
    @api.model
    def create_helpdesk(self):
        hd_pool = self.env['crm.helpdesk']
        summary_log_pool = self.env['od.helpdesk.summary.log']
        date_log_pool = self.env['od.helpdesk.date.log']
        brand_ids = [pr.id for pr in self.od_brand_ids]
        hd_rec = hd_pool.create({'name': self.name,
                        'od_organization_id': self.customer_id.id,
                        'partner_id': self.contact_id.id,
                        'od_project_id2': self.project_id and self.project_id.id or False,
                        'date_deadline': self.deadline,
                        'od_mobile_number': self.mobile,
                        'od_landline': self.landline,
                        'email_from': self.email,
                        'description': self.notes,
                        'od_brand_ids': [[6, False,brand_ids]],
                        'user_id': self.od_responsible and self.od_responsible.id or False,
                        'categ_id': self.od_categ_id and self.od_categ_id.id or False,
                        'priority': self.od_get_priority(),
                        'channel_id': self.od_channel_id and self.od_channel_id.id or False,
                        'portal_user_create_date': self.create_date
            
            })
        date_log_pool.create({'hd_id': hd_rec.id, 'name': 'Query Submitted through Portal', 'date': self.create_date, 'user_id': self.create_uid.id})
        for line in self.od_summary_lines:
            summary_log_pool.create({'hd_id': hd_rec.id,
                                     'name': line.name })
        return hd_rec
        
        
    def check_all_req_fields_filled(self):
        if not self.project_id:
            raise Warning("Please fill Project field in the Service Desk Section before Accepting")
        if not self.deadline:
            raise Warning("Please fill Deadline date in the Service Desk Section before Accepting")
        if not self.od_responsible:
            raise Warning("Please fill Responsible person in the Service Desk Section before Accepting")
        if not self.od_categ_id:
            raise Warning("Please fill Category field in the Service Desk Section before Accepting")
        if not self.od_channel_id:
            raise Warning("Please fill Channel field in the Service Desk Section before Accepting")
        
    
    @api.one
    def approve_hd_issue(self):
        date_log_pool = self.env['od.helpdesk.date.log']
        self.check_all_req_fields_filled()
        hd_rec = self.create_helpdesk()
        self.od_hd_issue_seq = hd_rec.od_number
        self.od_send_mail('approve_mail_hd_portal_user')
        date_log_pool.create({'hd_id': hd_rec.id, 'name': 'Query Approved by Service Desk', 'date': str(datetime.now()), 'user_id': self.env.user.id})

        self.unlink()
    
    @api.one    
    def reject_hd_issue(self):
        self.write({'state':'reject'})
        self.od_send_mail('reject_hd_mail_to_portal_user')
        
        
class od_phd_summary_log(models.Model):
    _name = "od.phd.summary.log"
    _order ='date'
    phd_id = fields.Many2one('helpdesk.portal',string="Help Desk",ondelete="cascade")
    name = fields.Text(string="Notes")
    date = fields.Datetime(string="Date",default=lambda self: fields.datetime.now())
        
    