# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import fields,osv

class od_cs_vendor_analysis(osv.osv):
    _name = "od.cs.vendor.analysis"
    _description = "Vendor Analysis"
    _auto = False

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'od_cs_vendor_analysis')
        
        cr.execute("""
            CREATE OR REPLACE VIEW od_cs_vendor_analysis AS (
             SELECT mat.id,
                cs.state,
                crm.id as lead_id,
                cc.id as cost_centre_id,
                dv.id as division_id,
                br.id as branch_id,
                cs.status AS stage,
                cs.number AS reference,
                cs.name AS costsheet,
                cs.date,
                cs.approved_date,
                cs.change_date,
                cs.company_id AS company,
                cs.od_customer_id AS customer,
                cs.sales_acc_manager AS sales_manager,
                cs.business_development AS bdm,
                mat.manufacture_id AS manufacturer,
                mat.part_no AS product,
                mat.types,
                mat.name AS description,
                mat.section_id,
                cg.name AS cost_group,
                cg.id AS cost_group_id,
                cg.proof_of_cost AS supplier,
                cg.supplier_currency_id AS pur_currency,
                cg.sales_currency_id AS sale_currency,
                cg.supplier_discount AS sup_discout,
                cg.customer_discount AS cust_discount,
                cg.profit AS profit_pecentage,
                cg.currency_exchange_factor AS ex_rate,
                mat.qty,
                mat.unit_cost_supplier_currency AS sup_cost,
                    CASE
                        WHEN cg.id IS NOT NULL THEN mat.unit_cost_supplier_currency * cg.currency_exchange_factor::double precision
                        ELSE 0::double precision
                    END AS local_cost,
                    CASE
                        WHEN cg.id IS NOT NULL THEN mat.unit_cost_supplier_currency * cg.currency_exchange_factor::double precision * mat.qty::double precision
                        ELSE 0::double precision
                    END AS line_cost,
                    CASE
                        WHEN cg.id IS NOT NULL THEN mat.unit_cost_supplier_currency * cg.currency_exchange_factor::double precision * mat.qty::double precision * (cg.profit / 100::double precision)
                        ELSE 0::double precision
                    END AS profit,
                    CASE
                        WHEN cg.profit > 0::double precision AND cg.customer_discount > 0::double precision AND cg.id IS NOT NULL THEN mat.unit_cost_supplier_currency * cg.currency_exchange_factor::double precision * mat.qty::double precision + mat.unit_cost_supplier_currency * cg.currency_exchange_factor::double precision * mat.qty::double precision * (cg.profit / 100::double precision) - (mat.unit_cost_supplier_currency * cg.currency_exchange_factor::double precision * mat.qty::double precision + mat.unit_cost_supplier_currency * cg.currency_exchange_factor::double precision * mat.qty::double precision * (cg.profit / 100::double precision)) * (cg.customer_discount / 100::double precision)
                        WHEN cg.profit > 0::double precision AND cg.customer_discount IS NULL OR cg.customer_discount = 0::double precision AND cg.id IS NOT NULL THEN mat.unit_cost_supplier_currency * cg.currency_exchange_factor::double precision * mat.qty::double precision + mat.unit_cost_supplier_currency * cg.currency_exchange_factor::double precision * mat.qty::double precision * (cg.profit / 100::double precision)
                        WHEN cg.customer_discount > 0::double precision AND cg.profit IS NULL OR cg.profit = 0::double precision AND cg.id IS NOT NULL THEN mat.unit_cost_supplier_currency * cg.currency_exchange_factor::double precision * mat.qty::double precision - mat.unit_cost_supplier_currency * cg.currency_exchange_factor::double precision * mat.qty::double precision * (cg.customer_discount / 100::double precision)
                        WHEN cg.id IS NOT NULL THEN mat.unit_cost_supplier_currency * cg.currency_exchange_factor::double precision * mat.qty::double precision
                        ELSE 0::double precision
                    END AS sale
               FROM od_cost_mat_main_pro_line mat
                 LEFT JOIN od_cost_sheet cs ON cs.id = mat.cost_sheet_id
                 LEFT JOIN od_cost_costgroup_material_line cg ON mat."group" = cg.id
                 LEFT JOIN crm_lead crm ON cs.lead_id=crm.id
                 LEFT JOIN od_cost_centre cc on cs.od_cost_centre_id = cc.id
                 LEFT JOIN od_cost_division dv on cs.od_division_id = dv.id
                 LEFT JOIN od_cost_branch br on cs.od_branch_id = br.id
                )
            """)