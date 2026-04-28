from openerp.osv import fields, osv

class survey_survey(osv.Model):

    _inherit = 'survey.survey'
    
    def _get_default_company(self, cr, uid, context=None):
            
            company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
            if not company_id:
                raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
            return company_id
    _columns={ 
    'company_id': fields.many2one('res.company','Company'),
    }
    _defaults ={
        'company_id': _get_default_company,
    }


class survey_user_input(osv.Model):
    ''' Metadata for a set of one user's answers to a particular survey '''
    _inherit = "survey.user_input"
    
    def _get_default_company(self, cr, uid, context=None):
            company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
            if not company_id:
                raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
            return company_id
    _columns={ 
    'company_id': fields.many2one('res.company','Company'),
    }
    _defaults ={
        'company_id': _get_default_company,
    }
