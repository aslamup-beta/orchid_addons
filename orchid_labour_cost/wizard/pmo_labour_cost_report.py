# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.osv import osv
from openerp.tools.translate import _
from openerp.exceptions import Warning
import openerp.addons.decimal_precision as dp


def simply(l):
    result = []
    for item in l :
        check = False
        # check item, is it exist in result yet (r_item)
        for r_item in result :
            if item['user_id'] == r_item['user_id'] and item['project_id'] == r_item['project_id'] :
                # if found, add all key to r_item ( previous record)
                check = True
                duration = r_item['duration'] + item['duration']
                
                actual = r_item['actual_amount'] + item['actual_amount']
                r_item['duration'] = duration
                
                r_item['actual_amount'] = actual
        if check == False :
            # if not found, add item to result (new record)
            result.append( item )

    return result


class od_pmo_labor_wiz(models.TransientModel):
    _name = 'od.pmo.labor.wiz'
    def od_get_company_id(self):
        return self.env.user.company_id
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')
    project_ids = fields.Many2many('account.analytic.account','rel_analytic_pmo_wiz', 'wiz_id', 'analytic_id', string="Projects")
    excluded_project_ids = fields.Many2many('account.analytic.account','rel_analytic_pmo_excluded_wiz', 'wiz_id', 'analytic_id', string="Excluded Projects")
    user_ids = fields.Many2many('res.users','rel_pmo_users','wiz_id','user_ids',string="Users")
    wiz_line = fields.One2many('od.pmo.labor.wiz.line','wiz_id',string="Wizard Line")
    @api.multi
    def get_timesheet(self):
        employee_obj = self.env['hr.employee']
        contract_obj = self.env['hr.contract']
        labour_cost_line = self.env['od.labour.line']
        timesheet = self.env['hr.analytic.timesheet']
        # working_hour = self.working_hour
        
        date_from = self.date_from
        date_to = self.date_to
        company_id = self.company_id and self.company_id.id or False
        domain = [('date','>=',date_from), ('date','<=',date_to),('company_id','=',company_id)]
        project_ids = self.project_ids 
        project_ids  = [dat.id for dat in project_ids]
        excluded_project_ids = self.excluded_project_ids
        excluded_project_ids  = [dat.id for dat in excluded_project_ids]
        user_ids = self.user_ids
        user_ids  = [dat.id for dat in user_ids]
        if project_ids:
            domain.append(('account_id','in',project_ids))
        if excluded_project_ids:
            domain.append(('account_id','not in',excluded_project_ids))
        if user_ids:
            domain.append(('user_id','in',user_ids))
        t_ids  = timesheet.search(domain)
        res = []
        for data in t_ids:
            employee_id =  employee_obj.search([('user_id','=',data.user_id.id)])
            if not employee_id:
                raise Warning("Please Activate the Employee for %s "%data.user_id.name)
            contract_id = contract_obj.search([('employee_id','=',employee_id.id),('od_active','=',True)])
            if len(contract_id) >1:
                raise Warning("Please Check the %s Employee Have More Than One Active Contract "%employee_id.name)
            if not contract_id:
                raise Warning("Please Check the %s Employee Have No Contract Exist"%employee_id.name)
            total_wage = contract_id.xo_total_wage
            
            working_hour = contract_id.xo_working_hours
            if not working_hour:
                raise Warning("Please Check %s The Employee Contract Working Hour Cannot Be Zero"%employee_id.name)
            if working_hour:
                unit_salary = (total_wage/30)/working_hour
            else:
                unit_salary = 0.0

           
            vals = {
                    'wiz_id':self.id,
                    'project_id':data.account_id.id,
                    'user_id':data.user_id.id,
                    'duration':data.unit_amount,
                    'actual_amount': abs(unit_salary * data.unit_amount)
                 }
            res.append(vals)
        
        
        result = simply(res)
        result2 = []
        for res in result:
            result2.append((0,0,res))
            
        self.write({'wiz_line':result2})
        wiz_id = self.id
        return {
            'domain': [('wiz_id','=',wiz_id)],
            'name': 'Labour Cost Report',
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'od.pmo.labor.wiz.line',
            'type': 'ir.actions.act_window',
        }


class od_pmo_labor_wiz_line(models.TransientModel):
    _name = 'od.pmo.labor.wiz.line'
    wiz_id = fields.Many2one('od.pmo.labor.wiz',string="Wizard")
    project_id = fields.Many2one('account.analytic.account','Project/Contract')
    user_id = fields.Many2one('res.users','User')
    duration = fields.Float(string='Duration',digits=dp.get_precision('Account'))
    actual_amount = fields.Float(string='Actual Amount',digits=dp.get_precision('Account'))