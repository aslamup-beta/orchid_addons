# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class AuditTemplate(models.Model):
    _inherit = 'audit.template'

    type = fields.Selection(
        selection_add=[
            ('pm_ksa', 'Project Manager KSA'),
        ],
    )


class audit_sample(models.Model):
    _inherit = "audit.sample"

    cust_feedback_line = fields.One2many('cust.feedback.line', 'sample_id', string="Details")
    ksa_pm_closed_project_line = fields.One2many('ksa.pm.closed.project.line', 'sample_id', string="Details")
    type = fields.Selection(
        selection_add=[
            ('pm_ksa', 'Project Manager KSA'),
        ],
    )
    total_avg_score = fields.Float(string="Total Average Score")


class cust_feedback_line(models.Model):
    _name = "cust.feedback.line"
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


class KsaPmClosedProjectLine(models.Model):
    _name = "ksa.pm.closed.project.line"
    sample_id = fields.Many2one('audit.sample', string="Sample", ondelete="cascade")
    project_id = fields.Many2one('project.project', string="Project")
    day_process_score = fields.Float("5 Day Processing")
    project_tot_score = fields.Float("Total Score")
    inv_sch_score = fields.Float(string="Invoice Schedule")
    cost_ctrl_score = fields.Float("Cost Control")
    comp_score = fields.Float(string="PMO Compliance")
    sch_ctrl_score = fields.Float(string="Schedule Control")
    cust_feedback_score = fields.Float(string="Customer Satisfaction")
    tot_act_val_prj = fields.Float(string="Actual Value")
    tot_act_cost_prj = fields.Float(string="Actual Cost")
    tot_act_profit = fields.Float(string="Actual Profit")
    tot_act_profit_ratio = fields.Float(string="Actual Profit %")

    @api.multi
    def btn_open_project(self):
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'project.project',
            'res_id': self.project_id and self.project_id.id or False,
            'type': 'ir.actions.act_window',
            'target': 'new',

        }
