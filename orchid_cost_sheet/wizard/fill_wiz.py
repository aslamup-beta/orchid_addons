from openerp import models, fields, api

class wiz_ren_fill(models.TransientModel):

    _name = 'wiz.ren.fill'
    mat_data = fields.One2many('wiz.fill.data','wiz_id')

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        cost_sheet_pool = self.pool.get('od.cost.sheet')
        res = super(wiz_ren_fill, self).default_get(cr, uid, fields, context=context)
        cost_sheet_id = context.get('active_id',False)
        items =[]
        if cost_sheet_id and not context.get('optional'):
            for mat_line in cost_sheet_pool.browse(cr,uid,cost_sheet_id).mat_main_pro_line:
                if mat_line.ren:
                    items.append({
                                  'brand_id':mat_line.manufacture_id and mat_line.manufacture_id.id,
                                  'product_id':mat_line.part_no and mat_line.part_no.id,
                                  'qty':mat_line.qty
                                  })

        if cost_sheet_id and context.get('optional'):
            for mat_line in cost_sheet_pool.browse(cr,uid,cost_sheet_id).mat_optional_item_line:
                if mat_line.ren:
                    items.append({
                                  'brand_id':mat_line.manufacture_id and mat_line.manufacture_id.id,
                                  'product_id':mat_line.part_no and mat_line.part_no.id,
                                  'qty':mat_line.qty
                                  })
        res['mat_data'] = items
        return res


    @api.one
    def fill_ren(self):
        sheet_pool = self.env['od.cost.sheet']
        sheet_id =self.env.context.get('active_id',False)
        sheet_obj = sheet_pool.browse(sheet_id)
        items = []
        count = 0
        for data in self.mat_data:

            qty = data.qty
            for i in range(qty):
                count +=1
                items.append({'item':count,
                              'manufacture_id':data.brand_id and data.brand_id.id,
                              'renewal_package_no':data.product_id and data.product_id.id })
        if self.env.context.get('optional'):
            sheet_obj.ren_optional_item_line = items
        else:
            sheet_obj.ren_main_pro_line = items

class wiz_fill_data(models.TransientModel):

    _name = 'wiz.fill.data'

    wiz_id = fields.Many2one('wiz.ren.fill')
    brand_id = fields.Many2one('od.product.brand',string='Manufacturer',required=True)
    product_id = fields.Many2one('product.product',string='Part No',required=True)
    qty = fields.Integer(string='Qty')
