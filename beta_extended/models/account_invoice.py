# -*- coding: utf-8 -*-

import itertools
from lxml import etree

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp
from openerp.tools import amount_to_text_en
# from . import amount_to_ar
from pprint import pprint
from openerp import tools
from itertools import groupby

from openerp.tools.translate import _
from openerp import models, fields, api
from datetime import date, timedelta, datetime


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.onchange('payment_term')
    def onchange_payment_term(self):
        if self.type == 'in_invoice' and self.company_id.id == 6:
            if self.payment_term and self.date_invoice:
                no_of_days = self.payment_term.no_of_days
                due_date_with_delta = datetime.strptime(self.date_invoice, '%Y-%m-%d') + timedelta(days=no_of_days)
                if due_date_with_delta:
                    self.date_due = str(due_date_with_delta)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.onchange('account_id')
    def onchange_line_account_id(self):
        if self.account_id:
            if self.account_id.od_branch_id:
                self.od_branch_id = self.account_id and self.account_id.od_branch_id or False
            else:
                self.od_branch_id = False
