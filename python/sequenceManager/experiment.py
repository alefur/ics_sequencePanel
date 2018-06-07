__author__ = 'alefur'

from functools import partial

from PyQt5.QtWidgets import QCheckBox, QPushButton

from sequenceManager.widgets import IconButton, EyeButton


class SubCommand(object):
    def __init__(self, id, cmdStr):
        self.id = id
        self.cmdStr = cmdStr
        self.visitStart = -1
        self.visitEnd = -1
        self.anomalies = ''
        self.status = 'init'
        if id == 0:
            self.setActive()

    @property
    def isFinished(self):
        return self.status == 'finished'

    def setFinished(self):
        self.status = 'finished'

    def setFailed(self):
        self.status = 'failed'

    def setActive(self):
        self.status = 'active'


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
        self.subcommands = []

        self.valid = QCheckBox()
        self.valid.stateChanged.connect(self.setValid)
        self.colorCheckbox()

        self.buttonMoveUp = IconButton(iconFile='arrow_up2.png')
        self.buttonMoveUp.clicked.connect(self.moveUp)

        self.buttonMoveDown = IconButton(iconFile='arrow_down2.png')
        self.buttonMoveDown.clicked.connect(self.moveDown)

        self.buttonDelete = IconButton(iconFile='delete.png')
        self.buttonDelete.clicked.connect(self.remove)

        self.buttonEye = EyeButton()
        self.buttonEye.clicked.connect(partial(self.showSubcommands))

    @property
    def kwargs(self):
        return dict(type=self.type, name=self.name, comments=self.comments, cmdStr=self.cmdStr)

    @property
    def isValid(self):
        return self.status == 'valid'

    @property
    def isActive(self):
        return self.status == 'active'

    @property
    def showSub(self):
        return self.buttonEye.state

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

    def setFinished(self):
        self.valid.setEnabled(False)
        self.setStatus(status='finished')

    def setFailed(self):
        self.valid.setEnabled(False)
        self.cleanupSubCommand()
        self.setStatus(status='failed')

    def setValid(self, state):
        status = "valid" if state == 2 else "init"
        self.setStatus(status=status)

    def showSubcommands(self):
        self.buttonEye.setState(state=not self.buttonEye.state)
        self.mwindow.updateTable()

    def handleResult(self, resp):
        reply = resp.replyList[-1]
        code = resp.lastCode

        if code == 'I':
            self.updateInfo(reply, fail=False)
        elif code == 'W':
            self.updateInfo(reply, fail=True)
        elif code == ':':
            self.setFinished()
            self.mwindow.sequencer.nextPlease()
        elif code == 'F':
            self.setFailed()
            self.mwindow.sequencer.nextPlease()

        self.mwindow.printResponse(resp=resp)

    def updateInfo(self, reply, fail):
        if 'newExperiment' in reply.keywords:
            self.addSubCommand(*reply.keywords['newExperiment'].values)
        if 'subCommand' in reply.keywords:
            self.updateSubCommandStatus(fail, *reply.keywords['subCommand'].values)

    def updateSubCommandStatus(self, fail, id, returnStr=''):
        id = int(id)
        subcommand = self.subcommands[id]

        if fail:
            subcommand.setFailed()
            subcommand.anomalies = returnStr
        else:
            subcommand.setFinished()

        try:
            self.subcommands[id + 1].setActive()
        except IndexError:
            pass

        self.mwindow.updateTable()

    def addSubCommand(self, experimentId, cmdList):

        self.id = experimentId
        self.subcommands = [SubCommand(id=i, cmdStr=cmdStr) for i, cmdStr in enumerate(cmdList.split(';'))]
        self.buttonEye.setEnabled(True)

        self.mwindow.updateTable()

    def cleanupSubCommand(self):
        for subcommand in self.subcommands:
            if not subcommand.isFinished:
                subcommand.setFailed()


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
