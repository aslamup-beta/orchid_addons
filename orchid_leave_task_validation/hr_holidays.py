from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from datetime import datetime
class hr_holidays(models.Model):
    _inherit = "hr.holidays"
    od_hr_employee_event_line = fields.One2many('od.hr.employee.event.line','holiday_id',copy=False,readonly=True)
    od_event = fields.Boolean(string='Event')
    od_warning = fields.Text(string='Warning',readonly=True)
    od_warn2 = fields.Text(string='Warning2',readonly=True,compute='check_legal_leave')

    @api.one
    @api.depends('date_from','number_of_days_temp','od_leave_encashment')
    def check_legal_leave(self):
        od_leave_encashment = self.od_leave_encashment
        company_id = self.company_id and self.company_id.id or False
        if self.holiday_status_id.id == 1 and not od_leave_encashment:
            create_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

#            create_date =datetime.strptime(self.create_date, '%Y-%m-%d %H:%M:%S') #wrong code done by @jm
            create_date =datetime.strptime(create_date, '%Y-%m-%d %H:%M:%S')
            if self.date_from:
                date_from =datetime.strptime(self.date_from, '%Y-%m-%d %H:%M:%S')
                delta = date_from - create_date
                no_of_days = self.number_of_days_temp
                if no_of_days > 19 and delta.days < 180 and company_id == 1:
                    self.od_warn2 =  "Short Notice!!! \n All leaves above 19 days should be applied at least 180 days in advance"
                elif no_of_days > 12 and delta.days < 90 and company_id== 1:
                    self.od_warn2 = "Short Notice!!! \n All leaves above 12 days should be applied at least 90 days in advance"
                elif no_of_days > 5 and delta.days < 45 and company_id == 1:
                    self.od_warn2 =  "Short Notice!!! \n All leaves above 5 days should be applied at least 45 days in advance"

    @api.one
    @api.depends('date_from','date_to','employee_id')
    def check_event(self):
        event_line = self.env['od.hr.employee.event.line']
        partner_id =self.employee_id and self.employee_id.address_home_id and self.employee_id.address_home_id.id
        if not partner_id:
            raise Warning('Please Set Home address Of this Employee in Employee Master')
        meeting_ids =  self.employee_id and self.employee_id.address_home_id and self.employee_id.address_home_id.meeting_ids
        date_from = self.date_from[:10]
        date_to = self.date_to[:10]
        meet_ids =[]
        for meet in meeting_ids:
            if meet.start_date >= date_from and meet.start_date <= date_to:
                meet_ids.append({'id':meet.id,'name':meet.name,'start_date':meet.start_date,'stop_date':meet.stop_date})
            if meet.stop_date <= date_to and meet.stop_date > date_from:
                meet_ids.append({'id':meet.id,'name':meet.name,'start_date':meet.start_date,'stop_date':meet.stop_date})
        meets = [dict(t) for t in set([tuple(d.items()) for d in meet_ids])]
        if len(meets) >= 1:
            event_line.search([('holiday_id','=',self.id)]).unlink()
            self.od_event = True
            self.od_warning = 'Warning !!! \n Employee Is an Attendee of Following Events'
            for val in meets:
                val.update({'holiday_id':self.id})
                event_line.create(val)


class od_hr_employee_event_line(models.Model):
    _name = 'od.hr.employee.event.line'
    name = fields.Char('Event')
    holiday_id = fields.Many2one('hr.holidays','Holidays')
    start_date = fields.Date(string='Start Date')
    stop_date = fields.Date(string='Stop Date')
