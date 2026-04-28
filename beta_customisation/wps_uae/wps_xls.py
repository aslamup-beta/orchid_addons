# -*- coding: utf-8 -*-
import xlwt
import time
from datetime import datetime
from openerp.osv import orm,fields
from openerp.report import report_sxw
from openerp.addons.report_xls.report_xls import report_xls
from openerp.addons.report_xls.utils import rowcol_to_cell, _render
from openerp.tools.translate import translate, _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from openerp import pooler
import logging
_logger = logging.getLogger(__name__)

_ir_translation_name = 'uae.payroll.cards.xls'

class uae_wps_xls_parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(uae_wps_xls_parser, self).__init__(cr, uid, name, context=context)
        hr_payslip_obj = self.pool.get('hr.payslip')
        self.context = context
        wanted_list = hr_payslip_obj._report_xls_fields_uae(cr, uid, context)
        template_changes = hr_payslip_obj._report_xls_template_uae(cr, uid, context)
        self.localcontext.update({
            'datetime': datetime,
            'wanted_list': wanted_list,
            'template_changes': template_changes,
            '_': self._,
        })

    def _(self, src):
        lang = self.context.get('lang', 'en_US')
        return translate(self.cr, _ir_translation_name, 'report', lang, src) or src

class uae_wps_xls(report_xls):

    def __init__(self, name, table, rml=False, parser=False, header=True, store=False):
        super(uae_wps_xls, self).__init__(name, table, rml, parser, header, store)
        
        # Cell Styles
        _xs = self.xls_styles
        # header
        rh_cell_format = _xs['bold'] + _xs['fill'] + _xs['borders_all']
        self.rh_cell_style = xlwt.easyxf(rh_cell_format)
        self.rh_cell_style_center = xlwt.easyxf(rh_cell_format + _xs['center'])
        self.rh_cell_style_right = xlwt.easyxf(rh_cell_format + _xs['right'])

        # lines
        aml_cell_format = _xs['borders_all']
        self.aml_cell_style = xlwt.easyxf(aml_cell_format)
        self.aml_cell_style_center = xlwt.easyxf(aml_cell_format + _xs['center'])
        self.aml_cell_style_date = xlwt.easyxf(aml_cell_format + _xs['left'], num_format_str=report_xls.date_format)
        self.aml_cell_style_decimal = xlwt.easyxf(aml_cell_format + _xs['right'], num_format_str=report_xls.decimal_format)

        # totals
        rt_cell_format = _xs['bold'] + _xs['fill'] + _xs['borders_all']
        self.rt_cell_style = xlwt.easyxf(rt_cell_format)
        self.rt_cell_style_right = xlwt.easyxf(rt_cell_format + _xs['right'])
        self.rt_cell_style_decimal = xlwt.easyxf(rt_cell_format + _xs['right'], num_format_str=report_xls.decimal_format)

        # XLS Template
        self.col_specs_template = {
        
            'emp_uid': {
                'header': [1, 13, 'text', _render("_('EmpUID')")],
                'lines': [1, 0, 'text', _render("line.contract_id.permit_no or ''")],
                'totals': [1, 0, 'text', None]},


            'routing_code':{
                'header': [1, 20, 'text', _render("_('Bank Routing code')")],
                'lines': [1, 0, 'text', _render("line.contract_id.xo_routing_code or ''")],
                'totals': [1, 0, 'text', None]},

            'bank_ac':{
                'header': [1, 20, 'text', _render("_('Account with Agent')")],
                'lines': [1, 0, 'text', _render("line.employee_id.bank_account_id and line.employee_id.bank_account_id.acc_number or ''")],
                'totals': [1, 0, 'text', None]},
            
            'net_salary':{
                'header': [1, 20, 'text', _render("_('Fixed Salary')")],
                'lines': [1, 0, 'number', _render("sum([c.amount for c in line.line_ids if c.code == 'UAE_NET']) or 0.0")],
                'totals': [1, 0, 'text', None]},
            
             'variable_salary':{
                'header': [1, 20, 'text', _render("_('Variable Salary')")],
                'lines': [1, 0, 'number', _render("0.0")],
                'totals': [1, 0, 'text', None]},
             
             'lpo':{
                'header': [1, 20, 'text', _render("_('LPO')")],
                'lines': [1, 0, 'number', _render("sum([c.number_of_days for c in line.worked_days_line_ids if c.code != 'WORK100']) or 0")],
                'totals': [1, 0, 'text', None]},

            'pay_from':{
                'header': [1, 20, 'text', _render("_('Pay From')")],
#                  'lines': [1, 0, 'text', _render("line.date_from or ''")],
                'lines': [1, 0, 'date', _render("datetime.strptime(line.date_from or '','%Y-%m-%d')")],
                'totals': [1, 0, 'text', None]},

            'pay_till':{
                'header': [1, 20, 'text', _render("_('Pay Till')")],
                'lines': [1, 0, 'date', _render("datetime.strptime(line.date_to or '','%Y-%m-%d')")],
#                 'lines': [1, 0, 'text', _render("line.date_to or ''")],
                'totals': [1, 0, 'text', None]},

        }

#sum([c.amount for c in line.line_ids if c.code == 'ALL']) or 


    def generate_xls_report(self, _p, _xs, data, objects, wb):
        
        wanted_list = _p.wanted_list
        self.col_specs_template.update(_p.template_changes)
        _ = _p._

        report_name = _("WPS FILE")
        ws = wb.add_sheet(report_name[:31])
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0  # Landscape
        ws.fit_width_to_pages = 1
        row_pos = 0

        # set print header/footer
        ws.header_str = self.xls_headers['standard']
        ws.footer_str = self.xls_footers['standard']


        # write empty row to define column sizes
        c_sizes = [17,20,28,15,15,10,15,15]
        c_specs = [('empty%s'%i, 1, c_sizes[i], 'text', None) for i in range(0,len(c_sizes))]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data, set_column_size=True)
        
        # Column Header Row
        cell_format = _xs['bold'] + _xs['fill_blue'] + _xs['borders_all'] + _xs['wrap'] + _xs['top']
        cell_style = xlwt.easyxf(cell_format)
        cell_style_right = xlwt.easyxf(cell_format + _xs['right'])
        cell_style_center = xlwt.easyxf(cell_format + _xs['center'])
        
        c_specs = [('emp_uid',1,0,'text',_("EmpUID")),('routing_code',1,0,'text',_("Bank Routing code")),('bank_ac',1,0,'text',_("Account with Agent")),('net_salary',1,0,'text',_("Fixed Salary")),('variable_salary',1,0,'text',_("Variable Salary")),('lpo',1,0,'text',_("LPO")),('pay_from',1,0,'text',_("Pay From")),('pay_till',1,0,'text',_("Pay Till")),]    
        
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=cell_style)
        ws.set_horz_split_pos(row_pos)
       
        for line in objects:
            c_specs = map(lambda x: self.render(x, self.col_specs_template, 'lines'), wanted_list)
            row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=self.aml_cell_style)

uae_wps_xls('report.uae.wps.xls',
    'hr.payslip',
    parser=uae_wps_xls_parser)

