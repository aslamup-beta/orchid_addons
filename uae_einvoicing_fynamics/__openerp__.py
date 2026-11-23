# -*- coding: utf-8 -*-
{
    'name': 'UAE E-Invoicing - Fynamics',
    'version': '8.0',
    'category': 'Invoicing',
    'summary': 'UAE e-invoicing integration with Fynamics',
    'description': '''
UAE e-invoicing integration for Odoo 8 Community.

Features:
- Fynamics OAuth2 client-credentials authentication
- Store Fynamics UUID and responses
- Check document status
- API logging
- Sandbox / Production configuration
    ''',
    'author': 'Aslam',
    'depends': ['account', 'beta_customisation'],
    'external_dependencies': {'python': ['requests']},
    'data': [
        'security/ir.model.access.csv',
        'views/account_invoice_view.xml',
        'views/cost_branch_view.xml',
        'views/res_partner_view.xml',
        'views/fynamics_log_view.xml',
    ],
    "website": "www.betait.net",
    'license': 'AGPL-3',
}