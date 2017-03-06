# -*- coding: utf-8 -*-
import werkzeug
import werkzeug.exceptions

NO_POSTMORTEM = ()

from ..root import request, _request_stack

class Web(object):
    _request_type = None
    
    def __init__(self, httprequest):
        self.httprequest = httprequest
        self.httpresponse = None
        #self.httpsession = httprequest.session
        self.gui = False
        if httprequest.path and httprequest.path.startswith('/gui'):
            if httprequest.remote_addr in ('localhost', '127.0.0.1'):
                self.gui = True
                httprequest.path = httprequest.path[4:] or '/'
                httprequest.environ['PATH_INFO'] = httprequest.path
        
    def __enter__(self):
        _request_stack.push(self)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        _request_stack.pop()

        #if self._cr:
        #    if exc_type is None and not self._failed:
        #        self._cr.commit()
        #    self._cr.close()
        # just to be sure no one tries to re-use the request
        #self.disable_db = True
        #self.uid = None

    def _handle_exception(self, exception):
        """Called within an except block to allow converting exceptions
           to abitrary responses. Anything returned (except None) will
           be used as response.""" 
        #self._failed = exception # prevent tx commit
        #if not isinstance(exception, NO_POSTMORTEM) \
        #        and not isinstance(exception, werkzeug.exceptions.HTTPException):
        #    manager.tools.debugger.post_mortem(manager.tools.config, sys.exc_info())
        raise

    def set_handler(self, endpoint, arguments, auth):
        # is this needed ?
        arguments = dict((k, v) for k, v in arguments.iteritems()
                         if not k.startswith("_ignored_"))

        self.endpoint_arguments = arguments
        self.endpoint = endpoint
        self.auth_method = auth

    def _call_function(self, *args, **kwargs):
        request = self
        if self.endpoint.routing['type'] != self._request_type:
            msg = "%s, %s: Function declared as capable of handling request of type '%s' but called with a request of type '%s'"
            params = (self.endpoint.original, self.httprequest.path, self.endpoint.routing['type'], self._request_type)
            _logger.info(msg, *params)
            raise werkzeug.exceptions.BadRequest(msg % params)

        if self.endpoint_arguments:
            kwargs.update(self.endpoint_arguments)

        # Correct exception handling and concurency retry
        #@service_model.check
        #def checked_call(___dbname, *a, **kw):
        #    # The decorator can call us more than once if there is an database error. In this
        #    # case, the request cursor is unusable. Rollback transaction to create a new one.
        #    if self._cr:
        #        self._cr.rollback()
        #        self.env.clear()
        #    result = self.endpoint(*a, **kw)
        #    if isinstance(result, Response) and result.is_qweb:
        #        # Early rendering of lazy responses to benefit from @service_model.check protection
        #        result.flatten()
        #    return result
        #
        #if self.db:
        #    return checked_call(self.db, *args, **kwargs)
        return self.endpoint(*args, **kwargs)

class SessionExpiredException(Exception):
    pass
