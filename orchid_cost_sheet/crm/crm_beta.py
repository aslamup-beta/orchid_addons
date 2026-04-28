# -*- coding: utf-8 -*-
from openerp.osv import fields,osv
from openerp.tools.translate import _
class crm_lead(osv.osv):
    _inherit = 'crm.lead'
    _columns = {
        'od_approval_state': fields.selection([('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected'),('request_cancel', 'Requested Cancellation'),('cancelled', 'Cancelled')],
                                 string=' Approval'),
        'od_bdm_user_id': fields.many2one('res.users', 'BDM', select=True, track_visibility='onchange',help="Business Development Manager"),
        'od_responsible_id': fields.many2one('res.users', 'Pre Sales', select=True, track_visibility='onchange',help=" User now handling"),

        'od_lead_bdm_user_id': fields.many2one('res.users', 'Lead BDM', select=True, track_visibility='onchange',help=" Lead Business Development Manager"),
        'od_lead_responsible_id': fields.many2one('res.users', 'Lead Pre Sales', select=True, track_visibility='onchange',help="Lead User now handling"),
        'user_id': fields.many2one('res.users', 'SAM', select=True, track_visibility='onchange',help="Sales Account Manager"),
        'date_deadline': fields.date('Date Deadline', help="Estimate of the date on which the opportunity will be won."),
        'date_action': fields.date('Expected Booking'),
        'od_branch_id':fields.many2one('od.cost.branch',string='Branch', copy=False),
        'od_division_id':fields.many2one('od.cost.division',string='Division', copy=False),
    }
    