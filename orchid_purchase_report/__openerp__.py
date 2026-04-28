# -*- coding: utf-8 -*-
{
    "name" : "Orchid Purchase Reports",
    "version" : "0.1",
    "author": "OrchidERP",
    "category" : "Purchase Management",
    "description": """OrchidERP Purchase Reports""",
    "website": ["http://www.orchiderp.com"],
    "depends": ['purchase','orchid_report','orchid_product'],
    "data" : [
            'security/ir.model.access.csv',
            'report/purchase_report_view.xml',
            'report/od_po_register_report_view.xml',
            'menu_view.xml'
            ],
    'css': [],
}
