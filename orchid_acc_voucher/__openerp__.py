# -*- coding: utf-8 -*-
{
    "name" : "Orchid Voucher Entry",
    "version" : "0.1",
    "author": ["Orchid GL Report", "OrchidERP" ],
    "category" : "Accounting & Finance",
    "description": """OrchidERP for Voucher Entry """,
    "website": ["http://www.orchiderp.com"],
    "depends": ['account_accountant','account','account_asset','product'],
    "data" : [#'account_voucher_view.xml'
            'extra_reports_reports.xml',
            'account_view.xml',
            'general_journal_view.xml',
            'inventory_journal_view.xml',
            'asset_journal_view.xml'
            ],
}
