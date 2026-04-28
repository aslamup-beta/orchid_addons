# -*- coding: utf-8 -*-
from openerp import fields, models, api
from openerp.exceptions import Warning


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def write(self, cr, uid, ids, values, context=None):
        
        
        res = super(ResPartner, self).write(cr, uid, ids, values, context=context)
        # BR-KSA-40
        recs = self.browse(cr, uid, ids, context)
        for record in recs:
            if record.vat and record.company_id.id==6:
                if len(str(record.vat)) != 15:
                    raise Warning('Vat must be exactly 15 digits')
                if (str(record.vat)[0] != '3' or str(record.vat)[-1] != '3') and record.country_id.code == 'SA':
                    raise Warning('Vat must start/end with 3')
            # BR-KSA-65
            if record.od_additional_no and record.company_id.id==6:
                if len(str(record.od_additional_no)) != 4:
                    raise Warning('Additional Number must be exactly 4 digits')
            # BR-KSA-67 
            if record.country_id and record.country_id.code == 'SA' and len(str(record.zip)) != 5:
                raise Warning('ZIP must be exactly 5 digits in case of SA')
        return res
