# -*- coding: utf-8 -*-
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

from openerp import models, fields, api, _

class od_hr_employee_certificate_line(models.Model):
    _name = 'od.hr.employee.certificate.line'
    _description = "Employee Carrier Certificates"
    
    employee_id = fields.Many2one('hr.employee', string='Employee')
    document_type_id = fields.Many2one('od.employee.document.type',string='Document Type',required=True, default=9)
    document_referance = fields.Char(string='Document Reference')
    attach_file = fields.Binary(string='Scanned Copy')
    issue_date = fields.Date(string='Issue Date')
    expiry_date = fields.Date(string='Expiry Date')
    attach_fname = fields.Char(string='Comp', size=32)

    def default_get(self, cr, uid, ids,context=None):
        res = super(od_hr_employee_certificate_line, self).default_get(cr, uid, ids, context=context)
        res.update({'employee_id': context.get('active_id', False)})
        return res
    
class od_hr_employee_appreciation_line(models.Model):
    _name = 'od.hr.employee.appreciation.line'
    _description = "Employee Appreciations"
    
    employee_id = fields.Many2one('hr.employee', string='Employee')
    partner_id = fields.Many2one('res.partner',string='Customer Name', domain=[('is_company','=',True)])
    document_referance = fields.Char(string='Reference')
    date = fields.Date(string='Date of Appreciation')
    attach_file = fields.Binary(string='Attachment')
    attach_fname = fields.Char(string='Comp', size=32)

    def default_get(self, cr, uid, ids,context=None):
        res = super(od_hr_employee_appreciation_line, self).default_get(cr, uid, ids, context=context)
        res.update({'employee_id': context.get('active_id', False)})
        return res
    