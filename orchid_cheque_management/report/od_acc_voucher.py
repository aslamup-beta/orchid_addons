# -*- coding: utf-8 -*-
import time

from openerp.report import report_sxw

class od_acc_voucher(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(od_acc_voucher, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time, 
        })
report_sxw.report_sxw('report.od.account.voucher', 'account.voucher', 'addons/orchid_cheque_management/report/od_acc_voucher_print.rml', parser=od_acc_voucher, header="external")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

