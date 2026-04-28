# -*- coding: utf-8 -*-
from openerp import models, fields, api, _, exceptions

class account_invoice(models.Model):
    _inherit = "account.invoice"
    
    od_remarks = fields.Char(string="Remarks")
    od_ignore = fields.Boolean('Ignore in Reports')
    od_refund = fields.Boolean('Mark as Refunded/Cancelled')
    inv_status = fields.Selection([('cancel', 'Cancelled'), ('refund', 'Refunded')], 'Refund Status')
    
    @api.multi
    def invoice_validate(self):
        analytic_id = self.od_analytic_account and self.od_analytic_account.id or False
        res = super(account_invoice, self).invoice_validate()
        if self.type in ['out_invoice', 'out_refund']:
            for line in self.invoice_line:
                if len(line.invoice_line_tax_id.ids) < 1:
                    raise exceptions.ValidationError("All Invoice Lines should be linked with Taxes")
        for line in self.invoice_line:
            if not line.account_analytic_id:
                raise exceptions.ValidationError("All Invoice Lines should be linked with Analytic Accounts")
            
        #Unlink refunded or Cancelled invoices from invoice plans
        if self.type == 'out_refund' and analytic_id:
            org_inv_id = self.od_original_invoice_id and self.od_original_invoice_id.id or False
            for sch_line in self.od_analytic_account.prj_inv_sch_line:
                if sch_line.invoice_id.id == org_inv_id:
                    sch_line.write({'invoice_id': False})
            for analytic in self.od_analytic_account.od_child_data:
                if analytic.od_project_invoice_schedule_line:
                    for sch_line in analytic.od_project_invoice_schedule_line:
                        if sch_line.invoice_id.id == org_inv_id:
                            sch_line.unlink()
            for analytic in self.od_analytic_account.od_grandchild_data:
                if analytic.od_project_invoice_schedule_line:
                    for sch_line in analytic.od_project_invoice_schedule_line:
                        if sch_line.invoice_id.id == org_inv_id:
                            sch_line.unlink()
                            
        return res