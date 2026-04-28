# -*- encoding: utf-8 -*-
import xlwt
import time
from datetime import datetime
from openerp.report import report_sxw
from openerp.addons.report_xls.report_xls import report_xls
from openerp.addons.report_xls.utils import rowcol_to_cell, _render
from openerp.tools.translate import _
from .od_stock_aging_report import report_orchid_stock_report

class stock_againg_xls_parser(report_orchid_stock_report):
    def __init__(self, cr, uid, name, context):
        super(stock_againg_xls_parser, self).__init__(cr, uid, name, context=context)


class stock_againg_xls(report_xls):
    column_sizes = [12,60,17,17,17,17,17,17]
    
    def generate_xls_report(self, _p, _xs, data, objects, wb):
       
        ws = wb.add_sheet('Aging Report')
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0 # Landscape
        ws.fit_width_to_pages = 1
        row_pos = 0
        lines = _p.get_lines(data)
        report_name = _("Stock Aging Report As On "+time.strftime('%d-%m-%Y '))
        if data.get('detail'):
            report_name = _("Stock Aging Report DetailAs On "+time.strftime('%d-%m-%Y '))


        # Title
        cell_format = _xs['bold'] + _xs['fill_grey'] + _xs['borders_all'] + _xs['center'] + _xs['xls_title']
        cell_style_header = xlwt.easyxf(cell_format)

        #Header Columns
        cell_format = _xs['bold'] + _xs['fill_blue'] + _xs['borders_all'] + _xs['center'] + _xs['underline']
        cell_style = xlwt.easyxf(cell_format)



        # lines
        aml_cell_format = _xs['borders_all']
        self.aml_cell_style = xlwt.easyxf(aml_cell_format)
        self.aml_cell_style_center = xlwt.easyxf(aml_cell_format + _xs['center'])
        self.aml_cell_style_date = xlwt.easyxf(aml_cell_format + _xs['left'], num_format_str=report_xls.date_format)
        self.aml_cell_style_decimal = xlwt.easyxf(aml_cell_format + _xs['right'], num_format_str=report_xls.decimal_format)


        # XLS Template
        self.col_specs_template = {
            'code': {
                'header': [1, 20, 'text',_("Code")],
                'lines': [1, 0, 'text', _render("str(line['product_id'].default_code or '')")]},

            'product_id': {
                'header': [1, 13, 'text',_("Description")],
                'lines': [1, 25, 'text',_render("str(line['product_id'].name)")]},
            'location_id': {
                'header': [1, 13, 'text',_("Location")],
                'lines': [1, 0, 'text', _render("str(line['lines'][0]['location_id'].complete_name)")]},
            'unit_id': {
                'header': [1, 13, 'text',_("Unit")],
                'lines': [1, 0, 'text', _render("str(line['product_id'].uom_id.name)")]},
            'p1': {
                'header': [1, 13, 'text',_("0-30444")],
                'lines': [1, 0, 'number', _render("line['lines'][0]['age'] in range(0,30) and line['lines'][0]['age'] or 0.0")]},
#                 'lines': [1, 0, 'number', _render("float(line['lines'][0]['age']) in range ()")]},
            'p2': {
                'header': [1, 13, 'text',_("30-60")],
                'lines': [1, 0, 'number', _render("line['lines'][0]['age'] in range(30,60) and line['lines'][0]['age'] or 0.0")]},
            'p3': {
                'header': [1, 13, 'text',_("60-90")],
                'lines': [1, 0, 'number',_render("line['lines'][0]['age'] in range(60,90) and line['lines'][0]['age'] or 0.0")]},
            'p4': {
                'header': [1, 13, 'text',_("90-120")],
                'lines': [1, 0, 'number', _render("line['lines'][0]['age'] in range(90,120) and line['lines'][0]['age'] or 0.0")]},
            'p4': {
                'header': [1, 13, 'text',_("120-ABV")],
                'lines': [1, 0, 'number', _render("line['lines'][0]['age'] >= 120 and line['lines'][0]['age'] or 0.0")]},
        }


        c_specs = [
            ('report_name', 8, 2, 'text', report_name),
        ]       
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=cell_style_header)


        field_list = ['code','product_id','location_id','unit_id','p1','p2','p3','p4']
        if data.get('detail'):
            row_pos +=1

            cell_format_pdt = _xs['bold'] + _xs['borders_all'] + _xs['underline']
            cell_style_pdt = xlwt.easyxf(cell_format_pdt)


            # XLS Template pdt
            self.col_specs_template = {

                'in_date': {
                    'header': [1, 20, 'text',_("In Date")],
                    'lines': [1, 0, 'text', _render("str(line['in_date'])")]},

                'location_id': {
                    'header': [1, 13, 'text',_("Location")],
                    'lines': [1, 0, 'text', _render("str(line['location_id'].complete_name)")]},

                'qty': {
                    'header': [1, 13, 'text',_("Qty")],
                    'lines': [1, 25, 'text',_render("str(line['qty'])")]},

                'unit_id': {
                    'header': [1, 13, 'text',_("Unit")],
                    'lines': [1, 0, 'text',_render("str(line['uom_id'].name)")]},
                'age': {
                    'header': [1, 13, 'text',_("Age")],
                    'lines': [1, 0, 'number',_render("str(line['age'])")]},
                'lot': {
                    'header': [1, 13, 'text',_("Lot/Serial")],
                    'lines': [1, 0, 'text',_render("str(line['lot'])")]},
                'inventory_value': {
                    'header': [1, 13, 'text',_("Inventory Value")],
                    'lines': [1, 0, 'number',_render("str(line['inventory_value'])")]},
            }
            field_list = ['in_date','location_id','qty','unit_id','age','lot','inventory_value']


            for product in lines:
                row_pos +=1

                product_name = _((product['product_id'].default_code or '') +' - '+(product['product_id'].name) or '' )
                c_specs_pdt = [
                    ('report_name', 5, 0, 'text', product_name),
                ]       
                row_data = self.xls_row_template(c_specs_pdt, [x[0] for x in c_specs_pdt])
                row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=cell_style_pdt)

                c1_specs = map(lambda x: self.render(x, self.col_specs_template, 'header'), field_list)
                row_data = self.xls_row_template(c1_specs, [x[0] for x in c1_specs])
                row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=cell_style)
                row_pos +=1
                for line in product['lines']:
                    line['uom_id'] = product['product_id'].uom_id

                    c1_specs = map(lambda x: self.render(x, self.col_specs_template, 'lines'), field_list)
                    row_data = self.xls_row_template(c1_specs, [x[0] for x in c1_specs])
                    row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=self.aml_cell_style)

        else:

            c1_specs = map(lambda x: self.render(x, self.col_specs_template, 'header'), field_list)
            row_data = self.xls_row_template(c1_specs, [x[0] for x in c1_specs])
            row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=cell_style)

            for line in lines:
                c1_specs = map(lambda x: self.render(x, self.col_specs_template, 'lines'), field_list)
                row_data = self.xls_row_template(c1_specs, [x[0] for x in c1_specs])
                row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=self.aml_cell_style)


stock_againg_xls('report.stock_aging_xls', 'stock.quant',
    parser=stock_againg_xls_parser)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
