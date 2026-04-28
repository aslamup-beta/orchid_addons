# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import fields,osv

class od_cs_summary(osv.osv):
    _name = "od.cs.summary"
    _description = "CS Summary"
    _auto = False

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'od_cs_summary')
        
        cr.execute("""
            CREATE OR REPLACE VIEW od_cs_summary AS (
                 SELECT cs.id,
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
                    crm.stage_id AS crm_stage,
                    cs.mat_tot_sale AS mat_sale,
                    cs.mat_tot_cost AS mat_cost,
                    cs.mat_profit AS mat_profit,
                    cs.mat_profit_percentage     AS mat_percentage,
                    cs.trn_tot_sale AS train_sale,
                    cs.trn_tot_cost AS train_cost,
                    cs.trn_profit AS train_profit,
                    cs.trn_profit_percentage AS train_percentage,
                    cs.bim_tot_sale AS manpower_sale,
                    cs.bim_tot_cost AS manpower_cost,
                    cs.bim_profit AS manpower_profit,
                    cs.bim_profit_percentage AS manpower_percentage,
                    cs.oim_tot_sale AS outsource_sale,
                    cs.oim_tot_cost AS outsource_cost,
                    cs.oim_profit AS outsource_profit,
                    cs.oim_profit_percentage AS outsource_percentage,
                    cs.bmn_tot_sale AS maintenance_sale,
                    cs.bmn_tot_cost AS maintenance_cost,
                    cs.bmn_profit AS maintenance_profit,
                    cs.bmn_profit_percentage AS maintenance_percentage,
                    cs.omn_tot_sale AS out_maintenance_sale,
                    cs.omn_tot_cost AS out_maintenance_cost,
                    cs.omn_profit AS out_maintenance_profit,
                    cs.omn_profit_percentage AS out_maintenance_percentage,
                    cs.o_m_tot_sale AS onm_sale,
                    cs.o_m_tot_cost AS onm_cost,
                    cs.o_m_profit AS onm_profit,
                    cs.o_m_profit_percentage AS onm_percentage,
                    cs.a_bim_sale,
                    cs.a_bmn_sale,
                    cs.a_om_sale,
                    cs.a_tot_sale,
                     
                    cs.a_bim_cost,
                    cs.a_bmn_cost,
                    cs.a_om_cost,
                    cs.a_tot_cost,
                     
                    cs.a_bim_profit,
                    cs.a_bmn_profit,
                    cs.a_om_profit,
                    cs.a_tot_profit,
                     
                    cs.a_bim_profit_percentage,
                    cs.a_bmn_profit_percentage,
                    cs.a_om_profit_percentage,
                    cs.a_tot_profit_percentage,
                    (cs.mat_tot_sale + cs.trn_tot_sale + cs.bim_tot_sale + cs.oim_tot_sale + cs.bmn_tot_sale + cs.omn_tot_sale  + cs.o_m_tot_sale  ) AS sales_sum,
                    cs.special_discount AS special_discount,
                    (cs.mat_tot_sale + cs.trn_tot_sale + cs.bim_tot_sale + cs.oim_tot_sale + cs.bmn_tot_sale + cs.omn_tot_sale  + cs.o_m_tot_sale +  cs.special_discount)   AS total_sales,
                    (cs.mat_tot_cost + cs.trn_tot_cost + cs.bim_tot_cost + cs.oim_tot_cost + cs.bmn_tot_cost + cs.omn_tot_cost + cs.o_m_tot_cost  ) AS total_cost,
                    ((cs.mat_tot_sale + cs.trn_tot_sale + cs.bim_tot_sale + cs.oim_tot_sale + cs.bmn_tot_sale + cs.omn_tot_sale  + cs.o_m_tot_sale + cs.special_discount  ) -  (  cs.mat_tot_cost + cs.trn_tot_cost + cs.bim_tot_cost + cs.oim_tot_cost + cs.bmn_tot_cost + cs.omn_tot_cost + cs.o_m_tot_cost  )) AS total_profit,
                     0 as total_percentage 
                   FROM od_cost_sheet cs
                   LEFT JOIN crm_lead crm ON cs.lead_id=crm.id
                   LEFT JOIN od_cost_centre cc on cs.od_cost_centre_id = cc.id
                   LEFT JOIN od_cost_division dv on cs.od_division_id = dv.id
                   LEFT JOIN od_cost_branch br on cs.od_branch_id = br.id
                   
                )
            """)