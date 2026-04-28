from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import datetime
class purchase_order(osv.osv):
    _inherit ='purchase.order'
    _columns ={
               'od_customer_id':fields.many2one('res.partner','Customer'),
               'od_custom_duty':fields.float('Custom Duty'),
               'od_freight_charge':fields.float('Freight Charge'),
               'od_discount':fields.float('Discount',readonly=True,states={'draft':[('readonly',False)]})
               }


    def od_send_purchase_confirmation_mail(self,cr,uid,ids,context=None):
        data = self.browse(cr,uid,ids,context=context)
        purchase_val = {'name':data.name}
        company_id = data.company_id and data.company_id.id
        template = 'od_purchase_order_confirmed_email_mail'
        if company_id == 6:
            template = template + '_saudi'
        template_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'orchid_beta', template)[1]
        ctx = context.copy()
        ctx['data'] = purchase_val
        self.pool.get('email.template').send_mail(cr, uid, template_id, uid, force_send=True, context=ctx)
    def action_picking_create(self, cr, uid, ids, context=None):
        for order in self.browse(cr, uid, ids):
            order_type_id = order.od_order_type_id and order.od_order_type_id.id
            picking_vals = {
                'picking_type_id': order.picking_type_id.id,
                'partner_id': order.partner_id.id,
                'date': max([l.date_planned for l in order.order_line]),
                'origin': order.name,
                'od_order_type_id':order_type_id,
                'od_cost_sheet_id': order.od_cost_sheet_id and order.od_cost_sheet_id.id or False,
                'od_cost_centre_id':order.od_cost_centre_id and order.od_cost_centre_id.id or False,
                'od_branch_id':order.od_branch_id and order.od_branch_id.id or False,
                'od_division_id':order.od_division_id and order.od_division_id.id or False,
                'od_analytic_id':order.project_id and order.project_id.id or False, 
            }
            picking_id = self.pool.get('stock.picking').create(cr, uid, picking_vals, context=context)
            self._create_stock_moves(cr, uid, order, order.order_line, picking_id, context=context)
            self.od_send_purchase_confirmation_mail(cr,uid,ids,context=context)
        return picking_id
    
    def view_invoice(self, cr, uid, ids, context=None):
        purchase_obj = self.browse(cr,uid,ids[0],context)
        od_discount = purchase_obj.od_discount
        date_order = datetime.strptime(purchase_obj.date_order, '%Y-%m-%d %H:%M:%S')
        date = date_order.strftime('%Y-%m-%d')
        amount_total = purchase_obj.amount_total
        check_total = amount_total - od_discount
        result = super(purchase_order,self).view_invoice(cr, uid, ids, context)
        self.pool.get('account.invoice').write(cr,uid,[result['res_id']],{'date_invoice':date,'date_due':date,'od_discount':od_discount,'check_total':check_total})
        return result
