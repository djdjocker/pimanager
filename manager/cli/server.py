# -*- coding: utf-8 -*-
import logging
import os
import time
import thread
import threading
import signal
import socket
import sys
import werkzeug
import werkzeug.serving

_logger = logging.getLogger(__name__)

class Server():
    def run(self, args):
        server = ThreadedServer()
        rc = server.run()
        sys.exit(rc)

class RequestHandler(werkzeug.serving.WSGIRequestHandler):
    def setup(self):
        # flag the current thread as handling a http request
        super(RequestHandler, self).setup()
        me = threading.currentThread()
        me.name = 'pimanager.http.request.%s' % (me.ident,)
        
class ThreadedServer(object):
    def __init__(self):
        self.interface = '0.0.0.0'
        self.port = 10000
        # runtime
        self.pid = os.getpid()
        
        self.gui_thread_id = threading.currentThread().ident
        self.http_thread_id = threading.currentThread().ident
        # Variable keeping track of the number of calls to the signal handler defined
        # below. This variable is monitored by ``quit_on_signals()``.
        self.quit_signals_received = 0

        self.httpd = None
        
    def run(self):
        self.start()
        try:
            while self.quit_signals_received == 0:
                time.sleep(60)
        except KeyboardInterrupt:
            pass
        self.stop()
    
    def start(self):
        _logger.debug("Setting signal handlers")
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGCHLD, self.signal_handler)
        signal.signal(signal.SIGHUP, self.signal_handler)
        
        self.http_spawn()
        #self.gui_spawn()

    def stop(self):
        """ Shutdown the WSGI server. Wait for non deamon threads."""
        _logger.info("Initiating shutdown")
        _logger.info("Hit CTRL-C again or send a second signal to force the shutdown.")

        if self.httpd:
            self.httpd.shutdown()
            self.close_socket(self.httpd.socket)

        # Manually join() all threads before calling sys.exit() to allow a second signal
        # to trigger _force_quit() in case some non-daemon threads won't exit cleanly.
        # threading.Thread.join() should not mask signals (at least in python 2.5).
        me = threading.currentThread()
        _logger.debug('current thread: %r', me)
        for thread in threading.enumerate():
            _logger.debug('process %r (%r)', thread, thread.isDaemon())
            if thread != me and not thread.isDaemon() and thread.ident != self.main_thread_id:
                while thread.isAlive():
                    _logger.debug('join and sleep')
                    # Need a busyloop here as thread.join() masks signals
                    # and would prevent the forced shutdown.
                    thread.join(0.05)
                    time.sleep(0.05)

        _logger.debug('--')
        logging.shutdown()

    def signal_handler(self, sig, frame):
        if sig in [signal.SIGINT, signal.SIGTERM]:
            # shutdown on kill -INT or -TERM
            self.quit_signals_received += 1
            if self.quit_signals_received > 1:
                # logging.shutdown was already called at this point.
                sys.stderr.write("Forced shutdown.\n")
                os._exit(0)
        elif sig == signal.SIGHUP:
            # restart on kill -HUP
            pycms.phoenix = True
            self.quit_signals_received += 1

    def http_spawn(self):
        t = threading.Thread(target=self.http_thread, name="pimanager.httpd")
        t.setDaemon(True)
        t.start()
        _logger.info('HTTP service (werkzeug) running on %s:%s', self.interface, self.port)

    def xmlrpc(self, environ, start_response):
        pass
        
    def http(self, environ, start_response):
        pass
        
    def http_thread(self):
        def app(environ, start_response):
            for handler in [self.xmlrpc, self.http]:
                result = handler(environ, start_response)
                if result is None:
                    continue
                return result

            # We never returned from the loop.
            response = 'No handler found.\n'
            start_response('404 Not Found', [('Content-Type', 'text/plain'), ('Content-Length', str(len(response)))])
            return [response]
            
        self.httpd = ThreadedWSGIServerReloadable(self.interface, self.port, app)
        self.httpd.serve_forever()
    
    
    
class ThreadedWSGIServerReloadable(werkzeug.serving.ThreadedWSGIServer):
    """ werkzeug Threaded WSGI Server patched to allow reusing a listen socket
    given by the environement, this is used by autoreload to keep the listen
    socket open when a reload happens.
    """
    def __init__(self, host, port, app):
        super(ThreadedWSGIServerReloadable, self).__init__(host, port, app, handler=RequestHandler)
        
    def handle_error(self, request, client_address):
        t, e, _ = sys.exc_info()
        if t == socket.error and e.errno == errno.EPIPE:
            # broken pipe, ignore error
            return
        _logger.exception('Exception happened during processing of request from %s', client_address)

    def server_bind(self):
        envfd = os.environ.get('LISTEN_FDS')
        if envfd and os.environ.get('LISTEN_PID') == str(os.getpid()):
            self.reload_socket = True
            self.socket = socket.fromfd(int(envfd), socket.AF_INET, socket.SOCK_STREAM)
            # should we os.close(int(envfd)) ? it seem python duplicate the fd.
        else:
            self.reload_socket = False
            super(ThreadedWSGIServerReloadable, self).server_bind()

    def server_activate(self):
        if not self.reload_socket:
            super(ThreadedWSGIServerReloadable, self).server_activate()
