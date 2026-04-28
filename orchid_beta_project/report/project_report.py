# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
from openerp import tools

class report_project_task_user(osv.osv):
    _inherit = 'report.project.task.user'
    _columns = {
        'date_deadline':fields.date('Deadline', readonly=True),
    }
