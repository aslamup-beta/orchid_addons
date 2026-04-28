from openerp.osv import fields,osv 

class crm_lead(osv.osv):
    _inherit = 'crm.lead'
    
     
    def _od_task_count(self, cr, uid, ids, field_name, arg, context=None):
        res ={}
        for obj in self.browse(cr, uid, ids, context):
            shipment_ids = self.pool.get('project.task').search(cr, uid, [('od_opp_id', '=', obj.id)])
            if shipment_ids:
                res[obj.id] = len(shipment_ids)
        return res
    _columns = {
                'od_task_count':fields.function(_od_task_count,string='Tasks',type='integer'),
                }
     
    