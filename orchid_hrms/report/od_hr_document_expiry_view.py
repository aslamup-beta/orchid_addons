# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import fields, osv
class od_hr_document_expiry_view(osv.osv):
    _name = "od.hr.document.expiry.view"
    _description = "od.hr.document.expiry.view"
    _auto = False
    _rec_name = 'employee_id'
    _columns = {
        'employee_id':fields.many2one('hr.employee','Employee'),
        'document_type_id':fields.many2one('od.employee.document.type',string='Document Type'),
        'document_referance':fields.char(string='Document Reference'),
        'issue_date':fields.date(string='Issue Date'),
        'expiry_date':fields.date(string='Expiry Date'),
        
    }


    def _select(self):
        select_str = """
              SELECT ROW_NUMBER () OVER (ORDER BY od_hr_employee_document_line.id ) AS id,
            od_hr_employee_document_line.employee_id as employee_id,
            od_hr_employee_document_line.document_type_id as document_type_id, 
            od_hr_employee_document_line.issue_date as issue_date,
            od_hr_employee_document_line.expiry_date as expiry_date,
            od_hr_employee_document_line.document_referance as document_referance
             
        """
        return select_str
    def _from(self):
        from_str = """
                od_hr_employee_document_line 
        """
        return from_str

    def _group_by(self):
        group_by_str = """
            GROUP BY od_hr_employee_document_line.employee_id,
            od_hr_employee_document_line.id,
            od_hr_employee_document_line.document_type_id, 
            od_hr_employee_document_line.issue_date,
            od_hr_employee_document_line.expiry_date,
            od_hr_employee_document_line.document_referance
                    
        """
        return group_by_str


    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM  %s 
  %s
            )""" % (self._table, self._select(), self._from(), self._group_by()))


