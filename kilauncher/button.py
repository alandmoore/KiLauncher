from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg

from . import utils


class LaunchButton(qtw.QPushButton):
    """ This is the actual button you push to launch the program.
    """

    def __init__(self, parent, config):
        """Construct a LaunchButton"""
        super().__init__(parent)
        self.config = config
        self.setObjectName("LaunchButton")

        self.name = self.config.name
        self.comment = self.config.comment
        self.icon = self.config.icon
        self.command = self.config.command
        self.process = None
        self.error_log = list()
        self.output_log = list()

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
                self.config.aggressive_icon_search
            )
            if self.icon else qtg.QIcon()
        )
        # scale the icon
        pixmap = icon.pixmap(*self.config.icon_size)
        if not pixmap.isNull():
            pixmap = pixmap.scaled(*self.config.icon_size)
        iconpane.setPixmap(pixmap)

        # Add everything to layouts and layouts to the button
        toplayout.addWidget(iconpane)
        toplayout.addLayout(leftlayout)
        self.setLayout(toplayout)

        # Set the button's size from config.
        self.setSizePolicy(qtw.QSizePolicy.Fixed, qtw.QSizePolicy.Fixed)
        self.setMinimumSize(qtc.QSize(*self.config.launcher_size))

        # Connect the callback
        self.clicked.connect(self.callback)

    def enable(self, exit_code):
        """Enable the button widget"""
        self.setDisabled(False)

    def enable_with_error(self, error_code):
        """Enable the button, but display an error."""
        self.setDisabled(False)
        print(self.error_log)
        print(self.output_log)

        qtw.QMessageBox.critical(
            None,
            "Command Failed!",
            "Sorry, this program isn't working!"
        )

    def log_error(self):
        if self.process:
            error = bytes(self.process.readAllStandardError())
            self.error_log.append(error.decode('utf-8'))

    def log_output(self):
        if self.process:
            output = bytes(self.process.readAllStandardOutput())
            self.output_log.append(output.decode('utf-8'))

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
        self.error_log.clear()
        self.output_log.clear()

        self.command = ' '.join(
            x for x in self.command.split()
            if x not in ('%f', '%F', '%u', '%U')
        )
        self.process = qtc.QProcess()
        # cannot be a kwarg
        self.process.setWorkingDirectory(qtc.QDir.homePath())
        self.process.finished.connect(self.enable)
        self.process.errorOccurred.connect(self.enable_with_error)
        # This should log standard error and standard output
        # Doesn't always catch stuff though.
        self.process.readyReadStandardError.connect(self.log_error)
        self.process.readyReadStandardOutput.connect(self.log_output)
        self.process.start(self.command)
        if not self.process.state() == qtc.QProcess.NotRunning:
            # Disable the button to prevent users clicking
            # 200 times waiting on a slow program.
            self.setDisabled(True)
