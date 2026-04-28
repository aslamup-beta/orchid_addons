# -*- coding: utf-8 -*-
{
    'name': 'Orchid Purchase Discount',
    'version': '1.0',
    'category': 'Purchases',
    'sequence': 6,
    'summary': 'Purchase order lines with discounts',
    'description': """
Allow to enter item level discount in header and line level,It allows to define a discount per line in the purchase
orders.
    """,
    'author': 'OrchidERP (800ERP)',
    'images': [],
    'depends': [
        "stock",
        "purchase",
],
    'data': [
        "views/purchase_discount_view.xml",
        "views/account_invoice_view.xml",
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': True,

    'qweb': [],
    'auto_install': False,
}
