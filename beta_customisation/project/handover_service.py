
# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning
from datetime import date, timedelta,datetime



class handover_service(models.Model):
    _name = "handover.service"
    _description = "Handover to Service Desk"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    
    def od_get_company_id(self):
        return self.env.user.company_id
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    name = fields.Char(string="Name", readonly=True)
    od_proj_manager = fields.Many2one('res.users', string="Beta IT Project Manager")
    od_sam = fields.Many2one('res.users', string="Beta IT Sales Account Manager")
    customer_id = fields.Many2one('res.partner', string="Customer")
    od_contact_ids = fields.Many2many('res.partner','od_handover_service_rel_contact_ids','h_service_id','partner_id',string="Contact Person")
    contract_no = fields.Char(string="Contract Number")
    contract_date = fields.Date(string="Contract Date")
    po_no = fields.Char(string="PO Number")
    po_date = fields.Date(string="PO Date")
    proj_so = fields.Many2one('sale.order', string="Project Sales Order")
    so_approval_date = fields.Date(string="SO Approval Date")
    so_val = fields.Float(string="SO Value")
    final_doc_folder = fields.Many2one('project.project',string="Materials Project") 
    #final_doc_folder_imp = fields.Many2one('project.project',string="Implementation Project")
    cost_sheet_id = fields.Many2one('od.cost.sheet',string="Cost Sheet")
    backup_copy = fields.Selection([('yes', 'YES'),('no', 'NO')],string="Do you have backup copy")
    comments = fields.Text(string="Comments")
    payment_details = fields.Text(string="Payment Details") 
    project_doc = fields.Char(string="Final Project Documentation")
    amc_so = fields.Many2one('sale.order', string="AMC Sales Order")
    is_proj_closed = fields.Selection([('yes', 'YES'),('no', 'NO')],string="Is Project closed fully")
    vendor_warranty = fields.Char(string="Vendor Warranty") 
    #serial_nmbr_xls
    tac_rma_case = fields.Selection([('yes', 'YES'),('no', 'NO')],string="Did you open earlier TAC or RMA Cases?")   
    rma_case_id = fields.One2many('tac.rma.case.table', 'handover_case_id' ,string="AMC Sales Order")
    state = fields.Selection([('draft', 'Start'),('handover', 'Hand over'),('approve', 'Approved'), ('reject', 'Rejected')],
                                  string='State', readonly=True,
                                  track_visibility='always', copy=False,  default= 'draft')
    sla_inc = fields.Boolean(string="SLA Included ?")
    date_log_history_line = fields.One2many('od.date.log.handover','handover_case_id',strint="Date Log History",readonly=True,copy=False)
    preventive_maintance_line = fields.One2many('od.preventive.maint.table','handover_case_id',strint="Preventive Maintanance Schedule")
    rej_reasn = fields.Text(string="Reason for Reject")
    
    @api.onchange('cost_sheet_id')
    def onchange_cost_sheet_id(self):
        cost_sheet = self.cost_sheet_id or False
        if cost_sheet:
            self.od_proj_manager = cost_sheet.reviewed_id and cost_sheet.reviewed_id.id or False
            self.od_sam = cost_sheet.lead_acc_manager and cost_sheet.lead_acc_manager.id or False
            self.customer_id = cost_sheet.od_customer_id and cost_sheet.od_customer_id.id or False
            self.po_no = cost_sheet.part_ref or False
            self.po_date =  cost_sheet.po_date or False
            self.so_approval_date = cost_sheet.approved_date and cost_sheet.approved_date[:10] or False
            self.so_val = cost_sheet.sum_total_sale or 0.0
            
    def send_mail_to_sd_manager(self,template):
        ir_model_data = self.env['ir.model.data']
        email_obj = self.pool.get('email.template')
        if self.company_id.id == 6:
            template = template +'_saudi'
        template_id = ir_model_data.get_object_reference('beta_customisation', template)[1]
        rec_id = self.id
        email_obj.send_mail(self.env.cr,self.env.uid,template_id,rec_id, force_send=True)
        return True
    
    def create_crm_helpdesk(self):
        if self.sla_inc:
            if len(self.preventive_maintance_line) == 0:
                raise Warning("At Lease One Preventive Maintenance Schedule Needed be added.")
            help_desk = self.env['crm.helpdesk']
            preventive_maint_sch = self.env['preventive.maint.schedule']
            od_organization_id = self.customer_id and self.customer_id.id
            categ_id =17
            for line in self.preventive_maintance_line:
                vals = {
                    'od_project_id':line.project_id.id,
                    'od_project_id2':line.project_id.id,
                    'user_id':line.project_id.od_owner_id and line.project_id.od_owner_id.id or False,
                    'name':line.name,
                    'od_organization_id':od_organization_id,
                    'date_deadline':line.date,
                    'categ_id':categ_id,
                    'od_prev_create':True,
                    }
                hp_id =help_desk.create(vals)
                preventive_maint_sch.create({'name': line.name, 
                                             'analytic_id': line.project_id.analytic_account_id.id, 
                                             'date': line.date, 
                                             'help_desk_id': hp_id.id})
        return True
                    
    def create_seq(self):
        sheet =self.cost_sheet_id
        sheet_id = sheet.id
        sheet_num = sheet.number
        costsheets = self.search([('cost_sheet_id','=',sheet_id)])
        cst_sheet_count = len(costsheets) 
        self.name = sheet_num +'-HO-'+str(cst_sheet_count)
        
    @api.one
    def approve_ho(self):
        self.create_crm_helpdesk()
        self.state = "approve"
        self.date_log_history_line = [{'name':'Hand over Approved','user_id': self.env.user.id, 'date':str(datetime.now())}]
  
        
    @api.multi
    def reject_ho_wizard(self):
        return {
              'name': _('Reject Handover'),
              'view_type': 'form',
              "view_mode": 'form',
              'res_model': 'wiz.handover.reject',
              'type': 'ir.actions.act_window',
              'target':'new',
              }
        
    @api.one
    def btn_confirm(self):
        self.create_seq()
        self.send_mail_to_sd_manager('handover_to_service_email_template')
        self.write({'state':'handover'})
        self.date_log_history_line = [{'name':'Hand over','user_id': self.env.user.id, 'date':str(datetime.now())}]
    
    @api.model
    def create(self,vals):
        res = super(handover_service, self).create(vals)
        res.btn_confirm()
        return res
                
class tac_rma_case_table(models.Model):
    _name = "tac.rma.case.table"
    
    handover_case_id =fields.Many2one('handover.service', string="Case ID")
    manufacture = fields.Many2one('od.product.brand', string="Manufacture")
    equipment = fields.Char(string="Equipment")
    location = fields.Char(string="Location")
    case_no = fields.Char(string="Case Number")
    case_status = fields.Selection([('open', 'Open'),('close', 'Closed')],string="Case Status")
    case_date = fields.Date(string="Case Date")
    beta_it_engineer = fields.Many2one('res.users', string="Beta IT Engineer")
    vendor_tac_contact = fields.Char(string="Vendor TAC Contact")
    #username = fields.Date(string="Username")
    #password =  fields.Char(string="Password")
    
class preventive_maintanance_table(models.Model):
    _name = "od.preventive.maint.table"
    
    handover_case_id =fields.Many2one('handover.service', string="Case ID")
    project_id = fields.Many2one('project.project',string="Project")
    name = fields.Char(string="Description")
    date = fields.Date(string="Date")
    
    
    
class od_date_log_handover(models.Model):
    _name = 'od.date.log.handover'
    handover_case_id =fields.Many2one('handover.service', string="Case ID")
    name = fields.Char(string='Name')
    user_id = fields.Many2one('res.users', string="User")
    date = fields.Datetime(string="Date")
    
class wiz_handover_reject(models.TransientModel):

    _name = 'wiz.handover.reject'
    
    rej_reasn = fields.Text(string="Reason for Reject")
    
    @api.one
    def send_lost_req(self):
        context = self._context
        active_id = context.get('active_id')
        handover = self.env['handover.service']
        handover_obj = handover.browse(active_id)
        handover_obj.write({'state': 'reject', 'rej_reasn': self.rej_reasn})
        handover_obj.send_mail_to_sd_manager('handover_rejected_by_sd_email_template')
        handover_obj.date_log_history_line = [{'name':'Hand over Rejected','user_id': self.env.user.id, 'date':str(datetime.now())}]

    
    
    
    
    
    
    