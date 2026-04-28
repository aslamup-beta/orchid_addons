from openerp import models, fields, api, _
from pprint import pprint
class res_partner(models.Model):
    _inherit = 'res.partner'
    
    od_google_map_link = fields.Char('Google Map Link')
    od_annual_it_spending= fields.Float('Annual IT Spending')
    od_tendering_process = fields.Char('Tendering Process')
    od_opportunities = fields.Char('Opportunities')
    od_strengths = fields.Char('Strengths')
    od_weakness = fields.Char('Weakness')
    od_threats = fields.Char('Threats')
    od_sales_action_lines = fields.One2many('od.res.part.sales.action','partner_id',string='Sales Action')
    
    
    def od_get_do(self):
        ob_id = self.id
        domain = [('partner_id','=',ob_id)]
        picking_obj = self.env['stock.picking']
        pickings = picking_obj.search(domain)
        return pickings
    @api.multi
    def od_btn_open_lots(self):
        model_data = self.env['ir.model.data']
        pickings = self.od_get_do()
        picking_ids = [pick.id for pick in pickings]
        stock_pack_op_obj = self.env['stock.pack.operation']
        domain = [('picking_id','in',picking_ids)]
        pack_ops = stock_pack_op_obj.search(domain)
        pack_op_ids = [op.id for op in pack_ops]
        dom = [('id','in',pack_op_ids)]
        search_view_id = model_data.get_object_reference('orchid_beta_project', 'beta_project_stock_pakc_op_search_view')

        return {
            'name': _('Beta Lot Serial View'),
            'domain':dom,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'stock.pack.operation',
            'type': 'ir.actions.act_window',
            }

    @api.model
    def create(self,vals):
        if vals.get('parent_id') and not vals.get('user_id'):
            parent_id = vals.get('parent_id')
            user_id = self.browse(parent_id).user_id and self.browse(parent_id).user_id.id or False
            vals['user_id'] = user_id
        return super(res_partner,self).create(vals)
    
class od_res_part_sales_action(models.Model):
    _name = "od.res.part.sales.action"
    ACT_TYPE_DOM = [
                    ('top_mgmt_visit','Top Management Visit'),
                    ('visit_cust_with_presales','Visit Customer With Pre-Sales'),
                    ('business_dev_visit','Business Development Visit'),
                    ('presentation','Presentation'),
                    ('poc','POC'),
                    ('marketting','Marketting'),
                    ('training','Training'),
                    ('my_own_sales_visit','My Own Sales Visit'),
                    ('engagement_with_principle_vendor','Engagement with Principle Vendor')
                    ]
    partner_id = fields.Many2one('res.partner',string="Partner")
    sales_action_type = fields.Selection(ACT_TYPE_DOM,string="Sales Action Type")
    objective = fields.Char(string='Objective')
    date = fields.Date(string='Date/Month')