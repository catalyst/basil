..
    Basil: Build A System Instant-Like
    Copyright (C) 2014 Catalyst IT Ltd
    
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    
    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

Basil Installation and Usage
============================

Installation
------------

@TODO NOT YET AVAILABLE

If you are using a Linux operating system, and have pip installed, you can
install basil from the command line with::

    >>> sudo pip install basil

.. note::

    You will need to install one or more basil templates in order to create
    projects with basil. These can also be installed through pip, e.g. ``pip
    install basil_django``.

Creating a project
------------------

To create a new basil project, simply enter the directory you want the project
to be a subdirectory of, and use::

    >>> basil create <template_name> [-t|--settings] []
    
Where ``<template_name>`` is the name of the template you wish to create the
project from, e.g. ``django``, ``flask``, ``pyramid``.

Basil create will ask you a series of configuration questions about your
project, and then proceed to set up your project directory, virtualenv,
and any other configurations the project requires, as specified in the chosen
template.

For example, if I enter::

    >>> cd /home/basil/src
    >>> basil create django

My new project will be created at ``/home/basil/src/<project directory>``.

@TODO --settings, --hook

Destroying a project
--------------------

To destroy a project created with basil, first enter parent directory of the
project (where basil create was originally run), then execute::

    >>> basil destroy <project_name>

Where ``<project_name>`` is the name of the project's directory and virtualenv.

Working with settings
---------------------

Basil provides several commands for configuring the settings that basil and its
contributed templates use.

The settings that are used by core basil are:

* ``encoding`` (default: ``utf-8``)
    Determines what text encoding all non-settings files are read and saved as.
* ``shell-config-file-path`` (default: ``~/.bashrc``)
    Determines what file basil will insert shell configuration lines to be
    executed whenever a new shell is opened.

::

    >>> basil settings

Lists all stored settings with their current values.

::

    >>> basil set <key> <value>

Sets the value for setting: ``<key>`` to ``<value>``.

::

    >>> basil unset <key>

Removes the stored setting value for ``<key>``.

Other core basil actions and arguments
--------------------------------------

::

    basil (-h|--help)

Displays help message for basil.

::

    basil (-v|--verbose) <action>

Display verbose debug output, including full error messages and tracebacks.

::

    basil version [-d|--db_manager <db_manager>] [<template>]

When no arguments are provided, displays basil's version number.

When ``<template>`` is provided, displays the latest installed version number
for the specified template.

When the ``db_manager`` option is specified with ``<db_manager>``, displays the
latest installed version number for the specified database manager.

::

    basil list [-d|--db_manager]

List all currently installed basil templates, or, if the ``db_manager`` option
is specified, lists all currently installed database managers.

::

    basil doc [-d|--db_manager <db_manager>] [<template>]

Shows documentation for a specified basil template, or, if the ``db_manager``
option is specified with ``<db_manager>``, shows documentation for the
specified database manager.

Template-specific actions
-------------------------

@TODO
