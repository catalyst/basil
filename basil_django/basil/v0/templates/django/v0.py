"""
Basil Django: Basil Template for standard Django projects.
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

from __future__ import print_function
from ...os_api import (virtualenvwrapper_call, in_virtualenvironment,
        get_virtualenvwrapper_output, get_output, quiet_call, )
from ...base_template import BaseTemplate
from os.path import isdir, isfile, join
from os import stat, chmod, chdir
import stat as stat_consts
import re
from datetime import date
from ...io import EncodedFile
from ...utils import DebugException, format_instructions

__version__ = '0.0.1'


class DjangoTemplate(BaseTemplate):
    """Sets up base Django installation."""

    @staticmethod
    def get_python_version():
        return 'python2.7'

    @staticmethod
    def get_prereq_pip_packages():
        return ['cookiecutter', ]

    def default_settings(self):
        return {
                "author_name": "Your Name",
                "email": "Your email",
                "description": "A short description of the project.",
                "domain_name": "example.com",
                "version": "0.1.0"
        }

    def alter_settings(self):
        if not self.existing_project:
            self.settings['year'] = date.today().year

    def validate_settings(self):
        unavailable_names = ['test', 'django']
        domain = re.compile('^[A-z\d-]{,63}(\.[A-z\d-]{,63})+$')
        version = re.compile('^\d+(\.\d+)*$')

        # Project name.
        if self.settings['project_name'] in unavailable_names:
            raise Exception('Project name must be a unique python package '
                    'name (e.g. not "test" or "django").')

        # Domain name.
        if not domain.match(self.settings['domain_name']):
            raise Exception('Domain name must only contain A-z characters, '
                    'digits, and dashes separated by periods.')

        # Version.
        if not version.match(self.settings['version']):
            raise Exception('Version number must only contain digits '
                    'separated by periods.')

    def get_virtualenvironment_pip_packages(self):
        return join('requirements', 'local.txt')

    def get_readme_file_path(self):
        return 'README.rst'

    def get_env_variables(self):
        return {
            'DJANGO_CONFIGURATION': 'Local',
            'DJANGO_SECRET_KEY': 'CHANGEME!!!',
            'DJANGO_SETTINGS_MODULE': 'config.settings'
            }

    def get_next_step_instructions(self):
        site = self.settings['project_name']
        return [
                ('Change DJANGO_SECRET_KEY in ~/.virtualenvs/{site}/bin/'
                'postactivate.').format(site=site),
                ("Run 'workon {site}' to activate your new virtual "
                "environment (then 'deactivate' to exit).").format(site=site),
                ("Move into the {site} directory and run 'basil new_app "
                "my_app_name' to create a new django app.").format(site=site),
                ("Optionally, activate a different settings class (e.g. "
                "'Local', 'Production', or another settings class defined in "
                "{site}/config/settings.py) by altering DJANGO_CONFIGURATION "
                "in ~/.virtualenvs/{site}/bin/postactivate").format(site=site),
                ("Start the server by running './{site}/manage.py runserver "
                "0.0.0.0:8080'").format(site=site),
                ("Administer your new site in your browser at: "
                "http://localhost:8080/admin").format(site=site),
                ("For more information on using django, see: "
                "https://docs.djangoproject.com/en/1.6/intro/tutorial01/")
                ]

    def create_project_dir(self):
        import cookiecutter.config
        from cookiecutter.main import cookiecutter as cookiecutter_make

        cookiecutter_settings = self.settings.copy()
        # repo_name is used by this cookiecutter template to name the outer
        # project directory.
        cookiecutter_settings['repo_name'] = self.get_name()

        print('')
        # Set the default cookiecutter config.
        cookiecutter.config.DEFAULT_CONFIG['default_context'].update(
                cookiecutter_settings)
        # Run cookiecutter, forcing no-input so that the default is used.
        cookiecutter_make("https://github.com/ben-denham/cookiecutter-django",
                None, True)
        print('')

    def final_setup(self):
        manage_py_path = join(self.settings['project_name'], 'manage.py')

        print('-- Making manage.py executable')
        st = stat(manage_py_path)
        chmod(manage_py_path, st.st_mode | stat_consts.S_IEXEC)

        print('-- Syncing database')
        try:
            virtualenvwrapper_call([manage_py_path, 'syncdb'],
                    self.get_name(), False)
        except Exception as e:
            raise DebugException("Database could not be synced, you can try "
                    "to sync the database again with 'workon {} && "
                    "{}/{}/manage.py syncdb'.".format(self.get_name(),
                            self.get_name(), self.settings['project_name']), e)

    def add_actions(self, actions):
        new_app_action = actions.add_action('new_app', self.new_app)
        new_app_action.add_argument('app_name', help='Name for the new '
                'application.')

    def new_app(self, args):
        app_name = args.app_name

        # Move into django-project directory.
        chdir(self.settings['project_name'])

        # Check we are in a valid project directory.
        if not isfile('manage.py'):
            raise Exception('manage.py does not exist in {}'.format(
                    self.settings['project_name']))

        # App name.
        unavailable_names = ['test', 'django']
        if app_name in unavailable_names:
            raise Exception('App name must be a unique python package name '
                    '(e.g. not "test" or "django").')
        if isdir(join(app_name)):
            raise Exception('An app named {} already exists in current '
                    'directory.'.format(app_name))

        # Get a string of installed apps.
        is_in_virtualenvironment = in_virtualenvironment(self.get_name())
        installed_apps_args = ['python', '-c',
                'from configurations import importer; importer.install(); '
                'import config.settings; print config.settings.INSTALLED_APPS']
        if not is_in_virtualenvironment:
            installed_apps = get_virtualenvwrapper_output(
                    installed_apps_args, virtualenv_name=self.get_name())
        else:
            installed_apps = get_output(installed_apps_args)

        if "'" + app_name + "'" in installed_apps:
            raise('An app named {} is already installed.'.format(app_name))

        print('-- Creating app')
        create_app_args = ['./manage.py', 'startapp', app_name]
        if is_in_virtualenvironment:
            quiet_call(create_app_args)
        else:
            virtualenvwrapper_call(create_app_args,
                    virtualenv_name=self.get_name())

        print('-- Adding app to list of installed local apps')
        settings_path = join('config', 'settings.py')

        # Read lines from settings file.
        with EncodedFile(settings_path, 'r') as f:
                lines = f.readlines()

        # Insert the new app inside LOCAL_APPS.
        index = ([i for i, s in enumerate(lines)
                if 'LOCAL_APPS = ' in s][:1] or [None])[0]
        lines.insert(index + 1, (' ' * 8) + "'" + app_name + "',\n")

        # Write the lines back into the file.
        with open(settings_path, 'w') as f:
            for line in lines:
                f.write(line)

        print('-- Creating initial database migration')
        create_initial_migration_args = ['./manage.py', 'schemamigration',
                app_name, '--initial']
        if is_in_virtualenvironment:
            quiet_call(create_initial_migration_args)
        else:
            virtualenvwrapper_call(create_initial_migration_args,
                    virtualenv_name=self.get_name())

        print('-- Applying initial database migration')
        apply_migration_args = ['./manage.py', 'migrate', app_name]
        if is_in_virtualenvironment:
            quiet_call(apply_migration_args)
        else:
            virtualenvwrapper_call(apply_migration_args,
                    virtualenv_name=self.get_name())

        instructions = format_instructions({
                '{app_name} successfully added to {project_name}'.format(
                        app_name=app_name, project_name=self.get_name()): [
                                ("To create a new migration: './manage.py "
                                "schemamigration {app_name} --auto'").format(
                                        app_name=app_name),
                                ("To execute a migration: ./manage.py migrate "
                                "{app_name}").format(app_name=app_name)
                                ]
                })

        print(instructions)
