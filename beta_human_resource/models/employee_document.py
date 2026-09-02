# -*- coding: utf-8 -*-
from openerp import models, fields, api
from datetime import date, timedelta


class BetaEmployeeDocumentLineNew(models.Model):
    _name = 'beta.employee.document.line.new'
    _description = 'Employee Document Line New'
    _order = 'id desc'

    employee_id = fields.Many2one(
        'hr.employee', string='Employee',
        default=lambda self: self.env.context.get('active_id'))
    od_document_type_id = fields.Many2one(
        'od.employee.document.type', string='Document Type', required=True)
    document_referance = fields.Char(string='Document Reference')
    attach_file = fields.Binary(string='Scanned Copy')
    attach_fname = fields.Char(string='File Name', size=128)
    issue_date = fields.Date(string='Issue Date')
    expiry_date = fields.Date(string='Expiry Date')
    reminder_sent = fields.Boolean(string='Reminder Sent', default=False, copy=False)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    od_document_line_ids = fields.One2many(
        'beta.employee.document.line.new', 'employee_id', string='Documents')
    od_document_line_count_new = fields.Integer(
        string='Document Count', compute='_compute_od_document_line_count')

    @api.multi
    def _compute_od_document_line_count(self):
        for employee in self:
            employee.od_document_line_count_new = len(employee.od_document_line_ids)

    @api.multi
    def od_view_new_documents(self):
        """Open the Documents list filtered to this employee, opened from
        the 'Documents' smart button on the employee form."""
        self.ensure_one()
        action = self.env['ir.actions.act_window'].for_xml_id(
            'beta_human_resource', 'action_beta_employee_document_line_new')
        action['domain'] = [('employee_id', '=', self.id)]
        action['context'] = {'default_employee_id': self.id}
        return action

    @api.model
    def cron_send_expiry_reminders(self):
        print("cron_send_expiry_reminders")
        days_before = 15
        target_date = date.today() + timedelta(days=days_before)

        doc_model = self.env['beta.employee.document.line.new']
        print("target_date", target_date)
        print("fields.Date.to_string(target_date)", fields.Date.to_string(target_date))
        domain = [
            ('expiry_date', '=', fields.Date.to_string(target_date)),
        ]
        docs = doc_model.search(domain)
        print("docs", docs)

        if not docs:
            return True

        template = self.env.ref(
            'beta_human_resource.email_template_document_expiry_reminder',
            raise_if_not_found=False)
        print("template", template)

        # Group documents by employee
        employees = docs.mapped('employee_id')
        print("employees", employees)

        # Filter employees where company_id is 1
        employees = [emp for emp in employees if emp.company_id.id == 1]

        for employee in employees:
            emp_docs = docs.filtered(lambda d: d.employee_id == employee)
            print("emp_docs", emp_docs)
            for emp_doc in emp_docs:
                if template:
                    template.with_context(
                        doc_type=emp_doc.od_document_type_id.name or '-',
                        exp_date=emp_doc.expiry_date,
                        days_before=days_before,
                    ).send_mail(employee.id, force_send=True)

                emp_doc.write({'reminder_sent': True})

        return True
