# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
from openerp.tools.translate import _
import time
from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta

class hr_payslip(osv.osv):
    _inherit = "hr.payslip"

    def _report_xls_fields(self, cr, uid, context=None):
        return [
            'code','otherid','routing_code','bank','date_from','date_to','worked_days','net_salary','variable_salary','days_on_leave'
        ]
    def _report_xls_template(self, cr, uid, context=None):
        res = {
            'move':{
                'header': [1, 20, 'text', _('Orchid Payroll WPS')],
            }
        }
        return res