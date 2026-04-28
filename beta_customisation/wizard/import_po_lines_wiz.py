# -*- coding: utf-8 -*-
from openerp import models, fields, api
import os
import csv
import tempfile
import base64
from openerp.exceptions import Warning

class wiz_import_export_po(models.TransientModel):

    _name = 'wiz.import.export.po'
    
    file_data = fields.Binary('File')
    file_name = fields.Char('File Name')
    

    def get_product_id(self):
        return True
    
    def transform_line_data(self,line):
        product_id=line.get('product_id')
        if product_id:
            part_no_name = self.get_product_id_from_name('product_product', product_id)
            line['product_id'] = part_no_name
        manufacture_id = line.get('od_pdt_brand_id')
        if manufacture_id:
            manufact_name = self.get_id_from_name('od_product_brand',manufacture_id)
            line['od_pdt_brand_id'] =manufact_name
        uom_id = line.get('product_uom')
        if uom_id:
            uom_name =self.get_id_from_name('product_uom',uom_id)
            line['product_uom'] = uom_name
        return line
        
    @api.multi
    def btn_import(self):
        context = self._context
        active_id = context.get('sheet_id')
        po = self.env['purchase.order']
        po = po.browse(active_id)
        if po.state not in ('draft', 'sent', 'bid'):
            raise Warning("Cannot Import Data - Purchase Order Already Submitted !!")
        model_line = context.get('active_model_line')
        model_line = model_line.split('.')
        model_line = "_".join(model_line)
        
        cr = self.env.cr
        file_name = self.file_name
        file_path = tempfile.gettempdir()+'/'+file_name
        data = self.file_data
        f = open(file_path,'wb') #temporary file object
        f.write(base64.b64decode(data))
        f.close() 
        archive = csv.DictReader(open(file_path))
        for line in archive:
            print line
            line = self.transform_line_data(line)
            line['order_id'] = active_id
            query1="INSERT INTO "
            query2= model_line
            query3="""(order_id, od_pdt_brand_id, product_id, name, product_qty,
            od_gross, product_uom, price_unit, state, date_planned
                    )   """
            query4 ="""
               VALUES (%(order_id)s,%(od_pdt_brand_id)s,%(product_id)s,%(name)s,%(product_qty)s,
               %(od_gross)s,%(product_uom)s, %(price_unit)s, %(state)s, %(date_planned)s);
            
              """
            query = query1 + query2 + query3 + query4
            cr.execute(query,line)
        return True
    
    
    def get_product_id_from_name(self,table_name,data_id):
        query1="select id from "
        query2= " where default_code='%s'"%data_id
        query = query1 + table_name + query2
        cr = self.env.cr 
        cr.execute(query)
        result=cr.fetchone() 
        result = result and result[0] or False
        if not result:
            raise Warning("No ID Found for %s"%data_id)
        return result
    
    
    def get_id_from_name(self,table_name,data_id):
        query1="select id from "
        query2= " where name='%s'"%data_id
        query = query1 + table_name + query2
        cr = self.env.cr 
        cr.execute(query)
        result=cr.fetchone() 
        result = result and result[0] or False
        if not result:
            raise Warning("No ID Found for %s"%data_id)
        return result
    
    
    