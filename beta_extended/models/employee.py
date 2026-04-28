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
from datetime import date, datetime
from openerp import tools
from itertools import groupby
import calendar
from dateutil.relativedelta import relativedelta


class hr_employee(models.Model):
    _inherit = "hr.employee"

    high_management_id = fields.Many2one('hr.employee', string='Higher Management')


    def action_view_duty_resumption(self, cr, uid, ids, context=None):
        leave_ids = self.pool.get('hr.holidays').search(cr, uid, [('employee_id', '=', ids[0]),('state', '=', 'validate'),('holiday_status_id', '=', 1)])
        leave_recs = self.pool['hr.holidays'].browse(cr, uid, leave_ids, context=context)
        today = date.today()
        yesterday = today - relativedelta(days=1)
        for rec in leave_recs:
            leave_end_date = datetime.strptime(rec.date_to, "%Y-%m-%d %H:%M:%S").date()
            leave_start_date = datetime.strptime(rec.date_from, "%Y-%m-%d %H:%M:%S").date()
            april_fst = datetime.strptime('2025-04-01 00:00:00', "%Y-%m-%d %H:%M:%S").date()
            if leave_end_date > yesterday:
                leave_ids.remove(rec.id)
            if leave_start_date < april_fst:
                leave_ids.remove(rec.id)
        action = self.pool['ir.actions.act_window'].for_xml_id(
            cr, uid, 'orchid_payroll', 'action_od_duty_reception11')
        action['domain'] = unicode([('id', 'in', leave_ids)])
        return action

    def od_action_open_document_request(self, cr, uid, ids, context=None):
        res = super(hr_employee, self).od_action_open_document_request(cr, uid, ids, context)
        model_data = self.pool.get('ir.model.data')
        tree_view = model_data.get_object_reference(cr, uid, 'beta_extended', 'od_document_request_tree_new')
        form_view = model_data.get_object_reference(cr, uid, 'beta_extended', 'od_document_request_form_new')
        res['views'] = [(tree_view and tree_view[1] or False, 'tree'), (form_view and form_view[1] or False, 'form')]
        return res

    def run_employee_passport_documents_expiry_reminder_90_days(self, cr, uid, context=None):
        context = dict(context or {})
        template_id = self.pool['email.template'].browse(cr, uid, 447)[0]
        hr_pool = self.pool['hr.employee']
        doc_pool = self.pool['od.hr.employee.document.line']
        today = datetime.date.today()
        emp_ids = hr_pool.search(cr, uid, [('active', '=', True), ('company_id', '=', 6)], context=context)
        if emp_ids:
            for emp_id in emp_ids:
                document_ids = doc_pool.search(cr, uid, [('employee_id', '=', emp_id), ('document_type_id', '=', 2)],
                                               context=context)
                emp_docs = doc_pool.browse(cr, uid, document_ids, context=context)
                for doc in emp_docs:
                    expiry_date = doc.expiry_date
                    context['doc_name'] = doc.document_type_id.name
                    context['expiry_date'] = expiry_date
                    if expiry_date:
                        expiry_date1 = datetime.datetime.strptime(expiry_date, '%Y-%m-%d').date()
                        expiry_date_bf_3mnth = expiry_date1 - relativedelta(days=90)
                        if expiry_date_bf_3mnth == today:
                            self.pool.get('email.template').send_mail(cr, uid, template_id.id, emp_id, force_send=True,
                                                                      context=context)

    def run_employee_passport_documents_expiry_reminder_to_hr(self, cr, uid, context=None):
        context = dict(context or {})
        template_id = self.pool['email.template'].browse(cr, uid, 448)[0]
        hr_pool = self.pool['hr.employee']
        doc_pool = self.pool['od.hr.employee.document.line']
        today = datetime.date.today()
        emp_ids = hr_pool.search(cr, uid, [('active', '=', True), ('company_id', '=', 6)], context=context)
        if emp_ids:
            for emp_id in emp_ids:
                document_ids = doc_pool.search(cr, uid, [('employee_id', '=', emp_id), ('document_type_id', '=', 2)],
                                               context=context)
                emp_docs = doc_pool.browse(cr, uid, document_ids, context=context)
                for doc in emp_docs:
                    expiry_date = doc.expiry_date
                    context['doc_name'] = doc.document_type_id.name
                    context['expiry_date'] = expiry_date
                    if expiry_date:
                        expiry_date1 = datetime.datetime.strptime(expiry_date, '%Y-%m-%d').date()
                        next_date_after_expiry_date = expiry_date1 + relativedelta(days=1)
                        if next_date_after_expiry_date == today:
                            self.pool.get('email.template').send_mail(cr, uid, template_id.id, emp_id, force_send=True,
                                                                      context=context)


class HrContract(models.Model):
    _inherit = "hr.contract"

    def od_send_mail(self, template):
        print("od_send_mail")
        ir_model_data = self.env['ir.model.data']
        email_obj = self.pool.get('email.template')
        # if self.company_id.id == 6:
        #     template = template + '_saudi'
        template_id = ir_model_data.get_object_reference('beta_extended', template)[1]
        # template_id = self.pool['email.template'].browse(cr,uid,354)[0]
        rec_id = self.id
        if template_id:
            email_obj.send_mail(self.env.cr, self.env.uid, template_id, rec_id, force_send=True)
        return True

    def ksa_emp_contract_expiry_reminder_120_days(self, cr, uid, context=None):
        template_id = self.pool['email.template'].browse(cr, uid, 444)[0]
        today = date.today()
        context = dict(context or {})
        contract_ids = self.pool['hr.contract'].search(cr, uid, [('employee_id.company_id', '=', 6),
                                                                 ('od_active', '=', True),
                                                                 ('od_limited', '=', True)], context=context)
        for contract in self.browse(cr, uid, contract_ids):
            contract_end_date = contract.date_end
            date_after_120_days = today + relativedelta(days=120)
            if contract_end_date == str(date_after_120_days):
                self.pool.get('email.template').send_mail(cr, uid, template_id.id, contract.id, force_send=True,
                                                          context=context)
        return True

    def ksa_emp_contract_expiry_reminder_97_days(self, cr, uid, context=None):
        template_id = self.pool['email.template'].browse(cr, uid, 445)[0]
        today = date.today()
        context = dict(context or {})
        contract_ids = self.pool['hr.contract'].search(cr, uid, [('employee_id.company_id', '=', 6),
                                                                 ('od_active', '=', True),
                                                                 ('od_limited', '=', True)], context=context)
        for contract in self.browse(cr, uid, contract_ids):
            contract_end_date = contract.date_end
            date_after_97_days = today + relativedelta(days=97)
            if contract_end_date == str(date_after_97_days):
                self.pool.get('email.template').send_mail(cr, uid, template_id.id, contract.id, force_send=True,
                                                          context=context)
        return True

    def ksa_emp_contract_expiry_reminder_next_day(self, cr, uid, context=None):
        template_id = self.pool['email.template'].browse(cr, uid, 446)[0]
        today = date.today()
        context = dict(context or {})
        contract_ids = self.pool['hr.contract'].search(cr, uid, [('employee_id.company_id', '=', 6),
                                                                 ('od_active', '=', True),
                                                                 ('od_limited', '=', True)], context=context)
        for contract in self.browse(cr, uid, contract_ids):
            contract_end_date = contract.date_end
            contract_end_date_object = datetime.strptime(contract_end_date, "%Y-%m-%d").date()
            next_day = contract_end_date_object + relativedelta(days=1)
            if today == next_day:
                self.pool.get('email.template').send_mail(cr, uid, template_id.id, contract.id, force_send=True,
                                                          context=context)
        return True

    def ksa_emp_contract_expiry_quarterly_list(self, cr, uid, context=None):
        today = date.today()
        context = dict(context or {})
        contract_ids = self.pool['hr.contract'].search(cr, uid, [('employee_id.company_id', '=', 6),
                                                                 ('od_active', '=', True),
                                                                 ('od_limited', '=', True)], context=context)
        line_data = []
        for contract in self.browse(cr, uid, contract_ids):
            target_date = datetime.strptime(contract.date_end, "%Y-%m-%d")
            # Get today's date
            today = datetime.now()
            # Calculate the difference
            difference = target_date - today
            # Extract the number of remaining days
            remaining_days = difference.days
            if remaining_days <= 120:
                line_dict = {
                    'employee_id': contract.employee_id.id,
                    'contract_id': contract.id,
                    'id_number': contract.employee_id.identification_id,
                    'start_date': contract.date_start,
                    'end_date': contract.date_end,
                    'remaining_days': remaining_days,
                }
                line_data.append(line_dict)
        if line_data:
            date_string = today.strftime("%d-%b-%Y")
            name = 'Report Created on' + " " + date_string

            emp_list = self.pool.get('hr.contract.quarterly').create(cr, uid, {'name': name, 'date_from': today})
            if emp_list:
                for data in line_data:
                    data['quarterly_id'] = emp_list
                    emp_list_line = self.pool.get('emp.contract.line').create(cr, uid, data)
            emp_list_obj = self.pool['hr.contract.quarterly'].browse(cr, uid, emp_list)[0]
            if emp_list_obj:
                emp_list_obj.od_send_mail('ksa_emp_contract_expiry_list')

        return True
