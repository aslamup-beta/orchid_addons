# -*- coding: utf-8 -*-
{
    "name" : "Beta Invoice",
    "version" : "0.1",
    "author": "Jamshid K",
    "category" : "Account Invoice",
    "description": """ Invoice Customization""",
    "website": "http://www.betait.net",
    "depends": ['base','account','orchid_cost_sheet','orchid_cost_centre'],
    'data': [
            'security/ir.model.access.csv',
            'account/invoice_view.xml',
            'models/transfer_acc_view.xml',
            'models/replace_acc_view.xml',
            #'customer_aging/aging_view.xml',
            'customer_aging/customer_aging_view.xml',
#             'customer_aging/cust_aging_high_level_view.xml',
            'supplier_aging/supplier_aging_view.xml',
            'wip_aging/wip_aging_view.xml',
            'unbilled_aging/unbilled_aging_view.xml',
             #'wizard/transfer.xml',
            ], 
    'demo': [],
    'installable': True,
  
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
