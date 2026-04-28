# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2013 Camptocamp (<http://www.camptocamp.com>)
#    Authors: Ferdinand Gasauer, Joel Grand-Guillaume
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

from openerp import models, fields, api
from openerp.tools.translate import _
from openerp.exceptions import Warning

class res_partner(models.Model):
    _inherit ='res.partner'
    x_custom_payment_term = fields.Text(string="Custom Supplier Payment Term")
    
class product_template(models.Model):
    _inherit ='product.template'
    
    @api.onchange('description')
    def onchange_description(self):
        description = self.description or ''
        if description:
            self.description_purchase = description
            self.description_sale = description
            
    arabic_description = fields.Text(string="Arabic Description")        
    


class purchase_order(models.Model):
    _inherit ='purchase.order'
    od_customer_id =fields.Many2one('res.partner','Customer')
    od_tax_id = fields.Many2one('account.tax','Tax to be Applied', domain=[('type_tax_use','=','purchase')])
    
    @api.one
    def apply_tax_all(self):
        tax_id = self.od_tax_id or False
        if tax_id:
            for line in self.order_line:
                line.write({'taxes_id': [(6, 0, [tax_id.id])]})
        return True
    
    @api.multi
    def po_manually_done(self):
        current_state = self.state
        if current_state not in ('approved','except_picking', 'except_invoice'):
            raise Warning("You cannot do Manual Correction from %s state"%current_state)
        self.write({'state': 'done'})
    
    #Added by Aslam: 08/01/2019
    @api.model
    def create(self,vals):
        analytic_id = vals.get('project_id', False)
        purchase_orders = self.search([('project_id','=',analytic_id)])
        analytic_obj = self.env['account.analytic.account'].browse(analytic_id)
        analytic_name = analytic_obj.code
        po_count = len(purchase_orders) + 1
        if vals.get('name','/')=='/':
            if analytic_name:
                vals['name'] = analytic_name + '-' + 'PO' + str(po_count)
            else:
                vals['name'] = self.env['ir.sequence'].get('purchase.order') or '/'
        return super(purchase_order, self).create(vals)
    
    @api.multi 
    def import_po_lines_wiz(self):
        ctx = self.env.context.copy()
        ctx['sheet_id'] = self.id
        return {
              'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'wiz.import.export.po',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context':ctx,
            }
    
class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    
    od_pdt_brand_id = fields.Many2one('od.product.brand','Product Brand')
    
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: