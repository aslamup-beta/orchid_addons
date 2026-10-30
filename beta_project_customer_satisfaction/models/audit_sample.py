# -*- coding: utf-8 -*-
from openerp import models,fields,api,_
from openerp.exceptions import Warning


class audit_sample(models.Model):
    _inherit ="audit.sample"

    cust_feedback_line = fields.One2many('cust.feedback.line', 'sample_id', string="Details")



class cust_feedback_line(models.Model):
    _name ="cust.feedback.line"
    sample_id = fields.Many2one('audit.sample', string="Sample", ondelete="cascade")
    analytic_id = fields.Many2one('account.analytic.account', string="Analytic/Project")
    score = fields.Float("Score From Project")
    sale_value = fields.Float(string="Sale Value")
    sale_value_percent = fields.Float("%Sale Value")
    weight = fields.Float(string="Weight")
    form_wt = fields.Float(string="Form Weight")

    @api.multi
    def btn_open(self):
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.analytic.account',
            'res_id': self.analytic_id and self.analytic_id.id or False,
            'type': 'ir.actions.act_window',
            'target': 'new',

        }