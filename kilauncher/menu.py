import os
import sys
import glob

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc

from .button import LaunchButton
from .defaults import DEFAULT_LAUNCHER_SIZE, DEFAULT_ICON_SIZE


class LauncherMenu(qtw.QWidget):
    """A single pane of launchers on a tab"""
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.launcherlayout = qtw.QGridLayout()
        self.layout = qtw.QVBoxLayout()
        # Show the description
        self.description_layout = qtw.QHBoxLayout()
        self.descriptionLabel = qtw.QLabel(self.config.get("description"))
        self.descriptionLabel.setObjectName("TabDescription")
        self.descriptionLabel.setSizePolicy(
            qtw.QSizePolicy.Expanding,
            qtw.QSizePolicy.Maximum
        )
        self.description_layout.addWidget(self.descriptionLabel)
        self.layout.addItem(self.description_layout)
        self.scroller = qtw.QScrollArea()
        self.scroller.setHorizontalScrollBarPolicy(qtc.Qt.ScrollBarAlwaysOff)
        self.scroller.setWidgetResizable(True)
        self.launcher_widget = qtw.QWidget(self)
        self.launcher_widget.setObjectName("LauncherPane")
        self.launcher_widget.setSizePolicy(
            qtw.QSizePolicy.Expanding,
            qtw.QSizePolicy.Expanding
        )
        self.launcher_widget.setLayout(self.launcherlayout)
        self.layout.addWidget(self.scroller)
        self.setLayout(self.layout)
        self.launcher_size = [
            int(x) for x
            in config.get("launcher_size", DEFAULT_LAUNCHER_SIZE).split('x')
        ]

        self.icon_size = [
            int(x) for x
            in config.get("icon_size", DEFAULT_ICON_SIZE).split('x')
        ]

        # figure out the default number of columns by dividing the
        # launcher width by the screen width.
        # Of course, if that's zero (if the launcher is actually wider
        # than the viewport) make it 1
        screen_width = qtw.qApp.desktop().availableGeometry().width()
        self.default_columns = (screen_width // self.launcher_size[0]) or 1

        self.columns = config.get("launchers_per_row", self.default_columns)
        self.current_coordinates = [0, 0]
        if self.config.get("desktop_path"):
            self.add_launchers_from_path(self.config.get("desktop_path"))
        for launcher in self.config.get("launchers", []):
            launcher["launcher_size"] = self.launcher_size
            launcher["icon_size"] = self.icon_size
            launcher["aggressive_icon_search"] = self.config.get(
                "aggressive_icon_search", False)
            b = LaunchButton(**launcher)
            self.add_launcher_to_layout(b)
        self.scroller.setWidget(self.launcher_widget)

    def add_launchers_from_path(self, path):
        """Add launchers to this pane from .desktop files in a given path."""
        categories = [c.lower() for c in self.config.get("categories", [])]
        # if the path is just a directory, we need to add a wildcard to get
        # the desktop files
        if os.path.isdir(path):
            path = os.path.join(path, "*.desktop")
        for desktop_file in glob.glob(path):
            if os.access(desktop_file, os.R_OK):
                b = LaunchButton(
                    desktop_file=desktop_file,
                    launcher_size=self.launcher_size,
                    icon_size=self.icon_size,
                    aggressive_icon_search=self.config.get(
                        "aggressive_icon_search"))
                if (
                    not categories or
                    len([c for c in b.categories if c in categories])
                ):
                    self.add_launcher_to_layout(b)
            else:
                sys.stderr.write(
                    ("Read access denied for {} in specified path {}."
                     "  Skipping.\n").format(desktop_file, path)
                )

    def add_launcher_to_layout(self, launcher):
        """Add a launcher object to the pane."""
        self.launcherlayout.addWidget(
            launcher,
            self.current_coordinates[0],
            self.current_coordinates[1]
        )
        self.current_coordinates[1] += 1
        if self.current_coordinates[1] % self.columns == 0:
            self.current_coordinates[1] = 0
            self.current_coordinates[0] += 1
