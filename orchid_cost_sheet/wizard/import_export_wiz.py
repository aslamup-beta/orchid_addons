# -*- coding: utf-8 -*-
from openerp import models, fields, api
import os
import csv
import tempfile
import base64
from openerp.exceptions import Warning
import csv, cStringIO
from PIL import Image

im = Image.new('RGB', (1920, 1080))

class wiz_import_export(models.TransientModel):

    _name = 'wiz.import.export'
    file_data = fields.Binary('File')
    file_name = fields.Char('File Name')
    export_file = fields.Binary('File')
    export_name = fields.Char('Export File Name')

    
    def get_product_id(self):
        return True
    
    
    
    
    def transform_line_data(self,line):
        part_no_id=line.get('part_no')
        if part_no_id:
            part_no_name = self.get_product_id_from_name('product_product', part_no_id)
            line['part_no'] = part_no_name
        manufacture_id = line.get('manufacture_id')
        if manufacture_id:
            manufact_name = self.get_id_from_name('od_product_brand',manufacture_id)
            line['manufacture_id'] =manufact_name
        types = line.get('types')
        if types:
            type_name =self.get_id_from_name('od_product_type',types)
            line['types'] = type_name
        uom_id = line.get('uom_id')
        if uom_id:
            uom_name =self.get_id_from_name('product_uom',uom_id)
            line['uom_id'] = uom_name
        return line
        
    
    @api.multi
    def btn_import(self):
        context = self._context
        active_id = context.get('sheet_id')
        cost_sheet = self.env['od.cost.sheet']
        cost_sheet = cost_sheet.browse(active_id)
        print "Active cost sheet .......",cost_sheet
        if cost_sheet.state not in ('draft', 'design_ready', 'submitted'):
            raise Warning("Cannot Import Data - Cost Sheet Already Submitted !!")
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
            line['cost_sheet_id'] = active_id
            print "line after transform",line
            query1="INSERT INTO "
            query2= model_line
            query3="""(cost_sheet_id,item_int,item,manufacture_id,part_no,name,types,qty,
            unit_cost_supplier_currency,uom_id
                    )   """
            query4 ="""
               VALUES (%(cost_sheet_id)s, %(item_int)s,
                    %(item)s,%(manufacture_id)s,%(part_no)s,%(name)s,%(types)s,%(qty)s,%(list_price)s,%(uom_id)s
                    );
            
              """
            query = query1 + query2 + query3 + query4
            cr.execute(query,line)
        return True
    

    
    def get_product_name_from_id(self,table_name,data_id):
        query1="select default_code from "
        query2= " where id=%s"%data_id
        query = query1 + table_name + query2
        cr = self.env.cr 
        cr.execute(query)
        result=cr.fetchone() 
        result = result and result[0] or ''
        return result
    
    
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
    
    
    
    def get_name_from_id(self,table_name,data_id):
        query1="select name from "
        query2= " where id=%s"%data_id
        query = query1 + table_name + query2
        cr = self.env.cr 
        cr.execute(query)
        result=cr.fetchone() 
        result = result and result[0] or ''
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
    
    
    
    def transform_data(self,data):
        for dat in data:
            dat['list_price'] = dat.pop('unit_cost_supplier_currency')
            part_no_id=dat.get('part_no')
            if part_no_id:
                part_no_name = self.get_product_name_from_id('product_product', part_no_id)
                dat['part_no'] = part_no_name
            manufacture_id = dat.get('manufacture_id')
            if manufacture_id:
                manufact_name = self.get_name_from_id('od_product_brand',manufacture_id)
                dat['manufacture_id'] =manufact_name
            types = dat.get('types')
            if types:
                type_name =self.get_name_from_id('od_product_type',types)
                dat['types'] = type_name
            uom_id = dat.get('uom_id')
            if uom_id:
                uom_name =self.get_name_from_id('product_uom',uom_id)
                dat['uom_id'] = uom_name    
               
        return data
    
    @api.multi
    def btn_export(self):
        context = self._context
        sheet_id = context.get('sheet_id')
        file_path = tempfile.gettempdir()+'/'+ 'data.csv'
        model_line =context.get('active_model_line')
        model_line = model_line.split('.')
        model_line = "_".join(model_line)
        query1 = "select item_int,item,manufacture_id,part_no,name,types,qty,unit_cost_supplier_currency,uom_id from "
        query2=model_line
        query3= " where cost_sheet_id=%s"%sheet_id
        query=query1 +query2 +query3
        cr = self.env.cr
        cr.execute(query)
        data = cr.dictfetchall()
        data = self.transform_data(data)
#         if not data:
#             data=[{'cost_sheet_id':sheet_id}]
        keys=['item_int','item','manufacture_id','part_no', 'name','qty', 'uom_id',   
               'list_price', 'types']
        print data,"x"*88
        
        with open(file_path, 'wb') as output_file:
            dict_writer = csv.DictWriter(output_file,fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(data)
        file = open(file_path,'rb')
        out = file.read()
        file.close()
        self.write({'export_file': base64.b64encode(out),'export_name':'Export.csv'})
        return {
               'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'wiz.import.export',
                'res_id':self.id,
                'type': 'ir.actions.act_window',
                'target': 'new',
            }
        
        
        
        
        
class wiz_import_export_ren(models.TransientModel):

    _name = 'wiz.import.export.ren'
    file_data = fields.Binary('File')
    file_name = fields.Char('File Name')
    export_file = fields.Binary('File')
    export_name = fields.Char('Export File Name')

    def transform_line_data(self,line):
        renewal_package_id=line.get('renewal_package_no')
        if renewal_package_id:
            part_no_name = self.get_product_id_from_name('product_product', renewal_package_id)
            line['renewal_package_no'] = part_no_name
        applicable_to=line.get('applicable_to')
        if applicable_to:
            part_no_name = self.get_product_id_from_name('product_product', applicable_to)
            line['applicable_to'] = part_no_name
        manufacture_id = line.get('manufacture_id')
        if manufacture_id:
            manufact_name = self.get_id_from_name('od_product_brand',manufacture_id)
            line['manufacture_id'] =manufact_name
        city_id = line.get('city_id')
        if city_id:
            city_name =self.get_id_from_name('res_country_state',city_id)
            line['city_id'] = city_name
        
        return line
    
    @api.multi
    def btn_import(self):
        context = self._context
        active_id = context.get('sheet_id')
        cost_sheet = self.env['od.cost.sheet']
        cost_sheet = cost_sheet.browse(active_id)
        if cost_sheet.state not in ('draft', 'design_ready', 'submitted'):
            raise Warning("Cannot Import Data - Cost Sheet Already Submitted !!")
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
            line['cost_sheet_id'] = active_id
            print "line after transform",line
            query1="INSERT INTO "
            query2= model_line
            query3="""(cost_sheet_id,item_int,item,manufacture_id,renewal_package_no,product_p_n,serial_no,city_id,
            location,start_date,expiry_date,notes
                    )   """
            query4 ="""
               VALUES (%(cost_sheet_id)s, %(item_int)s,
                    %(item)s,%(manufacture_id)s,%(renewal_package_no)s,%(applicable_to)s,%(serial_no)s,%(city_id)s,%(location)s,%(start_date)s,%(expiry_date)s,%(notes)s
                    );
            
              """
            query = query1 + query2 + query3 + query4
            cr.execute(query,line)
        return True
    
    def get_product_name_from_id(self,table_name,data_id):
        query1="select default_code from "
        query2= " where id=%s"%data_id
        query = query1 + table_name + query2
        cr = self.env.cr 
        cr.execute(query)
        result=cr.fetchone() 
        result = result and result[0] or ''
        return result
    
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
    
    def get_name_from_id(self,table_name,data_id):
        query1="select name from "
        query2= " where id=%s"%data_id
        query = query1 + table_name + query2
        cr = self.env.cr 
        cr.execute(query)
        result=cr.fetchone() 
        result = result and result[0] or ''
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
    
    def transform_data(self,data):
        for dat in data:
            
            renewal_package_no_id=dat.get('renewal_package_no')
            if renewal_package_no_id:
                part_no_name = self.get_product_name_from_id('product_product', renewal_package_no_id)
                dat['renewal_package_no'] = part_no_name 
            product_p_n_id=dat.pop('product_p_n')
            if product_p_n_id:
                part_no_name = self.get_product_name_from_id('product_product', product_p_n_id)
                dat['applicable_to'] = part_no_name
                
            manufacture_id = dat.get('manufacture_id')
            if manufacture_id:
                manufact_name = self.get_name_from_id('od_product_brand',manufacture_id)
                dat['manufacture_id'] =manufact_name
            city_id = dat.get('city_id')
            if city_id:
                city_name =self.get_name_from_id('res_country_state',city_id)
                dat['city_id'] = city_name
                
        return data
    
    @api.multi
    def btn_export(self):
        context = self._context
        sheet_id = context.get('sheet_id')
        file_path = tempfile.gettempdir()+'/'+ 'data.csv'
        model_line =context.get('active_model_line')
        model_line = model_line.split('.')
        model_line = "_".join(model_line)
        query1 = "select item_int,item,manufacture_id,renewal_package_no,product_p_n,serial_no,city_id,location,start_date,expiry_date,notes from "
        query2=model_line
        query3= " where cost_sheet_id=%s"%sheet_id
        query=query1 +query2 +query3
        cr = self.env.cr
        cr.execute(query)
        data = cr.dictfetchall()
        data = self.transform_data(data)
#         if not data:
#             data=[{'cost_sheet_id':sheet_id}]
        keys=['item_int','item','manufacture_id','renewal_package_no', 'applicable_to','serial_no', 'city_id',   
               'location', 'start_date', 'expiry_date', 'notes' ]
        with open(file_path, 'wb') as output_file:
            dict_writer = csv.DictWriter(output_file,fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(data)
        file = open(file_path,'rb')
        out = file.read()
        file.close()
        self.write({'export_file': base64.b64encode(out),'export_name':'Export.csv'})
        return {
               'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'wiz.import.export.ren',
                'res_id':self.id,
                'type': 'ir.actions.act_window',
                'target': 'new',
            }
    
    
