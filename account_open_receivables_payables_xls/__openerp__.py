# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 orchiderp nv/sa (www.orchiderp.com). All rights reserved.
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

{
    'name': 'Open Receivables/Payables XLS export',
    'version': '0.5',
    'license': 'AGPL-3',
    'author': 'orchiderp',
    'category': 'Hidden',
    'description': """
This module adds the 'Open Receivables/Payables by Period' report to the Accounting Partners reports.
The report is available in PDF and XLS format.
    """,
    'depends': ['account', 'report_xls'],
    'demo_xml': [],
    'init_xml': [],
    'update_xml' : [
        'wizard/partner_open_arap.xml',      
    ],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
