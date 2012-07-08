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

The program is still kind of in alpha state, so the exact usage is in flux.  

The kilauncher.yaml file is the configuration file, and is well commented to show how shortcuts can be configured.  Basically, you can give it directories full of .desktop files, individual .desktop files, or explicit name/comment/icon/command values to define launchers for each tab.

The stylesheet.css file is where the style info is kept.  It uses QT Stylesheet code, NOT regular CSS.  It's close, but the former is a subset so not everything works, and some things don't work like you'd expect.

The current command line options available are: 

================ =============================================================
Switch           Description
================ =============================================================
-c, --config     Specify a configuration file to use
-s, --stylesheet Override the stylesheet in the config file (nice for testing)
================ =============================================================


How I'd likely use it
~~~~~~~~~~~~~~~~~~~~~

Here's an example of how I'd likely make use of KiLauncher on a kiosk, for instace.

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
  
