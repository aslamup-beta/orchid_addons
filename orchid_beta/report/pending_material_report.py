# -*- coding: utf-8 -*-

from openerp import tools
from openerp.osv import fields,osv

class od_pending_report(osv.osv):
    _name = "od.pending.report"
    _description = "Pending Material"
    _auto = False
    _columns = {
    'order_id' : fields.many2one('sale.order',"Sale Order"),
    'date_order':fields.datetime(string="Date Order"),
    'name':fields.char(string="Description"),
    'product_id':fields.many2one('product.product','Product'),
    'order_qty':fields.float('Ordered Qty'),
    'deliverd_qty':fields.float('Deliverd Qty'),
    'balance_qty':fields.float('Balance Qty'),
    'partner_id':fields.many2one('res.partner','Partner'),
    'project_id':fields.many2one('account.analytic.account',"Analytic Account"),
    'owner_id':fields.many2one('res.users',"Owner"),
    'section_id':fields.many2one('crm.case.section','Sale Team'),
    'company_id':fields.many2one('res.company',"Company"),

    #jm
    'sale_terr_id':fields.many2one('od.partner.territory',string="Sale Territory"),

    }
    _order = "date_order ASC"
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'od_pending_report')
        cr.execute("""
            create or replace view od_pending_report as (
                  SELECT ROW_NUMBER () OVER (ORDER BY line.id ) AS id,order_id,so.date_order,
                  line.name,salesman_id,so.state,product_id,product_uom_qty as order_qty,
                  cl.od_territory_id as sale_terr_id,
                  so.partner_id,so.project_id,so.section_id,cs.reviewed_id as owner_id,so.company_id as company_id,
( SELECT sum(product_uom_qty) FROM stock_move move
          WHERE move.so_line_id=line.id and state ='done') as deliverd_qty,
(product_uom_qty-( SELECT sum(product_uom_qty) FROM stock_move move
          WHERE move.so_line_id=line.id and state ='done')) as balance_qty
 from sale_order_line line

left outer join sale_order so on line.order_id = so.id  
left outer join od_cost_sheet cs on cs.id = so.od_cost_sheet_id

left outer join crm_lead cl on cl.id = cs.lead_id

where so.state not in ('draft','cancel')

            )
        """)
