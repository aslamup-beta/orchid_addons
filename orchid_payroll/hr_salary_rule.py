# -*- coding: utf-8 -*-
import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp.osv import fields, osv
from openerp.tools.translate import _

class hr_salary_rule(osv.osv):
    _inherit = 'hr.salary.rule'
    _columns = {
        'od_product_id':fields.many2one('product.template','Product'),
        
    }
    _sql_constraints = [
        ('od_product_id_uniq', 'unique(od_product_id)', 'You Already Selected This Product'),
    ]
    


