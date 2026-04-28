# -*- coding: utf-8 -*-
import openerp
from openerp.addons.crm import crm
from openerp.osv import fields, osv
from openerp import tools
from openerp.tools.translate import _
from openerp.tools import html2plaintext


class crm_helpdesk(osv.osv):
    _inherit = "crm.helpdesk"
    _columns = {
        'od_ref3': fields.reference('Reference 3', selection=openerp.addons.base.res.res_request.referencable_models),
        'od_ref4': fields.reference('Reference 4', selection=openerp.addons.base.res.res_request.referencable_models),
    }
