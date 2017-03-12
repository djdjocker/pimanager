import sys
import signal
import time
from PyQt4.QtGui import QApplication, QWidget, QVBoxLayout#, QPushButton
from PyQt4.QtCore import QUrl, QThread, QObject, SIGNAL, Qt
from PyQt4.QtWebKit import QWebView

class Thread(QThread):
    def __init__(self):
        QThread.__init__(self)

    def run(self):
        time.sleep(3)
        self.emit(SIGNAL('some_signal'))

class Gui:
    def __init__(self):
        # Create an application
        
        
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        signal.signal(signal.SIGTERM, signal.SIG_DFL)
        signal.signal(signal.SIGCHLD, signal.SIG_DFL)
        signal.signal(signal.SIGHUP, signal.SIG_DFL)
        
        self.app = QApplication([])
 
        
        
        t = self.t = Thread()
        QObject.connect(t, SIGNAL('some_signal'), self.signalHandler, Qt.QueuedConnection)

    def quit(self):
        QApplication.quit()
        
    def run(self):
        # Show the window and run the app
        self.view.setHtml('ok')
        
        # Start new thread.
        self.t.start()
        self.app.exec_()
        
    def signalHandler(self):
        # We got signal!
        self.view.load(QUrl('http://google.fr/'))
        self.win.show()
        
"""view.setHtml('''
  <html>
    <head>
      <title>A Demo Page</title>
 
      <script language="javascript">
        // Completes the full-name control and
        // shows the submit button
        function completeAndReturnName() {
          var fname = document.getElementById('fname').value;
          var lname = document.getElementById('lname').value;
          var full = fname + ' ' + lname;
 
          document.getElementById('fullname').value = full;
          document.getElementById('submit-btn').style.display = 'block';
 
          return full;
        }
      </script>
    </head>
 
    <body>
      <form>
        <label for="fname">First name:</label>
        <input type="text" name="fname" id="fname"></input>
        <br />
        <label for="lname">Last name:</label>
        <input type="text" name="lname" id="lname"></input>
        <br />
        <label for="fullname">Full name:</label>
        <input disabled type="text" name="fullname" id="fullname"></input>
        <br />
        <input style="display: none;" type="submit" id="submit-btn"></input>
      </form>
    </body>
  </html>
''')"""

if __name__ == "__main__":
    sys.exit(Gui().run())