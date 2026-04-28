# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-TODAY OpenERP S.A. <http://www.odoo.com>
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

from openerp import models, fields, api
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from datetime import datetime
from openerp.exceptions import except_orm, Warning, RedirectWarning
import datetime 
import dateutil.relativedelta 
from datetime import date, timedelta

class od_leave_on_particular_period_report_wizard(models.TransientModel):
    _name = 'od.leave.on.particular.period.report.wizard'
    from_date = fields.Date(String="From Date",required="1")
    to_date = fields.Date(String="To Date",required="1")

    stage = fields.Selection([
            ('approved_leaves','Approved Leaves'),
            ('waiting_for_approval','Waiting For Approval'),

            ('rejected_leaves','Rejected Leaves'),

            ('resumed_leaves','Resumed Leaves'),
            ('waiting_for_resumption','Waiting For Resumption'),
            ('all_leaves','All'),
        ], string='stage', required="1", default='all_leaves')


    def od_generate_report(self,cr,uid,ids,context=None):
        wizard_obj = self.browse(cr,uid,ids,context)
        domain_ids = []
        from_date = wizard_obj.from_date
        to_date = wizard_obj.to_date
        stage = wizard_obj.stage
        from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d")
        to_date = str(datetime.datetime.strptime(to_date,"%Y-%m-%d") +timedelta(days=1))[:10]
        to_date = str(datetime.datetime.strptime(to_date, "%Y-%m-%d"))
        
        holiday_ids = []
        if stage == 'approved_leaves':
            holiday_ids = self.pool.get('hr.holidays').search(cr,uid,[('state','in',('validate','od_resumption_to_approve','od_approved')),('date_from','>=',str(from_date)),('date_to','<',str(to_date))])

        elif stage == 'waiting_for_approval':

            holiday_ids = self.pool.get('hr.holidays').search(cr,uid,[('state','in',('confirm','validate1','validate2')),('date_from','>=',str(from_date)),('date_to','<',str(to_date))])
        elif stage == 'rejected_leaves':

            holiday_ids = self.pool.get('hr.holidays').search(cr,uid,[('state','=','refuse'),('date_from','>=',str(from_date)),('date_to','<',str(to_date))])
        elif stage == 'resumed_leaves':
            holiday_ids = self.pool.get('hr.holidays').search(cr,uid,[('state','=','od_approved'),('date_from','>=',str(from_date)),('date_to','<',str(to_date))])



        elif stage == 'waiting_for_resumption':

            holiday_ids = self.pool.get('hr.holidays').search(cr,uid,[('state','=','od_resumption_to_approve'),('date_from','>=',str(from_date)),('date_to','<',str(to_date))])
        else:
            holiday_ids = self.pool.get('hr.holidays').search(cr,uid,[('date_from','>=',str(from_date)),('date_to','<',str(to_date))])


        already_assigned_ids = self.pool.get('od.leave.on.particular.period.report').search(cr,uid,[])
        self.pool.get('od.leave.on.particular.period.report').unlink(cr,uid,already_assigned_ids,context)


        for holiday_id in holiday_ids:
            holiday_obj = self.pool.get('hr.holidays').browse(cr,uid,holiday_id,context)
            vals = {'employee_id':holiday_obj.employee_id and holiday_obj.employee_id.id,
                    'holiday_status_id':holiday_obj.holiday_status_id and holiday_obj.holiday_status_id.id,
                    'from_date':holiday_obj.date_from,
                    'to_date':holiday_obj.date_to,
                    'state':holiday_obj.state}
            leave_on_particular_period_id = self.pool.get('od.leave.on.particular.period.report').create(cr,uid,vals)
            domain_ids.append(leave_on_particular_period_id)
            

        res = {
        'type': 'ir.actions.act_window',
        'view_mode': 'tree,graph',
        'view_type': 'form',
        'res_model': 'od.leave.on.particular.period.report',
        'domain': [('id', 'in',domain_ids)],
        }
        print res
        return res
    
    



