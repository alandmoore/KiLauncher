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
import argparse


class LaunchButton(QPushButton):
    """This is the actual button you push to launch the program."""
    
    def __init__(self, parent=None, **kwargs):
        super(LaunchButton, self).__init__(parent)
        self.setObjectName("LaunchButton")
        self.launcher_size = kwargs.get("launcher_size")
        self.icon_size = kwargs.get("icon_size")
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
        title = QLabel(self.name)
        title.setObjectName("LaunchButtonTitle")
        leftlayout.addWidget(title)
        comment = QLabel(self.comment)
        comment.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        comment.setWordWrap(True)
        comment.setObjectName("LaunchButtonDescription")

        leftlayout.addWidget(comment)
        textpane = QWidget()
        textpane.setLayout(leftlayout)
        iconpane = QLabel()
        # If the icon is a filename, attempt to load directly.  Otherwise, load from theme.
        if self.icon:
            icon = (os.path.isfile(self.icon) and QIcon(self.icon)) or QIcon.fromTheme(self.icon)
        else:
            icon = QIcon()
        iconpane.setPixmap(icon.pixmap(*self.icon_size))
        toplayout.addWidget(iconpane)
        toplayout.addWidget(textpane)
        self.setLayout(toplayout)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setMinimumSize(QSize(*self.launcher_size))

        self.connect(self, SIGNAL("clicked()"), self.callback)

    def callback(self):
        try:
            subprocess.call(self.command.split())
        except:
            QMessageBox.critical(None, "Command Failed!", "Sorry, this program isn't working!")
            
class LauncherMenu(QWidget):
    """This is a single pane of launchers on a tab"""
    def __init__(self, config, parent=None):
        super(LauncherMenu, self).__init__(parent)
        self.config = config
        self.launcherlayout = QGridLayout()
        self.layout = QVBoxLayout()
        # Show the description
        self.descriptionLabel = QLabel(self.config.get("description"))
        self.descriptionLabel.setObjectName("TabDescription")
        self.layout.addWidget(self.descriptionLabel)
        self.scroller = QScrollArea()
        self.scroller.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroller.setWidgetResizable(True)
        self.launcher_widget = QWidget(self)
        self.launcher_widget.setObjectName("LauncherPane")
        self.launcher_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.launcher_widget.setLayout(self.launcherlayout)
        self.layout.addWidget(self.scroller)
        self.setLayout(self.layout)
        self.columns = config.get("launchers_per_row", 5)
        self.launcher_size = (config.get("launcher_size") and [int(x) for x in config.get("launcher_size").split('x')]) or [240, 80]
        self.icon_size = (config.get("icon_size") and [int(x) for x in config.get("icon_size").split('x')]) or [64, 64]
        self.current_coordinates = [0, 0]
        if self.config.get("desktop_path"):
            self.add_launchers_from_path(self.config.get("desktop_path"))
        if self.config.get("launchers"):
            for launcher in self.config.get("launchers"):
                launcher["launcher_size"] = self.launcher_size
                launcher["icon_size"] = self.icon_size
                b = LaunchButton(**launcher)
                self.add_launcher_to_layout(b)
        self.scroller.setWidget(self.launcher_widget)

    def add_launchers_from_path(self, path):
        for desktop_file in glob.glob(path):
            b = LaunchButton(desktop_file=desktop_file, launcher_size=self.launcher_size, icon_size=self.icon_size)
            self.add_launcher_to_layout(b)

    def add_launcher_to_layout(self, launcher):
        self.launcherlayout.addWidget(launcher, self.current_coordinates[0], self.current_coordinates[1])
        self.current_coordinates[1] += 1
        if self.current_coordinates[1] % self.columns == 0:
            self.current_coordinates[1] = 0
            self.current_coordinates[0] += 1

class KiLauncher(QTabWidget):
    """This is the main appliation"""

    def __init__(self, config, parent=None, **kwargs):
        super(KiLauncher, self).__init__(parent)
        self.setObjectName("KiLauncher")
        self.tabBar().setObjectName("TabBar")
        self.stylesheet = kwargs.get("stylesheet") or config.get("stylesheet", 'stylesheet.css')
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

        #Quit button
        if (config.get("show_quit_button")):
            self.quit_button = QPushButton(config.get("quit_button_text") or "X")
            self.setCornerWidget(self.quit_button)
            self.connect(self.quit_button, SIGNAL("clicked()"), self.close)


    def init_tabs(self):
        for tabordinal, launchers in sorted(self.tabs.items()):
            lm = LauncherMenu(launchers)
            if launchers.get("icon"):
                icon = launchers.get("icon")
                icon = (os.path.isfile(icon) and QIcon(icon)) or QIcon.fromTheme(icon)
                self.addTab(lm, icon, launchers.get("name"))
            else:
                self.addTab(lm, launchers.get("name"))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", action="store", dest="config", default="kilauncher.yaml", help="The configuration file to use.")
    parser.add_argument("-s", "--stylesheet", action="store", dest="stylesheet", default=None, help="Override the stylesheet in the config file.")
    args = parser.parse_args()
    config = yaml.safe_load(open(args.config, 'r'))
    l = KiLauncher(config, stylesheet=args.stylesheet)
    l.show()
    app.exec_()
