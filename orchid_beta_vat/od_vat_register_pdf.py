# -*- encoding: utf-8 -*-
##############################################################################
import time
from openerp.osv import osv
from openerp.report import report_sxw
import datetime 
import dateutil.relativedelta 
from datetime import date, timedelta
import math

from openerp.exceptions import except_orm, Warning, RedirectWarning
from datetime import datetime
from datetime import date
from datetime import datetime,date
from datetime import timedelta

class report_od_vat_register_pdf(report_sxw.rml_parse):
	_name = "orchid_beta_vat.report.orchid_beta_vat.report_vat_register_pdf"


	def set_context(self, objects, data, ids, report_type=None):
		return super(report_od_vat_register_pdf, self).set_context(objects, data, ids, report_type=report_type)


	def __init__(self, cr, uid, name, context):
		super(report_od_vat_register_pdf, self).__init__(cr, uid, name, context=context)

		self.localcontext.update({
			'time': time,
			'get_data':self._get_data,
		})


	def _get_data(self,val):
		data={}
		pflag=0

		domain=[]

		# if context is None:
		#     context={}
		if val is None:
			val = {}

		# domain.append(('from_date','=',val.get('from_date')))
		# data = self.read(cr, uid, ids,['from_date','to_date','wizard_line'])[0]
		from_date=val.get('from_date')
		to_date=val.get('to_date')
		wizard_line_account_id=val.get('wizard_line')

		if from_date>to_date:
			raise Warning("From Date cannot be greater than To Date!!")
		inv_obj = self.pool['account.move.line']
		# inv_datas  =inv_obj.search(cr,uid,[('account_id','in',wizard_line_account_id),('date','>=',from_date),('date','<=',to_date)])
		inv_datas  =inv_obj.search(self.cr,self.uid,[('account_id','in',wizard_line_account_id),('date','>=',from_date),('date','<=',to_date)])


		obj_ls=[]


		for res in inv_obj.browse(self.cr,self.uid, inv_datas):

			if res.journal_id and res.journal_id.type=='purchase':
				pflag=1
			if res.journal_id:
				obj_ls.append(res)

		vat_period=datetime.strptime(from_date, '%Y-%m-%d').strftime('%d/%m/%Y')+"\tto\t"+datetime.strptime(to_date, '%Y-%m-%d').strftime('%d/%m/%Y')
	
		report_date = date.today()
		report_date=report_date.strftime("%d/%m/%Y")
		local_purchase=0
		foreign_purchase=0
		trans_d=0
		trans_c=0
		total_credit=0
		total_debit=0
		all_lines = []
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
				data['tax_code']=record.account_id.name
				
				if data['trans_type']=='Local Purchase':
					trans_d=trans_d+data['debit']
					trans_c=trans_c+data['credit']
					local_purchase=trans_c-trans_d

				if data['trans_type']=='Foreign Purchase':
					trans_d=trans_d+data['debit']
					trans_c=trans_c+data['credit']
					foreign_purchase=trans_c-trans_d
				if data['trans_type']==0:
					flag=1


				data['doc_date']=datetime.strptime(data['doc_date'], '%Y-%m-%d').strftime('%d/%m/%Y')
				total_credit=total_credit+data['credit']
				total_debit=total_debit+data['debit']

				
				
				all_lines.append(data)
				# all_lines.append(values)
				# all_lines.append(foreign_purchase)
				# all_lines.append(local_purchase)
				# all_lines.append(vat_period)
				# all_lines.append(report_date)
				# all_lines.append(total_debit)

			   

		# move_lines = {'filter': {'from': from_date, 'to': to_date}, 'period': {'vat_period': vat_period}, 'total': {'total_credit': total_credit,'total_debit':total_debit},
		#             'transaction_type': {'local_purchase': local_purchase,'foreign_purchase':foreign_purchase},'datas': {'values': all_lines}}  
		# print "all_linesssssssssssssssssssssssssssssssssss",all_lines
		# print "lineeeeeeeeeeeeeeeeeeeeeeeeeeeeeessssssssssssssssssssssssssssssssssssss",move_lines
		values={}
		values['total_credit']=total_credit
		values['total_debit']=total_debit
		values['vat_period']=vat_period
		values['report_date']=report_date
		values['local_purchase']=local_purchase
		values['foreign_purchase']=foreign_purchase
		values['all_lines']=all_lines
		return values




class report_stock_move_analysis(osv.AbstractModel):
	_name = 'report.orchid_beta_vat.report_vat_register_pdf'
	_inherit = 'report.abstract_report'
	_template = 'orchid_beta_vat.report_vat_register_pdf'
	_wrapped_report_class = report_od_vat_register_pdf


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
