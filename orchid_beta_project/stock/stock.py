# -*- coding: utf-8 -*-
from openerp import models,fields,api

class stock_picking(models.Model):
    _inherit = 'stock.picking'
    
    @api.one
    def od_get_no_of_lc(self):
        lc_recs = self.env['stock.landed.cost'].search([('picking_ids','in', self.id)])
        self.count_lc = len(lc_recs)
        
    od_notes = fields.Text(string="Notes")
    count_lc = fields.Integer("Count of Landed Cost", compute="od_get_no_of_lc")
    od_delivery_date = fields.Date(string="Date")
    od_delivery_note_no = fields.Char("Delivery Note No.")
    od_cust_po_ref = fields.Char("Customer P.O. Reference")
    od_contact_person = fields.Char("Customer Contact Person")
    od_cell_phone = fields.Char("Customer Cell Phone No.")
    od_beta_pm = fields.Many2one('res.users',"Beta IT Project Manager")
    od_location = fields.Char("Location")
    
    
    @api.multi
    def od_view_landed_cost(self):
        pick_id = self.id
        context = self.env.context
        ctx = context.copy()
        ctx['default_picking_ids'] = [(6,0,[pick_id])]
        if pick_id:
            domain = [('picking_ids','in',pick_id)]
            return {
                'domain':domain,
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'stock.landed.cost',
                'type': 'ir.actions.act_window',
                'context':ctx,
            }   

# class stock_transfer_details(models.TransientModel):
#     _inherit = 'stock.transfer_details'
#     @api.one
#     def do_detailed_transfer(self):
#         res = super(stock_transfer_details,self).do_detailed_transfer()
#         context = self._context
#         active_id = context.get('active_id')
#         picking = self.env['stock.picking']
#         lot = self.env['stock.production.lot']
#         pick_obj = picking.browse(active_id)
#         partner_id = pick_obj.partner_id and pick_obj.partner_id.id
#         print "partner id>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",partner_id
#         for line in self.item_ids:
#             lot_id = line.lot_id and line.lot_id.id or False
#             if lot_id:
#                 lot_obj = lot.browse(lot_id)
#                 lot_obj.write({'od_partner_id':partner_id})
#         return res
