from openerp import models, fields, api

class material_issue_wiz(models.TransientModel):
    _inherit = 'orchid_so2po.generate_purchase_order'
    
    @api.onchange('prod_select_all')
    def onchange_prod_select_all(self):
        if self.prod_select_all:
            for x in self.od_purchase_generate_line:
                x.line_check = True
        else:
            for x in self.od_purchase_generate_line:
                x.line_check = False
                
    @api.multi
    def delete_prod_lines(self):
        for line in self.od_purchase_generate_line:
            if line.line_check:
                line.unlink()
        return {
        'context': self.env.context,
        'view_type': 'form',
        'view_mode': 'form',
        'res_model': 'orchid_so2po.generate_purchase_order',
        'res_id': self.id,
        'view_id': False,
        'type': 'ir.actions.act_window',
        'target': 'new',
    }