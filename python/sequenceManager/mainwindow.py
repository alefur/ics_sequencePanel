__author__ = 'alefur'

import os
import pickle

from PyQt5.QtWidgets import QGridLayout, QWidget, QLineEdit, QAction, QMenuBar, QFileDialog
from sequenceManager.dialog import Dialog
from sequenceManager.sequencer import Sequencer
from sequenceManager.table import Table
from sequenceManager.widgets import LogArea


class ManagerWidget(QWidget):
    def __init__(self, manager):
        self.printLevels = {'D': 0, '>': 0,
                            'I': 1, ':': 1,
                            'W': 2,
                            'F': 3, '!': 4}
        self.printLevel = self.printLevels['I']
        self.experiments = []

        QWidget.__init__(self)
        self.manager = manager

        self.mainLayout = QGridLayout()
        self.sequencer = Sequencer(self)
        self.logLayout = QGridLayout()

        self.menuBar = self.createMenu()
        self.sequenceTable = Table(self)

        self.commandLine = QLineEdit()
        self.commandLine.returnPressed.connect(self.sendCmdLine)

        self.logArea = LogArea()
        self.logLayout.addWidget(self.logArea, 0, 0, 10, 1)
        self.logLayout.addWidget(self.commandLine, 10, 0, 1, 1)

        self.mainLayout.addWidget(self.menuBar, 0, 0, 1, 10)
        self.mainLayout.addWidget(self.sequenceTable, 1, 0, 10, 10)
        self.mainLayout.addLayout(self.sequencer, 11, 0, 4, 4)

        self.mainLayout.addLayout(self.logLayout, 15, 0, 10, 10)

        self.setMinimumWidth(920)
        self.setLayout(self.mainLayout)

    @property
    def actor(self):
        return self.manager.actor

    def addSequence(self):
        d = Dialog(self)

    def addExperiment(self, experiment):
        self.experiments.append(experiment)
        self.updateTable()

    def copyExperiment(self, experiments, filepath='temp.pickle'):

        copiedExp = [(type(experiment), experiment.kwargs) for experiment in experiments]
        with open(filepath, 'wb') as thisFile:
            pickler = pickle.Pickler(thisFile, protocol=2)
            pickler.dump(copiedExp)

    def pasteExperiment(self, ind, filepath='temp.pickle'):
        try:
            with open(filepath, 'rb') as thisFile:
                unpickler = pickle.Unpickler(thisFile)
                copiedExp = unpickler.load()

        except FileNotFoundError:
            return

        newExp = []

        for t, kwargs in copiedExp:
            newExp.append(t(self, **kwargs))

        self.experiments[ind:ind] = newExp
        self.updateTable()

    def removeExperiment(self, experiments):
        for experiment in experiments:
            if not experiment in self.experiments:
                continue

            self.experiments.remove(experiment)

        self.updateTable()

    def updateTable(self):
        self.sequenceTable.hide()
        self.sequenceTable.close()
        self.sequenceTable.deleteLater()
        self.mainLayout.removeWidget(self.sequenceTable)

        self.sequenceTable = Table(self)
        self.mainLayout.addWidget(self.sequenceTable, 1, 0, 10, 10)

    def sendCmdLine(self):

        self.sendCommand(fullCmd=self.commandLine.text())

    def sendCommand(self, fullCmd, callFunc=None):

        callFunc = self.printResponse if callFunc is None else callFunc
        import opscore.actor.keyvar as keyvar

        [actor, cmdStr] = fullCmd.split(' ', 1)
        self.logArea.newLine('cmdIn=%s %s' % (actor, cmdStr))
        self.actor.cmdr.bgCall(**dict(actor=actor,
                                      cmdStr=cmdStr,
                                      timeLim=600,
                                      callFunc=callFunc,
                                      callCodes=keyvar.AllCodes))

    def printResponse(self, resp):

        reply = resp.replyList[-1]
        code = resp.lastCode

        if self.printLevels[code] >= self.printLevel:
            self.logArea.newLine("%s %s %s" % (reply.header.actor,
                                               reply.header.code.lower(),
                                               reply.keywords.canonical(delimiter=';')))

    def createMenu(self):
        menubar = QMenuBar(self)
        fileMenu = menubar.addMenu('File')
        editMenu = menubar.addMenu('Edit')

        loadSequence = QAction('Open', self)
        loadSequence.triggered.connect(self.loadFile)
        loadSequence.setShortcut('Ctrl+O')

        saveSequence = QAction('Save', self)
        saveSequence.triggered.connect(self.saveFile)
        saveSequence.setShortcut('Ctrl+S')

        addSequence = QAction('Add Sequence', self)
        addSequence.triggered.connect(self.addSequence)

        selectAll = QAction('Select All', self)
        selectAll.triggered.connect(self.selectAll)
        selectAll.setShortcut('Ctrl+A')

        clearDone = QAction('Clear Done', self)
        clearDone.triggered.connect(self.clearDone)

        fileMenu.addAction(loadSequence)
        fileMenu.addAction(saveSequence)

        editMenu.addAction(addSequence)
        editMenu.addAction(selectAll)
        editMenu.addAction(clearDone)

        return menubar

    def loadFile(self):
        bpath = '/'.join(os.getcwd().split('/')[:3])
        filepath, fmt = QFileDialog.getOpenFileName(self, 'Open file', bpath, "Text files (*.txt, *.cfg)")
        if filepath:
            try:
                self.pasteExperiment(ind=0, filepath=filepath)
            except:
                self.manager.showError("Cannot load your file, it may be corrupted")

    def saveFile(self):
        bpath = '/'.join(os.getcwd().split('/')[:3])
        fname, fmt = QFileDialog.getSaveFileName(self, 'Save file', bpath, "Text files (*.txt, *.cfg)")

        if fname:
            filepath = '%s.cfg' % fname if len(fname.split('.')) < 2 else fname
            self.copyExperiment(experiments=self.experiments, filepath=filepath)

    def selectAll(self):
        self.sequenceTable.selectAll()

    def clearDone(self):
        toRemove = [experiment for experiment in self.experiments if experiment.status in ['finished', 'failed']]
        self.removeExperiment(toRemove)
