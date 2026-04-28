# -*- coding: utf-8 -*-
{
    "name" : "Orchid Leave Task Validation",
    "version" : "0.1",
    "author": "OrchidERP",
    "category" : "Hrms",
    "description": """Leave Task Validation  """,
    "website": "http://www.orchiderp.com",
    "depends": ['orchid_hrms'],
    'data': [
             'security/ir.model.access.csv',
           'hr_employee_view.xml',
            'hr_holidays_view.xml',
            ],
    'demo': [],
    'installable': True,
    'application': True,
    'images':[],
    'qweb':[],
    'active': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
