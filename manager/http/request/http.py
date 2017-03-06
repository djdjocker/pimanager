# -*- coding: utf-8 -*-
import logging
import werkzeug.exceptions

from ..root import request
from ..response import Response
from .web import Web, SessionExpiredException

_logger = logging.getLogger(__name__)

class Http(Web):
    _request_type = "http"
    
    def __init__(self, *args):
        super(Http, self).__init__(*args)
        params = self.httprequest.args.to_dict()
        params.update(self.httprequest.form.to_dict())
        params.update(self.httprequest.files.to_dict())
        params.pop('session_id', None)
        self.params = params

    def _handle_exception(self, exception):
        """Called within an except block to allow converting exceptions
           to abitrary responses. Anything returned (except None) will
           be used as response."""
        try:
            return super(Http, self)._handle_exception(exception)
        except SessionExpiredException:
            redirect = None
            req = request.httprequest
            if req.method == 'POST':
                request.session.save_request_data()
                redirect = '/web/proxy/post{r.path}?{r.query_string}'.format(r=req)
            elif not request.params.get('noredirect'):
                redirect = req.url
            if redirect:
                query = werkzeug.urls.url_encode({
                    'redirect': redirect,
                })
                return werkzeug.utils.redirect('/web/login?%s' % query)
        except werkzeug.exceptions.HTTPException, e:
            print e
            return e
        except Exception, e:
            print e
            raise

    def dispatch(self):
        if request.httprequest.method == 'OPTIONS' and request.endpoint and request.endpoint.routing.get('cors'):
            headers = {
                'Access-Control-Max-Age': 60 * 60 * 24,
                'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept'
            }
            return Response(status=200, headers=headers)

        #if request.httprequest.method not in ('GET', 'HEAD', 'OPTIONS', 'TRACE') \
        #        and request.endpoint.routing.get('csrf', True): # csrf checked by default
        #    token = self.params.pop('csrf_token', None)
        #    if not self.validate_csrf(token):
        #        if token is not None:
        #            _logger.warn("CSRF validation failed on path '%s'",
        #                         request.httprequest.path)
        #        else:
        #            _logger.warn("""No CSRF validation token provided for path '%s'
        #
        #            pycms URLs are CSRF-protected by default (when accessed with unsafe
        #            HTTP methods). See
        #            https://www.pycms.com/documentation/9.0/reference/http.html#csrf for
        #            more details.
        #
        #            * if this endpoint is accessed through pycms via py-QWeb form, embed a CSRF
        #              token in the form, Tokens are available via `request.csrf_token()`
        #              can be provided through a hidden input and must be POST-ed named
        #              `csrf_token` e.g. in your form add:
        #
        #                  <input type="hidden" name="csrf_token" t-att-value="request.csrf_token()"/>
        #
        #            * if the form is generated or posted in javascript, the token value is
        #              available as `csrf_token` on `web.core` and as the `csrf_token`
        #              value in the default js-qweb execution context
        #
        #            * if the form is accessed by an external third party (e.g. REST API
        #              endpoint, payment gateway callback) you will need to disable CSRF
        #              protection (and implement your own protection if necessary) by
        #              passing the `csrf=False` parameter to the `route` decorator.
        #            """, request.httprequest.path)
        #
        #        raise werkzeug.exceptions.BadRequest('Invalid CSRF Token')

        r = self._call_function(**self.params)
        if not r:
            r = Response(status=204)  # no content
        return r

