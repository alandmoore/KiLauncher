import os
import sys
import argparse
import yaml
from PyQt5 import QtWidgets as qtw
from .tabs import KiLauncherTabs


class KiLauncherApp(qtw.QApplication):

    # List of places to search for the config file
    config_locations = [
        '/etc/kilauncher/kilauncher.yaml',
        '/etc/kilauncher.yaml',
        '~/.kilauncher.yaml'
    ]

    def __init__(self):
        super().__init__(sys.argv)

        config_file = ''
        for config_location in self.config_locations:
            if os.path.exists(os.path.expanduser(config_location)):
                config_file = config_location

        # Setup arguments
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
        self.launcher = KiLauncherTabs(config, stylesheet=args.stylesheet)
        self.launcher.show()
