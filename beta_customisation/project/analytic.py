# -*- coding: utf-8 -*-
from openerp import models, fields

class account_analytic_account(models.Model):
    _inherit = "account.analytic.account"
    
    od_cust_lpo_ref = fields.Char(string="Customer LPO Reference")
    od_cust_name = fields.Many2one('res.partner', string="Customer Name")
    od_proj_manager = fields.Many2one('res.users', string="Beta IT Project Manager")
    od_sales_ord_no = fields.Many2one('sale.order', string="Beta Sales Order Number")
    od_proj_desc = fields.Text(string="Project Description")
    od_gp_cm = fields.Text(string="Good Practices")
    od_prb_cm = fields.Text(string="Problems")
    od_imp_opp_cm = fields.Text(string="Improvement Opportunities")
    od_gp_tm = fields.Text(string="Good Practices")
    od_prb_tm = fields.Text(string="Problems")
    od_imp_opp_tm = fields.Text(string="Improvement Opportunities")
    od_gp_sm = fields.Text(string="Good Practices")
    od_prb_sm = fields.Text(string="Problems")
    od_imp_opp_sm = fields.Text(string="Improvement Opportunities")
    od_gp_qm = fields.Text(string="Good Practices")
    od_prb_qm = fields.Text(string="Problems")
    od_imp_opp_qm = fields.Text(string="Improvement Opportunities")
    od_gp_rm = fields.Text(string="Good Practices")
    od_prb_rm = fields.Text(string="Problems")
    od_imp_opp_rm = fields.Text(string="Improvement Opportunities")
    od_gp_com = fields.Text(string="Good Practices")
    od_prb_com = fields.Text(string="Problems")
    od_imp_opp_com = fields.Text(string="Improvement Opportunities")
    od_gp_pm = fields.Text(string="Good Practices")
    od_prb_pm = fields.Text(string="Problems")
    od_imp_opp_pm = fields.Text(string="Improvement Opportunities")
    od_gp_hm = fields.Text(string="Good Practices")
    od_prb_hm = fields.Text(string="Problems")
    od_imp_opp_hm = fields.Text(string="Improvement Opportunities")
    od_consumed_25 = fields.Boolean(string="Budget Consumed (25%)")
    od_consumed_50 = fields.Boolean(string="Budget Consumed (50%)")
    od_consumed_75 = fields.Boolean(string="Budget Consumed (75%)")
    od_consumed_90 = fields.Boolean(string="Budget Consumed (90%)")
    
    