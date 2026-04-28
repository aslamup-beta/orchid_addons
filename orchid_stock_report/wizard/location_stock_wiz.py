# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import fields, osv
class od_location_stock_wiz(osv.osv_memory):
    _name='od.location.stock.wiz'

    _columns = {
        'product_id': fields.many2one('product.product','Product'),
        'location_id': fields.many2one('stock.location','Location',domain=[('usage','=','internal')]),
        'categ_id': fields.many2one('product.category','Category'),
#        'company_id':
    }

    def open_quant(self,cr,uid,ids,context=None):
        if context is None:
            context = {}

        data = self.read(cr, uid, ids, context=context)[0]
        domain = []
        product_id = data['product_id']
        if product_id:
            domain.append(('product_id','=',product_id[0]))
        product_categ_id = data['categ_id'] 
        if product_categ_id:
            domain.append(('categ_id','child_of',[product_categ_id[0]]))   
        location_id = data['location_id']
        if location_id:
            domain.append(('location_id','=',location_id[0]))




        res = {
            'view_type': 'form',
            'view_mode': 'tree,graph',
            'domain':domain,
            'context':{'search_default_odlocation':1,'search_default_odqntlocation':1},
            'res_model': 'od.location.stock.view',
            'type': 'ir.actions.act_window',
        }
        return res
