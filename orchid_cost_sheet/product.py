from openerp.osv import fields, osv

class product_product(osv.osv):
    _inherit = 'product.product'
    def name_get(self, cr, uid, ids, context=None):
        res = []
        for line in self.browse(cr, uid, ids, context=context):
            name = line.name
            res.append((line.id, name))
        return res