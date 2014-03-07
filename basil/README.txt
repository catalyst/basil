=====
Basil
=====

Basil follows best practice to create a new python project in the current
directory from a given template. Basil also supports removing projects and
performing additional actions that are specific to templates.

Basil is intended to set up python projects for many different frameworks (via
its template system), and to work on many different platforms and
distributions.

Currently, Basil has only been tested on Ubuntu 13.10.

Features
========

* Installs required packages and pip packages.
* Creates a new virtualenv with virtualenvwrapper, and installs pip packages in it.
* Creates a project directory.
* Sets up virtualenv environment variables.
* Creates a git repo for source control.
* Handles destroying projects.
* Allows templates to provide additional actions to be performed on projects.

Usage
=====

    See: 'basil -h'

Thanks also to
==============

Grant Paton-Simpson for help with design and architecture.

Licensing
=========

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