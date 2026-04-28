# -*- coding: utf-8 -*-
{
    'name' : 'Sale to Purchase Order',
    'version': '1.0',
    'author': 'OrchidERP',
    'website': 'http://www.orchiderp.com/',
    'depends' : ["sale", "purchase",'purchase_requisition'],
    'category' : 'Sale Management',
    'description': '''Create PO from the SO provided the Informations
    ''',
    'init_xml' : [],
    'demo_xml' : [],
    'update_xml' : ['wizard/generate_purchase_order_wizard.xml',
                    'sale_view.xml'],
    'active': False,
    'installable': True
}
