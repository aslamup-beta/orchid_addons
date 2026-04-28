import openerp.exceptions
from openerp.osv import fields, osv, expression
from openerp import SUPERUSER_ID

class res_users(osv.osv):
    _inherit = 'res.users'
    _columns = {
        'od_sales_team_ids': fields.many2many('crm.case.section', 'sale_member_rel','member_id', 'section_id',  'Team Members'),
    }
       
    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if args is None:
            args = []
        if context is None:
            context={}
        if context.get('sam_ids',False):
            company_id = self.browse(cr, uid, uid, context=context).company_id.id
            hr_pool = self.pool.get('hr.employee')
            emp_ids = hr_pool.search(cr, SUPERUSER_ID,  [('company_id', '=', company_id),('job_id', 'in', (17, 40, 83, 104, 130, 138, 140, 154, 182))], context=context)
            user_ids = [6]
            for emp_id in emp_ids:
                employee = hr_pool.browse(cr,SUPERUSER_ID,emp_id)
                user_ids.append(employee.user_id.id)
            if name:
                ids = self.search(cr, uid, [('name', operator, name),('id','in',user_ids)] + args, limit=limit, context=context or {})
            else:
                domain =[('id','in',user_ids)]
                ids = self.search(cr, uid, expression.AND([domain, args]), limit=limit, context=context)
            return self.name_get(cr, uid, ids, context=context)
        if context.get('not_sam_ids',False):
            company_id = self.browse(cr, uid, uid, context=context).company_id.id
            hr_pool = self.pool.get('hr.employee')
            emp_ids = hr_pool.search(cr, SUPERUSER_ID,  [('company_id', '=', company_id),('job_id', 'not in', (40, 83, 182))], context=context)
            user_ids = []
            for emp_id in emp_ids:
                employee = hr_pool.browse(cr,SUPERUSER_ID,emp_id)
                user_ids.append(employee.user_id.id)
            if name:
                ids = self.search(cr, uid, [('name', operator, name),('id','in',user_ids)] + args, limit=limit, context=context or {})
            else:
                domain =[('id','in',user_ids)]
                ids = self.search(cr, uid, expression.AND([domain, args]), limit=limit, context=context)
            return self.name_get(cr, uid, ids, context=context)
        if context.get('presale_ids',False):
            company_id = self.browse(cr, uid, uid, context=context).company_id.id
            hr_pool = self.pool.get('hr.employee')
            emp_ids = hr_pool.search(cr, SUPERUSER_ID,  [('company_id', '=', company_id),('job_id', 'in', (28,78,168,172,174,183,184,197,207,208,217))], context=context)
            user_ids = []
            for emp_id in emp_ids:
                employee = hr_pool.browse(cr,SUPERUSER_ID,emp_id)
                user_ids.append(employee.user_id.id)
#             user_ids = list(set(user_ids))
            if name:
                ids = self.search(cr, uid, [('name', operator, name),('id','in',user_ids)] + args, limit=limit, context=context or {})
            else:
                domain =[('id','in',user_ids)]
                ids = self.search(cr, uid, expression.AND([domain, args]), limit=limit, context=context)
            return self.name_get(cr, uid, ids, context=context)
        if context.get('solution_arch_ids',False):
            company_id = self.browse(cr, uid, uid, context=context).company_id.id
            hr_pool = self.pool.get('hr.employee')
            emp_ids = hr_pool.search(cr, SUPERUSER_ID,  [('company_id', '=', company_id),('job_id', 'in', (168,172,174,184,197,207,208,217))], context=context)
            user_ids = []
            for emp_id in emp_ids:
                employee = hr_pool.browse(cr,SUPERUSER_ID,emp_id)
                user_ids.append(employee.user_id.id)
#             user_ids = list(set(user_ids))
            if name:
                ids = self.search(cr, uid, [('name', operator, name),('id','in',user_ids)] + args, limit=limit, context=context or {})
            else:
                domain =[('id','in',user_ids)]
                ids = self.search(cr, uid, expression.AND([domain, args]), limit=limit, context=context)
            return self.name_get(cr, uid, ids, context=context)
        if context.get('bdm_ids',False):
            company_id = self.browse(cr, uid, uid, context=context).company_id.id
            hr_pool = self.pool.get('hr.employee')
            emp_ids = hr_pool.search(cr, SUPERUSER_ID,  [('company_id', '=', company_id),('job_id', 'in', (13, 45, 87, 124, 136, 137, 146, 152, 157, 158,28))], context=context)
            user_ids = []
            for emp_id in emp_ids:
                employee = hr_pool.browse(cr,SUPERUSER_ID,emp_id)
                user_ids.append(employee.user_id.id)
#             user_ids = list(set(user_ids))
            if name:
                ids = self.search(cr, uid, [('name', operator, name),('id','in',user_ids)] + args, limit=limit, context=context or {})
            else:
                domain =[('id','in',user_ids)]
                ids = self.search(cr, uid, expression.AND([domain, args]), limit=limit, context=context)
            return self.name_get(cr, uid, ids, context=context)
        if context.get('assign_ids',False):
            company_id = self.browse(cr, uid, uid, context=context).company_id.id
            hr_pool = self.pool.get('hr.employee')
            emp_ids = hr_pool.search(cr, SUPERUSER_ID,  [('company_id', '=', company_id),('job_id', 'in', (47, 107, 44, 86, 185, 186, 187, 184))], context=context)
            user_ids = [23]
            for emp_id in emp_ids:
                employee = hr_pool.browse(cr,SUPERUSER_ID,emp_id)
                user_ids.append(employee.user_id.id)
#             user_ids = list(set(user_ids))
            if name:
                ids = self.search(cr, uid, [('name', operator, name),('id','in',user_ids)] + args, limit=limit, context=context or {})
            else:
                domain =[('id','in',user_ids)]
                ids = self.search(cr, uid, expression.AND([domain, args]), limit=limit, context=context)
            return self.name_get(cr, uid, ids, context=context)
        if context.get('technicians_ids',False):
            company_id = self.browse(cr, uid, uid, context=context).company_id.id
            hr_pool = self.pool.get('hr.employee')
            emp_ids = hr_pool.search(cr, SUPERUSER_ID,  [('company_id', '=', company_id),('job_id', 'in', (44,86))], context=context)
            user_ids = [310]
            for emp_id in emp_ids:
                employee = hr_pool.browse(cr,SUPERUSER_ID,emp_id)
                user_ids.append(employee.user_id.id)
#             user_ids = list(set(user_ids))
            if name:
                ids = self.search(cr, uid, [('name', operator, name),('id','in',user_ids)] + args, limit=limit, context=context or {})
            else:
                domain =[('id','in',user_ids)]
                ids = self.search(cr, uid, expression.AND([domain, args]), limit=limit, context=context)
            return self.name_get(cr, uid, ids, context=context)
        if context.get('reviewer_ids',False):
            company_id = self.browse(cr, uid, uid, context=context).company_id.id
            hr_pool = self.pool.get('hr.employee')
            emp_ids = hr_pool.search(cr, SUPERUSER_ID,  [('company_id', '=', company_id),('job_id', 'in', (45, 87, 124, 214, 216))], context=context)
            user_ids = [2201] #raed klaib temp reviewer
            for emp_id in emp_ids:
                employee = hr_pool.browse(cr,SUPERUSER_ID,emp_id)
                user_ids.append(employee.user_id.id)
#             user_ids = list(set(user_ids))
            if name:
                ids = self.search(cr, uid, [('name', operator, name),('id','in',user_ids)] + args, limit=limit, context=context or {})
            else:
                domain =[('id','in',user_ids)]
                ids = self.search(cr, uid, expression.AND([domain, args]), limit=limit, context=context)
            return self.name_get(cr, uid, ids, context=context)
        
        if context.get('project_manager',False):
            company_id = self.browse(cr, uid, uid, context=context).company_id.id
            hr_pool = self.pool.get('hr.employee')
            emp_ids = hr_pool.search(cr, SUPERUSER_ID,  [('company_id', '=', company_id),('job_id', 'in', (30, 31, 43, 80, 82, 85, 164, 166,132,125,190,79,214,216))], context=context)
            user_ids = []
            for emp_id in emp_ids:
                employee = hr_pool.browse(cr,SUPERUSER_ID,emp_id)
                user_ids.append(employee.user_id.id)
#             user_ids = list(set(user_ids))
            if name:
                ids = self.search(cr, uid, [('name', operator, name),('id','in',user_ids)] + args, limit=limit, context=context or {})
            else:
                domain =[('id','in',user_ids)]
                ids = self.search(cr, uid, expression.AND([domain, args]), limit=limit, context=context)
            return self.name_get(cr, uid, ids, context=context)

        return super(res_users, self).name_search(cr, uid, name, args=args, operator=operator, context=context, limit=limit)


class account_analytic_account(osv.osv):
    _inherit = 'account.analytic.account'
    
    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if args is None:
            args = []
        if context is None:
            context={}
        if context.get('only_child_account',False):
            analytic_ids = []
            analytic_id = context.get('ao_id',False)
            if analytic_id:
                analytic_ids = self.search(cr, uid, [('parent_id','=',analytic_id),('type','=','contract')],context=context)
                grand_child_ids =self.search(cr, uid, [('grand_parent_id','=',analytic_id),('type','=','contract')], context=context)
                analytics = analytic_ids + grand_child_ids
                for a_id in analytics:
                    analytic = self.browse(cr,SUPERUSER_ID,a_id)
                    analytic_ids.append(analytic.id)
            if name:
                ids = self.search(cr, uid, [('name', operator, name),('id','in',analytic_ids)] + args, limit=limit, context=context or {})
            else:
                domain =[('id','in',analytic_ids)]
                ids = self.search(cr, uid, expression.AND([domain, args]), limit=limit, context=context)
            return self.name_get(cr, uid, ids, context=context)
        
        if context.get('analytic_all',False):
            analytic_ids = self.search(cr, uid, [('type','=','contract')],context=context)
            if name:
                ids = self.search(cr, uid, [('name', operator, name),('id','in',analytic_ids)] + args, limit=limit, context=context or {})
            else:
                domain =[('id','in',analytic_ids)]
                ids = self.search(cr, uid, expression.AND([domain, args]), limit=limit, context=context)
            return self.name_get(cr, uid, ids, context=context)
        
        if context.get('signed_off',False):
            analytic_ids = self.search(cr, uid, [('state','=','sign_off'),('type','=','contract'),('od_type_of_project','not in',('parent_level0','amc_view','o_m_view'))],context=context)
            if name:
                ids = self.search(cr, uid, [('name', operator, name),('id','in',analytic_ids)] + args, limit=limit, context=context or {})
            else:
                domain =[('id','in',analytic_ids)]
                ids = self.search(cr, uid, expression.AND([domain, args]), limit=limit, context=context)
            return self.name_get(cr, uid, ids, context=context)


        return super(account_analytic_account, self).name_search(cr, uid, name, args=args, operator=operator, context=context, limit=limit)

    