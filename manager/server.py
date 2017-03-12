# -*- coding: utf-8 -*-

import logging
import netaddr
import netifaces
import os

from bottle import route, run, request, hook, static_file
from PyQt4.QtCore import QUrl, QThread, SIGNAL
from templates import Template

_logger = logging.getLogger(__name__)

class Server(QThread):
    def __init__(self):
        QThread.__init__(self)
        
        self.register_hooks()
        self.httpd = None

    def run(self):
        _logger.info("Start HTTP server on port 10000")
        self.httpd = run(host='0.0.0.0', port=10000, reloader=True, debug=True, quiet=True)
        
    def register_hooks(self):
        @hook('before_request')
        def before_request():
            request.gui = False
            request.remote = False
            if request.path and request.path.startswith('/gui'):
                iface = netifaces.ifaddresses('eth0')[netifaces.AF_INET]
                
                if request.remote_addr in ('localhost', '127.0.0.1') or netaddr.IPAddress(request.remote_addr) in netaddr.IPNetwork('%(addr)s/%(netmask)s' % iface[0]):
                    if netaddr.IPAddress(request.remote_addr) in netaddr.IPNetwork('%(addr)s/%(netmask)s' % iface[0]):
                        request.remote = True
                
                    request.gui = True
                    path = request.path[4:] or '/'
                    request.path = path
                    request.environ['PATH_INFO'] = path
            
        @route('/')
        def index():
            #if request.remote:
            #    self.emit(SIGNAL('go_to(QString)'), 'http://127.0.0.1:10000%s' % request.path)
            return Template(content='ok').render()
            
        @route('/static/<filepath:path>')
        def server_static(filepath):
            if os.path.isfile(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static', filepath)):
                return static_file(filepath, root=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static'))
            return None
        