import sys
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QMessageBox, QFileDialog
from PyQt5 import uic
from cipher import Cipher

from main import Ui_MainWindow


class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None, cipher=None):
        super().__init__(parent)
        self.setupUi(self)
        self.connectSignalsSlots()
        self.connectElements()
        self.cipher = cipher

    def connectElements(self):
        self.statusbar.showMessage("Ready")
        self.cipherButton.clicked.connect(self.cipherClicked)
        self.decipherButton.clicked.connect(self.decipherClicked)

    def cipherClicked(self):
        if self.cipherText.toPlainText() != "":
            self.statusbar.showMessage("Ciphering...")
            try:
                c = self.cipher.encrypt_text(self.cipherText.toPlainText())
                self.cipherResults.setPlainText(c)
                self.statusbar.showMessage("Ciphering done")
            except:
                self.statusbar.showMessage("Ciphering failed")
        else:
            chosen_file = self.selectFile()
            print(chosen_file)
            if chosen_file != "":
                self.statusbar.showMessage("Ciphering...")
                try:
                    self.cipher.encrypt_file(chosen_file, chosen_file + ".cipher", self)
                    self.statusbar.showMessage("Ciphering done")
                except:
                    self.statusbar.showMessage("Ciphering failed")
            else:
                self.statusbar.showMessage("No file selected")

    def decipherClicked(self):
        if self.cipherText.toPlainText() != "":
            self.statusbar.showMessage("Deciphering...")
            try:
                c = self.cipher.decrypt_text(self.cipherText.toPlainText())
                self.cipherResults.setPlainText(c)
                self.statusbar.showMessage("Deciphering done")
            except:
                self.statusbar.showMessage("Deciphering failed")
        else:
            chosen_file = self.selectFile()
            print(chosen_file)
            if chosen_file != "":
                self.statusbar.showMessage("Deciphering...")
                try:
                    if chosen_file.endswith(".cipher"):
                        result_file_name = chosen_file.replace(".cipher", ".decipher")
                    else:
                        result_file_name = chosen_file + ".decipher"

                    self.cipher.decrypt_file(chosen_file, result_file_name, self)
                    self.statusbar.showMessage("Deciphering done")
                except:
                    self.statusbar.showMessage("Deciphering failed")
            else:
                self.statusbar.showMessage("No file selected")

    def selectFile(self):
        return QFileDialog.getOpenFileName()[0]

    def connectSignalsSlots(self):
        pass

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


class FindReplaceDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi("main.ui", self)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window(cipher=Cipher())
    win.show()
    sys.exit(app.exec())
