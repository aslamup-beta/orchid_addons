from datetime import date, datetime
from dateutil import relativedelta
import json
import time

from openerp.osv import fields, osv
from openerp.tools.float_utils import float_compare, float_round
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from openerp import SUPERUSER_ID, api
import openerp.addons.decimal_precision as dp
from openerp.addons.procurement import procurement

class stock_quant(osv.osv):
    _inherit = "stock.quant"
    def _get_accounting_data_for_valuation(self, cr, uid, move, context=None):
        journal_id, acc_src, acc_dest, acc_valuation = super(stock_quant,self)._get_accounting_data_for_valuation(cr, uid, move, context=context)
        return journal_id, acc_src, acc_dest, acc_valuation

class stock_move(osv.osv):
    _inherit = "stock.move"
    _columns = {
                'analytic_id':fields.many2one('account.analytic.account','Analytic Account')
                }
