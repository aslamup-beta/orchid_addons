# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
from openerp.tools.translate import _

class res_users(osv.osv):
	_inherit = 'res.users'
	_columns = {
		'allow_quick_create': fields.boolean('Allow Quick Create')
	}
