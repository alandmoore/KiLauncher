============
 KiLauncher
============

----------------------
A full-screen launcher
----------------------

Author
======

written by Alan D Moore (http://www.alandmoore.com)
Copyright 2012

Abstract
========

KiLauncher is a static full-screen launcher menu.  It features:

- Themeable appearance using (a subset of) CSS
- Static configuration
- Plaintext YAML configuration file
- Support for XDG .desktop launcher files

KiLauncher is aimed at situations where you want to provide a user with a simple, limited interface to an explicit set of applications.  It's possibly useful for:

- Kiosks (hence the name), CyberCafe, or other publicly-accessible computers
- Computers for children or computer novices who just want to launch a few programs easily
- Call centers, labs, POS systems, or other "locked down" workstations

What KiLauncher is NOT
~~~~~~~~~~~~~~~~~~~~~~

- It's not a desktop environment, window manager, task manager, or desktop shell.  Just a launcher.
- It's not a total lockdown solution.  You still need to address the lockdown of your desktop, launched programs, etc.
- It's not a dynamically-updating menu replacement that will automagically configure new launchers for you.
- It's not tested on platforms other than GNU/Linux on a regular basis.

Requirements
============

- python (should work with python 3.x or any recent python 2.x)
- pyqt4
- python-yaml
- python-xdg
- python-argparse

Usage
=====

Configuration file
~~~~~~~~~~~~~~~~~~

The kilauncher.yaml file is an example configuration file, and is well commented to show how shortcuts can be configured.  Basically, you can give it directories full of .desktop files, individual .desktop files, or explicit name/comment/icon/command values to define launchers for each tab.

If a config file is not specified on the command line, kilauncher will use ~/.kilauncher.yaml.  If that doesn't exist, it will use /etc/kilauncher.yaml.  If neither location exists and a file isn't specified, the program will just print an error to stdout and exit.

At minimum, a configuration file needs to contain:

- a "tabs_and_launchers" array
- at least one tab in the array
- at least one launcher in the tab


Global options
++++++++++++++

These options can be specified anywhere in the configuration file.

====================== ================ =============================================================================
Option                 Default          Description
====================== ================ =============================================================================
stylesheet             "stylesheet.css" Path to a stylesheet to use
icon_theme             (empty)          Name of an icon theme to use when only an icon name is specified
show_quit_button       false            If true, show a button on the top right to allow the user to quit
quit_button_text       "X"              The text to display on the quit button, if it's shown.
aggressive_icon_search false            If true, do a comprehensive recursive search to find icons for each launcher.
====================== ================ =============================================================================

Tab Options
+++++++++++

A tab is a single entry in the "tabs_and_launchers" dictionary.  They key for each tab can be anything, but it's only used for sorting the tabs, so it's probably best just to use ordinal integers or something else easy to sort.

Each tab can define the following options:
================== ========================================================================================================================================================================================
Option             Description
================== ========================================================================================================================================================================================
name               This is the name of the tab, which appears on the tab widget
description        This is a piece of text which appears at the top of the tab, above the launchers.
icon               This is an image which will appear on the tab widget, next to the name
desktop_path       This is a path to a directory of xdg desktop files which will be used to auto-generate the menu.  Globbing can be used here, so for example "/usr/share/applications/*.desktop" works.
launchers_per_row  Normally the program automatically calculates the number of launchers in a row according to available space, but you can hard-code it here to control the layout somewhat.
launcher_size      This is a set of dimensions in the format <width>x<height>, e.g. 240x180, which determine the size of the launcher buttons.
icon_size          This is a set of dimensions in the format <width>x<height>, e.g. 75x50, which determine the size of the icons on the launcher buttons.
launchers          This is an array of launcher specifications; see the next section for details.
================== ========================================================================================================================================================================================


Launcher Options
++++++++++++++++

The "launchers" array in a tab contains individual dictionaries that describe a launcher button.  The following options are available:

============   ===================================================================================================
Option         Description
============   ===================================================================================================
desktop_file    A path to an xdg desktop file from which the launcher details can be extracted.
name            The name that will appear on the launcher
comment         A comment or description that will appear on the launcher
icon            A path to, or (if using a theme) name of and icon to use on the launcher.
command         The command that will be run when the launcher is clicked.
============   ===================================================================================================

If you specify a desktop_file, the name, comment, icon, and command will be read from that file, and you don't need to specify them individually.
You //can//, however, if you want to: explicitly defining those things will override the settings in the .desktop_file.
If you want to explicitly specify all four settings, it is redundant and pointless to specify a desktop_file.
Be careful using a lot of fancy stuff in your "command" string -- e.g. pipes, redirects, quoted arguments, etc.
It's probably best to put complex commands in a script and just call the script in your command string.

Stylesheet
~~~~~~~~~~

The stylesheet.css file is where the style info is kept.  It uses QT Stylesheet code, NOT regular CSS.  It's close, but the former is a subset so not everything works, and some things don't work like you'd expect.

The included example stylesheets should give you a good starting point for styling the application.  To learn more about QT stylesheets and what's supported, see `http://qt-project.org/doc/qt-4.8/stylesheet-reference.html`_.


Command line options
~~~~~~~~~~~~~~~~~~~~

The current command line options available are:

================ =============================================================
Switch           Description
================ =============================================================
-c, --config     Specify a configuration file to use
-s, --stylesheet Override the stylesheet in the config file (nice for testing)
================ =============================================================


How I'd likely use it
~~~~~~~~~~~~~~~~~~~~~

Here's an example of how I'd likely make use of KiLauncher on a kiosk.

- Set up a basic Linux system, create a kiosk user
- create my custom kilauncher.yaml file, and place it in /etc

  - The easiest way, if you're just launching regular applications, is either copying .desktop files from /usr/share/applications into a folder then specifying that directory in the tab's desktop_directory option.
  - Alternately, you can just leave them in /usr/share/applications and manually specify them in the launcher list using desktop_file.
  - If you have a bunch of custom scripts or custom applications, it's probably easier to specify the name/icon/description/command manually in the launcher list.

- (optionally) customize stylesheet.css, and maybe put it with kilauncher.yaml in /etc
- In my kiosk user's home directory, create a .xsession file like so::

    xset s off
    xset -dpms
    openbox & #simple, minimal window manager
    tint2 & #minimal, menu-less task bar
    python kilauncher -c /etc/kilauncher.yaml -s /etc/stylesheet.css

- Configure my kiosk to auto-login to my kiosk user and use its custom session.

More info on setting up kiosk systems on Linux can be found on the author's blog:

http://www.alandmoore.com/blog/2011/11/05/creating-a-kiosk-with-linux-and-x11-2011-edition


Contributing
============

Contributions are welcome, as long as they keep the software developing along the same intended functions.  Some key points:

- the menu needs to remain static and hand-configurable (explicit configuration enables an administrator to control what's launchable)
- the appearance also needs to be hand-configurable
- Generally speaking, it needs to be appropriate for a public or locked-down kiosk

License
=======

KiLauncher, its documentation, and sample config files are released under the GNU GPL v3.  Please see the included COPYING file for details.
