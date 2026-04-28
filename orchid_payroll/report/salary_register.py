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
from openerp import tools
from openerp.osv import fields, osv

class od_salary_register(osv.osv):
    _name = "od.salary.register"
    _description = "od.salary.register"
    _auto = False
    _rec_name = 'name'
    
    _columns = {
        'company_id': fields.many2one('res.company','Company'),
        'employee_id':fields.many2one('hr.employee','Employee'),
        'name': fields.char('name'),
        'period_id': fields.many2one('account.period','Period', required=True, domain=[('state','<>','done'),('special','=',False)]),
        'date_from': fields.date('From Date'),
        'date_to': fields.date('To Date'),
        'salary_rule_id': fields.many2one('hr.salary.rule','Salary Rule'),
        'amount': fields.float('Amount'),
        'sequence': fields.integer('Sequence'),
        'code': fields.char('Code'),
    }

    def _select(self):
        select_str = """
        SELECT DISTINCT PH.id AS id,
        PH.EMPLOYEE_ID as employee_id,
        PH.company_id as company_id,
        PH.name as name,
        PH.XO_PERIOD_ID as period_id,
        PH.DATE_FROM as date_from,
        PH.DATE_TO as date_to,
        PL.AMOUNT as amount,
        PL.SALARY_RULE_ID as salary_rule_id,
        RULE.CODE as code,
        RULE.SEQUENCE as sequence,
        CASE WHEN (rule.code = 'BASIC') THEN pl.amount ELSE 0 END AS BASIC,
        CASE WHEN (rule.code = 'HRA') THEN pl.amount ELSE 0 END AS HRA,
        CASE WHEN (rule.code = 'TRANS') THEN pl.amount ELSE 0 END AS TRANS,
        CASE WHEN (rule.code = 'FOOD') THEN pl.amount ELSE 0 END AS FOOD,
        CASE WHEN (rule.code = 'NIGHT') THEN pl.amount ELSE 0 END AS NIGHT,
        CASE WHEN (rule.code = 'SPECIAL') THEN pl.amount ELSE 0 END AS SPECIAL,
        CASE WHEN (rule.code = 'NOT') THEN pl.amount ELSE 0 END AS NOT,
        CASE WHEN (rule.code = 'HOT') THEN pl.amount ELSE 0 END AS HOT,
        CASE WHEN (rule.code = 'GROSS') THEN pl.amount ELSE 0 END AS GROSS,
        CASE WHEN (rule.code = 'LOAN') THEN pl.amount ELSE 0 END AS LOAN,
        CASE WHEN (rule.code = 'NET') THEN pl.amount ELSE 0 END AS NET

        """
        return select_str

    def _from(self):
        from_str = """
                HR_PAYSLIP PH
        """
        return from_str
#    def _order_by(self):
#        order_by_str = """
#            ORDER BY rule.sequence
#        """
#        return order_by_str

    def init(self, cr):
        # self._table = sale_report
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM  %s 
    INNER JOIN HR_PAYSLIP_LINE PL ON (PL.SLIP_ID=PH.ID)
    INNER JOIN HR_SALARY_RULE RULE ON (RULE.ID = PL.SALARY_RULE_ID)
     WHERE PL.AMOUNT>0.0
            )""" % (self._table, self._select(), self._from()))



















# WHERE PL.AMOUNT > 0 
#    order by rule.sequence
##    order by rule.sequence







