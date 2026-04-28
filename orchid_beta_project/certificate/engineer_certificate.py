from openerp import models, fields, api
from openerp.exceptions import Warning
from datetime import datetime,date
class engineer_certificate(models.Model):
    _name = 'engineer.certificate'
    _order = 'id desc'
    
    def get_default_user_id(self):
        user_id = self.env.uid 
        return user_id
    
    def od_get_company_id(self):
        return self.env.user.company_id
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    
    user_id = fields.Many2one('res.users','Assigned By',default=get_default_user_id)
    brand_id = fields.Many2one('od.product.brand',string="Brand")
    name = fields.Char(string="Name")
    certificate_id = fields.Many2one('employee.certificate',string="Certificate")
    date = fields.Date(string="Date")
    month = fields.Selection([(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
                          (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'), 
                          (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December'), ], 
                          string='Month')
    
    attendees_ids = fields.One2many('engineer.certificate.attendees','engineer_cert_id',string="Attendees")
    clear_attendees_ids = fields.One2many('engineer.certificate.clear.attendees','engineer_cert_id',string="Attendees")
    state =fields.Selection([('draft','Draft'),('assigned','Assigned'),('in_progress','In Progress'),('done','Done')],string="Status",default='draft')
    allow_same_mnth = fields.Boolean(string="Allow Assigning Same month")
    
    def get_employee(self,user_id):
        employee = self.env['hr.employee']
        employee_dat= employee.search([('user_id','=',user_id)],limit=1)
        return employee_dat
    
    def update_employee_cert(self):
        month = self.month
        d = date.today()
        d_month = d.month
        allow_same_mnth = self.allow_same_mnth
        if not allow_same_mnth:
            if month == d_month:
                raise Warning("You Can Only Assign Certificates on Future Months")
        engineer_cert_id = self.id
        certificate_id = self.certificate_id and self.certificate_id.id or False
        brand_id = self.brand_id and self.brand_id.id or False
        for line in self.attendees_ids:
            user_id = line.user_id and line.user_id.id
            employee = self.sudo().get_employee(user_id)
#             eval('self'+'.'+'aud_date_start'+str(ex_num))
            cert_req = 'cert'+str(month)
            engineer_cert='engineer_cert_id'+str(month)
            certificate = 'cert_id'+ str(month)
            brand ='brand_id'+str(month)
            cert_status='cert_status'+str(month)
            stat = line.status
            line.status = 'assigned'
            if eval('employee.'+certificate):
                raise Warning("Certificate already Assigned, Kindly Remove this Employee %s or Clear His Certificate From this Month"%line.user_id.name)
            else:
                employee.write({engineer_cert:engineer_cert_id,cert_req:True,certificate:certificate_id,brand:brand_id,cert_status:stat})
    
    
    def od_send_mail(self,template,context):
        ir_model_data = self.env['ir.model.data']
        email_obj = self.pool.get('email.template')
        saudi_comp =6
        emp_company_id = self.company_id.id
        if emp_company_id == saudi_comp:
            template = template +'_saudi'
        template_id = ir_model_data.get_object_reference('orchid_beta_project', template)[1]
        crm_id = self.id
        email_obj.send_mail(self.env.cr, self.env.uid, template_id,crm_id,context)
        return True
    
    @api.one
    def send_mail_to_attendies(self):
        context = self.env.context
        attendies_email = []
        for line in self.attendees_ids:
            email = line.user_id and line.user_id.email
            attendies_email.append(email)
        attendies_emails = str(",".join(filter(None,attendies_email)))
        context =  context.copy()
        context['attendies_emails'] = attendies_emails
        print context,"1"*88
        if attendies_emails:
            self.od_send_mail('od_engineer_certificate_email_to_attendies',context=context)
        return True
    
    @api.one
    def btn_confirm(self):
        self.sudo().update_employee_cert()
        self.send_mail_to_attendies()
        self.write({'state':'in_progress'})
        
    @api.model
    def create(self,vals):
        res = super(engineer_certificate, self).create(vals)
        res.btn_confirm()
        return res
    
    
    @api.one
    def btn_reset_draft(self):
        self.write({'state':'draft'})
    
    @api.one
    def btn_done(self):
        self.write({'state':'done'})
    
    @api.one
    def btn_reset_progress(self):
        self.write({'state':'in_progress'})
        
    
    

class engineer_certificate_attendees(models.Model):
    _name ='engineer.certificate.attendees'
    engineer_cert_id = fields.Many2one('engineer.certificate',string="Sale Cert",ondelete="cascade")
    user_id = fields.Many2one('res.users',string="Engineer")
    status = fields.Selection([('not_achieved','Not Achieved'),('assigned','Assigned'),('waiting','Waiting For Confirmation'),('achieved','Achieved')],string="Status",default='not_achieved')
    
    def get_employee(self,user_id):
        employee = self.env['hr.employee']
        employee_dat= employee.search([('user_id','=',user_id)],limit=1)
        return employee_dat
    @api.one 
    def btn_confirm(self):
        self.write({'status':'achieved'})
        user_id = self.user_id and self.user_id.id or False
        employee = self.sudo().get_employee(user_id)
        month = self.engineer_cert_id and self.engineer_cert_id.month 
        cert_stat ='cert_status'+ str(month)
        employee.sudo().write({cert_stat:'achieved'})


class engineer_certificate_clear_attendees(models.Model):
    _name ='engineer.certificate.clear.attendees'
    engineer_cert_id = fields.Many2one('engineer.certificate',string="Sale Cert",ondelete="cascade")
    user_id = fields.Many2one('res.users',string="SAM")
    certificate_id = fields.Many2one('employee.certificate',string="Certificate")
    status = fields.Selection([('draft','Draft'),('cleared','Cleared')],string="Status",default='draft')
    
     
    def get_employee(self,user_id):
        employee = self.env['hr.employee']
        employee_dat= employee.search([('user_id','=',user_id)],limit=1)
        return employee_dat
    
    @api.one
    def btn_clear(self):
        self.write({'status':'cleared'})
        user_id = self.user_id and self.user_id.id or False
        employee = self.sudo().get_employee(user_id)
        month = self.engineer_cert_id and self.engineer_cert_id.month 
        cert_stat ='cert_status'+ str(month)
        cert_req = 'cert'+str(month)
        eng_cert='engineer_cert_id'+str(month)
        certificate = 'cert_id'+ str(month)
        brand ='brand_id'+str(month)
        employee.sudo().write({cert_stat:False,cert_req:False,eng_cert:False,certificate:False,brand:False})


