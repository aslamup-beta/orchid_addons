from openerp.osv import osv,fields
class project_task(osv.osv):
    _inherit = 'project.task'
    _columns = {
                  'od_opp_id':fields.many2one('crm.lead','Lead'),
                }