
from openerp.http import request, serialize_exception as _serialize_exception
from openerp.addons.web.controllers.main import Session
class Session(Session):

    def session_info(self):
        request.session.ensure_valid()
        return {
            "session_id": request.session_id,
            "uid": request.session.uid,
            "user_context": request.session.get_context() if request.session.uid else {},
            "db": request.session.db,
            "username": request.session.login,
            "company_id": request.env.user.company_id.id if request.session.uid else None,
            "allow_quick_create":request.env.user.allow_quick_create or False,
        }
