# -*- coding: utf-8 -*-
{
    "name": "Beta Human Resource",
    "version": "8.0.0.0",
    "author": "Beta Human Resource",
    "category": "HR",
    "description": """ Beta Human Resourcet""",
    "website": "http://www.betait.net",
    "depends": ['hr_expense', 'hr_contract', 'hr_holidays'],
    'data': [
        'security/ir.model.access.csv',
        'data/hr_doc_expiry_mails.xml',
        'views/payslip_view.xml',
        'views/employee_document_line_view.xml',
    ],
    'demo': [],
    'installable': True,

}
