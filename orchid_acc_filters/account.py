# -*- coding: utf-8 -*-
from openerp.osv import fields, osv, expression

class account_account(osv.osv):
    """ Inherited to Filter based on Accounts in lines"""
    _inherit = 'account.account'
    _columns = {
        'analytic_acc_ids':fields.many2many('account.analytic.account','account_analytic_rel', 'account_id', 'analytic_id', 'Analytic Accounts'),
        'asset_cate_ids': fields.many2many('account.asset.category', 'account_asset_category_rel', 'account_id', 'asset_cate_id', 'Asset Category'),
        'product_ids': fields.many2many('product.product','od_account_pdt_rel','account_id','product_id','Product'),
        'customer': fields.boolean('Customer'),
        'supplier': fields.boolean('Supplier'),
        'employee': fields.boolean('Employee'),
        'od_is_analytic':fields.boolean('Required'),
        'od_is_asset':fields.boolean('Required'),
        'od_is_product':fields.boolean('Required'),
        }
account_account()

        
class account_analytic_account(osv.osv):
    _inherit = "account.analytic.account"
    _description = "account_analytic_account"
    
    def get_analytic_acc(self, cr, uid, ids, context=None):
        analytic_ids = []
        for ana_brw in self.browse(cr, uid, ids, context):
            s_ids = self.search(cr, uid, [('parent_id','=',ana_brw.id),('type','=','normal')])
            for s_id in s_ids:
                analytic_ids.append(s_id)
            view_type_ids = self.search(cr, uid, [('parent_id','=',ana_brw.id),('type','=','view')])
            if view_type_ids:
                ret_ids = self.get_analytic_acc(cr, uid, view_type_ids, context)
                for ret_id in  ret_ids:
                    analytic_ids.append(ret_id)
        return analytic_ids
        
    
    def _search(self, cr, user, args, offset=0, limit=None, order=None, context=None, count=False, access_rights_uid=None):
        if context and context.has_key('account_id') and context['account_id']:
            l2=[]
            ana_ids = []
            cr.execute("""select analytic_id from account_analytic_rel where account_id = %s """%(context['account_id']))
            l2.extend([i[0] for i in cr.fetchall()])
            if l2:
                ana_ids =  self.get_analytic_acc(cr, user, l2, context)
                ana_ids = list(set(ana_ids))
            if not ana_ids:
                return super(account_analytic_account, self)._search(cr, user, args, offset=offset, limit=limit, order=order, context=context)
            args.append(['id', 'in', ana_ids])
        return super(account_analytic_account, self)._search(cr, user, args, offset=offset, limit=limit, order=order, context=context)

account_analytic_account()

class account_asset_asset(osv.osv):
    _inherit = "account.asset.asset"
    
    def _search(self, cr, user, args, offset=0, limit=None, order=None, context=None, count=False, access_rights_uid=None):
        asset_ids = []
        if context and context.has_key('account_id') and context['account_id']:
            l2=[]
            ana_ids = []
            cr.execute("""select asset_cate_id from account_asset_category_rel where account_id = %s """%(context['account_id']))
            l2.extend([i[0] for i in cr.fetchall()])
            for l1 in l2:
                ass_ids = self.search(cr, user, [('category_id','=',l1)])
                for a_id in ass_ids:
                    asset_ids.append(a_id)
            args.append(['id', 'in', asset_ids])
        return super(account_asset_asset, self)._search(cr, user, args, offset=offset, limit=limit, order=order, context=context)

account_asset_asset()

class res_partner(osv.osv):
    _inherit = 'res.partner'
    
    def _search(self, cr, user, args, offset=0, limit=None, order=None, context=None, count=False, access_rights_uid=None):
        """ Method override to get partners which type define in account form"""
        acc_obj = self.pool.get('account.account')
        if context and context.has_key('account_id') and context['account_id']:
            part_ids = []
            acc_brw = acc_obj.browse(cr, user, context['account_id'])
            if acc_brw.customer:
                for cust_id in self.search(cr, user, [('customer','=',True)]):
                    part_ids.append(cust_id)
            if acc_brw.supplier:
                for sup_id in self.search(cr, user, [('supplier','=',True)]):
                    part_ids.append(sup_id)
            if acc_brw.employee:
                for emp_id in self.search(cr, user, [('customer','=',False),('supplier','=',False)]):
                    part_ids.append(emp_id)
#            if not acc_brw.customer or not acc_brw.supplier or not acc_brw.employee:
#                return super(res_partner, self)._search(cr, user, args, offset=offset, limit=limit, order=order, context=context)
            part_ids = list(set(part_ids))
            args.append(['id', 'in', part_ids])
        return super(res_partner, self)._search(cr, user, args, offset=offset, limit=limit, order=order, context=context)
      
res_partner()

class product_product(osv.osv):
    _inherit = 'product.product'

    def _search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False, access_rights_uid=None):
        """ Method override to get products based on the category given in Account"""
        categ_ids = []
        product_ids = []
        if context and context.has_key('account_id') and context['account_id']:
            cr.execute("""select product_id from od_account_pdt_rel where account_id = %s """%(context['account_id']))
            categ_ids.extend([i[0] for i in cr.fetchall()])
            if not categ_ids:
                return super(product_product, self)._search(cr, uid, args, offset=offset, limit=limit, order=order,context=context)
            for cat_id in categ_ids:
                pdt_id= self.search(cr, uid,[('categ_id','=',cat_id)])
                product_ids.extend(pdt_id)
            args.append(['id','in',product_ids])
        return super(product_product, self)._search(cr, uid, args, offset=offset, limit=limit, order=order,context=context)
