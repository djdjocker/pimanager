# -*- coding: utf-8 -*-
import signal
import sys

from PyQt4.QtGui import QApplication
from PyQt4.QtCore import SIGNAL, QObject, Qt

#import http

from gui import Gui
from server import Server

gui = None
server = None

def start():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    signal.signal(signal.SIGTERM, signal.SIG_DFL)
    signal.signal(signal.SIGCHLD, signal.SIG_DFL)
    signal.signal(signal.SIGHUP, signal.SIG_DFL)
    
    app = QApplication([])
    
    global gui
    global server
    
    server = Server()
    server.start()
    
    gui = Gui()
    gui.go_to('http://127.0.0.1:10000/gui')
     
    QObject.connect(server, SIGNAL('go_to(QString)'), gui.go_to)#, Qt.QueuedConnection)
    
    sys.exit(app.exec_())