# -*- coding: utf-8 -*-
import htmlPy
import logging
import PySide
import signal

from manager.server import Server

_logger = logging.getLogger(__name__)

class GUI(htmlPy.AppGUI):
    def __init__(self, *args, **kwargs):
        super(GUI, self).__init__(title=u"PiManagerGUI", *args, **kwargs)
        self.window.setWindowState(PySide.QtCore.Qt.WindowState.WindowFullScreen)
        self.set_signals()
        self.http = None
        
    def set_signals(self):
        _logger.info("Setting signal handlers")
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        signal.signal(signal.SIGTERM, signal.SIG_DFL)
        signal.signal(signal.SIGCHLD, signal.SIG_DFL)
        signal.signal(signal.SIGHUP, signal.SIG_DFL)
        
    def start(self):
        self.http = Server()
        self.http.run()
        super(GUI, self).start()
        
    def stop(self):
        if self.http:
            self.http.stop()
        super(GUI, self).stop()