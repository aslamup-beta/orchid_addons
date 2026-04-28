# -*- coding: utf-8 -*-

from openerp import api, models, fields
import random
import hashlib
import qrcode
import base64
from io import BytesIO

class Users(models.Model):
    _inherit = 'res.users'
    
    is_2fa_enable = fields.Boolean(string="2FA Status", default=False, copy=False)
    secret_key = fields.Char(string="Secret Key", readonly=True, copy=False)
    qr_code = fields.Binary(String="QR Code", copy=False)
    file_name = fields.Char(string="File Name", copy=False)
    
    #TODO: create secret key while creating user if 2fa enabled
    @api.multi
    def _generate_secret_key(self):
        """Generate 16 digit secret key for 2FA"""
        valid_letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        secret_key = ''.join((random.choice(valid_letters) for i in xrange(16)))
        find_key = self.env['res.users'].search([('secret_key', '=', secret_key)])
        if find_key:
            self._generate_secret_key()
        secret_key = ' '.join(secret_key[i:i+4] for i in xrange(0,len(secret_key),4))
        return secret_key
    
    @api.multi
    def _generate_qr_code(self, key):
        #generate qr code
        qr = qrcode.QRCode(version=1,error_correction=qrcode.constants.ERROR_CORRECT_H,box_size=10,border=4,)
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        
        
#         new_key = "otpauth://totp/" + str(base_url) + "- ODOO " + "?secret=" + key.replace(" ", "")
        email = self.email or self.login or 'user@betait.net'
        new_key = "otpauth://totp/" + "betait.net:" + email + "?secret=" + key.replace(" ", "")
        qr.add_data(new_key) #you can put here any attribute
 
        qr.make(fit=True)
        img = qr.make_image()
        buffer = BytesIO()
        img.save(buffer)
        encode_img = base64.b64encode(buffer.getvalue())
        return encode_img
        
    
    @api.model
    def create(self, vals):
        res = super(Users, self).create(vals)
        if vals.get('is_2fa_enable') == True:
            key = self._generate_secret_key()
            encode_img = self._generate_qr_code(key)
            res.secret_key = key
            res.qr_code = encode_img
            res.file_name = "QR Code"
        return res
    
    @api.multi
    def write(self, vals):
        if vals.get('is_2fa_enable') == False:
            vals.update({'secret_key': '', 'qr_code': False, 'file_name': ''})
        if vals.get('is_2fa_enable') == True:
            key = self._generate_secret_key()
            encode_img = self._generate_qr_code(key)
            vals.update({'secret_key': key, 'qr_code': encode_img, 'file_name': "QR Code"})
        return super(Users, self).write(vals)
        
    
    @api.multi
    def send_two_factor_auth_mail(self):
        if self.is_2fa_enable:
            try:
                mail_id = self.env.ref('two_factor_authentication_v8.two_factor_auth_template').send_mail(self.id, force_send=True)
                #mail_id.send()
            except:
                pass
