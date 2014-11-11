# Basil

Basil makes it easy to set up best-practice, project development environments.

## Installation

Currently, Vagrant has only been tested on Ubuntu, but most of the functionality
should work on any operating system that can run Vagrant.

### Installation Steps

* Install [Vagrant](https://www.vagrantup.com/downloads.html) (minimum
  version: 1.5)
 * ``sudo apt-get install vagrant``
* Install [VirtualBox](https://www.virtualbox.org/)
 * ``sudo apt-get install virtualbox``
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
 
## Template Naming

Templates have folder names and displayed names. The following are conventions 
only. They should be followed unless there is a good reason, but practicality
beats purity.

### Template Folder Names
 
A general pattern is framework name then versions then variants - all lower case 
and joined with underscores. Dots and hyphens are OK. Some examples:

* drupal_7
* drupal_7_catalyst # Drupal 7 with the configuration preferred by Catalyst
* flask_0.10.1_py2.7 # both framework version and python version (general detail 
only)
* django_1.7_py3.4

But it is OK to use another label if it makes sense e.g.
* lamp_basic

### Template Display Names

As for template folder names but underscores can be replaced with spaces, and
variable case is OK. There is no need to separate sections. Some examples:

* Drupal 7.x
* Drupal 7 Catalyst
* Flask v0.10.1 Python 2.7
* Django v1.7 Python 3.4
* LAMP Stack (Basic)
