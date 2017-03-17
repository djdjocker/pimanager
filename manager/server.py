# -*- coding: utf-8 -*-

import logging
import manager
import netaddr
import netifaces
import os

from bottle import hook, post, redirect, request, response, route, run, static_file
from PyQt4.QtCore import QUrl, QThread, SIGNAL
from templates import Template

_logger = logging.getLogger(__name__)

remote_setting_overscan_stage = -1
local_setting_overscan_stage = -1

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
            request.localhost = False
            request.remote = False
            request.server = self
            
            iface = netifaces.ifaddresses('eth0')[netifaces.AF_INET]
            
            if netaddr.IPAddress(request.remote_addr) in netaddr.IPNetwork('%(addr)s/%(netmask)s' % iface[0]):
                request.remote = True
                
            if request.remote_addr in ('localhost', '127.0.0.1'):
                request.localhost = True
                response.set_cookie("synced", "localhost", path="/")
                
            if request.path and request.path.startswith('/gui'):
                if request.localhost or request.remote:
                    request.gui = True
                    path = request.path[4:] or '/'
                    request.path = path
                    request.environ['PATH_INFO'] = path
                
            if not manager.config.rc_exists and not request.path.startswith('/config') and not request.path.startswith('/static') and not request.path.startswith('/longpoll'):
                _logger.info('Redirect from %s to %s' % (request.path, '/config'))
                return redirect('%s/config' % (request.gui and '/gui' or ''))
            
            if request.gui and request.remote and not bool(request.get_cookie("synced", default=False)):
                response.set_cookie("synced", "remote", path="/")
                if request.path != manager.gui.view.url().path()[4:]:
                    redirect(manager.gui.view.url().path())
            elif request.gui and request.remote and bool(request.get_cookie("synced", default=False)) and not request.path.startswith('/static') and not request.path.startswith('/longpoll'):
                if request.path != manager.gui.view.url().path()[4:]:
                    self.emit(SIGNAL('go_to(QString)'), 'http://127.0.0.1:10000/gui%s' % request.path)
            elif not request.gui and request.remote:
                response.set_cookie("synced", "False", path="/")
            
                
        @hook('after_request')
        def after_request():
            _logger.info('%s %s %s %s' % (request.remote_addr,
                                            request.method,
                                            request.url,
                                            response.status))
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
        
        @route('/config')
        @route('/config/<stage:re[a-z]+>')
        def config(stage='global'):
            if not request.gui and request.remote:
                return Template(template_content=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates', 'config_not_alowed_remote.tpl')).render()
            elif request.gui and not (request.remote or request.localhost):
                return Template(template_content=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates', 'config_not_alowed_external.tpl')).render()
            else:
                extras = [
                    (os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates', 'config_overscan.tpl'), None)
                ]
                
                js = [
                    ("", "src/js/settings.js")
                ]
                return Template(template_content=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates', 'config.tpl'), js=js, extra=extras).render()
        
        @route('/longpoll/setting-overscan')
        def longpoll_setting_overscan():
            global remote_setting_overscan_stage, local_setting_overscan_stage
            
            if request.localhost:
                return setting_remote_overscan_opened
            elif request.remote:
                return local_setting_overscan_stage
                
            return False
        
        @post('/longpoll/set-setting-overscan-stage')
        def longpoll_set_setting_overscan(openend):
            global remote_setting_overscan_stage, local_setting_overscan_stage
            
            if request.localhost:
                local_setting_overscan_stage = openend
            elif request.remote:
                remote_setting_overscan_stage = openend
                
            return False
            