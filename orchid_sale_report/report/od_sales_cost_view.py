# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import fields, osv
class od_sales_cost_view(osv.osv):
    _name = "od.sales.cost.view"
    _description = "od.sales.cost.view"
    _auto = False
    _rec_name = 'product_id'

    _columns = {
        'invoice_no':fields.char('Invoice'),
        'sale_type':fields.char('Type'),
        'sale':fields.float('Sale'),
        'cost':fields.float('Cost'),
        'profit':fields.float('Profit'),
        'partner_id':fields.many2one('res.partner',string='Customer'),
        'product_id':fields.many2one('product.product',string='Product'),
        'company_id':fields.many2one('res.company',string='Company'),
        'date_invoice':fields.date('Date Invoice'),
        'period_id':fields.many2one('account.period',string='Period'),
        'date_due':fields.date('Date Due'),
        'user_id':fields.many2one('res.users',string='Salesperson'),
        'state':fields.char('State'),
        'section_id': fields.many2one('crm.case.section', 'Sales Team'),
        'currency_id':fields.many2one('res.currency',string='Currency'),
        'sale_currency':fields.float(string='Sale Currency'),
        'quantity':fields.float('Qty')
        

    }
    def _select(self):
        select_str = """
  SELECT ROW_NUMBER () OVER (ORDER BY INV.id) AS id,
inv.company_id as company_id,
inv.partner_id as partner_id,
inv.date_invoice as date_invoice,
inv.period_id as period_id,
inv.date_due as date_due,
inv.user_id as user_id,
inv.section_id as section_id,
inv.state as state,
inv.number as invoice_no,
inv.currency_id as currency_id,
inv.amount_total AS sale_currency,
invl.product_id as product_id,
invl.quantity as quantity,
CASE
 WHEN inv.type='out_invoice' THEN 'Sales'
  ELSE 'Return'
END AS sale_type,
CASE
 WHEN inv.type='out_invoice' THEN Sum(cr.credit*-1) 
 ELSE Sum(dr.debit*-1)
END AS sale,
CASE
 WHEN inv.type='out_invoice' THEN Sum(dr.debit) 
 ELSE Sum(cr.credit) 
END AS cost,
((Sum(cr.credit)+Sum(dr.debit))*-1) AS profit

        """
        return select_str



    def _from(self):
        from_str = """
                account_invoice AS INV  
        """
        return from_str

    def _group_by(self):
        group_by_str = """
            GROUP BY inv.type,
inv.company_id,
inv.partner_id,
inv.date_invoice,
inv.period_id,
inv.date_due,
inv.user_id,
inv.section_id,
inv.state,
inv.number,
inv.currency_id,
inv.amount_total,
invl.product_id,
invl.quantity,
inv.id

        """
        return group_by_str


    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM  %s 
INNER JOIN account_invoice_line AS invl ON invl.invoice_id= inv.id
LEFT OUTER JOIN od_account_move_line_debit AS dr ON dr.move_id = inv.move_id AND dr.product_id = invl.product_id
LEFT OUTER JOIN od_account_move_line_credit AS cr ON cr.move_id = inv.move_id AND cr.product_id = invl.product_id
WHERE
(cr.code = 'income' OR dr.code = 'expense')
AND inv.state<>'draft'
AND inv.type IN ('out_invoice','out_refund')
%s
 
            )""" % (self._table, self._select(), self._from(),self._group_by()))



