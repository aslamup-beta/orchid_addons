# -*- coding: utf-8 -*-
from openerp import SUPERUSER_ID
from openerp import tools
from openerp.osv import osv, fields, expression
from openerp.tools.translate import _

class product_template(osv.osv):
    _inherit = "product.template"
    _columns = {
        'name': fields.char('Name', required=True, translate=True, select=True),
    }
    # _sql_constraints = [
    #     ('product_name_uniq', 'unique (name)', 'Product Name should be unique!'),
    #     ('product_default_code_uniq', 'unique (default_code)', 'Internal Reference  should be unique!')
    #
    # ]
# class product_product(osv.osv):
#     _inherit = "product.product"
#     _sql_constraints = [
#     ('product_default_code_uniq', 'unique (default_code)', 'Internal Reference  should be unique!')
#     ]


class price_type(osv.osv):
    _inherit = "product.price.type"
    _columns = {
        'od_company_id': fields.many2one('res.company','Company',select=1)
    }
    _defaults = {
        'od_company_id': lambda s,cr,uid,c: s.pool.get('res.company')._company_default_get(cr, uid, 'product.price.type', context=c),
    }
