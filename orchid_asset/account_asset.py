import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
class account_asset_asset(osv.osv):
    _inherit = 'account.asset.asset'
    _order = 'id desc'
    

    def _check_mac_address(self, cr, uid, ids, context=None):
        obj_fy = self.browse(cr, uid, ids[0], context=context)
        mac_address = obj_fy.od_mac_address
        if mac_address:
            length_of_mac = len(mac_address)
            if length_of_mac != 17:
                return False
            length_of_attributes_mac = len(mac_address.split(':'))
            if length_of_attributes_mac != 6:
                return False
        return True

    def set_to_close(self, cr, uid, ids, context=None):
        obj = self.browse(cr,uid,ids,context)
        today_current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if not obj.od_closing_date:
            self.write(cr, uid, ids, {'od_closing_date': str(today_current_datetime)}, context=context)
            
        return self.write(cr, uid, ids, {'state': 'close'}, context=context)


    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        if vals.get('od_sequence', '/') == '/':
            vals['od_sequence'] = self.pool.get('ir.sequence').get(cr, uid, 'od.asset.asset') or '/'
        return super(account_asset_asset,self).create(cr, uid, vals, context=context)



    _columns = {
                'od_purchase_date':fields.date('OD Purchase Date',states={'draft':[('readonly',False)]},readonly=True),
                'od_sequence':fields.char('Sequence',readonly=True),
                'od_cost':fields.float('Cost',states={'draft':[('readonly',False)]},readonly=True),
                'od_depreciation':fields.float('Depreciation',states={'draft':[('readonly',False)]},readonly=True),
                'od_serial_number':fields.char('Serial Number',states={'draft':[('readonly',False)]},readonly=True),
                'od_prorata_days':fields.boolean('Prorata Days',states={'draft':[('readonly',False)]},readonly=True),
                'od_amount_per_day':fields.char('Amount Per Day',readonly=True),
                'od_cost_center_id':fields.many2one('od.cost.centre',string='Cost Centre',states={'draft':[('readonly',False)]},readonly=True),
                'od_mac_address':fields.char('MAC Address',states={'draft':[('readonly',False)]},readonly=True),
                'od_closing_date':fields.date('Closing Date',)
                }
    _defaults = {
                 'od_sequence':'/',
                 'od_purchase_date': fields.date.context_today,
                 }


    _constraints = [
        (_check_mac_address, 'Error!\nmac address should be like the format 64:5a:04:9c:bc:ca', ['od_mac_address'])
    ]







#     def compute_depreciation_board(self, cr, uid, ids, context=None):
#         res = super(account_asset_asset,self).compute_depreciation_board(cr, uid, ids, context=context)
#         print "haiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii",res
#         return res




    def onchange_category_id(self, cr, uid, ids, category_id, context=None):
        res = super(account_asset_asset,self).onchange_category_id(cr, uid, ids, category_id, context=context)
        asset_categ_obj = self.pool.get('account.asset.category')
        if category_id:
            category_obj = asset_categ_obj.browse(cr, uid, category_id, context=context)
            res['value']['od_prorata_days'] = category_obj.od_prorata_days
        return res
    def last_day_of_month(self,cr,uid,any_day,context=None):
        next_month = any_day.replace(day=28) + relativedelta(days=4)  # this will never fail
        return next_month - relativedelta(days=next_month.day)

    def compute_depreciation_board(self, cr, uid, ids, context=None):
        depreciation_lin_obj = self.pool.get('account.asset.depreciation.line')
        currency_obj = self.pool.get('res.currency')
        total_amount = 0

        for asset in self.browse(cr, uid, ids, context=context):
            amount_check = asset.purchase_value - asset.salvage_value
            if asset.value_residual == 0.0:
                continue
            posted_depreciation_line_ids = depreciation_lin_obj.search(cr, uid, [('asset_id', '=', asset.id), ('move_check', '=', True)],order='depreciation_date desc')
            old_depreciation_line_ids = depreciation_lin_obj.search(cr, uid, [('asset_id', '=', asset.id), ('move_id', '=', False)])
            if old_depreciation_line_ids:
                depreciation_lin_obj.unlink(cr, uid, old_depreciation_line_ids, context=context)

            amount_to_depr = residual_amount = asset.value_residual

            if asset.prorata:
                depreciation_date = datetime.strptime(self._get_last_depreciation_date(cr, uid, [asset.id], context)[asset.id], '%Y-%m-%d')
                depreciation_date=self.last_day_of_month(cr, uid, depreciation_date, context)
            else:
                # depreciation_date = 1st January of purchase year
                purchase_date = datetime.strptime(asset.purchase_date, '%Y-%m-%d')
                #if we already have some previous validated entries, starting date isn't 1st January but last entry + method period
                if (len(posted_depreciation_line_ids)>0):
                    last_depreciation_date = datetime.strptime(depreciation_lin_obj.browse(cr,uid,posted_depreciation_line_ids[0],context=context).depreciation_date, '%Y-%m-%d')
                    depreciation_date = (last_depreciation_date+relativedelta(months=+asset.method_period))
                else:
                    depreciation_date = datetime(purchase_date.year, 1, 1)
            day = depreciation_date.day
            month = depreciation_date.month
            year = depreciation_date.year
            total_days = (year % 4) and 365 or 366
            undone_dotation_number = self._compute_board_undone_dotation_nb(cr, uid, asset, depreciation_date, total_days, context=context)
            if asset.prorata and asset.od_prorata_days:
                dep_date = datetime.strptime(self._get_last_depreciation_date(cr, uid, [asset.id], context)[asset.id], '%Y-%m-%d')
                depreciation_date = self.last_day_of_month(cr, uid, dep_date, context)
                delta = depreciation_date - dep_date
                no_of_days = delta.days + 1
#                 last_date = depreciation_date + relativedelta(months=asset.method_number)
                new_ldate = dep_date + relativedelta(months=asset.method_number,days=-1)
                total_delta = new_ldate - dep_date
                total_days = total_delta.days +1
                if not total_days:
                    amount_per_day = 0
                else:
                    amount_per_day = asset.value_residual/total_days
                self.write(cr,uid,ids,{'od_amount_per_day':amount_per_day},context=context)
                for x in range(len(posted_depreciation_line_ids), undone_dotation_number):
                    i = x + 1
                    company_currency = asset.company_id.currency_id.id
                    current_currency = asset.currency_id.id
                    amount = amount_per_day * no_of_days
                    residual_amount -= amount

                    if i == undone_dotation_number:
                        amount = amount_check - total_amount
                        amount = round(amount,3)
                    else:
                        total_amount += amount
                    vals = {
                         'amount': amount,
                         'od_no_of_days':no_of_days,
                         'asset_id': asset.id,
                         'sequence': i,
                         'name': str(asset.id) +'/' + str(i),
                         'remaining_value': residual_amount,
                         'depreciated_value': (asset.purchase_value - asset.salvage_value) - (residual_amount + amount),
                         'depreciation_date': depreciation_date.strftime('%Y-%m-%d'),
                    }

                    if amount:
                        depreciation_lin_obj.create(cr, uid, vals, context=context)
                    next_date = (datetime(year, month, 01) + relativedelta(months=+asset.method_period))
                    depreciation_date=self.last_day_of_month(cr, uid, next_date, context)
                    delta = depreciation_date - next_date
                    if depreciation_date > new_ldate:
                        delta = new_ldate - next_date
                    no_of_days = delta.days+1
                    day = depreciation_date.day
                    month = depreciation_date.month
                    year = depreciation_date.year
                return True

            else:
                for x in range(len(posted_depreciation_line_ids), undone_dotation_number):
                    i = x + 1
                    amount = self._compute_board_amount(cr, uid, asset, i, residual_amount, amount_to_depr, undone_dotation_number, posted_depreciation_line_ids, total_days, depreciation_date, context=context)

                    company_currency = asset.company_id.currency_id.id
                    current_currency = asset.currency_id.id
                    # compute amount into company currency
                    amount = currency_obj.compute(cr, uid, current_currency, company_currency, amount, context=context)
                    residual_amount -= amount

                    vals = {
                         'amount': amount,
                         'asset_id': asset.id,
                         'sequence': i,
                         'name': str(asset.id) +'/' + str(i),
                         'remaining_value': residual_amount,
                         'depreciated_value': (asset.purchase_value - asset.salvage_value) - (residual_amount + amount),
                         'depreciation_date': depreciation_date.strftime('%Y-%m-%d'),
                    }

                    if amount:
                        depreciation_lin_obj.create(cr, uid, vals, context=context)
                    # Considering Depr. Period as months
                    depreciation_date = (datetime(year, month, day) + relativedelta(months=+asset.method_period))
                    depreciation_date=self.last_day_of_month(cr, uid, depreciation_date, context)
                    day = depreciation_date.day
                    month = depreciation_date.month
                    year = depreciation_date.year
        return True
class account_asset_depreciation_line(osv.osv):
    _inherit = 'account.asset.depreciation.line'
    _columns = {
                'od_no_of_days':fields.char('Days'),
                }
    def create_move(self, cr, uid, ids, context=None):
        context = dict(context or {})
        can_close = False
        asset_obj = self.pool.get('account.asset.asset')
        period_obj = self.pool.get('account.period')
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        currency_obj = self.pool.get('res.currency')
        created_move_ids = []
        asset_ids = []
        for line in self.browse(cr, uid, ids, context=context):
            depreciation_date = context.get('depreciation_date') or line.depreciation_date or time.strftime('%Y-%m-%d')
            period_ids = period_obj.find(cr, uid, depreciation_date, context=context)
            company_currency = line.asset_id.company_id.currency_id.id
            current_currency = line.asset_id.currency_id.id
            context.update({'date': depreciation_date})
            amount = currency_obj.compute(cr, uid, current_currency, company_currency, line.amount, context=context)
            sign = (line.asset_id.category_id.journal_id.type == 'purchase' and 1) or -1
            asset_name = line.asset_id.name
            od_cost_centre_id = line.asset_id.od_cost_center_id and line.asset_id.od_cost_center_id.id or False
            reference = line.name
            move_vals = {
                'name': asset_name,
                'date': depreciation_date,
                'ref': reference,
                'period_id': period_ids and period_ids[0] or False,
                'journal_id': line.asset_id.category_id.journal_id.id,
                }
            move_id = move_obj.create(cr, uid, move_vals, context=context)
            journal_id = line.asset_id.category_id.journal_id.id
            partner_id = line.asset_id.partner_id.id
            move_line_obj.create(cr, uid, {
                'name': asset_name,
                'ref': reference,
                'move_id': move_id,
                'account_id': line.asset_id.category_id.account_depreciation_id.id,
                'debit': 0.0,
                'credit': amount,
                'period_id': period_ids and period_ids[0] or False,
                'od_cost_centre_id':od_cost_centre_id,
                'journal_id': journal_id,
                'partner_id': partner_id,
                'currency_id': company_currency != current_currency and  current_currency or False,
                'amount_currency': company_currency != current_currency and - sign * line.amount or 0.0,
                'date': depreciation_date,
            })
            move_line_obj.create(cr, uid, {
                'name': asset_name,
                'ref': reference,
                'move_id': move_id,
                'account_id': line.asset_id.category_id.account_expense_depreciation_id.id,
                'credit': 0.0,
                'debit': amount,
                'period_id': period_ids and period_ids[0] or False,
                'od_cost_centre_id':od_cost_centre_id,
                'journal_id': journal_id,
                'partner_id': partner_id,
                'currency_id': company_currency != current_currency and  current_currency or False,
                'amount_currency': company_currency != current_currency and sign * line.amount or 0.0,
                'analytic_account_id': line.asset_id.category_id.account_analytic_id.id,
                'date': depreciation_date,
                'asset_id': line.asset_id.id
            })
            self.write(cr, uid, line.id, {'move_id': move_id}, context=context)
            created_move_ids.append(move_id)
            asset_ids.append(line.asset_id.id)
        # we re-evaluate the assets to determine whether we can close them
        for asset in asset_obj.browse(cr, uid, list(set(asset_ids)), context=context):
            if currency_obj.is_zero(cr, uid, asset.currency_id, asset.value_residual):
                asset.write({'state': 'close'})
        return created_move_ids



class account_asset_category(osv.osv):
    _inherit = 'account.asset.category'
    _columns ={
                 'od_prorata_days':fields.boolean('Prorata Days'),
               }
