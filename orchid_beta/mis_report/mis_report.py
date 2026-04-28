# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import fields,osv

# od_wip_report

class od_wip_report_move(osv.osv):
    _name = "od.order.stock.move"
    _description = "Order Stock Move"
    _auto = False

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'od_order_stock_move')
        
        cr.execute("""
            create or replace view od_order_stock_move as (
                SELECT 
                    odata.so_line_id,
                    odata.purchase_line_id,
                    odata.product_id,
                    sum(odata.delivered) AS delivered,
                    sum(odata.pending) AS pending,
                    sum(odata.cancel) AS cancel
                FROM ( SELECT 
                        smv.product_id,
                        smv.so_line_id,
                        smv.purchase_line_id,
                        CASE
                            WHEN ((smv.state)::text = 'done'::text) THEN sum(smv.product_qty)
                            ELSE (0)::numeric
                        END AS delivered,
                        CASE
                            WHEN ((smv.state)::text = 'cancel'::text) THEN sum(smv.product_qty)
                            ELSE (0)::numeric
                        END AS cancel,
                        CASE
                            WHEN (((smv.state)::text <> 'done'::text) AND ((smv.state)::text <> 'cancel'::text)) THEN sum(smv.product_qty)
                            ELSE (0)::numeric
                        END AS pending
                    FROM stock_move smv
                    GROUP BY 
                        smv.product_id,
                        smv.so_line_id,
                        smv.purchase_line_id,
                        smv.state
                    ) odata
                GROUP BY 
                    odata.so_line_id,
                    odata.purchase_line_id,
                    odata.product_id
                )
            """)

class od_wip_report(osv.osv):
    _name = "od.wip.report"
    _description = "Project Report"
    _auto = False
    
    # def _get_perecent(self, cursor, user, ids, name, attr, context=None):
    #     res = {}
    #     for rec in self.browse(cursor, user, ids, context=context):
    #         if rec.profit:
    #             res[rec.id] = (rec.profit/rec.invoice_amount or rec.profit) * 100 
    #     return res

    _columns = {
                'project_id':fields.many2one('project.project','Project',readonly=True),
                'partner_id':fields.many2one('res.partner','Customer',readonly=True),
                'date':fields.datetime(string="Date",readonly=True),
                'company_id':fields.many2one('res.company','Company',readonly=True),
                'invoice_amount':fields.float('Revenue',readonly=True),
                'project_cost':fields.float('Cost',readonly=True),
                'profit':fields.float('Profit',readonly=True),
                'provision_amount':fields.float('Provision',readonly=True),
                'manager_id':fields.many2one('res.users','Project Manager',readonly=True),
                'user_id':fields.many2one('res.users','Salesperson',readonly=True),
                'od_owner_id':fields.many2one('res.users','Project Owner',readonly=True),
                'od_type_of_project':fields.selection([('sup', 'Supply'),
                                                       ('imp','Implementation'),
                                                       ('sup_imp','Supply & Implementation'),
                                                       ('amc','A M C'),
                                                       ('o_m','O & M'),
                                                       ('comp_gen','Company General -(POC,Training,Trips,etc.)')
                                                       ],
                                                      'Type',readonly=True),
                # 'gp':fields.function(_get_perecent,type="float",string="GP")
    }
    _order = "project_id ASC"
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'od_wip_report')

        cr.execute("""
            create or replace view od_wip_report as (
                SELECT 
                    od_wip.id,
                    od_wip.provision_account_id, 
                    od_wip.expense_account_id, 
                    od_wip.journal_id, 
                    od_wip.move, 
                    od_wip.provision_amount, 
                    od_wip.wip_account_id, 
                    od_wip.invoice_amount, 
                    od_wip.date, 
                    od_wip.wip_account_balance, 
                    od_wip.project_id, 
                    od_wip.provision, 
                    od_wip.name, 
                    od_wip.project_cost, 
                    od_wip.invoice_account_id, 
                    od_wip.income_account_id, 
                    od_wip.profit, 
                    od_wip.company_id, 
                    account_analytic_account.code, 
                    account_analytic_account.partner_id, 
                    account_analytic_account.user_id, 
                    account_analytic_account.date_start, 
                    account_analytic_account.state, 
                    account_analytic_account.manager_id, 
                    account_analytic_account.type, 
                    account_analytic_account.od_owner_id, 
                    account_analytic_account.od_cost_sheet_id, 
                    account_analytic_account.od_type_of_project
                FROM od_wip INNER JOIN account_analytic_account ON od_wip.project_id = account_analytic_account.id
                WHERE od_wip.project_id IS NOT NULL
                GROUP BY
                    od_wip.id,
                    od_wip.provision_account_id, 
                    od_wip.expense_account_id, 
                    od_wip.journal_id, 
                    od_wip.move, 
                    od_wip.provision_amount,  
                    od_wip.wip_account_id, 
                    od_wip.invoice_amount, 
                    od_wip.date, 
                    od_wip.wip_account_balance, 
                    od_wip.project_id, 
                    od_wip.provision, 
                    od_wip.name, 
                    od_wip.project_cost, 
                    od_wip.invoice_account_id, 
                    od_wip.income_account_id, 
                    od_wip.profit, 
                    od_wip.company_id, 
                    account_analytic_account.code, 
                    account_analytic_account.partner_id, 
                    account_analytic_account.user_id, 
                    account_analytic_account.date_start, 
                    account_analytic_account.state, 
                    account_analytic_account.manager_id, 
                    account_analytic_account.type, 
                    account_analytic_account.od_owner_id, 
                    account_analytic_account.od_cost_sheet_id, 
                    account_analytic_account.od_type_of_project
                )
            """)


# od_po_status_report

class od_po_status_report(osv.osv):
    _name = "od.po.status.report"
    _description = "Purchase Report"
    _auto = False
    _columns = {
                'order_id':fields.many2one('purchase.order','Purchase',readonly=True),
                'partner_id':fields.many2one('res.partner','Supplier',readonly=True),
                'company_id':fields.many2one('res.company','Company',readonly=True),
                'date_planned':fields.date(string="Date Scheduled",readonly=True),
                'analytic_id':fields.many2one('account.analytic.account','Project',readonly=True),
                'product_id':fields.many2one('product.product','Product',readonly=True),
                'order_qty':fields.float('Order Qty',readonly=True),
                'price_unit':fields.float('Unit Price',readonly=True),
                'order_value':fields.float('Order Value',readonly=True),
                'delivered':fields.float('Received Qty',readonly=True),
                'delivered_value':fields.float('Received Value',readonly=True),
                'pending':fields.float('Pending Qty',readonly=True),
                'pending_value':fields.float('Pending Value',readonly=True),
                'cancel':fields.float('Cancel Qty',readonly=True),
                'cancel_value':fields.float('Cancel Value',readonly=True),
    }
    _order = "order_id ASC"

    def init(self, cr):    
        tools.drop_view_if_exists(cr, 'od_po_status_report')
        cr.execute("""
            create or replace view od_po_status_report as (
                SELECT 
                    min(odata.id) as id,
                    odata.order_id,
                    odata.company_id,
                    odata.partner_id,
                    odata.date_planned,
                    odata.account_analytic_id AS analytic_id,
                    odata.product_id AS product_id,
                    odata.order_qty AS order_qty,
                    odata.price_unit AS price_unit,
                    (odata.order_qty * odata.price_unit) AS order_value,
                    sum(odata.delivered) AS delivered,
                    (odata.delivered * odata.price_unit) AS delivered_value,
                    sum(odata.pending) AS pending,
                    (odata.pending * odata.price_unit) AS pending_value,
                    sum(odata.cancel) AS cancel,
                    (odata.cancel * odata.price_unit) AS cancel_value

                FROM ( SELECT pol.id,
                            pol.order_id,
                            pol.company_id,
                            pol.partner_id,
                            pol.date_planned,
                            pol.account_analytic_id,
                            pol.product_id,
                            pol.product_qty as order_qty,
                            pol.price_unit,
                            CASE
                                WHEN ((smv.state)::text = 'done'::text) THEN sum(smv.product_qty)
                                ELSE (0)::numeric
                            END AS delivered,
                            CASE
                                WHEN ((smv.state)::text = 'cancel'::text) THEN sum(smv.product_qty)
                                ELSE (0)::numeric
                            END AS cancel,
                            CASE
                                WHEN (((smv.state)::text <> 'done'::text) AND ((smv.state)::text <> 'cancel'::text)) THEN sum(smv.product_qty)
                                ELSE (0)::numeric
                            END AS pending
                        FROM stock_move smv LEFT JOIN purchase_order_line pol ON pol."id"=smv.purchase_line_id
                        WHERE pol.order_id IS NOT NULL AND pol.account_analytic_id IS NOT NULL
                        GROUP BY 
                            pol.id,
                            pol.order_id,
                            pol.account_analytic_id,
                            pol.product_id,
                            pol.product_qty,
                            pol.price_unit,
                            pol.company_id,
                            pol.partner_id,
                            pol.date_planned,
                            smv.state, 
                            smv.product_id
                        ) odata
                GROUP BY odata.id,
                        odata.company_id, 
                        odata.order_id,
                        odata.account_analytic_id,
                        odata.partner_id,
                        odata.product_id,
                        odata.order_qty,
                        odata.date_planned,
                        odata.price_unit,
                        odata.delivered,
                        odata.pending,
                        odata.cancel
                )
            """)


# od_emp_prj_report

class od_emp_prj_report(osv.osv):
    _name = "od.emp.prj.report"
    _description = "Employee Project"
    _auto = False
    _columns = {
                'date':fields.date(string="Date",readonly=True),
                'date_start':fields.date(string="Project Start",readonly=True),
                'date_end':fields.date(string="Project End",readonly=True),
                'job_id':fields.many2one('hr.job','Position',readonly=True),
                'department_id':fields.many2one('hr.department','Department',readonly=True),
                'parent_id':fields.many2one('hr.employee','Manager',readonly=True),
                'country_id':fields.many2one('res.country','Country',readonly=True),
                'company_id':fields.many2one('res.company','Company',readonly=True),
                'user_id':fields.many2one('res.users','Employee',readonly=True),
                'project_id':fields.many2one('account.analytic.account','Project',readonly=True),
                'partner_id':fields.many2one('res.partner','Customer',readonly=True),
                'duration':fields.float('Duration',readonly=True),
                'amount':fields.float('OH Cost',readonly=True),
                'actual_amount':fields.float('Actual Cost',readonly=True),
                'xo_total_wage':fields.float('Salary',readonly=True),
                'od_cost_centre_id':fields.many2one('od.cost.centre',string="Cost Centre",readonly=True),
                'branch_id':fields.many2one('od.cost.branch',string="Branch",readonly=True),
                'division_id':fields.many2one('od.cost.division',string="Division",readonly=True),
                'state':fields.selection([('template', 'Template'),
                                           ('draft','New'),
                                           ('open','In Progress'),
                                           ('pending','To Renew'),
                                           ('close','Closed'),
                                           ('cancelled', 'Cancelled')],
                                          'Status'),
}
    _order = "job_id ASC"

    def init(self, cr):    
        tools.drop_view_if_exists(cr, 'od_emp_prj_report')
        cr.execute("""
            create or replace view od_emp_prj_report as (
                SELECT
                    anl."state",
                    lbr."date",
                    lbr."name",
                    anl.date_start,
                    anl."date" AS date_end,
                    anl.od_owner_id,
                    anl.company_id,
                    anl.od_type_of_project,
                    lne.project_id,
                    emp.id,
                    emp.job_id,
                    emp.department_id,
                    emp.parent_id,
                    emp.country_id,
                    emp.od_cost_centre_id,
                    cc.branch_id,
                    cc.division_id,
                    lne.user_id,
                    lne.partner_id,
                    lne.duration,
                    lne.amount,
                    lne.actual_amount,
                    cont.xo_total_wage
                FROM
                    od_labour_line lne
                LEFT JOIN account_analytic_account anl ON  anl."id" = lne.project_id
                LEFT JOIN od_labour lbr ON lne.cost_id = lbr."id"
                LEFT JOIN resource_resource res ON res.user_id  = lne.user_id
                LEFT JOIN hr_employee emp ON emp.resource_id = res."id"
                LEFT JOIN hr_contract cont ON cont.employee_id=emp."id"
                LEFT JOIN od_cost_centre cc ON emp.od_cost_centre_id = cc.id 
                WHERE lbr."state" = 'done' AND anl.id IS NOT NULL
                GROUP BY
                    anl."state",
                    lbr."date",
                    lbr."name",
                    anl.date_start,
                    anl."date",
                    anl.od_owner_id,
                    anl.company_id,
                    anl.od_type_of_project,
                    lne.project_id,
                    emp.id,
                    emp.job_id,
                    emp.department_id,
                    emp.parent_id,
                    emp.country_id,
                    lne.user_id,
                    lne.partner_id,
                     emp.od_cost_centre_id,
                    cc.branch_id,
                    cc.division_id,
                    lne.duration,
                    lne.amount,
                    lne.actual_amount,
                    cont.xo_total_wage
            )
        """)



# od_prj_all_report

class od_prj_all_report(osv.osv):
    _name = "od.prj.all.report"
    _description = "Project 360"
    _auto = False
    _columns = {
                'state':fields.selection([('template', 'Template'),
                                           ('draft','New'),
                                           ('open','In Progress'),
                                           ('pending','To Renew'),
                                           ('close','Closed'),
                                           ('cancelled', 'Cancelled')],
                                          'Status'),
                'start_date':fields.date(string="Start End",readonly=True),
                'end_date':fields.date(string="End Date",readonly=True),
                'close_date':fields.date('Close Date',readonly=True),
                'partner_id':fields.many2one('res.partner','Customer',readonly=True),
                'company_id':fields.many2one('res.company','Company',readonly=True),
                'project_id':fields.many2one('account.analytic.account','Project',readonly=True),
                'user_id':fields.many2one('res.users','Salesman',readonly=True),
                'manager_id':fields.many2one('res.users','Manager',readonly=True),
                'original_total_price':fields.float('CS Price',readonly=True),
                'original_total_cost':fields.float('CS Cost',readonly=True),
                'original_profit':fields.float('CS Profit',readonly=True),
                'amended_total_price':fields.float('SO Price',readonly=True),
                'amended_total_cost':fields.float('SO Cost',readonly=True),
                'amended_profit':fields.float('SO Profit',readonly=True),
                'invoice_amount':fields.float('AC Price',readonly=True),
                'project_cost':fields.float('AC Cost',readonly=True),
                'profit':fields.float('AC Profit',readonly=True),
                'provision_amount':fields.float('Provision',readonly=True),
                'planned_days':fields.float('Planned Days',readonly=True),
                'actual_days':fields.float('Actual Days',readonly=True),       
    }
    _order = "project_id ASC"

    def init(self, cr):    
        tools.drop_view_if_exists(cr, 'od_prj_all_report')
        cr.execute("""
            create or replace view od_prj_all_report as (
                SELECT
                    MIN (anl. ID) AS ID,
                    anl."state",
                    anl.company_id,
                    anl.date_start AS start_date,
                    anl."date" AS end_date,
                    anl.partner_id,
                    anl.user_id,
                    anl.currency_id,
                    anl.manager_id,
                    anl.od_type_of_project,
                    (sol.od_original_price * sol.od_original_qty) as original_total_price,
                    (sol.od_original_unit_cost * sol.od_original_qty) AS original_total_cost,
                    ((sol.od_original_price * sol.od_original_qty) - (sol.od_original_unit_cost * sol.od_original_qty)) as original_profit,
                    (sol.price_unit * sol.product_uom_qty) as amended_total_price,
                    (sol.purchase_price * sol.product_uom_qty) as amended_total_cost,
                    ((sol.price_unit * sol.product_uom_qty) - (sol.purchase_price * sol.product_uom_qty)) as amended_profit,
                    so.project_id,
                    wip."date" AS close_date,
                    wip.invoice_amount,
                    wip.project_cost,
                    wip.profit,
                    wip.provision_amount,
                    (anl."date"::date - anl.date_start::date)AS planned_days,
                    (wip."date"::date - anl.date_start::date)AS actual_days
                FROM
                    account_analytic_account anl
                    LEFT JOIN sale_order so ON so.project_id = anl."id"
                    JOIN sale_order_line sol ON sol.order_id=so.id
                    LEFT JOIN od_wip wip ON wip.project_id=anl."id"
                WHERE anl.type='contract' AND anl.id IS NOT NULL
                GROUP BY
                    anl."state",
                    anl.company_id,
                    anl. ID,
                    anl.date_start,
                    anl."date",
                    anl.partner_id,
                    anl.user_id,
                    anl.currency_id,
                    anl.manager_id,
                    anl.od_type_of_project,
                    sol.od_original_price,
                    sol.od_original_qty,
                    sol.od_original_unit_cost,
                    sol.price_unit,
                    sol.product_uom_qty,
                    sol.purchase_price,
                    so.project_id,
                    wip."date",
                    wip.invoice_amount,
                    wip.project_cost,
                    wip.profit,
                    wip.provision_amount
                )
            """)
