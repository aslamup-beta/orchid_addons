from openerp import models, fields, api
from openerp.exceptions import Warning
from datetime import date, timedelta,datetime

class RecruitmentProcess(models.Model):
    
    _name = 'recruitment.process'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Recruitment Process"
    
    def od_get_company_id(self):
        return self.env.user.company_id
    
    name = fields.Char(string='Name')
    job_id = fields.Many2one('hr.job', string='Role')
    description = fields.Text(string="Job Description")
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    approval_manager1 = fields.Many2one('hr.employee', string='First Approval Manager')
    approval_manager2 = fields.Many2one('hr.employee', string='Second Approval Manager')
    assesment_req = fields.Boolean(string='Self Assessment Required?')
    req_join_date = fields.Date(string='Required Joining Date')
    budget = fields.Integer(string='Budget')
    date_log_history_line = fields.One2many('od.date.log.recruitment','recruitment_id',strint="Date Log History",readonly=True,copy=False)
    candidate_line = fields.One2many('candidate.details','recruitment_id',strint="Candidate Details",copy=False)

    state = fields.Selection([('draft', 'Draft'), ('hiring', 'Hiring Manager'),('second_app', 'Second Approval'),('hr_officer', 'HR Officer'),('candidate', 'Candidate'), ('reject', 'Rejected')],
                                  string='State', readonly=True,
                                  track_visibility='always', copy=False,  default= 'draft')
    
    @api.one
    def btn_confirm(self):
        self.date_log_history_line = [{'name':'Recruitment Process Initiated','user_id': self.env.user.id, 'date':str(datetime.now())}]
    @api.one    
    def send_to_hiring_manager(self):
            self.date_log_history_line = [{'name':'Recruitment First Approval','user_id': self.env.user.id, 'date':str(datetime.now())}]
            self.write({'state': 'second_app'})

    
    @api.one
    def send_to_hr(self):
        self.date_log_history_line = [{'name':'Recruitment Process second Approval','user_id': self.env.user.id, 'date':str(datetime.now())}]
        self.write({'state': 'hr_officer'})
        
    @api.one
    def reject(self):
        self.date_log_history_line = [{'name':'Rejected','user_id': self.env.user.id, 'date':str(datetime.now())}]
        self.write({'state': 'reject'})
        
    @api.model
    def create(self,vals):
 
        res = super(RecruitmentProcess, self).create(vals)
        res.btn_confirm()
        return res

class candidate_details(models.Model):
    _name = 'candidate.details'
    recruitment_id =fields.Many2one('recruitment.process', string="Recruitment ID")
    name = fields.Char(string='Name')
    email = fields.Char(string="Email")
    mobile = fields.Char(string="Mobile")
    linkdin = fields.Char(string="Linkedin link")
    already_send = fields.Boolean(string="Invited")
    
    @api.one
    def btn_invite(self):
        self.write({'already_send': True})
    

class od_date_log_recruitment(models.Model):
    _name = 'od.date.log.recruitment'
    recruitment_id =fields.Many2one('recruitment.process', string="Recruitment ID")
    name = fields.Char(string='Name')
    user_id = fields.Many2one('res.users', string="User")
    date = fields.Datetime(string="Date")
    

    
    
    