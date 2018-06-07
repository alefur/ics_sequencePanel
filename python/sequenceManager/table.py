from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem


class CenteredItem(QTableWidgetItem):
    color = {"init": ("#FF7D7D", "#000000"), "valid": ("#7DFF7D", "#000000"), "active": ("#4A90D9", "#FFFFFF"),
             "finished": ("#5f9d63", "#FFFFFF"), "failed": ("#9d5f5f", "#FFFFFF")}

    def __init__(self, experiment, attr, typeFunc, lock=False, align=Qt.AlignCenter):
        self.experiment = experiment
        self.attr = attr
        self.typeFunc = typeFunc

        QTableWidgetItem.__init__(self, str(getattr(experiment, attr)))
        self.setTextAlignment(align)

        if experiment.status != "init" or lock:
            self.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

        back, col = CenteredItem.color[experiment.status]

        self.setForeground(QColor(col))
        self.setBackground(QColor(back))

    def valueChanged(self):
        val = self.text()
        setattr(self.experiment, self.attr, self.typeFunc(val))


class Table(QTableWidget):
    def __init__(self, mwindow):
        self.mwindow = mwindow
        self.controlKey = False

        colnames = ['', '', '', ' Id ', '  Valid  ', '  Type  ', '  Name  ', '  Comments  ', ' CmdStr ',
                    '  VisitStart  ',
                    '  VisitEnd  ', '  Anomalies  ']

        allRows = [len(experiment.subcommands) if (experiment.showSub and experiment.subcommands) else 2 for experiment in self.experiments]

        QTableWidget.__init__(self, sum(allRows), len(colnames))

        self.setHorizontalHeaderLabels(colnames)

        self.verticalHeader().setDefaultSectionSize(6)
        self.verticalHeader().hide()

        rowNumber = 0
        for experiment in self.experiments:
            self.setRowHeight(rowNumber, 14)
            self.setRowHeight(rowNumber + 1, 14)

            self.setCellWidget(rowNumber, 0, experiment.buttonDelete)
            self.setCellWidget(rowNumber, 1, experiment.buttonMoveUp)
            self.setCellWidget(rowNumber + 1, 1, experiment.buttonMoveDown)
            self.setCellWidget(rowNumber, 2, experiment.buttonEye)
            self.setItem(rowNumber, 3, CenteredItem(experiment, 'id', int, lock=True))
            self.setCellWidget(rowNumber, 4, experiment.valid)
            self.setItem(rowNumber, 5, CenteredItem(experiment, 'type', str, lock=True))
            self.setItem(rowNumber, 6, CenteredItem(experiment, 'name', str))
            self.setItem(rowNumber, 7, CenteredItem(experiment, 'comments', str))

            nb = 2
            if experiment.showSub and experiment.subcommands:
                span = len(experiment.subcommands)
                cols = [0, 2, 3, 4, 5, 6, 7]
                for nb, subcommand in enumerate(experiment.subcommands):
                    self.setRowHeight(rowNumber + nb, 16)
                    self.setItem(rowNumber + nb, 8, CenteredItem(subcommand, 'cmdStr', str))
                    self.setItem(rowNumber + nb, 9, CenteredItem(subcommand, 'visitStart', int, lock=True))
                    self.setItem(rowNumber + nb, 10, CenteredItem(subcommand, 'visitEnd', int, lock=True))
                    self.setItem(rowNumber + nb, 11, CenteredItem(subcommand, 'anomalies', str))
                nb += 1

            else:
                span = 2
                cols = [0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
                self.setItem(rowNumber, 8, CenteredItem(experiment, 'cmdStr', str))
                self.setItem(rowNumber, 9, CenteredItem(experiment, 'visitStart', int, lock=True))
                self.setItem(rowNumber, 10, CenteredItem(experiment, 'visitEnd', int, lock=True))
                self.setItem(rowNumber, 11, CenteredItem(experiment, 'anomalies', str))

            for col in cols:
                self.setSpan(rowNumber, col, span, 1)

            rowNumber += nb

            for j in range(len(colnames)):
                if j == 4:
                    self.setColumnWidth(j, 40)
                else:
                    self.resizeColumnToContents(j)

        self.cellChanged.connect(self.userCellChange)
        self.setFont(self.getFont())
        self.horizontalHeader().setFont(self.getFont(size=11))

    @property
    def experiments(self):
        return self.mwindow.experiments

    def getFont(self, size=10):
        font = self.font()
        font.setPixelSize(size)
        return font

    def userCellChange(self, i, j):
        item = self.item(i, j)
        item.valueChanged()

    def selectAll(self):
        for i in range(self.rowCount()):
            try:
                self.item(i, 2).setSelected(True)
            except AttributeError:
                pass

    def keyPressEvent(self, QKeyEvent):

        try:
            if QKeyEvent.key() == Qt.Key_Control:
                self.controlKey = True

            if QKeyEvent.key() == Qt.Key_C and self.controlKey:

                selectedExp = [item.experiment for item in self.selectedItems()]
                self.mwindow.copyExperiment(selectedExp)

                for range in self.selectedRanges():
                    self.setRangeSelected(range, False)

            elif QKeyEvent.key() == Qt.Key_V and self.controlKey:
                if self.selectedRanges():
                    ind = max([range.bottomRow() for range in self.selectedRanges()]) // 2 + 1
                else:
                    ind = len(self.experiments)

                self.mwindow.pasteExperiment(ind)

            if QKeyEvent.key() == Qt.Key_Delete:
                selectedExp = [item.experiment for item in self.selectedItems()]
                self.mwindow.removeExperiment(selectedExp)

        except KeyError:
            pass

    def keyReleaseEvent(self, QKeyEvent):
        if QKeyEvent.key() == Qt.Key_Control:
            self.controlKey = False
