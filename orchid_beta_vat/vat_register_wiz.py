from openerp import models, fields, api
from openerp.tools.translate import _
from openerp.exceptions import except_orm, Warning, RedirectWarning

import base64
import xlwt
from cStringIO import StringIO
from pprint import pprint
import logging
from openerp import tools
_logger = logging.getLogger(__name__)

# from openerp.osv import orm, fields
from datetime import datetime
# from cStringIO import StringIO
# import base64
# import xlwt
import time
from datetime import date
from datetime import datetime,date
from datetime import timedelta
# from pprint import pprint
# import logging
# from openerp import tools
# _logger = logging.getLogger(__name__)

# from openerp.exceptions import except_orm



class OrchidVatRegister(models.TransientModel):
	"""
	Orchid Tax Register Output.
	"""
	_name = 'orchid.vat.register'
	_description = 'Vat Register '

	from_date = fields.Date(string='From Date')
	to_date = fields.Date(string='To Date')

	# wizard_line1=fields.One2many('orchid.vat.register.line','wizard_line_id',string='line_id_')

	wizard_line=fields.Many2many('account.account',string='line_id')
	excel_file = fields.Binary(string='Dowload Report Excel',readonly="1")
	file_name = fields.Char(string='Excel File',readonly="1")


	def generate(self, cr, uid, ids, context=None):
		data={}
		pflag=0
		if context is None:
			context={}
		
		data = self.read(cr, uid, ids,['from_date','to_date','wizard_line'])[0]
		from_date=data.get('from_date')
		to_date=data.get('to_date')

		wizard_line_account_id=data.get('wizard_line')
		if from_date>to_date:
			raise Warning("From Date cannot be greater than To Date!!")

		inv_obj = self.pool['account.move.line']
		inv_datas  =inv_obj.search(cr,uid,[('account_id','in',wizard_line_account_id),('date','>=',from_date),('date','<=',to_date)])
		# print"qqqqq",inv_datas

		obj_ls=[]
		for res in inv_obj.browse(cr, uid, inv_datas,context=context):
			
			if res.journal_id and res.journal_id.type=='purchase':
				pflag=1

			if res.journal_id:
			
				obj_ls.append(res)

		return self.generate_excel(cr,uid,ids,data,obj_ls,inv_datas,pflag,context=None)




	def generate_excel(self,cr,uid,ids,data,obj_ls,inv_datas,pflag,context=None):


		vat_period=datetime.strptime(data.get('from_date'), '%Y-%m-%d').strftime('%d/%m/%Y')+"\tto\t"+datetime.strptime(data.get('to_date'), '%Y-%m-%d').strftime('%d/%m/%Y')
		

		report_date = date.today()
		report_date=report_date.strftime("%d/%m/%Y")

		workbook= xlwt.Workbook(encoding="UTF-8")

		#For coloured cells
		xlwt.add_palette_colour("custom_colour", 0x10)
		workbook.set_colour_RGB(0x10,178, 190, 181)

		filename='VatRegister.xls'
		sheet= workbook.add_sheet('VAT Report',cell_overwrite_ok=True)
		
		style_coloured = xlwt.easyxf('font:name calibri,height 200;align: horiz center, vert center;pattern: fore_colour custom_colour,pattern solid;borders:top_color black, bottom_color black, right_color black, left_color black, top thin,right thin,bottom thin,left thin;pattern: fore_colour custom_colour,pattern solid')
		style_title= xlwt.easyxf('font:name calibri,height 200;align: horiz left, vert center;')
		style_left= xlwt.easyxf('font:name calibri,height 200;align: horiz left, vert center;borders:top_color black, bottom_color black, right_color black, left_color black, top thin,right thin,bottom thin,left thin;')
		style_right=xlwt.easyxf('font:name calibri,height 200;align: horiz right, vert center;borders:top_color black, bottom_color black, right_color black, left_color black, top thin,right thin,bottom thin,left thin;')
		style_centre=xlwt.easyxf('align: horiz center, vert center;')
		style_filter=xlwt.easyxf('font:name calibri,height 200;align: horiz center, vert center;borders:top_color black, bottom_color black,top thin,bottom thin;pattern: fore_colour custom_colour,pattern solid')
		style_grey=xlwt.easyxf('pattern:fore_colour custom_colour,pattern solid')
		row = 0
		col =0

		title=['Input VAT','Report Date','Period from']

		

		sheet.write(row,col,title[0],style_title)
		col=8
		sheet.write(row,col,title[1],style_title)
		col=col+1
		sheet.write(row,col,report_date,style_left)
		col=0
		row=row+1	
		sheet.write(row,col,title[2],style_title)
		col=col+1
		sheet.write(row,col,vat_period,style_left)

		row=row+1
		col=0
		header=['Document Number','Description','Document Type','Document Date','Posting Date'
				,'Debit','Credit','Local Currency','Transaction Type','Tax Code']

		for i in range(0,10):
			sheet.write(row,col,header[i],style_coloured)
			col=col+1
		
		
		local_purchase=0
		foreign_purchase=0
		trans_d=0
		trans_c=0
		row=row+1
		total_credit=0
		total_debit=0
		for ls in obj_ls:
			for record in ls:
				data = {}
				flag=0
				
				data['doc_num']=record.move_id.name
				data['description']=record.partner_id.name
				data['doc_type']=record.journal_id.name
				data['doc_date']=record.date
				data['debit']=ls.debit
				data['credit']=ls.credit
				data['currency']=ls.company_id.currency_id.name
				
				data['trans_type']=ls.invoice.od_order_type_id.name
				# print 'ccccccc',data['trans_type']
				data['tax_code']=record.account_id.name
				# print 'aaaaaaaaa',data['tax_code']
				# print 'recorddddddddd',data
				if data['trans_type']==0:
					flag=1

				if data['trans_type']=='Local Purchase':
					
					trans_d=trans_d+data['debit']
					trans_c=trans_c+data['credit']
					local_purchase=trans_c-trans_d

				if data['trans_type']=='Foreign Purchase':
					
					trans_d=trans_d+data['debit']
					trans_c=trans_c+data['credit']
					foreign_purchase=trans_c-trans_d


				data['doc_date']=datetime.strptime(data['doc_date'], '%Y-%m-%d').strftime('%d/%m/%Y')

				# print 'dateeeeeeeee',data['doc_date']
				total_credit=total_credit+data['credit']
				# print 'creeeeeeeeee',total_credit
				total_debit=total_debit+data['debit']

				# print 'creeeeeeeeee',total_debit




				
				col=0
				sheet.write(row,col,data['doc_num'],style_right)
				col=col+1
				sheet.write(row,col,data['description'],style_left)
				col=col+1
				sheet.write(row,col,data['doc_type'],style_left)
				col=col+1
				sheet.write(row,col,data['doc_date'],style_right)
				col=col+1
				sheet.write(row,col,data['doc_date'],style_right)
				col=col+1
				sheet.write(row,col,data['debit'],style_right)
				col=col+1
				
				sheet.write(row,col,data['credit'],style_right)
				col=col+1
				sheet.write(row,col,data['currency'],style_left)
				col=col+1
				if flag==1:
					sheet.write(row,col,"",style_left)
				else:
					sheet.write(row,col,data['trans_type'],style_left)
				col=col+1
				sheet.write(row,col,data['tax_code'],style_left)
				row=row+1
		
		
	
	
		col=0		
		footer=['Total','Net Output Payable']

		footer1=['Local purchases','Foreign Purchases']

		sheet.write(row,col,footer[0],style_coloured)

		for col in range(1,5):
			sheet.write(row,col,"",style_coloured)

		col=5
		sheet.write(row,col,total_debit,style_coloured)
		col=col+1
		sheet.write(row,col,total_credit,style_coloured)

		for col in range(7,10):
			sheet.write(row,col,"",style_coloured)

		row=row+1
		temp=0
		temp=row
		col=0
		for col in range(0,5):
			sheet.write(row,col,"",style_filter)
		col=2
		sheet.write(row,col,footer[1],style_filter)
		if pflag==1:
			col=2
			row=row+1
			sheet.write(row,col,footer1[0],style_centre)
			row=row+1
			sheet.write(row,col,footer1[1],style_centre)

		row=temp
		col=5
		payable=total_debit-total_credit
		sheet.write(row,col,payable,style_coloured)

		if pflag==1:
			row=row+1
			col=5
			sheet.write(row,col,local_purchase,style_right)
			row=row+1
			sheet.write(row,col,foreign_purchase,style_right)

			

		fp = StringIO()
		workbook.save(fp)
		excel_file = base64.encodestring(fp.getvalue())
		self.write(cr,uid,ids,{'excel_file':excel_file,'file_name':filename})
		fp.close()
		return {
			  'view_type': 'form',
			  "view_mode": 'form',
			  'res_model': 'orchid.vat.register',
			  'res_id': ids[0],
			  'type': 'ir.actions.act_window',
			  'target': 'new'
			  }

	def build_filter(self, cr, uid, ids, context=None):
		data = self.read(cr, uid, ids,['from_date','to_date','wizard_line'])[0]
		return data
		
	def print_pdf(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		data = self.build_filter(cr,uid,ids,context=context)
		return self.pool['report'].get_action(cr,uid,[], 'orchid_beta_vat.report_vat_register_pdf',context=context, data=data)
		
		
	


# class Report_Vat_Register_pdf(models.AbstractModel):
# 	_name = 'report.orchid_beta_vat.report_vat_register_pdf'

# 	@api.multi
# 	def render_html(self, data=None):
# 		model = self.env.context.get('active_model')
# 		docs = self.env[model].browse(self.env.context.get('active_id'))
# 		report_date = date.today()
# 		report_date=report_date.strftime("%d/%m/%Y")
# 		# print "bbbbbbbbbbbbbbbbbbbbbbbbbbbbb",data['datas']['values']
# 		print "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",data
# 		report_obj = self.env['report']
# 		report = report_obj._get_report_from_name('orchid_beta_vat.report_vat_register_pdf')
# 		docargs = {
# 			'doc_ids': self.ids,
# 			'doc_model': model,
# 			'docs': docs,
# 			'lines': data['datas']['values'],
# 			'report_date': report_date,
# 			'local_purchase': data['transaction_type']['local_purchase'],
# 			'foreign_purchase': data['transaction_type']['foreign_purchase'],
# 			'vat_period': data['period']['vat_period'],
# 			'total_credit' : data['total']['total_credit'],
# 			'total_debit' : data['total']['total_debit'],
# 			}
# 		return report_obj.render('orchid_beta_vat.report_vat_register_pdf', docargs)




class OrchidVatRegisterOutputLine(models.TransientModel):

	_name="orchid.vat.register.line"
	_description="orchid.vat.register.line"


	wizard_line_id=fields.Many2one("orchid.vat.register",string="accounts_line")
	account_id=fields.Many2one('account.account',string="ACCOUNTS")

class OrchidAccountRelation(models.TransientModel):

	_name="account.relation"
	_description="account.relation"


	wizard_line_id=fields.Many2one("orchid.vat.register",string="accounts_line")
	account_id=fields.Many2one('account.account',string="ACCOUNTS")



class OrchidVatRegioutput(models.TransientModel):
 
	_name="orchid.vat.register.output"
	_description="orchid.vat.register.line"
 
	 
	wizard_line_id=fields.Many2one("orchid.vat.register",string="accounts_line")
	account_id=fields.Many2one('account.account',string="ACCOUNTS")
 
 
class OrchidVatReginput(models.TransientModel):
 
	_name="orchid.vat.register.input"
	_description="orchid.vat.register.line"
	 
	 
	wizard_line_id=fields.Many2one("orchid.vat.register",string="accounts_line")
	account_id=fields.Many2one('account.account',string="ACCOUNTS")
	 
 
class OrchidVatRegioutputLine(models.TransientModel):
 
	_name="orchid.vat.register.output.line"
	_description="orchid.vat.register.line"
	 
	 
	wizard_line_id=fields.Many2one("orchid.vat.register",string="accounts_line")
	account_id=fields.Many2one('account.account',string="ACCOUNTS")
	  
	  
 
class OrchidVatRegiinine(models.TransientModel):
 
	_name="orchid.vat.register.input.line"
	_description="orchid.vat.register.line"
	 
	 
	wizard_line_id=fields.Many2one("orchid.vat.register",string="accounts_line")
	account_id=fields.Many2one('account.account',string="ACCOUNTS")




	
		