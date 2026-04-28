import datetime
from openerp.osv import fields, osv
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from datetime import date
import time

class project_project(osv.osv):
    _inherit = "project.project"
    
    def planned_invoice_reminder(self, cr, uid, context=None):
        template = 'od_planned_invoice_reminder_email_template'
        ir_model_data = self.pool.get('ir.model.data')
        proj_obj = self.pool.get('project.project')
        user_obj = self.pool.get('res.users')
        company_id = user_obj.browse(cr, uid, uid, context=context).company_id.id
        if company_id == 6:
            template = template +'_saudi'
        template_id = ir_model_data.get_object_reference(cr,uid,'beta_customisation', template)[1]
        open_projects  = proj_obj.search(cr, uid, [('state','=','open')])
        for proj_id in open_projects:
            proj=proj_obj.browse(cr,uid,proj_id)
            today = datetime.date.today()
            for inv_line in proj.od_project_invoice_schedule_line:
                invoice_id = inv_line.invoice_id and inv_line.invoice_id.id or False
                if not invoice_id:
                    planned_date = inv_line.date
                    check_date = today + relativedelta(days=7)
                    target_date = check_date.strftime('%Y-%m-%d')
                    if target_date == planned_date:
                        self.pool.get('email.template').send_mail(cr, uid, template_id, proj_id, force_send=True, context=context)
        return True