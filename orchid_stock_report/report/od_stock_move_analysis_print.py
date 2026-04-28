# -*- encoding: utf-8 -*-
##############################################################################
import time
from openerp.osv import osv
from openerp.report import report_sxw
import datetime 
import dateutil.relativedelta 
from datetime import date, timedelta
import math

class report_od_stock_move_analysis(report_sxw.rml_parse):
    _name = "orchid_stock_report.report.orchid.stock.move.analysis"


    def set_context(self, objects, data, ids, report_type=None):
        return super(report_od_stock_move_analysis, self).set_context(objects, data, ids, report_type=report_type)


    def __init__(self, cr, uid, name, context):
        super(report_od_stock_move_analysis, self).__init__(cr, uid, name, context=context)

        self.localcontext.update({
            'time': time,
            'get_data':self._get_data,
        })


    def _get_data(self,val):
        if val is None:
            val = {}
        #domain = [('location_id.usage','=','internal')]
        domain=[]
        history = self.pool.get('od.stock.history')
        if val.get('product_id'):
            domain.append(('product_id','=',val.get('product_id')[0]))
        history_ids = history.search(self.cr,self.uid,domain)
        print history_ids,"1"*88
        if history_ids:
            self.cr.execute("""select product_id, location_id, sum(opening) as opening, sum(incoming) as incoming, sum(outgoing) as outgoing,sum(closing) as closing from (
    select
     product_id as product_id, 
     location_id as location_id,
      sum(quantity) as opening, 
    0.0 as incoming,
    0.0 as outgoing,
    0.0 as closing
     from od_stock_history where id in %s and date <= %s  group by product_id, location_id
    Union 
    select
     product_id as product_id, 
     location_id as location_id,
      0.0 as opening, 
    sum(incoming_qty + transfer_in) as incoming,
    sum(outgoing_qty + transfer_out)  as outgoing,
    0.0 as closing
     from od_stock_history where id in %s and date between %s AND  %s  group by product_id, location_id
     union
     select
     product_id as product_id, 
     location_id as location_id,
      0.0 as opening, 
    0.0 as incoming,
    0.0 as outgoing,
    sum(quantity) as closing
     from od_stock_history where date <= %s and id in %s group by product_id, location_id
     ) as foo group by product_id, location_id""",(tuple(history_ids),val.get('date_from'),tuple(history_ids),val.get('date_from'),val.get('date_to'),val.get('date_to'),tuple(history_ids),))

        res = []
        
        for product_line in self.cr.dictfetchall():
            product_obj = self.pool.get('product.product')
            location_obj = self.pool.get('stock.location')
            product = product_obj.browse(self.cr, self.uid, product_line['product_id'])
            location = location_obj.browse(self.cr, self.uid, product_line['location_id'])
            product_line['product'] = '['+ str(product.default_code) +'] ' + str(product.name) or ''
            product_line['location'] = location.complete_name
            res.append(product_line)
        
        return res




class report_stock_move_analysis(osv.AbstractModel):
    _name = 'report.orchid_stock_report.report_stock_move_analysis'
    _inherit = 'report.abstract_report'
    _template = 'orchid_stock_report.report_stock_move_analysis'
    _wrapped_report_class = report_od_stock_move_analysis


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
