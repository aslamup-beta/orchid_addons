# -*- coding: utf-8 -*-
import itertools
from lxml import etree
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning



class account_period(models.Model):
    _inherit = "account.period"

    @api.model
    def _default_sequence(self):
        sequences = self.search_read([], ['od_sequence'],order='od_sequence desc',limit=1)
        for seq in sequences:
            return seq and seq.get('od_sequence') and seq.get('od_sequence')+1
        return 1

    od_sequence = fields.Integer(string='Sequence', default=_default_sequence,
        help="Gives the sequence of this line when displaying the invoice.")
