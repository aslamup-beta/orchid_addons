# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
from openerp.tools.translate import _
class ir_actions_report_xml(osv.osv):
    _inherit = 'ir.actions.report.xml'
    _columns = {
        'avilable_in_ddl':fields.boolean('Available In DDL',help="Template Names Can be used,\naccount.report_partnerledger_od1,\naccount.report_partnerledger_od2\n,account.report_partnerledger_od3\n,account.report_partnerledger_od4")
    }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
