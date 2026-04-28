from openerp import models, fields, api

class od_project_change_stages(models.Model):
	_name = 'od.project.change.stages'
	name = fields.Char('Stage')

class od_project_changes(models.Model):
	_name = 'od.project_changes'
	def od_get_company_id(self):
		return self.env.user.company_id
	company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
	name = fields.Char('Name',readonly=True)
	project_id = fields.Many2one('project.project','Project')
	# cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet')
	# new_cost_sheet_id = fields.Many2one('od.cost.sheet',string="New Cost Sheet",readonly=True)
	change_req_date = fields.Date('Request Date',required=True)
	change_appr_date = fields.Date('Approval Date',readonly=True)
	type_of_change = fields.Selection([('cost','Cost'),('scope','Schedule')],'Type Of Change',required=True)
	change_desc = fields.Text('Change Description')
	reason_for_change = fields.Text('Reason for Change')
	total_cost = fields.Float('Total Cost')
	profit = fields.Float('Profit')
	total_sale = fields.Float('Total Sale')
	profit_per = fields.Float('Profit Percentage')
	color = fields.Integer('Color Index')
	stage_id = fields.Many2one('od.project.change.stages','Stage')
	priority = fields.Selection([('0','Low'), ('1','Normal'), ('2','High')], 'Priority', select=True)
	state = fields.Selection([('new', 'New'),('awaiting', 'Awaiting Approval'),('in_progress', 'In Progress'),('closed','Closed')], string='State',default='new')

	# @api.one
    # def copy(self, default):
    #     default['name'] = self.name + " (Revision)"
    #     return super(Course, self).copy(default)


	@api.one
	def request_change(self):
		self.state = 'awaiting'
	@api.one
	def approve_change(self):
		if self.type_of_change == 'cost':
			default= {}
			cost_sheet_id= self.cost_sheet_id.copy(default)
			cost_sheet_id.status = 'active'
			cost_sheet_id.baseline_sheet_ref = self.cost_sheet_id.number
			self.new_cost_sheet_id = cost_sheet_id.id

		self.change_appr_date = fields.date.today()
		self.state = 'in_progress'

	@api.one
	def close(self):
		self.state = 'closed'

	# @api.onchange('project_id')
	# def onchange_project_id(self):
	# 	if self.project_id:
	# 		cost_sheet_id = self.project_id and self.project_id.od_cost_sheet_id and self.project_id.od_cost_sheet_id.id or False
	# 		if cost_sheet_id:
	# 			self.cost_sheet_id = cost_sheet_id


	@api.model
	def create(self,vals):
		vals['name'] = self.env['ir.sequence'].get('od.project.change.request') or '/'
		return super(od_project_changes,self).create(vals)



od_project_changes()

class project_project(models.Model):
	_inherit ='project.project'
# 	@api.one
# 	def _od_change_count(self):
# 			for obj in self:
# 				domain = [('project_id','=',obj.id)]
# 				change_req = self.env['od.project_changes'].search(domain)
# 				if change_req:
# 					self.od_change_req_count = len(change_req)
# 	od_change_req_count = fields.Integer(string='Change Request Count',compute='_od_change_count')

	def od_open_change_req(self,cr,uid,ids,context=None):
		project_id = ids[0]
		domain = [('project_id','=',project_id)]
		ctx ={'default_project_id':project_id}
		return {
            'domain': domain,
            'view_type': 'form',
            'view_mode': 'kanban,form,tree',
            'res_model': 'od.project_changes',
            'type': 'ir.actions.act_window',
            'context':ctx
        }
