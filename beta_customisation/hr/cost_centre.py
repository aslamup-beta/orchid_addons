#-*- coding:utf-8 -*-
from openerp.osv import osv, fields
from openerp.tools.translate import _




class od_cost_branch(osv.osv):
    _inherit = 'od.cost.branch'
    
    _columns = {
       
        'manager_user_id':fields.many2one('res.users',string="Manager User"),
        'sm_user_id':fields.many2one('res.users',string="Sales Manager"),
        'active':fields.boolean(string="Active")
    }
    _defaults = {'active': True,
                 }
    
class od_cost_division(osv.osv):
    _inherit = 'od.cost.division'
    
    _columns = {
       
        'manager_user_id':fields.many2one('res.users',string="Manager User"),
        'od_tech_lead':fields.many2one('res.users',string="Technical Lead"),
        'od_presales_lead':fields.many2one('res.users',string="Pre Sales Lead"),
        'mp_target':fields.float("MP Target"),
        'tc':fields.float("Technology Consultant Required"),
        'division_staff_ids':fields.one2many('division.staff.req','division_id', "Division Staffs Required"),
        'active':fields.boolean(string="Active")
    }
    _defaults = {'active': True,
                 }
    
class od_cost_centre(osv.osv):
    _inherit = 'od.cost.centre'
    
    _columns = {
                'active':fields.boolean(string="Active")
                }
    
    _defaults = {'active': True,
                 }
    
class division_staff_req(osv.osv):
    _name = 'division.staff.req'
    
    _columns = {
    'division_id': fields.many2one('od.cost.division',string="Division"),
    'branch_id': fields.many2one('od.cost.branch', string="Branch"),
    'job_id': fields.many2one('hr.job', string="Job"),
    'required': fields.integer("Required"),
    'available':fields.float(string="Available"),
    'weight':fields.float(string="Weight")
    }
    