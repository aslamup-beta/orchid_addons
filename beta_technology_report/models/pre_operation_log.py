from openerp import models, fields

class PreoprnLog(models.Model):
    _inherit = 'od.pre_opr.log'
    _order = 'id desc'

    partner_id = fields.Many2one('res.partner', string='Customer')

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    def create_pre_opn_log(self, preopr_cost):
        pre_op_log_obj = self.env['od.pre_opr.log']
        vals = {
            'opp_id': self.id,
            'partner_id': self.partner_id and self.partner_id.id or False,  # Added partner_id
            'cancel_date': fields.Date.today(),
            'cancel_by': self.env.user and self.env.user.id or False,
            'sam_id': self.user_id and self.user_id.id or False,
            'amount': preopr_cost,
        }
        log_id = pre_op_log_obj.create(vals)
        return log_id