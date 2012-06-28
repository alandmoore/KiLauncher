#!/usr/bin/python
# KiLauncher static fullscreen launcher menu
# By Alan D Moore
# Copyright 2012
# Released under the GNU GPL v3

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from xdg.DesktopEntry import DesktopEntry

import sys
import subprocess
import glob


class LaunchButton(QPushButton):

    def __init__(self, parent=None, **kwargs):
        super(LaunchButton, self).__init__(parent)
        if kwargs.get("desktopfile"):
            de = DesktopEntry(kwargs.get("desktopfile"))
            self.name = de.getName()
            self.comment = de.getComment()
            self.icon = de.getIcon()
            self.command = de.getExec()
        else:
            self.name = kwargs.get("name")
            self.comment = kwargs.get("comment")
            self.icon = kwargs.get("icon")
            self.command =  kwargs.get("command")
            
        toplayout = QHBoxLayout()
        leftlayout = QVBoxLayout()
        t = QLabel(self.name)
        t.setStyleSheet("font-weight: bold; font-size: 10pt; text-decoration: underline")
        leftlayout.addWidget(t)
        c = QLabel(self.comment)
        c.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        c.setWordWrap(True)
        c.setStyleSheet("font-weight: normal; font-size: 8pt;")
        leftlayout.addWidget(c)
        w = QWidget()
        w.setLayout(leftlayout)
        i = QLabel()
        i.setPixmap(QIcon.fromTheme(self.icon).pixmap(64,64))
        toplayout.addWidget(i)
        toplayout.addWidget(w)
        self.setLayout(toplayout)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setMinimumSize(QSize(240, 80))

        self.connect(self, SIGNAL("clicked()"), self.callback)

    def callback(self):
        subprocess.call([self.command])

class LauncherMenu(QWidget):

    def __init__(self, parent=None):
        super(LauncherMenu, self).__init__(parent)
        self.setWindowState(Qt.WindowFullScreen)
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.columns = 5
        self.current_coordinates = [0, 0]
        
    def add_launcher_from_xdg_file(self, desktop_file):
        b = LaunchButton(desktopfile=desktop_file)
        self.add_launcher_to_layout(b)

    def add_launcher_to_layout(self, launcher):
        self.layout.addWidget(launcher, self.current_coordinates[0], self.current_coordinates[1])
        self.current_coordinates[1] += 1
        if self.current_coordinates[1] % self.columns == 0:
            self.current_coordinates[1] = 0
            self.current_coordinates[0] += 1

if __name__ == '__main__':
    app = QApplication(sys.argv)
    l = LauncherMenu()
    l.setStyleSheet(open("stylesheet.css", 'r').read())
    for d in glob.glob("/usr/share/applications/s*.desktop"):
        l.add_launcher_from_xdg_file(d)
    l.show()
    app.exec_()
