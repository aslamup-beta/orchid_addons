# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2013 Camptocamp (<http://www.camptocamp.com>)
#    Authors: Ferdinand Gasauer, Joel Grand-Guillaume
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
##############################################################################

from openerp import models, fields, api
from openerp.tools.translate import _
from openerp.exceptions import Warning
from datetime import datetime

class od_tech_ticket_approval(models.Model):
    _name ='od.tech.ticket.approval'
    
    def od_get_company_id(self):
        return self.env.user.company_id
    def _get_today_date(self):
        return datetime.today().strftime('%d-%b-%y')
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    name = fields.Many2one('project.project','Project Name')
    user_id = fields.Many2one('res.users','Project Manager')
    partner_id = fields.Many2one('res.partner','Customer')
    date = fields.Date(string="Created Date", default=_get_today_date)
    ticket_line_ids = fields.One2many('od.tech.ticket.line','approval_form_id', "Linked Tickets")
    state = fields.Selection([('draft','Pending Approval'),('done','Approved'),('cancel','Cancelled By Owner')],string="Status", default="draft")
    
    def od1_send_mail(self,template):
        ir_model_data = self.env['ir.model.data']
        email_obj = self.pool.get('email.template')
        template_id = ir_model_data.get_object_reference('beta_customisation', template)[1]
        rec_id = self.id
        email_obj.send_mail(self.env.cr,self.env.uid,template_id,rec_id, force_send=True)
    
    @api.one
    def btn_done(self):
        self.write({'state':'done'})
    
    @api.one
    def btn_cancel(self):
        self.write({'state':'cancel'})
    
class od_tech_ticket_line(models.Model):
    _name ='od.tech.ticket.line'

    approval_form_id = fields.Many2one('od.tech.ticket.approval','Approval Form')
    assigned_id = fields.Many2one('res.users', 'Assigned To')
    date_start = fields.Datetime(string="Date Start")
    date_end = fields.Datetime(string="Date End")
    duration = fields.Float(string="Duration")
    status = fields.Selection([('draft','In Progress'),('done','Done'),('cancel_by_tl','Cancelled By Owner')],string="Status")
    ticket_id = fields.Many2one('project.task','Ticket')
    
        
    @api.one 
    def btn_confirm(self):
        ticket = self.ticket_id
        uid =self._uid
        date = str(datetime.now())
        if ticket.od_stage == 'draft':
            self.write({'status':'done'})
            ticket = self.ticket_id
            vals = {'od_initial_description': "Technician ticket auto-closed by system after Approval from PM.", 
                    'od_action_taken': "Technician ticket auto-closed by system after Approval from PM.",
                    'od_final_result': "Technician ticket auto-closed by system after Approval from PM."}
            for work_line in ticket.work_ids:
                work_line.write({'od_complete_date': self.date_end})
            ticket.write(vals)
            res =[{'evaluated_by':uid,'date':date}]
            ticket.od_tech_eval_log_ids = res
            ticket.sudo().btn_done()
        else:
            raise Warning("Ticket Cancelled or Already Approved, Kindly Discard this")
    
    @api.one 
    def btn_cancel(self):
        ticket = self.ticket_id
        if ticket.od_stage == 'draft':
            self.write({'status':'cancel_by_tl'})
            ticket.sudo().btn_cancel_by_owner()
        else:
            raise Warning("Ticket Cancelled or Already Approved, Kindly Discard this")
        
    @api.multi
    def btn_open_activity(self):
       
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'project.task',
                'res_id':self.ticket_id.id,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }
            
            
    
    