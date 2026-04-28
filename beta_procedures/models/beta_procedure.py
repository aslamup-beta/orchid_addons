# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import Warning

class Procedures(models.Model):
    
    _name = 'beta.procedures'
    _description = "Beta Procedures"
    _order = 'sequence'
    
    def od_get_company_id(self):
        return self.env.user.company_id
    
    name = fields.Char('Name')
    image = fields.Binary(string='Attached Image')
    description = fields.Text()
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    sequence = fields.Integer('sequence', help="Sequence for the handle.",default=10)
    eng_video = fields.Char('English Video Training')
    arb_video = fields.Char('Arabic Video Training')
    
class Structures(models.Model):
    
    _name = 'beta.structures'
    _description = "Beta Company Structures"
    _order = 'sequence'
    
    def od_get_company_id(self):
        return self.env.user.company_id
    
    name = fields.Char('Name')
    image = fields.Binary(string='Attached Image')
    description = fields.Text()
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    sequence = fields.Integer('sequence', help="Sequence for the handle.",default=10)
    
class RoleDescription(models.Model):
    
    _name = 'role.description'
    _description = "Role Description"
    _order = 'sequence'
    
    def od_get_company_id(self):
        return self.env.user.company_id
    
    name = fields.Char('Name')
    image = fields.Binary(string='Attached Image')
    description = fields.Text()
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    sequence = fields.Integer('sequence', help="Sequence for the handle.",default=10)
    eng_video = fields.Char('English Video Training')
    arb_video = fields.Char('Arabic Video Training')
    
class BetaKPI(models.Model):
    
    _name = 'beta.kpi'
    _description = "Beta KPIs"
    _order = 'sequence'
    
    def od_get_company_id(self):
        return self.env.user.company_id
    
    name = fields.Char('Name')
    image = fields.Binary(string='Attached Image')
    description = fields.Text()
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    sequence = fields.Integer('sequence', help="Sequence for the handle.",default=10)
    eng_video = fields.Char('English Video Training')
    arb_video = fields.Char('Arabic Video Training')
    
class BetaDocs(models.Model):
    
    _name = 'beta.docs'
    _description = "Beta Documents"
    _order = 'sequence'
    
    def od_get_company_id(self):
        return self.env.user.company_id
    
    
    name = fields.Char('Reference')
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    attach_file = fields.Binary('Attach File')
    attach_fname = fields.Char('File Name')
    issue_date = fields.Date('Issue Date')
    expiry_date = fields.Date('Expiry Date')
    sequence = fields.Integer('sequence', help="Sequence for the handle.",default=10)

    
class BetaVideos(models.Model):
    
    _name = 'beta.videos'
    _description = "Beta Videos"
    _order = 'sequence'
    
    @api.one 
    @api.depends('url')
    def _get_link(self):
        self.url2 = self.url
    
    name = fields.Char('Reference')
    url = fields.Char('URL')
    url2 = fields.Char('Video Link',compute="_get_link")
    issue_date = fields.Date('Issue Date')
    expiry_date = fields.Date('Expiry Date')
    sequence = fields.Integer('sequence', help="Sequence for the handle.",default=10)

class SaleTmp(models.Model):
    
    _name = 'od.sale.temp'
    _description = "Template-Sales"
    _order = 'sequence'
    
    def od_get_company_id(self):
        return self.env.user.company_id
    
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    sequence = fields.Integer('sequence', help="Sequence for the handle.",default=10)    
    name1 = fields.Text('Template Name')
    temp1 = fields.Binary('Template')
    attach_fname = fields.Char('File Name')
    expiry_date = fields.Date('Expiry Date')
    
    
class PreSaleTmp(models.Model):
    
    _name = 'od.presale.temp'
    _description = "Template-PreSales"
    _order = 'sequence'
    
    def od_get_company_id(self):
        return self.env.user.company_id
    
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    sequence = fields.Integer('sequence', help="Sequence for the handle.",default=10)
    name2 = fields.Text('Template Name')
    temp2 = fields.Binary('Template')
    attach_fname = fields.Char('File Name')
    
class PostSaleTmp(models.Model):
    
    _name = 'od.postsale.temp'
    _description = "Template-PostSales"
    _order = 'sequence'
    
    def od_get_company_id(self):
        return self.env.user.company_id
    
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    sequence = fields.Integer('sequence', help="Sequence for the handle.",default=10)
    name3 = fields.Text('Template Name')
    temp3 = fields.Binary('Template')
    attach_fname = fields.Char('File Name')
    
class ServiceTmp(models.Model):
    
    _name = 'od.service.temp'
    _description = "Template-Services"
    _order = 'sequence'
    
    def od_get_company_id(self):
        return self.env.user.company_id
    
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    sequence = fields.Integer('sequence', help="Sequence for the handle.",default=10)
    name4 = fields.Text('Template Name')
    temp4 = fields.Binary('Template')
    attach_fname = fields.Char('File Name')
    
class ProjTmp(models.Model):
    
    _name = 'od.proj.temp'
    _description = "Template-Projects"
    _order = 'sequence'
    
    def od_get_company_id(self):
        return self.env.user.company_id
    
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    sequence = fields.Integer('sequence', help="Sequence for the handle.",default=10)
    name5 = fields.Text('Template Name')
    temp5 = fields.Binary('Template')
    attach_fname = fields.Char('File Name')
    
class HRTmp(models.Model):
    
    _name = 'od.hr.temp'
    _description = "Template-HR"
    _order = 'sequence'
    
    def od_get_company_id(self):
        return self.env.user.company_id
    
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    sequence = fields.Integer('sequence', help="Sequence for the handle.",default=10)
    name6 = fields.Text('Template Name')
    temp6 = fields.Binary('Template')
    attach_fname = fields.Char('File Name')
    
class MSPTmp(models.Model):
    
    _name = 'od.msp.temp'
    _description = "Template-MSP"
    _order = 'sequence'
    
    def od_get_company_id(self):
        return self.env.user.company_id
    
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    sequence = fields.Integer('sequence', help="Sequence for the handle.",default=10)
    name7 = fields.Text('Template Name')
    temp7 = fields.Binary('Template')
    attach_fname = fields.Char('File Name')
    
class GovernanceTmp(models.Model):
    
    _name = 'od.governance.temp'
    _description = "Company Governance"
    _order = 'sequence'
    
    def od_get_company_id(self):
        return self.env.user.company_id
    
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    sequence = fields.Integer('sequence', help="Sequence for the handle.",default=10)
    name8 = fields.Text('Template Name')
    temp8 = fields.Binary('Template')
    attach_fname = fields.Char('File Name')


class InfoSecTmp(models.Model):
    _name = 'od.infosec.temp'
    _description = "Template-InfoSec"
    _order = 'sequence'

    def od_get_company_id(self):
        return self.env.user.company_id

    company_id = fields.Many2one('res.company', string='Company', default=od_get_company_id)
    sequence = fields.Integer('sequence', help="Sequence for the handle.", default=10)
    name9 = fields.Text('Template Name')
    temp9 = fields.Binary('Template')
    attach_fname = fields.Char('File Name')
    expiry_date = fields.Date('Expiry Date')


class VendorManagementTmp(models.Model):
    _name = 'od.vendor.temp'
    _description = "Template-Vendor Management"
    _order = 'sequence'

    def od_get_company_id(self):
        return self.env.user.company_id

    company_id = fields.Many2one('res.company', string='Company', default=od_get_company_id)
    vendor_id = fields.Many2one('od.product.brand', string='Vendor')
    sequence = fields.Integer('sequence', help="Sequence for the handle.", default=10)
    name10 = fields.Text('Template Name')
    temp10 = fields.Binary('Template')
    attach_fname = fields.Char('File Name')
    expiry_date = fields.Date('Expiry Date')