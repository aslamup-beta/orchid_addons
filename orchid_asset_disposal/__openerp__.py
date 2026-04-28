# -*- coding: utf-8 -*-
{

	'name': 'Orchid Asset Disposal',
	'version': '1.0',
	'category': 'Production',
	'sequence': 1,
	'summary': 'Orchid Asset Disposal',
	'author': 'OrchidERP',
	'website': 'https://orchiderp.com',
	'depends': ['base','account_asset'],
	'data': [
#'security/ir.model.access.csv',
			'data/asset_disposal_sequence.xml',
			'views/asset_disposal.xml',
			 
			 
			 
			],
	'demo': [],
	'test': [],
	'installable': True,
	'auto_install': False,
	'application': True,

}
