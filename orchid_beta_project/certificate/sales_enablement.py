from openerp import models, fields, api
from openerp.exceptions import Warning
class sale_enablement(models.Model):
	_name = 'sale.enablement'
	_order = 'id desc'
	
	
	@api.one
	def _get_score(self):
		score =0.0
		if self.state == 'done':
			score =100.0 
		self.score = score

	def get_default_user_id(self):
		user_id = self.env.uid 
		return user_id
	
	def od_get_company_id(self):
		return self.env.user.company_id
	
	
	company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
	
	
	user_id = fields.Many2one('res.users','Assigned By',default=get_default_user_id)
	name = fields.Char(string="Name of Session")
	certificate_id = fields.Many2one('employee.certificate',string="Certificate")
	date = fields.Date(string="Date")
	month = fields.Selection([(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
                          (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'), 
                          (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December'), ], 
                          string='Month')
	
	attendees_ids = fields.One2many('sale.enablement.attendees','sale_enab_id',string="Attendees")
	clear_attendees_ids = fields.One2many('sale.enablement.clear.attendees','sale_enab_id',string="Attendees")
	state =fields.Selection([('draft','Draft'),('in_progress','In Progress'),('done','Done')],string="Status",default='draft')
	od_division_id = fields.Many2one('od.cost.division',string="Technology Unit")
	score = fields.Float(string="Score",compute='_get_score')
	def get_employee(self,user_id):
		employee = self.env['hr.employee']
		employee_dat= employee.search([('user_id','=',user_id)],limit=1)
		return employee_dat	
		
	def update_employee_sess(self):
		month = self.month
		sale_enab = self.id
		
		
		for line in self.attendees_ids:
			user_id = line.user_id and line.user_id.id
			employee = self.sudo().get_employee(user_id)
			sess = 'sess'+str(month)
			sale_enab_id = 'sale_enab_id'+ str(month)
			second_sale_enab_id ='second_sale_enab_id'+ str(month)
			third_sale_enab_id ='third_sale_enab_id'+ str(month)
			sess_status='sess_status'+str(month)
			stat = line.status
			line.status = 'assigned'
			cert_id = 'cert_id'+str(month)
			if eval('employee.'+cert_id) and eval('employee.'+sale_enab_id) and eval('employee.'+second_sale_enab_id) and eval('employee.'+third_sale_enab_id):
				raise Warning("Already This Employee %s Assigned 3 Sessions and 1 Certificate,kindly Clear Before Assigning"%line.user_id.name)
				
			if eval('employee.'+sale_enab_id) and eval('employee.'+second_sale_enab_id) and eval('employee.'+third_sale_enab_id):
				raise Warning("Already This Employee %s Assigned Three Sessions,kindly Clear Before Assigning"%line.user_id.name)
			if eval('employee.'+sale_enab_id):
				sess = 'second_sess'+str(month)
				sale_enab_id = 'second_sale_enab_id'+ str(month)
				sess_status='second_sess_status'+str(month)
			if eval('employee.'+second_sale_enab_id):
				sess = 'third_sess'+str(month)
				sale_enab_id = 'third_sale_enab_id'+ str(month)
				sess_status='third_sess_status'+str(month)
				
			employee.write({sale_enab_id:sale_enab,sess:True,sess_status:stat})
			
	def od_send_mail(self,template,context):
		ir_model_data = self.env['ir.model.data']
		email_obj = self.pool.get('email.template')
		saudi_comp =6
		emp_company_id = self.company_id.id
		if emp_company_id == saudi_comp:
			template = template +'_saudi'
		template_id = ir_model_data.get_object_reference('orchid_beta_project', template)[1]
		crm_id = self.id
		email_obj.send_mail(self.env.cr, self.env.uid, template_id,crm_id,context)
		return True
	
	@api.one
	def send_mail_to_attendies(self):
		context = self.env.context
		attendies_email = []
		for line in self.attendees_ids:
			email = line.user_id and line.user_id.email
			attendies_email.append(email)
		#attendies_emails = ','.join(attendies_email)
		attendies_emails = str(",".join(filter(None,attendies_email)))
		context =  context.copy()
		context['attendies_emails'] = attendies_emails
		if attendies_emails:
			self.od_send_mail('od_sale_enablement_email_to_attendies',context=context)
		return True
		
	@api.one
	def btn_confirm(self):
		no_of_attendies = len(self.attendees_ids)
		if no_of_attendies < 3 :
			raise Warning("Atleast 3 users need to assigned before confirming a session")
		self.sudo().update_employee_sess()
		self.send_mail_to_attendies()
		self.write({'state':'in_progress'})
	
	@api.model
	def create(self,vals):
		res = super(sale_enablement, self).create(vals)
		res.btn_confirm()
		return res

	@api.one
	def btn_reset_draft(self):
		self.write({'state':'draft'})
	
	@api.one
	def btn_done(self):
		self.write({'state':'done'})
	
	@api.one
	def btn_reset_progress(self):
		self.write({'state':'in_progress'})

class sale_enab_certificate_attendees(models.Model):
	_name ='sale.enablement.attendees'
	sale_enab_id = fields.Many2one('sale.enablement',string="Sale Cert",ondelete="cascade")
	user_id = fields.Many2one('res.users',string="SAM")
	status = fields.Selection([('not_achieved','Not Achieved'),('assigned','Assigned'),('waiting','Waiting For Confirmation'),('achieved','Achieved')],string="Status",default='not_achieved')
	
		
	def get_employee(self,user_id):
		employee = self.env['hr.employee']
		employee_dat= employee.search([('user_id','=',user_id)],limit=1)
		return employee_dat
	@api.one 
	def btn_confirm(self):
		self.write({'status':'achieved'})
		user_id = self.user_id and self.user_id.id or False
		employee = self.sudo().get_employee(user_id)
		month = self.sale_enab_id and self.sale_enab_id.month
		sale_enab_id = self.sale_enab_id 
		cert_stat ='sess_status'+ str(month)
		sale_enab  = 'sale_enab_id'+str(month)
		second_sale_enab ='second_sale_enab_id' + str(month)
		second_cert_stat ='second_sess_status' + str(month)
		third_sale_enab ='third_sale_enab_id' + str(month)
		third_cert_stat ='third_sess_status' + str(month)
		if eval('employee.'+cert_stat) == 'waiting':
			if eval('employee.'+sale_enab) == sale_enab_id:
				employee.sudo().write({cert_stat:'achieved'})
		if eval('employee.'+second_cert_stat) =='waiting':
			if eval('employee.'+second_sale_enab) == sale_enab_id:
				employee.sudo().write({second_cert_stat:'achieved'})
		if eval('employee.'+third_cert_stat) =='waiting':
			if eval('employee.'+third_sale_enab) == sale_enab_id:
				employee.sudo().write({third_cert_stat:'achieved'})
		if sale_enab_id.state != 'done':
			sale_enab_id.write({'state': 'done'})
			
 
class sale_enab_clear_attendees(models.Model):
	_name ='sale.enablement.clear.attendees'
	sale_enab_id = fields.Many2one('sale.enablement',string="Sale Cert",ondelete="cascade")
	user_id = fields.Many2one('res.users',string="SAM")
	status = fields.Selection([('draft','Draft'),('cleared','Cleared')],string="Status",default='draft')
	clear_session = fields.Selection([('first','First'),('second','Second')],string="Clear Session",default='first',required=True)
		
	def get_employee(self,user_id):
		employee = self.env['hr.employee']
		employee_dat= employee.search([('user_id','=',user_id)],limit=1)
		return employee_dat
	@api.one 
	def btn_clear(self):
		
		
		self.write({'status':'cleared'})
		user_id = self.user_id and self.user_id.id or False
		employee = self.sudo().get_employee(user_id)
		month = self.sale_enab_id and self.sale_enab_id.month 
		
		
		sess_stat ='sess_status'+ str(month)
		sale_enab='sale_enab_id'+str(month)
		sess = 'sess'+str(month)
		if self.clear_session =='second':
			sess_stat ='second_sess_status'+ str(month)
			sale_enab='second_sale_enab_id'+str(month)
			sess = 'second_sess'+str(month)
		employee.sudo().write({sess:False,sess_stat:False,sale_enab:False})
		
	