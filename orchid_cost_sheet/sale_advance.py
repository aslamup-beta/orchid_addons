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

from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from pprint import pprint

class sale_advance_payment_inv(osv.osv_memory):
    _inherit = "sale.advance.payment.inv"
    _description = "Sales Advance Payment Invoice"
    
    
    def _prepare_advance_invoice_vals(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        sale_obj = self.pool.get('sale.order')
        ir_property_obj = self.pool.get('ir.property')
        fiscal_obj = self.pool.get('account.fiscal.position')
        inv_line_obj = self.pool.get('account.invoice.line')
        wizard = self.browse(cr, uid, ids[0], context)
        sale_ids = context.get('active_ids', [])

        result = super(sale_advance_payment_inv,self)._prepare_advance_invoice_vals(cr, uid, ids, context=context)
        pprint(result)
        sale=sale_obj.browse(cr, uid, sale_ids, context=context)
        order_type_id = sale.od_order_type_id and sale.od_order_type_id.id
        od_cost_sheet_id = sale.od_cost_sheet_id and sale.od_cost_sheet_id.id or False
        branch_id = sale.od_branch_id and sale.od_branch_id.id or False 
        division_id = sale.od_division_id and sale.od_division_id or False
        project_id = sale.project_id and sale.project_id.id
        if od_cost_sheet_id:
            if result:
                res_id = result[0][0]
                data_dict = result[0][1]
                data_dict.update({'od_cost_sheet_id':od_cost_sheet_id,'od_branch_id':branch_id,'od_division_id':division_id,
                                  'od_analytic_account':project_id})
                result =[(res_id,data_dict)]
        if order_type_id:
            income_account_id = sale.od_order_type_id and sale.od_order_type_id.income_acc_id and sale.od_order_type_id.income_acc_id.id
            expense_account_id = sale.od_order_type_id and sale.od_order_type_id.expense_acc_id and sale.od_order_type_id.expense_acc_id.id
            if result:
                res_id = result[0][0]
                data_dict = result[0][1]
                data_dict.update({'od_order_type_id':order_type_id,'od_inter_inc_acc_id':income_account_id,'od_inter_exp_acc_id':expense_account_id})
                result =[(res_id,data_dict)]
        
        return result

class sale_order_line_make_invoice(osv.osv_memory):
    _inherit = "sale.order.line.make.invoice"
    _description = "Sale OrderLine Make_invoice"

    def _prepare_invoice(self, cr, uid, order, lines, context=None):
        
        result = super(sale_order_line_make_invoice, self)._prepare_invoice(cr, uid, order, lines,context)
        cost_sheet_id = order.od_cost_sheet_id and order.od_cost_sheet_id.id or False
        cost_centre_id = order.od_cost_centre_id and order.od_cost_centre_id.id or False
        branch_id = order.od_branch_id and order.od_branch_id.id or False 
        division_id = order.od_division_id and order.od_division_id.id or False 
        project_id = order.project_id and order.project_id.id or False
        result.update({
                'od_cost_sheet_id':cost_sheet_id,
                'od_cost_centre_id':cost_centre_id,
                'od_branch_id':branch_id,
                'od_division_id':division_id,
                'od_analytic_account':project_id
            })
        return result
