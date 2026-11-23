# -*- coding: utf-8 -*-
"""Build the Fynamics UAE e-invoice JSON payload from an Odoo 8 account.invoice.

Python 2.7 / Odoo 8 compatible. Amounts are strings with 2 decimals.
"""
import datetime
import re
from collections import OrderedDict
from decimal import Decimal, ROUND_HALF_UP

from openerp import fields
from openerp.exceptions import Warning

# res.country.state name -> code sent to Fynamics
EMIRATE_CODES = {
    'abu dhabi': 'AUH',
    'dubai': 'DXB',
    'sharjah': 'SHJ',
    'ajman': 'AJM',
    'umm al quwain': 'UAQ',
    'ras al khaimah': 'RAK',
    'fujairah': 'FUJ',
}
VALID_EMIRATES = ('AUH', 'DXB', 'SHJ', 'AJM', 'UAQ', 'RAK', 'FUJ')
DEFAULT_SCHEME = '0235'
AGENCY_NAMES = {
    'TL': 'Trade License issuing Authority',
    'EID': 'Emirates ID',
    'PAS': 'Passport',
    'CD': 'Cabinet Decision',
}
VALID_TAX_CATEGORIES = ('S', 'Z', 'E', 'O', 'AE')
CREDIT_NOTE_CODES = ('381', '81', '261')
INVOICE_CODES = ('380', '389', '480')
BANK_REQUIRED_MEANS = ('30', '42')   # credit transfer / payment to bank account

# Peppol endpoint (scheme 0235) for buyers that are not registered on Peppol
SENTINEL_DOMESTIC = '9900000098'   # domestic buyer not yet onboarded
SENTINEL_DEEMED = '9900000097'     # deemed supply
SENTINEL_EXPORT = '9900000099'     # exports, buyer has no Peppol ID

def _r2(value):
    """Round to 2 decimals, half up: 406.626 -> 406.63, 406.625 -> 406.63, 406.624 -> 406.62."""
    return float(Decimal('%.6f' % (value or 0.0)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))


def _amt(value):
    return '%.2f' % _r2(value)


def _emirate_code(state_name):
    return EMIRATE_CODES.get((state_name or '').strip().lower(), '')


def _tin10(trn):
    return (trn or '')[:10]


def _percent_str(p):
    return ('%.2f' % p).rstrip('0').rstrip('.') or '0'


def _clean(value):
    return (value or '').strip() if isinstance(value, basestring) else (value or '')


def _check_party(errors, label, d):
    """d: dict of the values of one party; append every problem to errors."""
    optional = set() if d.get('trn_required', True) else set(['legal_id', 'agency_id', 'agency_name', 'tax_code'])
    for key, title in (('scheme', 'Scheme ID'), ('endpoint', 'Endpoint ID (TIN)'),
                       ('name', 'Name'), ('street', 'Street'), ('city', 'City'),
                       ('country', 'Country code'), ('tax_code', 'Party tax code'),
                       ('legal_name', 'Registration name'),
                       ('legal_id', 'Trade License Number or Company ID'),
                       ('agency_id', 'Scheme agency ID'),
                       ('agency_name', 'Scheme agency name')):
        if not d.get(key) and key not in optional:
            errors.append('%s: %s is missing.' % (label, title))
    if d.get('trn_required', True) and not re.match(r'^\d{15}$', d.get('trn') or ''):
        errors.append('%s: TRN must be exactly 15 digits (found "%s").' % (label, d.get('trn') or ''))
    if d.get('endpoint') and not re.match(r'^\d{10}$', d['endpoint']):
        errors.append('%s: Endpoint ID must be 10 digits (found "%s").' % (label, d['endpoint']))
    if d.get('country') == 'AE' and d.get('emirate') not in VALID_EMIRATES:
        errors.append('%s: Emirate/state must be one of %s (found "%s").' %
                      (label, ', '.join(VALID_EMIRATES), d.get('emirate') or ''))


def _party_block(d):
    # AdditionalStreetName and PostalZone are optional: sent only when filled
    address = OrderedDict([('StreetName', d['street'])])
    if d.get('street2'):
        address['AdditionalStreetName'] = d['street2']
    address['CityName'] = d['city']
    if d.get('zip'):
        address['PostalZone'] = d['zip']
    if d.get('emirate'):
        address['CountrySubentity'] = d['emirate']
    address['CountryCode'] = d['country']
    legal = OrderedDict([('RegistrationName', d['legal_name'])])
    if d.get('legal_id'):
        legal['CompanyID'] = d['legal_id']
        legal['schemeAgencyID'] = d['agency_id']
        legal['schemeAgencyName'] = d['agency_name']
    return OrderedDict([
        ('schemeID', d['scheme']),
        ('EndpointID', d['endpoint']),
        ('PartyName', d['name']),
        ('PostalAddress', address),
        ('PartyTaxCompanyID', d['trn']),
        ('PartyTaxCode', d['tax_code']),
        ('PartyLegalEntity', legal),
        ('PartyIdentificationCode', d['scheme']),
        ('PartyIdentificationNumber', d['trn']),
    ])


def _supplier_data(branch):
    trn = _clean(branch.supplier_party_tax_company_id)
    return {
        'scheme': _clean(branch.supplier_scheme_id) or DEFAULT_SCHEME,
        'endpoint': _clean(branch.supplier_endpoint_id),
        'name': _clean(branch.supplier_party_name) or branch.display_name,
        'street': _clean(branch.supplier_street_name),
        'street2': _clean(branch.supplier_street_name2),
        'zip': _clean(branch.supplier_zip_code),
        'city': _clean(branch.supplier_city_name),
        'emirate': branch.supplier_country_subentity,
        'country': _clean(branch.supplier_country_code) or 'AE',
        'trn': trn,
        'tax_code': _clean(branch.supplier_party_tax_code) or 'VAT',
        'legal_name': _clean(branch.supplier_registration_name) or
                      _clean(branch.supplier_party_name),
        'legal_id': _clean(branch.supplier_legal_company_id) or trn,
        'agency_id': _clean(branch.supplier_scheme_agency_id) or 'TL',
        'agency_name': _clean(branch.supplier_scheme_agency_name),
    }


def _customer_data(partner, txn_code):
    trn = _clean(partner.vat)
    country = (partner.country_id and partner.country_id.code) or 'AE'
    scheme = _clean(partner.customer_peppol_scheme) or DEFAULT_SCHEME
    endpoint = _clean(partner.customer_peppol_id) or _tin10(trn)
    trn_required = True
    if partner.customer_peppol_status == 'not_registered':
        # buyer is not on Peppol: send the predefined endpoint instead of the TIN
        scheme = DEFAULT_SCHEME
        txn = txn_code or ''
        if txn[-1:] == '1' or country != 'AE':      # Exports flag, or buyer outside UAE
            endpoint = SENTINEL_EXPORT
            trn = ''                                # export buyers have no TRN
            trn_required = False
        elif txn[1:2] == '1':                       # Deemed Supply flag
            endpoint = SENTINEL_DEEMED
        else:
            endpoint = SENTINEL_DOMESTIC
    agency_id = partner.customer_identification_scheme or 'TL'
    legal_id = _clean(partner.customer_identification_number)
    state = partner.state_id
    if country == 'AE':
        emirate = _emirate_code(state and state.name)
    else:  # buyer outside UAE: the subdivision is still mandatory, use state or city
        emirate = _clean(state and state.name) or _clean(partner.city)
    return {
        'scheme': scheme,
        'endpoint': endpoint,
        'name': _clean(partner.name),
        'street': _clean(partner.street),
        'street2': _clean(partner.street2),
        'zip': _clean(partner.zip),
        'city': _clean(partner.city),
        'emirate': emirate,
        'country': country,
        'trn': trn,
        'trn_required': trn_required,
        'tax_code': 'VAT' if trn else '',
        'legal_name': _clean(partner.name),
        'legal_id': legal_id,
        'agency_id': agency_id,
        'agency_name': AGENCY_NAMES.get(agency_id, agency_id),
    }


def _tax_category(tax, errors, idx, number):
    raw = tax.classified_tax_category
    cat = (getattr(raw, 'code', None) or raw or '')
    cat = cat.strip().upper() if isinstance(cat, basestring) else ''
    if cat not in VALID_TAX_CATEGORIES:
        errors.append('Line %s: tax "%s" has no valid Classified Tax Category (S/Z/E/O/AE).'
                      % (idx, tax.name))
        cat = 'S'
    # Odoo 8 stores percent taxes as a fraction (0.05 == 5%)
    percent = tax.amount * 100.0 if tax.type == 'percent' else 0.0
    if cat in ('Z', 'E', 'O'):
        percent = 0.0
    return cat, percent


def build_invoice_json(invoice):
    """Return a python dict ready for json.dumps(). Raises one Warning that lists
    every missing / badly formatted mandatory value."""
    invoice.ensure_one()
    errors = []

    if invoice.type not in ('out_invoice', 'out_refund'):
        raise Warning('Only customer invoices / credit notes can be sent.')
    if not invoice.invoice_line:
        raise Warning('Invoice %s has no lines.' % (invoice.number or ''))

    # ------------------------------------------------------------ codes
    inv_code = invoice.fynamics_invoice_type_code
    txn_code = invoice.fynamics_transaction_type_code
    pay_code = invoice.fynamics_payment_means_code
    for val, title in ((inv_code, 'Invoice Type'), (txn_code, 'Transaction Type'),
                       (pay_code, 'Payment Method')):
        if not val:
            errors.append('%s is not selected on the invoice.' % title)
    is_refund = invoice.type == 'out_refund'
    if inv_code in CREDIT_NOTE_CODES and not is_refund:
        errors.append('Invoice Type %s is a credit-note code but this is not a credit note.' % inv_code)
    if inv_code in INVOICE_CODES and is_refund:
        errors.append('Invoice Type %s cannot be used on a credit note.' % inv_code)

    original = invoice.od_original_invoice_id
    reason = (invoice.fynamics_credit_note_reason_code or '').strip()
    if inv_code in CREDIT_NOTE_CODES:
        if not reason:
            errors.append('Credit Note Reason Code is required for Invoice Type %s '
                          '(Invoice.DiscrepancyResponse).' % inv_code)
        # the original invoice is optional only for reason VD (volume discount)
        if not original and reason != 'VD':
            errors.append('Original Invoice is required for Invoice Type %s '
                          '(BillingReference.ID).' % inv_code)
    if original and not original.date_invoice:
        errors.append('Original invoice %s has no invoice date (BillingReference.IssueDate).'
                      % original.number)

    # ------------------------------------------------------------ parties
    branch = invoice.od_branch_id
    if not branch:
        raise Warning('Select a Branch on the invoice.')
    supplier = _supplier_data(branch)
    _check_party(errors, 'Supplier (branch %s)' % branch.display_name, supplier)

    partner = invoice.partner_id.commercial_partner_id
    customer = _customer_data(partner, txn_code)
    _check_party(errors, 'Customer (%s)' % partner.name, customer)
    is_export = (txn_code or '')[-1:] == '1'
    if is_export and customer['country'] == 'AE':
        errors.append('Transaction Type Exports needs a customer country outside the UAE.')

    # ------------------------------------------------------------ Check if Bank Account is required later
    bank = invoice.bank1_id
    if pay_code in BANK_REQUIRED_MEANS and not (bank and bank.acc_number):
        errors.append('Bank Account (IBAN) is required on the invoice for Payment Method %s.' % pay_code)

    currency = invoice.currency_id.name
    now_local = fields.Datetime.context_timestamp(invoice, datetime.datetime.now())
    issue_date = invoice.date_invoice or fields.Date.context_today(invoice)

    # ------------------------------------------------------------ lines
    # Step 1: the invoice lines give the VAT categories and the totals (as before)
    subtotals = OrderedDict()
    rate_cats = {}   # tax rate -> the (category, percent) keys used on the invoice
    total_net = 0.0

    for idx, line in enumerate(invoice.invoice_line, 1):
        taxes = line.invoice_line_tax_id
        if len(taxes) > 1:
            errors.append('Line %s has more than one tax; only one VAT category per line is allowed.' % idx)
            continue
        line_net = _r2(line.price_subtotal)
        if taxes:
            cat, percent = _tax_category(taxes[0], errors, idx, invoice.number)
        else:
            cat, percent = 'O', 0.0
        # NOT rounded here: tax is added up unrounded and rounded once per VAT category,
        # the same way the ERP does it (e.g. 3 x 135.542 = 406.626 -> 406.63)
        line_tax = line.price_subtotal * percent / 100.0

        st = subtotals.setdefault((cat, percent), [0.0, 0.0])
        st[0] += line_net
        st[1] += line_tax
        total_net += line_net
        rate_cats.setdefault(round(percent, 4), set()).add((cat, percent))

    # Step 2: the lines that are SENT come from the Government Print lines
    # (gov_alternate_line). Only the total VAT is compared with the invoice.
    lines = []
    gov_tax = 0.0
    gov_lines = invoice.gov_alternate_line
    if not gov_lines:
        errors.append('No Government Print lines on the invoice '
                      '(use "Copy from Invoice Lines" or add them).')

    for idx, gl in enumerate(gov_lines, 1):
        percent = gl.tax_rate or 0.0
        # category: same as the invoice line with this rate; otherwise 5 -> S, 0 -> Z
        cats = set(c for c, p in rate_cats.get(round(percent, 4), []))
        cat = cats.pop() if len(cats) == 1 else ('S' if percent else 'Z')
        if not gl.quantity:
            errors.append('Government line %s has no quantity.' % idx)
            continue
        description = (gl.name2 or '').replace('\n', ' ').strip()
        name = _clean(gl.section2)
        if not description:
            errors.append('Government line %s has no description.' % idx)
        if not name:
            errors.append('Government line %s has no part number.' % idx)

        line_net = gl.total_bf_tax                        # Total After Discount
        line_tax = gl.tax_amount or 0.0
        net_unit = line_net / gl.quantity
        gross_unit = gl.total_bf_discount / gl.quantity   # Total Before Discount
        discount_per_unit = gross_unit - net_unit

        gov_tax += line_tax

        uom_code = 'H87'   # unit code for "piece"; all items are sold in pieces
        lines.append(OrderedDict([
            ('ID', str(idx)),
            ('InvoicedQuantity', ('%.4f' % gl.quantity).rstrip('0').rstrip('.')),
            ('InvoicedUniteCode', uom_code),
            ('LineExtensionAmount', _amt(line_net)),
            ('LineExtensionAmountCurrencyCode', currency),
            ('Charge', []),
            ('Allowance', []),
            ('Item', OrderedDict([
                ('Description', description),
                ('Name', name),
                ('TaxCategoryID', cat),
                ('TaxCategoryPercent', _percent_str(percent)),
                ('TaxCategorySchemeID', 'VAT'),
            ])),
            ('Price', OrderedDict([
                ('PriceAmount', _amt(net_unit)),
                ('PriceAmountCurrencyCode', currency),
                ('BaseQuantity', '1'),
                ('BaseUnitCode', uom_code),
                ('AllowanceChargeIndicator', 'false'),
                ('AllowanceChargeAmountCurrencyCode', currency),
                ('AllowanceChargeAmountValue', _amt(discount_per_unit)),
                ('AllowanceChargeBaseAmountCurrencyCode', currency),
                ('AllowanceChargeBaseAmountValue', _amt(gross_unit)),
            ])),
            ('ItemPriceExtension', OrderedDict([
                ('Amount', _amt(line_net)),
                ('CurrencyCode', currency),
                ('TaxAmount', _amt(line_tax)),
                ('TaxAmountCurrencyCode', currency),
            ])),
        ]))

    # round once per VAT category, then add up
    for key in subtotals:
        subtotals[key] = [_r2(subtotals[key][0]), _r2(subtotals[key][1])]
    total_net = _r2(total_net)
    total_tax = _r2(sum(tax for taxable, tax in subtotals.values()))
    if gov_lines and abs(_r2(gov_tax) - total_tax) > 0.1:
        errors.append('Government Print VAT %.2f differs from invoice VAT %.2f.'
                      % (_r2(gov_tax), total_tax))
    total_gross = _r2(total_net + total_tax)

    # the amounts we send must equal the ERP amounts (rounded to 2 decimals, half up)
    if abs(total_tax - _r2(invoice.amount_tax)) > 0.001:
        errors.append('VAT to send %.2f differs from ERP VAT %s.' % (total_tax, invoice.amount_tax))
    if abs(total_gross - _r2(invoice.amount_total)) > 0.001:
        errors.append('Total to send %.2f differs from ERP total %s.' % (total_gross, invoice.amount_total))

    if errors:
        raise Warning('Cannot send %s to Fynamics:\n- %s' %
                      (invoice.number or '', '\n- '.join(errors)))

    tax_subtotals = []
    for (cat, percent), (taxable, tax) in subtotals.items():
        tax_subtotals.append(OrderedDict([
            ('TaxableAmount', _amt(taxable)),
            ('TaxableAmountCurrencyCode', currency),
            ('TaxAmount', _amt(tax)),
            ('TaxAmountCurrencyCode', currency),
            ('TaxCategoryID', cat),
            ('TaxCategoryPercent', _percent_str(percent)),
            ('TaxCategorySchemeID', 'VAT'),
        ]))

    # ------------------------------------------------------------ document
    payload = OrderedDict()
    payload['Invoice'] = OrderedDict([
        ('InvoiceNumber', invoice.number),
        ('IssueDate', issue_date),
        ('IssueTime', now_local.strftime('%H:%M:%S')),
        ('DueDate', invoice.date_due or issue_date),
        ('InvoiceTypeCode', inv_code),
        ('TransactionType', txn_code),
        ('DocumentCurrencyCode', currency),
    ])
    if inv_code in CREDIT_NOTE_CODES:
        payload['Invoice']['DiscrepancyResponse'] = reason
    if original:
        # the Fynamics request example sends BillingReference as a list
        payload['BillingReference'] = [OrderedDict([
            ('ID', original.number),
            ('IssueDate', original.date_invoice),
        ])]

    # optional: purchase order of the buyer and sales order of the seller
    order_ref = OrderedDict()
    if _clean(invoice.bt_po_ref):
        order_ref['ID'] = _clean(invoice.bt_po_ref)
    if _clean(invoice.origin):
        order_ref['SalesOrderID'] = _clean(invoice.origin)
    if order_ref:
        payload['OrderReference'] = order_ref

    payload['AdditionalDocumentReference'] = []
    payload['AccountingSupplierParty'] = _party_block(supplier)
    payload['AccountingCustomerParty'] = _party_block(customer)
    if is_export:   # deliver-to address is mandatory for exports (ibr-152-ae)
        delivery = OrderedDict([('StreetName', customer['street'])])
        if customer.get('street2'):
            delivery['AdditionalStreetName'] = customer['street2']
        delivery['CityName'] = customer['city']
        if customer.get('zip'):
            delivery['PostalZone'] = customer['zip']
        delivery['CountrySubentity'] = customer['emirate']
        delivery['CountryCode'] = customer['country']
        payload['Delivery'] = delivery


    payment = OrderedDict([('PaymentMeansCode', pay_code)])
    if bank and bank.acc_number:
        payment['PayeeFinancialAccount'] = OrderedDict([
            ('ID', bank.acc_number),
            ('AccountNumber', bank.acc_number),
        ])
    payload['PaymentMeans'] = payment

    payload['TaxTotal'] = OrderedDict([
        ('TaxIncludedIndicator', 'false'),
        ('TaxAmount', _amt(total_tax)),
        ('TaxAmountCurrencyCode', currency),
        ('DocumentTaxSubtotal', tax_subtotals),
    ])
    payload['LegalMonetaryTotal'] = OrderedDict([
        ('LineExtensionAmount', _amt(total_net)),
        ('LineExtensionAmountCurrencyCode', currency),
        ('TaxExclusiveAmount', _amt(total_net)),
        ('TaxExclusiveAmountCurrencyCode', currency),
        ('TaxInclusiveAmount', _amt(total_gross)),
        ('TaxInclusiveAmountCurrencyCode', currency),
        ('PayableAmount', _amt(total_gross)),
        ('PayableAmountCurrencyCode', currency),
    ])
    payload['TotalCharge'] = []
    payload['TotalAllowance'] = []
    payload['InvoiceLine'] = lines
    return payload