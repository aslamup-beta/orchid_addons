import re
import time
import math

from openerp import api, fields as fields2
from openerp import tools
from openerp.osv import fields, osv
from openerp.tools import float_round, float_is_zero, float_compare
from openerp.tools.translate import _

CURRENCY_DISPLAY_PATTERN = re.compile(r'(\w+)\s*(?:\((.*)\))?')
class res_currency(osv.osv):
    _inherit = "res.currency"
    def _current_rate(self, cr, uid, ids, name, arg, context=None):
        return self._get_current_rate(cr, uid, ids, context=context)
 
    def _current_rate_silent(self, cr, uid, ids, name, arg, context=None):
        return self._get_current_rate(cr, uid, ids, raise_on_no_rate=False, context=context)
 
    def _get_current_rate(self, cr, uid, ids, raise_on_no_rate=True, context=None):
        if context is None:
            context = {}
        res = {}
 
        date = context.get('date') or time.strftime('%Y-%m-%d')
        for id in ids:
            cr.execute('SELECT rate FROM res_currency_rate '
                       'WHERE currency_id = %s '
                         'AND name <= %s '
                       'ORDER BY name desc LIMIT 1',
                       (id, date))
            if cr.rowcount:
                res[id] = cr.fetchone()[0]
            elif not raise_on_no_rate:
                res[id] = 0
            else:
                currency = self.browse(cr, uid, id, context=context)
                raise osv.except_osv(_('Error!'),_("No currency rate associated for currency '%s' for the given period" % (currency.name)))
        return res
    _columns = {
              'rate': fields.function(_current_rate, string='Current Rate', digits=(12,20),
            help='The rate of the currency to the currency of rate 1.'),
      
                }
class res_currency_rate(osv.osv):
    _inherit ="res.currency.rate"
    _columns = {
      
        'rate': fields.float('Rate', digits=(12, 20), help='The rate of the currency to the currency of rate 1'),
      
    }