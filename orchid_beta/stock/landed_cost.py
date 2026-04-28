# -*- coding: utf-8 -*-
from openerp import models, fields, api
class stock_landed_cost(models.Model):
    _inherit = "stock.landed.cost"

    def od_send_mail(self,cr,uid,ids,context=None):
        data = self.browse(cr,uid,ids,context=context)
        pickings = []
        for picking in data.picking_ids:

            pickings.append(picking.name)
        vals = {'name':data.name,'pickings':pickings}
        company_id = data.od_company_id and data.od_company_id.id
        template = 'od_landed_cost_creation_email_mail'
        if company_id == 6:
            template = template + '_saudi'
        template_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'orchid_beta', template)[1]

        ctx =context.copy()
        ctx['data'] = vals
        self.pool.get('email.template').send_mail(cr, uid, template_id, uid, force_send=False, context=ctx)


    def create(self,cr,uid,vals,context=None):
        res = super(stock_landed_cost,self).create(cr,uid,vals,context=context)
        self.od_send_mail(cr,uid,res,context=context)
        return res
