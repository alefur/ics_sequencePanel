__author__ = 'alefur'

from PyQt5.QtWidgets import QGridLayout, QVBoxLayout, QLabel, QDialog, QDialogButtonBox
from sequenceManager.experiment import ExperimentRow
from sequenceManager.widgets import Label, LineEdit, ComboBox


class ExperimentLayout(QGridLayout):
    def __init__(self,
                 type='Experiment',
                 commandParse=('spsait expose', 'arc <exptime>')):

        QGridLayout.__init__(self)

        self.typeLabel = Label('Type')
        self.type = Label(type)

        self.nameLabel = Label('Name')
        self.name = LineEdit('')

        self.commentsLabel = Label('Comments')
        self.comments = LineEdit('')

        self.cmdStrLabel = Label('CmdStr')
        self.cmdStr = LineEdit('spsait expose arc exptime=2.0 duplicate=3')

        self.addWidget(self.typeLabel, 1, 0)
        self.addWidget(self.type, 1, 1)

        self.addWidget(self.nameLabel, 2, 0)
        self.addWidget(self.name, 2, 1)

        self.addWidget(self.commentsLabel, 3, 0)
        self.addWidget(self.comments, 3, 1)

        self.addWidget(self.cmdStrLabel, 4, 0)
        self.addWidget(self.cmdStr, 4, 1)

    def clearLayout(self):
        while self.count():
            item = self.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()


class CommandLayout(ExperimentLayout):
    def __init__(self):
        ExperimentLayout.__init__(self, type='Command')
        self.nameLabel.setDisabled(True)
        self.name.setDisabled(True)
        self.commentsLabel.setDisabled(True)
        self.comments.setDisabled(True)


class Dialog(QDialog):
    def __init__(self, mwindow):
        QDialog.__init__(self, mwindow)
        self.mwindow = mwindow
        self.availableSeq = dict(Command=CommandLayout,
                                 Experiment=ExperimentLayout)

        vbox = QVBoxLayout()
        self.grid = QGridLayout()
        self.grid.setSpacing(10)

        self.comboLabel = QLabel('Sequence type')

        self.comboType = ComboBox()
        self.comboType.addItems(list(self.availableSeq.keys()))
        self.comboType.currentIndexChanged.connect(self.showRelevantWidgets)
        self.comboType.setCurrentIndex(1)

        self.grid.addWidget(self.comboLabel, 1, 0)
        self.grid.addWidget(self.comboType, 1, 1)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Apply | QDialogButtonBox.Close)
        buttonBox.button(QDialogButtonBox.Apply).clicked.connect(self.addSequence)
        buttonBox.button(QDialogButtonBox.Close).clicked.connect(self.close)

        self.setLayout(vbox)

        vbox.addLayout(self.grid)
        vbox.addWidget(buttonBox)

        self.setWindowTitle('Add Sequence')
        self.setVisible(True)
        self.setMinimumWidth(400)

    def showRelevantWidgets(self):
        try:
            self.seqLayout.clearLayout()
            self.grid.removeItem(self.seqLayout)

        except Exception as e:
            pass

        obj = self.availableSeq[self.comboType.currentText()]
        self.seqLayout = obj()
        self.grid.addLayout(self.seqLayout, 2, 0, self.seqLayout.rowCount(), self.seqLayout.columnCount())

    def addSequence(self):
        type = self.seqLayout.type.text()
        name = self.seqLayout.name.text()
        comments = self.seqLayout.comments.text()
        cmdStr = self.seqLayout.cmdStr.text()

        experiment = ExperimentRow(self.mwindow, type=type, name=name, comments=comments, cmdStr=cmdStr)
        self.mwindow.addExperiment(experiment=experiment)
