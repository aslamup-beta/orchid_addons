# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import Warning
from __builtin__ import False

class wiz_assign_presale(models.TransientModel):

    _name = 'wiz.assign.presale'
    od_responsible_id = fields.Many2one('res.users',string='Presales Engineer',required=True)
    
    def is_a_sales_acc_manager(self, user):
            hr_pool = self.env['hr.employee']
            emp_rec = hr_pool.sudo().search([('user_id', '=', user)])
            return emp_rec.job_id.id in (40,83)

    @api.one
    def assign_presales(self):
        user = self.env.user.id or False
        if self.is_a_sales_acc_manager(user):
            raise Warning("You are not allowed to assign Pre-Sales Engineers. Kindly contact related Technology Unit Manager.")
        context = self._context
        active_id = context.get('active_id')
        od_responsible_id = self.od_responsible_id and self.od_responsible_id.id or False
        lead = self.env['crm.lead']
        lead_obj = lead.browse(active_id)
        lead_obj.write({'od_responsible_id':od_responsible_id})
        lead_obj.od_send_mail('od_opportunity_assigned_presales')
        return True
    
    
class wiz_assign_supporting_presale(models.TransientModel):

    _name = 'wiz.assign.supp.presale'
    other_presale_ids = fields.Many2many('res.users',string='Presales Engineer',required=True)
    
    def is_a_sales_acc_manager(self, user):
            hr_pool = self.env['hr.employee']
            emp_rec = hr_pool.sudo().search([('user_id', '=', user)])
            return emp_rec.job_id.id in (40,83)
    
    @api.one
    def assign_presales(self):
        user = self.env.user.id or False
        if self.is_a_sales_acc_manager(user):
            raise Warning("You are not allowed to assign Pre-Sales Engineers. Kindly contact related Technology Unit Manager.")
        presales_emails =[]
        context = self._context
        active_id = context.get('active_id')
        lead = self.env['crm.lead']
        lead_obj = lead.browse(active_id)
        ps = [x.id for x in self.other_presale_ids]
        user = self.env['res.users']
        user_obj = user.browse(ps)
        for user in user_obj:
            presales_emails.append(user.email)
        emails = ','.join(presales_emails)    
        context = self.env.context.copy()
        lead_obj.write({'other_presale_ids': [(4, ps)], 'support_presales_emails': emails})
        lead_obj.od_send_mail('od_opportunity_assigned_supporting_presales')
        return True
