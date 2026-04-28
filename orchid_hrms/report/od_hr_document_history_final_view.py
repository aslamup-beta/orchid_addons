# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import fields, osv
class od_hr_document_history_final_view(osv.osv):
    _name = "od.hr.document.history.final.view"
    _description = "od.hr.document.history.final.view"
    _auto = False
    _rec_name = 'employee_id'############################# refer main column
    _columns = {
        'employee_id':fields.many2one('hr.employee','Employee'),
        'process_date':fields.date('Action Date'),
        'doc_action':fields.char('Doc Action'),
        'action_type':fields.char('Action Type'),
        'document_type_id':fields.many2one('od.employee.document.type',string='Document Type')
        



    }

    _order = 'employee_id desc'################# for displaying record as desending cashier name
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'od_hr_document_history_final_view')
        cr.execute("""
            create or replace view od_hr_document_history_final_view as (
                select ROW_NUMBER () OVER (ORDER BY  od_hr_document_history.id ) AS id,
document_type_id as document_type_id,employee_id as employee_id,max(process_date) as process_date,doc_action as doc_action,action_type as action_type
from od_hr_document_history
group by document_type_id,employee_id,doc_action,action_type,od_hr_document_history.id


              )
               """)

