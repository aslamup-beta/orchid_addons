# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from datetime import datetime
from dateutil.relativedelta import relativedelta
import calendar
import math

class od_final_settlement_type_master(osv.osv):
    _name = "od.final.settlement.type.master"
    _description = "od.final.settlement.type.master"

    _columns = {
        'name': fields.char('Name',required=True),
        'final_settlement':fields.boolean('Final Settlement'),
        'remarks':fields.text('Remarks'),
        'journal_id':fields.many2one('account.journal','Journal',required="1"),
        'settlement_type_master_line':fields.one2many('od.final.settlement.type.master.line','settlement_type_master_line_id','Settlement Line')

    }

class od_final_settlement_type_master_line(osv.osv):
    _name = "od.final.settlement.type.master.line"
    _description = "od.final.settlement.type.master.line"

    _columns = {
        'account_id':fields.many2one('account.account','Account',domain=[('type', 'not in', ['view','consolidation','closed'])]),
        'settlement_type_master_line_id':fields.many2one('od.final.settlement.type.master')

    }



class od_final_settlement(osv.osv):
    _name = "od.final.settlement"
    _description = "od.final.settlement"
    
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id

    def set_to_draft(self, cr, uid, ids, context=None):
        obj = self.browse(cr,uid,ids,context)
        line1_unlink_ids = []
        line2_unlink_ids = []
        state = obj.state
        account_move_id = obj.account_move_id and obj.account_move_id.id
        if account_move_id:
            raise osv.except_osv(_('Warning!'), _('delete the journal entry'))

        for line1 in obj.account_line:
            line1_unlink_ids.append(line1.id)
        for line2 in obj.account_new_line:
            line2_unlink_ids.append(line2.id)
        self.pool.get('od.final.settlement.account.line').unlink(cr,uid,line1_unlink_ids,context)
        self.pool.get('od.final.settlement.new.account.line').unlink(cr,uid,line2_unlink_ids,context)
            
        
        self.write(cr,uid,ids,{'state':'draft','checking_acc_entry_button_ctrl':False,'basic_salary':0,'joining_date':False,'total_salary':0,
'gratuity_amt':0,'gratuity_date':False,'leave_salary':0,'leave_date':False,
'leave_pending':0,'airfare_amt':0,'unpaid_leave':0,'total_working_days':0})  
            

        return True




    def unlink(self, cr, uid, ids, context=None): 
        obj = self.browse(cr,uid,ids,context)
        state = obj.state
        if state != 'draft':
            raise osv.except_osv(_('Warning!'), _('it is not in draft state'))
            
        return osv.osv.unlink(self, cr, uid, ids, context=context)


    def onchange_settlement_type_id(self, cr, uid, ids, settlement_type_id, context=None):
        result = {}
        if settlement_type_id:
            setle_object = self.pool.get('od.final.settlement.type.master').browse(cr, uid, settlement_type_id, context=context)
            settlement = setle_object.final_settlement
            result['final_settlement'] = settlement 
                        

        return {'value': result}

    def check_accounts_entry(self, cr, uid, ids, context=None):
        obj = self.browse(cr,uid,ids,context)
        final_settlement = obj.final_settlement
        extra_row = {}
        transaction_ids = []
        recievable_acc_id = obj.employee_id.address_home_id.property_account_receivable and obj.employee_id.address_home_id.property_account_receivable.id
        payable_acc_id = obj.employee_id.address_home_id.property_account_payable and obj.employee_id.address_home_id.property_account_payable.id
        debit = 0
        credit = 0
        total_due = 0
        total_amt = 0
        total_debit =0
        total_credit =0
        sum_of_negative_values = 0
        sum_of_postive_values = 0
        existing_ids = self.pool.get('od.final.settlement.new.account.line').search(cr,uid,[('account_line_id','=',obj.id)])
        if existing_ids:
            self.pool.get('od.final.settlement.new.account.line').unlink(cr,uid,existing_ids,context)

        for linee in obj.account_line:
            transaction_ids.append(linee.id)
        if not transaction_ids:
            raise osv.except_osv(_('Warning!'), _('generate the transactions first'))
            
            
            

        for line in obj.account_line:
#            if not obj.account_line:
#                raise osv.except_osv(_('Warning!'), _('generate the transactions first'))
                
            total_due = total_due + line.balance
            total_amt = total_amt + line.amount
            if line.balance < 0:

                if line.amount <0:
                    sum_of_negative_values = sum_of_negative_values + line.balance
                    raise osv.except_osv(_('Warning!'), _('check the signs of balance and amount'))
                    
            if line.balance > 0:
                if line.amount >0:
                    sum_of_postive_values = sum_of_postive_values + line.balance
                    raise osv.except_osv(_('Warning!'), _('check the signs of balance and amount'))
                    
                credit = line.amount
                
                debit = 0
            else:
                credit = 0
                debit = line.amount
#            if sum_of_postive_values > math.fabs(sum_of_negative_values):
#                raise osv.except_osv(_('Warning!'), _('check the liability'))
                
                
            
                
                
            vals = {'account_id':line.account_id.id or False,'account_line_id':line.account_line_id.id or False,'final_settlement':final_settlement,'debit':math.fabs(debit),'credit':math.fabs(credit),'due':math.fabs(line.balance)}
            self.pool.get('od.final.settlement.new.account.line').create(cr,uid,vals)
        if total_due < 0:
            total_debit = 0
            total_credit =total_amt
            
            extra_row = {'account_id':payable_acc_id or False,'account_line_id':obj.id or False,'final_settlement':final_settlement,'debit':math.fabs(total_debit),'credit':math.fabs(total_credit)}  
        else:
            total_debit = total_amt
            total_credit =0
            extra_row = {'account_id':recievable_acc_id or False,'account_line_id':obj.id or False,'final_settlement':final_settlement,'debit':math.fabs(total_debit),'credit':math.fabs(total_credit)} 
        self.pool.get('od.final.settlement.new.account.line').create(cr,uid,extra_row)  
        self.write(cr,uid,ids,{'state':'progress'})  
        return True

#    def onchange_employee_id(self, cr, uid, ids, employee_id, context=None):
#        result = {}
#        if employee_id:
#            employee_object = self.pool.get('hr.employee').browse(cr, uid, employee_id, context=context)
#            contract_ids =self.pool.get('hr.contract').search(cr,uid,[('employee_id','=',employee_id)])
#            joined_date = False
#            if contract_ids:
#                contract_id = contract_ids[0]
#            
#                contract_object = self.pool.get('hr.contract').browse(cr,uid,contract_id,context=context)
#                
#                if contract_object:
#                    joined_date = contract_object.date_start
#            
#                    if contract_object.trial_date_start:
#                        joined_date = contract_object.trial_date_start
#            result['joined_date'] = joined_date or False
#            result['address_home_id'] = employee_object.address_home_id and employee_object.address_home_id.id or False
#            result['department_id'] = employee_object.department_id and employee_object.department_id.id or False
#            result['job_id'] = employee_object.job_id and employee_object.job_id.id or False
#                        

#        return {'value': result} 

    def action_generate(self, cr, uid, ids, context=None):
        payable = 0
        recievable = 0
        unpaid_tot = 0
        working_days = 0
        amount = 0
        for obj in self.browse(cr, uid, ids, context=context):
            gratuity = obj.employee_id.od_gratuity
            gratuity_date = obj.employee_id.od_gratuity_date
            final_settlement = obj.settlement_type_id.final_settlement
            leave_salary = obj.employee_id.od_leave_salary
            leave_salary_date = obj.employee_id.od_leave_salary_date
            leave_pending = obj.employee_id.od_leaves
            airfare_amt = obj.employee_id.od_air_fare
            joining_date = obj.employee_id.od_joining_date

##finding unpaid leave in employee master
            
#            for le in obj.employee_id.od_leave_history_line:
#                print "VVVVVVVVVVVVVVVVV",le
#                if le.holiday_status_id == 4 and le.state not in ('cancel','refuse'):
#                    print "BBBBBBBBBBBBBBBBBB",le.number_of_days_temp 
#                    unpaid_tot = unpaid_tot + le.number_of_days_temp  
            holiday_ids = self.pool.get('hr.holidays').search(cr,uid,[('employee_id','=',obj.employee_id.id),('holiday_status_id','=',4),('state','not in',('cancel','refuse'))])
            for h in holiday_ids:
                holiday_obj = self.pool.get('hr.holidays').browse(cr,uid,h,context)
                unpaid_tot = unpaid_tot + holiday_obj.number_of_days_temp 
                

            date_to = obj.date_to
            if date_to:
                date_to = datetime.strptime(date_to,"%Y-%m-%d")
            if joining_date:
                joining_date = datetime.strptime(joining_date,"%Y-%m-%d")
            if not (date_to and joining_date):
                raise osv.except_osv(_('Warning!'), _('make sure joining_date and document date given'))

            working_days = ((date_to - joining_date).days + 1) - unpaid_tot

            
                 


            
            employee_id = obj.employee_id and obj.employee_id.id
            contract_ids = self.pool.get('hr.contract').search(cr,uid,[('employee_id','=',employee_id),('od_active','=',True)])
            if not contract_ids:
                raise osv.except_osv(_('Warning!'), _('no active contract for this employee'))
            contract_id = contract_ids[0]
            contract_obj = self.pool.get('hr.contract').browse(cr,uid,contract_id,context)
            basic = contract_obj.wage
            total_sal = contract_obj.xo_total_wage
            self.write(cr,uid,ids,{'basic_salary':basic,'joining_date':obj.employee_id.od_joining_date,'total_salary':total_sal,
'gratuity_amt':gratuity,'gratuity_date':gratuity_date,'leave_salary':leave_salary,'leave_date':leave_salary_date,
'leave_pending':leave_pending,'airfare_amt':airfare_amt,'unpaid_leave':unpaid_tot,'total_working_days':working_days},context)


        
                
            partner_id = obj.employee_id and  obj.employee_id.address_home_id and obj.employee_id.address_home_id.id
            settlement_type_id = obj.settlement_type_id and obj.settlement_type_id.id
            settlement_ids = self.pool.get('od.final.settlement.type.master').search(cr,uid,[('id','=',settlement_type_id)])
            settlement_type_obj = self.pool.get('od.final.settlement.type.master').browse(cr,uid,settlement_ids,context=context)
            account_ids = []
            for accounts in settlement_type_obj.settlement_type_master_line:
                account_ids.append(accounts.account_id.id)
            if not account_ids:
                raise osv.except_osv(_('Error!'), _('first set the accounts in settlement type master'))
            
            
            if not partner_id:
                raise osv.except_osv(_('Error!'), _('define Home Address First'))
            if obj.account_line:
                for lines in obj.account_line:
                    self.pool.get('od.final.settlement.account.line').unlink(cr,uid,[lines.id],context=context)
                
    
            account_move_line_obj = self.pool.get('account.move.line')
            
            
                   
            move_ids = account_move_line_obj.search(cr,uid,[('partner_id','=',partner_id),('account_id','in',account_ids)])
            if not move_ids:
                raise osv.except_osv(_('Error!'), _('there is no accounting entries for the particular employee'))
                
            move_data = account_move_line_obj.browse(cr,uid,move_ids)
            move_line_credit={}
            move_line_debit={}
            for line in move_data:
                if not line.account_id:
                    continue
                if line.credit:
                    move_line_credit[line.account_id.id] = (line.account_id.id not in move_line_credit) \
                                                             and line.credit or (float(move_line_credit.get(line.account_id.id))+line.credit)
                if line.debit:
                    move_line_debit[line.account_id.id] = (line.account_id.id not in move_line_debit) \
                                                           and line.debit or (float(move_line_debit.get(line.account_id.id))+line.debit)

            result =  { k: move_line_debit.get(k, 0) - move_line_credit.get(k, 0) for k in set(move_line_debit) | set(move_line_credit) }
            for account_id in result:
                if result[account_id] < 0:
                    payable = math.fabs(result[account_id])
                    amount = math.fabs(result[account_id])
                elif result[account_id] >0:
                    amount = (-1 * result[account_id])
                    payable = 0
                    
                
                vals = {
                    'account_id':account_id,
                    'balance':result[account_id],
                    'account_line_id':ids[0],
                    'amount':amount,
                    'final_settlement_flag':final_settlement
            
                }
                self.pool.get('od.final.settlement.account.line').create(cr,uid,vals)
        self.write(cr,uid,ids,{'checking_acc_entry_button_ctrl':True})




        return True                    

    _columns = {
         'company_id': fields.many2one('res.company','Company'),
        'employee_id': fields.many2one('hr.employee','Employee',required=True),
#        'joined_date':fields.date('Date Of Join'),
        'account_move_id':fields.many2one('account.move','Entry',readonly="1"),
        'final_settlement':fields.boolean('Final Settlement'),


        'basic_salary':fields.float('Basic'),
        'total_salary':fields.float('Total Salary'),
        'joining_date':fields.date('Joining Date'),
        'unpaid_leave':fields.float('Unpaid Leaves'),
        'total_working_days':fields.float('Total Working Days'),
        'gratuity_amt':fields.float('Gratuity'),
        'gratuity_date':fields.date('Date'),
        'leave_salary':fields.float('Leave Salary'),
        'leave_date':fields.date('Leave Date'),
        'leave_pending':fields.float('Leave Pending'),
        'airfare_amt':fields.float('Airfare Amt'),
        'department_id':fields.related('employee_id','department_id',string='Department',type='many2one',relation='hr.department',readonly="1"),
        'job_id':fields.related('employee_id','job_id',string='Job',type='many2one',relation='hr.job',readonly="1"),
        'address_home_id':fields.related('employee_id','address_home_id',string='Home Address',type='many2one',relation='res.partner',readonly="1"),
        'document_date':fields.date('Document Date'),
        'date_from':fields.date('Date From'),
        'date_to':fields.date('Date To'),
        'settlement_type_id':fields.many2one('od.final.settlement.type.master','Settlement Type',required="1"),
        'state': fields.selection([
            ('draft', 'New'),
            ('progress', 'Progress'),
            ('done', 'Done'),
            ],
            'Status', readonly=True, track_visibility='onchange'),
        'reason':fields.text('Reason'),
        'account_line':fields.one2many('od.final.settlement.account.line','account_line_id','Account Line'),
        'account_new_line':fields.one2many('od.final.settlement.new.account.line','account_line_id','Account New Line'),
        'checking_acc_entry_button_ctrl':fields.boolean('Flag'),




        'fiscalyear_id': fields.related('period_id', 'fiscalyear_id', string='Fiscal Year', type='many2one', relation='account.fiscalyear'), 
    }
    _defaults = {
        'document_date': fields.date.context_today,
        'state': 'draft',
        'date_to':fields.date.context_today,
        'company_id': _get_default_company,
    }


    def action_validate(self, cr, uid, ids, context=None):
        obj = self.browse(cr,uid,ids,context)
        if not obj.account_new_line:
            raise osv.except_osv(_('Error!'), _('there is no lines in adjustment'))
        od_cost_centre_id = obj.employee_id.od_cost_centre_id and obj.employee_id.od_cost_centre_id.id
        if not od_cost_centre_id:
            raise osv.except_osv(_('Error!'), _('select  cost centre in employee master'))
            
        final_settlement = obj.final_settlement
        account_move_obj = self.pool.get('account.move')
        journal_id = obj.settlement_type_id.journal_id and obj.settlement_type_id.journal_id.id
        home_address = obj.employee_id.address_home_id and obj.employee_id.address_home_id.id
        date = obj.date_to
        total_credit = 0
        total_debit = 0
        narration = 'Final Settlement' + '/'+ str(obj.employee_id.name) 
        period_pool = self.pool.get('account.period')
        search_periods = period_pool.find(cr, uid, date, context=context) 
        period_id = search_periods[0]
        data_lines = []
        
        if not home_address:
            raise osv.except_osv(_('Error!'), _('pls define partner for the employee'))

        recievable_acc_id = obj.employee_id.address_home_id.property_account_receivable and obj.employee_id.address_home_id.property_account_receivable.id
        payable_acc_id = obj.employee_id.address_home_id.property_account_payable and obj.employee_id.address_home_id.property_account_payable.id
        if not payable_acc_id:
            raise osv.except_osv(_('Error!'), _('set payable acc in employee home address'))
        if not recievable_acc_id:
            raise osv.except_osv(_('Error!'), _('set recievable acc in employee home address'))

        for lines in obj.account_new_line:
            total_debit = total_debit + round(lines.debit,2)
            total_credit = total_credit + round(lines.credit,2)

        if total_debit != total_credit:

            raise osv.except_osv(_('Error!'), _('total debit and credit are not matching'))


        for line in obj.account_new_line:

            vals2 = {
                    'period_id':period_id,
                    'journal_id':journal_id,
                    'date':date,
                    'naration':narration,
                    'name':narration,
                    'account_id':line.account_id.id,
                    'debit':line.debit,
                    'credit':0.0,
                    'od_cost_centre_id':od_cost_centre_id,

                    'partner_id':home_address,
            }
            if vals2['debit'] >0.0 or vals2['credit'] >0.0:
                data_lines.append((0,0,vals2),)


            vals1 = {
                    'period_id':period_id,
                    'journal_id':journal_id,
                    'date':date,
                    'naration':narration,
                    'name':narration,
                    'account_id':line.account_id.id,
                    'debit':0.0,
                    'credit':line.credit,
                    'od_cost_centre_id':od_cost_centre_id,

                    'partner_id':home_address,
            }
            if vals1['debit'] >0.0 or vals1['credit'] >0.0:
                data_lines.append((0,0,vals1),)
            

        if data_lines:
            data = {
                'journal_id':journal_id,
                'period_id':period_id,
                'date':date,
                'state':'draft',
                'ref':narration,
                'line_id':data_lines
            }
            account_move_id = account_move_obj.create(cr,uid,data)

            self.write(cr,uid,ids,{'state':'done','account_move_id':account_move_id},context)
        else:
            raise osv.except_osv(_('Error!'), _('no lines for generating journal entry'))
            


        return True


class od_final_settlement_account_line(osv.osv):
    _name = "od.final.settlement.account.line"
    _description = "od.final.settlement.account.line"

    def _check_due_amt(self, cr, uid, ids, context=None): 
        obj_fy = self.browse(cr, uid, ids[0], context=context) 
        if math.fabs(obj_fy.amount) >0:
            if math.fabs(obj_fy.amount) > math.fabs(obj_fy.balance): 
                return False 
        return True 



    _columns = {
        'account_line_id':fields.many2one('od.final.settlement','settlement'),
        'account_id':fields.many2one('account.account','Account',required="1",domain=[('type', 'not in', ['view','consolidation','closed'])]),
        'balance':fields.float('Balance',readonly="1"),
        'amount':fields.float('Payable'),
        'final_settlement_flag':fields.boolean('Final Settlement'),



    }
    _constraints = [ 
        (_check_due_amt, 'Error!\nthe amount cannot be greater than due.', ['balance','amount']) 
    ]



class od_final_settlement_new_account_line(osv.osv):
    _name = "od.final.settlement.new.account.line"
    _description = "od.final.settlement.new.account.line"

    def create(self, cr, uid, vals, context=None):
        if vals.get('account_line_id') or  vals.get('account_id'):
            obj = self.pool.get('od.final.settlement').browse(cr,uid,[vals.get('account_line_id')],context)
            final_settlement = obj.final_settlement
         
            
            if final_settlement:
                vals['final_settlement'] = final_settlement
        return super(od_final_settlement_new_account_line, self).create(cr, uid, vals, context=context)




    _columns = {
        'account_line_id':fields.many2one('od.final.settlement','settlement',),
        'account_id':fields.many2one('account.account','Account',required="1",domain=[('type', 'not in', ['view','consolidation','closed'])]),
        'debit':fields.float('Debit',),
        'credit':fields.float('Credit'),
        'due':fields.float('Due'),
        'final_settlement':fields.boolean('Final Settlement'),


    }





class od_mode_of_payment(osv.osv):
    _name = 'od.mode.of.payment'
    _description = "od.mode.of.payment"


    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id


    _columns = {
        
        
        'company_id': fields.many2one('res.company','Company'),
        'name':fields.char(string='Name',required="1"),
        'notes':fields.text('Remarks'),
        'routing_codes':fields.char(string='Routing Code'),
        'establishment':fields.char(string='Establishment'),
        'sponser_id':fields.many2one('res.company',string='Sponsor'),
        'wps':fields.boolean(string='WPS')

    }
    _defaults ={
                'company_id': _get_default_company,
                
                }



# vim:loanandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
