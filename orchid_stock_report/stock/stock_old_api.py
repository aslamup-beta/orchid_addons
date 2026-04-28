# -*- coding: utf-8 -*-
import openerp
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class stock_move(osv.osv):
    _inherit = "stock.move"
    _columns = {
#        'od_cost': fields.float('Cost', digits_compute=dp.get_precision('Product Price')),

        'location_id': fields.many2one('stock.location', 'Source Location', required=True, select=True, auto_join=True,
                                       states={'done': [('readonly', True)]}, domain=[('usage','!=','view')],help="Sets a location if you produce at a fixed location. This can be a partner location if you subcontract the manufacturing operations."),
        'location_dest_id': fields.many2one('stock.location', 'Destination Location', required=True, states={'done': [('readonly', True)]},domain=[('usage','!=','view')], select=True,
                                            auto_join=True, help="Location where the system will stock the finished products."),

    
    }

    #For update the cost to the new orchid cost field
#    def create(self, cr, uid, vals, context=None):
#        if vals and vals.get('price_unit') and vals.get('product_uom_qty'):
#            vals['od_cost'] = vals.get('price_unit') * vals.get('product_uom_qty')
#        return super(stock_move,self).create(cr, uid, vals, context=context)

#    #Update cost in stock move in any cases if the value is missing in the stock move
#    def write(self,cr,uid,ids,vals,context=None):

#        print "PPPPPPPPPPPPPPPPPPPPPPDDDDRRRR",context
#        for mv_obj in self.browse(cr,uid,ids,context=context):
#            if context is None:
#                context = {}
#            if context.get('active_model') == 'mrp.production' and vals and vals.get('state') and vals.get('state') == 'done':
#                print "$$$$\n\n$$$$$",mv_obj.production_id
#                production_id = mv_obj.production_id and mv_obj.production_id.id
#                if production_id:
#                    domain = [('raw_material_production_id','=',production_id)]
#                    raw_move_ids = self.search(cr, uid, domain)
#                    cost = 0.0
#                    for raw in self.browse(cr, uid, raw_move_ids,context=context):
#                        cost += (raw.product_id.standard_price or 0 )* raw.product_qty
#                    print "%%%",cost
#                    vals['od_cost'],vals['price_unit'] = cost,cost/(mv_obj.product_qty or 1)

#                print "ddd",vals
#            else:
#                if vals and vals.get('price_unit'):
#                    vals['od_cost'] = mv_obj.product_qty * (vals.get('price_unit') or 0.0)
#                if vals and vals.get('state') and vals.get('state') == 'done' and not mv_obj.od_cost:
#                    vals['od_cost'] = mv_obj.product_id.standard_price *  mv_obj.product_qty
#        return super(stock_move,self).write(cr,uid,ids, vals,context=context)
