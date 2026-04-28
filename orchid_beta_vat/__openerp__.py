# -*- coding: utf-8 -*-
{
    'name': "orchid_beta_vat",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Your Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        #'templates.xml',
        # 'vat_menu.xml',
        'vat_register_wiz.xml',
        # 'vat_input_pdf.xml',
        'print_pdf.xml',
        'vat_register_pdf.xml',
        # 
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo.xml',
    # ],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
