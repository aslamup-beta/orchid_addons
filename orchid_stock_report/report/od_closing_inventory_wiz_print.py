# -*- encoding: utf-8 -*-
##############################################################################
import time
from openerp.osv import osv
from openerp.report import report_sxw
import datetime 
import dateutil.relativedelta 
from datetime import date, timedelta
import math

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
            for r_item in result :
                if item['product_id'] == r_item['product_id'] :
                    check = True
                    opening = r_item['detail']['opening'] +item['detail']['opening'] 
                    incoming = r_item['detail']['incoming'] +item['detail']['incoming'] 
                    outgoing = r_item['detail']['outgoing'] +item['detail']['outgoing'] 
                    closing = r_item['detail']['closing'] +item['detail']['closing'] 
                    r_item['detail']['opening'] = opening
                    r_item['detail']['incoming'] = incoming
                    r_item['detail']['outgoing'] = outgoing
                    r_item['detail']['closing'] = closing
            if check == False :
                result.append( item )
    
        return result



    def od_product_dict(self,data):
        res = []
        for val in data:
            res.append({'product_id':self.pool.get('product.product').browse(self.cr,self.uid,val[0]),'detail':{'opening':val[1],'incoming':val[2],'outgoing':val[3],'closing':val[4]}})
        return res


    

    def _get_lines(self,val):
        result = {}
        data = {}
        qry_data = []

        od_stock_move_analysis_obj = self.pool['od.stock.move.analysis']
        product_ids_from_category = []
        product_template_obj = self.pool['product.template']
        product_obj = self.pool['product.product']
        opening = []


        if val.get('categ_id'):
            template_ids = product_template_obj.search(self.cr, self.uid, [('categ_id','=',val.get('categ_id')[0])])
            for tmpl_ids in template_ids:
                product_ids = product_obj.search(self.cr, self.uid, [('product_tmpl_id','=',tmpl_ids)])
                product_ids_from_category = product_ids_from_category + product_ids

        #Lithin
        date_from = val.get('from_date')
        date_to =  val.get('to_date')
        stock_move_closing = self.pool['od.stock.move.analysis.for.closing.report']
        opening_domain = [('date','<',date_from)]
        new_ids = stock_move_closing.search(self.cr, self.uid, opening_domain)

        where_str = ''        

        if not val.get('product_id') and not val.get('location_id') and not product_ids_from_category:
            where_str = ''
        if not val.get('product_id') and not val.get('location_id') and product_ids_from_category:
            if len(product_ids_from_category) ==1:
                where_str = "where foo.product_id =  '"+str(product_ids_from_category[0])+"' "
            else:
                where_str = "where foo.product_id in "+str(tuple(product_ids_from_category))+ " "
        if not val.get('product_id') and val.get('location_id') and not product_ids_from_category:
            where_str = "where foo.location_dest_id = "+str(val.get('location_id')[0])+" "

        if not val.get('product_id') and val.get('location_id') and product_ids_from_category:
            if len(product_ids_from_category) ==1:
                where_str = "where foo.location_dest_id = '"+str(val.get('location_id')[0])+"' and foo.product_id = '"+str(product_ids_from_category[0])+"'  "
            else:
                where_str = "where foo.location_dest_id = '"+str(val.get('location_id')[0])+"' and foo.product_id in "+str(tuple(product_ids_from_category))+"  "

        if val.get('product_id') and not val.get('location_id') and not product_ids_from_category:
            where_str = "where foo.product_id = '"+str(val.get('product_id')[0])+"'  "

        if val.get('product_id') and val.get('location_id') and not product_ids_from_category:
            where_str = " where foo.product_id = '"+str(val.get('product_id')[0])+"' and foo.location_dest_id = '"+str(val.get('location_id')[0])+"' "



        qry = "select product_id, location_dest_id, sum(opening) as opening,sum(incoming_qty) as incoming_qty,sum(outgoing_qty)  as outgoing_qty , 0 as closing from \
(select product_id,location_dest_id,COALESCE(sum(in_qty),0)  as opening, 0 as incoming_qty, 0 as outgoing_qty \
from od_stock_move_analysis_for_closing_report  where date <  '"+str(val.get('from_date'))+"' \
group by product_id,location_dest_id \
union  \
select product_id,location_dest_id,0 as opening,COALESCE(sum(in_qty),0)  as incoming_qty, 0 as outgoing_qty  \
from od_stock_move_analysis_for_closing_report  where date >=  '"+str(val.get('from_date'))+"'  and  \
date <  '"+str(val.get('to_date'))+"'  \
group by product_id,location_dest_id \
union \
select product_id,location_dest_id,0 as opening, 0 as incoming_qty,COALESCE(sum(out_qty),0)  as outgoing_qty \
from od_stock_move_analysis_for_closing_report  where date >=  '"+str(val.get('from_date'))+"'  and date <  '"+str(val.get('to_date'))+"'  \
group by product_id,location_dest_id \
) as foo "+ where_str +"group by foo.product_id, foo.location_dest_id"
        self.cr.execute(qry)
        qry_data = self.cr.fetchall()


        main_data = []
        for tup in qry_data:
            stock_obj = self.pool['stock.location'].browse(self.cr, self.uid,tup[1])
            if stock_obj.usage == 'internal':
                lst = list(tup)
                lst[5] = (abs(lst[2]) + abs(lst[3])) -abs(lst[4])
                lst[1] = self.pool['stock.location'].browse(self.cr, self.uid,tup[1])
                lst[0] = self.pool['product.product'].browse(self.cr, self.uid,tup[0]) 
                tup = tuple(lst)
                main_data.append(tup)

        return main_data


class report_stock_closing(osv.AbstractModel):
    _name = 'report.orchid_stock_report.report_stock_closing'
    _inherit = 'report.abstract_report'
    _template = 'orchid_stock_report.report_stock_closing'
    _wrapped_report_class = report_orchid_stock_report


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

