# -*- coding: utf-8 -*-
from openerp import fields,models,api,_
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
class od_document_request(models.Model):
    _inherit = 'od.document.request'
    _od_status = [('softcopy','Soft Copy Attached'),('hardcopy','Hard Copy Given'),('pending','Pending')]

    @api.one
    @api.depends('create_date')
    def od_get_year(self):
        if self.create_date:
            create_date = self.create_date
            create_date = datetime.strptime(create_date, DEFAULT_SERVER_DATETIME_FORMAT)
            year = create_date.year
            self.od_year = year
    status = fields.Selection(_od_status,string="HR Status")
    od_year = fields.Integer(string="Year",compute="od_get_year")
