# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError

DEFAULT_MESSAGE_EN = (
    u"Thank you for working with us. As part of our ongoing efforts to "
    u"develop and enhance our services, we would be delighted to hear "
    u"your feedback."
)
DEFAULT_MESSAGE_AR = (
    u"شكراً لتعاونك معنا. كجزء من جهودنا المستمرة لتطوير وتحسين "
    u"خدماتنا، يسعدنا جداً سماع آرائك"
)


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
        default=DEFAULT_MESSAGE_EN,
        help='The full sentence shown in the email when Language is English.')

    message_ar = fields.Char(
        string='Message (Arabic)',
        default=DEFAULT_MESSAGE_AR,
        help='The full sentence shown in the email when Language is Arabic.')

    @api.onchange('language')
    def _onchange_language(self):
        """Refill the message for the selected language with the default
        text, but only if the field is empty or still holds the default,
        so we never overwrite something the user typed."""
        if self.language == 'ar':
            if not self.message_ar or self.message_ar == DEFAULT_MESSAGE_AR:
                self.message_ar = DEFAULT_MESSAGE_AR
        else:
            if not self.message_en or self.message_en == DEFAULT_MESSAGE_EN:
                self.message_en = DEFAULT_MESSAGE_EN

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