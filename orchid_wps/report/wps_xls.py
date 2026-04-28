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

_ir_translation_name = 'payroll.cards.xls'

class wps_xls_parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(wps_xls_parser, self).__init__(cr, uid, name, context=context)
        hr_payslip_obj = self.pool.get('hr.payslip')
        self.context = context
        wanted_list = hr_payslip_obj._report_xls_fields(cr, uid, context)
        template_changes = hr_payslip_obj._report_xls_template(cr, uid, context)
        self.localcontext.update({
            'datetime': datetime,
            'wanted_list': wanted_list,
            'template_changes': template_changes,
            '_': self._,
        })

    def _(self, src):
        lang = self.context.get('lang', 'en_US')
        return translate(self.cr, _ir_translation_name, 'report', lang, src) or src

class wps_xls(report_xls):

    def __init__(self, name, table, rml=False, parser=False, header=True, store=False):
        super(wps_xls, self).__init__(name, table, rml, parser, header, store)



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

            'code': {
                'header': [1, 20, 'text', _render("_('Code')")],
                'lines': [1, 0, 'text', _render("_('EDR')")],
                'totals': [1, 0, 'text', None]},

            'otherid': {
                'header': [1, 13, 'text', _render("_('Other ID')")],
                'lines': [1, 0, 'text', _render("line.employee_id.otherid or ''")],
                'totals': [1, 0, 'text', None]},


            'routing_code':{
                'header': [1, 20, 'text', _render("_('Routing Code')")],
                'lines': [1, 0, 'text', _render("line.contract_id.xo_routing_code or ''")],
                'totals': [1, 0, 'text', None]},

            'bank':{
                'header': [1, 20, 'text', _render("_('Bank')")],
                'lines': [1, 0, 'text', _render("line.employee_id.bank_account_id.acc_number or ''")],
                'totals': [1, 0, 'text', None]},

            'date_from':{
                'header': [1, 20, 'text', _render("_('From Date')")],
                'lines': [1, 0, 'text', _render("line.date_from or ''")],
                'totals': [1, 0, 'text', None]},

            'date_to':{
                'header': [1, 20, 'text', _render("_('To Date')")],
                'lines': [1, 0, 'text', _render("line.date_to or ''")],
                'totals': [1, 0, 'text', None]},

            'worked_days':{
                'header': [1, 20, 'text', _render("_('Worked Days')")],
                'lines': [1, 0, 'number', _render("line.xo_total_no_of_days or 0")],
                'totals': [1, 0, 'text', None]},

            'net_salary':{
                'header': [1, 20, 'text', _render("_('Net Salary')")],
                'lines': [1, 0, 'number', _render("sum([c.amount for c in line.line_ids if c.code == 'NET']) or 0.0")],
                'totals': [1, 0, 'text', None]},

            'variable_salary':{
                'header': [1, 20, 'text', _render("_('Variable Salary')")],
                'lines': [1, 0, 'number', _render("0.0")],
                'totals': [1, 0, 'text', None]},

            'days_on_leave':{
                'header': [1, 20, 'text', _render("_('Days On Leave')")],
                'lines': [1, 0, 'number', _render("sum([c.number_of_days for c in line.worked_days_line_ids if c.code != 'WORK100']) or 0")],
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

        c_specs = [
            ('report_name', 6, 1, 'text', report_name),
        ]
       
        total_net_salary=0.0
        payment_mtd=[]
        for line in objects:
            total_net_salary += sum([c.amount for c in line.line_ids if c.code == 'NET'])
            payment_mtd.append(line.xo_mode_of_payment_id)

            c_specs = map(lambda x: self.render(x, self.col_specs_template, 'lines'), wanted_list)
            row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=self.aml_cell_style)

        if len(payment_mtd) > 0 and (len(set(payment_mtd)) == 1):
            payment_mtd = payment_mtd[0]
            employer_uniq_id = str(payment_mtd.routing_codes or '')
            establishment = str(payment_mtd.establishment or '')
            current_date = str(datetime.now().strftime("%Y-%m-%d"))
            current_time = str(datetime.now().strftime("%H%M"))

            salary_month = str(datetime.now().strftime("%m%Y"))

            for l in objects:
                period_date = l.xo_period_id and l.xo_period_id.date_start
                d1 = datetime.strptime(period_date, DEFAULT_SERVER_DATE_FORMAT)
                salary_month = d1.strftime("%m%Y")

            last_row = _("SCR")
            total_empolyes= len(objects)
            c_specs = [('code',1,0,'text',last_row),('otherid',1,0,'text',employer_uniq_id),('routing_code',1,0,'text',establishment),('bank',1,0,'text',current_date),('date_from',1,0,'text',current_time),('date_to',1,0,'text',salary_month),('worked_days',1,0,'number',total_empolyes),('net_salary',1,0,'number',total_net_salary),('variable_salary',1,0,'text',_("AED"))]
            row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=self.aml_cell_style)

wps_xls('report.wps.xls',
    'hr.payslip',
    parser=wps_xls_parser)

