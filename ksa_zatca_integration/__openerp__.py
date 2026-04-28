# -*- coding: utf-8 -*-
{
    'name': "KSA Zatca Phase-2",
    'summary': """
        Phase-2 of ZATCA e-Invoicing(Fatoorah): Integration Phase""",
    'description': """
        Phase-2 of ZATCA e-Invoicing(Fatoorah): Integration Phase
    """,
    'live_test_url': 'https://youtu.be/_M3PtOBzeC4',
    "author": "Aslam",
    "website": "www.betait.net",
    'license': 'AGPL-3',
     'images': ['static/description/cover.png'],
    'category': 'Invoicing',
    'version': '8.1',
    'price': 1500, 'currency': 'USD',
    'depends': ['account', 'sale', 'purchase', 'beta_account_debitnote'],
    'external_dependencies': {
        'python': ['cryptography', 'lxml', 'qrcode']
    },
    'data': [
        'data/data.xml',
        'views/res_company.xml',
        'views/account_invoice.xml',
        'views/account_tax.xml',
#         'reports/account_invoice.xml',
#         'reports/res_partner.xml',
#         'reports/res_company.xml',
#         'reports/sale_order_report.xml',
#         'reports/e_invoicing_b2c.xml',
#         'reports/report.xml',
    ],
}
