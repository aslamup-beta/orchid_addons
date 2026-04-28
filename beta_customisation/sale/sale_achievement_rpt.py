# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.addons.crm import crm
from openerp.osv import fields, osv
from openerp import tools

class sales_achievement_report(osv.osv):
    """ Sales Achievement Report """
    _name = "sales.achieve.report"
    _auto = False
    _description = "Sales Achievement Report"
    _rec_name = 'sam_id'

    _columns = {
        'month_start': fields.date('Month Start', readonly=True),
        'month_end': fields.date('Month End', readonly=True),
        'sam_id':fields.many2one('hr.employee', 'Sale Account Manager', readonly=True),
        'company_id': fields.many2one('res.company', 'Company', readonly=True),
        'annual_target': fields.float('Annual Target',digits=(16,2),readonly=True),
        'mnthly_target': fields.float('Monthly Target',digits=(16,2),readonly=True), 
        'accumulated_target': fields.float('Accumulated Target', digits=(16,2),readonly=True),
        'commit_kpi': fields.float('Commit', digits=(16,2),readonly=True),
        'commit_perc': fields.float('Commit Percentage', digits=(16,2),readonly=True),
        'achieved_kpi': fields.float('Achieved', digits=(16,2),readonly=True),
        'achieved_perc': fields.float('Achieved Percentage', digits=(16,2),readonly=True),
        'accumulated_achiev': fields.float('Accumulated Achievement', digits=(16,2),readonly=True),
        'deficit': fields.float('Deficit', digits=(16,2),readonly=True),
        'amt_to_target': fields.float('Amount to Target', digits=(16,2),readonly=True)
        
    }

    def init(self, cr):
  
        """
            Sales Achievement Report
            @param cr: the current row, from the database cursor
        """
        tools.drop_view_if_exists(cr, 'sales_achieve_report')
        cr.execute("""
            CREATE OR REPLACE VIEW sales_achieve_report AS (
               SELECT
                    c.id,
                    c.date_start as month_start,
                    c.date_end as month_end,
                    c.employee_id as sam_id,
                    c.company_id,
                    c.target*12 as annual_target,
                    c.target as mnthly_target,
                   
                    c.target + COALESCE(
                         (
                            SELECT SUM(b.target)
                            FROM audit_sample b
                            WHERE b.date_start < c.date_start AND
                            b.date_start >='01-Jan-19' AND
                             b.employee_id=c.employee_id
                            
                          ), 0) as accumulated_target,
                    
                          
                   
                    sum(DISTINCT  l.gp) as commit_kpi,
                    (sum(DISTINCT l.gp)/NULLIF(c.target,0))*100 as commit_perc,
                    sum(DISTINCT p.gp) as achieved_kpi,
                    (sum(DISTINCT p.gp)/NULLIF(c.target,0))*100 as achieved_perc,
                                               
                    COALESCE(sum(DISTINCT p.gp), 0) + COALESCE(
                         (
                            SELECT SUM(DISTINCT  x.gp)
                            FROM audit_sample m
                            LEFT JOIN achieved_gp_sample_line x ON (x.sample_id=m.id)
                            WHERE m.date_start < c.date_start AND
                            m.date_start >='01-Jan-20' AND
                             m.employee_id=c.employee_id
                          ), 0) as accumulated_achiev,
                                 
                    (COALESCE(sum(DISTINCT p.gp), 0) + COALESCE(
                         (
                            SELECT SUM(DISTINCT  x.gp)
                            FROM audit_sample m
                            LEFT JOIN achieved_gp_sample_line x ON (x.sample_id=m.id)
                            WHERE m.date_start < c.date_start AND
                            m.date_start >='01-Jan-20' AND
                             m.employee_id=c.employee_id
                          ), 0)) - (c.target + COALESCE(
                         (
                            SELECT SUM(b.target)
                            FROM audit_sample b
                            WHERE b.date_start < c.date_start AND
                            b.date_start >='01-Jan-20' AND
                            b.employee_id=c.employee_id
                            
                          ), 0)) as deficit,
                          
                        (COALESCE(sum(DISTINCT p.gp), 0) + COALESCE(
                         (
                            SELECT SUM(DISTINCT  x.gp)
                            FROM audit_sample m
                            LEFT JOIN achieved_gp_sample_line x ON (x.sample_id=m.id)
                            WHERE m.date_start < c.date_start AND
                            m.date_start >='01-Jan-20' AND
                             m.employee_id=c.employee_id
                          ), 0)) - c.target*12 as amt_to_target
                                               
                                               
                FROM
                    audit_sample c
                    LEFT JOIN commit_gp_sample_line l ON (l.sample_id=c.id)
                    LEFT JOIN achieved_gp_sample_line p ON (p.sample_id=c.id)
                    
                WHERE c.aud_temp_id = 5 AND
                      c.date_start >='01-Jan-20'
                  
                GROUP BY c.id
            )""")


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
