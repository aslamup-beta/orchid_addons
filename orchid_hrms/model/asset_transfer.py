from openerp import models, fields, api

class asset_transfer(models.Model):
	_name = 'asset.transfer'
	_description = 'Asset Transfer'
	name = fields.Char(default='/')
	od_current_emp_id = fields.Many2one('hr.employee','Current Holder')
	od_asset_id = fields.Many2one('account.asset.asset','Asset',required=True)
	od_trans_emp_id = fields.Many2one('hr.employee','Transfer To')
	od_date = fields.Date(string="Transfer Date",default=fields.Date.today)
	od_from_date = fields.Date(string="From Date")
	state = fields.Selection([('draft','Draft'),('transferred','Transferred')],'State',default='draft')
	od_type = fields.Selection([('issue','Issue Asset'),('transfer','Transfer Asset')],'Operation Type',default='transfer',required=True)

	def create(self, cr, uid, vals, context=None):
		if context is None:
			context = {}
		if vals.get('name', '/') == '/':
			vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'asset.transfer') or '/'
		return super(asset_transfer,self).create(cr, uid, vals, context=context)
	@api.onchange('od_asset_id')
	def onchange_asset_id(self):
		if self.od_asset_id:
			asset_id = self.od_asset_id and self.od_asset_id.id
			asset_facilitate_line = self.env['od.hr.employee.facilitates.line'].search([('asset_id','=',asset_id)])
			self.od_current_emp_id = asset_facilitate_line.employee_id and asset_facilitate_line.employee_id.id
			self.od_from_date =asset_facilitate_line.od_from_date
	@api.one
	def transfer_asset(self):
		cur_employee_id = self.od_current_emp_id and self.od_current_emp_id.id
		trans_emp_id = self.od_trans_emp_id and self.od_trans_emp_id.id
		asset_id = self.od_asset_id and self.od_asset_id.id
		date = self.od_date
		search_domain = [('asset_id','=',asset_id)]
		if self.od_current_emp_id:
			search_domain.append(('employee_id','=',cur_employee_id))
		asset_facilitate_line = self.env['od.hr.employee.facilitates.line'].search(search_domain)
		asset_facilitate_line.employee_id = trans_emp_id
		asset_facilitate_line.od_from_date = date
		self.state = 'transferred'
	@api.one
	def issue_asset(self):
		trans_emp_id = self.od_trans_emp_id and self.od_trans_emp_id.id
		asset_id = self.od_asset_id and self.od_asset_id.id
		date = self.od_date
		if trans_emp_id:
			self.env['od.hr.employee.facilitates.line'].create({
            'employee_id': trans_emp_id,
            'asset_id': asset_id,
            'od_from_date': date,
        })
			self.state = 'transferred'
		
asset_transfer()
