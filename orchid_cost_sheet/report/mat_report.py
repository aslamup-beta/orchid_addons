
from openerp.osv import fields,osv
from openerp import tools

class material_report(osv.osv):
    _name = "material.report"
    _description = "Material Report"
    _auto = False
    _columns = {
        'cost_sheet_id': fields.many2one('od.cost.sheet', 'Cost Sheet', readonly=True),
        'partner_id':fields.many2one('res.partner', 'Customer', readonly=True),
        'brand_id':fields.many2one('od.product.brand', 'Brand', readonly=True),
        'currency_id': fields.many2one('res.currency', 'Supplier Currency', readonly=True),
        'cost': fields.float('Cost From Supplier', readonly=True, group_operator="sum"),
        'op_stage_id':fields.many2one('crm.case.stage',string="Opp Stage")
        
    }
    _order = 'cost_sheet_id desc, cost desc'
    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'material_report')
        cr.execute("""
            create or replace view material_report as (
               
                select
                    min(l.id) as id,
                    s.op_stage_id,
                    s.od_customer_id as partner_id,
                    l.cost_sheet_id,
                    l.manufacture_id as brand_id,
                    l.supplier_currency_id as currency_id,
                    l.discounted_total_supplier_currency as cost
                   
                from od_cost_mat_main_pro_line l
                    left join od_cost_sheet s on (l.cost_sheet_id=s.id)
                where s.company_id=6 and s.status ='active' and s.state in ('draft','design_ready','submitted')
                group by
                    s.od_customer_id,
                    l.cost_sheet_id,
                    l.manufacture_id,
                    l.supplier_currency_id,
                    s.op_stage_id,
                    l.discounted_total_supplier_currency
                   
            )
        """)