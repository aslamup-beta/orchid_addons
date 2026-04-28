
from openerp import models, fields, api
from openerp.exceptions import Warning
import datetime
from datetime import date
import time
from dateutil.relativedelta import relativedelta


class FinanceDocuments(models.Model):
    
    _name = 'od.finance.doc'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Finance Documents"
    _order = 'sequence'
    
    def od_get_company_id(self):
        return self.env.user.company_id
    
    @api.one
    def _od_attachement_count(self):
        for obj in self:
            attachement_ids = self.env['od.attachement'].search([('model_name', '=', self._name),('object_id','=',obj.id)])
            if attachement_ids:
                self.od_attachement_count = len(attachement_ids)
    
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    sequence = fields.Integer('sequence', help="Sequence for the handle.",default=10)
    name = fields.Char('Document Name')
    issue_date = fields.Date('Issue Date')
    expiry_date = fields.Date('Expiry Date')
    od_attachement_count = fields.Integer(string="Attachement Count",compute="_od_attachement_count")
    notes = fields.Text("Notes")
    
    def od_open_attachement(self,cr,uid,ids,context=None):

        model_name=self._name
        object_id = ids[0]
        domain = [('model_name','=',model_name),('object_id','=',object_id)]
        ctx = {'default_model_name':model_name,'default_object_id':object_id}
        return {
            'domain': domain,
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'od.attachement',
            'type': 'ir.actions.act_window',
            'context':ctx
                }
        
    def fin_doc_expiry_date_reminder(self, cr, uid, context=None):
        today = date.today()
        context = dict(context or {})
        template = 'od_fin_doc_expiry_date'
        template_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'beta_procedures', template)[1]
        doc_ids= self.search(cr, uid, [],context=context)
        for doc in self.browse(cr,uid,doc_ids):
            doc_end_date = doc.expiry_date
            date_after_30_days = today + relativedelta(months=1)
            print "date_after_30_days", date_after_30_days
            if doc_end_date == str(date_after_30_days):
                self.pool.get('email.template').send_mail(cr, uid, template_id, doc.id, force_send=False, context=context)
        return True
    
class SaleTmp(models.Model):
    
    _inherit = 'od.sale.temp'
    
    def ksa_govt_doc_expiry_date_reminder_same_day(self, cr, uid, context=None):
        today = date.today()
        context = dict(context or {})
        template_id = 357
        doc_ids= self.search(cr, uid, [('company_id','=', 6)],context=context)
        for doc in self.browse(cr,uid,doc_ids):
            expiry_date = doc.expiry_date
#             today = datetime.datetime.strptime(today, "%Y-%m-%d").date()
            if expiry_date == str(today):
                self.pool.get('email.template').send_mail(cr, uid, template_id, doc.id, force_send=False, context=context)
        return True
    
    def ksa_govt_doc_expiry_date_reminder_30_days(self, cr, uid, context=None):
        today = date.today()
        context = dict(context or {})
        template_id = 356
        doc_ids= self.search(cr, uid, [('company_id','=', 6)],context=context)
        for doc in self.browse(cr,uid,doc_ids):
            expiry_date = doc.expiry_date
            date_after_30_days = today + relativedelta(months=1)
            if expiry_date == str(date_after_30_days):
                self.pool.get('email.template').send_mail(cr, uid, template_id, doc.id, force_send=False, context=context)
        return True
