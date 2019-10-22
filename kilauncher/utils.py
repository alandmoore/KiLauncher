#####################
# Utility Functions #
#####################

import os
import sys
import re
import datetime
from pathlib import Path

from PyQt5 import QtGui as qtg


def debug(message):
    timestamp = datetime.datetime.now().isoformat()
    sys.stderr.write('{}:  '.format(timestamp))
    sys.stderr.write(str(message))
    sys.stderr.write('\n')


def coalesce(*args):
    for item in args:
        if item:
            return item
    return args[-1]


def recursive_find(rootdir, myfilename):
    yield from Path(rootdir).rglob(myfilename)


def parse_size(size_string):
    """Translates a WxH string to a tuple of ints"""

    if not re.match(r'^\d+x\d+$', size_string):
        raise ValueError(f'Size string not understood: {size_string}')
    size = [
        int(x)
        for x in size_string.split('x')
    ][:2]
    return size


def icon_anyway_you_can(icon_name, recursive_search=True):
    """Take an icon name or path, and take various measures
    to return a valid QIcon
    """
    icon = None
    if Path(icon_name).is_file():
        icon = qtg.QIcon(icon_name)
    elif qtg.QIcon.hasThemeIcon(icon_name):
        icon = qtg.QIcon.fromTheme(icon_name)
    elif (Path("/usr/share/pixmaps") / icon_name).is_file():
        icon = qtg.QIcon(str(Path("/usr/share/pixmaps") / icon_name))
    elif recursive_search:
        # Last ditch effort
        # search through some known (Linux) icon locations
        # This recursive search is really slow, hopefully it can be avoided.
        debug(
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
                # strip path elements from filename
                filename = Path(filename).name
                for path in recursive_find(directory, filename):
                    debug(
                        "(eventually found \"{}\")".format(path))
                    icon = qtg.QIcon(str(path))
                    break
            if icon:
                break
        if not icon:
            debug(
                """Couldn't find an icon for "{}".""".format(icon_name))
    return icon or qtg.QIcon()
