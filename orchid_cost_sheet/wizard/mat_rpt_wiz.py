from openerp import models, fields, api

class wiz_mat_report(models.TransientModel):

    _name = 'wiz.mat.report'
    brand_id = fields.Many2one('od.product.brand',string='Manufacturer',required=True)
    company_id = fields.Many2one('res.company',string="Company")
    mat_data = fields.One2many('wiz.mat.data','wiz_id')
    
    @api.one
    def generate(self):
        company_id = self.company_id and self.company_id.id
        domain = [('status','=','active'),('state','in',('draft','design_ready','submitted')),('company_id','=',company_id),('op_stage_id','not in',(7,8,13))]  
        brand_id = self.brand_id and self.brand_id.id 
        sheet_pool = self.env['od.cost.sheet']
        sheet_ids = sheet_pool.search(domain)
        data = []
        
        for sheet in sheet_ids:
            cost_sheet_id = sheet.id 
            partner_id = sheet.od_customer_id and sheet.od_customer_id.id
            cost =0.0
            for line in sheet.mat_main_pro_line:
                if line.od_manufacture_id.id == brand_id:
                    cost += line.discounted_total_supplier_currency 
                    currency_id = line.supplier_currency_id and line.supplier_currency_id.id
            data.append({'cost_sheet_id':cost_sheet_id,'brand_id':brand_id,'currency_id':currency_id,'partner_id':partner_id,'cost':cost})
            
            cost =0.0
            for line in sheet.trn_customer_training_extra_expense_line:
                if line.od_manufacture_id.id == brand_id:
                    cost += line.discounted_total_supplier_currency 
                    currency_id = line.supplier_currency_id and line.supplier_currency_id.id
            data.append({'cost_sheet_id':cost_sheet_id,'brand_id':brand_id,'currency_id':currency_id,'partner_id':partner_id,'cost':cost})
                    
            
        

           
    

class wiz_mat_data(models.TransientModel):

    _name = 'wiz.mat.data'

    wiz_id = fields.Many2one('wiz.mat.report',)
    brand_id = fields.Many2one('od.product.brand',string='Manufacturer')
    currency_id = fields.Many2one('res.currency',string="Currency")
    cost = fields.Float(string="Cost From Supplier")
    cost_local = fields.Float("Cost in Local Currency")
    cost_sheet_id = fields.Many2one('od.cost.sheet',string="Cost Sheet")
    tab = fields.Selection([('trn','Training'),('mat','Material')],string="Tab")
    partner_id = fields.Many2one('res.partner',string="Customer")