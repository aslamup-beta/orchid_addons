# -*- coding: utf-8 -*-
{
    "name" : "Orchid Order Type",
    "version" : "0.1",
    "author": "OrchidERP",
    "category" : "Sales",
    "description": """OrchidERP Different Seq for sale order with sequencing""",
    "website": ["http://www.orchiderp.com"],
    "depends": ['sale','purchase','orchid_account_anglo_saxon'],
    "data" : [
              'sequence.xml',
                'order_view.xml',
                'sale/sale_view.xml',
                'stock/stock_view.xml',
                'purchase/purchase_view.xml',
                'stock/account_invoice_view.xml',
                'res_partner_view.xml'
            ],
    'css': [],
}
