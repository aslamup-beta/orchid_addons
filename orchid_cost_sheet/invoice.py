# -*- coding: utf-8 -*-
from openerp import models,fields,api,_

class account_invoice(models.Model):
    _inherit = "account.invoice"
    
    @api.one
    @api.depends('od_cost_sheet_id','name')
    def _compute_part_ref(self):
        if self.od_cost_sheet_id and self.od_cost_sheet_id.part_ref:
            self.od_part_ref = self.od_cost_sheet_id.part_ref
        else:
            self.od_part_ref = self.name
    
    od_original_invoice_id = fields.Many2one('account.invoice',string="Original Invoice")
    od_cost_sheet_id = fields.Many2one('od.cost.sheet',string="Cost Sheet",readonly=True)
    od_cost_centre_id =fields.Many2one('od.cost.centre',string='Cost Centre',readonly=True,states={'draft':[('readonly',False)]})
    od_branch_id =fields.Many2one('od.cost.branch',string='Branch',readonly=True,states={'draft':[('readonly',False)]})
    od_division_id = fields.Many2one('od.cost.division',string='Division',readonly=True,states={'draft':[('readonly',False)]})
    lead_id = fields.Many2one('crm.lead',string="Opportunity",related="od_cost_sheet_id.lead_id",readonly=True)
     
    od_sale_team_id = fields.Many2one('crm.case.section',string="Sale Team",related="lead_id.section_id",readonly=True)
    op_stage_id = fields.Many2one('crm.case.stage',string="Opp Stage",related="lead_id.stage_id",readonly=True)    
    op_expected_booking = fields.Date(string="Opp Expected Booking",related="lead_id.date_action",readonly=True)    
   
    op_stage_id = fields.Many2one('crm.case.stage',string="Opp Stage",related="lead_id.stage_id",readonly=True)    
    fin_approved_date = fields.Datetime(string="Finance Approved Date",related="od_cost_sheet_id.approved_date",readonly=True)
    od_closing_date = fields.Date(string="Closing Date")
    
    od_part_ref = fields.Char('Partner Reference', readonly="1",compute='_compute_part_ref')
    
class account_invoice_line(models.Model):
    _inherit = "account.invoice.line"
    so_line_id = fields.Many2one('sale.order.line','Sale Order Line')
