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
1. Install PyQt5

::

    sudo pacman -S pyqt5-common python2-pyqt5 # archlinux

2. Try the ghostrunner_example repo for a quick setup

::

    cd ~/projects
    git clone git@github.com:wearespindle/ghostrunner_example.git
    cd ghostrunner_example
    virtualenv2 .
    . ./bin/activate
    pip install -r requirements.txt
    # This seems to be required for virtualenv...
    cp -R /usr/lib/python2.7/site-packages/PyQt5 ./lib/python2.7/site-packages/
    cp /usr/lib/python2.7/site-packages/sip.so ./lib/python2.7/site-packages/
    cd example
    GHOST_DISPLAY=1 ./manage.py test --verbosity=2

This should show feedback from two simple tests. Documentation is a bit sparse for now. Checkout ghost.test.testcases for more
information about the TestCase methods that ghost provides.
