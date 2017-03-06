import collections
import functools
import inspect
import logging
import os
import werkzeug.exceptions
import werkzeug.wrappers

from ..response import Response
from ..root import request

routers_per_module = collections.defaultdict(list)
_logger = logging.getLogger(__name__)

class RouterType(type):
    def __init__(cls, name, bases, attrs):
        super(RouterType, cls).__init__(name, bases, attrs)

        for k, v in attrs.items():
            if inspect.isfunction(v) and hasattr(v, 'original_func'):
                # Set routing type on original functions
                routing_type = v.routing.get('type')
                parent = [claz for claz in bases if isinstance(claz, RouterType) and hasattr(claz, k)]
                parent_routing_type = getattr(parent[0], k).original_func.routing_type if parent else routing_type or 'http'
                if routing_type is not None and routing_type is not parent_routing_type:
                    routing_type = parent_routing_type
                    _logger.warn("Subclass re-defines <function %s.%s.%s> with different type than original."
                                    " Will use original type: %r" % (cls.__module__, cls.__name__, k, parent_routing_type))
                v.original_func.routing_type = routing_type or parent_routing_type

        # store the Router in the Routers list
        name_class = ("%s.%s" % (cls.__module__, cls.__name__), cls)
        class_path = name_class[0].split(".")
        if not class_path[:2] == ["manager", "module"]:
            module = ""
        else:
            # we want to know all modules that have Routers
            module = class_path[2]
        # but we only store Routers directly inheriting from Router
        if not "Router" in globals() or not Router in bases:
            return
        routers_per_module[module].append(name_class)

class Router(object):
    __metaclass__ = RouterType

def route(route=None, **kw):
    """Decorator marking the decorated method as being a handler for
    requests. The method must be part of a subclass of ``Controller``.

    :param route: string or array. The route part that will determine which
                  http requests will match the decorated method. Can be a
                  single string or an array of strings. See werkzeug's routing
                  documentation for the format of route expression (
                  http://werkzeug.pocoo.org/docs/routing/ ).
    :param type: The type of request, can be ``'http'`` or ``'json'``, default to``'http'``.
    :param auth: The type of authentication method, can on of the following:

                 * ``user``: The user must be authenticated and the current request
                   will perform using the rights of the user.
                 * ``public``: The user may or may not be authenticated. If she isn't,
                   the current request will perform using the shared Public user.
                 * ``none``: The method is always active, even if there is no
                   database. Mainly used by the framework and authentication
                   modules. There request code will not have any facilities to access
                   the database nor have any configuration indicating the current
                   database nor the current user.
    :param install: The availlability of the route when PiManager not installed:
    
                 * True: Only availlable on installation mode
                 * False: Not availlable on installation mode
                 * 'Both': Allways availlable
    :param methods: A sequence of http methods this route applies to. If not
                    specified, all methods are allowed.
    :param cors: The Access-Control-Allow-Origin cors directive value.
    :param bool csrf: Whether CSRF protection should be enabled for the route.

                      Defaults to ``True``. See :ref:`CSRF Protection
                      <csrf>` for more.

    .. _csrf:

    .. admonition:: CSRF Protection
        :class: alert-warning

        .. versionadded:: 9.0

        PiManager implements token-based `CSRF protection
        <https://en.wikipedia.org/wiki/CSRF>`_.

        CSRF protection is enabled by default and applies to *UNSAFE*
        HTTP methods as defined by :rfc:`7231` (all methods other than
        ``GET``, ``HEAD``, ``TRACE`` and ``OPTIONS``).

        CSRF protection is implemented by checking requests using
        unsafe methods for a value called ``csrf_token`` as part of
        the request's form data. That value is removed from the form
        as part of the validation and does not have to be taken in
        account by your own form processing.

        When adding a new controller for an unsafe method (mostly POST
        for e.g. forms):

        * if the form is generated in Python, a csrf token is
          available via :meth:`request.csrf_token()
          <pimanager.request.base.Request.csrf_token`, the
          :data:`~pimanager.request` object is available by default
          in templates, it may have to be added
          explicitly if you are not using templates.

        * if the form is generated in Javascript, the CSRF token is
          added by default to the template (js) rendering context as
          ``csrf_token`` and is otherwise available as ``csrf_token``
          on the ``pimanager.core`` module:

          .. code-block:: javascript

              require('pimanager.core').csrf_token

        * if the endpoint can be called by external parties (not from
          pimanager) as e.g. it is a REST API or a `webhook
          <https://en.wikipedia.org/wiki/Webhook>`_, CSRF protection
          must be disabled on the endpoint. If possible, you may want
          to implement other methods of request validation (to ensure
          it is not called by an unrelated third-party).

    """
    
    routing = kw.copy()
    
    assert 'type' not in routing or routing['type'] in ("http", "json")
    assert 'install' not in routing or routing['install'] in (True, False, 'Both')
    
    def decorator(f):
        if route:
            if isinstance(route, list):
                routes = route
            else:
                routes = [route]
                
            routing['routes'] = routes
            
        @functools.wraps(f)
        def response_wrap(*args, **kw):
            response = f(*args, **kw)
            
            if isinstance(response, Response) or f.routing_type == 'json':
                return response

            if isinstance(response, basestring):
                return Response(response)

            if isinstance(response, werkzeug.exceptions.HTTPException):
                response = response.get_response(request.httprequest.environ)
                
            if isinstance(response, werkzeug.wrappers.BaseResponse):
                response = Response.force_type(response)
                response.set_default()
                return response

            _logger.warn("<function %s.%s> returns an invalid response type for an http request" % (f.__module__, f.__name__))
            
            return response
        
        response_wrap.routing = routing
        response_wrap.original_func = f
        return response_wrap
    
    return decorator

class BaseRouter(Router):
    @route('/', auth="none")
    def index(self, r=None):
        return "ok" #request.redirect('/installation')