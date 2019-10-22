"""Configuration object for KiLauncher"""
from pathlib import Path
from dataclasses import dataclass
from PyQt5 import QtGui as qtg
from xdg.DesktopEntry import DesktopEntry

from . import utils


@dataclass
class ButtonConfig:
    name: str = None
    comment: str = None
    icon: qtg.QIcon = None
    icon_size: tuple = None
    launcher_size: tuple = None
    command: str = None
    desktop_file: str = None
    aggressive_icon_search: bool = False
    categories: list = None

    def __str__(self):
        return "ButtonConfig: {}".format(vars(self))

    def __post_init__(self):
        if isinstance(self.icon_size, str):
            self.icon_size = utils.parse_size(self.icon_size)
        if isinstance(self.launcher_size, str):
            self.launcher_size = utils.parse_size(self.launcher_size)

        # Load in details from a .desktop file, if there is one.
        if self.desktop_file:
            try:
                de = DesktopEntry(self.desktop_file)
            except PermissionError as e:
                utils.debug(
                    "Access denied on desktop file: {}, {}"
                    .format(self.desktop_file, e)
                )
            else:
                self.name = de.getName()
                self.comment = de.getComment()
                self.icon = de.getIcon()
                self.command = de.getExec()
                self.categories = [c.lower() for c in de.getCategories()]


@dataclass
class TabConfig:
    name: str
    description: str
    icon: qtg.QIcon = None
    launchers: list = None
    launcher_size: tuple = None
    icon_size: tuple = None
    desktop_path: str = None
    launchers_per_row: int = 3
    categories: list = None
    aggressive_icon_search: bool = False

    def __post_init__(self):
        if self.launchers is None:
            self.launchers = []
        if self.categories is None:
            self.categories = []
        if isinstance(self.icon_size, str):
            self.icon_size = utils.parse_size(self.icon_size)
        if isinstance(self.launcher_size, str):
            self.launcher_size = utils.parse_size(self.launcher_size)

        self.add_desktop_path()

    def add_desktop_path(self):
        """Add launchers to this config from .desktop files in a given path."""
        if not self.desktop_path:
            return
        path = Path(self.desktop_path)
        pattern = '*.desktop'
        if not path.is_dir():
            pattern = path.name
            path = path.parent
            utils.debug(
                '{} dissected into {} and {}'
                .format(self.desktop_path, path, pattern)
            )
        if not path.exists():
            utils.debug(
                "Desktop Path does not exist: {}"
                .format(self.desktop_path)
            )
            return

        categories = set([c.lower() for c in self.categories])
        # if the path is just a directory, we need to add a wildcard to get
        # the desktop files
        for desktop_file in path.glob(pattern):
            button_config = ButtonConfig(
                desktop_file=desktop_file,
                launcher_size=self.launcher_size,
                icon_size=self.icon_size,
                aggressive_icon_search=self.aggressive_icon_search
            )
            in_categories = set(button_config.categories) & categories
            if (  # Filter categories if we've defined them
                    not categories or in_categories
            ):
                self.add_launcher(button_config)

    def add_launcher(self, buttonconfig):
        self.launchers.append(buttonconfig)

    def __str__(self):
        return "TabConfig: {}".format(vars(self))


class KiLauncherConfig:

    options = {
        "stylesheet": {
            "default": "/etc/kilauncher/stylesheet.css",
            "switches": ('-s', '--stylesheet'),
            "action": "store",
            "help": "The QSS stylesheet to apply to the application."
        },
        "launcher_size": {
            "switches": ('--launcher-size',),
            "action": "store",
            "default": '240x80',
            "help": "The default size of launch buttons, in WxH format.",
            "transform": utils.parse_size
        },
        "icon_size": {
            "switches": ('--icon-size',),
            "action": "store",
            "default": "64x64",
            "help": "The default size of icons, in WxH format.",
            "transform": utils.parse_size
        },
        "icon_theme": {
            "switches": ('--icon-theme',),
            "action": "store",
            "help": "Icon theme to use (X11 systems only).",
            "default": None
        },
        "tabs_and_launchers": {
            "default": []
        },
        "aggressive_icon_search": {
            "default": False
        },
        "quit_button_text": {
            "default": "Quit this program"
        },
        "show_quit_button": {
            "switches": ('-b', '--quit-button'),
            "action": "store",
            "help": "Show the quit button to exit the menu",
            "transform": (
                lambda x: x.lower() != 'false' if isinstance(x, str) else x
            ),
            "choices": ["True", "False"],
            "default": False
        },
        "autostart": {
            "default": []
        }
    }

    def __init__(self, file_dict, args_dict):
        """Construct a config from the file and CLI args"""

        for opt_name, opt_conf in self.options.items():
            file_val = file_dict.get(opt_name)
            args_val = args_dict.get(opt_name)
            default_val = opt_conf.get('default')
            value = utils.coalesce(args_val, file_val, default_val)
            if opt_conf.get('transform'):
                value = opt_conf.get('transform')(value)
            setattr(self, opt_name, value)

        self._build_tabs_and_launchers()

        # check some values
        if not Path(self.stylesheet).exists():
            utils.debug(
                "Warning: stylesheet '{}' could not be located.  "
                "Using default."
                .format(self.stylesheet))
            self.stylesheet = None

    def _build_tabs_and_launchers(self):
        """Take the dicts and build objects"""

        cascading_attrs = (
            'icon_size',
            'launcher_size',
            'aggressive_icon_search'
        )
        raw_config = self.tabs_and_launchers
        new_config = list()
        for _, tab in raw_config.items():
            launchers = tab.pop('launchers', [])
            # cascade parent values if they aren't defined for the tab
            for attribute in cascading_attrs:
                tab[attribute] = tab.get(attribute, getattr(self, attribute))
            # create the new tab config and button config
            tab_config = TabConfig(**tab)
            for launcher in launchers:
                for attribute in cascading_attrs:
                    launcher[attribute] = launcher.get(
                        attribute, getattr(tab_config, attribute))
                tab_config.add_launcher(ButtonConfig(**launcher))
            new_config.append(tab_config)

        self.tabs_and_launchers = new_config

    def __str__(self):
        return "KiLauncherConfig: {}".format(vars(self))
