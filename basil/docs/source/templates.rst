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

.. py:currentmodule:: basil.v0.base_template

Templates
#########

Creating a new template
=======================

This tutorial is intended as a guide for those wishing to create their own
basil templates. In our demonstration, we will imagine that we are creating a
template called ``parrot``, that could be installed with
``pip install basil_parrot``, and a new project created with
``basil create parrot``.

Requirements
------------

Please ensure that you have python, setuptools, pip, and basil installed on
your machine.

Basic Structure
---------------

The structure for our basil package will be as follows:

.. parsed-literal::

    basil_parrot/
        setup.py
        LICENSE.txt # Should be GPLv3
        README.txt
        basil/
            __init__.py
            v\ |basil_major_version|\ /
                __init__.py
                templates/
                    __init__.py
                    parrot/
                        __init__.py
                        v1.py

Every ``__init__.py`` in the hierarchy should start with the following two
lines::

    import pkg_resources
    pkg_resources.declare_namespace(__name__)

(This is so that many different packages can share the same namespace, via
Python's namespace packaging system).

.. note::

    You do not need to include these lines in the ``__init__.py`` of any
    ``tests`` directories.

The contents of ``setup.py`` should be as follows::

    from setuptools import setup, find_packages

    packages = find_packages()
    namespace_packages = packages[:]
    for package in namespace_packages:
        if package.split('.')[-1] == 'tests':
            namespace_packages.remove(package)
    
    setup(
          name='basil_parrot',
          version='1.0',
          author='Your name',
          author_email='your_address@email.com',
          packages=packages,
          namespace_packages=namespace_packages,
          url='http://pypi.python.org/pypi/basil_parrot',
          license='LICENSE.txt',
          description='Basil template to create a parrot project.',
          long_description=open('README.txt').read(),
          install_requires=['basil'],
          )

All of the actual template code will be contained within a class that inherits
from ``BaseTemplate``:

.. autoclass:: BaseTemplate()

The Template Class
------------------

To start our template, place the following code in
'basil_parrot/v\ |basil_major_version|\ /templates/parrot/v1.py'

.. parsed-literal::

    from ...base_template import BaseTemplate

    __version__ = '|basil_major_version|.1.0'


    class ParrotTemplate(BaseTemplate):
        """Sets up parrot installation."""
        pass

.. note::

    For more information on version numbers, see :doc:`versioning`

In your template class, the following methods must be implemented:

    .. automethod:: BaseTemplate.create_project_dir
    .. automethod:: BaseTemplate.get_readme_file_path

For example::
        
    def create_project_dir(self, directory_name):
        import os

        # Create project folder.
        os.mkdir(directory_name)
        
        # Put an empty file in it.
        open(os.join(directory_name, 'test_file.txt'), 'a').close()
        
    def get_readme_file_path(self):
        return 'readme.txt'
        
Project Settings
----------------

To accept user configuration for the project (such as the project's name),
implement one or more of the following methods in the template class:

    .. automethod:: BaseTemplate.default_settings
    .. automethod:: BaseTemplate.alter_settings
    .. automethod:: BaseTemplate.validate_settings

For example, we could add a description parameter that will have it's words
captialized, and forced to be at most 500 characters::

    def default_settings(self):
        return {
            "description": "A short description of the project.",
        }
        
    def alter_settings(self):
        from string import capwords
        self.settings['description'] = capwords(self.settings['description'])
        
    def validate_settings(self):
        if len(self.settings['description']) > 500:
            raise Exception(
                    'Description must be no longer than 500 characters.')

Specifying Dependencies
-----------------------

To specify dependencies on vendor or pip packages, or a particular python
version, implement one or more of the following methods in the template class:

    .. automethod:: BaseTemplate.get_prereq_packages
    .. automethod:: BaseTemplate.get_prereq_pip_packages
    .. automethod:: BaseTemplate.get_python_version

Additional Project Actions
--------------------------

Actions can be added to your basil template by implementing ``add_actions``:

    .. automethod:: BaseTemplate.add_actions
    
Actions can be run from an existing project's directory with:
``basil action_name``

Database Configuration
----------------------

You can add database configuration to your template by implementing
``get_db_manager_config``:

    .. automethod:: BaseTemplate.get_db_manager_config

.. note:: 
    When using a database manager, ensure ``install_requires`` in ``setup.py``
    lists the package containing the db_manager. For example::

        install_requires=['basil', 'basil_postgres']
    
Additional Template Configuration
---------------------------------

Additional methods that can be implemented in the template class to add
functionality are:

    .. automethod:: BaseTemplate.destroy
    .. automethod:: BaseTemplate.final_setup
    .. automethod:: BaseTemplate.get_env_variables
    .. automethod:: BaseTemplate.get_next_step_instructions
    .. automethod:: BaseTemplate.get_further_config_instructions
    .. automethod:: BaseTemplate.get_virtualenvironment_pip_packages

Installing your template
------------------------

Run the following terminal commands from ``basil_parrot``::

    >>> python setup.py sdist
    >>> sudo pip install dist/basil_parrot-1.0.tar.gz

To uninstall::

    >>> sudo pip uninstall basil_parrot

Subclassing Templates
=====================

Subclassing a template is a useful way to create a custom version of an
existing template.

To subclass a template instead of creating a new one, make the following
alterations to your template (We will assume the "parent template" is called
``bird``):

1. In setup.py, ensure ``install_requires`` lists the package containing the
   ``bird`` template. For example::
   
      install_requires=['basil', 'basil_bird']

2. In your template file, instead of importing ``BaseTemplate`` from
   ``...base_template``, import the ``BirdTemplate`` from ``..bird.v1``::
   
      from ..bird.v1 import BirdTemplate
   
   .. note::
   
      ``v1`` may vary depending on which major version of the parent template
      you wish to subclass. For more information, see: :doc:`versioning`

3. Ensure your template class now inherits from ``BirdTemplate`` instead of
   ``BaseTemplate``::
   
      class ParrotTemplate(BirdTemplate):

4. Override methods as usual in your template, bearing in mind you may need to
   use :py:func:`super` to ensure that functionality in ``BirdTemplate`` is
   still executed.
