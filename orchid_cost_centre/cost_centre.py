#-*- coding:utf-8 -*-
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _

class od_cost_division(osv.osv):
    _name = 'od.cost.division'
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id
    def onchange_manager_id(self, cr, uid, ids, manager_id=False, context=None):
        res = {}
        if manager_id:
            employee_pool = self.pool.get('hr.employee')
            emp_obj = employee_pool.browse(cr,uid,manager_id)
            email = emp_obj.work_email
            res['value'] = {'email': email}
        return res

    _columns = {
        'name': fields.char('Name',size=128,required="1"),
        'code': fields.char('Code',size=10,required="1"),
        'description': fields.text('Description'),
        'company_id': fields.many2one('res.company','Company'),
        'manager_id':fields.many2one('hr.employee',string="Manager"),
        'division_manager_id':fields.many2one('res.users',string="Division Manager"),
        'email':fields.char(string='E-mail'),
        'tech_consult_id':fields.many2one('res.users',string="Technology Unit Manager"),
         'pdt_grp_id':fields.many2one('od.product.group',string="Product Group"),
        'unit_alias':fields.char(string='Unit Alias'),
    }
    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'Code must be unique...!'),
    ]
    _defaults = {
        'company_id': _get_default_company,
    }

class od_cost_branch(osv.osv):
    _name = 'od.cost.branch'
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id
    
    def onchange_manager_id(self, cr, uid, ids, manager_id=False, context=None):
        res = {}
        if manager_id:
            employee_pool = self.pool.get('hr.employee')
            emp_obj = employee_pool.browse(cr,uid,manager_id)
            email = emp_obj.work_email
            res['value'] = {'email': email}
        return res
    
    _columns = {
        'name': fields.char('Name',size=128,required="1"),
        'code': fields.char('Code',size=10,required="1"),
        'description': fields.text('Description'),
        'company_id': fields.many2one('res.company','Company'),
        'manager_id':fields.many2one('hr.employee',string="Manager"),
        'branch_manager_id':fields.many2one('res.users',string="Branch Manager"),
        'pmo_manager_id':fields.many2one('res.users',string="PMO Manager"),
        'tech_consult_id':fields.many2one('res.users',string="Technology Consultant"),
        'unit_alias':fields.char(string='Unit Alias'),
        'email':fields.char(string='E-mail'),
    }
    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'Code must be unique...!'),
    ]
    _defaults = {
        'company_id': _get_default_company,
    }

class od_cost_centre(osv.osv):
    _name = 'od.cost.centre'
    _description = 'OD Cost Centre'

    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id

    _columns = {
        'name': fields.char('Name',size=128,required="1"),
        'code': fields.char('Code',size=10,required="1"),
        'branch_id': fields.many2one('od.cost.branch','Branch'),
        'division_id': fields.many2one('od.cost.division','Division'),
        'currency_id': fields.many2one('res.currency','Default Currency'),
        'company_id': fields.many2one('res.company','Company',required=True),
        'description': fields.text('Description'),
    }
    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'Code must be unique...!'),
    ]
    _defaults = {
        'company_id': _get_default_company,
    }
