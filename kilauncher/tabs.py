import sys
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg

from . import utils
from .menu import LauncherMenu


class KiLauncherTabs(qtw.QTabWidget):
    """The main application"""

    def __init__(self, config, parent=None, **kwargs):
        """Construct the KiLauncher"""
        super().__init__(parent)
        self.setObjectName("KiLauncher")
        self.tabBar().setObjectName("TabBar")
        self.config = config

        # Ideally, the menu should be full screen,
        # but always stay beneath other windows
        self.setWindowState(qtc.Qt.WindowFullScreen)
        self.setWindowFlags(  # Prevents window decorations
            qtc.Qt.Window | qtc.Qt.FramelessWindowHint
        )
        # Put KiLauncher on bottom and prevent it covering other windows
        self.setAttribute(qtc.Qt.WA_X11NetWmWindowTypeDesktop)
        self.setAttribute(qtc.Qt.WA_X11DoNotAcceptFocus)
        self.setAttribute(qtc.Qt.WA_DeleteOnClose)

        # "fullscreen" doesn't always work, depending on the WM.
        # This is a workaround.
        self.resize(qtw.qApp.desktop().availableGeometry().size())

        # Setup the appearance
        if self.config.stylesheet:
            with open(self.config.stylesheet, 'r') as s:
                self.setStyleSheet(s.read())
        if self.config.icon_theme:
            qtg.QIcon.setThemeName(self.config.icon_theme)

        # Set up the tabs
        if self.config.tabs_and_launchers:
            self.init_tabs()
        else:
            self.setLayout(qtw.QHBoxLayout())
            self.layout().addWidget(
                qtw.QLabel(
                    "No tabs were configured.  "
                    "Please check your configuration file."
                ))
        # Since tabs are not dynamic, just hide them if there's only one.
        show_tabbar = len(self.config.tabs_and_launchers) > 1
        self.tabBar().setVisible(show_tabbar)

        # Quit button
        if (self.config.show_quit_button):
            self.quit_button = qtw.QPushButton(self.config.quit_button_text)
            self.quit_button.setObjectName("QuitButton")
            if show_tabbar:
                self.setCornerWidget(self.quit_button)
            else:
                # if we aren't showing the tab bar,
                # add the button to the widget in tab 0
                self.widget(0).description_layout.addWidget(self.quit_button)
            self.quit_button.clicked.connect(self.close)

        # Run the "autostart" commands
        self.procs = {}
        for command in self.config.autostart:
            self.procs[command] = qtc.QProcess()
            self.procs[command].start(command)
            self.procs[command].error.connect(self.command_error)

    def command_error(self, error):
        """Called when an autostart has an error"""
        proc = self.sender()
        command = [k for k, v in self.procs.items() if v == proc][0]
        utils.debug(
            """Command "{}" failed with error: {}. """
            .format(command, error)
        )

    def close(self):
        """Overridden from QWidget to do some cleanup before closing."""
        # Close our auto-started processes.
        for name, process in self.procs.items():
            process.close()
        super().close()
        sys.exit()

    def init_tabs(self):
        """Populate each tab with a LauncherPane of Launchers."""
        for tabordinal, launchers in enumerate(self.config.tabs_and_launchers):
            lm = LauncherMenu(launchers)
            launcher_name = launchers.name
            if launchers.icon:
                icon = utils.icon_anyway_you_can(launchers.icon, False)
                self.addTab(lm, icon, launcher_name)
            else:
                self.addTab(lm, launcher_name)
