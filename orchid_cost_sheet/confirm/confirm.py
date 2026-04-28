# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import Warning
class ConfirmPopup(models.TransientModel):
    _name = 'gen.wiz.confirm'

    
    @api.one
    def button_confirm(self):
        context = self.env.context
        active_model = context.get('active_model')
        active_id =context.get('active_id')
        write_data = context.get('write_data',False)
        create_invoice = context.get('create_invoice',False)
        method =context.get('method',False)
        active_obj =self.env[active_model].browse(active_id)
        if write_data:
            active_obj.write(write_data)
        elif create_invoice:
           
            active_obj.create_invoice()
        elif method:
            func = getattr(active_obj, method)
            func()
    @api.multi
    def button_cancel(self):
        return True
    
    
class ConfirmDesignReady(models.TransientModel):
    _name = 'gen.wiz.confirm.design.ready'

    
    @api.one
    def button_confirm(self):
        context = self.env.context
        active_model = context.get('active_model')
        active_id =context.get('active_id')
        write_data = context.get('write_data',False)
        create_invoice = context.get('create_invoice',False)
        method =context.get('method',False)
        active_obj =self.env[active_model].browse(active_id)
        if write_data:
            active_obj.write(write_data)
        elif create_invoice:
           
            active_obj.create_invoice()
        elif method:
            func = getattr(active_obj, method)
            func()
    @api.multi
    def button_cancel(self):
        return True
    