# -*- coding: utf-8 -*-
from openerp import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'


    customer_peppol_status = fields.Selection([
        ('registered', 'Registered on Peppol'),
        ('not_registered', 'Not registered on Peppol'),
    ], string='Peppol Status', default='registered',
        help='Not registered: a predefined endpoint is sent instead of the TIN '
             '(domestic 9900000098, deemed supply 9900000097, exports 9900000099).')
    # schemeID
    customer_peppol_scheme = fields.Char(string='Scheme ID', default='0235')
    # EndpointID (TIN number)
    customer_peppol_id = fields.Char(string='TIN Number (Peppol ID)',
                                     help='Sent as EndpointID. First 10 digits of the TRN.')
    # PartyLegalEntity.schemeAgencyID
    customer_identification_scheme = fields.Selection([
        ('TL', 'Trade License'),
        ('EID', 'Emirates ID'),
        ('PAS', 'Passport'),
        ('CD', 'Cabinet Decision'),
    ], string='Legal Registration Identifier Type', default='TL',
        help='TL: mainland & free zone companies (issued by DED, IFZA, ADGM etc.)\n'
             'EID: individual / sole trader, issued by ICA\n'
             'PAS: foreign individuals, passport number\n'
             'CD: government entities, Cabinet Decision number')
    customer_identification_number = fields.Char(string='Legal Registration Identifier No.')
