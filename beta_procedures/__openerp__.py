# -*- coding: utf-8 -*-
{
    "name" : "Beta Procedures",
    "version" : "0.2",
    "author": "Beta Information Technology",
    "category" : "Tools",
    "description": """ Beta Support""",
    "website": "http://www.betait.net",
    "depends": ['base','crm'],
    'data': [
            'security/ir.model.access.csv',
            'views/beta_procedure_view.xml',
            'views/cheque_print_view.xml',
            'views/crm_lead_view.xml',
            'views/beta_recruitment_view.xml',
            'views/finance_doc_view.xml',
            'views/mail_template.xml',
            'wizard/tax_report_wizard_view.xml',
            'reports/tax_report.xml'
            ], 
    'demo': [],
    'installable': True,
  
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: