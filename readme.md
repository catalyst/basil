# Basil

Basil makes it easy to set up best-practice, project development environments.

## Installation

Currently, Vagrant has only been tested on Ubuntu, but most of the functionality
should work on any operating system that can run Vagrant.

### Installation Steps

* Install [Vagrant](https://www.vagrantup.com/downloads.html) (minimum
  version: 1.5)
 * ``sudo apt-get install vagrant``
* Install [Python 3.4](https://www.python.org/downloads/)
 * ``sudo apt-get install python3.4``
* Install Tkinter for Python 3.4
 * ``sudo apt-get install python3.4-tk``
* Download [Basil](https://github.com/catalyst/basil/archive/master.zip)
 * Or clone with git: ``git clone https://github.com/catalyst/basil.git``
* Run Basil's ``web.py`` with Python 3.4
 * ``python3.4 web.py``
* Open Basil in your web browser at http://localhost:8000
 * If port 8000 is already in use on your computer, Basil will tell you which
 port it is running on.
