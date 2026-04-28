# -*- coding: utf-8 -*-
{
    'name': 'Orchid Bank Reconcile',
    'version': '1.0.1',
    'category': 'Accounting & Finance',
    'sequence': 8,
    'summary': 'Bank Reconcile',
    'description' : """
Bank Reconciliation and Accounting Management
    """,
    'author': 'OrchidERP',
    'website': 'http://www.orchiderp.com/',
    'images': [],
    'depends': ['account','orchid_acc_report'],
    'data': [
        'sequence.xml',
        'account_view.xml',
        'bank_reconciliation_view.xml'
    ],
    'demo': [

    ],
    'qweb' : [
        "static/src/xml/account_move_line_quickadd.xml",
        "static/src/xml/account_move_reconcilation.xml",

    ],
    'test': [
    ],
    'installable': True,
    'application': True,

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
