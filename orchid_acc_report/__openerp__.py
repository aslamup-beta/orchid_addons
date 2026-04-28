# -*- coding: utf-8 -*-
{
    "name" : "Orchid Accounting Reports",
    "version" : "0.1",
    "author": "OrchidERP",
    "category" : "Accounting AND Finance",
    "description": """OrchidERP Accounting Reports""",
    "website": "http://www.orchiderp.com",
    "depends": ['report_webkit','orchid_report',
#'orchid_cost_centre'
],
    "data" : [
            'account_view.xml',
            'wizard/account_report_partner_ledger_view.xml',
            'wizard/account_report_general_ledger_view.xml',
            'wizard/account_report_account_balance_view.xml',

            'wizard/accounting_financial_report_view.xml',
           'wizard/account_report_aged_partner_balance_view.xml',
            'views/report_orchid_trend.xml',
            'report.xml',
            'wizard/od_trend_report_view.xml',
            
            ],
    'css': [],
}
