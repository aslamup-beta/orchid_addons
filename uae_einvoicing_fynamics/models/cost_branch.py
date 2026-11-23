# -*- coding: utf-8 -*-
from openerp import models, fields, api

SANDBOX_URL = 'https://sandbox-uae.fynamicstax.com/api/partner'


class od_cost_branch(models.Model):
    _inherit = "od.cost.branch"

    # ------------------------------------------------ Fynamics API configuration
    fynamics_enabled = fields.Boolean(string='UAE E-Invoicing Enabled')
    fynamics_environment = fields.Selection([
        ('sandbox', 'Sandbox'),
        ('production', 'Production'),
    ], string='Environment', default='sandbox')
    fynamics_base_url = fields.Char(string='Base URL', default=SANDBOX_URL)
    fynamics_client_id = fields.Char(string='Client ID')
    fynamics_client_secret = fields.Char(string='Client Secret')
    fynamics_scope = fields.Char(string='Scope')
    fynamics_timeout = fields.Integer(string='HTTP Timeout (seconds)', default=60)

    fynamics_token_path = fields.Char(string='Token Endpoint', default='/auth/authenticate')
    fynamics_submit_path = fields.Char(string='Submit Endpoint', default='/sales-invoice/invoice')
    fynamics_status_path = fields.Char(string='Status Endpoint',
                                       default='/sales-invoice/get-document-status/{uuid}',
                                       help='{uuid} is replaced by the document UUID.')

    fynamics_access_token = fields.Text(string='Access Token', readonly=True)
    fynamics_token_expires_at = fields.Datetime(string='Token Expiry', readonly=True)
    fynamics_last_auth_message = fields.Text(string='Last Authentication Message', readonly=True)

    # ---- AccountingSupplierParty
    supplier_scheme_id = fields.Char(string='Scheme ID', default='0235',
                                     help='AccountingSupplierParty.schemeID')
    supplier_endpoint_id = fields.Char(string='Peppol ID',
                                       help='AccountingSupplierParty.EndpointID (Peppol endpoint, '
                                            'first 10 digits of the TRN)')
    supplier_party_name = fields.Char(string='Party Name',
                                      help='AccountingSupplierParty.PartyName')

    # ---- PostalAddress
    supplier_street_name = fields.Char(string='Street Name')
    supplier_street_name2 = fields.Char(string='Additional Street Name')
    supplier_city_name = fields.Char(string='City')
    supplier_zip_code = fields.Char(string='Zip Code')
    supplier_country_subentity = fields.Selection([
        ('AUH', 'Abu Dhabi'),
        ('DXB', 'Dubai'),
        ('SHJ', 'Sharjah'),
        ('AJM', 'Ajman'),
        ('UAQ', 'Umm Al Quwain'),
        ('RAK', 'Ras Al Khaimah'),
        ('FUJ', 'Fujairah'),
    ], string='Country Subentity (Emirate)')
    supplier_country_code = fields.Char(string='Country Code', default='AE', size=2)

    # ---- Tax
    supplier_party_tax_company_id = fields.Char(string='TRN', size=15,
                                                help='15 digit UAE Tax Registration Number')
    supplier_party_tax_code = fields.Char(string='Party Tax Code', default='VAT')

    # ---- PartyLegalEntity
    supplier_registration_name = fields.Char(string='Registration Name')
    supplier_legal_company_id = fields.Char(string='Trade License/Company ID')
    supplier_scheme_agency_id = fields.Char(string='Scheme Agency ID', default='TL')
    supplier_scheme_agency_name = fields.Char(string='Scheme Agency Name',
                                              default='Trade License issuing Authority')

    @api.onchange('fynamics_environment')
    def onchange_fynamics_environment(self):
        self.fynamics_base_url = SANDBOX_URL if self.fynamics_environment == 'sandbox' else ''

    @api.multi
    def action_fynamics_test_authentication(self):
        self.ensure_one()
        from ..services.fynamics_api import FynamicsAPI
        FynamicsAPI(self).authenticate(force=True)
        self.write({'fynamics_last_auth_message': 'Authentication successful'})
        return True