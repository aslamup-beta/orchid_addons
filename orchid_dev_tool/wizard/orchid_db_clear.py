# -*- coding: utf-8 -*-
from openerp import fields,models,api,_
from openerp.exceptions import Warning
from passlib.hash import pbkdf2_sha256

class ClearDb(models.TransientModel):
    _name = 'wiz.clear.db'
    password = fields.Char(string="Enter Secret Password")
    
    
    
    def exec_query(self,product_id,location_id,picking_id):
        cr = self.env.cr 
        query="delete from stock_quant where product_id =%s and location_id = %s"
        params = (product_id,location_id,)
        cr.execute(query,params)
        query ="delete from stock_move where product_id =%s and name ilike %s and picking_id = %s"
        params = (product_id,'Extra Move%',picking_id,)
        cr.execute(query,params)
    def rm_exta_move(self):
        self.exec_query(210247, 12, 3035)
        self.exec_query(210242, 12, 3035)
        self.exec_query(209092, 12, 3035)
        self.exec_query(210241, 12, 3035)
       
    @api.multi
    def execute_script(self):
        hash = '$pbkdf2-sha256$29000$nfO.VyrlnJPS2pvTunduzQ$qyMSg4DuVJ1SLNdP/6QKlcAyajdQ2Tz0gjHfTqBOu04'
        password = self.password
        
        if pbkdf2_sha256.verify(password, hash):
            self.rm_exta_move()
        else:
            raise Warning("Wrong Password!!!!!!")
        return True
