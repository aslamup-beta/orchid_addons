# -*- coding: utf-8 -*-
###############################################################################
#from datetime import datetime, timedelta
#import time
#from openerp.osv import fields, osv
#from openerp.tools.translate import _
#import openerp.addons.decimal_precision as dp


#class product_template(osv.osv):
#    _inherit = "product.template"

##    def od_update_od_valuation_cost(self, cr, uid, ids, context=None):
###Code to udpate the od_valuation_cost cost in product master
#        product_costing_real_ids = self.pool.get('product.product').search(cr,uid,[('cost_method','=','real')])
#        company = self.pool['res.users'].browse(cr, uid, uid,context=context).company_id
#        company_id = company and company.id

#        for obj in self.pool.get('product.product').browse(cr, uid,product_costing_real_ids):
#            qry = "select coalesce(sum(cost*qty)/sum(qty),0) from stock_quant qnt \
#left join stock_location loc on (qnt.location_id  = loc.id)  where  \
#qnt.product_id = %s and qnt.company_id = %s and  \
#loc.usage = 'internal' and qty > 0 "%(obj.id,company_id)
#            cr.execute(qry)
#            res = cr.fetchone()
#            avg_price = res and res[0]

#            new_price = obj.cost_method == 'real' and avg_price or obj.standard_price
#            self.pool.get('product.product').write(cr,uid,obj.id,{'standard_price':avg_price},context)
