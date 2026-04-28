# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
from openerp.tools.translate import _

class res_partner(osv.osv):
    _inherit = 'res.partner'
    _columns = {
                'name': fields.char('Name', required=True, select=True,translate=True)
                }
 
class account_journal(osv.osv):
    _inherit = 'account.journal'
    _columns = {
                'name': fields.char('Journal Name', required=True,translate=True)
                }   

class account_account(osv.osv):
    _inherit = 'account.account'
    _columns = {
               'name': fields.char('Name', required=True, select=True,translate=True),
                }  
class account_asset(osv.osv):
    _inherit = 'account.asset.asset'
    _columns = {
               'name': fields.char('Asset Name', required=True, readonly=True, states={'draft':[('readonly',False)]},translate=True)
                }   

class account_analytic_account(osv.osv):
    _inherit = 'account.analytic.account'
    _columns = {
                 'name': fields.char('Account/Contract Name', required=True, track_visibility='onchange',translate=True),
                }    


    
      

    
