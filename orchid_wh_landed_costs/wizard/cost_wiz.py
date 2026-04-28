# -*- coding: utf-8 -*-
from openerp import models, fields, api
class cost_wiz(models.TransientModel):
    _name = 'cost.wiz'
    def default_get(self, cr, uid, fields, context=None):
        res = super(cost_wiz, self).default_get(cr, uid, fields, context=context)

        cost = context.get('cost')
        res ={'cost':cost}
        return res


    cost = fields.Char("Cost",readonly=True)
