# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from datetime import datetime

class stock_transfer_details_items(models.TransientModel):
    _inherit = 'stock.transfer_details_items'

    @api.multi
    def multi_split_quantities(self):
        for det in self:
            if det.quantity>1:
                qty= det.quantity
                for num in range(1,int(qty)):
                    det.quantity = 1
                    new_id = det.copy(context=self.env.context)
                    new_id.quantity = 1
                    new_id.packop_id = False

        if self and self[0]:
            return self[0].transfer_id.wizard_view()
