from openerp import models, fields, api
from datetime import datetime
from openerp.exceptions import Warning
class od_grn(models.Model):
    _name = 'od.grn'
    def od_get_company_id(self):
        return self.env.user.company_id
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    name = fields.Char('Name',readonly=True,default="/")
    date = fields.Date('Date',states={'draft':[('readonly',False)]},readonly=True,default=fields.Date.today)
    picking_id = fields.Many2one('stock.picking','Picking',domain=[('picking_type_id.code','=','incoming'),('state','=','assigned')],states={'draft':[('readonly',False)]},readonly=True,copy=False)
    state = fields.Selection([('draft','Draft'),('ready','Ready'),('done','Done')],'Status',default='draft')
    grn_lines = fields.One2many('od.grn.line','grn_id','Transfer Line',ondelete='cascade',copy=False,states={'draft':[('readonly',False)],'ready':[('readonly',False)]},readonly=True)
    _sql_constraints = [
        ('unique_picking_id', 'UNIQUE (picking_id)', 'Only one Document of Transfer allowed for one picking'),
        ]
    
    @api.model
    def create(self,vals):
        picking_obj = self.env['stock.picking']
        pick_id =vals.get('picking_id')
        pick_name = picking_obj.browse(pick_id).name
        vals['name'] = pick_name
        return super(od_grn,self).create(vals) 
    
    @api.one
    def unlink(self):
        if self.state == 'done':
            raise Warning("You Cannot Delete Transeferred Record")
        return super(od_grn,self).unlink()

    def od_check_serial_no(self,cr,uid,ids,context=None):
        obj = self.browse(cr,uid,ids,context)
        if not obj.grn_lines:
            raise Warning("No lines found") 
        company_id = obj.company_id and obj.company_id.id            
        for line in obj.grn_lines:
            lot_id = False
            if line.product_id and line.serial_no:
                lot_id = self.pool.get('stock.production.lot').search(cr,uid,[('name','=',line.serial_no),('product_id','=',line.product_id.id)])
                
                
                if lot_id and not line.new_lot:
                    lot_id = lot_id[0]
                    self.pool.get('od.grn.line').write(cr,uid,[line.id],{'lot_id':lot_id,'new_lot':False},context)
                else:
                    lot_id = self.pool.get('stock.production.lot').create(cr,uid,{'name':line.serial_no,'product_id':line.product_id.id})
                    self.pool.get('od.grn.line').write(cr,uid,[line.id],{'lot_id':lot_id,'new_lot':True},context)
                
                
    
    @api.one
    def reset(self):
        self.grn_lines = False
        self.state ='draft'    
    def od_validate(self):
        trans_obj = {}
        pick_mv = {}
        for line in self.grn_lines:
            trans_obj[line.product_id.id] = trans_obj.get(line.product_id.id,0)+line.qty
        for move in self.picking_id.move_lines:
            pick_mv[move.product_id.id] = pick_mv.get(move.product_id.id,0)+ move.product_uom_qty
        return trans_obj == pick_mv
    @api.one
    def od_transfer(self):
        processed_ids = []
#         check = self.od_validate()
#         
#         if not check:
#             raise Warning('Qty MisMatch in Picking Move line and Transfer Line,Please Correct It')
        if self.picking_id.state != 'assigned':
            raise Warning('This Picking Cannot Be Transfer In Current State') 
        for data in self:
            picking_id = data.picking_id 
            date = data.date
            for line in data.grn_lines:
                pack_data= {
                    'product_id': line.product_id.id,
                    'product_uom_id': line.product_uom_id.id,
                    'product_qty': line.qty,
                    'lot_id': line.lot_id.id,
                    'location_id': line.location_id.id,
                    'location_dest_id': line.location_dest_id.id,
                    'date':date ,
                    'owner_id': picking_id.owner_id.id,
                    'picking_id':picking_id.id
                        }
                packop_id = self.env['stock.pack.operation'].create(pack_data)
                processed_ids.append(packop_id.id)
        packops = self.env['stock.pack.operation'].search(['&', ('picking_id', '=', picking_id.id), '!', ('id', 'in', processed_ids)])
        packops.unlink()
        picking_id.do_transfer()
        self.state= 'done'
    @api.one
    def od_load(self):
        move_lines = []
        self.grn_lines.unlink()
        for line in self.picking_id.move_lines:
            move_lines.append({
                            'product_id':line.product_id.id,
                            'qty':line.product_uom_qty,
                            'product_uom_id':line.product_uom.id,
                            'location_id': line.location_id.id,
                            'location_dest_id':line.location_dest_id.id,
                            })
        self.grn_lines =move_lines
        self.state ='ready'
    @api.multi
    def grn_form_view(self):
        view = self.env.ref('orchid_beta.od_grn_form')
        return {
            
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'od.grn',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'res_id': self.ids[0],
            'context': self.env.context,
        }

    
    
        
class od_grn_line(models.Model):
    _name = 'od.grn.line'
    grn_id = fields.Many2one('od.grn',string='GRN')
    product_id = fields.Many2one('product.product',string='Product',required=True)
    qty = fields.Float(string='Quantity',digits=(6, 3),required=True)
    lot_id = fields.Many2one('stock.production.lot',string="Serial/Lot")
    serial_no = fields.Char(string="Serial No")
    product_uom_id = fields.Many2one('product.uom',string="UoM",required=True)
    location_id = fields.Many2one('stock.location',string="Source Location",required=True)
    location_dest_id = fields.Many2one('stock.location',string='Destination Location',required=True)
    new_lot = fields.Boolean(string="Is New Lot")
    
    @api.multi
    def multi_split_quantities(self):
        for data in self:
            if data.qty>1:
                qty= data.qty
                for num in range(1,int(qty)):
                    data.qty =1
                    new_id = data.copy(context=self.env.context)
                    new_id.qty = 1
        if self and self[0]:
            return self.grn_id.grn_form_view()
    @api.multi
    def split_quantities(self):
        for data in self:
            if data.qty>1:
                data.qty =(data.qty - 1)
                new_id = data.copy(context=self.env.context)
                new_id.qty = 1
        if self and self[0]:
            return self.grn_id.grn_form_view()
class stock_picking(models.Model):
    _inherit ='stock.picking'
    
    def od_open_split(self,cr,uid,ids,context=None):
        pick_id = ids[0]
        domain =[('picking_id','=',pick_id)]
        grn_id = self.pool.get('od.grn').search(cr,uid,domain)
        res= {
              
              'view_type': 'form',
              "view_mode": 'tree,form',
              'res_model': 'od.grn',
              'type': 'ir.actions.act_window',
              'domain': domain,
              'context': {'default_picking_id':pick_id},
              }
        if grn_id:
            res['res_id'] = grn_id[0]
        return res
