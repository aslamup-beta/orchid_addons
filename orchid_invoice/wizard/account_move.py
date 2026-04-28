from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _

class od_account_moves(osv.osv_memory):
    _name = 'od.account.moves'

    def run(self, cr, uid, ids, context=None):
        if not context:
            context = dict()

        active_model = context.get('active_model', False) or False
        active_ids = context.get('active_ids', []) or []
        if active_ids:
            record_ids = []
            records = self.pool[active_model].browse(cr, uid, active_ids, context=context)
            status = []
            for record in records:
                status.append(record.state)
                record_ids.append(record.id)
#            for st in status:
#                if st == 'post':
#                    record_ids.append(record.id)
#                    print "seconf for",record_ids
  
            acc_obj = self.pool.get('account.invoice')
            acc_obj.invoice_validate_demo(cr,uid,record_ids,context)
        
        

        return True
#def button_cancel(self, cr, uid, ids, context=None):
#        for line in self.browse(cr, uid, ids, context=context):
#            if not line.journal_id.update_posted:
#                raise osv.except_osv(_('Error!'), _('You cannot modify a posted entry of this journal.\nFirst you should set the journal to allow cancelling entries.'))
#        if ids:
#            cr.execute('UPDATE account_move '\
#                       'SET state=%s '\
#                       'WHERE id IN %s', ('draft', tuple(ids),))
#            self.invalidate_cache(cr, uid, context=context)
#        return True








