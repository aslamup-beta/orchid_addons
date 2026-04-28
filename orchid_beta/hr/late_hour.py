# -*- coding: utf-8 -*-
import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp.osv import fields, osv
from openerp.tools.translate import _


class od_late_hour(osv.osv):
    _name = 'od.late.hour'
    _description = "Late Hour"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id

    def unlink(self, cr, uid, ids, context=None):
        for late_hour in self.browse(cr, uid, ids, context=context):
            if late_hour.state != 'draft':
                raise osv.except_osv(_('Warning!'),_('You cannot delete it, it is not in draft state'))
 
        return super(od_late_hour, self).unlink(cr, uid, ids, context)




    _columns = {
        'name':fields.char('Document No', size=64, required=True),
        'company_id': fields.many2one('res.company','Company'),
        'period_id':fields.many2one('account.period','Period', required=True, domain=[('state','<>','done'),('special','=',False)],track_visibility='onchange'),
        'narration':fields.text('Narration'),
        'date':fields.date('Date'),
        'late_hour_line':fields.one2many('od.late.hour.line','hr_late_hour_id','Late hour Lines'),
        
        'state': fields.selection([
            ('draft', 'Draft'),
            ('waiting_approval', 'Waiting Approval'),
            ('approved', 'Approved'),
            ],
            'Status', readonly=True,track_visibility='onchange'),
    }
    _defaults={
        'name':'/',
        'state': 'draft',
        'date': fields.date.context_today,
        'company_id': _get_default_company,
    }

    def button_confirm(self, cr, uid, ids, context=None):
        self.write(cr, uid,ids, {'state': 'approved'})
        return True


    def button_reset(self, cr, uid, ids, context=None):
#        obj =
        self.write(cr, uid,ids, {'state': 'draft'})
#        for 
        return True



    def button_submit(self, cr, uid, ids, context=None):
        self.write(cr, uid,ids, {'state': 'waiting_approval'})
        return True

    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'od.late.hour') or '/'
        return super(od_late_hour, self).create(cr, uid, vals, context=context)

class od_late_hour_line(osv.osv):
     _name = 'od.late.hour.line'
     _description = "Late Hour Line"

     def _get_od_code(self, cr, uid, ids, field_name, arg=None, context=None):
        res ={}
        for rec in self.browse(cr, uid, ids, context):
            res[rec.id] = rec.late_time_type.code or ''
        return res


     def _get_od_state(self, cr, uid, ids, field_name, arg=None, context=None):
        res ={}
        for rec in self.browse(cr, uid, ids, context):
            state = rec.hr_late_hour_id.state
            res[rec.id] = state
        return res

     def create(self, cr, uid, vals, context=None):

        parameter_obj = self.pool.get('ir.config_parameter')
        #company parameter
        late_hour_rule = parameter_obj.search(cr,uid,[('key', '=', 'def_late_hour_rule')])
        if not late_hour_rule:
            raise osv.except_osv(_('Settings Warning!'),_('No salary rule defined for late hours\nset in System Parameters with def_late_hour_rule!'))
        company_param =parameter_obj.browse(cr,uid,late_hour_rule)
        rule_id = company_param.od_model_id and company_param.od_model_id.id or False
        vals['late_time_type'] = rule_id
        
        return super(od_late_hour_line, self).create(cr, uid, vals, context=context)




   
     _columns = {
        'employee_id':fields.many2one('hr.employee','Employee Name', required=True),
        'date':fields.date('Date'),
        'late_hour':fields.float('Late Hour'),
        'hr_late_hour_id': fields.many2one('od.late.hour','Late Hour'),
        'period_id': fields.related('hr_late_hour_id', 'period_id', type='many2one', relation='account.period', string='Period', store=True, readonly=True),
        'payslip_id':fields.many2one('hr.payslip','PaySlip'),
#        'state':fields.related('hr_late_hour_id', 'state', type='char',string="State",store=True),
        'late_time_type':fields.many2one('hr.salary.rule','Rule'),
        'code': fields.function(_get_od_code, string='Code', type='char', size=10,store=True),
    }



