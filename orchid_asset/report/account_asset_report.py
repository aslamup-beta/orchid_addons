# -*- encoding: utf-8 -*-
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

from openerp import tools
from openerp.osv import fields, osv

class asset_asset_report(osv.osv):
    _inherit = "asset.asset.report"
    _description = "Assets Analysis"
    _auto = False
    _columns = {
        'od_cost': fields.float('Cost', readonly=True),
        'od_depreciation': fields.float('Depreciation', readonly=True),
        
    }
    
    def init(self, cr):
    	tools.drop_view_if_exists(cr, 'asset_asset_report')
     	cr.execute("""
    	    create or replace view asset_asset_report as (
                select 
                    min(dl.id) as id,
                    dl.name as name,
                    dl.depreciation_date as depreciation_date,
                    a.purchase_date as purchase_date,
                    (CASE WHEN (select min(d.id) from account_asset_depreciation_line as d
                                left join account_asset_asset as ac ON (ac.id=d.asset_id)
                                where a.id=ac.id) = min(dl.id)
                      THEN a.purchase_value
                      ELSE 0
                      END) as gross_value,
                    dl.amount as depreciation_value, 
                    (CASE WHEN dl.move_check
                      THEN dl.amount
                      ELSE 0
                      END) as posted_value,
                    (CASE WHEN NOT dl.move_check
                      THEN dl.amount
                      ELSE 0
                      END) as unposted_value,
                    dl.asset_id as asset_id,
                    dl.move_check as move_check,
                    a.category_id as asset_category_id,
                    a.partner_id as partner_id,
                    a.state as state,
                    count(dl.*) as nbr,
                    a.od_cost as od_cost,
                    a.od_depreciation as od_depreciation,
                    a.company_id as company_id
                from account_asset_depreciation_line dl
                    left join account_asset_asset a on (dl.asset_id=a.id)
                group by 
                    dl.amount,dl.asset_id,dl.depreciation_date,dl.name,
                    a.purchase_date, dl.move_check, a.state, a.category_id, a.partner_id, a.company_id,
                    a.purchase_value,a.od_depreciation,a.od_cost, a.id, a.salvage_value
        )""")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
