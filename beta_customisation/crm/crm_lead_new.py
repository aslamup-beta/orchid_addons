# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import Warning
from datetime import datetime


class crm_lead(models.Model):
    _inherit = "crm.lead"

    destination_stage_id = fields.Many2one('crm.case.stage', string="Destination Stage")
    customer_ref_data = fields.Char(string="Bid Reference")
    customer_ref_type = fields.Selection(
        [('etimad', 'Etimad'),
         ('forsah', 'Forsah'),
         ('sap_ariba', 'SAP Ariba'),
         ('customer_portal', 'Customer Portal'),
         ('inquiry', 'Inquiry')],
        string="Bid Reference الرقم المرجعي للمنافسة")

    @api.one
    def _compute_tq_count(self):
        for obj in self:
            sheet_ids = self.env['od.tender.request'].search([('lead_id', '=', obj.id)])
            if sheet_ids:
                self.od_tender_req_count = len(sheet_ids)

    @api.one
    def _compute_lg_count(self):
        for obj in self:
            sheet_ids = self.env['od.lg.request.form'].search([('lead_id', '=', obj.id)])
            if sheet_ids:
                self.od_lg_request_count = len(sheet_ids)

    od_tender_req_count = fields.Integer(string='Count', compute="_compute_tq_count")
    od_lg_request_count = fields.Integer(string='Count', compute="_compute_lg_count")

    @api.multi
    def write(self, vals):
        context = self._context
        #         if self.env.user.has_group('orchid_beta.group_beta_sale_account_mananger') and not context.get('allow_write'):
        if not context.get('allow_write') and not self.env.user.has_group('orchid_beta.group_beta_workers'):
            if self.stage_id.id == 1:
                if vals.get('stage_id') and vals.get('stage_id') != 1:
                    raise Warning("You are not allowed to change Opportunity state from this Menu Item")

            if self.stage_id.id == 4:
                if vals.get('stage_id') and vals.get('stage_id') != 4:
                    raise Warning("You are not allowed to change Opportunity state from this Menu Item")
            if self.stage_id.id == 6:
                if vals.get('stage_id') and vals.get('stage_id') != 6:
                    raise Warning("Opportunity already won, You Cannot change state !!")

            if self.stage_id.id in (12, 5, 14):
                if vals.get('stage_id') and vals.get('stage_id') not in (5, 12, 14):
                    raise Warning(
                        "You can only move to 'Pipeline' , 'High Probability' or 'Commit' from this Menu Item")

            if self.stage_id.id in (7, 8):
                if vals.get('stage_id') and vals.get('stage_id') not in (7, 8):
                    raise Warning("You can only move to 'Lost' or 'Cancelled' from this Menu Item")
            if self.stage_id.id == 13:
                if vals.get('stage_id') and vals.get('stage_id') != 13:
                    raise Warning("You are not allowed to change Opportunity state from this Menu Item")
        return super(crm_lead, self).write(vals)

    def od1_send_mail(self, template):
        ir_model_data = self.env['ir.model.data']
        email_obj = self.pool.get('email.template')
        if self.company_id.id == 6:
            template = template + '_saudi'
        template_id = ir_model_data.get_object_reference('beta_customisation', template)[1]
        rec_id = self.id
        email_obj.send_mail(self.env.cr, self.env.uid, template_id, rec_id, force_send=True)
        return True

    @api.one
    def request_cancel(self):
        self.write({'od_approval_state': 'request_cancel'})
        self.od1_send_mail('crm_cancel_request_email_template')

    @api.one
    def request_mark_lost(self):
        self.write({'od_approval_state': 'request_cancel'})
        self.od1_send_mail('crm_lost_request_email_template')

    @api.one
    def reject_cancel(self):
        self.write({'od_approval_state': 'approved'})
        self.od1_send_mail('crm_reject_request_email_template')

    @api.one
    def od_mark_cancel(self):
        self.od1_send_mail('crm_cancel_email_template')
        cost_sheets = self.env['od.cost.sheet'].search([('lead_id', '=', self.id)])
        for sheet in cost_sheets:
            sheet.btn_cancel()
        self.write({'stage_id': 8, 'od_approval_state': 'cancelled'})

    @api.multi
    def request_return_to_pipeline(self):
        return {
            'name': _('Request Return'),
            'view_type': 'form',
            "view_mode": 'form',
            'res_model': 'wiz.lead.request.return',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    # @api.one
    # def request_return_to_pipeline(self):
    #     self.write({'od_approval_state':'pending'})
    #     self.od1_send_mail('crm_return_to_pipeline_request_email_template')

    @api.one
    def od_returned_to_pipeline(self):
        self.od1_send_mail('crm_returned_to_pipeline_email_template')
        cost_sheets = self.env['od.cost.sheet'].search([('lead_id', '=', self.id)])
        for sheet in cost_sheets:
            if self.destination_stage_id.id == 12:
                sheet.write({'state': 'submitted'})
            if self.destination_stage_id.id == 1:
                sheet.write({'state': 'draft'})
        self.write({'stage_id': self.destination_stage_id.id, 'od_approval_state': 'approved'})

    @api.multi
    def od_open_lg_request(self):
        opp_id = self.id
        partner_id = self.partner_id and self.partner_id.id or False
        sale_val = self.planned_revenue
        context = self.env.context
        ctx = context.copy()
        ctx['default_lead_id'] = opp_id
        ctx['default_partner_id'] = partner_id
        ctx['default_job_amt'] = sale_val
        ctx['group_by'] = 'state'
        if opp_id:
            domain = [('lead_id', '=', opp_id)]
            return {
                'domain': domain,
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'od.lg.request.form',
                'type': 'ir.actions.act_window',
                'context': ctx,
            }

    @api.multi
    def od_open_tender_request(self):
        opp_id = self.id
        partner_id = self.partner_id and self.partner_id.id or False
        sale_val = self.planned_revenue
        context = self.env.context
        ctx = context.copy()
        ctx['default_lead_id'] = opp_id
        ctx['default_partner_id'] = partner_id
        ctx['default_job_amt'] = sale_val
        ctx['group_by'] = 'state'
        if opp_id:
            domain = [('lead_id', '=', opp_id)]
            return {
                'domain': domain,
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'od.tender.request',
                'type': 'ir.actions.act_window',
                'context': ctx,
            }


class wiz_lead_request_return(models.TransientModel):
    _name = 'wiz.lead.request.return'

    destination_stage_id = fields.Many2one('crm.case.stage', string="Destination Stage")

    @api.one
    def send_return_req(self):
        context = self._context
        active_id = context.get('active_id')
        lead = self.env['crm.lead']
        lead_obj = lead.browse(active_id)
        lead_obj.write({'od_approval_state':'pending', 'destination_stage_id': self.destination_stage_id.id,})
        lead_obj.od1_send_mail('crm_return_to_pipeline_request_email_template')
