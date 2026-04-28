# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
from openerp.tools.translate import _
import time
from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta

class hr_payslip(osv.osv):
    _inherit = "hr.payslip"

    def _report_xls_fields_uae(self, cr, uid, context=None):
        return [
            'emp_uid','routing_code','bank_ac','net_salary','variable_salary','lpo','pay_from','pay_till'
        ]
    def _report_xls_template_uae(self, cr, uid, context=None):
        res = {
            'move':{
                'header': [1, 20, 'text', _('Orchid Payroll WPS')],
            }
        }
        return res