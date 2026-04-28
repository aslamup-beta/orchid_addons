# -*- coding: utf-8 -*-
from openerp import models, fields, api
from pprint import pprint
from datetime import datetime
import openerp.addons.decimal_precision as dp

import os
import csv
import tempfile
import base64


class import_csv(models.TransientModel):
    _name = 'import.csv.wiz'
    
    file_data = fields.Binary('File', required=True,)
    file_name = fields.Char('File Name',default="ImportFile.csv")
    
    @api.multi
    def update(self):
        cr = self.env.cr
        file_name = self.file_name
        file_path = tempfile.gettempdir()+'/'+file_name
        data = self.file_data
        f = open(file_path,'wb')
        f.write(base64.b64decode(data))
        f.close() 
#         archive = csv.DictReader(open(file_path))
#         for line in archive:
#             cr.execute("UPDATE account_move_line set od_branch_id=%s where id=%s",(line.get('Branch/ID'),line.get('ID')))
#             