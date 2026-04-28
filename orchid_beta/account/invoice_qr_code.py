# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
import qrcode
import base64
import re
from io import BytesIO
import binascii


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    
    qr_code = fields.Binary("QR Code", attachment=True, compute='_compute_qrcode', copy=False)
    display_contract_no = fields.Boolean("Display Contract #")
    contract_no = fields.Char(string="Contract #")
    service_wo = fields.Char(string="Service W.O")
    
    def invoice_validate(self, cr, uid, ids, context=None):
        res = super(AccountInvoice, self).invoice_validate(cr, uid, ids, context=context)
        inv_rec = self.pool.get('account.invoice').browse(cr, uid, ids, context=context)
        if inv_rec.company_id.id == 6 and inv_rec.type in ('out_invoice','out_refund') and not inv_rec.zatca_onboarding_status:
            template_id = 'report.report_ksa_e_invoice1'
            if inv_rec.type == 'out_refund':
                template_id = 'report.report_ksa_e_invoice_credit_note'
            result = self.pool['report'].get_pdf(cr, uid, [ids[0]], template_id, context=context)
            out = base64.b64encode(result)
            file_name = inv_rec.name_get()[0][1]
            file_name = re.sub(r'[^a-zA-Z0-9_-]', '_', file_name)
            file_name += ".pdf"
            self.pool.get('ir.attachment').create(cr, uid,
                                              {
                                               'name': file_name,
                                               'datas': out,
                                               'datas_fname': file_name,
                                               'res_model': self._name,
                                               'res_id': inv_rec.id,
                                               'type': 'binary'
                                              },
                                              context=context)
        return res
    
    def _string_to_hex(self, value):
        if value:
            string = str(value)
            string_bytes = string.encode("UTF-8")
            encoded_hex_value = binascii.hexlify(string_bytes)
            hex_value = encoded_hex_value.decode("UTF-8")
            # print("This : "+value +"is Hex: "+ hex_value)
            return hex_value
    
    def _get_hex(self, tag, length, value):
        if tag and length and value:
            # str(hex(length))
            hex_string = self._string_to_hex(value)
            length = int(len(hex_string)/2)
            # print("LEN", length, " ", "LEN Hex", hex(length))
            conversion_table = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']
            hexadecimal = ''
            while (length > 0):
                remainder = length % 16
                hexadecimal = conversion_table[remainder] + hexadecimal
                length = length // 16
            # print(hexadecimal)
            if len(hexadecimal) == 1:
                hexadecimal = "0" + hexadecimal
            return tag + hexadecimal + hex_string
    
    def get_qr_code_data(self):
        for record in self:
            seller_vat_no = record.company_id.vat or 'NIL'
            #sellername = str(record.company_id.name)
            sellername = "Dar Beta Information Technology Co."
            seller_hex = self._get_hex("01", "0c", sellername)
            vat_hex = self._get_hex("02", "0f", seller_vat_no)
            time_stamp = str(record.date_invoice) + "T00:00:00Z"
            # print(self.create_date)
            date_hex = self._get_hex("03", "14", time_stamp)
            total_with_vat_hex = self._get_hex("04", "0a", str(round(record.amount_total, 2)))
            total_vat_hex = self._get_hex("05", "09", str(round(record.amount_tax, 2)))
            qr_hex = seller_hex + vat_hex + date_hex + total_with_vat_hex + total_vat_hex
            encoded_base64_bytes = base64.b64encode(bytearray.fromhex(qr_hex)).decode()
            return encoded_base64_bytes
    
    @api.depends('partner_id', 'state')
    def _compute_qrcode(self):
        for record in self:
            if record.partner_id and record.company_id and record.date_invoice:
                #partner_vat = record.partner_id.vat or 'NIL'
                #inv_number = record.number or 'Draft Invoice'
#                 data = 'QR Code Details:' +'\n\nSupplier Name: ' + record.company_id.name + '\nVat Number:  ' + record.company_id.vat + '\nCustomer Name:  '+ record.partner_id.name+ \
#                          '\nCustomer VAT:  '+ partner_vat + '\nInvoice Number:  '+ inv_number +'\nInvoice Date:  '+ record.date_invoice   + '\nCreate Datetime:  ' +  \
#                          record.create_date + '\nTotal Vat:  '+record.company_id.currency_id.name+ ' ' + '{:,.2f}'.format(record.amount_tax) + '\nTotal Amount Due:  '+ record.company_id.currency_id.name+ ' '+ '{:,.2f}'.format(record.amount_total)
                data = self.get_qr_code_data()
                record.qr_code = record.generate_qr_code(data) if data else None
                
            
    def generate_qr_code(self, data):
        """this function will generate and return qrcode with provided data """
        if data:
            qr = qrcode.QRCode(
                version=10,  # value increases(1 to 40), the number of cells (square black and white dots) increases,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)
            img = qr.make_image()
            temp = BytesIO()
            img.save(temp, "PNG")
            qr_image = base64.b64encode(temp.getvalue())
            return qr_image
        else:
            return None

    
