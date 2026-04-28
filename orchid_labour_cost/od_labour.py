# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.osv import osv
from openerp.tools.translate import _
from openerp.exceptions import Warning
import openerp.addons.decimal_precision as dp
from __builtin__ import False
def simply(l):
    result = []
    for item in l :
        check = False
        # check item, is it exist in result yet (r_item)
        for r_item in result :
            if item['user_id'] == r_item['user_id'] and item['project_id'] == r_item['project_id'] and item['od_opp_id'] == r_item['od_opp_id'] :
                # if found, add all key to r_item ( previous record)
                check = True
                duration = r_item['duration'] + item['duration']
                amount = r_item['amount'] + item['amount']
                actual = r_item['actual_amount'] + item['actual_amount']
                r_item['duration'] = duration
                r_item['amount'] = amount
                r_item['actual_amount'] = actual
        if check == False :
            # if not found, add item to result (new record)
            result.append( item )

    return result

class od_labour(models.Model):
    _name = 'od.labour'
    _order = 'id desc'
    
    def od_get_company_id(self):
        return self.env.user.company_id
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    name = fields.Char(string='Title', required=True,readonly=True, states={'draft': [('readonly', False)]})
    date = fields.Date(required=True,readonly=True, states={'draft': [('readonly', False)]},string='Entry Date')
    date_from = fields.Date(reuired=True,states={'draft': [('readonly', False)]},string='Date From',required=True)
    date_to = fields.Date(reuired=True,states={'draft': [('readonly', False)]},string='Date To',required=True)
    rate = fields.Selection([('overhead','Overhead Rate'),('actual','Actual Rate')],default='actual',string='State',required=True)
    wip_account_id = fields.Many2one('account.account','WIP Account',required=True,readonly=True, states={'draft': [('readonly', False)]})
    # working_hour = fields.Float(string='Total W.hours',help="Total Working Hour in a month multiplied by working hour in a day ex (25*8 =200)",required=True)
    journal_id = fields.Many2one('account.journal','Journal',required=True,readonly=True,states={'draft': [('readonly', False)]})
    expense_account_id = fields.Many2one('account.account','Provision Account',required=True,readonly=True,states={'draft': [('readonly', False)]})
    move = fields.Many2one('account.move','Journal Entry',readonly=True)
    state = fields.Selection([('draft','Draft'),('done','Done'),('cancel','Cancel')],default='draft',string='State')
    actual = fields.Boolean('Actual',readonly=True,states={'draft': [('readonly', False)]})
    labour_line = fields.One2many('od.labour.line','cost_id')



    @api.one
    def btn_cancel(self):
        self.write({'state':'cancel'})
        move_id = self.move
        move_id.button_cancel()
        move_id.unlink()

    @api.one
    def btn_reset_draft(self):
        self.write({'state':'draft'})

    @api.one
    def unlink(self):
        #add your code here
        if self.state != 'draft':
            raise osv.except_osv(_('User Error!'), _('You can only delete draft Labour Cost'))
        return super(od_labour, self).unlink()

    def get_employee_partner(self,partner_id):
        hr_pool =self.env['hr.employee']
        hr_id = hr_pool.sudo().search([('address_home_id','=',partner_id)],limit=1)
        return hr_id 
    def get_cc_attrs(self,partner_id):
        hr_id = self.get_employee_partner(partner_id)
        cc = hr_id.od_cost_centre_id and hr_id.od_cost_centre_id.id or False 
        branch = hr_id.od_branch_id and hr_id.od_branch_id.id or False
        division = hr_id.od_division_id and hr_id.od_division_id.id or False
        return cc,branch,division
    @api.one
    def create_move(self):
        period_obj = self.env['account.period']
        move_obj = self.env['account.move']
        date = self.date
        period_ids = period_obj.find(date).id
        ref = self.name
        journal_id = self.journal_id and self.journal_id.id
        debit_account = self.wip_account_id.id
        credit_account = self.expense_account_id.id
        actual = self.actual
        move_lines =[]

        for line in self.labour_line:
            opp_id=False
            partner_id = line.partner_id.id
            amount = line.amount
            od_cost_centre_id = line.project_id and line.project_id.od_cost_centre_id and line.project_id.od_cost_centre_id.id or False
            od_branch_id = line.project_id and line.project_id.od_branch_id and line.project_id.od_branch_id.id or False
            od_division_id = line.project_id and line.project_id.od_division_id and line.project_id.od_division_id.id or False
            manual =  line.project_id.od_manual
            company_id = self.env.user.company_id.id or False
            if manual:
                od_cost_centre_id = line.project_id and line.project_id.cost_centre_id and line.project_id.cost_centre_id.id or False 
                od_branch_id  = line.project_id and line.project_id.branch_id and line.project_id.branch_id.id or False 
                od_division_id = line.project_id and line.project_id.division_id and line.project_id.division_id.id
            
            if company_id==6 and self.wip_account_id.id == 6567:
                opp_id = self.env['crm.lead'].search([('id','=', line.od_opp_id.id)])
                od_cost_centre_id = line.project_id and line.project_id.cost_centre_id and line.project_id.cost_centre_id.id or False
                od_branch_id = opp_id.od_branch_id and opp_id.od_branch_id.id or False
                od_division_id = opp_id.od_division_id and opp_id.od_division_id.id or False
                
            if company_id==1 and self.wip_account_id.id in [2135,6632]:
                opp_id = self.env['crm.lead'].search([('id','=', line.od_opp_id.id)])
                od_cost_centre_id = line.project_id and line.project_id.cost_centre_id and line.project_id.cost_centre_id.id or False
                od_branch_id = opp_id.od_branch_id and opp_id.od_branch_id.id or False
                od_division_id = opp_id.od_division_id and opp_id.od_division_id.id or False
                
            if not (od_cost_centre_id and od_branch_id) and not (self.wip_account_id.id in(6567,2135,6632)):
                raise Warning("The Project/Analytic %s Not linked with Branch and Cost Center "%line.project_id.name)
            if actual:
                amount = line.actual_amount
            vals1={
                'name': ref,
                'ref': ref,
                'period_id': period_ids ,
                'journal_id': journal_id,
                'date': date,
                'account_id': credit_account,
                'debit': 0.0,
                'credit': abs(amount),
                'partner_id': partner_id,
                'analytic_account_id': line.project_id.id,
                'od_cost_centre_id': od_cost_centre_id,
                'od_branch_id': od_branch_id,
                'od_division_id': od_division_id,
                'od_opp_id':opp_id and opp_id.id

            }
            vals2={
                'name': ref,
                'ref': ref,
                'period_id': period_ids ,
                'journal_id': journal_id,
                'date': date,
                'account_id': debit_account,
                'credit': 0.0,
                'debit': abs(amount),
                'partner_id': partner_id,
                'analytic_account_id': line.project_id.id,
                'od_cost_centre_id': od_cost_centre_id,
                'od_branch_id': od_branch_id,
                'od_division_id': od_division_id,
                'od_opp_id':opp_id and opp_id.id

            }
            move_lines.append([0,0,vals1])
            move_lines.append([0,0,vals2])
            line.state = 'done'
        move_vals = {

                'date': date,
                'ref': ref,
                'period_id': period_ids ,
                'journal_id': journal_id,
                'line_id':move_lines

                }
        move_id = move_obj.create(move_vals).id
        self.move = move_id
        self.state = 'done'
        return True



    @api.one
    def get_timesheet(self,project_ids,excluded_project_ids):
        cr = self.env.cr
        employee_obj = self.env['hr.employee']
        contract_obj = self.env['hr.contract']
        labour_cost_line = self.env['od.labour.line']
        timesheet = self.env['hr.analytic.timesheet']
        lead_obj = self.env['crm.lead']
        # working_hour = self.working_hour
        actual = self.actual
        date_from = self.date_from
        date_to = self.date_to
        company_id = self.company_id and self.company_id.id or False
        domain = [('date','>=',date_from), ('date','<=',date_to),('company_id','=',company_id)]
        if project_ids:
            domain.append(('account_id','in',project_ids))
        if excluded_project_ids:
            domain.append(('account_id','not in',excluded_project_ids))
        t_ids  = timesheet.search(domain)
        labour_cost_line.search([('cost_id', '=',self.ids[0])]).unlink()
        res = []
        
        for data in t_ids:
            opp_id = False
            timesheet_id = data.id 
            query ="select task_id from project_task_work where hr_analytic_timesheet_id=%s"%timesheet_id
            cr.execute(query)
            task_id = cr.fetchone()
            
            if task_id and task_id[0]:
                task_id = task_id[0]
                query ="select od_opp_id from project_task where id =%s"%task_id
                cr.execute(query)
                opp_id = cr.fetchone()
                opp_id = opp_id and opp_id[0]
                opp_rec = lead_obj.search([('id','=',opp_id)])
                cust_id = opp_rec.partner_id and opp_rec.partner_id.id or False
                branch_id = opp_rec.od_branch_id and opp_rec.od_branch_id.id or False
            employee_id =  employee_obj.search([('user_id','=',data.user_id.id)])
            if not employee_id:
                raise Warning("Please Activate the Employee for %s "%data.user_id.name)
            contract_id = contract_obj.search([('employee_id','=',employee_id.id),('od_active','=',True)])
            if len(contract_id) >1:
                raise Warning("Please Check the %s Employee Have More Than One Active Contract "%employee_id.name)
            if not contract_id:
                raise Warning("Please Check the %s Employee Have No Contract Exist"%employee_id.name)
            total_wage = contract_id.xo_total_wage
            partner_id = employee_id.address_home_id and employee_id.address_home_id.id
            working_hour = contract_id.xo_working_hours
            if not working_hour:
                raise Warning("Please Check %s The Employee Contract Working Hour Cannot Be Zero"%employee_id.name)
            if working_hour:
                unit_salary = (total_wage/30)/working_hour
            else:
                unit_salary = 0.0

            if not partner_id:
                partner_id = data.user_id and data.user_id.partner_id and data.user_id.partner_id.id
            if not opp_id:
                proj_rec = data.account_id
                cust_id = proj_rec.partner_id and proj_rec.partner_id.id or False
                branch_id = proj_rec.od_branch_id and proj_rec.od_branch_id.id or False

            if company_id==6 :
                amount = abs(data.amount)
            else:
                budget_unit_salary = 350.00
                if data.user_id.id in (2427, 37, 18, 54, 2423, 2428):
                    budget_unit_salary = 75.00
                amount = abs(budget_unit_salary * data.unit_amount)
                
            vals = {
                    'cost_id':self.ids[0],
                    'project_id':data.account_id.id,
                    'user_id':data.user_id.id,
                    'partner_id': partner_id,
                    'duration':data.unit_amount,
                    'amount':amount,
                    'actual_amount': abs(unit_salary * data.unit_amount),
                    'od_opp_id':opp_id,
                    'cust_id': cust_id,
                    'branch_id' : branch_id
                 }
            res.append(vals)
        result = simply(res)
        for vals in result:
            labour_cost_line.create(vals)

        return True
class od_labour_line(models.Model):
    _name = 'od.labour.line'
    cost_id = fields.Many2one('od.labour',string='Labour Cost')
    date = fields.Date()
    project_id = fields.Many2one('account.analytic.account','Project/Contract')
    user_id = fields.Many2one('res.users','User')
    partner_id = fields.Many2one('res.partner','Employee')
    duration = fields.Float(string='Duration',digits=dp.get_precision('Account'))
    amount = fields.Float(string="Overhead",digits=dp.get_precision('Account'))
    actual_amount = fields.Float(string='Actual Amount',digits=dp.get_precision('Account'))
    move_id = fields.Many2one('account.move','Journal Voucher',readonly=True)
    state = fields.Selection([('draft','Draft'),('done','Done')],default='draft',string='State')
    od_opp_id = fields.Many2one('crm.lead',string="Opportunity",readonly=True)
    cust_id = fields.Many2one('res.partner','Customer')
    branch_id = fields.Many2one('od.cost.branch','Branch')
    @api.one
    def unlink(self):
        if self.state == 'done':
            raise osv.except_osv(_('User Error!'), _('You can only delete draft Cost Line'))
        return super(od_labour_line, self).unlink()
