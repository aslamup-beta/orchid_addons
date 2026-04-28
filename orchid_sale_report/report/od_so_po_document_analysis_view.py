# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import fields, osv

class od_so_po_document_analysis_view(osv.osv):
    _name = "od.so.po.document.analysis.view"
    _description = "od.so.po.document.analysis.view"
    _auto = False
    _rec_name = 'sale_order_id'
    _columns = {
        'sale_order_id': fields.many2one('sale.order','Sale Order'),
        'purchase_order_id': fields.many2one('purchase.order','Purchase Order'),
#        'so_name':fields.char('So Name'),
#        'po_name':fields.char('Po Name'),

        'so_date': fields.datetime('So Date Order', readonly=True),  # TDE FIXME master: rename into date_order
        'so_date_confirm': fields.date('So Date Confirm', readonly=True),
        'so_product_id': fields.many2one('product.product', 'So Product', readonly=True),
        'so_product_uom': fields.many2one('product.uom', 'So Unit of Measure', readonly=True),
        'so_product_uom_qty': fields.float('#So of Qty', readonly=True),

        'so_partner_id': fields.many2one('res.partner', 'Customer', readonly=True),
        'so_company_id': fields.many2one('res.company', 'So Company', readonly=True),
        'so_user_id': fields.many2one('res.users', 'Salesperson', readonly=True),
        'so_price_total': fields.float('So Total Price', readonly=True),
        'so_delay': fields.float('So Commitment Delay', digits=(16,2), readonly=True),
        'so_categ_id': fields.many2one('product.category','So Product', readonly=True),
        'so_nbr': fields.integer('# So of Lines', readonly=True),  # TDE FIXME master: rename into nbr_lines
        'so_state': fields.selection([
            ('draft', 'Quotation'),
            ('waiting_date', 'Waiting Schedule'),
            ('manual', 'Manual In Progress'),
            ('progress', 'In Progress'),
            ('invoice_except', 'Invoice Exception'),
            ('done', 'Done'),
            ('cancel', 'Cancelled')
            ], 'So Order Status', readonly=True),
        'so_pricelist_id': fields.many2one('product.pricelist', 'So Pricelist', readonly=True),
        'so_analytic_account_id': fields.many2one('account.analytic.account', 'So Analytic Account', readonly=True),
        'so_section_id': fields.many2one('crm.case.section', 'Sales Team'),

        'po_date': fields.datetime('Po Order Date', readonly=True, help="Date on which this document has been created"),  # TDE FIXME master: rename into date_order
        'po_state': fields.selection([('draft', 'Request for Quotation'),
                                     ('confirmed', 'Waiting Supplier Ack'),
                                      ('approved', 'Approved'),
                                      ('except_picking', 'Shipping Exception'),
                                      ('except_invoice', 'Invoice Exception'),
                                      ('done', 'Done'),
                                      ('cancel', 'Cancelled')],'Po Order Status', readonly=True),
        'po_product_id':fields.many2one('product.product', 'Po Product', readonly=True),
        'po_picking_type_id': fields.many2one('stock.warehouse', 'Po Warehouse', readonly=True),
        'po_location_id': fields.many2one('stock.location', 'Po Destination', readonly=True),
        'po_partner_id':fields.many2one('res.partner', 'Supplier', readonly=True),
        'po_pricelist_id':fields.many2one('product.pricelist', 'Po Pricelist', readonly=True),
        'po_date_approve':fields.date('Po Date Approved', readonly=True),
        'po_expected_date':fields.date('Po Expected Date', readonly=True),
        'po_validator' : fields.many2one('res.users', 'Po Validated By', readonly=True),
        'po_product_uom' : fields.many2one('product.uom', 'Po Reference Unit of Measure', required=True),
        'po_company_id':fields.many2one('res.company', 'Po Company', readonly=True),
        'po_user_id':fields.many2one('res.users', 'Po Responsible', readonly=True),
        'po_delay':fields.float('Po Days to Validate', digits=(16,2), readonly=True),
        'po_delay_pass':fields.float('Po Days to Deliver', digits=(16,2), readonly=True),
        'po_quantity': fields.integer('Po Unit Quantity', readonly=True),  # TDE FIXME master: rename into unit_quantity
        'po_price_total': fields.float('Po Total Price', readonly=True),
        'po_price_average': fields.float('Po Average Price', readonly=True, group_operator="avg"),
        'po_negociation': fields.float('Po Purchase-Standard Price', readonly=True, group_operator="avg"),
        'po_price_standard': fields.float('Po Products Value', readonly=True, group_operator="sum"),
        'po_nbr': fields.integer('# Po of Lines', readonly=True),  # TDE FIXME master: rename into nbr_lines
        'po_category_id': fields.many2one('product.category', 'Po Category', readonly=True)








        
    }
    def _select(self):
        select_str = """
              SELECT ROW_NUMBER () OVER (ORDER BY so.id ) AS id,
              so.id as sale_order_id,

              sorpt.date as so_date,
              sorpt.date_confirm as so_date_confirm,
              sorpt.product_id as so_product_id,
              sorpt.product_uom as so_product_uom,
              sorpt.product_uom_qty as so_product_uom_qty,
              sorpt.partner_id as so_partner_id,
              sorpt.company_id as so_company_id,
              sorpt.user_id as so_user_id,


              sorpt.price_total as so_price_total,
              sorpt.delay as so_delay,
              sorpt.categ_id as so_categ_id,
              sorpt.nbr as so_nbr,
              sorpt.state as so_state,
              sorpt.pricelist_id as so_pricelist_id,
              sorpt.analytic_account_id as so_analytic_account_id,
              sorpt.section_id as so_section_id,


              porpt.date as po_date,
              porpt.state as po_state,
              porpt.product_id as po_product_id,
              porpt.picking_type_id as po_picking_type_id,
              porpt.location_id as po_location_id,
              porpt.partner_id as po_partner_id,
              porpt.pricelist_id as po_pricelist_id,
              porpt.date_approve as po_date_approve,


              porpt.expected_date as po_expected_date,
              porpt.validator as po_validator,
              porpt.product_uom as po_product_uom,
              porpt.company_id as po_company_id,
              porpt.user_id as po_user_id,
              porpt.delay as po_delay,
              porpt.delay_pass as po_delay_pass,
              porpt.quantity as po_quantity,


              porpt.price_total as po_price_total,
              porpt.price_average as po_price_average,
              porpt.negociation as po_negociation,
              porpt.price_standard as po_price_standard,
              porpt.nbr as po_nbr,
              porpt.category_id as po_category_id,

              po.id as purchase_order_id
        """
        return select_str
#sl.date_planned as date_planned
    def _from(self):
        from_str = """
                sale_order so
        """
        return from_str

    def _group_by(self):
        group_by_str = """
            GROUP BY so.id,
            po.id,
            sorpt.date,
            sorpt.date_confirm,
            sorpt.product_id,
            sorpt.product_uom,
            sorpt.product_uom_qty,
            sorpt.partner_id,
            sorpt.company_id,
            sorpt.user_id,
            sorpt.price_total,
            sorpt.delay,
            sorpt.categ_id,
            sorpt.nbr,
            sorpt.state,
            sorpt.pricelist_id,
            sorpt.analytic_account_id,
            sorpt.section_id,
            porpt.date,
            porpt.state,
            porpt.product_id,
            porpt.picking_type_id,
            porpt.location_id,
            porpt.partner_id,
            porpt.pricelist_id,
            porpt.date_approve,


            porpt.expected_date,
            porpt.validator,
            porpt.product_uom,
            porpt.company_id,
            porpt.user_id,
            porpt.delay,
            porpt.delay_pass,
            porpt.quantity,


            porpt.price_total,
            porpt.price_average,
            porpt.negociation,
            porpt.price_standard,
            porpt.nbr,
            porpt.category_id


        """
        return group_by_str


    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM  %s 
LEFT OUTER JOIN purchase_order po ON po.origin=so.name
LEFT OUTER JOIN sale_report sorpt ON sorpt.order_id=so.id
LEFT OUTER JOIN purchase_report porpt ON porpt.order_id=so.id

  %s
            )""" % (self._table, self._select(), self._from(), self._group_by()))























