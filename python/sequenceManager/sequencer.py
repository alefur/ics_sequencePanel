__author__ = 'alefur'

from datetime import datetime as dt
from datetime import timedelta

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QGridLayout, QPushButton, QSpinBox, QProgressBar
from sequenceManager.widgets import CLabel, Label


class DelayBar(QProgressBar):
    def __init__(self, mwindow):
        self.mwindow = mwindow
        QProgressBar.__init__(self)
        self.setStyleSheet("QProgressBar { font: 8pt;}")
        self.setVisible(False)
        self.progressing = QTimer(mwindow)
        self.progressing.setInterval(500)
        self.progressing.timeout.connect(self.waitInProgress)

    @property
    def sequencer(self):
        return self.mwindow.sequencer

    @property
    def delta(self):
        return (dt.now() - self.tstart).total_seconds()

    def start(self, delay):
        self.tstart = dt.now()
        self.delay = delay

        self.setValue(0)
        self.setRange(0, delay)
        self.setFormat(
            "Start : %s \r\n " % ((self.tstart + timedelta(seconds=delay)).isoformat())[:-10] + '%p%')
        self.setVisible(True)
        self.progressing.start()

    def stop(self):
        self.progressing.stop()
        self.hide()

    def waitInProgress(self):
        if not self.sequencer.onGoing:
            self.stop()
        else:
            if self.delta < self.delay:
                self.setValue(self.delta)
            else:
                self.stop()
                self.sequencer.activateSequence()


class Sequencer(QGridLayout):
    def __init__(self, mwindow):
        self.mwindow = mwindow
        QGridLayout.__init__(self)
        self.status = CLabel('OFF')
        self.startButton = QPushButton("START")
        self.stopButton = QPushButton("STOP")
        self.abortButton = QPushButton("ABORT")

        self.delayBar = DelayBar(mwindow=mwindow)
        self.delayBar.setFixedSize(160, 28)

        self.delay = QSpinBox()
        self.delay.setValue(0)
        self.delay.setRange(0, 24 * 60 * 10)

        self.startButton.clicked.connect(self.startSequence)
        self.stopButton.clicked.connect(self.stopSequence)
        self.abortButton.clicked.connect(self.abortSequence)

        self.addWidget(Label("Delay (min)"), 0, 1)
        self.addWidget(self.status, 1, 0)
        self.addWidget(self.delay, 1, 1)
        self.addWidget(self.delayBar, 0, 2, 1, 2)

        self.addWidget(self.startButton, 1, 2)
        self.addWidget(self.stopButton, 1, 2)
        self.addWidget(self.abortButton, 1, 3)

        self.stopButton.setVisible(False)

    @property
    def onGoing(self):
        return self.stopButton.isVisible()

    @property
    def validated(self):
        return [experiment for experiment in self.mwindow.experiments if experiment.isValid]

    def startSequence(self):
        self.startButton.setVisible(False)
        self.stopButton.setVisible(True)

        delay = self.delay.value() * 60
        delay = 5 if not delay else delay

        self.startingSoon(delay=delay)

    def startingSoon(self, delay):
        if len(self.validated):
            self.status.setText('WAITING')
            self.delayBar.start(delay=delay)
        else:
            self.stopSequence()

    def activateSequence(self):
        isActive = True in [experiment.isActive for experiment in self.validated]
        self.status.setText('PROCESSING')

        for experiment in self.validated:
            if not isActive:
                experiment.setActive()
                isActive = True
                break

        if not isActive:
            self.stopSequence()

    def stopSequence(self):
        self.status.setText('OFF')
        self.startButton.setVisible(True)
        self.stopButton.setVisible(False)

    def nextPlease(self):
        if self.onGoing:
            self.startingSoon(delay=5)

    def abortSequence(self):
        pass
