from openerp import models, fields, api, _
import xmlrpclib
import re


class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.model
    def get_sanitized_tasks(self, domain=None, fields=None, rec_models=None):
        """Return task data with XML-sanitized text fields"""
        print("get_sanitized_tasks")
        print("get_sanitized_tasks,,,,,,,,,,,,,,,,,,,,,,, rec_models", rec_models)
        if domain is None:
            domain = []
        if fields is None:
            fields = ['name', 'description', 'user_id', 'date_deadline']  # Default fields

        records = self.env[rec_models].search(domain, order='id asc')
        result = []
        # hhh
        for record in records:
            record_data = {}
            for field in fields:
                value = getattr(record, field, False)
                print("value..................", type(value), value)

                # Handle different field types
                if field == 'user_id':
                    # For many2one fields, return ID and name as tuple
                    if value:
                        record_data[field] = (value.id, value.name)
                    else:
                        record_data[field] = False

                elif isinstance(value, (str, unicode)):
                    # Sanitize XML problematic characters in text fields
                    value = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', value)
                    value = value.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    record_data[field] = value

                elif isinstance(value, models.Model):
                    print("value1111111111", value, len(value))
                    # For other model fields, just return the ID

                    if len(value) > 1:
                        record_data[field] = [(rec.id, rec.name) for rec in value] if value else False
                    else:
                        record_data[field] = (value.id, value.name) if value else False
                    # record_data[field] = value.id if value else False

                elif isinstance(value, (list, tuple)):
                    print("value222222222222", value)
                    # For one2many or many2many fields, return list of IDs
                    record_data[field] = [rec.id for rec in value] if value else []
                    print("error on this loooooooooooop")

                else:
                    # For other types (int, float, bool, date, datetime)
                    record_data[field] = value

            # Convert to regular dict to avoid defaultdict issues
            result.append(dict(record_data))
        print("result,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,", len(result), result)
        return result

