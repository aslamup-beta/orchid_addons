from openerp import models, fields, api, _

class account_analytic_account(models.Model):

    _inherit = "account.analytic.account"

    DOMAIN = [('parent_level0' ,'Parent Level View') ,('amc_view' ,'AMC View') ,('o_m_view' ,'O&M View')
              ,('credit' ,'Credit') ,('sup' ,'Supply') ,('imp' ,'Implementation')
              ,('sup_imp' ,'Supply & Implementation'),
              ('amc' ,'AMC') ,('o_m' ,'O&M') ,('cust_trn' ,'Customer Training') ,('poc' ,'(POC,Presales)'), ('comp_gen' ,'Company General -(Training,Labs,Trips,etc.)'), ('msp' ,'MSP')]

    od_type_of_project = fields.Selection(DOMAIN ,string="Type Of Project")

class project_project(models.Model):

    _inherit ='project.project'

    DOMAIN = [('parent_level0', 'Parent Level View'), ('amc_view', 'AMC View'), ('o_m_view', 'O&M View'),
              ('credit', 'Credit'), ('sup', 'Supply'), ('imp', 'Implementation'),
              ('sup_imp', 'Supply & Implementation'), ('amc', 'AMC'),
              ('o_m', 'O&M'), ('cust_trn', 'Customer Training'), ('poc', '(POC,Presales)'),
              ('comp_gen', 'Company General -(Training,Labs,Trips,etc.)'), ('msp' ,'MSP')]

    od_type_of_project = fields.Selection(DOMAIN, string="Type Of Project")