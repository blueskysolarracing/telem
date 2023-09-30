from PyQt5 import QtWidgets
import time
import math
import sqlite3 
import numpy as np
from datetime import datetime
from sender import BssrProtocolSender


class App:

    def __init__(self, sender):
        # Qt app setup
        self.qt_application = QtWidgets.QApplication([])
        
        #self.cur = con.cursor()

        # Layout of Parent Widget
        self.parent_window = QtWidgets.QWidget()
        self.parent_window.setGeometry(100, 100, 400, 300)
        self.parent_window.setWindowTitle("Communications to Solar")
        self.parent_layout = QtWidgets.QFormLayout()
        self.parent_layout.setSpacing(10)
        self.parent_layout.setContentsMargins(0, 0, 0, 0)
        self.parent_window.setLayout(self.parent_layout)

        # Configure the communications plotting tab - tharaka

        self.text_edit = QtWidgets.QLineEdit()
        self.text_edit.setMaxLength(11)
        self.pushButton = QtWidgets.QPushButton('Enter')

        self.request = QtWidgets.QPushButton('Hear us?')
        self.pullOver = QtWidgets.QPushButton('Pull Over')
        self.drlOff = QtWidgets.QPushButton('ECO Off')
        self.drlOn = QtWidgets.QPushButton('ECO On')
        self.egress = QtWidgets.QPushButton('EGRESS')

        self.parent_layout.addWidget(self.request)
        self.parent_layout.addWidget(self.pullOver)
        self.parent_layout.addWidget(self.drlOff)
        self.parent_layout.addWidget(self.drlOn)
        self.parent_layout.addWidget(self.egress)
        self.parent_layout.addWidget(self.pushButton)
        self.parent_layout.addWidget(self.text_edit)
        self.parent_layout.addWidget(self.pushButton)


        # Connect each button to its corresponding function
        self.pushButton.clicked.connect(self.send_text)
        self.request.clicked.connect(self.send_request)
        self.pullOver.clicked.connect(self.send_pullOver)
        self.drlOff.clicked.connect(self.send_drlOff)
        self.drlOn.clicked.connect(self.send_drlOn)
        self.egress.clicked.connect(self.send_egress)

        self.sender = BssrProtocolSender(connection=None)


    #Functions for the buttons in Communication Request - tharaka
    def send_text(self):
        print(len(self.text_edit.text()))
        text = self.text_edit.text()
        self.sender.phrase_sender(text)
    
    def send_request(self):
        self.sender.phrase_sender('Hear us?')

    def send_pullOver(self):
        self.sender.phrase_sender("Pull Over")

    def send_drlOff(self):
        self.sender.phrase_sender("ECO Off")

    def send_drlOn(self):
        self.sender.phrase_sender("ECO On")

    def send_egress(self):
        self.sender.phrase_sender("EGRESS")
    


    def start(self):
        """
        Visualize the app and begin the event loop
        """
        self.parent_window.show()
        self.qt_application.exec()