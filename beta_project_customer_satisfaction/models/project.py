# -*- coding: utf-8 -*-
import uuid

from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError


class account_analytic_account(models.Model):
    _inherit = "account.analytic.account"

    cust_feedback_score = fields.Float(
        string="Customer Feedback Score",
        compute="_kpi_score"
    )

    def get_cust_feedback_score(self):
        self.ensure_one()
        cust_feedback_score = 0
        project_id = self.env['project.project'].search(
            [('analytic_account_id', '=', self.id)], limit=1
        )
        if project_id:
            cust_feedback_score = project_id.score
        return cust_feedback_score

    @api.one
    def _kpi_score(self):
        day_process_score = 0
        invoice_schedule_score = 0
        cost_control_score = 0
        compliance_score = 0
        schedule_control_score = 0
        cust_feedback_score = 0
        total_score = 0
        print("self.company_id", self.company_id)
        if self.company_id.id == 6:
            day_process_score = .1 * self.get_day_procss_score()
            invoice_schedule_score = .25 * self.get_invoice_schedule_score()
            cost_control_score = .2 * self.get_cost_control_score()
            compliance_score = .1 * self.get_compliance_score()
            schedule_control_score = .25 * self.get_schedule_control_score()
            cust_feedback_score = .1 * self.get_cust_feedback_score()

            total_score = (
                    day_process_score
                    + invoice_schedule_score
                    + cost_control_score
                    + compliance_score
                    + schedule_control_score
                    + cust_feedback_score
            )
        if self.company_id.id == 1:
            day_process_score = .1 * self.get_day_procss_score()
            invoice_schedule_score = .3 * self.get_invoice_schedule_score()
            cost_control_score = .2 * self.get_cost_control_score()
            compliance_score = .1 * self.get_compliance_score()
            schedule_control_score = .3 * self.get_schedule_control_score()

            total_score = day_process_score + invoice_schedule_score + cost_control_score + compliance_score + schedule_control_score

        self.day_process_score = day_process_score
        self.invoice_schedule_score = invoice_schedule_score
        self.cost_control_score = cost_control_score
        self.compliance_score = compliance_score
        self.schedule_control_score = schedule_control_score
        self.cust_feedback_score = cust_feedback_score
        self.total_score = total_score




class ProjectProject(models.Model):
    _inherit = 'project.project'

    # A project only ever has one "current" feedback request/answer, so
    # this lives directly on project.project rather than in a separate
    # project.customer.feedback model + One2many. Re-sending a request
    # (see action_send_feedback_request) resets rating/feedback_text so
    # the project always reflects the latest answer only.
    feedback_token = fields.Char(
        string='Feedback Token', copy=False, readonly=True, index=True)

    rating = fields.Selection(
        [(str(i), str(i)) for i in range(0, 11)],
        string='Customer Rating', copy=False, default=False,
        help='0 = extremely unsatisfied, 10 = extremely satisfied.')

    feedback_text = fields.Text(string='Customer Feedback Score', copy=False)

    score = fields.Float(
        string='Score', compute='_compute_score', store=True, copy=False,
        help='Automatically calculated as (rating / 10) * 100.')

    feedback_language = fields.Selection([
        ('en', 'English'),
        ('ar', 'Arabic'),
    ], string='Feedback Language', copy=False, default='en',
        help='Language the last feedback request was sent in. The public '
             'feedback page renders in this language to match the email.')

    feedback_sent_to = fields.Char(
        string='Feedback Sent To', copy=False, readonly=True,
        help='The "To" email address the last feedback request was '
             'actually sent to (as entered in the wizard).')

    feedback_message = fields.Char(
        string='Feedback Message', copy=False, readonly=True,
        help='The full sentence typed into the wizard (in whichever '
             'language was selected) and shown as-is in the last feedback '
             'email - no surrounding boilerplate text is added.')

    _sql_constraints = [
        ('feedback_token_uniq', 'unique(feedback_token)',
         'The feedback token must be unique!'),
    ]

    @api.depends('rating')
    def _compute_score(self):
        for project in self:
            # Note: '0' is a valid rating (extremely unsatisfied) - check
            # against False/'' explicitly rather than a plain truthy test,
            # since bool('0') is True in Python this happens to already be
            # safe for the *string* selection value, but keep it explicit
            # for clarity given get_feedback_url() below had exactly this
            # class of bug with an integer 0.
            project.score = int(project.rating) * 10.0 \
                if project.rating not in (False, '') else 0.0

    @api.model
    def get_by_token(self, token):
        """Fetch a project from its public feedback token. Returns an empty
        recordset if the token is unknown."""
        if not token:
            return self.browse()
        return self.search([('feedback_token', '=', token)], limit=1)

    @api.multi
    def is_submitted(self):
        """True once the customer has answered the current request - there
        is no separate state field to keep in sync."""
        self.ensure_one()
        return bool(self.rating)

    @api.multi
    def get_feedback_url(self, rating=None):
        """Build the public feedback URL for this project, optionally with
        a pre-selected rating (used by the 0-10 rating bar links in the
        email). Note: rating=0 is a valid, meaningful value ("extremely
        unsatisfied") - checking `is not None` rather than plain
        truthiness, since `if rating:` would silently drop it (0 is
        falsy)."""
        self.ensure_one()
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url') or ''
        # base_url = 'http://localhost:8068'
        url = '%s/feedback/feedback?token=%s' % (base_url, self.feedback_token)
        if rating is not None:
            url += '&rating=%s' % rating
        return url

    @api.multi
    def action_submit_feedback(self, rating, feedback_text):
        """Called by the public controller when the customer submits the
        feedback form."""
        self.ensure_one()
        vals = {}
        if rating in [str(i) for i in range(0, 11)]:
            vals['rating'] = rating
        if feedback_text:
            vals['feedback_text'] = feedback_text
        if vals:
            self.write(vals)
        return True

    @api.multi
    def action_send_feedback_request(self):
        """Button handler on the Project form: opens the wizard that asks
        for From email, To email, and Language before anything is sent.
        Nothing is pre-filled - all three must be entered manually."""
        self.ensure_one()
        wizard = self.env['project.feedback.request.wizard'].create({
            'project_id': self.id,
            'email_from': 'cx.ksa@betait.net',
        })
        view = self.env.ref(
            'beta_project_customer_satisfaction.view_feedback_request_wizard_form',
            raise_if_not_found=False)
        return {
            'name': _('Send Feedback Request'),
            'type': 'ir.actions.act_window',
            'res_model': 'project.feedback.request.wizard',
            'res_id': wizard.id,
            'view_mode': 'form',
            'view_id': view.id if view else False,
            'target': 'new',
        }

    @api.multi
    def send_feedback_email(self, email_from, email_to, language, message):
        """Actually emails the feedback request with a clickable 0-10
        rating bar, using the From/To/Language/Message entered in the
        wizard - all four are required, nothing is auto-fetched or
        defaulted here. `message` is shown as-is in the email (no
        surrounding boilerplate sentence any more). Resets any previous
        rating/feedback so a fresh request can be answered again."""
        self.ensure_one()
        if not email_from:
            raise UserError(_('Please provide a "From" email address.'))
        if not email_to:
            raise UserError(_('Please provide a "To" email address.')) 
        if not message:
            raise UserError(_('Please provide a Message.'))
        if language not in ('en', 'ar'):
            raise UserError(_('Please select a Language (English or Arabic).'))

        vals = {
            'rating': False,
            'feedback_text': False,
            'feedback_language': language,
            'feedback_sent_to': email_to,
            'feedback_message': message,
        }
        if not self.feedback_token:
            vals['feedback_token'] = uuid.uuid4().hex
        self.write(vals)

        template_xmlid = (
            'beta_project_customer_satisfaction.email_template_customer_feedback_ar'
            if language == 'ar' else
            'beta_project_customer_satisfaction.email_template_customer_feedback_en'
        )
        template = self.env.ref(template_xmlid, raise_if_not_found=False)
        if not template:
            raise UserError(_('Feedback email template not found.'))

        # feedback_email_from/feedback_email_to are read by the template's
        # own email_from/email_to mako expressions (see
        # data/email_template.xml) via `ctx.get(...)` - there is no
        # automatic fallback any more, so both must be provided here.
        template.with_context(
            feedback_email_from=email_from,
            feedback_email_to=email_to,
        ).send_mail(self.id, force_send=True)
        return True
