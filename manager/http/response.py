# -*- coding: utf-8 -*-
import mimetypes
import werkzeug.wrappers

from .root import request

mimetypes.add_type('application/font-woff', '.woff')
mimetypes.add_type('application/vnd.ms-fontobject', '.eot')
mimetypes.add_type('application/x-font-ttf', '.ttf')

class Response(werkzeug.wrappers.Response):
    """ Response object passed through controller route chain.

    In addition to the :class:`werkzeug.wrappers.Response` parameters, this
    class's constructor can take the following additional parameters
    for QWeb Lazy Rendering.

    :param basestring template: template to render
    :param dict qcontext: Rendering context to use
    :param int uid: User id to use for the ir.ui.view render call,
                    ``None`` to use the request's user (the default)

    these attributes are available as parameters on the Response object and
    can be altered at any time before rendering

    Also exposes all the attributes and methods of
    :class:`werkzeug.wrappers.Response`.
    """
    default_mimetype = 'text/html'
    def __init__(self, *args, **kw):
        template = kw.pop('template', None)
        qcontext = kw.pop('qcontext', None)
        uid = kw.pop('uid', None)
        super(Response, self).__init__(*args, **kw)
        self.set_default(template, qcontext, uid)

    def set_default(self, template=None, qcontext=None, uid=None):
        self.template = template
        self.qcontext = qcontext or dict()
        self.uid = uid
        # Support for Cross-Origin Resource Sharing
        if request.endpoint and 'cors' in request.endpoint.routing:
            self.headers.set('Access-Control-Allow-Origin', request.endpoint.routing['cors'])
            methods = 'GET, POST'
            if request.endpoint.routing['type'] == 'json':
                methods = 'POST'
            elif request.endpoint.routing.get('methods'):
                methods = ', '.join(request.endpoint.routing['methods'])
            self.headers.set('Access-Control-Allow-Methods', methods)

    @property
    def is_qweb(self):
        return self.template is not None

    def render(self):
        """ Renders the Response's template, returns the result
        """
        view_obj = request.registry["ir.ui.view"]
        uid = self.uid or request.uid or pycms.SUPERUSER_ID
        self.qcontext['request'] = request
        return view_obj.render(
            request.cr, uid, self.template, self.qcontext,
            context=request.context)

    def flatten(self):
        """ Forces the rendering of the response's template, sets the result
        as response body and unsets :attr:`.template`
        """
        if self.template:
            self.response.append(self.render())
            self.template = None
