from openerp import models, fields, api

class od_implementation(models.Model):
	_name = 'od.implementation'

	def name_get(self, cr, uid, ids, context=None):
		if not ids:
			return []
		if isinstance(ids, (int, long)):
			ids = [ids]
		reads = self.read(cr, uid, ids, ['name', 'code'], context=context)
		res = []
		for record in reads:
			name = record['name']
			if record['code']:
				name ='[' + record['code'] + ']' + name
			res.append((record['id'], name))
		return res
	def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
		args = args or []
		if name:
			ids = self.search(cr, uid, [('code', 'ilike', name)] + args, limit=limit, context=context or {})
			if not ids:
				ids = self.search(cr, uid, [('name', operator, name)] + args, limit=limit, context=context or {})
		else:
			ids = self.search(cr, uid, args, limit=limit, context=context or {})
		return self.name_get(cr, uid, ids, context or {})
	
	@api.one
	@api.depends('optimistic','most_likely','pessimistic','challenge')
	def compute_duration(self):
		
		optimistic = self.optimistic
		most_likely = self.most_likely
		pessimistic = self.pessimistic
		challenge = self.challenge
		self.expected_act_duration = ((optimistic + 4 * most_likely + pessimistic)/6) * challenge
	
	

	


# 	display_name = fields.Char(string='Name', compute='_compute_display_name')
	
	
	def od_get_company_id(self):
		return self.env.user.company_id
	company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
	
	name = fields.Char('Name',required=True)
	project_phase = fields.Many2one('od.project.phase',string='Phase')
# 	category_id = fields.Many2one('od.product.group','Category')
# 	subcategory_id = fields.Many2one('od.product.sub.group','Sub category')
# 	category = fields.Many2one('od.project.category','Category')
# 	subcategory = fields.Many2one('od.project.sub.category','Sub category')
	
	categ_id  = fields.Many2one('od.product.sub.group','Category')
	sub_categ_id = fields.Many2one('od.project.sub.category','Sub category')
	code = fields.Char('Code')
	method = fields.Text('Method')
	check_list = fields.One2many('od.project.checklist','implement_id','Checklist')
	job_id = fields.Many2one('hr.job','Skill Set')
	optimistic = fields.Float('Optimistic')
	most_likely = fields.Float('Most Likely')
	pessimistic = fields.Float('Pessimistic')
	expected_act_duration = fields.Float(string='Expected Activity duration',compute='compute_duration',store=True)
	challenge = fields.Float(string='Challenge(0.1 - 1.0)',default=1.0)
	
# 	_sql_constraints = [
#         ('unique_code', 'UNIQUE (code)', 'Code must be unique!'),
# 		]
class od_project_checklist(models.Model):
	_name = 'od.project.checklist'
	def od_get_company_id(self):
		return self.env.user.company_id
	company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
	implement_id = fields.Many2one('od.implementation',string='Implementation Code')
	name = fields.Char(string="Checklist")