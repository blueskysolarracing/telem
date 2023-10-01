from PyQt5 import QtWidgets
import time
import math
import sqlite3 
import numpy as np
from datetime import datetime
from sender.radiosender import BssrProtocolSender


class App:

    def __init__(self, sender: BssrProtocolSender):
        self.sender = sender
        self.sender
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
        self.pull_over = QtWidgets.QPushButton('Pull Over')
        self.eco_off = QtWidgets.QPushButton('ECO Off')
        self.eco_on = QtWidgets.QPushButton('ECO On')
        self.egress = QtWidgets.QPushButton('EGRESS')

        self.parent_layout.addWidget(self.request)
        self.parent_layout.addWidget(self.pull_over)
        self.parent_layout.addWidget(self.eco_off)
        self.parent_layout.addWidget(self.eco_on)
        self.parent_layout.addWidget(self.egress)
        self.parent_layout.addWidget(self.pushButton)
        self.parent_layout.addWidget(self.text_edit)
        self.parent_layout.addWidget(self.pushButton)


        # Connect each button to its corresponding function
        
        # communication buttons
        self.pushButton.clicked.connect(self.send_text)
        self.request.clicked.connect(lambda: self.sender.phrase_sender("Hear us?"))
        self.pull_over.clicked.connect(lambda: self.sender.phrase_sender("Pull Over"))
        self.egress.clicked.connect(lambda: self.sender.phrase_sender("EGRESS"))
        
        # motor control buttons
        self.eco_off.clicked.connect(self.sender.eco_off_sender)
        self.eco_on.clicked.connect(self.sender.eco_on_sender)


    #Functions for the buttons in Communication Request - tharaka
    def send_text(self):
        print(len(self.text_edit.text()))
        text = self.text_edit.text()
        self.sender.phrase_sender(text)


    def start(self):
        """
        Visualize the app and begin the event loop
        """
        self.parent_window.show()
        self.qt_application.exec()