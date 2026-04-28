# -*- coding: utf-8 -*-
{
    'name': 'Orchid POC Tab',
    'version': '1.0',
    'category': 'Opportunity',
    'sequence': 6,
    
    'description': """
     Opportunity Poc tab
    """,
    'author': 'OrchidERP (800ERP)',
    'images': [],
    'depends': [
         "crm",'orchid_partner','orchid_product','orchid_attachement',
],
    'data': [
             'security/ir.model.access.csv',
#              'crm/crm_view.xml',
#              'crm/inquiry_type.xml',
        
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': True,

    'qweb': [],
    'auto_install': False,
}
