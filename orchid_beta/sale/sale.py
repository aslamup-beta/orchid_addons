from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import datetime
from openerp.exceptions import Warning
import openerp.addons.decimal_precision as dp
class sale_order(osv.osv):
    _inherit ='sale.order'
    _columns ={
               'od_discount':fields.float('Discount',digits_compute=dp.get_precision('Account'),readonly=True),
               'state': fields.selection([
                   ('draft', 'Draft Quotation'),
                   ('sent', 'Quotation Sent'),
                   ('od_approved','Approved'),
                   ('cancel', 'Cancelled'),
                   ('waiting_date', 'Waiting Schedule'),
                   ('progress', 'Sales Order'),
                   ('manual', 'Sale to Invoice'),
                   ('shipping_except', 'Shipping Exception'),
                   ('invoice_except', 'Invoice Exception'),
                   ('done', 'Done'),
                   ], 'Status', readonly=True, copy=False, help="Gives the status of the quotation or sales order.\
                     \nThe exception status is automatically set when a cancel operation occurs \
                     in the invoice validation (Invoice Exception) or in the picking list process (Shipping Exception).\nThe 'Waiting Schedule' status is set when the invoice is confirmed\
                      but waiting for the scheduler to run on the order date.", select=True),

               }

    def od_action_create_proc(self,cr,uid,ids,context=None):
        """Create the required procurements to supply sales order lines, also connecting
        the procurements to appropriate stock moves in order to bring the goods to the
        sales order's requested location.

        :return: True
        """
        context = context or {}
        context['lang'] = self.pool['res.users'].browse(cr, uid, uid).lang
        val ={'state':'od_approved'}
        lines = []
        for order in self.browse(cr, uid, ids, context=context):
            for line in order.order_line:
                lines.append(line.id)
                line.state = 'confirmed'
        if not lines:
            raise Warning("No order lines")
        order.write(val)
        return True
    def od_send_sale_approval_mail(self,cr,uid,ids,context=None):
        data = self.browse(cr,uid,ids,context=context)
        sale_val = {'name':data.name}
        company_id = data.company_id and data.company_id.id
        template = 'od_sale_new_confirmed_email_mail'
        if company_id == 6:
            template = template + '_saudi'
        template_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'orchid_beta', template)[1]
        ctx = context.copy()
        ctx['data'] = sale_val
        self.pool.get('email.template').send_mail(cr, uid, template_id, uid, force_send=False, context=ctx)
    def od_action_approve(self,cr,uid,ids,context=None):
        if not context:
            context = {}
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        # self.od_send_sale_approval_mail(cr,uid,ids,context={})
        self.signal_workflow(cr, uid, ids, 'od_signal_approve')
        self.od_send_sale_approval_mail(cr,uid,ids,context=context)
        return True
    def od_check_invoice(self,cr,uid,ids,context=None):
        data = self.browse(cr,uid,ids)
        order_policy = data.order_policy
        if order_policy == 'picking':
            return False
        return True
    def od_check_exception(self,cr,uid,ids,context=None):
        data = self.browse(cr,uid,ids)
        state = data.state
        order_policy = data.order_policy
        if state == 'approved' and order_policy == 'picking':
            return True
        return False

    def od_check_do(self,cr,uid,ids,contex=None):
        data = self.browse(cr,uid,ids)
        picking = self.pool.get('stock.picking')
        name = data.name
        dom = [('origin','=',name)]
        pickings = picking.search(cr,uid,dom)
        states = [pick.state for pick in picking.browse(cr,uid,pickings)]
        states = [str(item) for item in states]
        for state in states:
            if state != 'cancel':
                raise Warning(_('Please Cancel All Material Request Associated with Sales Order - \'%s\'.') % name)
                return False
        return True
    
    def od_action_cancel(self,cr,uid,ids,context=None):
        if not context:
            context = {}
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        self.signal_workflow(cr, uid, ids, 'od_signal_cancel3')

    def od_action_invoice_create(self,cr,uid,ids,grouped=False, states=['confirmed', 'done', 'exception'], date_invoice = False, context=None):
        if states is None:
            states = ['confirmed', 'done', 'exception']
        res = False
        invoices = {}
        invoice_ids = []
        invoice = self.pool.get('account.invoice')
        obj_sale_order_line = self.pool.get('sale.order.line')
        partner_currency = {}
        # If date was specified, use it as date invoiced, usefull when invoices are generated this month and put the
        # last day of the last month as invoice date
        if date_invoice:
            context = dict(context or {}, date_invoice=date_invoice)
        for o in self.browse(cr, uid, ids, context=context):
            currency_id = o.pricelist_id.currency_id.id
            if (o.partner_id.id in partner_currency) and (partner_currency[o.partner_id.id] <> currency_id):
                raise osv.except_osv(
                    _('Error!'),
                    _('You cannot group sales having different currencies for the same partner.'))

            partner_currency[o.partner_id.id] = currency_id
            lines = []
            for line in o.order_line:
                if line.invoiced:
                    continue
                elif (line.state in states):
                    lines.append(line.id)
            created_lines = obj_sale_order_line.invoice_line_create(cr, uid, lines)
            if created_lines:
                invoices.setdefault(o.partner_invoice_id.id or o.partner_id.id, []).append((o, created_lines))
        if not invoices:
            for o in self.browse(cr, uid, ids, context=context):
                for i in o.invoice_ids:
                    if i.state == 'draft':
                        return i.id
        for val in invoices.values():
            if grouped:
                res = self._make_invoice(cr, uid, val[0][0], reduce(lambda x, y: x + y, [l for o, l in val], []), context=context)
                invoice_ref = ''
                origin_ref = ''
                for o, l in val:
                    invoice_ref += (o.client_order_ref or o.name) + '|'
                    origin_ref += (o.origin or o.name) + '|'
                    self.write(cr, uid, [o.id], {'state': 'progress'})
                    cr.execute('insert into sale_order_invoice_rel (order_id,invoice_id) values (%s,%s)', (o.id, res))
                    self.invalidate_cache(cr, uid, ['invoice_ids'], [o.id], context=context)
                #remove last '|' in invoice_ref
                if len(invoice_ref) >= 1:
                    invoice_ref = invoice_ref[:-1]
                if len(origin_ref) >= 1:
                    origin_ref = origin_ref[:-1]
                invoice.write(cr, uid, [res], {'origin': origin_ref, 'name': invoice_ref})
            else:
                for order, il in val:
                    res = self._make_invoice(cr, uid, order, il, context=context)
                    invoice_ids.append(res)
                    self.write(cr, uid, [order.id], {'state': 'progress'})
                    cr.execute('insert into sale_order_invoice_rel (order_id,invoice_id) values (%s,%s)', (order.id, res))
                    self.invalidate_cache(cr, uid, ['invoice_ids'], [order.id], context=context)
        return res
    def od_action_invoice(self,cr,uid,ids,context=None):
        if not context:
            context = {}
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        self.signal_workflow(cr, uid, ids, 'od_invoice')
        self.write(cr,uid,ids,{'state':'manual'})
