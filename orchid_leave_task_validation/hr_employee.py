from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning

class hr_employee(models.Model):
    _inherit = 'hr.employee'
    od_cost_centre_id = fields.Many2one('od.cost.centre',string='Cost Centre')
    od_branch_id = fields.Many2one('od.cost.branch',string='Branch')
    od_division_id = fields.Many2one('od.cost.division',string='Technology Unit')
    
    od_first_manager_id = fields.Many2one('res.users',string="First Approval Manager")
    od_second_manager_id = fields.Many2one('res.users',string="Second Approval Manager")