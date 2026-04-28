# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
from openerp.tools.translate import _
import copy
import math
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
import datetime
import dateutil.relativedelta
from datetime import date, timedelta
import itertools
from lxml import etree
import openerp.addons.decimal_precision as dp
import time
from openerp import workflow
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from openerp import SUPERUSER_ID





class od_leave_on_particular_period_report(models.Model):
    _name = 'od.leave.on.particular.period.report'
    _description = "od.leave.on.particular.period.report"
    employee_id = fields.Many2one('hr.employee',string='Employee')
    holiday_status_id = fields.Many2one('hr.holidays.status',string='Leave Type',)
    from_date = fields.Datetime(string='From Date')
    to_date = fields.Datetime(string='To Date')
    state = fields.Char('state')

