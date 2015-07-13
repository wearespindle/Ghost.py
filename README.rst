About
=====

Ghostrunner is a fork of ghost.py(https://github.com/jeanphix/Ghost.py);
a webkit web client written in python. It was forked to suit our needs for a
reliable fast browser tester that worked well with Django. Ghostrunner features:

* Django LiveServerTestCase with transaction support (sqlite)
* PyQT5 support, running a more recent, less buggy, QtWebkit version.

Ghostrunner requires PyQT5 to work properly. PySide still uses Qt4, which
segfaults randomly during tests. This is probably related to an old version
of QtWebkit.


Usage
=====

Manual setup
------------
1. Install PyQt5

::

    sudo pacman -S pyqt5-common python2-pyqt5 # archlinux

2. Install ghostrunner from github and run some example tests

::

    cd ~/projects
    git clone git@github.com:wearespindle/ghostrunner.git


3a. Using virtualenv

::

    cd ghostrunner/tests
    virtualenv2 .
    . ./bin/activate
    pip install -r requirements.txt
    # This is be required for virtualenv...
    cp -R /usr/lib/python2.7/site-packages/PyQt5 ./lib/python2.7/site-packages/
    cp /usr/lib/python2.7/site-packages/sip.so ./lib/python2.7/site-packages/
    # Run the tests with an open X display.
    GHOST_DISPLAY=1 ./manage.py test --verbosity=2

3b. Using docker

::

    pacman -S xorg-xhost
    docker-compose build
    # Run with builtin xvfb
    docker-compose run ghostrunner
    # Run with the host's X11 server and a display window.
    xhost +
    docker-compose run ghostrunnerx11

This should run two simple tests. Documentation is a bit sparse for now.
Checkout ghost.test.testcases for more information about the TestCase methods
that ghostrunner provides.
