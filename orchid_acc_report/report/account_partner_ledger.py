import time
from openerp.report import report_sxw
from openerp.addons.account.report.account_partner_ledger import third_party_ledger
from datetime import datetime, date, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.translate import _
from openerp.osv import osv
from pprint import pprint

class third_party_ledger(third_party_ledger):
    def __init__(self, cr, uid, name, context=None):
        super(third_party_ledger, self).__init__(cr, uid, name, context=context)
        self.localcontext.update( {
#            'get_invoice': self.get_invoice
            'get_payment_details':self.get_payment_details,
            'od_get_sum': self.od_get_sum,

        })
        self.context = context
        self.od_aged_date= date.today()


    def od_get_sum(self,data):
        res={}
        credit=debit=balance=0
        pdc_credit=pdc_debit=0
        adv_credit=adv_debit=0
        net_credit=net_debit=0
        paid_credit = paid_debit = 0
        for value in data:
            if value.get('pdc_check') and not value.get('reconcile_ref'):
                pdc_credit +=value.get('credit')
                pdc_debit +=value.get('debit')
            if (value.get('od_advance_payment') and not value.get('reconcile_ref')):
                adv_credit +=value.get('credit')
                adv_debit +=value.get('debit')
            if not  ((value.get('pdc_check') and not value.get('reconcile_ref')) or (value.get('od_advance_payment') and not value.get('reconcile_ref'))):
                net_credit +=value.get('credit')
                net_debit +=value.get('debit')
            if (value.get('invoice_state') == 'paid'):
                paid_credit += value.get('credit')
                paid_debit += value.get('debit')

            credit+=value.get('credit')
            debit+=value.get('debit')

        res['credit']=credit
        res['debit'] = debit
        res['balance'] = debit - credit

        res['pdc_credit'] = pdc_credit
        res['pdc_debit'] = pdc_debit
        res['pdc_balance'] = pdc_debit - pdc_credit

        res['adv_credit'] = adv_credit
        res['adv_debit'] = adv_debit
        res['adv_balance'] = adv_debit - adv_credit

        res['net_credit'] = net_credit
        res['net_debit'] = net_debit
        res['net_balance'] = net_debit - net_credit

        res['paid_credit'] = paid_credit
        res['paid_debit'] = paid_debit
        res['paid_balance'] = paid_debit - paid_credit
        return res

    def set_context(self, objects, data, ids, report_type=None):
        if data['form'].get('od_group_company_report') and ids:
            partner_obj =self.pool.get('res.partner').browse(self.cr, self.uid, ids)
            affiliate_ids = [partner.id for partner in partner_obj.affiliate_ids]
            ids = list(set(ids+affiliate_ids))
        if data['form'].get('od_aged_on'):
            self.od_aged_date = data['form'].get('od_aged_on')
        return super(third_party_ledger, self).set_context(objects, data, ids, report_type)

 
    def od_deduplicate(self,l):
        result = []
        rec_dict = {}
        for item in l :
            check = False
            # check item, is it exist in result yet (r_item)
            for r_item in result :
                if item.get('reconcile_ref',False) == r_item.get('reconcile_ref',False) :
                    # if found, add all key to r_item ( previous record)
                    check = True
                    net_bal = float(r_item.get('row_net_balance',0))+float(item.get('row_net_balance',0))
                    r_item['row_net_balance'] = net_bal
                    rec_dict[item.get('reconcile_ref')] = net_bal
                 
            if check == False :
                # if not found, add item to result (new record)
                
                
                result.append( item )
        
        for item in l:
            if item.get('reconcile_ref',False):
                net_bal = rec_dict.get(item['reconcile_ref'],False)
                item['row_net_balance'] = net_bal
     
        return l
    
    
    def get_payment_details(self, partner):
        move_state = ['draft','posted']
        if self.target_move == 'posted':
            move_state = ['posted']

        full_account = []
        if self.reconcil:
            RECONCILE_TAG = " "
        else:
            RECONCILE_TAG = "AND l.reconcile_ref IS NULL"
        self.cr.execute(
            "SELECT l.id, l.date, j.code, acc.code as a_code,m.date as move_date,l.date_maturity as date_maturity, acc.name as a_name, l.ref, m.name as move_name, l.name, l.reconcile_ref as reconcile_ref, l.debit, l.credit, l.amount_currency,l.currency_id, c.symbol AS currency_code, acc_v.pdc_check as pdc_check, acc_v.check_date as check_date, acc_v.check_no as check_no, acc_v.od_advance_payment as od_advance_payment,acc_v.type as voucher_type, acc_v.check_clear as check_clear, acc_v.check_bounce as check_bounce, acc_inv.name as invoice_name, acc_inv.number as invoice_number, acc_inv.date_due as invoice_date_due,acc_inv.date_invoice as invoice_date, acc_inv.residual as invoice_residual, acc_inv.check_total as invoice_check_total,acc_inv.state as invoice_state, acc_inv.amount_total as invoice_amount_total,acc_inv.type as type " \
            "FROM account_move_line l " \
            "LEFT JOIN account_journal j " \
                "ON (l.journal_id = j.id) " \
            "LEFT JOIN account_account acc " \
                "ON (l.account_id = acc.id) " \
            "LEFT JOIN res_currency c ON (l.currency_id=c.id)" \
            "LEFT JOIN account_move m ON (m.id=l.move_id)" \
            "LEFT JOIN account_voucher acc_v ON (acc_v.move_id = l.move_id)" \
            "LEFT JOIN account_invoice acc_inv ON (acc_inv.move_id = l.move_id)" \
            "WHERE l.partner_id = %s " \
                "AND l.account_id IN %s AND " + self.query +" " \
                "AND m.state IN %s " \
                " " + RECONCILE_TAG + " "\
                "ORDER BY l.date",
                (partner.id, tuple(self.account_ids), tuple(move_state)))
        res = self.cr.dictfetchall()
        sum = 0.0
        if self.initial_balance:
            sum = self.init_bal_sum
        balance = 0
        for r in res:
            sum += r['debit'] - r['credit']
            r['progress'] = sum
            balance = r['balance'] = (r.get('debit') - r.get('credit') + balance)
            r['row_balance'] = r.get('debit') - r.get('credit')
            r['row_net_balance'] = r.get('debit') - r.get('credit')
            aged_date = datetime.strptime(str(self.od_aged_date), '%Y-%m-%d')
            r['invoice_date_due_days'] = r['invoice_date_days'] = 0
            if r['invoice_date_due']:
                invoice_date_due=datetime.strptime(r['invoice_date_due'], '%Y-%m-%d')
                r['invoice_date_due_days'] =  (aged_date -  invoice_date_due).days
            if r['invoice_date']:
                invoice_date=datetime.strptime(r['invoice_date'], '%Y-%m-%d')
                r['invoice_date_days'] = (aged_date - invoice_date).days
            
            r['move_line_date_maturity_days'] = r['move_date_days'] = 0
            if r['date_maturity']:
                date_due=datetime.strptime(r['date_maturity'], '%Y-%m-%d')
                r['move_line_date_maturity_days'] =  (aged_date -  date_due).days
            if r['move_date']:
                move_date=datetime.strptime(r['move_date'], '%Y-%m-%d')
                r['move_date_days'] = (aged_date - move_date).days
            full_account.append(r)
        pprint(full_account)
        full_account = self.od_deduplicate(full_account)
        pprint(full_account)
        return full_account


class report_partnerledger_od1(osv.AbstractModel):
    _name = 'report.account.report_partnerledger_od1'
    _inherit = 'report.abstract_report'
    _template = 'account.report_partnerledger_od1'
    _wrapped_report_class = third_party_ledger

class report_partnerledger_od2(osv.AbstractModel):
    _name = 'report.account.report_partnerledger_od2'
    _inherit = 'report.abstract_report'
    _template = 'account.report_partnerledger_od2'
    _wrapped_report_class = third_party_ledger


class report_partnerledger_od3(osv.AbstractModel):
    _name = 'report.account.report_partnerledger_od3'
    _inherit = 'report.abstract_report'
    _template = 'account.report_partnerledger_od3'
    _wrapped_report_class = third_party_ledger

class report_partnerledger_od4(osv.AbstractModel):
    _name = 'report.account.report_partnerledger_od4'
    _inherit = 'report.abstract_report'
    _template = 'account.report_partnerledger_od4'
    _wrapped_report_class = third_party_ledger


class report_partnerledger_od5(osv.AbstractModel):
    _name = 'report.account.report_partnerledger_od5'
    _inherit = 'report.abstract_report'
    _template = 'account.report_partnerledger_od5'
    _wrapped_report_class = third_party_ledger


class report_partnerledger_od6(osv.AbstractModel):
    _name = 'report.account.report_partnerledger_od6'
    _inherit = 'report.abstract_report'
    _template = 'account.report_partnerledger_od6'
    _wrapped_report_class = third_party_ledger


class report_partnerledger_od7(osv.AbstractModel):
    _name = 'report.account.report_partnerledger_od7'
    _inherit = 'report.abstract_report'
    _template = 'account.report_partnerledger_od7'
    _wrapped_report_class = third_party_ledger

class report_partnerledger_od8(osv.AbstractModel):
    _name = 'report.account.report_partnerledger_od8'
    _inherit = 'report.abstract_report'
    _template = 'account.report_partnerledger_od8'
    _wrapped_report_class = third_party_ledger

class report_partnerledger_od9(osv.AbstractModel):
    _name = 'report.account.report_partnerledger_od9'
    _inherit = 'report.abstract_report'
    _template = 'account.report_partnerledger_od9'
    _wrapped_report_class = third_party_ledger
