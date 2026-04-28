# -*- coding: utf-8 -*-
{
    "name" : "Orchid WMS Landed Costs",
    "version" : "0.1",
    "author": "OrchidERP",
    "category" : "purchase",
    "description": """Add tabs which shows a detailed and simple lines""",
    "website": "http://www.orchiderp.com",
    "depends": ['stock_landed_costs'],
    'data': [
            'wizard/cost_wiz_view.xml',
            'stock_landed_cost_data.xml',
            'stock_landed_costs_view.xml',
            'landed_cost_report.xml',
            'views/report_landed_cost_print.xml',
            ],
    'demo': [],
    'installable': True,
    'active': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
