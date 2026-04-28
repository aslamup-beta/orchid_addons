from openerp import models, fields, api, _
from openerp.exceptions import Warning
class od_attachement(models.Model):
	_name = 'od.attachement'
	
	def od_get_company_id(self):
		return self.env.user.company_id
	
	company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
	name = fields.Char('Reference')
	model_name = fields.Char('Model Name',readonly=True)
	object_id = fields.Integer('Object ID')
	attach_file = fields.Binary('Attach File')
	issue_date = fields.Date('Issue Date')
	expiry_date = fields.Date('Expiry Date')
	attach_fname = fields.Char('Attach Filename')
	notify_user = fields.Many2one('res.users',string="Notify User")
	
	@api.model
	def create(self,vals):
		file_name = vals.get('attach_fname') or False
		if file_name:
			file_type = file_name.split('.')[-1]
			if file_type == "msg":
				raise Warning(_("Please convert msg files to PDF and then upload ! "))
		return super(od_attachement,self).create(vals)