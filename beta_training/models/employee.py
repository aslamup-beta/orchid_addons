# -*- coding: utf-8 -*-

import itertools
from lxml import etree
from openerp.osv import osv
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp
from openerp.tools import amount_to_text_en
# from . import amount_to_ar
from pprint import pprint
from openerp import tools
from itertools import groupby


class hr_employee(models.Model):
    _inherit = "hr.employee"

    def action_view_employee_idp(self, cr, uid, ids, context=None):
        emp_idp_ids = self.pool.get('employee.idp').search(cr, uid, [('employee_id', '=', ids[0])])
        # emp_training_ids = self.env['employee.training.contract'].search([('training_id', '=', self.id)])
        domain = [('id', 'in', emp_idp_ids)]
        # ctx = {'default_training_id': self.id}
        action = self.pool['ir.actions.act_window'].for_xml_id(
            cr, uid, 'beta_training', 'action_open_employee_idp')
        action['domain'] = unicode([('id', 'in', emp_idp_ids)])
        return action
