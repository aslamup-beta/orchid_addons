# -*- coding: utf-8 -*-

import time
from openerp.report import report_sxw
from openerp import pooler

class journal_entry(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(journal_entry, self).__init__(cr, uid, name, context=context)
        self._invoiceNumber = ''
        self.localcontext.update( 
                                  {
                                   'time': time,
                                   'getLines': self._lines_get,
                                   'invoice' : self._invoice,
                                  }
                                )
        self.context = context
    
    def _invoice(self):
        return self._invoiceNumber
    
    def _lines_get(self, move):
        moveline_obj = pooler.get_pool(self.cr.dbname).get('account.move.line')
        movelines = moveline_obj.search(self.cr, self.uid,[('move_id','=',move.id)])
        movelines = moveline_obj.browse(self.cr, self.uid, movelines)
        
        # Set Invoice Number to self._invoiceNumber
        invoice_obj = pooler.get_pool(self.cr.dbname).get('account.invoice')
        invoiceLine = invoice_obj.search(self.cr, self.uid,[('move_id','=',move.id)])
        if len(invoice_obj.browse(self.cr, self.uid, invoiceLine)):
            self._invoiceNumber = invoice_obj.browse(self.cr, self.uid, invoiceLine)[0]['number']
        else:
            self._invoiceNumber = ''
        
        return movelines
    
report_sxw.report_sxw('report.journal_entry', 'account.move',
                      'addons/orchid_acc_voucher/reports/journal_entry.rml',
                      parser=journal_entry)
        
        
        
        
