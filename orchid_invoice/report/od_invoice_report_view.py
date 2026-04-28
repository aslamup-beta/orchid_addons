# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import tools
import openerp.addons.decimal_precision as dp
from openerp.osv import fields,osv

class od_invoice_report_view(osv.osv):
    _name = "od.invoice.report.view"
    _description = "Sale Report"
    _auto = False
    _rec_name = 'date'


#    def _get_percentage(self, cr, uid, ids, field_names, args, context=None):
#        """Compute the amounts in the currency of the user
#        """
#        if context is None:
#            context={}
#        ctx = context.copy()
#        for item in self.browse(cr, uid, ids, context=context):
#            ctx['profit'] = item.profit
#            res[item.id] = {
#                'profile_percentage': 20,
#            }
#        return res


    _columns = {
        'date': fields.date('Date', readonly=True),
        'product_id': fields.many2one('product.product', 'Product', readonly=True),
        'product_qty':fields.float('Product Quantity', readonly=True),
        'uom_name': fields.char('Reference Unit of Measure', size=128, readonly=True),
        'payment_term': fields.many2one('account.payment.term', 'Payment Term', readonly=True),
        'period_id': fields.many2one('account.period', 'Force Period', domain=[('state','<>','done')], readonly=True),
        'fiscal_position': fields.many2one('account.fiscal.position', 'Fiscal Position', readonly=True),
        'currency_id': fields.many2one('res.currency', 'Currency', readonly=True),
        'categ_id': fields.many2one('product.category','Category of Product', readonly=True),
        'journal_id': fields.many2one('account.journal', 'Journal', readonly=True),
        'partner_id': fields.many2one('res.partner', 'Partner', readonly=True),
        'commercial_partner_id': fields.many2one('res.partner', 'Partner Company', help="Commercial Entity"),
        'company_id': fields.many2one('res.company', 'Company', readonly=True),
        'user_id': fields.many2one('res.users', 'Salesperson', readonly=True),
        'price_total': fields.float('Invoice', readonly=True),
        'price_average': fields.float('Average Price', readonly=True, group_operator="avg"),
        'currency_rate': fields.float('Currency Rate', readonly=True),
        'nbr': fields.integer('# of Invoices', readonly=True),  # TDE FIXME master: rename into nbr_lines
        'type': fields.selection([
            ('out_invoice','Customer Invoice'),
            ('in_invoice','Supplier Invoice'),
            ('out_refund','Customer Refund'),
            ('in_refund','Supplier Refund'),
            ],'Type', readonly=True),
        'state': fields.selection([
            ('draft','Draft'),
            ('proforma','Pro-forma'),
            ('proforma2','Pro-forma'),
            ('open','Open'),
            ('paid','Done'),
            ('cancel','Cancelled')
            ], 'Invoice Status', readonly=True),
        'date_due': fields.date('Due Date', readonly=True),
        'account_id': fields.many2one('account.account', 'Account',readonly=True),
        'account_line_id': fields.many2one('account.account', 'Account Line',readonly=True),
        'partner_bank_id': fields.many2one('res.partner.bank', 'Bank Account',readonly=True),
        'residual': fields.float('Total Residual', readonly=True),
        'country_id': fields.many2one('res.country', 'Country of the Partner Company'),
        'od_account_invoice_id':fields.many2one('account.invoice','Invoice'),
        'cost':fields.float('Cost'),
        'profit':fields.float('Profit'),
        'od_pdt_group_id': fields.many2one('od.product.group','Group'),

        'od_pdt_sub_group_id': fields.many2one('od.product.sub.group','Sub Group'),
        'od_pdt_type_id': fields.many2one('od.product.type','Type'),
        'od_pdt_sub_type_id': fields.many2one('od.product.sub.type','Sub Type'),
        'od_pdt_classification_id': fields.many2one('od.product.classification','Classification'),

        'od_pdt_brand_id': fields.many2one('od.product.brand','Brand'),
        'od_pdt_hscode_id': fields.many2one('od.product.hscode','HS Code'),
#        'profile_percentage': fields.function(_get_percentage, string="Profile(%)", type='float'),





    }
    _order = 'date desc'



    def _select(self):
        select_str = """
  SELECT ROW_NUMBER () OVER (ORDER BY acc_inv_repo.id) AS id,
    acc_inv_repo.date as date,
    acc_inv_repo.product_id as product_id,

    acc_inv_repo.product_qty as product_qty,
    acc_inv_repo.uom_name as uom_name,

    acc_inv_repo.payment_term as payment_term,
    acc_inv_repo.period_id as period_id,

    acc_inv_repo.fiscal_position as fiscal_position,
    acc_inv_repo.currency_id as currency_id,

    acc_inv_repo.categ_id as categ_id,
    acc_inv_repo.journal_id as journal_id,

    acc_inv_repo.partner_id as partner_id,
    acc_inv_repo.commercial_partner_id as commercial_partner_id,
    acc_inv_repo.company_id as company_id,
    acc_inv_repo.user_id as user_id,
    acc_inv_repo.price_total as price_total,
    acc_inv_repo.price_average as price_average,

    

    acc_inv_repo.currency_rate as currency_rate,
    acc_inv_repo.nbr as nbr,

    acc_inv_repo.type as type,
    acc_inv_repo.state as state,

    acc_inv_repo.date_due as date_due,
    acc_inv_repo.account_id as account_id,

    acc_inv_repo.account_line_id as account_line_id,
    acc_inv_repo.partner_bank_id as partner_bank_id,

    acc_inv_repo.residual as residual,
    acc_inv_repo.country_id as country_id,
    acc_inv_repo.od_account_invoice_id as od_account_invoice_id,
    inv_line_cost.cost as cost,
    (acc_inv_repo.price_total - inv_line_cost.cost) as profit,

    pdt_t.od_pdt_group_id as od_pdt_group_id,
    pdt_t.od_pdt_sub_group_id as od_pdt_sub_group_id,
    pdt_t.od_pdt_type_id as od_pdt_type_id,
    pdt_t.od_pdt_sub_type_id as od_pdt_sub_type_id,

    pdt_t.od_pdt_classification_id as od_pdt_classification_id,
    pdt_t.od_pdt_brand_id as od_pdt_brand_id,

   pdt_t.od_pdt_hscode_id as od_pdt_hscode_id


    

        """
        return select_str




    def _from(self):
        from_str = """
account_invoice_report  acc_inv_repo
        """
        return from_str

    def _group_by(self):
        group_by_str = """
              
        """
        return group_by_str

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM  %s 
LEFT JOIN od_invoice_line_cost_view inv_line_cost ON 
inv_line_cost.inv_id = acc_inv_repo.od_account_invoice_id
AND inv_line_cost.product_id = acc_inv_repo.product_id
left join product_product pdt on (acc_inv_repo.product_id = pdt.id)
left join product_template pdt_t on (pdt.product_tmpl_id = pdt_t.id)
WHERE acc_inv_repo.type in ('out_refund','out_invoice')
and acc_inv_repo.state in ('open','paid')
%s
 
            )""" % (self._table, self._select(), self._from(),self._group_by()))


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
