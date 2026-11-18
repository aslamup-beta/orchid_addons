# -*- coding: utf-8 -*-
{
    'name': 'ZATCA PDF/A-3 Invoice Print',
    'version': '1.0',
    'category': 'Accounting',
    'summary': 'One-click PDF/A-3 invoice with the ZATCA cleared XML embedded',
    'description': """
ZATCA PDF/A-3 Invoice Printing
============================
Adds a "Print PDF/A-3 (ZATCA)" button on the customer invoice form.

The button:
 1. renders the KSA e-invoice report (with QR code) to PDF,
 2. converts it to PDF/A-3,
 3. embeds the ZATCA cleared XML (field zatca_hash_cleared_invoice),
 4. downloads the final PDF and stores a copy as an attachment on the invoice.

Server requirements: Ghostscript (gs) and qpdf. No Python 3 needed. See README.
""",
    'depends': ['account'],
    'data': [
        'views/account_invoice_view.xml',
    ],
    'installable': True,
    'application': False,
}
