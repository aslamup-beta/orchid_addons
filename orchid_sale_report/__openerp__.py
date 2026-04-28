# -*- coding: utf-8 -*-
{
    "name" : "Orchid Sale Reports",
    "version" : "0.1",
    "author": "OrchidERP",
    "category" : "Sales Management",
    "description": """OrchidERP Sales Reports""",
    "website": ["http://www.orchiderp.com"],
    "depends": ['sale','sale_order_dates','orchid_invoice','orchid_report','orchid_purchase_report'],
    "data" : [
           # 'report/sale_report_view.xml',
            'report/od_so_register_report_view.xml',
#            'report/od_so_po_document_analysis_view.xml',
            'report/od_sales_cost_view.xml',
#            'report/od_sales_partners_analysis_view.xml',
#            'report/od_sales_invoice_analysis_view.xml',
            'menu_view.xml'
            ],
    'css': [],
}
