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

        colnames = ['', '', ' Id ', '  Valid  ', '  Type  ', '  Name  ', '  Comments  ', ' CmdStr ', '  VisitStart  ',
                    '  VisitEnd  ', '  Anomalies  ']

        QTableWidget.__init__(self, len(self.mwindow.experiments) * 2, len(colnames))

        self.setHorizontalHeaderLabels(colnames)

        self.verticalHeader().setDefaultSectionSize(6)
        self.verticalHeader().hide()

        for i, experiment in enumerate(self.experiments):
            self.setCellWidget(2 * i, 0, experiment.buttonDelete)
            self.setCellWidget(2 * i, 1, experiment.buttonMoveUp)
            self.setCellWidget(2 * i + 1, 1, experiment.buttonMoveDown)

            self.setItem(2 * i, 2, CenteredItem(experiment, 'id', int, lock=True))
            self.setCellWidget(2 * i, 3, experiment.valid)
            self.setItem(2 * i, 4, CenteredItem(experiment, 'type', str, lock=True))
            self.setItem(2 * i, 5, CenteredItem(experiment, 'name', str))
            self.setItem(2 * i, 6, CenteredItem(experiment, 'comments', str))
            self.setItem(2 * i, 7, CenteredItem(experiment, 'cmdStr', str))
            self.setItem(2 * i, 8, CenteredItem(experiment, 'visitStart', int, lock=True))
            self.setItem(2 * i, 9, CenteredItem(experiment, 'visitEnd', int, lock=True))
            self.setItem(2 * i, 10, CenteredItem(experiment, 'anomalies', str))

            self.setRowHeight(2 * i + 1, 14)
            self.setRowHeight(2 * i, 14)

            for j in range(len(colnames)):
                if j == 3:
                    self.setColumnWidth(j, 40)
                else:
                    self.resizeColumnToContents(j)

                if j == 1:
                    continue

                self.setSpan(2 * i, j, 2, 1)

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
