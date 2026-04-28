import time

from openerp.osv import fields, orm


class TaxReportWizard(orm.TransientModel):
    """Will launch tax report and pass required args"""

    #_inherit = "account.common.account.report"
    _inherit = "general.ledger.webkit"
    _name = "od.tax.report"
    _description = "VAT Report"
    
    
    
    def _get_tax_account(self, cr, uid, context=None):
        return self.pool.get('account.account').search(cr, uid ,[('parent_id', 'in', (5723,2172,5719,6661))])
    
    _defaults = {
        'account_ids': _get_tax_account,
    }
    
    def xls_export(self, cr, uid, ids, context=None):
        return self.check_report(cr, uid, ids, context=context)

    def _print_report(self, cr, uid, ids, data, context=None):
        context = context or {}
        if context.get('xls_export'):
            # we update form with display account value
            data = self.pre_print_report(cr, uid, ids, data, context=context)
            
            return {'type': 'ir.actions.report.xml',
                    'report_name': 'account.account_report_tax_report_xls',
                    'datas': data}
        else:
            return super(TaxReportWizard, self)._print_report(cr, uid, ids, data, context=context)