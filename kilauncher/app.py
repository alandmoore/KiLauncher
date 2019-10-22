import sys
import argparse
import yaml
from pathlib import Path
from PyQt5 import QtWidgets as qtw
from .tabs import KiLauncherTabs
from .config import KiLauncherConfig
from . import utils


class KiLauncherApp(qtw.QApplication):

    # List of places to search for the config file
    # First location gets priority
    config_locations = [
        Path('~/.kilauncher.yaml').expanduser(),
        Path('/etc/kilauncher.yaml'),
        Path('/etc/kilauncher/kilauncher.yaml')
    ]

    def __init__(self):
        super().__init__(sys.argv)

        config_file = ''
        for config_location in self.config_locations:
            if config_location.exists():
                config_file = config_location
                break

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
        for option, opt_data in KiLauncherConfig.options.items():
            if opt_data.get('switches'):
                parser.add_argument(
                    *opt_data.get('switches'),
                    action=opt_data.get('action', 'store_true'),
                    default=opt_data.get('default'),
                    choices=opt_data.get('choices'),
                    dest=option
                )
        args = parser.parse_args()
        config_file = (
            Path(args.config).expanduser()
            if args.config
            else config_file
        )
        if not config_file or not config_file.exists():
            utils.debug("No config file found or specified; exiting")
            sys.exit(1)
        file_config = yaml.safe_load(config_file.read_text())
        config = KiLauncherConfig(file_config, vars(args))
        utils.debug(config)
        self.launcher = KiLauncherTabs(config)
        self.launcher.show()
