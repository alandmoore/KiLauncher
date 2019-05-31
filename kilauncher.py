#!/usr/bin/python
"""
KiLauncher static fullscreen launcher menu
By Alan D Moore
Copyright 2012
Released under the GNU GPL v3
"""

import sys
import glob
import yaml
import os
import argparse

from xdg.DesktopEntry import DesktopEntry

from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg
from PyQt5 import QtWidgets as qtw

DEFAULT_LAUNCHER_SIZE = '240x80'
DEFAULT_ICON_SIZE = '64x64'
DEFAULT_STYLESHEET = '/etc/kilauncher/stylesheet.css'


#####################
# Utility Functions #
#####################

def coalesce(*args):
    for item in args:
        if item:
            return item
    return args[-1]

def recursive_find(rootdir, myfilename):
    return [
        os.path.join(rootdir, filename)
        for rootdir, dirnames, filenames in os.walk(rootdir)
        for filename in filenames
        if filename == myfilename
    ]


def icon_anyway_you_can(icon_name, recursive_search=True):
    """Take an icon name or path, and take various measures
    to return a valid QIcon
    """
    icon = None
    if os.path.isfile(icon_name):
        icon = qtg.QIcon(icon_name)
    elif qtg.QIcon.hasThemeIcon(icon_name):
        icon = qtg.QIcon.fromTheme(icon_name)
    elif os.path.isfile(os.path.join("/usr/share/pixmaps", icon_name)):
        icon = qtg.QIcon(os.path.join("/usr/share/pixmaps", icon_name))
    elif recursive_search:
        # Last ditch effort
        # search through some known (Linux) icon locations
        # This recursive search is really slow, hopefully it can be avoided.
        sys.stderr.write(
            """Warning: had to recursively search for icon "{}".
            Please set a full path to the correct file to reduce startup time.
            """.format(icon_name))
        directories = ["/usr/share/pixmaps",
                       "/usr/share/icons",
                       "/usr/share/icons/hicolor",
                       "/usr/share/" + icon_name]
        extensions = [
            "", "png", "xpm", "svg", "jpg", "jpeg",
            "bmp", "tiff", "tif", "ico"
        ]
        possible_filenames = [
            "{}.{}".format(icon_name, extension)
            for extension in extensions
        ]
        for directory in directories:
            for filename in possible_filenames:
                paths = recursive_find(directory, filename)
                if paths:
                    sys.stderr.write(
                        "(eventually found \"{}\")".format(paths[0]))
                    icon = qtg.QIcon(paths[0])
                    break
            if icon:
                break
        if not icon:
            sys.stderr.write(
                """Couldn't find an icon for "{}".""".format(icon_name))
    return icon or qtg.QIcon()


###############
# GUI classes #
###############

class KiLabel(qtw.QLabel):
    """A label class with additional styling capabilites

    Experimental, not yet in use.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Doesn't work, because stylesheets don't update the palette
        color = self.palette().color(qtg.QPalette.WindowText)
        outline_color = "black" if color.lightness() > 128 else "white"

        ds = qtw.QGraphicsDropShadowEffect(blurRadius=4, color=qtg.QColor(outline_color), xOffset=0, yOffset=0)
        self.setGraphicsEffect(ds)

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
        title = qtw.Label(self.name)
        title.setObjectName("LaunchButtonTitle")
        leftlayout.addWidget(title)

        # The button's descriptive comment
        comment = qtw.Label(self.comment)
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
            icon_anyway_you_can(
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


class KiLauncher(qtw.QTabWidget):
    """The main application"""

    def __init__(self, config, parent=None, **kwargs):
        """Construct the KiLauncher"""
        super().__init__(parent)
        self.setObjectName("KiLauncher")
        self.tabBar().setObjectName("TabBar")
        self.aggressive_icon_search = config.get("aggressive_icon_search")
        self.stylesheet = coalesce(
            kwargs.get('stylesheet'),
            config.get('stylesheet'),
            DEFAULT_STYLESHEET
        )

        if not os.path.exists(self.stylesheet):
            sys.stderr.write(
                "Warning: stylesheet '{}' could not be located.  Using default."
                .format(self.stylesheet))
            self.stylesheet = None

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
        if self.stylesheet:
            with open(self.stylesheet, 'r') as s:
                self.setStyleSheet(s.read())
        if config.get("icon_theme"):
            qtg.QIcon.setThemeName(config.get("icon_theme"))

        # Set up the tabs
        self.tabs = config.get("tabs_and_launchers")
        if self.tabs:
            self.init_tabs()
        else:
            self.setLayout(qtw.QHBoxLayout())
            self.layout().addWidget(
                qtw.QLabel(
                    "No tabs were configured.  "
                    "Please check your configuration file."
                ))
        # Since tabs are not dynamic, just hide them if there's only one.
        show_tabbar = len(self.tabs) > 1
        self.tabBar().setVisible(show_tabbar)

        # Quit button
        if (config.get("show_quit_button")):
            self.quit_button = qtw.QPushButton(
                config.get("quit_button_text") or "X", parent=self)
            self.quit_button.setObjectName("QuitButton")
            if show_tabbar:
                self.setCornerWidget(self.quit_button)
            else:
                self.widget(0).description_layout.addWidget(self.quit_button)
            self.quit_button.clicked.connect(self.close)

        # Run the "autostart" commands
        self.autostart = config.get("autostart", [])
        self.procs = {}
        for command in self.autostart:
            self.procs[command] = qtw.QProcess()
            self.procs[command].start(command)
            self.procs[command].error.connect(self.command_error)

    def command_error(self, error):
        """Called when an autostart has an error"""
        proc = self.sender()
        command = [k for k, v in self.procs.items() if v == proc][0]
        sys.stderr.write(
            """Command "{}" failed with error: {}. """.format(command, error))

    def close(self):
        """Overridden from QWidget to do some cleanup before closing."""
        # Close our auto-started processes.
        for name, process in self.procs.items():
            process.close()
        super().close()
        sys.exit()

    def init_tabs(self):
        """Populate each tab with a LauncherPane of Launchers."""
        for tabordinal, launchers in sorted(self.tabs.items()):
            launchers["aggressive_icon_search"] = self.aggressive_icon_search
            lm = LauncherMenu(launchers)
            launcher_name = launchers.get("name", "Tab {}".format(tabordinal))
            if launchers.get("icon"):
                icon = launchers.get("icon")
                icon = icon_anyway_you_can(icon, False)
                self.addTab(lm, icon, launcher_name)
            else:
                self.addTab(lm, launcher_name)

if __name__ == '__main__':

    # List of places to search for the config file
    config_locations = [
        '/etc/kilauncher/kilauncher.yaml',
        '/etc/kilauncher.yaml',
        '~/.kilauncher.yaml'
    ]
    config_file = ''
    for config_location in config_locations:
        if os.path.exists(os.path.expanduser(config_location)):
            config_file = config_location
    app = qtw.QApplication(sys.argv)
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--config",
        action="store",
        dest="config",
        default=None,
        help="The configuration file to use."
    )
    parser.add_argument(
        "-s",
        "--stylesheet",
        action="store",
        dest="stylesheet",
        default=None,
        help="Override the stylesheet in the config file."
    )
    args = parser.parse_args()
    config_file = args.config or os.path.expanduser(config_file)
    if not config_file:
        sys.stderr.write("No config file found or specified; exiting")
        sys.exit(1)
    with open(config_file, 'r') as c:
        config = yaml.safe_load(c)
    l = KiLauncher(config, stylesheet=args.stylesheet)
    l.show()
    app.exec_()
