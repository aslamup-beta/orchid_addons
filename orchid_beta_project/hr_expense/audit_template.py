# -*- coding: utf-8 -*-
from openerp import models,fields,api,_
from openerp.exceptions import Warning
class audit_template(models.Model):
    _name ="audit.template"
    name = fields.Char(string="Name",required=True)
    type = fields.Selection([('post_sales','Post Sales'),('pre_sales','Pre-Sales Engineer'),
                             ('pre_sales_mgr','Pre-Sales Manager'),('sales_acc_mgr','Sales Account Manager'),
                             ('service_sale_spl','Service Sale Specialist'),
                             ('sm','Sales Manager'),
                             ('bdm','BDM'), ('bdm_sec','BDM-SEC'),('bdm_net','BDM-NET-DC'),('bdm_dc','BDM-DC'),('bdm_ksa','BDM-KSA'),('ttl','Technical Team Leader'),
                             ('pm','Project Manager'),('pmo','PMO Director'),('pdm','Project Department Manager'),
                             ('tc','Technology Consultant'),('tum','Technology Unit Manager'),('sde','Service Desk Engineer'),('sdm','Service Desk Manager'),
                             ('hoo','Head Of Operation'),
                             ('sde_ksa','Service Desk Engineer KSA'),
                             ('po_officer','Purchase Officer'),
                             
                             ],string="Type",required=True)
    
    desc  = fields.Text(string="Description")
    calc = fields.Text(string="Calculation Method")
    data_model = fields.Char(string="Data Model")
    bdm_ksa_line = fields.One2many('audit.temp.bdm.ksa','audit_temp_id',string="BDM KSA Details")
    
class audit_temp_bdm_ksa(models.Model):
    _name ='audit.temp.bdm.ksa'
    audit_temp_id = fields.Many2one('audit.template',string="Audit Template")
    branch_id = fields.Many2one('od.cost.branch',string="Branch")
    gp_target = fields.Float(string="GP Target")
    month_incent = fields.Float(string="Monthly Incentive")
    
    
    
