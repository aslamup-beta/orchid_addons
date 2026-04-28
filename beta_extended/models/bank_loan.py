# -*- coding: utf-8 -*-

import itertools
from lxml import etree

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp
from openerp.tools import amount_to_text_en
# from . import amount_to_ar
from pprint import pprint
from openerp import tools
from itertools import groupby


class BankLoan(models.Model):
    _inherit = "od.beta.bank.loan"

    basic_salary = fields.Float(string="Basic Salary")
    allowance = fields.Float(string="Allowance")
    total_salary = fields.Float(string="Total Salary")
    join_date = fields.Date(string="Date of Joining")
    n_bank_name_ar = fields.Char('Bank Name(Arabic)', track_visibility='onchange')

    def _get_contract_obj(self):
        employee_id = self.name and self.name.id or False
        res =self.env['hr.contract'].search([('od_active','=',True),('employee_id','=',employee_id)],limit=1)
        if self.name and self.name.active == False:
            res =self.env['hr.contract'].search([('employee_id','=',employee_id)], order='id desc')[0]
        return res

    def _get_allowances(self):
        contract = self._get_contract_obj()
        result = 0.0
        for line in contract.xo_allowance_rule_line_ids:
            if line.code=='OA':
                result += line.amt
            if line.code=='ALW':
                result += line.amt
            if line.code == 'KSA_HA':
                result += line.amt
            if line.code == 'KSA_TA':
                result += line.amt
        return result

    @api.onchange('name')
    def onchange_name_get_data(self):
        contract_obj = self._get_contract_obj()
        employee = self.name or False
        if employee:
            self.join_date = employee.od_joining_date or False
            self.allowance = self._get_allowances()
            self.basic_salary = contract_obj.wage
            self.total_salary = contract_obj.wage + self._get_allowances()

