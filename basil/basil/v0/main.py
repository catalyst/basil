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

from __future__ import print_function
from os import chdir
from shutil import rmtree
from os.path import join, isdir, isfile
import sys
import os_api
from base_template import get_template_class
from base_db_manager import get_db_manager_class
from utils import (BasilVersionException, get_basil_major_version,
        get_module_major_version, iteritems, load_module_from_file,
        DebugException, format_instructions)
from io import to_unicode, from_unicode, EncodedFile
import json
from actions import ActionCollectionConfig
from settings import (set_basil_setting, unset_basil_setting,
        read_basil_settings, basil_settings_path)
from hooks import run_hook
from inspect import getdoc
from types import ModuleType
from textwrap import wrap

__version__ = u'0.1'
settings_file_name = u'.basil'
debug = False

# Python 2/3 input compatibility.
if sys.version_info.major < 3:
    input = raw_input


def load_project_settings(project_dir=''):
    """Return project settings from a project's settings file."""
    project_dir = to_unicode(project_dir)

    settings_file_path = join(project_dir, settings_file_name)

    if not isfile(settings_file_path):
        if project_dir == '':
            project_dir = 'current directory'
        raise Exception('{} file does not exist in {}.'.format(
                settings_file_name, project_dir))

    # Load project settings.
    with EncodedFile(settings_file_path, 'r') as fp:
        return json.load(fp)


def load_project(settings):
    """Return a project object based on the provided project settings."""
    # Check if the project is compatible with this version of Basil.
    current_major_version = get_basil_major_version(__version__)
    project_major_version = get_basil_major_version(settings['basil_version'])
    if (current_major_version != project_major_version):
        raise BasilVersionException(('The project in this directory could not '
                'be loaded with Basil version {current} because it was '
                'created with Basil version {project}. Please use '
                "'basil{project}' to operate on this project.\n").format(
                        current=current_major_version,
                        project=project_major_version))

    # Load the template and project.
    template = get_template_class(settings['template'],
            get_module_major_version(settings['template_version']))

    return template(settings['settings'], existing_project=True)


def create(args):
    """Create a new project in the current directory"""
    template_name = args.template_name
    major_version_number = args.major_version_number
    settings_file_path = args.settings
    hook_module_path = args.hook
    hook_module = None
    if hook_module_path:
        try:
            hook_module = load_module_from_file(hook_module_path)
        except:
            print("* '{}' could not be imported\n* Ignoring hooks".format(
                hook_module_path))

    # Import the required template module.
    template = get_template_class(template_name, major_version_number)

    print('--------------------------------------------------------------')
    print('- {} template documentation:'.format(template_name))
    print('--------------------------------------------------------------')
    print(getdoc(template))
    print('--------------------------------------------------------------')

    # Get values from the template.
    python_version = to_unicode(template.get_python_version())
    template_version = to_unicode(template.get_version())

    # Add pre-requisites from the template.
    prereq_packages = os_api.default_prereq_packages[:]
    prereq_packages.insert(0, python_version)
    prereq_packages += template.get_prereq_packages()

    # Get pre-requisite pip packages.
    prereq_pip_packages = os_api.default_prereq_pip_packages[:]
    prereq_pip_packages += template.get_prereq_pip_packages()

    print('-- Installing pre-requisite packages (This may take a while)')
    for package in prereq_packages:
        os_api.install_package(to_unicode(package))

    print('-- Installing pre-requisite pip-packages (This may take a while)')
    for pip_package in prereq_pip_packages:
        os_api.install_pip_package(to_unicode(pip_package))

    # Ensure that git has the required config settings.
    os_api.require_git_config()

    # Handle project settings provided in a JSON file.
    input_settings = None
    if settings_file_path:
        with EncodedFile(settings_file_path, 'r') as fp:
            input_settings = json.load(fp)

    try:
        # Attempt to create a new project from the template.
        project = template(input_settings)
    except Exception as e:
        # Display any error messages (e.g. input validation errors), and exit.
        print('** Project could not be created:')
        raise e

    # Get project values + run pre-hook.
    project_name = to_unicode(project.get_name())
    os_api.validate_project_does_not_exists(project_name)

    project_settings = project.get_settings()
    if hook_module:
        print('-- Running pre-hook')
        run_hook(hook_module, 'pre', project_settings)

    db_manager_config = project.get_db_manager_config()

    completed_steps = [
            'Installed required system packages and pip packages.',
            ("New '{site}' virtualenv created with required pip "
            "packages.").format(site=project_name),
            "Set up '{site}' project directory.".format(site=project_name),
            "Git repository initialized."
            ]
    if db_manager_config != None:
        completed_steps.append('Configured required project database(s) and '
        'user(s).')
    instructions_dict = {
            '{site} project created successfully!'.format(site=project_name): completed_steps,
            'Next steps:': os_api.get_next_step_instructions(project_name)
                    + project.get_next_step_instructions(),
            'Further configuration: ': os_api.get_further_config_instructions(
                    project_name)
                    + project.get_further_config_instructions()
            }
    instructions = format_instructions(instructions_dict)

    readme_path = to_unicode(project.get_readme_file_path())

    print('-- Setting up virtualenvironment')
    os_api.add_virtualenvwrapper_shell_config()
    os_api.make_virtualenvironment(python_version, project_name)

    print('-- Setting up project directory')
    try:
        project.create_project_dir()
    except Exception as e:
        # Display any error messages, and exit.
        print('** Project directory could not be created.')
        raise e

    # Change directory into the repository directory.
    print("-- Changing directory to '{}'".format(project_name))
    chdir(project_name)

    print('-- Installing required pip packages in virtualenvironment (This '
            'may take a while)')
    virtualenv_pip_packages = project.get_virtualenvironment_pip_packages()
    if isinstance(virtualenv_pip_packages, basestring):
        # Install the pip packages in the requirements file.
        os_api.install_pip_requirements(virtualenv_pip_packages, project_name)
    else:
        # Loop over the provided pip packages.
        for pip_package in virtualenv_pip_packages:
            os_api.install_pip_package(pip_package, project_name)

    print('-- Saving project settings in {} file'.format(settings_file_name))
    settings = {
        u'template': template_name,
        u'basil_version': __version__,
        u'template_version': template_version,
        u'settings': project_settings,
        u'virtualenvironment_pip_freeze': os_api.get_virtualenvwrapper_output(
                ['pip', 'freeze'], virtualenv_name=project_name),
        }
    if db_manager_config:
        settings['db_manager_version'] = to_unicode(
                db_manager_config.db_manager_class.get_version())
    with EncodedFile(settings_file_name, 'w') as fp:
        json.dump(settings, fp, ensure_ascii=False)

    # Database setup.
    if (db_manager_config != None):
        db_manager_class = db_manager_config.db_manager_class

        print('--------------------------------------------------------------')
        print('- {} template documentation:'.format(
                db_manager_config.db_manager_name))
        print('--------------------------------------------------------------')
        print(getdoc(db_manager_class))
        print('--------------------------------------------------------------')

        print('-- Installing database pre-requisite packages (This may take '
        'a while)')
        for package in db_manager_class.get_prereq_packages():
            os_api.install_package(to_unicode(package))

        print('-- Installing database pre-requisite pip packages in '
                'virtualenvironment (This may take a while)')
        for pip_package in db_manager_class.get_virtualenv_prereq_pip_packages():
            os_api.install_pip_package(to_unicode(pip_package), project_name)

        print('-- Starting database server')
        db_manager = db_manager_class()

        print('-- Creating databases')
        for db in db_manager_config.dbs:
            db_manager.create_database(db)

        print('-- Adding database users')
        for user in db_manager_config.users:
            db_manager.create_user(user)

            # Grant permissions.
            for db_name in user.granted_dbs:
                db_manager.grant_permissions(to_unicode(db_name), user)

    print("-- Saving instructions in {}".format(readme_path))
    with EncodedFile(readme_path, 'a', errors='replace') as readme:
        readme.write(instructions)

    print('-- Initializing git repo')
    os_api.quiet_call(['git', 'init'])

    print('-- Making initial git commit')
    os_api.quiet_call(['git', 'add', '.'])
    os_api.quiet_call(['git', 'commit', '-m', 'Initial commit.'])

    print('-- Configuring virtualenvironment environment variables')
    os_api.add_virtualenvironment_environment_variables(project_name,
            project.get_env_variables())

    try:
        # Allow the template to perform additional, final configuration steps.
        project.final_setup()
    except Exception as e:
        # Display any error messages, and exit.
        print('** Final setup of project failed.')
        raise e

    if hook_module:
        print('-- Running post-hook')
        run_hook(hook_module, 'post', project_settings)

    # Display instructions in the case of a successful project initialization.
    print(instructions)
    print("Instructions saved in: {readme}".format(readme=readme_path))


def destroy(args):
    """Destroy a project in the current directory."""

    # Get the project name.
    project_name = args.project_name.strip('/')

    # Ensure the project directory exists in the current directory.
    if not isdir(project_name):
        raise Exception("'{}' does not exist in the current "
                "directory; ".format(project_name))

    settings = load_project_settings(project_name)
    project = load_project(settings)

    dependent_packages = (os_api.default_prereq_packages
            + [project.get_python_version(), ] + project.get_prereq_packages())
    dependent_pip_packages = (os_api.default_prereq_pip_packages
             + project.get_prereq_pip_packages())

    # Ensure we are not in the virtualenvironment that will be destroyed.
    if os_api.in_virtualenvironment(project_name):
        raise Exception("Please exit the virtualenvironment with "
                "'deactivate' before deleting the project.")

    # Confirm that the user wants to destroy the whole project.
    choice = input(from_unicode('Are you sure you want to delete the project '
            'directory and virtualenvironment for {}? [y/N] '.format(
                    project_name)))
    if choice in ['Y', 'y']:
        print('-- Allowing template to clean up')
        try:
            project.destroy()
        except Exception as e:
            de = DebugException("* '{}' template-specific project destruction "
                    "could not be completed; continuing anyway".format(
                            settings['template']), e)
            print(de)

        db_manager_config = project.get_db_manager_config()
        if db_manager_config != None:
            print('-- Cleaning up database')

            # Get the db_manager
            db_manager_class = db_manager_config.db_manager_class

            print('---- Starting database server')
            db_manager = db_manager_class()

            print('---- Deleting databases')
            for db in db_manager_config.dbs:
                try:
                    db_manager.delete_database(db)
                except Exception as e:
                    de = DebugException("* '{}' db_manager could not delete "
                            "database: '{}'; continuing anyway".format(
                                    db_manager_config.db_manager_name,
                                    db), e)
                    print(de)

            print('---- Deleting database users')
            for user in db_manager_config.users:
                try:
                    db_manager.delete_user(user)
                except Exception as e:
                    de = DebugException("* '{}' db_manager could not delete "
                            "database user: '{}'; continuing anyway".format(
                                    db_manager_config.db_manager_name,
                                    user), e)
                    print(de)

            dependent_packages += db_manager.get_prereq_packages()

        print('-- Removing project directory')
        try:
            rmtree(project_name)
        except Exception as e:
            de = DebugException("* Could not remove directory: '{}'; "
                    "continuing anyway".format(project_name), e)
            print(de)

        print('-- Removing virtualenvironment')
        try:
            os_api.destroy_virtualenvironment(project_name)
        except Exception as e:
            de = DebugException("* Could not remove virtualenv: '{}'; "
                    "continuing anyway".format(project_name), e)
            print(de)

        instructions_dict = {
                '{site} successfully destroyed'.format(site=project_name): [
                        ('You may wish to remove the following system packages '
                        'that this project depended on:\n\n'
                        '{dependent_packages}').format(
                                dependent_packages='\n'.join(
                                        dependent_packages)),
                        ('You may wish to remove the following pip packages '
                        'that this project depended on:\n\n'
                        '{dependent_pip_packages}').format(
                                dependent_pip_packages=to_unicode('\n'.join(
                                        dependent_pip_packages))),
                        ('You may wish to remove the '
                        '"basil-virtualenvwrapper-config" block from '
                        '{shell_config}.').format(shell_config=to_unicode(
                                os_api.shell_conf_path))
                        ],
                '*** IMPORTANT WARNING ***': [
                        'You should only remove packages that are not '
                        'depended on by other packages or projects.',
                        'Removing packages may result in data loss (e.g. '
                        'databases).',
                        'Only remove the "basil-virtualenvwrapper-config" '
                        'block if this is your only project and you no longer '
                        'wish to use virtualenvwrapper.'
                        ]
                }

        print(format_instructions(instructions_dict))
    else:
        print('Aborting')


def list_modules(args):
    if args.db_manager:
        import db_managers as module_list
    else:
        import templates as module_list
    for name, item in iteritems(module_list.__dict__):
        if isinstance(item, ModuleType):
            print(name)


def set_setting(args):
    set_basil_setting(args.key, args.value)
    print("'{}' set to: {}".format(args.key, args.value))


def unset_setting(args):
    unset_basil_setting(args.key)
    print("'{}' unset".format(args.key))


def list_settings(args):
    settings = read_basil_settings()
    for key, value in iteritems(settings):
        print('{}: {}'.format(key, value))


def doc(args):
    if args.template:
        template_class = get_template_class(args.template)
        print(getdoc(template_class))
    elif args.db_manager:
        db_manager_class = get_db_manager_class(args.db_manager)
        print(getdoc(db_manager_class))


def version(args):
    if args.template:
        template_class = get_template_class(args.template)
        print(template_class.get_version())
    elif args.db_manager:
        db_manager_class = get_db_manager_class(args.db_manager)
        print(db_manager_class.get_version())
    else:
        print(__version__)


def main():
    actions = ActionCollectionConfig()

    create_action = actions.add_action('create', create, description='Create '
            'a new project from a basil template.')
    create_action.add_argument('template_name', help='Name of the project '
            'template.')
    create_action.add_argument('major_version_number', nargs='?', type=int,
            help='Major template version to use.')
    create_action.add_argument('-t', '--settings',
            help='Path to file containing JSON object of settings and values '
            'to be used instead of the settings prompt.')
    create_action.add_argument('-o', '--hook',
            help='Python module to call pre() and post() hooks on. A '
            'dictionary of project settings will be passed to each hook '
            'function.')

    destroy_action = actions.add_action('destroy', destroy,
            description='Destroy a project created with basil in the current'
            'directory.')
    destroy_action.add_argument('project_name', help='Name of the project to '
            'destroy')

    list_action = actions.add_action('list', list_modules,
            description='List all basil templates that are currently '
            'installed for this version of basil.')
    list_action.add_argument('-d', '--db_manager', action='store_true',
            help='If specified, installed db_managers will be listed instead.')

    set_action = actions.add_action('set', set_setting, description='Set a '
            'new value for a basil settings key.')
    set_action.add_argument('key',
            help='Basil setting key to set in {}. Setting keys used in core '
            'Basil: shell-config-file-path, workon-home'.format(
                    basil_settings_path))
    set_action.add_argument('value',
            help='New value for the setting.')

    unset_action = actions.add_action('unset', unset_setting,
            description='Unset the current value for a basil settings key.')
    unset_action.add_argument('key',
            help='Basil setting key to unset in {}.'.format(
                    basil_settings_path))

    doc_action = actions.add_action('doc', doc, description='Display '
            'documentation for a basil template or database manager.')
    doc_group = doc_action.add_mutually_exclusive_group(required=True)
    doc_group.add_argument('template', nargs='?',
            help='template to display documentation for')
    doc_group.add_argument('-d', '--db_manager',
            help='db_manager to display the latest version of')

    version_action = actions.add_action('version', version,
            description='Display the version number for Basil, or a '
            'particular basil template or database manager.')
    version_group = version_action.add_mutually_exclusive_group()
    version_group.add_argument('template', nargs='?',
            help='template to display the latest version of')
    version_group.add_argument('-d', '--db_manager',
            help='db_manager to display the latest version of')

    actions.add_action('settings', list_settings, description='List all '
            'currently configured basil settings.')

    try:
        # Attempt to load the project and its available actions.
        settings = load_project_settings()
        project = load_project(settings)
        project.add_actions(actions)
    except BasilVersionException as e:
        # This exception will occur if a .basil file is found in the current
        # directory for a different major version of Basil.
        print('* {}'.format(to_unicode(e)))
    except:
        pass

    # Execute the action configuration against the command line arguments.
    actions.execute()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
