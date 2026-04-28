# -*- coding: utf-8 -*-
import time
from openerp import models, fields, api

from pprint import pprint
from datetime import datetime
import openerp.addons.decimal_precision as dp
from datetime import datetime


class EmpContractExpiryWizard(models.TransientModel):
    _name = 'emp.contract.expiry.wiz'

    employee_ids = fields.Many2many('hr.employee', string="Employee")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    wiz_line = fields.One2many('emp.contract.expiry.data.line', 'org_wiz_id', string="Wiz Line")

    def od_get_company_id(self):
        return self.env.user.company_id

    company_id = fields.Many2one('res.company', string='Company', default=od_get_company_id)

    def get_contracts(self):
        contract_obj = self.env['hr.contract']
        company_id = self.env.user.company_id.id
        domain = [('company_id', '=', company_id), ('od_active', '=', True), ('od_limited', '=', True)]
        if self.employee_ids:
            domain += [('employee_id', 'in', self.employee_ids.ids)]
        contracts = contract_obj.search(domain)
        return contracts

    def get_data(self):
        company_id = self.env.user.company_id.id
        result = []
        contracts = self.get_contracts()
        for contract in contracts:
            remaining_days = 0
            target_date = datetime.strptime(contract.date_end, "%Y-%m-%d")
            print("target_date", target_date)
            # Get today's date
            today = datetime.now()
            # Calculate the difference
            difference = target_date - today
            # Extract the number of remaining days
            remaining_days = difference.days
            print("remaining_days", remaining_days)
            line_dict = {
                'employee_id': contract.employee_id.id,
                'id_number': contract.employee_id.identification_id,
                'start_date': contract.date_start,
                'end_date': contract.date_end,
                'remaining_days': remaining_days,
            }
            po_rpt_line = self.env['emp.contract.expiry.data.line']
            line = po_rpt_line.create(line_dict)
            print("line", line)
            result.append(line.id)
        return result

    @api.multi
    def export_rpt(self):
        model_data = self.env['ir.model.data']
        result = self.get_data()
        print("result", result)
        vw = 'tree_view_emp_contract_expiry_data_line'
        #         result = self.get_data()

        tree_view = model_data.get_object_reference('beta_extended', vw)
        # self.wiz_line.unlink()
        # self.write({'wiz_line': result})
        # del (result)
        return {
            'domain': [('id', 'in', result)],
            'name': 'Contract Expiry',
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(tree_view and tree_view[1] or False, 'tree')],
            'res_model': 'emp.contract.expiry.data.line',
            'type': 'ir.actions.act_window',
        }


class EmpContractExpiryData(models.TransientModel):
    _name = 'emp.contract.expiry.data'

    def od_get_company_id(self):
        return self.env.user.company_id

    company_id = fields.Many2one('res.company', string='Company', default=od_get_company_id)
    line_ids = fields.One2many('emp.contract.expiry.data.line', 'wiz_id', string="Wiz Line", readonly=True)


class EmpContractExpiryDataLine(models.TransientModel):
    _name = 'emp.contract.expiry.data.line'

    def od_get_company_id(self):
        return self.env.user.company_id

    company_id = fields.Many2one('res.company', string='Company', default=od_get_company_id)

    wiz_id = fields.Many2one('emp.contract.expiry.data', string="Wizard data")
    org_wiz_id = fields.Many2one('ps.po.rpt.wiz', string="Wizard")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    id_number = fields.Char(string="ID Number")
    start_date = fields.Date(string="Contract Start Date")
    end_date = fields.Date(string="Contract End Date")
    remaining_days = fields.Float(string="Remaining Days Until Contract Expiration")

    @api.multi
    def btn_open_po(self):
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'purchase.order',
            'res_id': self.purchase_id and self.purchase_id.id or False,
            'type': 'ir.actions.act_window',
            'target': 'new',

        }
