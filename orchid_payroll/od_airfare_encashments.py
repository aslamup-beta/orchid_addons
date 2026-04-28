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


class od_airfare_encashments(osv.osv):
    _name = "od.airfare.encashments"
    _description = "od.airfare.encashments"

#    def to_approve(self,cr,uid,ids,context=None):
#        self.write(cr,uid,ids,{'state':'approved'},context=context)

    def to_refused(self,cr,uid,ids,context=None):
        self.write(cr,uid,ids,{'state':'refused'},context=context)
    def submit(self,cr,uid,ids,context=None):
        self.write(cr,uid,ids,{'state':'to_approve'},context=context)

    def set_to_draft(self,cr,uid,ids,context=None):
        self.write(cr,uid,ids,{'state':'draft'},context=context)






    def unlink(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.state not in ['draft']:
                raise osv.except_osv(_('Invalid Action!'), _('Cannot delete  which is in state \'%s\'.') %(rec.state,))
        return super(od_airfare_encashments, self).unlink(cr, uid, ids, context=context)

    def _check_eligibility_date(self, cr, uid, ids, field_name, arg, context=None): 
        res ={} 
        eligibility_date = ''


        for li in self.browse(cr, uid, ids, context): 
            employee_id = li.employee_id.id
            employee_obj = self.pool.get('hr.employee').browse(cr,uid,employee_id,context)
            eligibility_date =employee_obj.od_eligibility_date
            if eligibility_date:
                system_date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                eligibility_date_time = datetime.strptime(str(eligibility_date), '%Y-%m-%d') 
                duration = (datetime.strptime(str(system_date_time), '%Y-%m-%d %H:%M:%S') -  datetime.strptime(str(eligibility_date_time), '%Y-%m-%d %H:%M:%S')).days
                if duration < 0:
                    raise osv.except_osv(_('Warning!'),_('You are not eligible'))
            
            
            res[li.id] = eligibility_date
        return res
        


    _columns = {
        'employee_id': fields.many2one('hr.employee','Employee',required=True),
        'department_id':fields.related('employee_id','department_id',string='Department',type='many2one',relation='hr.department',readonly="1"),
        'job_id':fields.related('employee_id','job_id',string='Job',type='many2one',relation='hr.job',readonly="1"),
        'address_home_id':fields.related('employee_id','address_home_id',string='Home Address',type='many2one',relation='res.partner',readonly="1"),
        'od_eligibility_date':fields.function(_check_eligibility_date,string='Eligibility Date',type='date',readonly="1",store=True),

        'state': fields.selection([
            ('draft', 'Draft'),
            ('to_approve', 'To Approve'),
            ('refused', 'Refused'),
            ('approved', 'Approved'),
            ],
            'Status', readonly=True, track_visibility='onchange'),
        'amount':fields.float('Amount'),
        'notes':fields.text('Remarks')




    }
#    _constraints = [(_check_eligibility_date, 'you are not eligibile', ['od_eligibility_date'])]
    _defaults = {
        'state': 'to_approve'
    }
