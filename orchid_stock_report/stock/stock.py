from openerp import models, fields, api, _

class stock_report(models.Model):
    _inherit ='stock.move'

    def od_get_reserved_pickings(self,cr,uid,ids,context=None):
        product_id  = self.browse(cr,uid,ids).product_id and self.browse(cr,uid,ids).product_id.id or False
        res=self.search(cr,uid,[('product_id','=',product_id),('reserved_quant_ids','!=',False)])
        pick_ids = [move.picking_id.id for move in self.browse(cr,uid,res)]
        pick_ids=list(set(pick_ids))
        domain =[('id','in',pick_ids)]
        result = self.pool['ir.actions.act_window'].search(cr,uid,[('name','=','Picking Tree')])[0]
        result = self.pool['ir.actions.act_window'].read(cr, uid, [result], context=context)[0]
        result['domain'] = domain
        return result
