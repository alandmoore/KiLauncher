from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc

from .button import LaunchButton


class LauncherMenu(qtw.QWidget):
    """A single pane of launchers on a tab"""
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.launcherlayout = qtw.QGridLayout()
        self.layout = qtw.QVBoxLayout()
        # Show the description
        self.description_layout = qtw.QHBoxLayout()
        self.descriptionLabel = qtw.QLabel(self.config.description)
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

        # figure out the default number of columns by dividing the
        # launcher width by the screen width.
        # Of course, if that's zero (if the launcher is actually wider
        # than the viewport) make it 1
        screen_width = qtw.qApp.desktop().availableGeometry().width()
        self.default_columns = (screen_width // self.config.launcher_size[0]) or 1

        self.columns = self.config.launchers_per_row
        self.current_coordinates = [0, 0]
        for launcher in self.config.launchers:
            b = LaunchButton(self, launcher)
            self.add_launcher_to_layout(b)
        self.scroller.setWidget(self.launcher_widget)

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
