# -*- coding: utf-8 -*-
import base64
import logging
import os
import re
import shutil
import subprocess
import tempfile

from openerp import api, models
from openerp.exceptions import Warning as UserError
from openerp.tools.translate import _

from .pdfa3_embed import EmbedError, embed_xml

_logger = logging.getLogger(__name__)

# Field on account.invoice that holds the XML cleared by ZATCA
XML_FIELD = 'zatca_hash_cleared_invoice'

# QWeb report (template) used for the printed invoice with the QR code.
# Can be overridden in Settings > Technical > Parameters > System Parameters
# with the key  zatca_pdfa3.report_name
DEFAULT_REPORT_NAME = 'report.report_ksa_e_invoice_government'


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------
    @api.multi
    def _zatca_get_xml_bytes(self):
        """Return the cleared XML as raw bytes.

        The field can be a Many2one to ir.attachment (the XML file), or a
        Text/Binary field. The content may be the XML itself or its base64
        encoding (ZATCA returns the cleared invoice base64 encoded); all of
        these are handled.
        """
        self.ensure_one()
        if XML_FIELD not in self._fields:
            raise UserError(_('Field %s does not exist on invoices. '
                              'Is the ZATCA module installed?') % XML_FIELD)
        value = self[XML_FIELD]
        if not value:
            raise UserError(_('This invoice has no ZATCA cleared XML yet '
                              '(%s is empty). Clear/report it first.') % XML_FIELD)

        if getattr(value, '_name', None) == 'ir.attachment':
            # attachment.datas is base64 of the file content
            if not value.datas:
                raise UserError(_('The attachment in %s has no file content.')
                                % XML_FIELD)
            value = base64.b64decode(value.datas)
        elif isinstance(value, type(u'')):
            value = value.encode('utf-8')

        def is_xml(data):
            data = data.lstrip()
            if data.startswith(b'\xef\xbb\xbf'):
                data = data[3:].lstrip()
            return data.startswith(b'<')

        if is_xml(value):
            return value
        try:
            decoded = base64.b64decode(value)
        except Exception:
            decoded = b''
        if is_xml(decoded):
            return decoded
        raise UserError(_('The content of %s is neither XML nor base64 XML.')
                        % XML_FIELD)

    @api.model
    def _zatca_param(self, key, default):
        return self.env['ir.config_parameter'].get_param(
            'zatca_pdfa3.' + key, default) or default

    @api.model
    def _zatca_run(self, cmd):
        _logger.info('ZATCA PDF/A-3: running %s', ' '.join(cmd))
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        out, err = proc.communicate()
        if proc.returncode != 0:
            raise UserError(_('Command failed (%s):\n%s') % (cmd[0], err or out))
        return out

    @api.multi
    def _zatca_embed_xml(self, pdfa_path, xml_path, out_path, filename):
        """Normalise the PDF with qpdf (classic xref, no object streams), then
        embed the XML as a PDF/A-3 associated file in pure Python.
        Fallback: plain `qpdf --add-attachment` (no /AF entry, so the result
        may fail strict PDF/A-3 validation)."""
        qpdf = self._zatca_param('qpdf', 'qpdf')
        flat = os.path.join(os.path.dirname(out_path), 'flat.pdf')
        self._zatca_run([qpdf, '--object-streams=disable', pdfa_path, flat])
        try:
            with open(flat, 'rb') as f:
                pdf = f.read()
            with open(xml_path, 'rb') as f:
                xml = f.read()
            result = embed_xml(pdf, xml, filename)
            with open(out_path, 'wb') as f:
                f.write(result)
            return
        except EmbedError as e:
            _logger.warning('PDF/A-3 embedding failed (%s); '
                            'falling back to qpdf --add-attachment', e)
        self._zatca_run([
            qpdf, pdfa_path, out_path,
            '--add-attachment', xml_path,
            '--key=%s' % filename, '--mimetype=text/xml', '--'])

    # ------------------------------------------------------------------
    # button
    # ------------------------------------------------------------------
    @api.multi
    def action_print_zatca_pdfa3(self):
        self.ensure_one()
        xml_bytes = self._zatca_get_xml_bytes()

        # 1) the normal invoice PDF (with QR code)
        report_name = self._zatca_param('report_name', DEFAULT_REPORT_NAME)
        pdf_bytes = self.env['report'].get_pdf(self, report_name)

        safe = re.sub(r'[^A-Za-z0-9_.-]+', '-', self.number or 'invoice-%s' % self.id)
        tmp = tempfile.mkdtemp(prefix='zatca_pdfa3_')
        try:
            src = os.path.join(tmp, 'src.pdf')
            xml = os.path.join(tmp, '%s.xml' % safe)
            pdfa = os.path.join(tmp, 'pdfa.pdf')
            final = os.path.join(tmp, '%s_pdfa3.pdf' % safe)
            with open(src, 'wb') as f:
                f.write(pdf_bytes)
            with open(xml, 'wb') as f:
                f.write(xml_bytes)

            # 2) PDF -> PDF/A-3 (Ghostscript)
            self._zatca_run([
                self._zatca_param('gs', 'gs'),
                '-dPDFA=3', '-dPDFACompatibilityPolicy=1',
                '-sColorConversionStrategy=RGB',
                '-dBATCH', '-dNOPAUSE', '-dQUIET', '-sDEVICE=pdfwrite',
                '-sOutputFile=%s' % pdfa, src])

            # 3) embed the cleared XML
            self._zatca_embed_xml(pdfa, xml, final, os.path.basename(xml))

            with open(final, 'rb') as f:
                result = f.read()
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

        # 4) keep a copy on the invoice and download it
        att_name = '%s_pdfa3.pdf' % safe
        Attachment = self.env['ir.attachment']
        att = Attachment.search([('res_model', '=', 'account.invoice'),
                                 ('res_id', '=', self.id),
                                 ('name', '=', att_name)], limit=1)
        # explicit type: the invoice form context carries default_type=
        # 'out_invoice', which is not a valid ir.attachment type
        vals = {'datas': base64.b64encode(result), 'datas_fname': att_name,
                'type': 'binary'}
        if att:
            att.write(vals)
        else:
            vals.update({'name': att_name, 'res_model': 'account.invoice',
                         'res_id': self.id})
            att = Attachment.create(vals)

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/binary/saveas?model=ir.attachment&field=datas'
                   '&filename_field=datas_fname&id=%d' % att.id,
            'target': 'self',
        }