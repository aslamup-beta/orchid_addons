# -*- coding: utf-8 -*-
{
    "name": "Beta Technology Report",
    "version": "8.0.0.0",
    "author": "Beta Technology",
    "category": "Sale",
    "description": """ Sale Technology Report""",
    "website": "http://www.betait.net",
    "depends": ['crm', 'beta_customisation'],
    'data': [
        'data/vendor_rebate_email_template.xml',
        'security/ir.model.access.csv',
        'views/costsheet_view.xml',
        'views/vendor_rebate.xml',
        'wizard/sale_in_new_view.xml',
        'wizard/opp_revenue_rpt_new_view.xml',
        'wizard/sale_in_brand_rpt_view.xml',
        'wizard/opp_revenue_brand_rpt_view.xml',
    ],
    'demo': [],
    'installable': True,

}
