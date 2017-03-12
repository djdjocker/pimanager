# -*- coding: utf-8 -*-
from PyQt4.QtGui import QWidget, QVBoxLayout
from PyQt4.QtWebKit import QWebView
from PyQt4.QtCore import QUrl

class Gui:
    def __init__(self):
        # And a window
        self.win = QWidget()
        self.win.setContentsMargins(0,0,0,0)
        self.win.showFullScreen()
 
        # And give it a layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        self.win.setLayout(layout)
 
        # Create and fill a QWebView
        self.view = QWebView()
        
        # Add the QWebViewto the layout
        layout.addWidget(self.view)
        
    def go_to(self, url):
        self.view.load(QUrl(url))
        self.win.show()