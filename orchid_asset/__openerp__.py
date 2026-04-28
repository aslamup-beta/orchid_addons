# -*- coding: utf-8 -*-
{

	'name': 'Orchid Asset',
	'version': '1.0',
	'category': 'Accounting And Finance',
	'summary': 'Orchid Asset',
	'author': 'OrchidERP',
	'website': 'https://orchiderp.com',
	'depends': ['base','account_asset','orchid_cost_centre'],
	'data': [
            'wizard/asset_report_view.xml',
            'views/report_asset_statement.xml',
            'report.xml',
			 'account_asset_view.xml',
			 'data/asset_seq.xml',
			],
	'demo': [],
	'test': [],
	'installable': True,
	'auto_install': False,
	'application': True,

}
