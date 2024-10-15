import os
import sys
import jwt
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from PyQt5.QtCore import QUrl
from dotenv import load_dotenv, set_key
from datetime import datetime

class BrowserWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Embedded Browser')
        self.setGeometry(100, 100, 800, 600)

        # Create a central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Create a QWebEngineView
        self.browser = QWebEngineView()
        layout.addWidget(self.browser)
        
        # Load a website
        self.browser.setUrl(QUrl(os.environ.get("FLOW_LOGIN_URL", "https://flow.ciandt.com/account/sign-in")))

        # Get the default profile and cookie store
        profile = QWebEngineProfile.defaultProfile()
        self.cookie_store = profile.cookieStore()
        self.cookie_store.cookieAdded.connect(self.cookie_added)

        self.cookie_list = []

    def cookie_added(self, cookie):
        # Add the FLOW_TOKEN and FLOW_TENANT environment variables
        if cookie.name() == "FlowToken":
            # Add new environment variable
            flowToken = str(cookie.value(), "utf-8")
            decoded = jwt.decode(flowToken, options={"verify_signature": False})
            # Check if FlowToken is valid
            if datetime.fromtimestamp(decoded["exp"]) > datetime.now():
                os.environ["FLOW_TOKEN"] = flowToken
                set_key('.env', "FLOW_TOKEN", flowToken)
                self.cookie_list.append(cookie.name())
        elif cookie.name() == "FlowTenant":
            # Add new environment variable
            flowTenant = str(cookie.value(), "utf-8")
            set_key('.env', "FLOW_TENANT", flowTenant)
            self.cookie_list.append(cookie.name())
        
        # Close the window if both cookies are added
        if len(self.cookie_list) == 2:
            mainWindow.close()

if __name__ == '__main__':
    # Load environment variables from .env file
    load_dotenv()

    # Check if local FlowToken is valid
    flowToken = os.environ.get('FLOW_TOKEN')
    if flowToken:
        decoded = jwt.decode(flowToken, options={"verify_signature": False})
        # If FlowToken is not expired, exit the program
        if datetime.fromtimestamp(decoded["exp"]) > datetime.now():
            sys.exit()
    
    # Get a new FlowToken
    app = QApplication(sys.argv)
    mainWindow = BrowserWindow()
    mainWindow.show()
    sys.exit(app.exec_())