#-*- coding:utf-8 -*-
from datetime import datetime
from dateutil.relativedelta import relativedelta
import calendar
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _

class od_multiple_cheque(osv.osv):
    _name = 'od.multiple.cheque'
    _description = 'od.multiple.cheque'

    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'od.multiple.cheque') or '/'
        return super(od_multiple_cheque, self).create(cr, uid, vals, context=context)


    def get_pdc_payable_from_parameter(self,cr, uid, ids, context=None):
        journal_obj = self.pool.get('account.journal')
        parameter_obj = self.pool.get('ir.config_parameter')
        parameter_ids = parameter_obj.search(cr, uid, [('key','=','Def_PDCP_Journal')])
        if not parameter_ids:
            raise osv.except_osv(_('Settings Warning!'),_('Plz conf it in System Parameters with key Def_PDCP_Journal!'))
        parameter_data= parameter_obj.read(cr, uid, parameter_ids[0],['od_model_id'])
        if not parameter_data.get('od_model_id'):
            raise osv.except_osv(_('Settings Warning!'),_('No Value Found in System Parameter with key Def_PDCP_Journal'))
        journ_id = parameter_data.get('od_model_id').split(',')[1]
        journ_recn=journal_obj.browse(cr, uid,int(journ_id),context)
        return journ_recn.id


    def generate_cheque(self, cr, uid, ids, context=None):
        acc_voucher_obj = self.pool.get('account.voucher')
        for multi_cheque in self.browse(cr, uid, ids, context=context):
            line_ids = acc_voucher_obj.search(cr, uid,[('multiple_cheque_id','=',multi_cheque.id)])
            if line_ids:
                raise osv.except_osv(_('Warning!'),_('Cheques already Created!'))
            no_of_installments = multi_cheque.no_of_installments or 1
            ds = datetime.strptime(multi_cheque.date_start, '%Y-%m-%d')
#            de = datetime.strptime(multi_cheque.date_end, '%Y-%m-%d')
            loop_count = 0
            next_date = ds
            final_date = ds
            install_amt = multi_cheque.amount / no_of_installments
            journal_id = self.get_pdc_payable_from_parameter(cr, uid, ids, context=context)
#the loop creats the account_voucher for the number of installations given
            while loop_count < no_of_installments:
                loop_count +=1
                acc_voucher_obj.create(cr, uid, {
                        'payment_type': multi_cheque.payment_type,
                        'partner_id': multi_cheque.partner_id and multi_cheque.partner_id.id,
                        'account_id': multi_cheque.partner_id and multi_cheque.partner_id.property_account_receivable.id or False,
                        'journal_id': journal_id,
                        'amount':install_amt,
                        'check_date':next_date,
                        'state':'draft',
                        'check_bank':True,
                        'multiple_cheque_id':multi_cheque.id})
                final_date = next_date
                next_date = next_date + relativedelta(months=1)
            self.write(cr, uid, ids, {'date_end':final_date})
        return True

    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id

    _columns = {
        'name': fields.char('Name'),
        'payment_type': fields.selection([('cust_payment', 'Customer Payment'), ('sup_payment', 'Supplier Payment'), ('expense', 'Expense'), ('income', 'Income')], 'Type', size=24),
        'partner_id':fields.many2one('res.partner', 'Partner'),
        'company_id': fields.many2one('res.company','Company'),
        'date': fields.date('Date',required="1"),
        'date_start': fields.date('Start Date'),
        'date_end': fields.date('End Date'),
        'no_of_installments': fields.integer('#Installments'),
        'amount': fields.float('Amount', required="1"),
        'check_line': fields.one2many('account.voucher','multiple_cheque_id','Check Lines'),
        'description': fields.text('Description'),
    }
    _defaults = {
        'name': '/',
        'date': fields.date.context_today,
        'date_start': fields.date.context_today,
        'company_id': _get_default_company,
    }

class account_voucher(osv.osv):
    _inherit = 'account.voucher'
    _columns = {
        'multiple_cheque_id' : fields.many2one('od.multiple.cheque','Multi Check',ondelete='cascade'),
    }

#class od_multiple_cheque_line(osv.osv):
#    _name = 'od.multiple.cheque.line'
#    _description = 'Od Multiple Cheque '
#    _columns = {
#        'multiple_cheque_id': fields.many2one('od.multiple.cheque','Multiple Check',ondelete='cascade'),
#        'date_cheque': fields.date('Cheque Date'),
#        'amount': fields.float('Amount'),
#    }
