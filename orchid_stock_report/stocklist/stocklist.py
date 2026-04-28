# # -*- coding: utf-8 -*-
# from openerp import fields,models,api,_
# from openerp.exceptions import Warning
# import xlwt
# from cStringIO import StringIO
# import base64
# # import pandas as pd
# 
# 
# class stockList(models.TransientModel):
#     _name = 'wiz.od.stock.list'
#     location_id = fields.Many2one('stock.location',string="Location")
#     excel_file=fields.Binary('Dowload Report Excel',readonly=True)
#     file_name = fields.Char('Excel File', size=64,readonly=True)
#     
#     
#     
#     def _get_data(self,location_id):
#         quant_pool = self.env['stock.quant']
#         quant_data_set = quant_pool.search([('location_id','child_of',[location_id])]) 
#         quant_data = [{'Product':x.product_id.name,'Description':x.product_id.description_sale or 'No Description','Quantity':x.qty,'Inventory Value':x.inventory_value,'Cost':x.inventory_value/x.qty,'Location':x.location_id.name} for x in quant_data_set]
#         return quant_data
#     @api.multi
#     def print_excel_report(self):
#         location_id = self.location_id and self.location_id.id or False
#         result = self._get_data(location_id)
#         dataframe= pd.DataFrame(result,columns=['Product','Description','Quantity','Cost','Inventory Value','Location'])
#         filename ='stocklist.xlsx'
#         writer = pd.ExcelWriter(filename, engine='xlsxwriter')
#         fp = StringIO()
#         writer.book.filename = fp
#         dataframe.to_excel(writer, sheet_name='Sheet1')
#         writer.save()
#         excel_file = base64.encodestring(fp.getvalue())
#         self.write({'excel_file':excel_file,'file_name':filename})
#         fp.close()
#         return {
#               'view_type': 'form',
#               "view_mode": 'form',
#               'res_model': 'wiz.od.stock.list',
#               'res_id': self.id,
#               'type': 'ir.actions.act_window',
#               'target': 'new'
#               }
#     
#     