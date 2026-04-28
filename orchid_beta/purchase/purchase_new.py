# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from datetime import datetime
from openerp.exceptions import Warning
class Purchase(models.Model):
    _inherit = 'purchase.order'
    
    @api.one 
    @api.depends('od_discount','amount_untaxed','amount_tax')
    def _compute_total(self):
        self.bt_amount_total = self.amount_untaxed + self.amount_tax - self.od_discount
    
    
    STATE_SELECTION = [
        ('draft', 'Draft PO'),
        ('sent', 'RFQ'),
        ('bid', 'Bid Received'),
        ('submit', 'Submitted'),('first_approval','First Approval'),('second_approval','Second Approval'),
        ('confirmed', 'Waiting Approval'),
        ('approved', 'Purchase Confirmed'),
        ('except_picking', 'Shipping Exception'),
        ('except_invoice', 'Invoice Exception'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ]

    READONLY_STATES = {
        'submit':[('readonly', True)],
        'first_approval': [('readonly', True)],
        'second_approval': [('readonly', True)],
        
    }
    
    
    def get_id_from_param(self,param):
        parameter_obj = self.env['ir.config_parameter']
        key =[('key', '=', param)]
        param_obj = parameter_obj.search(key)
        if not param_obj:
            raise Warning(_('Settings Warning!'),_('NoParameter Not defined\nconfig it in System Parameters with %s'%param))
        result_id = param_obj.od_model_id and param_obj.od_model_id.id or False
        return result_id
    
    def get_default_user(self,name):
        company_id = self.env.user.company_id.id
        param = name+'_approval_user'
        if company_id == 6:
            param = param + '_saudi'
        return self.get_id_from_param(param)
    
    def get_first_approval_user(self):
        return self.get_default_user('first')
    def get_second_approval_user(self):
        return self.get_default_user('second')
    def get_confirm_approval_user(self):
        return self.get_default_user('confirm')
    def get_warehouse_approval_user(self):
        return self.get_default_user('warehouse')
    
    od_select_all = fields.Boolean("Select All")
    bt_amount_total = fields.Float(string="Total",compute='_compute_total')
    
    first_approval_id = fields.Many2one('res.users',string="First Approval",states=READONLY_STATES,default=get_first_approval_user)
    second_approval_id = fields.Many2one('res.users',string="Second Approval",states=READONLY_STATES,default=get_second_approval_user)
    confirmation_id = fields.Many2one('res.users',string="Confirmation",states=READONLY_STATES,default=get_confirm_approval_user)
    warehouse_user_id = fields.Many2one('res.users',string="Warehouse User",states=READONLY_STATES,default=get_warehouse_approval_user)
    state = fields.Selection(STATE_SELECTION,string="Status",track_visibility='always')
    bt_purchase_log_lines = fields.One2many('purchase.order.log','order_id',string="Purchase Order Log")
    
    od_cost_sheet_id = fields.Many2one('od.cost.sheet',string="Cost Sheet")
    od_cost_centre_id = fields.Many2one('od.cost.centre',string="Cost Center")
    od_branch_id =  fields.Many2one('od.cost.branch',string="Branch")
    od_division_id = fields.Many2one('od.cost.division',string="Division")
    project_id  = fields.Many2one('account.analytic.account',string="Analytic Account/Project")
    od_cost_saving = fields.Boolean("Cost Saving", copy=False)
    od_po_lines_submit_log = fields.One2many('od.po.line.submit.log','order_id',string="Purchase Order Lines Submit Log")
    od_manual_jv_ref = fields.Char("JV Number", copy=False)
    od_part_delvry = fields.Selection([('allowed', 'Allowed'), ('not_allowed', 'Not Allowed')], string='Partial Delivery')
    
    
    def check_user_approval_access(self,user_id):
        uid = self._uid
        user_pool =self.env['res.users']
        user_obj = user_pool.browse(user_id)
        if uid ==101:
            return True
        if  uid != user_id:
            raise Warning("You are not allowed to do this action on this Purchase Order, Please ask %s to do this."%user_obj.name)
        return uid == user_id
    
    def write_purchase_log(self,state,next_user_id):
        user_id = self._uid 
        date = str(datetime.now())
        self.bt_purchase_log_lines = [{'state':state,'date':date,'user_id':user_id,'next_user_id':next_user_id and next_user_id.id}]
    
    @api.multi    
    def create_po_line_submit_log(self):
        po_line_submit_log =self.env['od.po.line.submit.log']
        for line in self.order_line:
            if not line.account_analytic_id:
                raise Warning("Please Link Analytic Account On All Purchase Order Lines")
            vals = {'order_id': line.order_id.id,
                    'product_id': line.product_id.id,
                    'qty':line.product_qty,
                    'price_unit': line.od_gross,
                    'disc':line.discount
                }
            po_line_submit_log.create(vals)
        return True
    
    @api.multi    
    def compare_cost_saving(self):
        po_line_submit_log =self.env['od.po.line.submit.log']
        for line in self.order_line:
            key =[('order_id', '=', line.order_id.id),('product_id', '=', line.product_id.id), ('qty', '=', line.product_qty)]
            po_line_log = po_line_submit_log.search(key,limit=1)
            if po_line_log:
                log_unit_price = po_line_log.price_unit
                log_disc = po_line_log.disc
                if line.od_gross < log_unit_price or line.discount > log_disc:
                    self.write({'od_cost_saving':True})
        return True
    
            
#     def wkf_submit(self):
#         self.write({'state':'submit'})
#         self.wr
    
    @api.onchange('od_select_all')
    def onchange_od_select_all(self):
        if self.od_select_all:
            for x in self.order_line:
                x.od_select = True
        else:
            for x in self.order_line:
                x.od_select = False
    @api.multi
    def od_delete_lines(self):
        for line in self.order_line:
            if line.od_select:
                line.unlink()
    
class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    od_select = fields.Boolean("#")
    
class PurchaseOrderLog(models.Model):
    _name ="purchase.order.log"
    order_id = fields.Many2one('purchase.order',string="Purchase Order")
    state = fields.Selection([('created','Created'),('submit','Submitted'),('first','First Approval'),('second','Second Approval'),('confirm','Confirmed')])
    user_id = fields.Many2one('res.users',string="User")
    date = fields.Datetime(string="Date Time")
    next_user_id = fields.Many2one('res.users',string="Sent To")
    
class PurchaseOrderLineSubmitLog(models.Model):
    _name ="od.po.line.submit.log"
    
    order_id = fields.Many2one('purchase.order',string="Purchase Order")
    product_id = fields.Many2one('product.product',string="Product")
    qty = fields.Float(string="Quantity")
    price_unit = fields.Float(string="Unit Price")
    disc = fields.Float(string="Discount")
    
    
    