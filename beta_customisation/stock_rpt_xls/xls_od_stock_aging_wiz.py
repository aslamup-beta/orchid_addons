# -*- coding: utf-8 -*-
##############################################################################
from openerp import models, fields, api
from openerp.exceptions import Warning
from openerp import SUPERUSER_ID
from dateutil.relativedelta import relativedelta
from pprint import pprint
import time
import datetime
from datetime import date

class od_stock_aging_report_wizard_xls(models.TransientModel):
    _name = "od.stock.aging.report.wizard.xls"
    _description = "Stock Aging Report Wizard"
    
    def get_default_loc(self):
        loc_id = False
        company_id = self.env.user.company_id.id
        if company_id ==6:
            loc_id =23
        if company_id ==1:
            loc_id =12
        return loc_id
            
    
    
    
    product_id =fields.Many2one('product.product',string='Product')
    location_id=fields.Many2one('stock.location',string='Location',default=get_default_loc)
    categ_id =fields.Many2one('product.category',string='Product Category')
    detail =fields.Boolean('Detail')
    age=fields.Float('Age(Days)')
    stock_list=fields.Boolean('Stock List Only')
    wiz_line = fields.One2many('od.betax.stock.rpt.data','wiz_id',string="Wiz Line")
    period_length = fields.Selection([(30,'30'),(60,'60'),(90,'90')],string="Period Length",default=30)
    date = fields.Date(string="Date",default=fields.Date.context_today)
    compare = fields.Boolean(string="Compare")
    
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
    
    def get_res(self,kq):
        res ={'total_qty':0.0,'total_val':0.0}
        str1='q_'+str(kq)+'_'
        str2='v_'+str(kq)+'_'
        for i in range(1,8):
            s1 = str1+str(i)
            s2 = str2+str(i)
            res[s1] =0.0
            res[s2] =0.0
        return res
        
    
    
    def get_single_vals(self,data,kq):
        str1='q_'+str(kq)+'_'
        str2='v_'+str(kq)+'_'
        for val in data:
            
#             res = {'total_qty':0.0,'total_val':0.0,'0-30':0.0,'0-30val':0.0,'30-60':0.0,'30-60val':0.0,
#                    '60-90':0.0,'60-90val':0.0,'90-120':0.0,'90-120val':0.0,'120-150':0.0,'120-150val':0.0,'150-180':0.0,'150-180val':0.0,
#                    '180-abv':0.0,'180-abvval':0.0,}
            res = self.get_res(kq)
            for line in val.get('lines'):
                
                res['total_qty'] += line['qty']
                res['total_val'] += line['inventory_value']
                
                if line['age'] >=0 and line['age'] <=kq:
                    i =1
                    res[str1+str(i)] += line['qty']
                    res[str2+str(i)] += line['inventory_value']
                elif line['age'] >kq and line['age'] <=2*kq:
                    i =2
                    res[str1+str(i)] += line['qty']
                    res[str2+str(i)] += line['inventory_value']
                elif line['age'] >2*kq and line['age'] <=3*kq:
                    i =3
                    res[str1+str(i)] += line['qty']
                    res[str2+str(i)] += line['inventory_value']
                elif line['age'] >3*kq and line['age'] <=4*kq:
                    i =4
                    res[str1+str(i)] += line['qty']
                    res[str2+str(i)] += line['inventory_value']
                elif line['age'] >4*kq and line['age'] <=5*kq:
                    i =5
                    res[str1+str(i)] += line['qty']
                    res[str2+str(i)] += line['inventory_value']
                elif line['age'] >5*kq and line['age'] <=6*kq:
                    i =6
                    res[str1+str(i)] += line['qty']
                    res[str2+str(i)] += line['inventory_value']    
                elif line['age']>6*kq:
                    i =7
                    res[str1+str(i)] += line['qty']
                    res[str2+str(i)] += line['inventory_value']
            print res['total_qty'],"aaaa"
            if res['total_qty'] !=0.0:
                
                val['res'] =res
            
                
        return data
                    
    def process_data(self,data):
        result =[]
        cr = self.env.cr 
        for val in data:
            new_val = val.get('res') or {}
            product_id = val.get('product_id')
            new_val.update({'product_id':product_id})
            if self.compare:
                cr.execute("select sum(debit-credit) from account_move_line where product_id=%s and account_id=5233",(product_id,))
                res = cr.fetchall()
                print "res>>>>>>>>>>>>>>",res
                entry_value =res and res[0] and res[0][0] or 0.0
                new_val.update({'entry_value':entry_value})
            result.append((0,0,new_val))
        return result 

    def get_lines(self,val,period_length):
        age = val.get('age') or 0
        res1 = []
        cr = self.env.cr 
        uid = self.env.uid
        if val.get('location_id'):
                
                cr.execute( "select product_id,in_date,location_id,EXTRACT(DAY FROM (current_timestamp - stock_quant.in_date)) as age,sum(qty),stock_quant.cost as cost" \
                                        " FROM stock_quant where EXTRACT(DAY FROM (current_timestamp - stock_quant.in_date)) >=0 and location_id = %s group by product_id,in_date,location_id,stock_quant.cost",(val.get('location_id'),))
                res1 = cr.fetchall()

        if val.get('product_id'):
            cr.execute( "select product_id,in_date,location_id,EXTRACT(DAY FROM (current_timestamp - stock_quant.in_date)) as age,sum(qty),stock_quant.cost as cost" \
                                        " FROM stock_quant where EXTRACT(DAY FROM (current_timestamp - stock_quant.in_date)) >=0 and product_id = %s and location_id=%s group by product_id,in_date,stock_quant.lot_id,location_id,stock_quant.cost",(val.get('product_id'),val.get('location_id'),))
            
            res1 = cr.fetchall()
        if val.get('categ_id'):
            cr.execute('select id from product_template where categ_id=%s',(val.get('categ_id'),))
            product_temp_ids = cr.fetchall()
            pr_ids =[]
            for tmpl_ids in product_temp_ids:
                p_ids = self.pool.get('product.product').search(cr,uid, [('product_tmpl_id','=',tmpl_ids)])
                pr_ids += p_ids
            
            cr.execute( "select product_id,in_date,location_id,EXTRACT(DAY FROM (current_timestamp - stock_quant.in_date)) as age,sum(qty),stock_quant.cost as cost" \
                                        " FROM stock_quant where EXTRACT(DAY FROM (current_timestamp - stock_quant.in_date)) >=0 and product_id in %s and location_id=%s group by product_id,in_date,stock_quant.lot_id,location_id,stock_quant.cost",(tuple(pr_ids),val.get('location_id'),))
            
            res1 = cr.fetchall()
            
        dict_data = []
        for data in res1:
            r = {
                'product_id':data[0],
                'lines':[{
                        'in_date':data[1],
                        'location_id':data[2],
                        'age':data[3],
                        'qty':data[4],
                        'cost':data[5],
                        'inventory_value':data[4] * data[5],
                        'total_available_qty':data[4],
                       
                        }]
            }
            print "product>>>>>>>>>",data[0],data[4]
            if r and data[4]:
                dict_data.append(r)
        result = self.od_deduplicate(dict_data)
        
        single_val = self.get_single_vals(result,period_length)
        processed_data = self.process_data(single_val)
        return processed_data
    
    @api.multi
    def export_rpt(self):
        vals ={}
        product_id = self.product_id and self.product_id.id or False
        location_id = self.location_id and self.location_id.id or False
    
        categ_id = self.categ_id and self.categ_id.id or False
        period_length = self.period_length
       
        stock_list = self.stock_list
        compare = self.compare
        vals['location_id'] = location_id
        if product_id:
            vals['product_id'] = product_id 
            
        if categ_id:
            vals['categ_id'] = categ_id
        result = self.get_lines(vals,period_length)
        self.write({'wiz_line':result})
        wiz_id = self.id
        
        model_data = self.env['ir.model.data']
        period_length = self.period_length
        vw ='od_stock_aging_report_30tree_view'
        if period_length ==60:
            vw='od_stock_aging_report_60tree_view'
        
        if period_length == 90:
            vw = 'od_stock_aging_report_90tree_view'            
        
        if stock_list:
            vw = 'od_stock_aging_rpt_stock_list_only_tree_view'
            
        if stock_list and compare:
            vw = 'od_stock_aging_rpt_stock_list_plus_compare_tree_view'
        tree_view = model_data.get_object_reference( 'beta_customisation', vw)
        return {
            'domain': [('wiz_id','=',wiz_id)],
            'name': 'Stock Aging Report',
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(tree_view and tree_view[1] or False, 'tree')],
            'res_model': 'od.betax.stock.rpt.data',
            'type': 'ir.actions.act_window',
        }
        
    @api.multi
    def print_directly(self):
        vals ={}
        product_id = self.product_id and self.product_id.id or False
        location_id = self.location_id and self.location_id.id or False
    
        categ_id = self.categ_id and self.categ_id.id or False
        period_length = self.period_length
       
        stock_list = self.stock_list
        vals['location_id'] = location_id
        if product_id:
            vals['product_id'] = product_id 
            
        if categ_id:
            vals['categ_id'] = categ_id
        data = self.get_lines(vals,period_length)

        rpt_temp = 'report.od_stock_analysis_thirty'
        if period_length ==60:
            rpt_temp='report.od_stock_analysis_sixty'
        
        if period_length == 90:
            rpt_temp = 'report.od_stock_analysis_ninty'
            
        if stock_list:
            rpt_temp = 'report.od_stock_analysis_list_only'         

        rpt_pool = self.env['od.betax.stock.rpt.data']
        currency_id = self.env.user.company_id.currency_id.id
        
        vals = {
            'wiz_line':data,
            }
        
        rpt =self.create(vals)
        rpt_id =rpt.id
        ctx = self.env.context
        cr = self.env.cr
        uid = self.env.uid
        return self.pool['report'].get_action(cr, uid, [rpt_id], rpt_temp , context=ctx)


    

class wiz_project_rpt_data(models.TransientModel):
    _name = 'od.betax.stock.rpt.data'
    
    wiz_id = fields.Many2one('od.stock.aging.report.wizard.xls',string="Wizard")
    product_id = fields.Many2one('product.product',string="Code")
    name = fields.Text(string="Description",related='product_id.description')
    uom_id =fields.Many2one('product.uom',related="product_id.uom_id")
    categ_id = fields.Many2one('product.category',string='Product Category',related="product_id.categ_id", store=True)
    period_length = fields.Selection([(30,'30'),(60,'60'),(90,'90')],string="Period Length")
    q_30_1= fields.Float(string="0  -  30")
    q_30_2= fields.Float(string="30 -  60")
    q_30_3= fields.Float(string="60 -  90")
    q_30_4= fields.Float(string="90 - 120")
    q_30_5= fields.Float(string="120 - 150")
    q_30_6= fields.Float(string="150 - 180")
    q_30_7= fields.Float(string=" 180+  ")

    
    v_30_1= fields.Float(string=" - ",digits=(16,2))
    v_30_2= fields.Float(string=" - ",digits=(16,2))
    v_30_3= fields.Float(string=" - ",digits=(16,2))
    v_30_4= fields.Float(string=" - ",digits=(16,2))
    v_30_5= fields.Float(string=" - ",digits=(16,2))
    v_30_6= fields.Float(string=" - ",digits=(16,2))
    v_30_7= fields.Float(string=" - ",digits=(16,2))






    q_60_1= fields.Float(string="0  -  60")
    q_60_2= fields.Float(string="60 -  120")
    q_60_3= fields.Float(string="120 -  180")
    q_60_4= fields.Float(string="180 - 240")
    q_60_5= fields.Float(string="240 - 300")
    q_60_6= fields.Float(string="300 - 360")
    q_60_7= fields.Float(string=" 360+  ")

    
    v_60_1= fields.Float(string=" - ",digits=(16,2))
    v_60_2= fields.Float(string=" - ",digits=(16,2))
    v_60_3= fields.Float(string=" - ",digits=(16,2))
    v_60_4= fields.Float(string=" - ",digits=(16,2))
    v_60_5= fields.Float(string=" - ",digits=(16,2))
    v_60_6= fields.Float(string=" - ",digits=(16,2))
    v_60_7= fields.Float(string=" - ",digits=(16,2))
    
    
    q_90_1= fields.Float(string="0  -  90")
    q_90_2= fields.Float(string="90 -  180")
    q_90_3= fields.Float(string="180 -  270")
    q_90_4= fields.Float(string="270 - 360")
    q_90_5= fields.Float(string="360 - 450")
    q_90_6= fields.Float(string="450 - 540")
    q_90_7= fields.Float(string=" 540+  ")
    
    v_90_1= fields.Float(string=" - ",digits=(16,2))
    v_90_2= fields.Float(string=" - ",digits=(16,2))
    v_90_3= fields.Float(string=" - ",digits=(16,2))
    v_90_4= fields.Float(string=" - ",digits=(16,2))
    v_90_5= fields.Float(string=" - ",digits=(16,2))
    v_90_6= fields.Float(string=" - ",digits=(16,2))
    v_90_7= fields.Float(string=" - ",digits=(16,2))
    
    total_qty = fields.Float(string="Total Qty",digits=(16,2))
    total_val = fields.Float(string="Total Value",digits=(16,2))
    entry_value = fields.Float(string="Entry Value",digits=(16,2))
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidt - 