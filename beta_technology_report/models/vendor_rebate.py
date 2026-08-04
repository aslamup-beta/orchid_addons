import datetime
from openerp import models, fields, api, _
from datetime import date
from openerp.exceptions import Warning
from openerp import SUPERUSER_ID
# from dateutil.relativedelta import relativedelta
import openerp.addons.decimal_precision as dp


class VendorRebate(models.Model):
    _name = 'vendor.rebate'
    _description = 'Vendor Rebate'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'id desc'

    def od_get_company_id(self):
        return self.env.user.company_id

    company_id = fields.Many2one('res.company', string='Company', default=od_get_company_id)
    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    vendor_id = fields.Many2one('od.product.brand', string='Vendor',
                                states={'draft': [('readonly', False)]}, readonly=True)
    customer_id = fields.Many2one('res.partner', string='Customer', domain=[('is_company', '=', True)],
                                  states={'draft': [('readonly', False)]}, readonly=True)
    amount = fields.Float(string='Rebate Amount (SAR)', required=True, states={'draft': [('readonly', False)]},
                          readonly=True)
    date = fields.Date(string='Date', default=fields.Date.today, required=True, states={'draft': [('readonly', False)]},
                       readonly=True)
    description = fields.Text(string='Terms & Condition', states={'draft': [('readonly', False)]}, readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', track_visibility='onchange')

    invoice_id = fields.Many2one('account.invoice', string='Generated Invoice', readonly=True, copy=False)
    od_cost_centre_id = fields.Many2one('od.cost.centre', string='Cost Centre')
    od_branch_id = fields.Many2one('od.cost.branch', string='Branch')
    od_division_id = fields.Many2one('od.cost.division', string='Technology Unit')
    deposit_within_months = fields.Integer(string='Deposited within (Months)',
                                           states={'approved': [('readonly', True)], 'cancel': [('readonly', True)]})
    deal_reference = fields.Char(string='Deal Registration Info / Ref',
                                 states={'approved': [('readonly', True)], 'cancel': [('readonly', True)]})

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('vendor.rebate') or _('New')
        return super(VendorRebate, self).create(vals)

    def od_send_mail(self, template):
        ir_model_data = self.env['ir.model.data']
        email_obj = self.pool.get('email.template')
        saudi_comp = 6
        emp_company_id = self.company_id.id
        if emp_company_id == saudi_comp:
            template = template + '_saudi'
        template_id = ir_model_data.get_object_reference('beta_technology_report', template)[1]
        rebate_id = self.id
        email_obj.send_mail(self.env.cr, self.env.uid, template_id, rebate_id)
        return True

    @api.multi
    def action_submit(self):
        if self.amount <= 0:
            raise Warning(_("Rebate amount must be greater than zero."))
        self.od_send_mail('vendor_rebate_approval')
        self.write({'state': 'pending'})

    @api.multi
    def action_approve(self):
        self.write({'state': 'approved'})

    @api.multi
    def action_cancel(self):
        self.write({'state': 'cancelled'})

    @api.multi
    def action_reset_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def action_create_invoice(self):
        self.ensure_one()
        if self.invoice_id:
            raise Warning(_('An invoice has already been generated for this rebate.'))

        account_obj = self.env['account.account']
        income_account = account_obj.search([('code', '=', '5332')], limit=1)
        expense_account = account_obj.search([('code', '=', '6577')], limit=1)

        journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
        if not journal:
            raise Warning(_('No Sales Journal found.'))

        # Invoice lines setup
        invoice_lines = [(0, 0, {
            'name': _('Vendor Rebate: %s') % (self.name,),
            'account_id': 6577,
            'price_unit': self.amount,
            'product_id': 261059,
            'quantity': 1.0,
            'account_analytic_id': 21803,
            'invoice_line_tax_id': [(6, 0, [30])]
        })]

        # Create Customer Invoice
        invoice_vals = {
            'name': self.name,
            'origin': self.name,
            'type': 'out_invoice',
            'journal_id': journal.id,
            'partner_id': self.customer_id.id,
            'account_id': 5202,
            'user_id': 101,
            'invoice_line': invoice_lines,
            'date_invoice': fields.Date.today(),
            'od_analytic_account': 21803,
            'od_inter_inc_acc_id': 6577,
            'od_cost_centre_id': self.od_cost_centre_id.id,
            'od_branch_id': self.od_branch_id.id,
            'od_division_id': self.od_division_id.id,
            'section_id': 39,
            'state': 'draft'
        }

        invoice = self.env['account.invoice'].create(invoice_vals)
        self.write({'invoice_id': invoice.id})

        return {
            'name': _('Generated Invoice'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.invoice',
            'res_id': invoice.id,
            'view_mode': 'form',
            'view_id': self.env.ref('account.invoice_form').id,
            'view_type': 'form',
        }

    @api.one
    @api.model
    def unlink(self):
        for rec in self:
            if rec.state == 'approved':
                raise Warning(_('You cannot delete an approved rebate.'))
        return super(VendorRebate, self).unlink()
