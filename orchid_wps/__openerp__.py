# -*- encoding: utf-8 -*-

{
    'name': 'Orhid WPS export',
    'version': '0.1',
    'license': 'AGPL-3',
    'author': 'OrchidERP',
    'website': 'http://www.orchidinfosys.com',
    'category': 'Payroll',
    'summary': 'Will generate wps files',
    'description': """Generates wps files for the employee
    """,
    'depends': ['orchid_payroll' ,'orchid_hrms','report_xls'],
    'data': [
        'report/wps.xml',
        
    ],
}
