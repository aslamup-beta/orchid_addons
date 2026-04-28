# -*- coding: utf-8 -*-

import time
from datetime import datetime
from dateutil import relativedelta

from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, timedelta
import unicodedata
from openerp import SUPERUSER_ID
from openerp.exceptions import Warning
#import dateutil.relativedelta 

class hr_payslip_employees(osv.osv_memory):
    _inherit = 'hr.payslip.employees'

    def compute_sheet(self, cr, uid, ids, context=None):
        emp_pool = self.pool.get('hr.employee')
        slip_pool = self.pool.get('hr.payslip')
        run_pool = self.pool.get('hr.payslip.run')
        slip_ids = []
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, context=context)[0]
        self_obj = self.browse(cr,uid,ids,context)
        run_data = {}
        if context and context.get('active_id', False):
            run_data = run_pool.read(cr, uid, context['active_id'], ['date_start', 'date_end', 'credit_note','xo_period_id','xo_total_no_of_days','journal_id','od_cut_days'])
        from_date =  self_obj.date_from or run_data.get('date_start', False) 
        to_date = self_obj.date_to or run_data.get('date_end', False)
        credit_note = self_obj.credit_note
        od_cut_days = self_obj.od_cut or run_data.get('od_cut_days',False) or 0
        prev_month_cut_day = od_cut_days + 1
        if od_cut_days < 0:
            raise osv.except_osv(_('Error!'),_('cut off days should not less than zero'))
        
        if od_cut_days==0:
        
            journal_id = self_obj.journal_id and self_obj.journal_id.id 
            xo_period_id = self_obj.xo_period_id and self_obj.xo_period_id.id 
            xo_total_no_of_days = self_obj.xo_total_no_of_days
            if not data['employee_ids']:
                raise Warning("You must select employee(s) to generate payslip(s).")
            for emp in emp_pool.browse(cr, SUPERUSER_ID, data['employee_ids'], context=context):
                context['od_cut_days'] = 0
                
                period_change_data = slip_pool.onchange_payslip_period(cr, uid, [],emp.id, xo_period_id,od_cut_days,context=context)
                f_d= period_change_data['value']['date_from']
                t_d= period_change_data['value']['date_to']

                slip_data = slip_pool.onchange_employee_id(cr, SUPERUSER_ID, [], f_d, t_d, emp.id, contract_id=False, context=context)
#            slip_data = slip_pool.onchange_employee_id(cr, uid, [], from_date, to_date, emp.id, contract_id=False, context=context)
          #  print "$$$$$$$$$$",period_change_data,from_date, to_date,f_d,t_d
                if period_change_data['value'].get('xo_msg', False) == 'Contract Period Not Valid':
                    raise Warning("Not a valid contract for an employee for the employee %s"%emp.name)
                modified_worked_days_line_ids = []
                worked_days_line_ids_new = [(0, 0, x) for x in slip_data['value'].get('worked_days_line_ids', False)]
                if worked_days_line_ids_new:
                    for _,_,line in worked_days_line_ids_new:
                        if not isinstance(line['code'], str):
                            new_code = str(unicodedata.normalize('NFKD', line['code']).encode('ascii','ignore')).rstrip() 
                            

                            line['code'] = new_code
                        w = (0,0,line)
                        modified_worked_days_line_ids.append(w)
                        
                        
                        
#            [(0, 0, x) for x in slip_data['value'].get('input_line_ids', False)]
                res = {
                'employee_id': emp.id,
                'name': slip_data['value'].get('name', False),
                'struct_id': slip_data['value'].get('struct_id', False),
                'contract_id': slip_data['value'].get('contract_id', False),
                'payslip_run_id': int(self_obj.payslip),
                'input_line_ids':modified_worked_days_line_ids,
                'worked_days_line_ids': [(0, 0, x) for x in slip_data['value'].get('worked_days_line_ids', False)],
#                'date_from': from_date,
#                'date_to': to_date,

                'date_from': period_change_data['value'].get('date_from', False),
                'date_to': period_change_data['value'].get('date_to', False),

                'credit_note': credit_note,

                'journal_id':journal_id,
                'xo_period_id' : xo_period_id,
                'xo_total_no_of_days':xo_total_no_of_days
                }
            #slip_ids.append(slip_pool.create(cr, uid, res, context=context))
                payslip_id  = slip_pool.create(cr, uid, res, context=context)
                slip_pool.compute_sheet(cr, uid, [payslip_id], context=context)
        else:
            xo_period_id = self_obj.xo_period_id and self_obj.xo_period_id.id 
            self.pool.get('account.period').browse(cr,uid,xo_period_id,context)
            date_f = self.pool.get('account.period').browse(cr,uid,xo_period_id,context).date_start
            
            new_end_date = date_f[:8] + str(od_cut_days)
            fist_day_of_current_date = date_f[:8] + str(1)
            xx = datetime.strptime(fist_day_of_current_date,"%Y-%m-%d") - timedelta(days=1)
            ss = xx.strftime('%Y-%m-%d')
            prev_date = ss[:8] + str(prev_month_cut_day) 
            diff = (datetime.strptime(new_end_date,"%Y-%m-%d") - datetime.strptime(prev_date,"%Y-%m-%d")).days + 1
            journal_id = self_obj.journal_id and self_obj.journal_id.id 
            if not data['employee_ids']:
                raise osv.except_osv(_("Warning!"), _("You must select employee(s) to generate payslip(s)."))
            context['od_cut_days'] = od_cut_days

            for emp in emp_pool.browse(cr, uid, data['employee_ids'], context=context):
            
                period_change_data = slip_pool.onchange_payslip_period(cr, uid, [],emp.id, xo_period_id,od_cut_days,context=context)
                f_d= prev_date
                t_d= new_end_date
                slip_data = slip_pool.onchange_employee_id(cr, uid, [], f_d, t_d, emp.id, contract_id=False, context=context)

                if period_change_data['value'].get('xo_msg', False) == 'Contract Period Not Valid':
                    raise osv.except_osv(_('Error!'),_('Contract for Employee: (%s) is not valid!')%(emp.name))



                if period_change_data['value'].get('xo_msg', False) == 'Contract Period Not Valid':
                    raise osv.except_osv(_('Error!'),_('Contract for Employee: (%s) is not valid!')%(emp.name))

                modified_worked_days_line_ids = []
                worked_days_line_ids_new = [(0, 0, x) for x in slip_data['value'].get('worked_days_line_ids', False)]
                if worked_days_line_ids_new:
                    for _,_,line in worked_days_line_ids_new:
                        if not isinstance(line['code'], str):
                            new_code = str(unicodedata.normalize('NFKD', line['code']).encode('ascii','ignore')).rstrip() 
                            line['code'] = new_code
                        w = (0,0,line)
                        modified_worked_days_line_ids.append(w)
            
                res = {
                'employee_id': emp.id,
                'name': slip_data['value'].get('name', False),
                'struct_id': slip_data['value'].get('struct_id', False),
                'contract_id': slip_data['value'].get('contract_id', False),
                'payslip_run_id': int(self_obj.payslip),
                'input_line_ids': modified_worked_days_line_ids,
                'worked_days_line_ids': [(0, 0, x) for x in slip_data['value'].get('worked_days_line_ids', False)],

                'date_from': f_d,
                'date_to': t_d,

                'credit_note': credit_note,

                'journal_id':journal_id,
                'xo_period_id' : xo_period_id,
                'xo_total_no_of_days':diff
                }

                payslip_id  = slip_pool.create(cr, uid, res, context=context)
                slip_pool.compute_sheet(cr, uid, [payslip_id], context=context)
            
            
        
        return {'type': 'ir.actions.act_window_close'}



