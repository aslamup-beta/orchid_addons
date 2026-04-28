# -*- coding: utf-8 -*-
from openerp.osv import osv, fields
from openerp.tools.misc import attrgetter

class ir_config_parameter(osv.osv):
    _inherit = 'ir.config_parameter'

    def onchange_od_model_id(self, cr, uid,ids, od_model_id,context=None):
        res = {}
        if od_model_id:
            data = od_model_id.split(',')
            value=self.pool.get(str(data[0])).browse(cr,uid,int(data[1]),context).name
            res = {'value':{'value':value}}
        return res

    def _models_field_get(self, cr, uid, field_key, field_value, context=None):
        get = attrgetter(field_key, field_value)
        obj = self.pool.get('ir.model.fields')
        ids = obj.search(cr, uid, [], context=context)
        res = set()
        for o in obj.browse(cr, uid, ids, context=context):
            res.add(get(o))
        return list(res)

    def _models_get(self, cr, uid, context=None):
        return self._models_field_get(cr, uid, 'model', 'model_id.name', context)

    _columns = {
        'od_model_id' : fields.reference('Ref Value/Table',selection=_models_get,size=128,help="Select the Resource/Model/Table from where the data has to get"),
    }
