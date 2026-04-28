from openerp import api, tools
from openerp.osv import fields, osv

class hr_payslip(osv.osv):
    
    _inherit = 'hr.payslip'
    
    def get_contract(self, cr, uid, employee, date_from, date_to, context=None):
        """
        @param employee: browse record of employee
        @param date_from: date field
        @param date_to: date field
        @return: returns the ids of all active contracts for the given employee that need to be considered for the given dates
        """
        res = super(hr_payslip, self).get_contract(cr, uid, employee, date_from, date_to, context=context)
        contract_obj = self.pool.get('hr.contract')
        clause = []
        #a contract is valid if it ends between the given dates
        clause_1 = ['&',('date_end', '<=', date_to),('date_end','>=', date_from)]
        #OR if it starts between the given dates
        clause_2 = ['&',('date_start', '<=', date_to),('date_start','>=', date_from)]
        #OR if it starts before the date_from and finish after the date_end (or never finish)
        clause_3 = ['&',('date_start','<=', date_from),'|',('date_end', '=', False),('date_end','>=', date_to)]
        clause_final =  [('od_active', '=', True),('employee_id', '=', employee.id),'|','|'] + clause_1 + clause_2 + clause_3
        contract_ids = contract_obj.search(cr, uid, clause_final, context=context)
        return contract_ids

class hr_payslip_run(osv.osv):
    _inherit = 'hr.payslip.run'

    def od_confirm_all(self, cr, uid, ids, context=None):
        pay_batch_obj = self.browse(cr,uid,ids,context)
        for line in pay_batch_obj.slip_ids:
            if line.state == 'draft':
                line.compute_sheet()
                line.signal_workflow('hr_verify_sheet')
                line.signal_workflow('process_sheet')
        pay_batch_obj.write({'state':'close'})
        return True