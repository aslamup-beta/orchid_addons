import time
from openerp.report import report_sxw
from openerp.addons.account.report.account_general_ledger import general_ledger
from openerp.tools.translate import _
from openerp.osv import osv
from pprint import pprint
class general_ledger(general_ledger):
    def __init__(self, cr, uid, name, context=None):
        super(general_ledger, self).__init__(cr, uid, name, context=context)
        self.localcontext.update( {
            'date_grouped_lines': self.date_grouped_lines,
            'partner_grouped_lines':self.partner_grouped_lines,
        })
        self.context = context

   
    def partner_grouped_lines(self,account):
        res = self.lines(account)
        partner_dict = self.od_partner_dict(res)
        data = self.od_deduplicate_partner(partner_dict)
        new_data = sorted(data, key=lambda k: k['partner'])
        return new_data
   
   
    def date_grouped_lines(self,account):
        res = self.lines(account)
        date_dict = self.od_date_dict(res)
        data = self.od_deduplicate(date_dict) 
        return data

    def od_deduplicate(self,l):
        result = []
        for item in l :
            check = False
            for r_item in result :
                if item['date'] == r_item['date'] :
                    check = True
                    lines = r_item['lines'] 
                    for line in item['lines']:
                        lines.append(line)
                    r_item['lines'] = lines
            if check == False :
                result.append( item )
        return result
    
    def od_deduplicate_partner(self,l):
        result = []
        for item in l :
            check = False
            # check item, is it exist in result yet (r_item)
            for r_item in result :
                if item['partner'] == r_item['partner'] :
                    # if found, add all key to r_item ( previous record)
                    check = True
                    lines = r_item['lines'] 
                    for line in item['lines']:
                        lines.append(line)
                    r_item['lines'] = lines
            if check == False :
                # if not found, add item to result (new record)
                result.append( item )
    
        return result

    def od_date_dict(self,data):
        res = []
        for val in data:
            res.append({'date':val.get('ldate'),'lines':[val]})
        return res
    
    def od_partner_dict(self,data):
        res = []
        for val in data:
            res.append({'partner':val.get('partner'),'lines':[val]})
        return res


class report_generalledger_od1(osv.AbstractModel):
    _name = 'report.account.report_generalledger_od1'
    _inherit = 'report.abstract_report'
    _template = 'account.report_generalledger_od1'
    _wrapped_report_class = general_ledger

class report_generalledger_od2(osv.AbstractModel):
    _name = 'report.account.report_generalledger_od2'
    _inherit = 'report.abstract_report'
    _template = 'account.report_generalledger_od2'
    _wrapped_report_class = general_ledger

class report_generalledger_od3(osv.AbstractModel):
    _name = 'report.account.report_generalledger_od3'
    _inherit = 'report.abstract_report'
    _template = 'account.report_generalledger_od3'
    _wrapped_report_class = general_ledger

class report_generalledger_od4(osv.AbstractModel):
    _name = 'report.account.report_generalledger_od4'
    _inherit = 'report.abstract_report'
    _template = 'account.report_generalledger_od4'
    _wrapped_report_class = general_ledger

class report_generalledger_od5(osv.AbstractModel):
    _name = 'report.account.report_generalledger_od5'
    _inherit = 'report.abstract_report'
    _template = 'account.report_generalledger_od5'
    _wrapped_report_class = general_ledger

class report_generalledger_od6(osv.AbstractModel):
    _name = 'report.account.report_generalledger_od6'
    _inherit = 'report.abstract_report'
    _template = 'account.report_generalledger_od6'
    _wrapped_report_class = general_ledger

class report_generalledger_od7(osv.AbstractModel):
    _name = 'report.account.report_generalledger_od7'
    _inherit = 'report.abstract_report'
    _template = 'account.report_generalledger_od7'
    _wrapped_report_class = general_ledger

class report_generalledger_od8(osv.AbstractModel):
    _name = 'report.account.report_generalledger_od8'
    _inherit = 'report.abstract_report'
    _template = 'account.report_generalledger_od8'
    _wrapped_report_class = general_ledger

class report_generalledger_od9(osv.AbstractModel):
    _name = 'report.account.report_generalledger_od9'
    _inherit = 'report.abstract_report'
    _template = 'account.report_generalledger_od9'
    _wrapped_report_class = general_ledger
