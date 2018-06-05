__author__ = 'alefur'
import os

import sequenceManager as seqman
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QCheckBox, QPushButton

imgpath = os.path.abspath(os.path.join(os.path.dirname(seqman.__file__), '../..', 'img'))


class ExperimentRow(object):
    color = {"init": ("#FF7D7D", "#000000"), "valid": ("#7DFF7D", "#000000"), "active": ("#4A90D9", "#FFFFFF"),
             "finished": ("#5f9d63", "#FFFFFF"), "failed": ("#9d5f5f", "#FFFFFF")}

    def __init__(self, mwindow, type, name, comments, cmdStr):
        self.status = 'init'
        self.id = -1
        self.mwindow = mwindow
        self.type = type
        self.name = name
        self.comments = comments
        self.cmdStr = cmdStr
        self.visitStart = -1
        self.visitEnd = -1
        self.anomalies = ''

        self.valid = QCheckBox()
        self.valid.stateChanged.connect(self.setValid)
        self.colorCheckbox()

        pixUp = QPixmap()
        pixUp.load('%s/%s' % (imgpath, 'arrow_up2.png'))
        iconUp = QIcon(pixUp)

        self.buttonMoveUp = QPushButton()
        self.buttonMoveUp.setIcon(iconUp)
        self.buttonMoveUp.clicked.connect(self.moveUp)

        pixDown = QPixmap()
        pixDown.load('%s/%s' % (imgpath, 'arrow_down2.png'))
        iconDown = QIcon(pixDown)

        self.buttonMoveDown = QPushButton()
        self.buttonMoveDown.setIcon(iconDown)
        self.buttonMoveDown.clicked.connect(self.moveDown)

        pixDelete = QPixmap()
        pixDelete.load('%s/%s' % (imgpath, 'delete.png'))
        iconDelete = QIcon(pixDelete)

        self.buttonDelete = QPushButton()
        self.buttonDelete.setIcon(iconDelete)
        self.buttonDelete.clicked.connect(self.remove)

    @property
    def kwargs(self):
        return dict(type=self.type, name=self.name, comments=self.comments, cmdStr=self.cmdStr)

    @property
    def isValid(self):
        return self.status == 'valid'

    @property
    def isActive(self):
        return self.status == 'active'

    def colorCheckbox(self):
        self.valid.setStyleSheet("QCheckBox {background-color:%s};" % ExperimentRow.color[self.status][0])

    def setStatus(self, status):
        self.status = status
        self.colorCheckbox()

        self.mwindow.updateTable()

    def setActive(self):
        self.setStatus(status='active')
        self.mwindow.sendCommand(fullCmd=self.cmdStr,
                                 callFunc=self.handleResult)

    # def delayedCommand(self, fullCmd, callFunc, delay):
    #
    #     QTimer.singleShot(delay, partial(self.sendCommand, fullCmd, callFunc))
    #
    # def sendCommand(self, fullCmd, callFunc):
    #     if self.mwindow.onGoing:
    #         self.mwindow.sendCommand(fullCmd=fullCmd,
    #                                  callFunc=callFunc)
    #     else:
    #         self.setValid(state=2)

    def setFinished(self):
        self.setStatus(status='finished')

    def setFailed(self):
        self.setStatus(status='failed')

    def setValid(self, state):
        status = "valid" if state == 2 else "init"
        self.setStatus(status=status)

    def handleResult(self, resp):
        reply = resp.replyList[-1]
        code = resp.lastCode
        if code == ':':
            self.setFinished()
        elif code == 'F':
            self.setFailed()

        self.mwindow.printResponse(resp=resp)
        self.mwindow.sequencer.nextPlease()

    def moveUp(self):
        experiments = self.mwindow.experiments

        new_ind = experiments.index(self) - 1
        new_ind = 0 if new_ind < 0 else new_ind
        experiments.remove(self)
        experiments.insert(new_ind, self)

        self.mwindow.updateTable()

    def moveDown(self):
        experiments = self.mwindow.experiments

        new_ind = experiments.index(self) + 1
        new_ind = len(experiments) - 1 if new_ind > len(experiments) - 1 else new_ind
        experiments.remove(self)
        experiments.insert(new_ind, self)

        self.mwindow.updateTable()

    def remove(self):
        experiments = self.mwindow.experiments
        experiments.remove(self)

        self.mwindow.updateTable()
