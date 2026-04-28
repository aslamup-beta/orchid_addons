# -*- coding: utf-8 -*-
{
	'name': 'Orchid Beta Reports',
	'version': '1.0',
	'category': 'Reports',
	'sequence': 7,
	'summary': 'Orchid Beta Reports',
	'author': 'OrchidERP',
	'website': 'https://orchiderp.com',
	'depends': ['base'],
	'data': [
			'security/ir.model.access.csv',
            'views/mis_report.xml',
            'views/product_sale_analysis.xml',
			],
	'demo': [],
	'test': [],
	'installable': True,
	'auto_install': False,
	'application': True,

}
