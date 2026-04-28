import datetime
import math
import time
from operator import attrgetter

from openerp.exceptions import Warning
from openerp import tools
from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import timedelta
import dateutil.relativedelta 


class od_hr_holidays_public(osv.osv):

    _name = 'od.hr.holidays.public'
    _description = 'Public Holidays'
    
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id

    _columns = {
        'company_id': fields.many2one('res.company','Company',required=True),
        'year': fields.char("Calendar Year", required=True),
        'line_ids': fields.one2many('od.hr.public.holidays.line', 'holidays_public_id', 'Holiday Dates'),
    }
    _defaults ={
    'company_id': _get_default_company,
}

    _rec_name = 'year'
    _order = "year"

    _sql_constraints = [
        ('year_unique', 'UNIQUE(year)', _('Duplicate year!')),
    ]


    def unlink(self, cr, uid, ids, context=None): 
        line_ids_obj = self.browse(cr,uid,ids,context)
        unlink_ids = [] 
        for obj in line_ids_obj.line_ids:
            if obj.variable:
                raise osv.except_osv(_('Invalid Action!'), _('You cannot Delete it,first de allocate all holidays'))
            unlink_ids.append(obj.id)

        return osv.osv.unlink(self, cr, uid, unlink_ids, context=context)



class od_hr_public_holidays_line(osv.osv):

    _name = 'od.hr.public.holidays.line'
    _description = 'Public Holidays Lines'

    _columns = {
        'name': fields.char('Name', size=128, required=True),
        'date': fields.date('Date', required=True),
        'holidays_public_id': fields.many2one('od.hr.holidays.public', 'Holiday Calendar Year'),
        'variable': fields.boolean('Active',readonly="1"),
    }

    _order = "date, name desc"
    def od_allocate(self,cr,uid,ids,context=None):
        obj = self.browse(cr,uid,ids,context)
        pub_comp_id = obj.company_id and obj.company_id.id
        self.pool.get('od.hr.public.holidays.line').write(cr,uid,[obj.id],{'variable':True},context)
        date = str(obj.date) 
        qry ="SELECT id from hr_holidays where (date_from,date_to) OVERLAPS ('"+date+"', '"+date+"');" 
        cr.execute(qry)
        result = cr.fetchall()
        parameter_ids = []
        new_tmp_days = 0
        for obj in result:
            for holi in self.pool.get('hr.holidays').browse(cr,uid,obj[0],context):
                emp_comp_id = holi.employee_id and holi.employee_id.company_id and holi.employee_id.company_id.id
                if emp_comp_id:
                    if emp_comp_id == pub_comp_id:
                        self.pool.get('hr.holidays').write(cr,uid,[holi.id],{'date_to':holi.date_to,'date_from':holi.date_from},context=context)
                else:
                    self.pool.get('hr.holidays').write(cr,uid,[holi.id],{'date_to':holi.date_to,'date_from':holi.date_from},context=context)

        return True
                


    def unlink(self, cr, uid, ids, context=None): 
        line_ids_obj = self.browse(cr,uid,ids,context)
    
        variable =  line_ids_obj.variable
        if variable:
            raise osv.except_osv(_('Invalid Action!'), _('you cannot delete without deallocating it'))
            

        return osv.osv.unlink(self, cr, uid, [line_ids_obj.id], context=context)

    def od_deallocate(self,cr,uid,ids,context=None):
        obj = self.browse(cr,uid,ids,context)
        pub_comp_id = obj.company_id and obj.company_id.id
        self.pool.get('od.hr.public.holidays.line').write(cr,uid,[obj.id],{'variable':False},context)

        date = str(obj.date) 
        qry ="SELECT id from hr_holidays where (date_from,date_to) OVERLAPS ('"+date+"', '"+date+"');" 
        cr.execute(qry)
        result = cr.fetchall()
        parameter_ids = []
        new_tmp_days = 0

        for obj in result:
            for holi in self.pool.get('hr.holidays').browse(cr,uid,obj[0],context):
                emp_comp_id = holi.employee_id and holi.employee_id.company_id and holi.employee_id.company_id.id
                if emp_comp_id:
                    if emp_comp_id == pub_comp_id:
                        self.pool.get('hr.holidays').write(cr,uid,[holi.id],{'date_to':holi.date_to,'date_from':holi.date_from},context=context)
                else:
                    self.pool.get('hr.holidays').write(cr,uid,[holi.id],{'date_to':holi.date_to,'date_from':holi.date_from},context=context)
        return True
