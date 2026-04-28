# -*- coding: utf-8 -*-
import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp.osv import fields, osv
from openerp.tools.translate import _


class od_hr_over_time(osv.osv):
    _name = 'od.hr.over.time'
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id
    _columns = {
        'name':fields.char('Document No', size=64, required=True),
        'company_id': fields.many2one('res.company','Company'),
        'period_id':fields.many2one('account.period','Period', required=True, domain=[('state','<>','done'),('special','=',False)]),
        'narration':fields.text('Narration'),
        'date':fields.date('Date'),
        'over_time_lines':fields.one2many('od.hr.over.time.line','hr_over_time_id','Hr Over Time Lines'),
        
        'state': fields.selection([
            ('draft', 'Draft'),
            ('confirm', 'Confirmed'),
            ],
            'Status', readonly=True),
    }
    _defaults={
        'name':'/',
        'state': 'draft',
        'date': fields.date.context_today,
        'company_id': _get_default_company,
    }

    def button_confirm(self, cr, uid, ids, context=None):
        self.write(cr, uid,ids, {'state': 'confirm'})
        return True

    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'od.hr.overtime') or '/'
        return super(od_hr_over_time, self).create(cr, uid, vals, context=context)

class od_hr_over_time_line(osv.osv):
     _name = 'od.hr.over.time.line'

     def _get_od_code(self, cr, uid, ids, field_name, arg=None, context=None):
        res ={}
        for rec in self.browse(cr, uid, ids, context):
            res[rec.id] = rec.over_time_type.code or ''
        return res
   
     _columns = {
        'employee_id':fields.many2one('hr.employee','Employee Name', required=True),
        'hour':fields.float('Hour'),
        'over_time_type':fields.many2one('hr.salary.rule','OT Type'),
        'code': fields.function(_get_od_code, string='Code', type='char', size=10,store=True),
        'hr_over_time_id': fields.many2one('od.hr.over.time','OverTime'),
        'payslip_id':fields.many2one('hr.payslip','PaySlip'),
        'period_id': fields.related('hr_over_time_id', 'period_id', type='many2one', relation='account.period', string='Period', store=True, readonly=True)
    }
   


