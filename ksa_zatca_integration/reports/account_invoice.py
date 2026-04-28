from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from openerp import api, fields, models, exceptions
from datetime import timedelta
import lxml.etree as ET
import base64
import qrcode
import datetime


class AccountMoveReport(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def _default_currency_id(self):
        for record in self:
            currency = self.env['res.currency'].sudo().search([('name', '=', 'SAR')])[0]
            record.invoice_multi_currency_id = currency.id or None

    invoice_multi_currency_id = fields.Many2one('res.currency', string='Invoice Report Currency',
                                                compute="_default_currency_id")

    @api.multi
    def _get_zatca_report_base_filename(self):
        self.ensure_one()
        date_invoicetime = datetime.datetime.strptime(self.date_invoicetime, DEFAULT_SERVER_DATETIME_FORMAT)
        return "%s - %s - %s" % (self.company_id.vat,
                                 "{:%Y-%m-%d %H_%M_%S}".format(date_invoicetime + timedelta(hours=3)),
                                 self.id)

    @api.multi
    def get_tax_amount(self):
        data = 0.0
        if self.invoice_line:
            for rec in self.invoice_line:
                taxable_amount = rec.price_unit * rec.quantity
                data += ((rec.tax_ids[0].amount if rec.tax_ids else 0.0) * taxable_amount) / 100
        return data

    @api.multi
    def print_einv_standard(self):
        if not self.zatca_invoice:
            raise exceptions.MissingError("Xml not created yet.")
        # return self.env.ref('ksa_zatca_integration.report_sales_order').report_action(self)
        return self.env['report'].get_action(self, 'ksa_zatca_integration.report_sales_order')

    @api.multi
    def print_einv_b2c(self):
        if not self.zatca_invoice:
            raise exceptions.MissingError("Xml not created yet.")
        return self.env['report'].get_action(self, 'ksa_zatca_integration.report_e_invoicing_b2c')
        # return self.env.ref('ksa_zatca_integration.report_e_invoicing_b2c').report_action(self)

    @api.multi
    def get_invoice_type_code(self):
        invoice = base64.b64decode(self.zatca_invoice).decode()
        xml_file = ET.fromstring(invoice).getroottree()
        ksa_2 = xml_file.find("//{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}InvoiceTypeCode").attrib.get('name', '')
        return ksa_2

    @api.multi
    def get_bt_131(self, id):
        invoice = base64.b64decode(self.zatca_invoice).decode()
        xml_file = ET.fromstring(invoice).getroottree()
        # LineExtensionAmount
        bt_131_find = "//{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ID[.='" + str(id) + "']"
        bt_126 = xml_file.find(bt_131_find).getparent()
        bt_131 = bt_126.find('{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}LineExtensionAmount')
        return bt_131.text

    @api.multi
    def get_bt_136(self, id):
        invoice = base64.b64decode(self.zatca_invoice).decode()
        xml_file = ET.fromstring(invoice).getroottree()
        # LineExtensionAmount
        bt_136_find = "//{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ID[.='" + str(id) + "']"
        bt_126 = xml_file.find(bt_136_find).getparent()
        bg_27 = bt_126.find('{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}AllowanceCharge')
        if bg_27 is None:
            return "0.0"
        bt_136 = bg_27.find('{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}Amount')
        return bt_136.text

    @api.multi
    def get_ksa_11(self, id):
        invoice = base64.b64decode(self.zatca_invoice).decode()
        xml_file = ET.fromstring(invoice).getroottree()
        # LineExtensionAmount
        ksa_11_find = "//{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ID[.='" + str(id) + "']"
        bt_126 = xml_file.find(ksa_11_find).getparent()
        tax_total = bt_126.find('{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}TaxTotal')
        if tax_total is None:
            return "0.0"
        ksa_11 = tax_total.find('{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}TaxAmount')
        return ksa_11.text

    @api.multi
    def get_ksa_12(self, id):
        invoice = base64.b64decode(self.zatca_invoice).decode()
        xml_file = ET.fromstring(invoice).getroottree()
        # LineExtensionAmount
        ksa_12_find = "//{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ID[.='" + str(id) + "']"
        bt_126 = xml_file.find(ksa_12_find).getparent()
        tax_total = bt_126.find('{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}TaxTotal')
        if tax_total is None:
            return "0.0"
        ksa_12 = tax_total.find('{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}RoundingAmount')
        return ksa_12.text

    @api.multi
    def get_bt_120(self):
        invoice = base64.b64decode(self.zatca_invoice).decode()
        xml_file = ET.fromstring(invoice).getroottree()
        tax_total = xml_file.find('./{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}TaxTotal')
        if tax_total is None:
            return "0.0"
        bt_120 = tax_total.findall('.//{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}TaxExemptionReason')
        if not len(bt_120):
            return ""
        bt_120_text = ''
        for x in bt_120:
            bt_120_text += x.text + ", "
        return bt_120_text[:-2]

    @api.multi
    def get_qrcode(self):
        # qr = qrcode.QRCode(version=1,
        #                    box_size=10,
        #                    border=5)
        #
        # # Adding data to the instance 'qr'
        # qr.add_data(self.l10n_sa_qr_code_str)
        #
        # qr.make(fit=True)
        # img = qr.make_image(fill_color='red',
        #                     back_color='white')
        # x = img

        qr = qrcode.make(self.l10n_sa_qr_code_str)
        from PIL import Image
        import io

        def image_to_byte_array(image):
            # BytesIO is a fake file stored in memory
            buffered = io.BytesIO()
            # image.save expects a file as a argument, passing a bytes io ins
            image.save(buffered)
            # Turn the BytesIO object back into a bytes object
            imgByteArr = buffered.getvalue()
            img_str = base64.b64encode(buffered.getvalue())
            return img_str

        return "data:image/png;base64," + image_to_byte_array(qr).decode()
