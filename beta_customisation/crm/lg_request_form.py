# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning

class BetaLGRequest(models.Model):
    _name = 'od.lg.request.form'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "LG Request Form"
    _rec_name = 'job_name'
    _order = 'create_date desc'
    
    def od_get_company_id(self):
        return self.env.user.company_id
    
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    date = fields.Date(string='Date')
    state = fields.Selection([('draft', 'Pending Verification'),('verify', 'Verified'), ('approve', 'Approved'), ('cancel', 'Cancelled')],
                                  string='State', readonly=True,
                                  track_visibility='always', copy=False, default="draft")
    partner_id = fields.Many2one('res.partner', string='Customer')
    lead_id = fields.Many2one('crm.lead', string='Related Opportunity')
    cost_sheet_id = fields.Many2one('od.cost.sheet', string='Related Cost sheet')
    guarantee_name = fields.Selection([('bid_bond', 'Bid Bond'),('performance_bond', 'Performance Bond'), ('advance_payment_guarantee', 'Advance Payment Guarantee')],
                                  string='Guarantee Name', default="bid_bond")
    lang = fields.Selection([('eng', 'English'),('arab', 'Arabic'), ('both', 'Both')],
                                  string='Language', copy=False)
    format = fields.Selection([('general', 'General Format'),('custom', 'Customer Format')],
                                  string='Format Type', copy=False)
    is_fixed = fields.Boolean(string="Fixed Guarantee")
    auto_ren = fields.Boolean(string="Auto Renewal")
    job_amt = fields.Float(string="Sales Value")
    enter_lg_amt = fields.Boolean(string="Enter LG Amt and Convert Percent?")
    enter_lg_per = fields.Boolean(string="Enter LG Percent and Convert Amt?")
    lg_amt = fields.Float(string="L/G Amount")
    lg_perc = fields.Float(string="L/G %")
    lg_amt1 = fields.Float(string="L/G Amount")
    lg_perc1 = fields.Float(string="L/G %")
    cust_lpo = fields.Char(string='Cust.LPO/Ref. #')
    job_name = fields.Char(string='Job Name/Desc')
    
    valdity_from = fields.Date(string='Validity From')
    valdity_to = fields.Date(string='Validity To')
    comments = fields.Text(string='Comments')
    requested_by = fields.Many2one('res.users', string='Requested By')
    req_date = fields.Date(string='Date')
    verified_by = fields.Many2one('res.users', string='Verified By')
    verify_date = fields.Date(string='Date')
    approved_by = fields.Many2one('res.users', string='Approved By')
    appr_date = fields.Date(string='Date')
    
    def od_send_mail(self,template):
        ir_model_data = self.env['ir.model.data']
        email_obj = self.pool.get('email.template')
        saudi_comp =6
        emp_company_id = self.company_id.id
        if emp_company_id == saudi_comp:
            template = template +'_saudi'    
        template_id = ir_model_data.get_object_reference('beta_customisation', template)[1]
        crm_id = self.id
        email_obj.send_mail(self.env.cr, self.env.uid, template_id,crm_id)
        return True
    
    @api.onchange('lg_amt')
    def onchange_lg_amt(self):
        if self.lg_amt and self.job_amt:
            self.lg_perc = (self.lg_amt/self.job_amt)*100
    
    @api.onchange('lg_perc1')
    def onchange_lg_perc1(self):
        if self.lg_perc1 and self.job_amt:
            self.lg_amt1 = self.job_amt*(self.lg_perc1/100.0)
    
    @api.one
    def btn_confirm(self):
        if not (self.enter_lg_amt or self.enter_lg_per):
            raise Warning("Please enter L/G amount using one of the two options.")
        self.requested_by = self.env.user.id
        self.req_date = fields.Date.today()
        self.od_send_mail('od_notify_finance_verify_lg_request')
        self.write({'state':'draft'})
    
    @api.model
    def create(self,vals):
        res = super(BetaLGRequest, self).create(vals)
        res.btn_confirm()
        return res
    
    @api.one
    def btn_refuse(self):
        self.od_send_mail('od_notify_sam_refuse_lg_request')
        self.write({'state':'cancel'})
    
    @api.one
    def btn_verify(self):
        self.verified_by = self.env.user.id
        self.verify_date = fields.Date.today()
        self.od_send_mail('od_notify_gm_approve_lg_request')
        self.write({'state':'verify'})
        
    @api.one
    def btn_approve(self):
        self.approved_by = self.env.user.id
        self.appr_date = fields.Date.today()
        self.od_send_mail('od_notify_sam_verify_lg_request')
        self.write({'state':'approve'})
        
    