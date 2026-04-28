import datetime
import math
import time
import re
from operator import attrgetter

from openerp.exceptions import Warning
from openerp import tools
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import models, fields, api
from datetime import date, timedelta, datetime


class CommitmentLetter(models.Model):
    _name = "commitment.letter"
    _description = "Commitment Letter"
    _rec_name = 'name'
    _order = 'create_date desc'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    def od_get_company_id(self):
        return self.env.user.company_id

    company_id = fields.Many2one('res.company', string='Company', default=od_get_company_id)
    state = fields.Selection(
        [('draft', 'To Submit'), ('confirm', 'To Approve'),
         ('validate', 'Approved'), ('refuse', 'Refused')],
        'Status', readonly=True, track_visibility='onchange', copy=False, default='draft')
    letter_date = fields.Date('Date', track_visibility='onchange', select=True, copy=False, default=fields.Date.today)
    subject = fields.Char('Subject', default='Commitment Letter')
    subject_ar = fields.Char('Subject(Arabic)', default='Enter Subject In Arabic')
    commitment = fields.Text('Description')
    commitment_ar = fields.Text('Description (Arabic)')
    customer_id = fields.Many2one('res.partner', string="Customer")
    contact_person_id = fields.Many2one('res.partner', string="Contact Person")
    cus_job_position = fields.Char('Job Position', track_visibility='onchange')
    po_number = fields.Char('PO Number', track_visibility='onchange')
    po_date = fields.Date('PO Date', track_visibility='onchange', select=True, copy=False)
    contract_number = fields.Char('Contract Number', track_visibility='onchange')
    project_id = fields.Many2one('project.project', string="Project")
    manager_id = fields.Many2one('res.users', string="Project Manager")
    manager_name = fields.Char('Project Manager')
    name = fields.Char('Number')
    manager_name_ar = fields.Char('Project Manager(Arabic)')
    job_id = fields.Many2one('hr.job', string="Job Title")
    cost_sheet_id = fields.Many2one('od.cost.sheet', string="Cost Sheet")
    content_type = fields.Selection([('en', 'English'), ('ar', 'Arabic')],
                                  string='Content Type', default='en')
    customer_name = fields.Char('Customer')
    customer_name_ar = fields.Char('Customer (Arabic)')
    contact_person = fields.Char('Contact Person')
    contact_person_ar = fields.Char('Contact Person (Arabic)')

    def extract_english_sentence(self,text):
        # Regular expression to find words with only English letters
        print("text", text)
        words = re.findall(r'\b[A-Za-z]+\b', text)
        # Join the words back into a single sentence
        english_sentence = ' '.join(words)
        return english_sentence

    @api.onchange('project_id')
    def onchange_project_id(self):
        # contract_obj = self._get_contract_obj()
        project_id = self.project_id or False
        if project_id:
            self.cost_sheet_id = project_id.od_cost_sheet_id or False
            self.customer_id = project_id.partner_id or False
            self.contact_person_id = project_id.lead_id.od_contact_person or False
            if project_id.partner_id:
                self.customer_name = self.extract_english_sentence(project_id.partner_id.name)
            if project_id.lead_id and project_id.lead_id.od_contact_person:
                self.contact_person = self.extract_english_sentence(project_id.lead_id.od_contact_person.name)
            if self.contact_person_id:
                self.cus_job_position = self.contact_person_id.function
            # self.cus_job_position = contract_obj.wage
            self.po_number = self.cost_sheet_id.part_ref
            self.po_date = self.cost_sheet_id.po_date
            print("self.cost_sheet_id", self.cost_sheet_id)
            print("self.cost_sheet_id.od_owner_id", project_id.od_owner_id)
            self.manager_id = project_id.od_owner_id or False
            self.manager_name = self.extract_english_sentence(project_id.od_owner_id.name)
            manager_job = False
            manager_emp = self.env['hr.employee'].search([('user_id', '=', project_id.od_owner_id.id)], limit=1)
            if manager_emp:
                manager_job = self.env['hr.job'].search([('id', '=', manager_emp.job_id.id)], limit=1)
            if manager_job:
                self.job_id = manager_job or False

    @api.model
    def create(self, vals):
        res = super(CommitmentLetter, self).create(vals)
        if res.company_id.id == 6:
            res.name = self.env['ir.sequence'].get('od.project.commitment.letter') or '/'
        if res.company_id.id == 1:
            res.name = self.env['ir.sequence'].get('od.project.commitment.letter.uae') or '/'
        return res


    def od_send_mail(self, template):
        ir_model_data = self.env['ir.model.data']
        email_obj = self.pool.get('email.template')
        if self.company_id.id == 6:
            template = template + '_saudi'
        template_id = ir_model_data.get_object_reference('beta_extended', template)[1]
        rec_id = self.id
        email_obj.send_mail(self.env.cr, self.env.uid, template_id, rec_id, force_send=True)
        return True

    @api.one
    def action_submit(self):
        self.od_send_mail('od_commitment_letter_approval_manager')
        return self.write({'state': 'confirm'})

    @api.one
    def action_approve(self):
        self.od_send_mail('od_commitment_letter_notify_project')
        return self.write({'state': 'validate'})

    @api.one
    def action_refuse(self):
        self.od_send_mail('od_commitment_letter_refused')
        return self.write({'state': 'refuse'})
