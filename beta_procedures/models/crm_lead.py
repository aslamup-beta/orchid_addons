from openerp.osv import fields, osv
import datetime
from dateutil.relativedelta import relativedelta

class crm_lead(osv.osv):
    _inherit = "crm.lead"
    
#     def _get_date(self, cr, uid, ids, field_name, arg, context=None): 
#         res ={} 
#         expiry_date = ''
#         for li in self.browse(cr, uid, ids, context): 
#             today = datetime.date.today()
#             context = dict(context or {})
#             today_date = datetime.datetime.strptime(str(today), "%Y-%m-%d").date()
#             expiry_date = today_date + relativedelta(days=14)
#             res[li.id] = expiry_date
#         return res
    
    _columns = {
    'od_activity_lines1' : fields.one2many('od.lead.activity.log','lead_id1',string="Work Logs"),
    }
class od_lead_activity_log(osv.osv):
    _name = "od.lead.activity.log"
    _order ='id desc'
      
    _columns = {
    'lead_id1' : fields.many2one('crm.lead',string="Lead"),
    'name' : fields.text(string="Notes"),
    'date' : fields.datetime(string="Date"),
    'user_id' : fields.many2one('res.users',string="User")
    }
    
    _defaults = {
        'date': fields.datetime.now,
        'user_id': lambda obj, cr, uid, context: uid,
    }
