# -*- encoding: utf-8 -*-
##############################################################################
import time
from openerp import tools
from openerp.report import report_sxw
from datetime import datetime
from openerp.osv import fields, osv
from dateutil.relativedelta import relativedelta
from datetime import timedelta
import time 
from openerp import SUPERUSER_ID
from math import *
from pprint import pprint
class od_stock_aging_temp_view(osv.osv):
    _name = 'od.stock.aging.temp.view'
    _description = "od.stock.aging.temp.view"
    _auto = False
    _rec_name = 'product_id'
    _columns = {
        'product_id': fields.many2one('product.product','Product'),
        'location_id': fields.many2one('stock.location', 'Location',),
        'day_30sale': fields.float('30Day Sale'),
        'day_60sale': fields.float('60Day Sale'),
        'day_90sale': fields.float('90Day Sale'),
    }
    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)

#        cr.execute("""CREATE or REPLACE VIEW %s as (select foo.product_id||'-'||foo.location_id as id,foo.product_id,foo.location_id,COALESCE(sum(foo.day_30sale),0) as day_30sale,COALESCE(sum(foo.day_60sale),0) as day_60sale,COALESCE(sum(foo.day_90sale),0) as day_90sale 
#            from ( 
#            select pol.product_id ,pos.location_id, sum(pol.qty) as day_30sale,0 as day_60sale,0 as day_90sale from pos_order_line pol   
#            left join pos_order pos ON (pol.order_id = pos.id)  
#            where pos.date_order <= CURRENT_DATE AND pos.date_order > CURRENT_DATE - 30  
#            group by pol.product_id ,pos.location_id 
#            union  
#            select pol.product_id , pos.location_id,0 as day_30sale,sum(pol.qty) as day_60sale,0 as day_90sale from pos_order_line pol  
#            left join pos_order pos ON (pol.order_id = pos.id) 
#            where pos.date_order <= CURRENT_DATE - 30 AND pos.date_order > CURRENT_DATE - 60 group by pol.product_id ,pos.location_id 
#            union  
#            select pol.product_id , pos.location_id,0 as day_30sale,0 as day_60sale,sum(pol.qty) as day_90sale from pos_order_line pol  
#            left join pos_order pos ON (pol.order_id = pos.id) 
#            where pos.date_order <= CURRENT_DATE - 60 AND pos.date_order > CURRENT_DATE - 90 group by pol.product_id ,pos.location_id 
#            ) as foo group by foo.product_id ,foo.location_id)""" % (self._table,))



class report_orchid_stock_report(report_sxw.rml_parse):
    _name = "orchid_stock_report.report.orchid.stock.report"

    def set_context(self, objects, data, ids, report_type=None):
        return super(report_orchid_stock_report, self).set_context(objects, data, ids, report_type=report_type)


    def __init__(self, cr, uid, name, context):
        super(report_orchid_stock_report, self).__init__(cr, uid, name, context=context)

        self.localcontext.update({
            'time': time,
            'get_lines':self._get_lines,
        })

    def od_deduplicate(self,l):
        result = []
        for item in l :
            check = False
            # check item, is it exist in result yet (r_item)
            for r_item in result :
                if item['product_id'] == r_item['product_id'] :
                    # if found, add all key to r_item ( previous record)
                    check = True
                    lines = r_item['lines'] 
                    for line in item['lines']:
                        lines.append(line)
                    r_item['lines'] = lines
            if check == False :
                # if not found, add item to result (new record)
                result.append( item )
    
        return result
    
    def get_single_vals(self,data):
        for val in data:
            res = {'total_qty':0.0,'total_val':0.0,'0-30':0.0,'0-30val':0.0,'30-60':0.0,'30-60val':0.0,
                   '60-90':0.0,'60-90val':0.0,'90-120':0.0,'90-120val':0.0,'120-abv':0.0,'120-abvval':0.0,}
            for line in val.get('lines'):
                res['total_qty'] += line['qty']
                res['total_val'] += line['inventory_value']
                if line['age'] >0 and line['age'] <=30:
                    res['0-30'] += line['qty']
                    res['0-30val'] += line['inventory_value']
                elif line['age'] >30 and line['age'] <=60:
                    res['30-60'] += line['qty']
                    res['30-60val'] += line['inventory_value']
                elif line['age'] >60 and line['age'] <=90:
                    res['60-90'] += line['qty']
                    res['60-90val'] += line['inventory_value']
                elif line['age'] >90 and line['age'] <=120:
                    res['90-120'] += line['qty']
                    res['90-120val'] += line['inventory_value']
                elif line['age']>120:
                    res['120-abv'] += line['qty']
                    res['120-abvval'] += line['inventory_value']
            if res['total_qty'] !=0.0:
                val['res'] =res
        return data
                    
                

    def _get_lines(self,val):
        quant_obj = self.pool['stock.quant']
        age = val.get('age') or 0
        product_template_obj = self.pool.get('product.template')
        product_obj = self.pool.get('product.product')
        product_ids_from_category = []
        whereQry = ' ;'
        result = []
        res1 = []
        current_date_time = datetime.now().strftime('%Y-%m-%d')
        current_date_time = datetime.strptime(str(current_date_time),"%Y-%m-%d")
        current_date_time_31 = current_date_time - timedelta(days=31)

        current_date_time_31 = str(current_date_time_31)
        

        current_date_time_61 = current_date_time - timedelta(days=61)
        current_date_time_61 = str(current_date_time_61)

        current_date_time_91 = current_date_time - timedelta(days=91)
        current_date_time_91 = str(current_date_time_91)

        current_date_time_121 = current_date_time - timedelta(days=121)
        current_date_time_121 = str(current_date_time_121)

        current_date_time_151 = current_date_time - timedelta(days=151)
        current_date_time_151 = str(current_date_time_151)
         


        current_date_time_181 = current_date_time - timedelta(days=181)
        current_date_time_181 = str(current_date_time_181)


        location_dest_id_customer = self.pool.get('stock.location').search(self.cr,self.uid,[('usage','=','customer')])


        if val and val.get('categ_id'):
            
            template_ids = product_template_obj.search(self.cr, self.uid, [('categ_id','=',val.get('categ_id')[0])])
            for tmpl_ids in template_ids:
                product_ids = product_obj.search(self.cr, self.uid, [('product_tmpl_id','=',tmpl_ids)])
                product_ids_from_category = product_ids_from_category + product_ids
        if not val.get('product_id') and not val.get('location_id') and not val.get('categ_id'):
            self.cr.execute( "select stock_quant.product_id,stock_quant.in_date,stock_quant.location_id,EXTRACT(DAY FROM (current_timestamp - stock_quant.in_date)) AS age,sum(stock_quant.qty),stock_quant.cost as cost" \
                                        " FROM stock_quant INNER JOIN stock_location ON (stock_location.id = stock_quant.location_id) where date_part('day',age(current_timestamp,stock_quant.in_date)) >=%s and stock_location.usage='internal' group by stock_quant.product_id,stock_quant.in_date,stock_quant.location_id,stock_quant.cost",(age,))
            res1 = self.cr.fetchall()



        if not val.get('product_id') and not val.get('location_id') and val.get('categ_id'):
            if len(product_ids_from_category) == 1:

                self.cr.execute( "select stock_quant.product_id,stock_quant.in_date,stock_quant.location_id,EXTRACT(DAY FROM (current_timestamp - stock_quant.in_date)) AS age,sum(stock_quant.qty),stock_quant.cost as cost" \
                                        " FROM stock_quant INNER JOIN stock_location ON (stock_location.id = stock_quant.location_id) where EXTRACT(DAY FROM (current_timestamp - stock_quant.in_date)) >=%s and product_id = %s and stock_location.usage='internal' group by stock_quant.product_id,stock_quant.in_date,stock_quant.location_id,stock_quant.cost",(age,product_ids_from_category[0]),)
                res1 = self.cr.fetchall()
                
            else:
                x = (age,tuple(product_ids_from_category),)


                self.cr.execute( "select stock_quant.product_id,stock_quant.in_date,stock_quant.location_id,EXTRACT(DAY FROM (current_timestamp - stock_quant.in_date)) AS age,sum(stock_quant.qty),stock_quant.cost as cost" \
                                        " FROM stock_quant INNER JOIN stock_location ON (stock_location.id = stock_quant.location_id) where EXTRACT(DAY FROM (current_timestamp - stock_quant.in_date)) >=%s and product_id in %s and stock_location.usage='internal' group by stock_quant.product_id,stock_quant.in_date,stock_quant.location_id,stock_quant.cost",x)
                res1 = self.cr.fetchall()

        if not val.get('product_id') and val.get('location_id') and not val.get('categ_id'):

                self.cr.execute( "select product_id,in_date,location_id,EXTRACT(DAY FROM (current_timestamp - stock_quant.in_date)) as age,sum(qty),stock_quant.cost as cost" \
                                        " FROM stock_quant where EXTRACT(DAY FROM (current_timestamp - stock_quant.in_date)) >=%s and location_id = %s group by product_id,in_date,location_id,stock_quant.cost",(age,val.get('location_id')[0],))
                res1 = self.cr.fetchall()



        if not val.get('product_id') and val.get('location_id') and val.get('categ_id'):

            if len(product_ids_from_category) == 1:

                self.cr.execute( "select product_id,in_date,location_id,EXTRACT(DAY FROM (current_timestamp - stock_quant.in_date)) as age,sum(qty),stock_quant.cost as cost" \
                                        " FROM stock_quant where EXTRACT(DAY FROM (current_timestamp - stock_quant.in_date)) >=%s and product_id = %s and location_id =%s group by product_id,in_date,location_id,stock_quant.cost",(age,product_ids_from_category[0],val.get('location_id')[0],))
                res1 = self.cr.fetchall()
                
            else:
                x = (age,tuple(product_ids_from_category),val.get('location_id')[0],)
                self.cr.execute( "select product_id,in_date,location_id,EXTRACT(DAY FROM (current_timestamp - stock_quant.in_date)) as age,sum(qty),stock_quant.cost as cost" \
                                        " FROM stock_quant where EXTRACT(DAY FROM (current_timestamp - stock_quant.in_date)) >=%s and product_id in %s and location_id =%s group by product_id,in_date,stock_quant.lot_id,location_id,stock_quant.cost",x)
                res1 = self.cr.fetchall()


        if val.get('product_id') and not val.get('location_id') and not val.get('categ_id'):

            self.cr.execute( "select stock_quant.product_id,stock_quant.in_date,stock_quant.location_id,EXTRACT(DAY FROM (current_timestamp - stock_quant.in_date)) AS age,sum(stock_quant.qty),stock_quant.cost as cost" \
                                        " FROM stock_quant INNER JOIN stock_location ON (stock_location.id = stock_quant.location_id) where EXTRACT(DAY FROM (current_timestamp - stock_quant.in_date)) >=%s and product_id = %s and stock_location.usage='internal' group by stock_quant.product_id,stock_quant.in_date,stock_quant.lot_id,stock_quant.location_id,stock_quant.cost",(age,val.get('product_id')[0],))
            res1 = self.cr.fetchall()


        if val.get('product_id') and not val.get('location_id') and val.get('categ_id'):



            self.cr.execute( "select stock_quant.product_id,stock_quant.in_date,stock_quant.location_id,EXTRACT(DAY FROM (current_timestamp - stock_quant.in_date)) AS age,sum(stock_quant.qty),stock_quant.cost as cost" \
                                        " FROM stock_quant INNER JOIN stock_location ON (stock_location.id = stock_quant.location_id) where EXTRACT(DAY FROM (current_timestamp - stock_quant.in_date)) >=%s and product_id = %s and stock_location.usage='internal' group by stock_quant.product_id,stock_quant.in_date,stock_quant.lot_id,stock_quant.location_id,stock_quant.cost",(age,val.get('product_id')[0],))
            res1 = self.cr.fetchall()
        if val.get('product_id') and val.get('location_id') and not val.get('categ_id') or val.get('categ_id'):



            self.cr.execute( "select product_id,in_date,location_id,EXTRACT(DAY FROM (current_timestamp - stock_quant.in_date)) as age,sum(qty),stock_quant.cost as cost" \
                                        " FROM stock_quant where EXTRACT(DAY FROM (current_timestamp - stock_quant.in_date)) >=%s and product_id = %s and location_id=%s group by product_id,in_date,stock_quant.lot_id,location_id,stock_quant.cost",(age,val.get('product_id')[0],val.get('location_id')[0],))
            res1 = self.cr.fetchall()


        dict_data = []
        for data in res1:
            new_id = str(data[0])+'-'+str(data[2])


#            tem_ids = self.pool.get('od.stock.aging.temp.view').search(self.cr, SUPERUSER_ID,[('product_id','=',data[0]),('location_id','=',data[2])])
#            temp_view = self.pool.get('od.stock.aging.temp.view').browse(self.cr, SUPERUSER_ID,tem_ids)

#                
#            
            r = {
                'product_id':self.pool.get('product.product').browse(self.cr,self.uid,data[0]),
                'lines':[{
                        'in_date':data[1],
                        'location_id':self.pool.get('stock.location').browse(self.cr,self.uid,data[2]),
                        'age':data[3],
                        'qty':data[4],
                        'cost':data[5],
                        'inventory_value':data[4] * data[5],
                        'total_available_qty':data[4],
                       
                        }]
            }
            if r:
                dict_data.append(r)
        result = self.od_deduplicate(dict_data)
        pprint(result)
        single_val = self.get_single_vals(result)
        pprint(single_val)
        return single_val

class report_stock_aging(osv.AbstractModel):
    _name = 'report.orchid_stock_report.report_stock_aging'
    _inherit = 'report.abstract_report'
    _template = 'orchid_stock_report.report_stock_aging'
    _wrapped_report_class = report_orchid_stock_report

class report_stock_list(osv.AbstractModel):
    _name = 'report.orchid_stock_report.report_stock_list'
    _inherit = 'report.abstract_report'
    _template = 'orchid_stock_report.report_stock_list'
    _wrapped_report_class = report_orchid_stock_report

class report_stock_aging_detail(osv.AbstractModel):
    _name = 'report.orchid_stock_report.report_stock_aging_detail'
    _inherit = 'report.abstract_report'
    _template = 'orchid_stock_report.report_stock_aging_detail'
    _wrapped_report_class = report_orchid_stock_report

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

