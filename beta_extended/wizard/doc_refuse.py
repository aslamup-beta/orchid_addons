# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import Warning


class DocRefuseWizard(models.TransientModel):
    _name = 'doc.refuse.wiz'

    refuse_reason = fields.Text(string="Return with Comments")

    @api.one
    def button_confirm(self):
        context = self.env.context
        active_model = context.get('active_model')
        active_id = context.get('active_id')
        # write_data = context.get('write_data', False)
        # create_invoice = context.get('create_invoice', False)
        # method = context.get('method', False)
        active_obj = self.env[active_model].browse(active_id)
        # if write_data:
        active_obj.write({
            'refuse_reason': self.refuse_reason,
            'state': 'refused'
        })
        active_obj.od_send_mail('od_doc_request_refused_employee')

    @api.multi
    def button_cancel(self):
        return True
