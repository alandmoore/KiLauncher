import os
import sys

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg
from xdg.DesktopEntry import DesktopEntry

from . import utils


class LaunchButton(qtw.QPushButton):
    """ This is the actual button you push to launch the program.
    """

    def __init__(self, parent=None, **kwargs):
        """Construct a LaunchButton"""
        super().__init__(parent)
        self.setObjectName("LaunchButton")
        self.launcher_size = kwargs.get("launcher_size")
        self.icon_size = kwargs.get("icon_size")
        self.name = None
        self.comment = None
        self.icon = None
        self.command = None
        self.categories = None

        # Load in details from a .desktop file, if there is one.
        desktop_file = kwargs.get("desktop_file")
        if desktop_file:
            if os.access(desktop_file, os.R_OK):
                de = DesktopEntry(desktop_file)
                self.name = de.getName()
                self.comment = de.getComment()
                self.icon = de.getIcon()
                self.command = de.getExec()
                self.categories = [c.lower() for c in de.getCategories()]
            else:
                sys.stderr.write(
                    "Read access denied on manually-specified "
                    "desktop file {}.  Button may be missing data.\n"
                    .format(desktop_file)
                )

        # This allows for overriding the settings in DesktopEntry
        self.name = kwargs.get("name", self.name)
        self.comment = kwargs.get("comment", self.comment)
        self.icon = kwargs.get("icon", self.icon)
        self.command = kwargs.get("command", self.command)

        # Create the layouts and widgets to hold the information
        toplayout = qtw.QHBoxLayout()
        leftlayout = qtw.QVBoxLayout()

        # The button's title
        title = qtw.QLabel(self.name)
        title.setObjectName("LaunchButtonTitle")
        leftlayout.addWidget(title)

        # The button's descriptive comment
        comment = qtw.QLabel(self.comment)
        comment.setSizePolicy(
            qtw.QSizePolicy.Expanding,
            qtw.QSizePolicy.Expanding
        )
        comment.setWordWrap(True)
        comment.setObjectName("LaunchButtonDescription")
        leftlayout.addWidget(comment)

        # The button's icon, if there is one
        iconpane = qtw.QLabel()
        icon = (
            utils.icon_anyway_you_can(
                self.icon,
                kwargs.get("aggressive_icon_search", False)
            )
            if self.icon else qtg.QIcon()
        )
        # scale the icon
        pixmap = icon.pixmap(*self.icon_size)
        if not pixmap.isNull():
            pixmap = pixmap.scaled(*self.icon_size)
        iconpane.setPixmap(pixmap)

        # Add everything to layouts and layouts to the button
        toplayout.addWidget(iconpane)
        toplayout.addLayout(leftlayout)
        self.setLayout(toplayout)

        # Set the button's size from config.
        self.setSizePolicy(qtw.QSizePolicy.Fixed, qtw.QSizePolicy.Fixed)
        self.setMinimumSize(qtc.QSize(*self.launcher_size))

        # Connect the callback
        self.clicked.connect(self.callback)

    def enable(self, exit_code):
        """Enable the button widget"""
        self.setDisabled(False)

    def enable_with_error(self, error):
        """Enable the button, but display an error."""
        self.setDisabled(False)
        qtw.QMessageBox.critical(
            None,
            "Command Failed!",
            "Sorry, this program isn't working!"
        )

    def callback(self):
        """Run the button's callback function

        Commands are called in a separate thread using QProcess.
        This way, they can indicate to us when they are finished,
        or if they ran correctly, using signals.
        XDG commands in desktop files sometimes have placeholder
        arguments like '%u' or '%f'.
        We're going to strip these out, because they have no meaning in the
        context of a button-push.
        """

        # set the working directory to ~
        os.chdir(os.path.expanduser('~'))
        self.command = ' '.join(
            x for x in self.command.split()
            if x not in ('%f', '%F', '%u', '%U')
        )
        self.p = qtc.QProcess()
        self.p.finished.connect(self.enable)
        self.p.error.connect(self.enable_with_error)
        self.p.start(self.command)
        if not self.p.state() == qtc.QProcess.NotRunning:
            # Disable the button to prevent users clicking
            # 200 times waiting on a slow program.
            self.setDisabled(True)
