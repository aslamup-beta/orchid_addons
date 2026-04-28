# -*- encoding: utf-8 -*-
{
    'name': 'Financial Journal reports',
    'version': '0.4',
    'license': 'AGPL-3',
    'author': 'OrchidERP',
    'category': 'Accounting & Finance',
    'description': """

Journal Reports
===============

This module adds journal reports by period and by fiscal year with
    - entries printed per move
    - option to group entries with same general account & VAT case
    - vat info per entry
    - vat summary

These reports are available in PDF and XLS format.


    """,
    'depends': [
        'account_voucher',
        'report_xls',
    ],
    'demo': [],
    'data': [
        'wizard/print_journal_wizard.xml',
    ],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
