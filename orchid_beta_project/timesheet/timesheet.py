# -*- coding: utf-8 -*-

from openerp.osv import fields,osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import Warning
from pprint import pprint
from openerp import SUPERUSER_ID

class hr_analytic_timesheet(osv.osv):
    _inherit = "hr.analytic.timesheet"
    
    def od_get_hourly_rate(self,cr,uid,user_id,context=None):
        uid = SUPERUSER_ID
        employee_pool = self.pool['hr.employee']
        contract_pool = self.pool['hr.contract']
     
        employee_id = employee_pool.search(cr,SUPERUSER_ID,[('user_id','=',user_id)],limit=1)
        if not employee_id:
            raise Warning(" This User with User ID %s not Related to Any Employee ,Please Configure First"%user_id)
        contract_id = contract_pool.search(cr,uid,[('employee_id','=',employee_id),('od_active','=',True)],limit=1)
        if not contract_id:
            raise Warning("No Active Contract For this Employee")
        contract_obj = contract_pool.browse(cr,uid,contract_id)
        hourly_rate = contract_obj.od_hourly_rate
        return hourly_rate
    def on_change_user_id(self, cr, uid, ids, user_id, account_id=False, unit_amount=0):
        res = super(hr_analytic_timesheet, self).on_change_user_id(cr, SUPERUSER_ID, ids, user_id,account_id,unit_amount)
        hourly_rate = self.od_get_hourly_rate(cr, uid,user_id)
        if res.get('value'):
            res['value']['hourly_rate'] = hourly_rate
        return res
    
    
    def on_change_unit_amount(self, cr, uid, id, prod_id, unit_amount, company_id, unit=False, journal_id=False, context=None):
        res = super(hr_analytic_timesheet,self).on_change_unit_amount(cr, SUPERUSER_ID, id, prod_id, unit_amount, company_id, unit, journal_id, context)
        value  =  res.get('value',False)
    
        if value:
            amount = value.get('amount',0)
            res['value']['amount'] = 0.0
        return res
