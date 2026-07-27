# -*- coding: utf-8 -*-
from openerp import models, fields, api, exceptions, _


class SlaReportWizard(models.TransientModel):
    """Wizard used to collect the parameters (organisation, date range)
    needed to generate the SLA report, and to trigger the generation of
    an Excel (.xlsx) file that is downloaded by the browser.
    """
    _name = 'sla.report.wizard'
    _description = 'SLA Report Wizard'

    organisation_id = fields.Many2one(
        comodel_name='res.partner',
        string='Customer',
        required=True,
        help='Organisation for which the SLA report will be generated. '
             'Tickets are matched against the od_organization_id field '
             'on crm.helpdesk.',
    )
    date_start = fields.Date(
        string='Start Date',
        required=True,
        default=fields.Date.context_today,
    )
    date_end = fields.Date(
        string='End Date',
        required=True,
        default=fields.Date.context_today,
    )

    @api.multi
    def _check_dates(self):
        """Basic sanity check on the chosen date range."""
        for wizard in self:
            if wizard.date_start and wizard.date_end \
                    and wizard.date_start > wizard.date_end:
                raise exceptions.ValidationError(
                    _('The start date cannot be later than the end date.')
                )

    @api.multi
    def get_report_data(self):
        """Fetch crm.helpdesk tickets matching this wizard's organisation
        (via od_organisation_id) and date range, and return the full data
        structure consumed by the xlsx generator.

        :return: dict with organisation name, counts, period and a list
                 of ticket line dicts.
        """
        self.ensure_one()
        helpdesk_obj = self.env['crm.helpdesk']

        domain = [
            ('od_organization_id', '=', self.organisation_id.id),
            ('create_date', '>=', self.date_start + ' 00:00:00'),
            ('create_date', '<=', self.date_end + ' 23:59:59'),
        ]

        tickets = helpdesk_obj.search(domain)

        total_count = len(tickets)
        closed_count = len(tickets.filtered(lambda t: t.state == 'done'))

        ticket_lines = []
        for ticket in tickets:
            status_label = dict(
                ticket._fields['state'].selection
            ).get(ticket.state, ticket.state or '')

            priority_label = ticket.priority or '-'
            if 'priority' in ticket._fields \
                    and ticket._fields['priority'].selection:
                priority_label = dict(
                    ticket._fields['priority'].selection
                ).get(ticket.priority, ticket.priority or '-')

            # Calculate hours difference between initiation and closing dates
            hours_difference = '-'

            # Debug: Print the values to see what's happening
            print("Initiation Date:", ticket.initiation_date)
            print("Actual Close Date:", ticket.actual_close_date)
            print("State:", ticket.state)

            # Check if both dates exist
            if ticket.initiation_date and ticket.actual_close_date:
                try:
                    # Convert to datetime objects
                    if isinstance(ticket.initiation_date, str):
                        initiation = fields.Datetime.from_string(ticket.initiation_date)
                    else:
                        initiation = ticket.initiation_date

                    if isinstance(ticket.actual_close_date, str):
                        closing = fields.Datetime.from_string(ticket.actual_close_date)
                    else:
                        closing = ticket.actual_close_date

                    # Calculate difference in hours
                    time_diff = closing - initiation
                    hours_difference = round(time_diff.total_seconds() / 3600.0, 2)

                    print("Time Difference in Hours:", hours_difference)

                except Exception as e:
                    print("Error calculating time difference:", str(e))
                    hours_difference = '-'
            else:
                print("One or both dates are missing or False")
                print("Initiation Date exists:", bool(ticket.initiation_date))
                print("Actual Close Date exists:", bool(ticket.actual_close_date))

            defined_response = ''
            if ticket.od_project_id2 and ticket.od_project_id2.od_cost_sheet_id:
                if ticket.priority == '0':
                    defined_response = str(ticket.od_project_id2.od_cost_sheet_id.od_resol_time_min)
                if ticket.priority == '1':
                    defined_response = str(ticket.od_project_id2.od_cost_sheet_id.od_resol_time_maj)
                if ticket.priority == '2':
                    defined_response = str(ticket.od_project_id2.od_cost_sheet_id.od_resol_time_ctc)

            ticket_lines.append({
                'sequence': ticket.od_number,
                'description': ticket.name or '',
                'status': status_label,
                'initiation_date': ticket.initiation_date,
                'closing_date': ticket.actual_close_date if ticket.date_closed else '-',
                'hours_difference': hours_difference,  # New column
                'defined_response': defined_response,  # New column 2
                'priority': priority_label,
                'project': ticket.od_project_id2.name,
            })

        return {
            'organisation_name': self.organisation_id.name or '',
            'total_count': total_count,
            'closed_count': closed_count,
            'date_start': self._format_date(self.date_start),
            'date_end': self._format_date(self.date_end),
            'ticket_lines': ticket_lines,
        }

    @api.model
    def _format_date(self, value):
        """Format a date/datetime string (YYYY-MM-DD[...]) to dd/mm/yyyy.
        Returns '-' for falsy values.
        """
        if not value:
            return '-'
        try:
            date_part = value[:10]
            year, month, day = date_part.split('-')
            return '%s/%s/%s' % (day, month, year)
        except Exception:
            return value

    @api.multi
    def action_generate_report(self):
        """Validate the wizard inputs and redirect the browser to the
        controller endpoint that streams the generated .xlsx file,
        triggering a download.
        """
        self.ensure_one()
        self._check_dates()

        return {
            'type': 'ir.actions.act_url',
            'url': '/bit_outsource_emp_expiry/xlsx/%s' % self.id,
            'target': 'self',
        }
