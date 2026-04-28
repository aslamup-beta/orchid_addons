from openerp.report import report_sxw
from openerp.tools.translate import _
from openerp.addons.account.report.account_financial_report import report_account_common
from openerp.osv import osv
class report_account_common(report_account_common):

    def __init__(self, cr, uid, name, context=None):
        super(report_account_common, self).__init__(cr, uid, name, context=context)
        self.context = context

class report_financial_od1(osv.AbstractModel):
    _name = 'report.account.report_financial_od1'
    _inherit = 'report.abstract_report'
    _template = 'account.report_financial_od1'
    _wrapped_report_class = report_account_common
    
    
class report_financial_od2(osv.AbstractModel):
    _name = 'report.account.report_financial_od2'
    _inherit = 'report.abstract_report'
    _template = 'account.report_financial_od2'
    _wrapped_report_class = report_account_common
    
class report_financial_od3(osv.AbstractModel):
    _name = 'report.account.report_financial_od3'
    _inherit = 'report.abstract_report'
    _template = 'account.report_financial_od3'
    _wrapped_report_class = report_account_common
    
class report_financial_od4(osv.AbstractModel):
    _name = 'report.account.report_financial_od4'
    _inherit = 'report.abstract_report'
    _template = 'account.report_financial_od4'
    _wrapped_report_class = report_account_common