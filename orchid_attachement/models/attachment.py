from openerp.osv import osv, fields
from openerp import SUPERUSER_ID, tools

import logging
import sys

_logger = logging.getLogger(__name__)


class od_attachement(osv.Model):
    _inherit = "od.attachement"

    def _auto_init(self, cr, context=None):
        cr.execute("select COUNT(*) from information_schema.columns where table_name='od_attachement' AND column_name='attach_file';")
        res = cr.dictfetchone()
        if res.get('count'):
            _logger.info('Starting conversion for od_attachement: saving data for further processing.')
            cr.execute("ALTER TABLE od_attachement RENAME COLUMN attach_file TO attach_file_old")
            cr.commit()
        else:
            _logger.info('No attach_file field found in od_attachement; no data to save.')
        return super(od_attachement, self)._auto_init(cr, context=context)

    def _auto_end(self, cr, context=None):
        super(od_attachement, self)._auto_end(cr, context=context)
        cr.execute("select COUNT(*) from information_schema.columns where table_name='od_attachement' AND column_name='attach_file_old';")
        res = cr.dictfetchone()
        if res.get('count'):
            _logger.info('Starting rewrite of od_attachement, saving attach_files to filestore.')
            for document_line_id in self.pool.get('od.attachement').search(cr, SUPERUSER_ID, [], context=context):
                wvals = {}
                cr.execute("SELECT attach_file_old FROM od_attachement WHERE id = %s", (document_line_id, ))
                res = cr.dictfetchone()
                datas = res.get('attach_file_old')
                if datas:
                    wvals.update({'attach_file': datas[:]})
                    try:
                        self.pool.get('od.attachement').write(cr, SUPERUSER_ID, document_line_id, wvals)
                        cr.execute("UPDATE od_attachement SET attach_file_old = null WHERE id=%s", (document_line_id, ))
                    except:
                        filename = '/tmp/od_attachement_attach_file_%d.b64' % (document_line_id, )
                        with open(filename, 'wb') as f:
                            f.write(datas)
                        _logger.error('Failed to convert attach_file for product template %d - raw base-64 encoded data stored in %s' % (document_line_id, filename))
                        _logger.error('The error was: %s' % sys.exc_info()[0])
            cr.execute("ALTER TABLE od_attachement RENAME COLUMN attach_file_old TO attach_file_bkp")
            cr.commit()
        else:
            _logger.info('No attach_file_old field present in od_attachement; assuming data is already saved in the filestore.')

    def _get_attach_file(self, cr, uid, ids, name, args, context=None):
        attachment_field = 'attach_file_attachment_id' if name=='attach_file' else 'attach_file_medium_attachment_id'
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = {
                'attach_file': obj.attach_file_attachment_id and obj.attach_file_attachment_id.datas or None,
            }
        return result

    def _set_attach_file(self, cr, uid, id, name, value, args, context=None):
        obj = self.browse(cr, uid, id, context=context)
        attach_file_id = obj.attach_file_attachment_id.id
        if not value:
            ids = [attach_id for attach_id in [attach_file_id] if attach_id]
            if ids:
                self.pool['ir.attachment'].unlink(cr, uid, ids, context=context)
            return True
        if not (attach_file_id):
            attach_file_id = self.pool['ir.attachment'].create(cr, uid, {'name': 'Attach File'}, context=context)
            self.write(cr, uid, id, {'attach_file_attachment_id': attach_file_id},
                       context=context)
        self.pool['ir.attachment'].write(cr, uid, attach_file_id, {'datas': value}, context=context)

        return True

    _columns = {
        'attach_file_attachment_id': fields.many2one('ir.attachment', 'Attach File attachment', help='Technical field to store attach_file in filestore'),
        'attach_file': fields.function(_get_attach_file, fnct_inv=_set_attach_file, string="Attach File", multi='_get_attach_file', type='binary'),
    }

