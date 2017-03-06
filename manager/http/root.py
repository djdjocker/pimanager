# -*- coding: utf-8 -*-
import collections
import inspect
import logging
import manager
import os
import urlparse
import werkzeug
import werkzeug.local
import werkzeug.wsgi
import werkzeug.wrappers

_request_stack = werkzeug.local.LocalStack()

request = _request_stack()

from .route import *
from manager.tools.func import lazy_property
from request import Http, request
from route import routers_per_module

_logger = logging.getLogger(__name__)
# 1 week cache for statics as advised by Google Page Speed
STATIC_CACHE = 60 * 60 * 24 * 7


class Root(object):
    def __init__(self):
        self._loaded = False
    
    def __call__(self, environ, start_response):
        """ Handle a WSGI request
        """
        if not self._loaded:
            self._loaded = True
            self.load_addons()
        return self.dispatch(environ, start_response)

    def load_addons(self):
        self._loaded = True
        statics = {'/static': os.path.join(os.path.dirname(manager.__file__), 'static')}
        
        if statics:
            _logger.info("HTTP Configuring static files")
        app = werkzeug.wsgi.SharedDataMiddleware(self.dispatch, statics, cache_timeout=STATIC_CACHE)
        self.dispatch = DisableCacheOnDebug(app)
    
    def dispatch(self, environ, start_response):
        try:
            httprequest = werkzeug.wrappers.Request(environ)
            httprequest.app = self

            #explicit_session = self.setup_session(httprequest)
            #self.setup_db(httprequest)
            #self.setup_lang(httprequest)

            request = self.get_request(httprequest)

            def _dispatch_nodb():
                try:
                    func, arguments = self.nodb_routing_map.bind_to_environ(request.httprequest.environ).match()
                except werkzeug.exceptions.HTTPException, e:
                    return request._handle_exception(e)
                request.set_handler(func, arguments, "none")
                result = request.dispatch()
                return result

            with request:
                #db = request.session.db
                #if db:
                #    pycms.modules.registry.RegistryManager.check_registry_signaling(db)
                #    try:
                #        with pycms.tools.mute_logger('pycms.sql_db'):
                #            ir_http = request.registry['ir.http']
                #    except (AttributeError, psycopg2.OperationalError, psycopg2.ProgrammingError):
                        # psycopg2 error or attribute error while constructing
                        # the registry. That means either
                        # - the database probably does not exists anymore
                        # - the database is corrupted
                        # - the database version doesnt match the server version
                        # Log the user out and fall back to nodb
                #        request.session.logout()
                        # If requesting /web this will loop
                #        if request.httprequest.path == '/web':
                #            result = werkzeug.utils.redirect('/web/database/selector')
                #        else:
                #            result = _dispatch_nodb()
                #    else:
                #        result = ir_http._dispatch()
                #        pycms.modules.registry.RegistryManager.signal_caches_change(db)
                #else:
                result = _dispatch_nodb()

                response = self.get_response(httprequest, result)#, explicit_session)
            return response(environ, start_response)

        except werkzeug.exceptions.HTTPException, e:
            return e(environ, start_response)

    def get_request(self, httprequest):
        # deduce type of request
        #if httprequest.args.get('jsonp'):
        #    return JsonRequest(httprequest)
        #if httprequest.mimetype in ("application/json", "application/json-rpc"):
        #    return JsonRequest(httprequest)
        #else:
        return Http(httprequest)

    def get_response(self, httprequest, result):#, explicit_session):
        #if isinstance(result, Response):# and result.is_qweb:
        #    try:
        #        result.flatten()
        #    except(Exception), e:
        #        if request.db:
        #            result = request.registry['ir.http']._handle_exception(e)
        #        else:
        #            raise

        if isinstance(result, basestring):
            response = Response(result, mimetype='text/html')
        else:
            response = result

        # save to cache if requested and possible
        if getattr(request, 'cache_save', False) and response.status_code == 200:
            response.freeze()
            r = response.response
            if isinstance(r, list) and len(r) == 1 and isinstance(r[0], str):
                request.registry.cache[request.cache_save] = {
                    'content': r[0],
                    'mimetype': response.headers['Content-Type'],
                    'time': time.time(),
                }

        #if httprequest.session.should_save:
        #    if httprequest.session.rotate:
        #        self.session_store.delete(httprequest.session)
        #        httprequest.session.sid = self.session_store.generate_key()
        #        httprequest.session.modified = True
        #    self.session_store.save(httprequest.session)
        
        # We must not set the cookie if the session id was specified using a http header or a GET parameter.
        # There are two reasons to this:
        # - When using one of those two means we consider that we are overriding the cookie, which means creating a new
        #   session on top of an already existing session and we don't want to create a mess with the 'normal' session
        #   (the one using the cookie). That is a special feature of the Session Javascript class.
        # - It could allow session fixation attacks.
        
        #if not explicit_session and hasattr(response, 'set_cookie'):
        #    response.set_cookie('session_id', httprequest.session.sid, max_age=90 * 24 * 60 * 60)

        return response

    @lazy_property
    def nodb_routing_map(self):
        _logger.info("Generating nondb routing")
        return self._routing_map([''])

    def _routing_map(self, modules):
        routing_map = werkzeug.routing.Map(strict_slashes=False, converters=None)

        def get_subclasses(klass):
            def valid(c):
                return c.__module__.startswith('manager.addons.') and c.__module__.split(".")[2] in modules
            
            subclasses = klass.__subclasses__()
            result = []
            
            for subclass in subclasses:
                if valid(subclass):
                    result.extend(get_subclasses(subclass))
            
            if not result and valid(klass):
                result = [klass]
            
            return result

        uniq = lambda it: collections.OrderedDict((id(x), x) for x in it).values()

        for module in modules:
            if module not in routers_per_module:
                continue

            for _, cls in routers_per_module[module]:
                subclasses = uniq(c for c in get_subclasses(cls) if c is not cls)
                if subclasses:
                    name = "%s (extended by %s)" % (cls.__name__, ', '.join(sub.__name__ for sub in subclasses))
                    cls = type(name, tuple(reversed(subclasses)), {})

                o = cls()
                members = inspect.getmembers(o, inspect.ismethod)
                for _, mv in members:
                    if hasattr(mv, 'routing'):
                        routing = dict(type='http', auth='user', methods=None, routes=None)
                        methods_done = list()
                        # update routing attributes from subclasses(auth, methods...)
                        for claz in reversed(mv.im_class.mro()):
                            fn = getattr(claz, mv.func_name, None)
                            if fn and hasattr(fn, 'routing') and fn not in methods_done:
                                methods_done.append(fn)
                                routing.update(fn.routing)
                        if routing['auth'] == "none": #not nodb_only or 
                            assert routing['routes'], "Method %r has not route defined" % mv
                            endpoint = EndPoint(mv, routing)
                            for url in routing['routes']:
                                if routing.get("combine", False):
                                    # deprecated v7 declaration
                                    url = o._cp_path.rstrip('/') + '/' + url.lstrip('/')
                                    if url.endswith("/") and len(url) > 1:
                                        url = url[: -1]

                                xtra_keys = 'defaults subdomain build_only strict_slashes redirect_to alias host'.split()
                                kw = {k: routing[k] for k in xtra_keys if k in routing}
                                routing_map.add(werkzeug.routing.Rule(url, endpoint=endpoint, methods=routing['methods'], **kw))
        return routing_map
        
class DisableCacheOnDebug(object):
    def __init__(self, app):
        self.app = app
    def __call__(self, environ, start_response):
        def start_wrapped(status, headers):
            referer = environ.get('HTTP_REFERER', '')
            parsed = urlparse.urlparse(referer)
            debug = parsed.query.count('debug') >= 1

            new_headers = []
            unwanted_keys = ['Last-Modified']
            if debug:
                new_headers = [('Cache-Control', 'no-cache')]
                unwanted_keys += ['Expires', 'Etag', 'Cache-Control']

            for k, v in headers:
                if k not in unwanted_keys:
                    new_headers.append((k, v))

            start_response(status, new_headers)
        return self.app(environ, start_wrapped)

class EndPoint(object):
    def __init__(self, method, routing):
        self.method = method
        self.original = getattr(method, 'original_func', method)
        self.routing = routing
        self.arguments = {}
    
    def __call__(self, *args, **kw):
        return self.method(*args, **kw)
