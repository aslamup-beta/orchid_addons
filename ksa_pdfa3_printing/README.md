# ZATCA PDF/A-3 Invoice Button (Odoo 8)

Adds **Print PDF/A-3 (ZATCA)** to the customer invoice form (visible in states Open / Paid).

## Server requirements
- Ghostscript: `gs` in PATH (`apt-get install ghostscript`)
- qpdf in PATH (`apt-get install qpdf`)
- Nothing else: the XML embedding is done in pure Python 2 inside the module.

## Install
1. Copy the `zatca_pdfa3_button` folder into your Odoo addons path.
2. Restart Odoo, then Settings > Local Modules > Update Modules List.
3. Install "ZATCA PDF/A-3 Invoice Button".

## Configuration (optional)
Settings > Technical > Parameters > System Parameters:

| Key | Default | Meaning |
|---|---|---|
| `zatca_pdfa3.report_name` | `report.report_ksa_e_invoice_government` | QWeb template used for the printout |
| `zatca_pdfa3.gs` | `gs` | Ghostscript executable |
| `zatca_pdfa3.qpdf` | `qpdf` | qpdf executable |

## Notes
- The XML is read from the field `zatca_hash_cleared_invoice` (plain XML or base64 XML are both accepted).
- The result is also saved as an attachment `<invoice number>_pdfa3.pdf` on the invoice.
- If your ZATCA module puts the report under a module prefix (for example `my_module.report_ksa_e_invoice_government`), set `zatca_pdfa3.report_name` accordingly.
- Flow: report PDF -> `gs` (PDF/A-3) -> `qpdf --object-streams=disable` -> XML appended as an associated file (/AF, AFRelationship=Alternative).
- If the embedding cannot be done (unusual PDF structure), it falls back to `qpdf --add-attachment` and logs a warning.
