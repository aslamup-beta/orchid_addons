# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
from openerp.tools.translate import _
class ir_ui_view(osv.osv):
    _inherit = 'ir.ui.view'
    _columns = {
        'model': fields.char('Model',required=True)
    }
    def add_button(self,cr,uid,ids,context=None):
        ir_model_data_obj = self.pool.get('ir.model.data')
        obj = self.browse(cr,uid,ids,context=context)
        name = obj.name
        model = obj.model
        org_name = name.split('.')
        org_name = org_name[0]
        if org_name:
            ir_actions_report_xml_ids = self.pool.get('ir.actions.report.xml').search(cr, uid, [('report_name', 'ilike', org_name),('model','=',model)])
        else:
            ir_actions_report_xml_ids = self.pool.get('ir.actions.report.xml').search(cr, uid, [('report_name', 'ilike', name),('model','=',model)])
        ir_actions_report_xml_data = self.pool.get('ir.actions.report.xml').browse(cr, uid, ir_actions_report_xml_ids, context=context)
        report_name = ir_actions_report_xml_data.report_name
        words = []
        words = report_name.split('.')
        module_name = ''
        module_name = words[0]
        if name:
            model_data_id = ir_model_data_obj.create(cr, uid,{
                            'res_id':ids[0],
                            'complete_name': name,
                            'name':name,
                            'model':'ir.ui.view',
                            'module':module_name
                        
                            })
            self.write(cr, uid,ids[0],{'model_data_id':model_data_id})
        return True








































