"""
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
"""

from inspect import isclass
from utils import BasilVersionException, get_module
from io import prompt_settings
from sys import modules

# Settings that apply to all templates.
base_settings = {
        'project_name': 'project_name',
        }


class BaseTemplate(object):
    """Base basil project template.
    All prerequisites defined in static methods will be installed before
    any object's are created.

    A template's docstring will be displayed at the beginning of the project
    creation process, and when 'basil doc' is run for this template.

    Each template's docstring should contain a description of:

        * What the template is intended for
        * What the template will do when creating a project."""

    @classmethod
    def get_version(cls):
        """Returns the version number of the module this template class is
        defined in.

        The version number should be specified in the module's __version__
        The first digit should be the major version of Basil the template is
        designed for;
        The second digit should be the major version of the template for
        that version of Basil.

        E.g. 1.2.3 would be the 3rd minor version of the 2nd major version of
        the template for basil 1.x.
        """
        return modules[cls.__module__].__version__

    @staticmethod
    def get_python_version():
        """Should return the python version for the virtual environment."""
        return 'python'

    @staticmethod
    def get_prereq_packages():
        """Should return a list of system packages to be installed before
        creating the project."""
        return []

    @staticmethod
    def get_prereq_pip_packages():
        """Should return either a string path to a requirements file, or a list
        of pip packages to be installed before creating the project.
        Each package should either be:

            * A string representing the package (with optional version).
            * A os_api.PipPackage object.
        """
        return []

    def __init__(self, settings=None, existing_project=False):
        """Accepts a settings dictionary to rebuild a project's object."""
        self.existing_project = existing_project
        if (settings != None):
            self.settings = settings
        else:
            default_settings = base_settings.copy()
            default_settings.update(self.default_settings())
            self.settings = prompt_settings(default_settings)
        self.alter_settings()
        self.validate_settings()

    def default_settings(self):
        """Should return a dictionary of settings with default values that will
        be used to prompt the user for input.

        Note, even if not specified here, the following settings will be
        prompted for:

        """ + '\n'.join(base_settings.keys())
        return {}

    def alter_settings(self):
        """Should make pre-validation alterations to the self.settings
        dictionary. Called after settings have been entered by the user, but
        before they have been validated. """
        pass

    def validate_settings(self):
        """Should check values in the self.settings dictionary, and raise
        exceptions if anything is invalid."""
        pass

    def get_virtualenvironment_pip_packages(self):
        """Should return a list of system packages to be installed in the
        project's virtualenvironment."""
        return []

    def get_readme_file_path(self):
        """Should return the path to the readme file relative to the project's
        root directory."""
        raise Exception("get_readme_file_path() should return the path to the "
                "readme file relative to the project's root directory.")

    def get_env_variables(self):
        """Should return a dictionary of environment variables and values to
        be set inside the virtualenv."""
        return {}

    def get_name(self):
        """Returns the name of the project's root folder. This will also
        be the name of the virtualenv."""
        return self.settings['project_name']

    def get_db_manager_config(self):
        """Should return a base_db_manager.DbManagerConfig if the template
        requires a database to be configured, or None if it doesn't."""
        """
        from basil.v0.base_db_manager import DbManagerConfig
        db_manager_config = DbManagerConfig('postgres', 0)
        db_manager_config.add_db(name='test')
        db_manager_config.add_user(name='tester', password='123456',
                granted_dbs=['test', ])
        return db_manager_config
        """
        return None

    def get_instructions(self):
        """Should return basic instructions on what the user should do after
        the project is set up correctly."""
        return ''

    def create_project_dir(self):
        """Should create the project's directory inside the current directory,
        and fill it with all necessary files. Exceptions raised in here will
        stop the project creation process, and have their messages displayed to
        the user.
        The project's directory should be the value of self.get_name().
        """
        raise Exception("create_project_dir() should create the project's "
                "directory inside the current directory, and fill it with all "
                "necessary files.")

    def final_setup(self):
        """Will be called after all other project configuration is complete.
        Current directory will be the project's root directory.
        Exceptions raised in here will stop the project creation process, and
        have their messages displayed to the user."""
        pass

    def get_settings(self):
        """Should return a dictionary of settings to be saved, which will be
        used to create the object when running destroy."""
        return self.settings

    def destroy(self):
        """Called when a project is destroyed. Should cleanup anything done in
        final_setup()."""
        pass

    def add_actions(self, actions):
        """Should add actions to an actions.ActionCollectionConfig.
        The actions will be callable from a project directory::

            my_action = actions.add_action('my_action', self.my_action)
            my_action.add_argument('positional_arg',
                    help='A positional argument.', default='test')
            my_action.add_argument('-f', '--foo', action='store_true',
                    metavar='Foo', help='An optional flag.')

        See: basil's 'actions' module.
        """
        pass


def get_template_class(template_name, major_version_number=None):
    """Factory to retrieve a template class for a certain version of basil."""

    # Get the appropriate template module.
    template_module = get_module('templates.' + template_name,
            major_version_number)

    template = None
    for c in template_module.__dict__.values():
        # Find the class that inherits from BaseTemplate.
        if isclass(c) and issubclass(c, BaseTemplate) and c != BaseTemplate:
            template = c
            break
    if template != None:
        return template
    else:
        raise BasilVersionException("{} template class could not be found."
                .format(template_name))
