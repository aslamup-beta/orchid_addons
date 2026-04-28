# -*- coding: utf-8 -*-
import time
from openerp.osv import osv
from openerp.report import report_sxw
from common_report_header import common_report_header


class general_ledger(report_sxw.rml_parse, common_report_header):
    _inherit = 'report.account.general.ledger'

    def _get_account(self, data):
#        if data['model'] == 'account.account':
#            return self.pool.get('account.account').browse(self.cr, self.uid, data['form']['id']).company_id.name
        return super(general_ledger ,self)._get_account(data)
