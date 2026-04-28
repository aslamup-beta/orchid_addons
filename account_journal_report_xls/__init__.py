# -*- encoding: utf-8 -*-
##############################################################################

try:
    from . import account_journal
    from . import wizard
    from . import report
except ImportError:
    import logging
    logging.getLogger('openerp.module').warning('report_xls not available in addons path. account_financial_report_webkit_xls will not be usable')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
