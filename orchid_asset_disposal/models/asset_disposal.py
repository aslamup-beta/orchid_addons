from openerp import models, fields, api
from openerp.exceptions import Warning
from openerp.tools.translate import _
class asset_disposal(models.Model):
    _name = 'asset.disposal'
    _description = 'Asset Disposal'
    _order = 'id desc'
    
    
    
    
    @api.one
    @api.depends('od_category_id')
    def _compute_asset_category(self):
        categ = self.env['account.asset.category']
        for x in self:
            if x.od_category_id:
                cat_id = x.od_category_id.id
                category_obj = categ.browse(cat_id)
                x.od_account_asset_id = category_obj.account_asset_id and category_obj.account_asset_id.id 
                x.od_account_depreciation_id = category_obj.account_depreciation_id and category_obj.account_depreciation_id.id
                x.od_acc_exp_dep_id = category_obj.account_expense_depreciation_id and category_obj.account_expense_depreciation_id.id
    @api.one
    @api.depends('od_asset_id')
    def _compute_asset_vals(self):
        asset =self.env['account.asset.asset']
        for x in self:
            if x.od_asset_id:
                asset_id = self.od_asset_id.id
                asset_obj = asset.browse(asset_id)
                x.od_category_id = asset_obj.category_id and asset_obj.category_id.id
                x.od_purchase_value = asset_obj.purchase_value
                x.od_asset_value = asset_obj.od_cost
                x.od_salvage_value = asset_obj.salvage_value
                x.od_residual_value = asset_obj.value_residual
    
    def od_get_company_id(self):
        return self.env.user.company_id
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    name = fields.Char(default='/')
    od_asset_id = fields.Many2one('account.asset.asset','Asset')
    od_category_id = fields.Many2one('account.asset.category','Asset Category',readonly=True,store=True,compute='_compute_asset_vals')
    od_sale_value = fields.Float(string='Sale Value')
    od_account_asset_id = fields.Many2one('account.account','Asset Account',readonly=True,store=True,compute='_compute_asset_category')
    od_account_depreciation_id = fields.Many2one('account.account','Depreciation Account',readonly=True,store=True,compute='_compute_asset_category')
    od_acc_exp_dep_id = fields.Many2one('account.account','Ex.Depreciation Account',readonly=True,store=True,compute='_compute_asset_category')
    od_partner_id = fields.Many2one('res.partner','Partner')
    od_prof_loss_acc_id = fields.Many2one('account.account','Profit/Loss Account')
    od_asset_value = fields.Float(string='Asset Value',readonly=True,store=True,compute='_compute_asset_vals')
    od_depr_value = fields.Float(string='Depreciation Value',readonly=True)
    od_exp_depr_value = fields.Float(string='Exp.Depreciation Value',readonly=True)
    od_purchase_value = fields.Float(string='Net Value',readonly=True,store=True,compute='_compute_asset_vals')
    od_salvage_value = fields.Float(string='Salvage Value',readonly=True,store=True,compute='_compute_asset_vals')
    od_residual_value = fields.Float(string='Residual Value',readonly=True,store=True,compute='_compute_asset_vals')
    od_journal_id = fields.Many2one('account.journal','Journal')
    od_sale_account_id = fields.Many2one('account.account','Sale Account')
    od_date = fields.Date(string="Disposal Date",default=fields.Date.today,required=True)
    od_disposed = fields.Boolean(default=False)
    od_computed = fields.Boolean(default=False)
    od_move_id = fields.Many2one('account.move')
#     od_entry_count = fields.Integer(compute=_compute_count)
    state = fields.Selection([
         ('draft', "Draft"),
         ('estimated', "Estimated"),
         ('disposed', "Disposed"),
    ], default='draft')
    
    
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        if vals.get('name', '/') == '/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'od.asset.disposal') or '/'
        return super(asset_disposal,self).create(cr, uid, vals, context=context)
    
    def _get_period(self, cr, uid, context=None):
        period_ids = self.pool.get('account.period').find(cr, uid, context=context)
        return period_ids and period_ids[0] or False
    
    def show_entries(self,cr,uid,ids,context=None):
        move_id = self.browse(cr,uid,ids).od_move_id.id
#         context = dict(context or {}, search_default_asset_id=asset_id, default_asset_id=asset_id)
        return {
            
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'domain':[('move_id','=',move_id)],
            'view_id': False,
            'type': 'ir.actions.act_window',
            'context':context
            
        }

    
    @api.one
    def asset_dispose(self):
        if self.state != 'disposed':
            asset_id = self.od_asset_id and self.od_asset_id.id
            account_asset_id = self.od_account_asset_id and self.od_account_asset_id.id
            account_depreciation_id = self.od_account_depreciation_id and self.od_account_depreciation_id.id
            partner_id = self.od_partner_id and self.od_partner_id.id
            prof_loss_acc_id = self.od_prof_loss_acc_id and self.od_prof_loss_acc_id.id
            sale_acc_id = self.od_sale_account_id and self.od_sale_account_id.id
            asset_value = self.od_asset_value
            depr_value = self.od_depr_value
            sale_value = self.od_sale_value
            profit_loss_value = sale_value - (asset_value - depr_value)
            journal_id = self.od_journal_id and self.od_journal_id.id
            period_id = self._get_period()
            name =self.name
            line_name = self.od_asset_id.name
            l1 = {
                'name': line_name,
                'credit': 0.0,
                'debit':depr_value,
                'account_id': account_depreciation_id,
                'date':self.od_date,
#                'asset_id':asset_id,
            }
            l2 = {
                'name':line_name,
                'debit': 0.0,
                'credit':asset_value ,
                'account_id': account_asset_id ,
                'date':self.od_date,
#                'asset_id':asset_id,
            }
            l3 = {
                'name':line_name,
                'credit':0.0,
                'debit':-profit_loss_value,
                'account_id':prof_loss_acc_id,
                'partner_id':partner_id,
                'date':self.od_date
                }
            l4 = {
                'name':line_name,
                'debit':0.0,
                'credit':profit_loss_value,
                'account_id':prof_loss_acc_id,
                'partner_id':partner_id,
                'date':self.od_date,
#                'asset_id':asset_id,
                }
            l5 = {
                'name':line_name,
                'debit':sale_value,
                'credit':0.0,
                'account_id':sale_acc_id,
                'date':self.od_date,
#                'asset_id':asset_id,
                }
            if profit_loss_value >= 0:
                
                move = self.env['account.move'].create({
                
                'name':name,
                'narration':name,
                'line_id': [(0, 0, l1), (0, 0, l2),(0, 0, l4),(0, 0, l5)],
                'journal_id': journal_id,
                'period_id': period_id,
                'date': self.od_date,
            })
            else:
                move = self.env['account.move'].create({
                
                'name':name,
                'narration':name,
                'line_id': [(0, 0, l1), (0, 0, l2),(0, 0, l3),(0, 0, l5)],
                'journal_id': journal_id,
                'period_id': period_id,
                'date': self.od_date,
            })
                
            self.od_move_id = move
            asset_id = self.od_asset_id.id    
            asset_obj = self.env['account.asset.asset'].browse(asset_id)
            asset_obj.state = 'close'
            if not asset_obj.od_closing_date:
                asset_obj.od_closing_date = self.od_date

            self.od_disposed = True
            self.state = 'disposed'
        else:
            raise Warning('You Already Created Journal Entry and Asset Closed')
        return self.write({})
    
    
    
#     @api.one
#     def compute_asset_query(self):
#         asset_account = self.od_account_asset_id.id
#         asset_id = self.od_asset_id.id
#         asset_acc_ids = [x.id for x in self.env.search([('')])]
    
    def compute_asset_query(self,cr,uid,ids,context=None):
        asset_id = self.browse(cr,uid,ids).od_asset_id.id
        account_expense_depreciation_id = self.browse(cr,uid,ids).od_acc_exp_dep_id.id
        query_params = (account_expense_depreciation_id,asset_id)
        depreciation = self.browse(cr,uid,ids).od_asset_id.od_depreciation or 0.0
        cr.execute("select sum(debit-credit) from account_move_line where account_id=%s  and asset_id=%s ",query_params)
        od_exp_depr_value = cr.fetchone()[0] or 0.0
    
        total = od_exp_depr_value + depreciation
        depr_value= 0.0
        if total:
            depr_value = total
        vals = {'od_exp_depr_value':total,'od_depr_value': total,'od_computed':True,'state':'estimated'}
        self.write(cr,uid,ids,vals,context=context)
        return True
     
        
        
#     @api.one 
#     def compute_asset(self):
#         asset_id = self.od_asset_id.id
#         account_asset_id = self.od_account_asset_id.id
#         account_depreciation_id = self.od_account_depreciation_id.id
#         account_expense_depreciation_id = self.od_acc_exp_dep_id.id
#         exp_depr_ids = []
#         asset_acc_ids = []
#         depr_acc_ids = []
#         domain_exp_depr =[('asset_id','=',asset_id),('account_id','=',account_expense_depreciation_id)]
#         domain_depr =[('asset_id','=',asset_id),('account_id','=',account_depreciation_id)]
#         domain_asset =[('asset_id','=',asset_id),('account_id','=',account_asset_id)]
#         for x in self.env['account.move.line'].search(domain_exp_depr):
#             exp_depr_ids.append(x.id)
#         for x in self.env['account.move.line'].search(domain_asset):
#             asset_acc_ids.append(x.id)
#         for x in self.env['account.move.line'].search(domain_depr):
#             depr_acc_ids.append(x.id)
#              
#         balance_exp_depr= 0.0
#         balance_depr= 0.0
#         balance_asset= 0.0
#         for line_id in exp_depr_ids:
#             move_line=self.env['account.move.line'].browse(line_id)
#             debit = move_line.debit
#             credit = move_line.credit
#             balance_exp_depr += debit-credit
#         for line_id in depr_acc_ids:
#             move_line=self.env['account.move.line'].browse(line_id)
#             debit = move_line.debit
#             credit = move_line.credit
#             balance_depr += debit-credit
#         for line_id in asset_acc_ids:
#             move_line=self.env['account.move.line'].browse(line_id)
#             debit = move_line.debit
#             credit = move_line.credit
#             balance_asset += debit-credit
#         self.od_exp_depr_value = balance_exp_depr
#         self.od_depr_value = balance_depr
#         self.od_asset_value = balance_asset
    @api.onchange('od_category_id')
    def _onchange_asset_category(self):
        if self.od_category_id:
            cat_id = self.od_category_id.id
            category_obj = self.env['account.asset.category'].browse(cat_id)
            self.od_account_asset_id = category_obj.account_asset_id and category_obj.account_asset_id.id 
            self.od_account_depreciation_id = category_obj.account_depreciation_id and category_obj.account_depreciation_id.id
            self.od_acc_exp_dep_id = category_obj.account_expense_depreciation_id and category_obj.account_expense_depreciation_id.id
    @api.onchange('od_asset_id')
    def _onchange_asset_id(self):
        if self.od_asset_id:
            asset_id = self.od_asset_id.id
            asset_obj = self.env['account.asset.asset'].browse(asset_id)
            self.od_category_id = asset_obj.category_id and asset_obj.category_id.id
            self.od_purchase_value = asset_obj.purchase_value
            self.od_asset_value = asset_obj.od_cost
            self.od_salvage_value = asset_obj.salvage_value
            self.od_residual_value = asset_obj.value_residual
asset_disposal()
