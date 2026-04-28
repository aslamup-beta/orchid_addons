# -*- coding: utf-8 -*-


from openerp.osv import fields,osv
from openerp import tools


class brand_rpt_wiz(osv.osv_memory):
    _name ='brand.rpt.wiz'
    
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id
    _columns = {
        'company_id': fields.many2one('res.company','Company',required=True),
        'date_from': fields.date('Supplier PO Order Date From', help="Date From"),
        'date_to':fields.date('Supplier PO Order Date To', help="Date From"),
        'od_pdt_brand_ids': fields.many2many('od.product.brand','wiz_brand_vendeor_rel', 'wiz_id', 'brand_id', 'Brand'),
        'partner_ids': fields.many2many('res.partner','wiz_partner_sup_vendor_rel', 'wiz_id', 'partner_id', 'Supplier',domain=[('is_company','=',True),('supplier','=',True)]),
        'customer_ids':fields.many2many('res.partner','wiz_partner_cust_vendor_rel', 'wiz_id', 'partner_id', 'Customer',domain=[('is_company','=',True),('supplier','=',True)]),
        'project_ids':fields.many2many('account.analytic.account','wiz_brand_analytic_rel', 'wiz_id', 'project_id', 'Projects'),
        }
    _defaults ={
    'company_id': _get_default_company,
        }
    def export_rpt(self,cr,uid,ids,context=None):
        tools.sql.drop_view_if_exists(cr, 'od_vendor_brand_rpt')
        company_id = self.browse(cr,uid,ids).company_id and self.browse(cr,uid,ids).company_id.id
        where ="where s.company_id=%s AND s.state  in ('approved','done','except_picking','except_invoice','second_approval')"%company_id
        partner_ids =[part.id for part in self.browse(cr,uid,ids).partner_ids]
        customer_ids = [part.id for part in self.browse(cr,uid,ids).customer_ids]
        od_pdt_brand_ids = [brand.id for brand in self.browse(cr,uid,ids).od_pdt_brand_ids]
        project_ids = [pr.id for pr in self.browse(cr,uid,ids).project_ids]
        date_from = self.browse(cr,uid,ids).date_from 
        date_to = self.browse(cr,uid,ids).date_to
        
        if date_from:
            where = where + " AND s.date_order>='%s'"%date_from 
        
        if date_to:
            date_to = date_to +' 23:59:59'
            where = where + " AND s.date_order<='%s'"%date_to
        if partner_ids:
            if len(partner_ids) ==1:
                where = where+' AND s.partner_id=%s'%partner_ids[0]
            else:
                where = where+' AND s.partner_id in %s'%str(tuple(partner_ids))
        if customer_ids:
            if len(customer_ids) ==1:
                where = where+' AND s.od_customer_id=%s'%customer_ids[0]
            else:
                where = where+' AND s.od_customer_id in %s'%str(tuple(customer_ids))
        if od_pdt_brand_ids:
            if len(od_pdt_brand_ids) ==1:
                where = where+' AND t.od_pdt_brand_id=%s'%od_pdt_brand_ids[0]
            else:
                where = where+' AND t.od_pdt_brand_id in %s'%str(tuple(od_pdt_brand_ids))
        if project_ids:
            if len(project_ids) ==1:
                where = where+' AND s.project_id=%s'%project_ids[0]
            else:
                where = where+' AND s.project_id in %s'%str(tuple(project_ids))
                
                
                
                
        query ="""
            create or replace view od_vendor_brand_rpt as (
                WITH currency_rate (currency_id, rate, date_start, date_end) AS (
                    SELECT r.currency_id, r.rate, r.name AS date_start,
                        (SELECT name FROM res_currency_rate r2
                        WHERE r2.name > r.name AND
                            r2.currency_id = r.currency_id
                         ORDER BY r2.name ASC
                         LIMIT 1) AS date_end
                    FROM res_currency_rate r
                )
                select
                    min(l.id) as id,
                    s.date_order as date,
                    s.state,
                    l.order_id,
                    s.date_approve,
                    s.project_id,
                    s.minimum_planned_date as expected_date,
                    s.dest_address_id,
                    s.pricelist_id,
                    s.validator,
                    spt.warehouse_id as picking_type_id,
                    s.partner_id as partner_id,
                    s.od_customer_id as customer_id,
                    s.create_uid as user_id,
                    s.company_id as company_id,
                    l.product_id,
                    t.categ_id as category_id,
                    t.uom_id as product_uom,
                    t.od_pdt_brand_id,
                    s.location_id as location_id,
                    sum(l.product_qty/u.factor*u2.factor) as quantity,
                    extract(epoch from age(s.date_approve,s.date_order))/(24*60*60)::decimal(16,2) as delay,
                    extract(epoch from age(l.date_planned,s.date_order))/(24*60*60)::decimal(16,2) as delay_pass,
                    count(*) as nbr,
                    sum(l.price_unit/cr.rate*l.product_qty)::decimal(16,2) as price_total,
                    avg(100.0 * (l.price_unit/cr.rate*l.product_qty) / NULLIF(ip.value_float*l.product_qty/u.factor*u2.factor, 0.0))::decimal(16,2) as negociation,
                    sum(ip.value_float*l.product_qty/u.factor*u2.factor)::decimal(16,2) as price_standard,
                    (sum(l.product_qty*l.price_unit/cr.rate)/NULLIF(sum(l.product_qty/u.factor*u2.factor),0.0))::decimal(16,2) as price_average
                from purchase_order_line l
                    join purchase_order s on (l.order_id=s.id)
                        left join product_product p on (l.product_id=p.id)
                            left join product_template t on (p.product_tmpl_id=t.id)
                            LEFT JOIN ir_property ip ON (ip.name='standard_price' AND ip.res_id=CONCAT('product.template,',t.id) AND ip.company_id=s.company_id)
                    left join product_uom u on (u.id=l.product_uom)
                    left join product_uom u2 on (u2.id=t.uom_id)
                    left join stock_picking_type spt on (spt.id=s.picking_type_id)
                    join currency_rate cr on (cr.currency_id = s.currency_id and
                        cr.date_start <= coalesce(s.date_order, now()) and
                        (cr.date_end is null or cr.date_end > coalesce(s.date_order, now())))
                    %s
                group by
                    s.company_id,
                    s.create_uid,
                    s.partner_id,
                    s.project_id,
                   s.od_customer_id,
                    u.factor,
                    s.location_id,
                    l.price_unit,
                    s.date_approve,
                    l.date_planned,
                    l.order_id,
                    l.product_uom,
                    s.minimum_planned_date,
                    s.pricelist_id,
                    s.validator,
                    s.dest_address_id,
                    l.product_id,
                    t.categ_id,
                    t.od_pdt_brand_id,
                    s.date_order,
                    s.state,
                    spt.warehouse_id,
                    u.uom_type,
                    u.category_id,
                    t.uom_id,
                    u.id,
                    u2.factor
            )
            
        """%where
        
        cr.execute(query)
        return {
            
            'name': 'Principle Vendor Report',
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'od.vendor.brand.rpt',
            'type': 'ir.actions.act_window',
            'context':{'search_default_brand':1,'search_default_po':1}
        }
        
    

class od_vendor_brand_rpt(osv.osv):
    _name = "od.vendor.brand.rpt"
    _description = "Vendor Brand Report"
    _auto = False
    
    
    
    
    def btn_open_po(self,cr,uid,ids,context=None):
        obj = self.browse(cr,uid,ids)
        order_id = obj.order_id and obj.order_id.id or False
       
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'purchase.order',
                'res_id':order_id,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }
    
    
    _columns = {
        'date': fields.datetime('Order Date', readonly=True, help="Date on which this document has been created"),  # TDE FIXME master: rename into date_order
        'state': fields.selection([('draft', 'Request for Quotation'),
                                   ('second_approval','Second Approval'),
                                     ('confirmed', 'Waiting Supplier Ack'),
                                      ('approved', 'Approved'),
                                      
                                      ('except_picking', 'Shipping Exception'),
                                      ('except_invoice', 'Invoice Exception'),
                                      ('done', 'Done'),
                                      ('cancel', 'Cancelled')],'Order Status', readonly=True),
        'product_id':fields.many2one('product.product', 'Product', readonly=True),
        'picking_type_id': fields.many2one('stock.warehouse', 'Warehouse', readonly=True),
        'location_id': fields.many2one('stock.location', 'Destination', readonly=True),
        'order_id':fields.many2one('purchase.order',string="Purchase Order",readonly=True),
        'partner_id':fields.many2one('res.partner', 'Supplier', readonly=True),
        'customer_id':fields.many2one('res.partner', 'Customer', readonly=True),
        'project_id':fields.many2one('account.analytic.account','Project',readonly=True),
        'pricelist_id':fields.many2one('product.pricelist', 'Pricelist', readonly=True),
        'date_approve':fields.date('Date Approved', readonly=True),
        'expected_date':fields.date('Expected Date', readonly=True),
        'validator' : fields.many2one('res.users', 'Validated By', readonly=True),
        'product_uom' : fields.many2one('product.uom', 'Reference Unit of Measure', required=True),
        'company_id':fields.many2one('res.company', 'Company', readonly=True),
        'user_id':fields.many2one('res.users', 'Responsible', readonly=True),
        'delay':fields.float('Days to Validate', digits=(16,2), readonly=True),
        'delay_pass':fields.float('Days to Deliver', digits=(16,2), readonly=True),
        'quantity': fields.integer('Unit Quantity', readonly=True),  # TDE FIXME master: rename into unit_quantity
        'price_total': fields.float('Total Cost', readonly=True),
        'price_average': fields.float('Average Price', readonly=True, group_operator="avg"),
        'negociation': fields.float('Purchase-Standard Price', readonly=True, group_operator="avg"),
        'price_standard': fields.float('Products Value', readonly=True, group_operator="sum"),
        'nbr': fields.integer('# of Lines', readonly=True),  # TDE FIXME master: rename into nbr_lines
        'category_id': fields.many2one('product.category', 'Category', readonly=True),
        'od_pdt_brand_id': fields.many2one('od.product.brand','Brand'),


    }




