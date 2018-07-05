__author__ = 'alefur'
from datetime import datetime as dt
import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QTextCursor, QIcon, QPixmap
from PyQt5.QtWidgets import QPlainTextEdit, QLabel, QComboBox, QLineEdit, QProgressBar, QPushButton
import sequencePanel

imgpath = os.path.abspath(os.path.join(os.path.dirname(sequencePanel.__file__), '../..', 'img'))


class Label(QLabel):
    def __init__(self, *args, **kwargs):
        QLabel.__init__(self, *args, **kwargs)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(
            """QLabel { border-style: outset;border-width: 2px;border-radius: 7px;border-color: beige;font: bold 8pt; padding: 3px;}""")


class WhiteLabel(QLabel):
    def __init__(self, *args, **kwargs):
        QLabel.__init__(self, *args, **kwargs)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(
            "QLabel { background-color : white; color : black; qproperty-alignment: AlignCenter; font: 8pt; border-radius: 7px;padding: 3px;}")


class ComboBox(QComboBox):
    def __init__(self, *args, **kwargs):
        QComboBox.__init__(self, *args, **kwargs)
        self.setStyleSheet("QComboBox { font: 8pt;}")


class LineEdit(QLineEdit):
    def __init__(self, *args, **kwargs):
        QLineEdit.__init__(self, *args, **kwargs)
        self.setStyleSheet("QLineEdit { font: 8pt;}")


class CLabel(QLabel):
    colors = {"ON": ('green', 'white'),
              "OFF": ('red', 'white'),
              "WAITING": ('blue', 'white'),
              "PROCESSING": ('green', 'white')
              }

    def __init__(self, txt):
        QLabel.__init__(self)
        self.setText(txt=txt)

    def setColor(self, background, police='white'):
        if background == "red":
            self.setStyleSheet(
                "QLabel {font-size: 9pt; qproperty-alignment: AlignCenter; color:%s; background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,stop: 0 #f43131, stop: 1 #5e1414); border: 1px solid gray;border-radius: 3px;}" % police)
        elif background == "green":
            self.setStyleSheet(
                "QLabel {font-size: 9pt; qproperty-alignment: AlignCenter; color:%s; background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,stop: 0 #45f42e, stop: 1 #195511); border: 1px solid gray;border-radius: 3px;}" % police)
        elif background == "blue":
            self.setStyleSheet(
                "QLabel {font-size: 9pt; qproperty-alignment: AlignCenter; color:%s; background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,stop: 0 #3168f4, stop: 1 #14195e); border: 1px solid gray;border-radius: 3px;}" % police)
        elif background == "yellow":
            self.setStyleSheet(
                "QLabel {font-size: 9pt; qproperty-alignment: AlignCenter; color:%s; background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,stop: 0 #edf431, stop: 1 #5e5b14); border: 1px solid gray;border-radius: 3px;}" % police)
        elif background == "orange":
            self.setStyleSheet(
                "QLabel {font-size: 9pt; qproperty-alignment: AlignCenter; color:%s; background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,stop: 0 #f4a431, stop: 1 #5e4a14); border: 1px solid gray;border-radius: 3px;}" % police)

    def setText(self, txt):
        try:
            background, police = CLabel.colors[txt]
            self.setColor(background=background, police=police)
        except KeyError:
            pass

        QLabel.setText(self, txt)


class LogArea(QPlainTextEdit):
    def __init__(self):
        QPlainTextEdit.__init__(self)
        self.logArea = QPlainTextEdit()
        self.setMaximumBlockCount(10000)
        self.setReadOnly(True)

        self.setStyleSheet("background-color: black;color:white;")
        self.setFont(QFont("Monospace", 8))

    def newLine(self, line):
        self.insertPlainText("\n%s  %s" % (dt.now().strftime("%H:%M:%S.%f"), line))
        self.moveCursor(QTextCursor.End)
        self.ensureCursorVisible()

    def trick(self, qlineedit):
        self.newLine(qlineedit.text())


class ProgressBar(QProgressBar):
    def __init__(self, *args, **kwargs):
        QProgressBar.__init__(self, *args, **kwargs)
        self.setStyleSheet("QProgressBar { font: 8pt;}")


class IconButton(QPushButton):
    def __init__(self, iconFile):
        QPushButton.__init__(self)
        pix = QPixmap()
        pix.load('%s/%s' % (imgpath, iconFile))
        icon = QIcon(pix)
        self.setIcon(icon)


class EyeButton(QPushButton):
    def __init__(self):
        QPushButton.__init__(self)
        pixon = QPixmap()
        pixon.load('%s/%s' % (imgpath, 'eye_on.png'))
        self.icon_on = QIcon(pixon)

        pixon = QPixmap()
        pixon.load('%s/%s' % (imgpath, 'eye_off.png'))
        self.icon_off = QIcon(pixon)

        self.setState(False)
        self.setEnabled(False)

    def setState(self, state):
        icon = self.icon_on if not state else self.icon_off
        self.setIcon(icon)
        self.state = state
