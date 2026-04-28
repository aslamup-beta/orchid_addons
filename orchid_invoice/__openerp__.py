# -*- coding: utf-8 -*-
{
    "name" : "Orchid Invoice",
    "version" : "0.1",
    "author": "OrchidERP",
    "category" : "Account Invoice",
    "description": """ Invoice due date calculation,when invoice create through delivery order and Invoice line cost updation """,
    "website": "http://www.orchiderp.com",
    "depends": ['account','sale','orchid_product','account_analytic_default'],
    'data': ['security/ir.model.access.csv',
            'account_invoice_view.xml',
#             'wizard/account_move.xml',
#             'report/account_invoice_report_view.xml',
             'report/od_invoice_report.xml'
            ], 
    'demo': [],
    'installable': True,
    'active': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
