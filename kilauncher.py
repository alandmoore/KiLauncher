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
import yaml
import os

class LaunchButton(QPushButton):

    def __init__(self, parent=None, **kwargs):
        super(LaunchButton, self).__init__(parent)
        self.launcher_size = kwargs.get("launcher_size")
        if kwargs.get("desktop_file"):
            de = DesktopEntry(kwargs.get("desktop_file"))
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
        # If the icon is a filename, attempt to load directly.  Otherwise, load from theme.
        icon = (os.path.isfile(self.icon) and QIcon(self.icon)) or QIcon.fromTheme(self.icon)
        i.setPixmap(icon.pixmap(64,64))
        toplayout.addWidget(i)
        toplayout.addWidget(w)
        self.setLayout(toplayout)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setMinimumSize(QSize(*self.launcher_size))

        self.connect(self, SIGNAL("clicked()"), self.callback)

    def callback(self):
        subprocess.call(self.command.split())

class LauncherMenu(QWidget):
    """This is a single pane of launchers on a tab"""
    def __init__(self, config, parent=None):
        super(LauncherMenu, self).__init__(parent)
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.columns = config.get("launchers_per_row", 5)
        self.launcher_size = (config.get("launcher_size") and [int(x) for x in config.get("launcher_size").split('x')]) or [240, 80]
        self.current_coordinates = [0, 0]
        self.config = config
        if self.config.get("desktop_path"):
            self.add_launchers_from_path(self.config.get("desktop_path"))
        if self.config.get("launchers"):
            for launcher in self.config.get("launchers"):
                launcher["launcher_size"] = self.launcher_size
                b = LaunchButton(**launcher)
                self.add_launcher_to_layout(b)
                
    def add_launchers_from_path(self, path):
        for desktop_file in glob.glob(path):
            b = LaunchButton(desktop_file=desktop_file, launcher_size=self.launcher_size)
            self.add_launcher_to_layout(b)

    def add_launcher_to_layout(self, launcher):
        self.layout.addWidget(launcher, self.current_coordinates[0], self.current_coordinates[1])
        self.current_coordinates[1] += 1
        if self.current_coordinates[1] % self.columns == 0:
            self.current_coordinates[1] = 0
            self.current_coordinates[0] += 1


class KiLauncher(QTabWidget):
    """This is the main appliation"""

    def __init__(self, config, parent=None):
        super(KiLauncher, self).__init__(parent)
        self.stylesheet = config.get("stylesheet", 'stylesheet.css')
        self.setWindowState(Qt.WindowFullScreen)

        # Setup the appearance
        if self.stylesheet:
            self.setStyleSheet(open(self.stylesheet, 'r').read())
        if config.get("icon_theme"):
            QIcon.setThemeName(config.get("icon_theme"))

        # Set up the tabs    
        self.tabs = config.get("tabs_and_launchers")
        if self.tabs:
            self.init_tabs()
        else:
            self.setLayout(QHBoxLayout())
            self.layout().addWidget(QLabel("No tabs were configured.  Please check your configuration file."))

    def init_tabs(self):
        for tabname, launchers in self.tabs.iteritems():
            lm = LauncherMenu(launchers)
            self.addTab(lm, tabname)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    config = yaml.safe_load(open('kilauncher.yaml', 'r'))
    l = KiLauncher(config)
    l.show()
    app.exec_()
