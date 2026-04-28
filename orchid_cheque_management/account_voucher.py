from openerp.osv import osv,fields
class account_voucher(osv.osv):
    _inherit = 'account.voucher'

#set the account for the selected partner
    def onchange_od_partner_id(self, cr, uid, ids,partner_id,context=None):
        res={}
        if partner_id:
            partner = self.pool.get('res.partner').browse(cr,uid,partner_id)
#            print "###############",partner
#            writeoff_acc_id = partner.
#            return {'value': {'writeoff_acc_id': writeoff_acc_id}}
        return res

    def onchange_od_group_pay(self, cr, uid, ids, od_group_pay,context=None):
        return {'value':{'partner_id':''}}


    _columns = {
        'od_partner_id':fields.many2one('res.partner','Partner'),
        'od_populate': fields.selection([('dr','Debit'),('cr','Credit')], 'Allocation'),
        'od_group_pay': fields.boolean('Pay as Group',readonly=True,states={'draft':[('readonly',False)]}),
        'od_payee':fields.char('Payee',readonly=True,states={'draft':[('readonly',False)]}),
        'od_acc_payee':fields.boolean('A/c Payee',readonly=True,states={'draft':[('readonly',False)]})
    }


    #partner selection in diff amount writeoff
    def writeoff_move_line_get(self, cr, uid, voucher_id, line_total, move_id, name, company_currency, current_currency, context=None):

        move_line = super(account_voucher,self).writeoff_move_line_get(cr, uid, voucher_id, line_total, move_id, name, company_currency, current_currency, context=None)

        voucher = self.pool.get('account.voucher').browse(cr,uid,voucher_id,context)
        if voucher.state == 'draft' and voucher.pdc_check and voucher.od_with_out_allocaion:
#            partner_rec_acc_id = voucher.partner_id.property_account_receivable.id
#            partner_payable_acc_id = voucher.partner_id.property_account_payable.id
            mvl_acc_id = move_line.get('account_id')
#            if mvl_acc_id and mvl_acc_id == partner_rec_acc_id:
            move_line['account_id'] = voucher.od_check_clearing_acc_id and voucher.od_check_clearing_acc_id.id or move_line.get('account_id')



        if voucher.od_partner_id and voucher.od_partner_id.id:
            move_line['partner_id'] = voucher.od_partner_id and voucher.od_partner_id.id
        return move_line



    def od_deallocate(self,cr, uid, ids, context=None):
        ctx = context.copy()
        for voucher in self.browse(cr,uid,ids,context):
            

            voucher.line_cr_ids.unlink()
            voucher.line_dr_ids.unlink()
            voucher_cr_lines=[]
            voucher_dr_lines=[]

            partner_id = voucher.partner_id and voucher.partner_id.id
            journal_id = voucher.journal_id and voucher.journal_id.id
            price = voucher.amount or 0.0
            currency_id = voucher.currency_id and voucher.currency_id.id
            ttype = voucher.type
            rate = voucher.payment_rate
            date = voucher.date
            ctx.update({'date': date})

            payment_rate_currency_id = voucher.payment_rate_currency_id and voucher.payment_rate_currency_id.id

            voucher_rate = self.pool.get('res.currency').read(cr, uid, [currency_id], ['rate'], context=ctx)[0]['rate']
            ctx.update({
                'voucher_special_currency': payment_rate_currency_id,
                'voucher_special_currency_rate': rate * voucher_rate,
            })
            res = self.od_recompute_voucher_lines(cr,uid,ids,partner_id,journal_id,price,currency_id,ttype,date,context=ctx)
            cr_lines = res['value'].get('line_cr_ids')
            dr_lines = res['value'].get('line_dr_ids')

            
#            if cr_lines and voucher.od_populate == 'cr':
#                for line in cr_lines:
#                    voucher_cr_lines.append([0,0,line])
#            elif dr_lines and voucher.od_populate == 'dr':
#                for line in dr_lines:
#                    voucher_dr_lines.append([0,0,line])
#            else:
            for line in cr_lines:
                voucher_cr_lines.append([0,0,line])
            for line in dr_lines:
                voucher_dr_lines.append([0,0,line])

            voucher.write({'line_cr_ids':voucher_cr_lines,'line_dr_ids':voucher_dr_lines})

            return res

        return self.od_recompute_voucher_lines(cr,uid,ids,partner_id,journal_id,price,currency_id,ttype,date,context=ctx)



#    to avoid automatic Allocation
    def recompute_voucher_lines(self, cr, uid, ids, partner_id, journal_id, price, currency_id, ttype, date, context=None):
        #set default values
        default = {
            'value': {'line_dr_ids': [], 'line_cr_ids': [], 'pre_line': False},
        }
        return default

#automatic alocation is overide to allocate manually
    def od_recompute_voucher_lines(self, cr, uid, ids, partner_id, journal_id, price, currency_id, ttype, date, context=None):
        if context is None:
            context={}
        if context.get('od_manual_allocate'):
            return {}
        """
        Returns a dict that contains new values and context

        @param partner_id: latest value from user input for field partner_id
        @param args: other arguments
        @param context: context arguments, like lang, time zone

        @return: Returns a dict which contains new values, and context
        """
        def _remove_noise_in_o2m():
            """if the line is partially reconciled, then we must pay attention to display it only once and
                in the good o2m.
                This function returns True if the line is considered as noise and should not be displayed
            """
            if line.reconcile_partial_id:
                if currency_id == line.currency_id.id:
                    if line.amount_residual_currency <= 0:
                        return True
                else:
                    if line.amount_residual <= 0:
                        return True
            return False
        if context is None:
            context = {}
        context_multi_currency = context.copy()

        currency_pool = self.pool.get('res.currency')
        move_line_pool = self.pool.get('account.move.line')
        partner_pool = self.pool.get('res.partner')
        journal_pool = self.pool.get('account.journal')
        line_pool = self.pool.get('account.voucher.line')

        #set default values
        default = {
            'value': {'line_dr_ids': [], 'line_cr_ids': [], 'pre_line': False},
        }

        # drop existing lines
        line_ids = ids and line_pool.search(cr, uid, [('voucher_id', '=', ids[0])])
        for line in line_pool.browse(cr, uid, line_ids, context=context):
            if line.type == 'cr':
                default['value']['line_cr_ids'].append((2, line.id))
            else:
                default['value']['line_dr_ids'].append((2, line.id))

        if not partner_id or not journal_id:
            return default

        journal = journal_pool.browse(cr, uid, journal_id, context=context)
        partner = partner_pool.browse(cr, uid, partner_id, context=context)
        currency_id = currency_id or journal.company_id.currency_id.id

        total_credit = 0.0
        total_debit = 0.0
        account_type = None
        if context.get('account_id'):
            account_type = self.pool['account.account'].browse(cr, uid, context['account_id'], context=context).type
        if ttype == 'payment':
            if not account_type:
                account_type = 'payable'
            total_debit = price or 0.0
        else:
            total_credit = price or 0.0
            if not account_type:
                account_type = 'receivable'

##Custom Code
        move_search_domain = [('state','=','valid'), ('account_id.type', '=', account_type), ('reconcile_id', '=', False), ('partner_id', '=', partner_id)]
        if context.get('od_group_pay'):
            move_search_domain = [('state','=','valid'), ('account_id.type', '=', account_type), ('reconcile_id', '=', False), ('partner_id', 'child_of', partner_id)]

        if not context.get('move_line_ids', False):
            ids = move_line_pool.search(cr, uid, move_search_domain, context=context)
        else:
            ids = context['move_line_ids']
        invoice_id = context.get('invoice_id', False)
        company_currency = journal.company_id.currency_id.id
        move_lines_found = []

        #order the lines by most old first
        ids.reverse()
        account_move_lines = move_line_pool.browse(cr, uid, ids, context=context)

        #compute the total debit/credit and look for a matching open amount or invoice
        for line in account_move_lines:
            if _remove_noise_in_o2m():
                continue

            if invoice_id:
                if line.invoice.id == invoice_id:
                    #if the invoice linked to the voucher line is equal to the invoice_id in context
                    #then we assign the amount on that line, whatever the other voucher lines
                    move_lines_found.append(line.id)
            elif currency_id == company_currency:
                #otherwise treatments is the same but with other field names
                if line.amount_residual == price:
                    #if the amount residual is equal the amount voucher, we assign it to that voucher
                    #line, whatever the other voucher lines
                    move_lines_found.append(line.id)
                    break
                #otherwise we will split the voucher amount on each line (by most old first)
                total_credit += line.credit or 0.0
                total_debit += line.debit or 0.0
            elif currency_id == line.currency_id.id:
                if line.amount_residual_currency == price:
                    move_lines_found.append(line.id)
                    break
                total_credit += line.credit and line.amount_currency or 0.0
                total_debit += line.debit and line.amount_currency or 0.0

        remaining_amount = price
        #voucher line creation
        for line in account_move_lines:

            if _remove_noise_in_o2m():
                continue

            if line.currency_id and currency_id == line.currency_id.id:
                amount_original = abs(line.amount_currency)
                amount_unreconciled = abs(line.amount_residual_currency)
            else:
                #always use the amount booked in the company currency as the basis of the conversion into the voucher currency
                amount_original = currency_pool.compute(cr, uid, company_currency, currency_id, line.credit or line.debit or 0.0, context=context_multi_currency)
                amount_unreconciled = currency_pool.compute(cr, uid, company_currency, currency_id, abs(line.amount_residual), context=context_multi_currency)
            line_currency_id = line.currency_id and line.currency_id.id or company_currency
            rs = {
                'name':line.move_id.name,
                'type': line.credit and 'dr' or 'cr',
                'move_line_id':line.id,
                'account_id':line.account_id.id,
                'amount_original': amount_original,
                'amount': 0.0, #custom
                'date_original':line.date,
                'date_due':line.date_maturity,
                'amount_unreconciled': amount_unreconciled,
                'currency_id': line_currency_id,
                'od_partner_id':line.partner_id and line.partner_id.id, #Custom Code
            }
            remaining_amount -= rs['amount']
            #in case a corresponding move_line hasn't been found, we now try to assign the voucher amount
            #on existing invoices: we split voucher amount by most old first, but only for lines in the same currency
            if not move_lines_found:
                if currency_id == line_currency_id:
                    if line.credit:
                        amount = min(amount_unreconciled, abs(total_debit))
                        rs['amount'] = 0.0
                        total_debit -= amount
                    else:
                        amount = min(amount_unreconciled, abs(total_credit))
                        rs['amount'] = 0.0
                        total_credit -= amount

            if rs['amount_unreconciled'] == rs['amount']:
                rs['reconcile'] = True

            if rs['type'] == 'cr':
                default['value']['line_cr_ids'].append(rs)
            else:
                default['value']['line_dr_ids'].append(rs)

            if len(default['value']['line_cr_ids']) > 0:
                default['value']['pre_line'] = 1
            elif len(default['value']['line_dr_ids']) > 0:
                default['value']['pre_line'] = 1
            default['value']['writeoff_amount'] = self._compute_writeoff_amount(cr, uid, default['value']['line_dr_ids'], default['value']['line_cr_ids'], price, ttype)
        return default

class account_voucher_line(osv.osv):
    _inherit = 'account.voucher.line'
    _columns = {
        'od_partner_id': fields.many2one('res.partner','Partner'),
    }
