# -*- coding: utf-8 -*-

from datetime import datetime, date, timedelta
from openerp import models, fields, api, _
from openerp.exceptions import Warning
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF, DEFAULT_SERVER_DATETIME_FORMAT


class CrmHelpdesk(models.Model):
    _inherit = "crm.helpdesk"

    initiation_date = fields.Datetime(string="Initiation Date")
    # actual_closing_date = fields.Datetime(string="Actual Closing Date")
    customer_email = fields.Binary(string="Customer Email")
    actual_close_date = fields.Datetime(
        string="Actual Close Date",
        compute='_compute_actual_close_date',
        store=True,
        help="Date when the helpdesk ticket was actually closed"
    )

    @api.depends('state', 'od_realtime_date_logs', 'od_realtime_date_logs.date')
    def _compute_actual_close_date(self):
        """
        Compute the actual close date from the date log entries.
        Only takes the date if the helpdesk state is 'done'.
        """
        for helpdesk in self:
            if helpdesk.state == 'done':
                # Get the latest date log entry (or the one that represents the close date)
                # Assuming you want the most recent date log entry
                date_log = self.env['od.helpdesk.date.log'].search([
                    ('hd_id', '=', helpdesk.id)
                ], order='date desc', limit=1)

                if date_log:
                    helpdesk.actual_close_date = date_log.date
                else:
                    helpdesk.actual_close_date = False
            else:
                helpdesk.actual_close_date = False
