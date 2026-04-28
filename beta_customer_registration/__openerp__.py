# -*- coding: utf-8 -*-
{
    "name": "Beta Customer Registration",
    "version": "8.0.0.0",
    "author": "Nabeel",
    "category": "Sale",
    "description": """ Customer Registration Process""",
    "website": "http://www.betait.net",
    "depends": ['sale', 'orchid_beta'],
    'data': [
        'data/customer_reg_email_template.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/customer_registration_view.xml',
    ],
    'demo': [],
    'installable': True,

}
