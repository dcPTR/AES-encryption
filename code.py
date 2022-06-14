import sys
import os
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QMessageBox, QFileDialog
from PyQt5 import QtCore
from PyQt5 import uic
from threading import Thread
from KeyProvider import KeyProvider
from cipher import Cipher
from message_sender import MessageSender
from tcp_handler import TCPHandler
from main import Ui_MainWindow


class Window(QMainWindow, Ui_MainWindow):
    signal = QtCore.pyqtSignal(str)

    def __init__(self, parent=None, cipher=None):
        super().__init__(parent)
        self.setupUi(self)
        self.connectSignalsSlots()
        self.connectElements()
        self.cipher = cipher
        self.tcp = None
        self.serverThread = None
        self.recvThread = None

    def connectElements(self):
        self.statusbar.showMessage("Ready")
        self.cipherButton.clicked.connect(self.cipherClicked)
        self.decipherButton.clicked.connect(self.decipherClicked)
        self.runServerButton.clicked.connect(self.runServerClicked)
        self.stopServerButton.clicked.connect(self.stopServerClicked)
        self.connectButton.clicked.connect(self.connectClicked)
        self.disconnectButton.clicked.connect(self.disconnectClicked)
        self.cipherModeCBC.clicked.connect(self.cipherModeCBCClicked)
        self.cipherModeECB.clicked.connect(self.cipherModeECBClicked)

    def cipherModeCBCClicked(self):
        self.cipher.set_mode("CBC")

    def cipherModeECBClicked(self):
        self.cipher.set_mode("ECB")

    def cipherClicked(self):
        self.cipherText.setStyleSheet("background-color:white")
        if self.cipherText.toPlainText() != "":
            self.statusbar.showMessage("Ciphering...")
            try:
                _, _ = self.cipher.provider.get_key_pair()
                self.tcp.exchange_public_key()
                c = self.cipher.encrypt_text(self.cipherText.toPlainText())
                self.statusbar.showMessage("Ciphering done")
                self.cipherResults.setPlainText(c)
                if self.tcp is not None and self.tcp.is_connected():
                    sender = MessageSender()
                    sender.send_message(self.tcp, c.encode())
                    self.statusbar.showMessage("Sent encrypted message")

            except Exception as e:
               print(e)
               self.statusbar.showMessage("Ciphering failed")
        else:
            chosen_file = self.selectFile()
            print(chosen_file)
            if chosen_file != "":
                self.statusbar.showMessage("Ciphering...")
                try:
                    _, _ = self.cipher.provider.get_key_pair()
                    self.tcp.exchange_public_key()
                    result_file_name = chosen_file + ".cipher"
                    self.cipher.encrypt_file(chosen_file, result_file_name, self)
                    self.statusbar.showMessage("Ciphering done")
                    if self.tcp is not None and self.tcp.is_connected():
                        print("Sending file")
                        self.statusbar.showMessage("Sending file")
                        f = open(result_file_name, 'rb')
                        sender = MessageSender()
                        sender.send_message(self.tcp, f.read(), os.path.basename(result_file_name + ".sent"), self)
                        self.statusbar.showMessage("Cipher message sent")
                except Exception as e:
                    print(f"exception {e}")
                    self.statusbar.showMessage("Ciphering failed")
            else:
                self.statusbar.showMessage("No file selected")

    def decipherClicked(self):
        self.cipherText.setStyleSheet("background-color:white")
        if self.cipherText.toPlainText() != "":
            self.statusbar.showMessage("Deciphering...")
            try:
                c = self.cipher.decrypt_text(self.cipherText.toPlainText())
                self.cipherResults.setPlainText(c)
                # if self.tcp is not None and self.tcp.is_connected():
                #     self.tcp.send_message(c)
                self.statusbar.showMessage("Deciphering done")
            except Exception as e:
                print(e)
                self.statusbar.showMessage("Deciphering failed")
        else:
            chosen_file = self.selectFile()
            print(chosen_file)
            if chosen_file != "":
                self.statusbar.showMessage("Deciphering...")
                try:
                    if chosen_file.endswith(".cipher"):
                        result_file_name = chosen_file.replace(".cipher", "")
                    elif chosen_file.endswith(".cipher.sent"):
                        result_file_name = chosen_file.replace(".cipher.sent", "")
                    else:
                        result_file_name = chosen_file

                    self.cipher.decrypt_file(chosen_file, result_file_name, self)
                    self.statusbar.showMessage("Deciphering done")
                    # if self.tcp is not None and self.tcp.is_connected():
                    #     f = open(result_file_name, 'rb')
                    #     self.tcp.send_message(f.read(), os.path.basename(result_file_name))

                except Exception as e:
                    print(e)
                    self.statusbar.showMessage("Deciphering failed")
            else:
                self.statusbar.showMessage("No file selected")

    def selectFile(self):
        return QFileDialog.getOpenFileName()[0]

    def connectSignalsSlots(self):
        self.signal.connect(self.updateCipherResult)

    def findAndReplace(self):
        dialog = FindReplaceDialog(self)
        dialog.exec()

    def about(self):
        QMessageBox.about(
            self,
            "Simple AES Encryption",
            "<p>A simple encryption app built with:</p>"
            "<p>- PyQt</p>"
            "<p>- Qt Designer</p>"
            "<p>- Python</p>",
        )

    def runServerClicked(self):
        if self.serverPort.text() == "" or self.clientPort.text() == "":
            return

        try:
            self.tcp = TCPHandler(int(self.serverPort.text()), int(self.clientPort.text()))
        except Exception as e:
            print(e)
            return

        self.serverThread = Thread(target=self.tcp.listen)
        self.serverThread.start()
        self.connectButton.setEnabled(True)
        self.stopServerButton.setEnabled(True)
        self.runServerButton.setEnabled(False)

    def connectClicked(self):
        if not self.tcp.try_connect():
            return

        self.connectButton.setEnabled(False)
        self.disconnectButton.setEnabled(True)
        self.recvThread = Thread(target=self.handleReceiving)
        self.recvThread.start()

    def disconnectClicked(self):
        if not self.tcp.disconnect():
            return

        self.connectButton.setEnabled(True)
        self.disconnectButton.setEnabled(False)
        self.recvThread.join()

    def stopServerClicked(self):
        self.tcp.stop_listen()
        self.connectButton.setEnabled(False)
        self.disconnectButton.setEnabled(False)
        self.stopServerButton.setEnabled(False)
        self.runServerButton.setEnabled(True)
        self.serverThread.join()

    def handleReceiving(self):
        while self.tcp is not None and self.tcp.is_connected():
            msg, filename = self.tcp.recv()
            if self.tcp.hasJustAcknowledged():
                self.onMessageDelivered()

            if msg is None:
                continue

            print(f";{filename}; {len(filename)}")
            if len(filename) == 0:
                self.signal.emit(msg.decode())
            else:
                with open(filename, 'wb') as f:
                    f.write(msg)

    def updateCipherResult(self, text):
        self.cipherResults.setPlainText(text)

    def onMessageDelivered(self):
        self.cipherText.setStyleSheet("background-color:lightgreen")

    def update_progress(self, i, n):
        self.progressBar.setValue(int(i / n * 100))


class FindReplaceDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi("main.ui", self)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window(cipher=Cipher())
    win.show()
    sys.exit(app.exec())
