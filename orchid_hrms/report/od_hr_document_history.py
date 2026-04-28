# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import fields, osv
class od_hr_document_history(osv.osv):
    _name = "od.hr.document.history"
    _description = "od.hr.document.history"
    _auto = False
    _rec_name = 'employee_id'############################# refer main column
    _columns = {
        'employee_id':fields.many2one('hr.employee','Employee'),
        'process_date':fields.date('Process Date'),
        'doc_action':fields.char('Doc Action'),
        'action_type':fields.char('Action Type'),
        'document_type_id':fields.many2one('od.employee.document.type',string='Document Type')
        



    }
    _order = 'employee_id desc'################# for displaying record as desending cashier name
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'od_hr_document_history')
        cr.execute("""
            create or replace view od_hr_document_history as (
                select ROW_NUMBER () OVER (ORDER BY  od_holiday_document_line.id ) AS id,
document_type_id as document_type_id,recieved_date as process_date,hr_holidays.employee_id as employee_id,'issue' as doc_action,'Leave' as action_type
from od_holiday_document_line  
join hr_holidays on hr_holidays.id = od_holiday_document_line.holiday_id
join od_employee_document_type on od_employee_document_type.id = od_holiday_document_line.document_type_id
where recieved <> 't' and issued = 't' and od_employee_document_type.custodian = 'company'

UNION
select ROW_NUMBER () OVER (ORDER BY  od_holiday_document_line.id ) AS id, document_type_id,issued_date as process_date,hr_holidays.employee_id,'received' as doc_action,'Leave' as action_type
from od_holiday_document_line  
join hr_holidays on hr_holidays.id = od_holiday_document_line.holiday_id
join od_employee_document_type on od_employee_document_type.id = od_holiday_document_line.document_type_id
where recieved = 't' and od_employee_document_type.custodian = 'company'

UNION
select ROW_NUMBER () OVER (ORDER BY  od_document_request.id ) AS id, document_type_id,return_date as process_date,employee_id,'received' as doc_action,'Document' as action_type
from od_document_request 
join od_employee_document_type on od_employee_document_type.id = od_document_request.document_type_id
where is_returned ='t' and od_employee_document_type.custodian = 'company'

UNION
select ROW_NUMBER () OVER (ORDER BY  od_document_request.id ) AS id, document_type_id,issued_date as process_date,employee_id,'issue' as doc_action,'Document' as action_type
from od_document_request 
join od_employee_document_type on od_employee_document_type.id = od_document_request.document_type_id
where is_returned <> 't' and is_issued = 't' and od_employee_document_type.custodian = 'company'

UNION
select ROW_NUMBER () OVER (ORDER BY  od_employee_joining_document_line.id ) AS id, document_type_id,recieved_date as process_date,od_employee_joining.employee_id,'received' as doc_action,'Joining' as action_type
FROM  od_employee_joining_document_line 
join od_employee_joining on od_employee_joining_document_line.joining_id =od_employee_joining.id 
join od_employee_document_type on od_employee_document_type.id = od_employee_joining_document_line.document_type_id
where recieved = 't' and od_employee_document_type.custodian = 'company'
              )
               """)



#  group by
#                    hr_holidays.employee_id

















#select document_type_id,recieved_date as process_date,hr_holidays.employee_id,'issue' as doc_action,'Leave' as action_type
#from od_holiday_document_line  
#join hr_holidays on hr_holidays.id = od_holiday_document_line.holiday_id
#join od_employee_document_type on od_employee_document_type.id = od_holiday_document_line.document_type_id
#where recieved <> 't' and issued = 't' and od_employee_document_type.custodian = 'company'
#UNION
#select document_type_id,issued_date as process_date,hr_holidays.employee_id,'received' as doc_action,'Leave' as action_type
#from od_holiday_document_line  
#join hr_holidays on hr_holidays.id = od_holiday_document_line.holiday_id
#join od_employee_document_type on od_employee_document_type.id = od_holiday_document_line.document_type_id
#where recieved = 't' and od_employee_document_type.custodian = 'company'
#UNION
#select document_type_id,return_date as process_date,employee_id,'received' as doc_action,'Document' as action_type
#from od_document_request 
#join od_employee_document_type on od_employee_document_type.id = od_document_request.document_type_id
#where is_returned ='t' and od_employee_document_type.custodian = 'company'
#UNION
#select document_type_id,issued_date as process_date,employee_id,'issue' as doc_action,'Document' as action_type
#from od_document_request 
#join od_employee_document_type on od_employee_document_type.id = od_document_request.document_type_id
#where is_returned <> 't' and is_issued = 't' and od_employee_document_type.custodian = 'company'
#UNION
#select document_type_id,recieved_date as process_date,od_employee_joining.employee_id,'received' as doc_action,'Joining' as action_type
#FROM  od_employee_joining_document_line 
#join od_employee_joining on od_employee_joining_document_line.joining_id =od_employee_joining.id 
#join od_employee_document_type on od_employee_document_type.id = od_employee_joining_document_line.document_type_id
#where recieved = 't' and od_employee_document_type.custodian = 'company'

#od_pos_payment_type_report_view()
