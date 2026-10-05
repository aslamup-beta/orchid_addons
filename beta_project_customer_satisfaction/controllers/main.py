# -*- coding: utf-8 -*-
from openerp import http
from openerp.http import request


class CustomerFeedbackController(http.Controller):

    @http.route(['/feedback/feedback'], type='http', auth='public',
                website=True, csrf=False)
    def feedback_page(self, token=None, rating=None, **kwargs):
        """Public landing page reached from the rating-bar links in the
        email. `rating` (0-10), if present, comes pre-selected from the
        clicked bar segment but the customer can still change it before
        submitting."""
        Project = request.env['project.project'].sudo()
        project = Project.get_by_token(token)

        if not project:
            return request.render(
                'beta_project_customer_satisfaction.feedback_invalid', {})

        lang = project.feedback_language or 'en'
        thankyou_template = (
            'beta_project_customer_satisfaction.feedback_thankyou_ar'
            if lang == 'ar' else
            'beta_project_customer_satisfaction.feedback_thankyou_en'
        )
        form_template = (
            'beta_project_customer_satisfaction.feedback_form_ar'
            if lang == 'ar' else
            'beta_project_customer_satisfaction.feedback_form_en'
        )

        if project.is_submitted():
            # Already answered the current request - show the thank-you
            # page instead of letting the same link be replayed. A fresh
            # link (new token isn't needed, just a reset rating/text) is
            # issued whenever "Send Feedback Request" is clicked again.
            return request.render(thankyou_template, {'project': project})

        valid_ratings = [str(i) for i in range(0, 11)]
        values = {
            'project': project,
            'token': token,
            'selected_rating': rating if rating in valid_ratings else '',
        }
        return request.render(form_template, values)

    @http.route(['/feedback/submit'], type='http', auth='public',
                website=True, csrf=False, methods=['POST'])
    def feedback_submit(self, token=None, rating=None, feedback_text=None,
                         **kwargs):
        Project = request.env['project.project'].sudo()
        project = Project.get_by_token(token)

        if not project:
            return request.render(
                'beta_project_customer_satisfaction.feedback_invalid', {})

        project.action_submit_feedback(rating, feedback_text)

        lang = project.feedback_language or 'en'
        thankyou_template = (
            'beta_project_customer_satisfaction.feedback_thankyou_ar'
            if lang == 'ar' else
            'beta_project_customer_satisfaction.feedback_thankyou_en'
        )
        return request.render(thankyou_template, {'project': project})
