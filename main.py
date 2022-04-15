# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.cipherButton = QtWidgets.QPushButton(self.centralwidget)
        self.cipherButton.setGeometry(QtCore.QRect(310, 450, 121, 51))
        self.cipherButton.setObjectName("cipherButton")
        self.cipherText = QtWidgets.QTextEdit(self.centralwidget)
        self.cipherText.setGeometry(QtCore.QRect(120, 160, 531, 70))
        self.cipherText.setLocale(QtCore.QLocale(QtCore.QLocale.Polish, QtCore.QLocale.Poland))
        self.cipherText.setObjectName("cipherText")
        self.cipherResults = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.cipherResults.setGeometry(QtCore.QRect(120, 250, 531, 70))
        self.cipherResults.setReadOnly(True)
        self.cipherResults.setObjectName("cipherResults")
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setGeometry(QtCore.QRect(100, 360, 611, 41))
        self.progressBar.setMaximum(100)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 26))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuLoad = QtWidgets.QMenu(self.menubar)
        self.menuLoad.setObjectName("menuLoad")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuLoad.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.cipherButton.setText(_translate("MainWindow", "Szyfruj plik"))
        self.cipherText.setPlaceholderText(_translate("MainWindow", "Tekst do zaszyfrowania"))
        self.cipherResults.setPlaceholderText(_translate("MainWindow", "Rezultat szyfrowania"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuLoad.setTitle(_translate("MainWindow", "Load"))
