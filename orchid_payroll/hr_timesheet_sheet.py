# -*- coding: utf-8 -*-

import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from openerp.osv import fields, osv
from openerp.tools.translate import _
class hr_timesheet_sheet(osv.osv):
    _inherit = "hr_timesheet_sheet.sheet"
    _table = 'hr_timesheet_sheet_sheet'

#Inherited to avoid the constraint chal
    def _sheet_date(self, cr, uid, ids, forced_user_id=False, context=None):
#        for sheet in self.browse(cr, uid, ids, context=context):
#            new_user_id = forced_user_id or sheet.user_id and sheet.user_id.id
#            if new_user_id:
#                cr.execute('SELECT id \
#                    FROM hr_timesheet_sheet_sheet \
#                    WHERE (date_from <= %s and %s <= date_to) \
#                        AND user_id=%s \
#                        AND id <> %s',(sheet.date_to, sheet.date_from, new_user_id, sheet.id))
#                if cr.fetchall():
#                    return False
        return True
    _constraints = [
        (_sheet_date, 'You cannot have 2 timesheets that overlap!\nPlease use the menu \'My Current Timesheet\' to avoid this problem.', ['date_from','date_to']),
    ]
