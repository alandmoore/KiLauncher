#####################
# Utility Functions #
#####################

import os
import sys
from PyQt5 import QtGui as qtg



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
