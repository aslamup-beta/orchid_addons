import datetime
import math
import time
from operator import attrgetter
import re
from openerp.exceptions import Warning
from openerp import tools
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import models, fields, api
from datetime import date, timedelta, datetime

class BetaPartner(models.Model):
    _name = "beta.partner"
    _description = "Beta Partner"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    def od_get_company_id(self):
        return self.env.user.company_id

    def od_get_user_id(self):
        return self.env.user

    @api.model
    def check_email(self, email, name):
        regex = '^[a-zA-Z0-9]+[\._-]?[a-zA-Z0-9]+[@]\w+[.]\w{2,10}$'
        regex1 = '^[a-zA-Z0-9]+[\._-]?[a-zA-Z0-9]+[@]\w+[\._-]\w+[.]\w{2,10}$'
        regex2 = '^[a-zA-Z0-9]+[\._-]?[a-zA-Z0-9]+[\._-]?[a-zA-Z0-9]+[@]\w+[\._-]\w+[.]\w{2,10}$'
        regex3 = '^[a-zA-Z0-9]+[\._-]?[a-zA-Z0-9]+[\._-]?[a-zA-Z0-9]+[@]\w+[.]\w{2,10}$'
        regex4 = '^[a-zA-Z0-9]+[\._-]?[a-zA-Z0-9]+[\._-]?[a-zA-Z0-9]+[@]\w+[\._-]\w+[\._-]\w+[.]\w{2,10}$'
        if (re.search(regex, email)):
            return True
        elif (re.search(regex1, email)):
            return True
        elif (re.search(regex2, email)):
            return True
        elif (re.search(regex3, email)):
            return True
        elif (re.search(regex4, email)):
            return True
        else:
            raise Warning("Please Enter a valid Email for %s" % name)

    @api.onchange('email')
    def onchange_email(self):
        email = self.email
        if email:
            name = self.contact_person
            self.check_email(email, name)

    @api.onchange('od_state_id')
    def onchange_state(self):
        state = self.od_state_id
        if state:
            self.od_country_id = state.country_id and state.country_id.id or False

    @api.onchange('user_id')
    def onchange_user_id(self):
        if self.user_id:
            team_obj = self.env['crm.case.section']
            sales_team = team_obj.search([
                '|',
                ('user_id', '=', self.user_id.id),
                ('member_ids', 'in', [self.user_id.id])
            ], order="id desc", limit=1)
            if sales_team:
                self.team_id = sales_team.id
            else:
                self.team_id = False
        else:
            self.team_id = False

    @api.onchange('related_partner_id')
    def onchange_related_partner(self):
        if self.related_partner_id:
            partner = self.related_partner_id
            self.registration_type = 'modify'
            self.name = partner.name
            self.od_street = partner.street
            self.od_street2 = partner.street2
            self.od_state_id = partner.state_id and partner.state_id.id or False
            self.od_city = partner.city
            self.od_zip = partner.zip
            self.od_country_id = partner.country_id and partner.country_id.id or False
            self.website = partner.website
            self.od_class = partner.od_class
            self.user_id = partner.user_id and partner.user_id.id or False
            self.team_id = partner.section_id and partner.section_id.id or False
            self.company_id = partner.company_id and partner.company_id.id or False
            self.od_industry_id = partner.od_industry_id and partner.od_industry_id.id or False
            self.vat_id = partner.vat
            self.od_building_no = partner.od_building_no
            self.od_additional_no = partner.od_additional_no
            self.od_other_buyer_id = partner.od_other_buyer_id
            self.od_cr_no = partner.od_cr_no
            self.district = partner.district
            self.buyer_identification = partner.buyer_identification
            self.image = partner.image_medium

    @api.depends('name', 'od_street', 'od_street2','od_class', 'related_partner_id', 'registration_type', 'user_id',
                 'team_id', 'od_industry_id', 'vat_id', 'company_id', 'od_building_no', 'od_additional_no', 'od_city',
                 'od_zip', 'district', 'od_state_id', 'od_country_id', 'website')
    def _compute_change_summary(self):
        for rec in self:
            if rec.registration_type == 'modify' and rec.related_partner_id:
                diff = "<ul>"
                p = rec.related_partner_id

                # Compare fields and build the HTML string
                if rec.name != p.name:
                    diff += "<li><b>Name:</b> " + (p.name or '(Empty)') + " ==>  " + (rec.name or '(Removed)') + "</li>"

                if rec.user_id != p.user_id:
                    diff += "<li><b>Sales Account Manager:</b> " + (p.user_id.name or '(Empty)') + " ==>  " + (rec.user_id.name or '(Removed)') + "</li>"

                if rec.team_id != p.section_id:
                    diff += "<li><b>Sales Team:</b> " + (p.section_id.name or '(Empty)') + " ==>  " + (rec.team_id.name or '(Removed)') + "</li>"

                if rec.od_class != p.od_class:
                    diff += "<li><b>Class:</b> " + (p.od_class or '(Empty)') + " ==>  " + (rec.od_class or '(Removed)') + "</li>"

                if rec.od_industry_id != p.od_industry_id:
                    diff += "<li><b>Industry:</b> " + (p.od_industry_id.name or '(Empty)') + " ==>  " + (rec.od_industry_id.name or '(Removed)') + "</li>"

                if rec.vat_id != p.vat:
                    diff += "<li><b>VAT:</b> " + (p.vat or '(Empty)') + " ==>  " + (rec.vat_id or '(Removed)') + "</li>"

                if rec.od_street != p.street:
                    diff += "<li><b>Street:</b> " + (p.street or '(Empty)') + " ==>  " + (rec.od_street or '(Removed)') + "</li>"

                if rec.od_street2 != p.street2:
                    diff += "<li><b>Short Address:</b> " + (p.street2 or '(Empty)') + " ==>  " + (rec.od_street2 or '(Removed)') + "</li>"

                if rec.od_zip != p.zip:
                    diff += "<li><b>Postal Code:</b> " + (p.zip or '(Empty)') + " ==>  " + (rec.od_zip or '(Removed)') + "</li>"

                if rec.district != p.district:
                    diff += "<li><b>District:</b> " + (p.district or '(Empty)') + " ==>  " + (rec.district or '(Removed)') + "</li>"

                if rec.od_state_id != p.state_id:
                    diff += "<li><b>City:</b> " + (p.state_id.name or '(Empty)') + " ==>  " + (rec.od_state_id.name or '(Removed)') + "</li>"

                if rec.od_country_id != p.country_id:
                    diff += "<li><b>Country:</b> " + (p.country_id.name or '(Empty)') + " ==>  " + (rec.od_country_id.name or '(Removed)') + "</li>"

                if rec.od_building_no != p.od_building_no:
                    diff += "<li><b>Building No:</b> " + (p.od_building_no or '(Empty)') + " ==>  " + (rec.od_building_no or '(Removed)') + "</li>"

                if rec.od_additional_no != p.od_additional_no:
                    diff += "<li><b>Secondary No:</b> " + (p.od_additional_no or '(Empty)') + " ==>  " + (rec.od_additional_no or '(Removed)') + "</li>"

                if rec.buyer_identification != p.buyer_identification:
                    diff += "<li><b>Buyer Identification:</b> " + (p.buyer_identification or '(Empty)') + " ==>  " + (rec.buyer_identification or '(Removed)') + "</li>"

                if rec.od_other_buyer_id != p.od_other_buyer_id:
                    diff += "<li><b>Other Buyer ID:</b> " + (p.od_other_buyer_id or '(Empty)') + " ==>  " + (rec.od_other_buyer_id or '(Removed)') + "</li>"

                if rec.od_cr_no != p.od_cr_no:
                    diff += "<li><b>Commercial Register:</b> " + (p.od_cr_no or '(Empty)') + " ==>  " + (rec.od_cr_no or '(Removed)') + "</li>"

                if rec.website != p.website:
                    diff += "<li><b>Website:</b> " + (p.website or '(Empty)') + " ==>  " + (rec.website or '(Removed)') + "</li>"

                diff += "</ul>"

                if diff == "<ul></ul>":
                    rec.change_summary = "<p style='color:green;'>No changes detected compared to the original customer record.</p>"
                else:
                    rec.change_summary = diff
            else:
                rec.change_summary = "<p>New Customer Registration - No comparison needed.</p>"

    state = fields.Selection(
        [('draft', 'Draft'), ('confirm', 'Pending Approval'),
         ('validate', 'Approved'), ('refuse', 'Refused')],
        'Status', readonly=True, track_visibility='onchange', copy=False, default='draft')
    name = fields.Char(string="Name")
    image = fields.Binary(string='Image')
    active = fields.Boolean(string="Active", default=True)
    od_street = fields.Char(string="Street")
    od_street2 = fields.Char(string="Short Address")
    od_state_id = fields.Many2one('res.country.state', string='City')
    od_city = fields.Char(string="City")
    od_zip = fields.Char(string="Postal Code")
    related_partner_id = fields.Many2one('res.partner', string='Related Partner')
    new_partner_id = fields.Many2one('res.partner', string='Newly Created Customer in ERP')
    od_country_id = fields.Many2one('res.country', string='Country')
    company_id = fields.Many2one('res.company', string='Company', default=od_get_company_id)
    od_industry_id = fields.Many2one('od.partner.industry', string='Industry')
    od_territory_id = fields.Many2one('od.partner.territory', string='Territory')
    team_id = fields.Many2one('crm.case.section', string='Sales Team')
    website = fields.Char(string="Website")
    contact_person = fields.Char(string="Contact Person")
    function = fields.Char(string="Job Position")
    email = fields.Char(string="Email")
    mobile = fields.Char(string="Mobile")
    phone = fields.Char(string="Phone")
    user_id = fields.Many2one('res.users', string="Sales Account Manager")
    # created_by = fields.Many2one('res.users', string="Created By", default=od_get_user_id)
    vat_id = fields.Char(string="TRN")
    od_class = fields.Selection([('a', 'A'), ('b', 'B'), ('c', 'C'), ('r', 'R')], string="Class")
    od_building_no = fields.Char(string="Building No.")
    od_additional_no = fields.Char(string="Secondary No.")
    od_other_buyer_id = fields.Char(string="Other Buyer ID")
    od_cr_no = fields.Char(string="Commercial Register")
    district = fields.Char(string='District')
    buyer_identification = fields.Selection([('NAT', 'National ID'), ('IQA', 'Iqama Number'),
                                             ('PAS', 'Passport ID'),
                                             ('CRN', 'Commercial Registration number'),
                                             ('MOM', 'Momra license'), ('MLS', 'MLSD license'),
                                             ('SAG', 'Sagia license'), ('GCC', 'GCC ID'),
                                             ('OTH', 'Other OD'),
                                             ('TIN', 'Tax Identification Number'), ('700', '700 Number')],
                                            string="Buyer Identification",
                                            help="|) In case multiple IDs exist then one of the above must be entered,"
                                                 "||) In case of tax invoice, "
                                                 "      1) Not mandatory for export invoices.")

    registration_type = fields.Selection([('new', 'Create New Customer'),('modify', 'Modify Existing Customer')], string="Request Type", default='new')
    change_summary = fields.Html(compute='_compute_change_summary', string="Changes Detected")
    change_summary_frozen = fields.Html(string="Approved Changes")

    def od_send_mail(self, template):
        ir_model_data = self.env['ir.model.data']
        email_obj = self.pool.get('email.template')
        if self.company_id.id == 6:
            template = template + '_saudi'
        template_id = ir_model_data.get_object_reference('beta_customer_registration', template)[1]
        rec_id = self.id
        email_obj.send_mail(self.env.cr, self.env.uid, template_id, rec_id, force_send=True)
        return True

    @api.one
    def action_submit(self):
        for record in self:
            if record.vat_id and record.company_id.id==6:
                if len(str(record.vat_id)) != 15:
                    raise Warning('Vat must be exactly 15 digits')
                if (str(record.vat_id)[0] != '3' or str(record.vat_id)[-1] != '3') and record.od_country_id.code == 'SA':
                    raise Warning('Vat must start/end with 3')
            # BR-KSA-65
            if record.od_additional_no and record.company_id.id==6:
                if len(str(record.od_additional_no)) != 4:
                    raise Warning('Secondary Number must be exactly 4 digits')
            # BR-KSA-67
            if record.od_country_id and record.od_country_id.code == 'SA' and len(str(record.od_zip)) != 5:
                raise Warning('Postal Code must be exactly 5 digits in case of SA')

        if self.registration_type == 'new':
            if self.related_partner_id:
                raise Warning("You firstly choose modify customer and load an existing customer details to create a new customer. This is not allowed.")
            self.od_send_mail('customer_registration_approval_manager')
        else:
            self.od_send_mail('customer_modify_approval_manager')
        return self.write({'state': 'confirm'})

    @api.one
    def action_approve(self):
        if self.env.user.id not in  [2137,154]:
            raise Warning("You are not authorized to approve this customer registration")
        part_obj = self.env['res.partner']
        if self.registration_type == 'new':

            self.od_send_mail('customer_registration_notify_manager')
            company = part_obj.create({
                'name': self.name,
                'street': self.od_street,
                'street2': self.od_street2,
                'state_id':  self.od_state_id and self.od_state_id.id,
                'user_id': self.user_id and self.user_id.id,
                'section_id': self.team_id and self.team_id.id,
                'od_industry_id': self.od_industry_id and self.od_industry_id.id,
                'city': self.od_state_id and self.od_state_id.name,
                'zip': self.od_zip,
                'country_id': self.od_country_id and self.od_country_id.id,
                'vat': self.vat_id,
                'od_class': self.od_class,
                'od_building_no': self.od_building_no,
                'od_additional_no': self.od_additional_no,
                'od_other_buyer_id': self.od_other_buyer_id,
                'od_cr_no': self.od_cr_no,
                'district': self.district,
                'buyer_identification': self.buyer_identification,
                'image_medium': self.image,
                'customer': True,
                'is_company': True,
                'website': self.website,
            })

            contact = part_obj.create({
                'name': self.contact_person,
                'function': self.function,
                'phone': self.phone,
                'mobile': self.mobile,
                'parent_id': company and company.id,
                'email': self.email,
                'customer': True,
                'use_parent_address': True,
                'type': 'contact'
            })
            return self.write({'state': 'validate', 'new_partner_id': company.id})
        elif self.registration_type == 'modify':
            if self.registration_type == 'modify':
                self.change_summary_frozen = self.change_summary
            self.related_partner_id.write({
                'name': self.name,
                'street': self.od_street,
                'street2': self.od_street2,
                'state_id': self.od_state_id and self.od_state_id.id,
                'user_id': self.user_id and self.user_id.id,
                'section_id': self.team_id and self.team_id.id,
                'od_industry_id': self.od_industry_id and self.od_industry_id.id,
                'city': self.od_state_id and self.od_state_id.name,
                'zip': self.od_zip,
                'country_id': self.od_country_id and self.od_country_id.id,
                'vat': self.vat_id,
                'od_class': self.od_class,
                'od_building_no': self.od_building_no,
                'od_additional_no': self.od_additional_no,
                'od_other_buyer_id': self.od_other_buyer_id,
                'od_cr_no': self.od_cr_no,
                'district': self.district,
                'buyer_identification': self.buyer_identification,
                'image_medium': self.image,
                'customer': True,
                'is_company': True,
                'website': self.website,
            })
            return self.write({'state': 'validate'})

        return None

    @api.one
    def action_refuse(self):
        if self.env.user.id not in  [2137,154]:
            raise Warning("You are not authorized to refuse this customer registration")
        self.od_send_mail('customer_registration_refused')
        return self.write({'state': 'refuse'})

    @api.one
    def action_reset_to_draft(self):
        return self.write({'state': 'draft'})

    @api.one
    @api.model
    def unlink(self):
        for rec in self:
            if rec.state == 'validate':
                raise Warning(_('You Cannot Delete An Approved Customer Registration Form.'))
        return super(BetaPartner, self).unlink()
