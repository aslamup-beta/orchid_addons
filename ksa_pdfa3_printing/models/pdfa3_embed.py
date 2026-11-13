# -*- coding: utf-8 -*-

import re
import time


class EmbedError(Exception):
    pass


def _to_bytes(value):
    if isinstance(value, bytes):
        return value
    return value.encode('ascii')


def embed_xml(pdf, xml, filename, description='ZATCA e-invoice XML',
              relationship='Alternative'):
    """Return the bytes of `pdf` with `xml` embedded.

    pdf, xml: bytes. filename / description: ASCII, no parentheses or backslash.
    """
    filename = _to_bytes(filename)
    description = _to_bytes(description)
    relationship = _to_bytes(relationship)
    if re.search(br'[()\\]', filename + description):
        raise EmbedError('filename/description must not contain ( ) or \\')

    # --- locate the last xref / trailer --------------------------------
    eofs = list(re.finditer(br'startxref\s+(\d+)\s+%%EOF', pdf))
    if not eofs:
        raise EmbedError('startxref not found')
    last = eofs[-1]
    prev = int(last.group(1))
    if pdf[prev:prev + 4] != b'xref':
        raise EmbedError('PDF uses xref streams; normalise it with '
                         'qpdf --object-streams=disable first')
    t_start = pdf.rfind(b'trailer', 0, last.start())
    if t_start < 0:
        raise EmbedError('trailer not found')
    trailer = pdf[t_start:last.start()]

    size_m = re.search(br'/Size\s+(\d+)', trailer)
    root_m = re.search(br'/Root\s+(\d+)\s+0\s+R', trailer)
    if not size_m or not root_m:
        raise EmbedError('/Size or /Root missing in trailer')
    size = int(size_m.group(1))
    root = int(root_m.group(1))

    # --- read the catalog (latest version of the root object) ------------
    cat_matches = list(re.finditer(br'(?:^|[\r\n])%d\s+0\s+obj\b' % root, pdf))
    if not cat_matches:
        raise EmbedError('catalog object not found')
    body_start = cat_matches[-1].end()
    body_end = pdf.find(b'endobj', body_start)
    body = pdf[body_start:body_end].strip()
    if not (body.startswith(b'<<') and body.endswith(b'>>')):
        raise EmbedError('catalog is not a plain dictionary')
    if re.search(br'/AF\b', body) or re.search(br'/Names\b', body):
        raise EmbedError('catalog already has /AF or /Names (not supported)')

    n_stream = size
    n_spec = size + 1

    new_catalog = (
            b'%d 0 obj\n' % root
            + body[:-2].rstrip()
            + b'\n/AF [%d 0 R]\n' % n_spec
            + b'/Names << /EmbeddedFiles << /Names [(%s) %d 0 R] >> >>\n>>\nendobj\n'
            % (filename, n_spec))

    moddate = _to_bytes(time.strftime('D:%Y%m%d%H%M%S', time.gmtime())) + b'Z'
    stream_obj = (
            b'%d 0 obj\n<< /Type /EmbeddedFile /Subtype /text#2Fxml /Length %d '
            b'/Params << /Size %d /ModDate (%s) >> >>\nstream\n'
            % (n_stream, len(xml), len(xml), moddate)
            + xml + b'\nendstream\nendobj\n')

    spec_obj = (
            b'%d 0 obj\n<< /Type /Filespec /F (%s) /UF (%s) /Desc (%s) '
            b'/AFRelationship /%s /EF << /F %d 0 R /UF %d 0 R >> >>\nendobj\n'
            % (n_spec, filename, filename, description, relationship,
               n_stream, n_stream))

    # --- append the update ------------------------------------------------
    out = pdf if pdf.endswith(b'\n') else pdf + b'\n'
    off_cat = len(out)
    out += new_catalog
    off_stream = len(out)
    out += stream_obj
    off_spec = len(out)
    out += spec_obj
    xref_off = len(out)

    def entry(offset):
        return b'%010d 00000 n \n' % offset  # exactly 20 bytes

    out += (b'xref\n%d 1\n' % root + entry(off_cat)
            + b'%d 2\n' % n_stream + entry(off_stream) + entry(off_spec))

    new_trailer = b'trailer\n<< /Size %d /Root %d 0 R /Prev %d' % (
        size + 2, root, prev)
    info_m = re.search(br'/Info\s+\d+\s+0\s+R', trailer)
    if info_m:
        new_trailer += b' ' + info_m.group(0)
    id_m = re.search(br'/ID\s*\[[^\]]*\]', trailer)
    if id_m:
        new_trailer += b' ' + id_m.group(0)
    new_trailer += b' >>\nstartxref\n%d\n' % xref_off
    out += new_trailer + b'%%EOF\n'
    return out
