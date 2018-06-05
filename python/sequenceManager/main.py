__author__ = 'alefur'

import argparse
import os
import pwd
import sys

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from mainwindow import ManagerWidget


class SequenceManager(QMainWindow):
    def __init__(self, reactor, actor, d_width, d_height, cmdrName):
        QMainWindow.__init__(self)
        self.reactor = reactor
        self.actor = actor
        self.display = d_width, d_height
        self.setName("%s.%s" % ("sequenceManager", cmdrName))

        self.managerWidget = ManagerWidget(self)
        self.setCentralWidget(self.managerWidget)

        self.show()

    def setName(self, name):
        self.cmdrName = name
        self.setWindowTitle(name)

    def showError(self, error):
        return QMessageBox.critical(self, 'Warning', error, QMessageBox.Ok, QMessageBox.Cancel)

    def closeEvent(self, QCloseEvent):
        self.reactor.callFromThread(self.reactor.stop)
        QCloseEvent.accept()


def main():
    app = QApplication(sys.argv)

    parser = argparse.ArgumentParser()

    parser.add_argument('--name', default=pwd.getpwuid(os.getuid()).pw_name, type=str, nargs='?', help='cmdr name')
    parser.add_argument('--stretch', default=0.6, type=float, nargs='?', help='window stretching factor')

    args = parser.parse_args()

    geometry = app.desktop().screenGeometry()
    import qt5reactor

    qt5reactor.install()
    from twisted.internet import reactor

    import miniActor

    actor = miniActor.connectActor(['hub'])

    try:
        ex = SequenceManager(reactor,
                             actor,
                             geometry.width() * args.stretch,
                             geometry.height() * args.stretch,
                             args.name)
    except:
        actor.disconnectActor()
        raise

    reactor.run()
    actor.disconnectActor()


if __name__ == "__main__":
    main()
