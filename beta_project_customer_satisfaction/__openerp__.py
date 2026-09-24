# -*- coding: utf-8 -*-
{
    'name': 'Beta Project Customer Satisfaction',
    'version': '1.0',
    'category': 'Project Management',
    'summary': 'Single-language (AR or EN) 0-10 customer satisfaction rating for projects',
    'description': """
Beta Project Customer Satisfaction
====================================
Adds a 0-10 rating-bar customer satisfaction feedback loop directly on
Project - no separate feedback model, since a project only ever needs one
current rating/feedback/score:

- "Send Feedback Request" button in the Project form header opens a
  wizard asking for From email, To email, and Language (English or
  Arabic), then sends from the project model with those choices.
- The email renders in whichever single language was picked (not both
  side by side) and contains a clickable 0-10 gradient rating bar
  (red -> yellow -> green) with "Extremely Unsatisfied"/"Extremely
  Satisfied" labels above its ends, linking to a public, token-secured
  feedback page in the same language and design.
- Rating, Feedback text, Score (rating x 10) and the last-used Feedback
  Language are stored directly on project.project and shown in a
  "Feedback" tab on the Project form.
- Re-sending a request resets the previous answer so the project always
  reflects the latest feedback only.
- Feeds `account.analytic.account.cust_feedback_score`, used by this
  fork's existing KPI scoring (`_kpi_score`) and surfaced on the "Post
  Project Evaluation - KPI" page (via `orchid_beta_project`).

Note: this module depends on `website` in addition to project/mail/base,
because the public feedback page is served through Odoo's website/QWeb
http controller stack.
""",
    'author': 'Your Company',
    'website': 'https://www.example.com',
    # 'email_template' is required in this fork: the feedback email uses
    # the email.template model (confirmed from your earlier
    # "ParseError: mail.template" fix), which lives in that addon here
    # rather than being merged into 'mail'.
    'depends': ['project', 'mail', 'email_template', 'base', 'website','orchid_beta_project'],
    'data': [
        'security/ir.model.access.csv',
        'views/project_view.xml',
        'views/feedback_wizard_view.xml',
        'views/feedback_templates.xml',
        'data/email_template.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
