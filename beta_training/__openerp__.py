# -*- coding: utf-8 -*-
{
    "name": "Beta Training",
    "version": "8.0.0.0",
    "author": "Nabeel",
    "category": "Human Resources",
    "description": """ Training Management""",
    "website": "http://www.betait.net",
    "depends": ['mail', 'hr', 'calendar'],
    'data': [
        'data/sequence.xml',
        'data/training_mail_template.xml',
        'security/ir.model.access.csv',
        'views/training_card_view.xml',
        'views/training_type_view.xml',
        'views/trainer_info_view.xml',
        'views/training_docs_view.xml',
        'views/trainer_contract_view.xml',
        'wizard/training_feedback_wiz.xml',
        'views/employee_training_contract_view.xml',
        'views/employee_idp_view.xml',
        'views/coop_trainee_view.xml',
        'views/employee_view.xml',

        'report/certificate_external_template.xml',
    ],
    'demo': [],
    'installable': True,

}
