#-*- coding:utf-8 -*-
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import datetime
from datetime import timedelta
from openerp import SUPERUSER_ID

#import time
class hr_expense_expense(osv.osv):
    _inherit = 'hr.expense.expense'
    _columns = {
        'state': fields.selection([
            ('draft', 'New'),
            ('cancelled', 'Refused'),
            ('confirm', 'Waiting Approval'),
            ('second_approval', 'Second Approval'),
            ('accepted', 'Approved'),
            ('done', 'Waiting Payment'),
            ('paid', 'Paid'),
            ],
            'Status', readonly=True, track_visibility='onchange', copy=False,
            help='When the expense request is created the status is \'Draft\'.\n It is confirmed by the user and request is sent to admin, the status is \'Waiting Confirmation\'.\
            \nIf the admin accepts it, the status is \'Accepted\'.\n If the accounting entries are made for the expense request, the status is \'Waiting Payment\'.'),
    }
