# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError


class ProjectFeedbackRequestWizard(models.TransientModel):
    _name = 'project.feedback.request.wizard'
    _description = 'Send Customer Feedback Request'

    project_id = fields.Many2one(
        'project.project', string='Project', required=True)

    email_from = fields.Char(
        string='From Email',
        help='Sender address the feedback request will be emailed from.')

    email_to = fields.Char(
        string='To Email',
        help='Recipient address the feedback request will be emailed to.')

    language = fields.Selection([
        ('en', 'English'),
        ('ar', 'Arabic'),
    ], string='Language', required=True, default='en',
        help='The feedback email (and the public feedback page it links '
             'to) will be sent/shown in this language. Determines which '
             'of Message (English) / Message (Arabic) below is used.')

    message_en = fields.Char(
        string='Message (English)',
        help='The full sentence shown in the email when Language is '
             'English - e.g. "Thank you for working with us on the '
             'SA12504 TALEMIA-RFQ Cisco UCCX and Recording project."')

    message_ar = fields.Char(
        string='Message (Arabic)',
        help='The full sentence shown in the email when Language is '
             'Arabic - e.g. "نشكركم على تعاونكم معنا في مشروع '
             'SA12504 TALEMIA-RFQ Cisco UCCX and Recording."')

    @api.multi
    def action_send(self):
        self.ensure_one()
        if not self.email_to:
            raise UserError(_('Please enter a "To" email address.'))
        if not self.email_from:
            raise UserError(_('Please enter a "From" email address.'))
        message = self.message_ar if self.language == 'ar' else self.message_en
        if not message:
            raise UserError(_(
                'Please enter a Message (%s).'
            ) % (_('Arabic') if self.language == 'ar' else _('English')))
        self.project_id.send_feedback_email(
            email_from=self.email_from, email_to=self.email_to,
            language=self.language, message=message)
        return {'type': 'ir.actions.act_window_close'}
