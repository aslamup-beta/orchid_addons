# -*- coding: utf-8 -*-
{
    "name" : "Orchid Cheque Management",
    "version" : "0.1",
    "author": "OrchidERP",
    "category" : "Orchid",
    "description": """Orchid Cheque Management """,
    "website": ["http://www.orchiderp.com"],
#    "depends": ['account','orchid_acc_voucher','fleet','stock','orchid_cheque_management','orchid_acc_filters'],
    "depends": ["account_accountant"],
    "data" : [
            'cheque_management_seq.xml',
            'cheque_management_view.xml',
            'multiple_cheque_view.xml',
            'security/ir.model.access.csv',
            'cheque_management_report.xml',
            'account_voucher.xml'
    ],
    'css': [],
    'installable': True,
    'auto_install': False,
    'application': True,
} 
