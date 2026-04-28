# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
from openerp import fields, models, api, _
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


class od_document_request(models.Model):
    _inherit = 'od.document.request'
    _description = "Document Request"
    _rec_name = 'employee_id'
    _order = 'create_date desc'

    requested_date = fields.Date(string="Requested Date", default=fields.Date.today)
    emp_notified = fields.Boolean(string="Employee Notified")
    manager_id = fields.Many2one('res.users', string="Direct Manager")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('to_approve', 'In Progress'),
        ('approved', 'Done'),
        ('refused', 'Refused')
    ], string='Status', index=True, readonly=True,
        track_visibility='onchange', default='draft')
    ref_to = fields.Char(string="Make Reference To (English)", default="To Whom It May Concern")
    ref_to_ar = fields.Char(string="Make Reference To (Arabic)", default="من يهمه الأمر")
    active = fields.Boolean(string="Active", default=True)
    refuse_reason = fields.Text(string="Return Reason")

    @api.one
    @api.constrains('employee_id', 'manager_id')
    def _check_manager(self):
        if self.employee_id and self.manager_id:
            if self.employee_id.sudo().parent_id.user_id and self.employee_id.sudo().parent_id.user_id.id != self.manager_id.id:
                raise Warning(_('Please select the correct manager'))

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        employee = self.employee_id or False
        if employee:
            self.manager_id = employee.sudo().parent_id and employee.sudo().parent_id.user_id and employee.sudo().parent_id.user_id.id or False

    def od_send_mail(self, template):
        print("template", template)
        ir_model_data = self.env['ir.model.data']
        email_obj = self.pool.get('email.template')
        if self.company_id.id == 6:
            template = template + '_saudi'
        template_id = ir_model_data.get_object_reference('beta_extended', template)[1]
        rec_id = self.id
        if template_id:
            email_obj.send_mail(self.env.cr, self.env.uid, template_id, rec_id, force_send=True)
        return True

    @api.one
    def action_notify_employee(self):
        if self.is_issued and not self.emp_notified:
            self.od_send_mail('od_doc_request_approved_employee')
            self.write({'emp_notified': True})

    @api.one
    def action_submit(self):
        self.od_send_mail('od_doc_request_approval_manager')
        return self.write({'state': 'to_approve'})

    @api.one
    def approval_action(self):
        if self.employee_id.user_id.id == self.env.user.id:
            raise osv.except_osv(_('Warning!'),
                                 _('You are not allowed to Approve your own request. Kindly contact your manager'))
        # self.od_send_mail('od_doc_request_notify_hr')
        return self.write({'state': 'approved'})

    # @api.one
    # def refuse_action(self):
    #     self.od_send_mail('od_doc_request_refused_employee')
    #     return self.write({'state': 'refused'})

    @api.multi
    def refuse_action(self):
        ctx = {'method': 'btn_cancel'}
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'doc.refuse.wiz',
            'context': ctx,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    @api.one
    def action_reset_to_draft(self):
        return self.write({'state': 'draft'})


class od_employee_document_type(models.Model):
    _inherit = 'od.employee.document.type'

    def od_get_company_id(self):
        return self.env.user.company_id

    company_id = fields.Many2one('res.company', string='Company', default=od_get_company_id)
    active = fields.Boolean(string="Active", default=True)
