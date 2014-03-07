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

Why Basil?
##########

Why do we need Basil?
=====================

Easy or best practice
---------------------

Because the choice without basil is between easy or best practice - you can't
have both. One of basil's mottos is “best practice made easy”.

Best practice is fiddly
-----------------------
Following best practice manually is not easy. For example, a good strategy for
enabling all settings to be version controlled without including secrets
requires the setting of secret key environment values in the appropriate
virtual environment. Not too hard to do once you know precisely how but there
are numerous such fiddly changes to make. The overall hassle of configuration
is a deterrent to quickly spinning up web frameworks to play with. Best
practice configuration is a pain point basil addresses.

Easy has problems
-----------------
If people opt for easy instead of best practice, we can only hope they fix
everything up before deployment. The reality is that the development of lots
of web sites will be less secure than ideal. And sites will be unnecessarily
diverse structure-wise – which negates one of the key benefits of web
frameworks – standardisation.

What about alternatives?
========================

Vagrant
-------

Vagrant is a great way of working with virtual machines. And the vagrant
project is an inspiration in terms of its simple api and helpful documentation.
What's not to love about: vagrant up or vagrant halt? But virtual machines are
not necessarily the easiest way of working with web frameworks on the OS you
are interested in. Using basil we can create three solid framework environments
with three simple commands: ``basil create django``, ``basil create
flask``, and ``basil create pyramid``.

Non-python deployment alternatives
----------------------------------

Looking at puppet, chef etc, basil has the advantage of being a python-based
tool. It will be easier for Python developers to work with. It also comes with
templates ready-to-use for the main versions of the main web frameworks. And it
makes it easy for new frameworks to be added by the community.

Buildout
--------

As for one of the main python alternatives, buildout, the developers have made
a different trade-off between simplicity and flexibility. Basil specialises in
spinning up web frameworks for development – and nothing else makes this
specific task so easy. Basil has the potential to become the obvious best way
to set up web frameworks in development – and that can only help the popularity
of Python-based frameworks.

Your own scripts
----------------

Unlikely to be consistent with anyone else – dozens of blogs all with subtle
differences in advice.

Are they going to be cross-platform? Basil will be.

Basil and its templates will be tried and tested. They will handle unicode
properly etc.

Basil will cover all the edge cases that are hard to remember and keep
up-to-date with changes in best practice for the main web frameworks. Do you really feel confident maintaining your script for multiple frameworks as they go through upgrades e.g. Django 1.5 to 1.6?

Will your own bash script, for example, be as quick and easy to use and modify?

This is one of those cases where it is best to let a community handle the
quirks. For the same reasons you don't make your own javascript and SVG
library.

Basil and deployment
====================

Basil is not about deployment to production etc. Tools like puppet, chef,
fabric etc are powerful and well-supported options in this space. But basil
makes it easy to run pre and post scripts and there may well be some basic
scripts made available for deployment in simple cases.

Elements of best practice
=========================

* Sane and standardised folder structure-wise
* Virtual environments
* Structure supporting versioned settings but not versioned secrets

Other features
==============

Basil, unlike its namesake from Fawlty Towers, is very polite. It doesn't do
things without letting you know and it makes it easy to tidy up if you want to
remove a project e.g. basil destroy myproject.

Basil has also been architected to make it easy to handle projects made with
different major versions of basil. There is little point being easy to use if
everything becomes complicated over time.