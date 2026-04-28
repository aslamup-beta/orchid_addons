from openerp import models, fields, api
from openerp.exceptions import Warning

import time
import datetime
from datetime import date
from dateutil.relativedelta import relativedelta

class od_payroll_transactions_line(models.Model):
    
    _inherit = 'od.payroll.transactions.line'
    
    def create(self, cr, uid, vals, context=None):
        # Automatically adding employee payroll transactions to corresponding periods of payroll transactions.
        if 'period_id' in vals:
            transaction_ids = self.pool.get('od.payroll.transactions').search(cr,uid,[('period_id','=', vals.get('period_id', False))])
            if transaction_ids:
                vals['payroll_transactions_id'] = transaction_ids[0]
        return super(od_payroll_transactions_line, self).create(cr, uid, vals, context=context)
    

class hr_contract(models.Model):
    _inherit ="hr.contract"
     
     
    @api.multi
    def set_duration_end_date(self):
        contract_ids= self.env['hr.contract'].search([('od_active','=',True)])
        today = datetime.date.today()
        for contract in contract_ids:
            company_id = self.env.user.company_id.id or False
            if company_id == 6 and contract.employee_id.country_id.id !=194:
                date_end = contract.employee_id
                date_end = datetime.datetime.strptime(date_end, "%Y-%m-%d").date()
                while (date_end < today):
                    dt = date_end + relativedelta(months=24)
                    contract.write({'od_limited':True,'date_end': dt})
                    date_end = dt
        return True
    
        