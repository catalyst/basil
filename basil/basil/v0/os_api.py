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
from subprocess import check_call, check_output, STDOUT
from os import getenv, devnull, walk
from os.path import join, isdir, isfile
from mmap import mmap, ACCESS_READ
from utils import iteritems, DebugException
from io import to_unicode, from_unicode, EncodedFile
from settings import get_basil_setting

# Look into using http://amoffat.github.io/sh/ if it get Windows support.

# Define pre-requisites to be installed on the system.
default_prereq_packages = [
    'python-pip',
    'git',
    'python-dev'
]
# In most cases, pip packages should be added in setup.py instead of here.
default_prereq_pip_packages = []

# Final start and ends will have the project name appended.
virtualenv_conf_start = u'# __basil-virtualenvwrapper-config-start__'
virtualenv_conf_end = u'# __basil-virtualenvwrapper-config-end__'

# OS-specific variables - will most likely need changing for a different OS.
shell_conf_path = get_basil_setting('shell-config-file-path',
        join(getenv('HOME'), '.bashrc'))
workon_home = get_basil_setting('workon-home',
        join(getenv('HOME'), '.virtualenvs'))
__virtualenvwrapper_sh_path__ = None


def find_virtualenvwrapper_sh():
    """Determine where virtualenvwrapper.sh or an equivalent file is located
    on the system"""
    global __virtualenvwrapper_sh_path__

    # Return the stored path if it has been set.
    if __virtualenvwrapper_sh_path__ != None:
        return __virtualenvwrapper_sh_path__

    # When locating virtualenvwrapper.sh, we will test these common paths
    # first.
    probable_virtualenvwrapper_sh_paths = [
            '/usr/local/bin/virtualenvwrapper.sh',
            '/etc/bash_completion.d/virtualenvwrapper',
            '/usr/local/bin/virtualenvwrapper_bashrc'
            ]
    # If we do not find one of the above files, we will search the whole disk
    # for one of these virtualenvwrapper.sh files.
    possible_virtualenvwrapper_filenames = [
            'virtualenvwrapper.sh',
            'virtualenvwrapper_bashrc'
            ]

    print('---- Looking for virtualenvwrapper.sh or equivalent in probable '
            'locations')
    for path in probable_virtualenvwrapper_sh_paths:
        if isfile(path):
            __virtualenvwrapper_sh_path__ = path
            break

    if __virtualenvwrapper_sh_path__ == None:
        print('---- Searching system for virtualenvwrapper.sh or equivalent '
                '(This may take a while)')
        for root, _, files in walk('/'):
            for filename in possible_virtualenvwrapper_filenames:
                if filename in files:
                    __virtualenvwrapper_sh_path__ = join(root, filename)
                    break

    if __virtualenvwrapper_sh_path__ == None:
        raise Exception('Path to virtualenvwrapper.sh or equivalent could not '
                'be determined')
    else:
        print('---- Found: {}'.format(__virtualenvwrapper_sh_path__))
        return __virtualenvwrapper_sh_path__


def get_virtualenvwrapper_conf_lines():
    """Generate the virtualenvwrapper config lines for the shell config
    file."""
    return u'''# Do not make any manual changes in this block, as
# it will be replaced each time a new basil project is created.
export WORKON_HOME={}
source {}
'''.format(workon_home, find_virtualenvwrapper_sh())


def validate_virtualenv_name(virtualenv_name):
    """Check if a given string is a valid name for a virtualenvironment."""
    if not virtualenv_name:
        raise Exception('Virtualenvironment name cannot be empty.')
    try:
        to_unicode(virtualenv_name).encode('ascii')
    except UnicodeEncodeError as e:
        raise DebugException('Virtualenvironment name cannot contain '
                'non-ascii characters', e)
    return True


def quiet_call(args, quiet_out=True, quiet_err=False):
    """Call a system command with a custom level of 'quietness'."""
    args = [from_unicode(to_unicode(arg)) for arg in args]

    if quiet_out and quiet_err:
        return check_call(args, stdout=open(devnull, 'wb'), stderr=STDOUT)
    elif quiet_out and (not quiet_err):
        return check_call(args, stdout=open(devnull, 'wb'))
    elif (not quiet_out) and quiet_err:
        return check_call(args, stderr=open(devnull, 'wb'))
    else:
        return check_call(args)


def virtualenvwrapper_call(args, virtualenv_name=None, quiet_out=True,
        quiet_err=False):
    """Call a system command in a context where virtualenvwrapper commands are
    available.
    If virtualenv_name is supplied, the command will be called from within that
    virtualenvironment."""
    command_string = ' '.join(["'{}'".format(a) for a in args])
    if virtualenv_name != None:
        validate_virtualenv_name(virtualenv_name)
        command_string = 'workon {};{}'.format(virtualenv_name, command_string)
    quiet_call(['bash', '-c',
            get_virtualenvwrapper_conf_lines() + command_string], quiet_out,
            quiet_err)


def call_as_user(username, args, quiet_out=True, quiet_err=False):
    """Call a command as a different user."""
    quiet_call(['sudo', '-u', username] + args, quiet_out, quiet_err)


def get_output(args, quiet_err=False):
    """Get output from a system command."""
    args = [from_unicode(to_unicode(arg)) for arg in args]

    if quiet_err:
        output = check_output(args, stderr=open(devnull, 'wb'))
    else:
        output = check_output(args)
    return to_unicode(output)


def get_virtualenvwrapper_output(args, virtualenv_name=None, quiet_err=False):
    """Get output from a system command called with virtualenvwrapper commands
    available.
    If virtualenv_name is supplied, the command will be called from within that
    virtualenvironment."""
    if in_virtualenvironment():
        raise Exception('The shell is already in a virtualenv.')

    command_string = ' '.join(["'{}'".format(a) for a in args])
    if virtualenv_name != None:
        validate_virtualenv_name(virtualenv_name)
        command_string = 'workon {};{}'.format(virtualenv_name, command_string)
    return get_output(['bash', '-c', get_virtualenvwrapper_conf_lines()
            + command_string], quiet_err)


def get_output_as_user(username, args, quiet_out=True, quiet_err=False):
    """Get output from a command called as a different user."""
    return get_output(['sudo', '-u', username] + args, quiet_out, quiet_err)


def in_virtualenvironment(virtualenv_name=None):
    """Returns true if the current shell is running in a virtualenvironment."""
    if virtualenv_name == None:
        path = '.virtualenvs'
    else:
        validate_virtualenv_name(virtualenv_name)
        path = join('.virtualenvs', virtualenv_name, 'bin')

    python_path = get_output(['which', 'python'])

    return path in python_path


def install_package(package):
    """Install a package on the system."""
    try:
        quiet_call(['sudo', 'apt-get', 'install', '-yq', package])
    except Exception as e:
        raise DebugException("Could not install package: '{}'".format(package),
                e)


class PipPackage(object):
    """Entity to encapsulate information about a pip package to be
    installed.

    Version should be a version identifier
    E.g. '==3.0', '<4'

    Options should be a list of other options to run pip install with see:
    http://www.pip-installer.org/en/latest/reference/pip_install.html#requirements-file-format.
    """

    def __init__(self, name, version=None, options=[]):
        self.name = to_unicode(name)
        self.version = None
        self.options = []

        if version:
            self.version = to_unicode(version)

        if options:
            self.options = options

    def get_args(self):
        package = self.name
        if self.version:
            package += self.version

        args = [package]
        if self.options:
            args += self.options

        return args


def install_pip_package(package, virtualenv_name=None):
    """Install a pip package on the system, or in a virtualenvironment.
    package should be a PipPackage or a package name string"""
    args = ['pip', 'install', '-q']
    if isinstance(package, PipPackage):
        args += package.get_args()
    else:
        args.append(package)

    exception_message = ("Could not install pip package with command args: "
            "'{}'".format(args))

    if virtualenv_name != None:
        validate_virtualenv_name(virtualenv_name)
        exception_message += " in virtualenv: '{}'".format(virtualenv_name)
        try:
            virtualenvwrapper_call(args, virtualenv_name=virtualenv_name)
        except Exception as e:
            raise DebugException(exception_message, e)
    else:
        # When not in the virtualenvironment, we must use sudo to pip install.
        args.insert(0, 'sudo')
        try:
            quiet_call(args)
        except Exception as e:
            raise DebugException(exception_message, e)


def install_pip_requirements(file_path, virtualenv_name):
    """Install a pip requirements file in a virtualenvironment."""
    validate_virtualenv_name(virtualenv_name)
    try:
        virtualenvwrapper_call(['pip', 'install',  '-qr', file_path],
                virtualenv_name=virtualenv_name, quiet_out=False)
    except Exception as e:
        raise DebugException("Could not install pip packages from '{}' in "
                "virtualenv: '{}'".format(file_path, virtualenv_name), e)


def make_virtualenvironment(python_version, virtualenv_name):
    """Create a new virtualenvironment with a specific python version."""
    validate_virtualenv_name(virtualenv_name)
    try:
        virtualenvwrapper_call(['mkvirtualenv', '-p',
                '/usr/bin/{}'.format(python_version), virtualenv_name])
    except Exception as e:
        raise DebugException("Could not create virtualenv: '{}' with python: "
                "'{}'".format(virtualenv_name, python_version), e)


def destroy_virtualenvironment(virtualenv_name):
    """Destroy a virtualenvironment."""
    validate_virtualenv_name(virtualenv_name)
    try:
        virtualenvwrapper_call(['rmvirtualenv', virtualenv_name])
    except Exception as e:
        raise DebugException("Could not destroy virtualenv: '{}'".format(
                virtualenv_name), e)


def add_virtualenvwrapper_shell_config():
    """Add/replace virtualenvwrapper config lines in a shell config file."""

    replaced_existing = False

    if not isfile(shell_conf_path):
        raise Exception("'{}' does not exist.".format(shell_conf_path))

    # Read all lines from shell config file.
    with EncodedFile(shell_conf_path, 'r') as f:
        lines = f.readlines()
        file_content = mmap(f.fileno(), 0, access=ACCESS_READ)

    # Check if config already exists in shell config file.
    if (file_content.find(virtualenv_conf_start) > -1 and
             file_content.find(virtualenv_conf_end) > -1):
        # Rewrite the config file, replacing any existing virtualenvwrapper
        # config.
        with EncodedFile(shell_conf_path, 'w') as f:
            delete_line = False
            for line in lines:
                line = to_unicode(line)
                if virtualenv_conf_end in line:
                    delete_line = False
                    print('---- Replacing Virtualenv config in {}.'.format(
                            shell_conf_path))
                    f.write(get_virtualenvwrapper_conf_lines())
                    replaced_existing = True
                if not delete_line:
                    f.write(line)
                if virtualenv_conf_start in line:
                    delete_line = True

    if not replaced_existing:
        # If there was no existing config to replace, append it to the end.
        virtualenv_conf = ''.join([
                virtualenv_conf_start,
                '\n',
                get_virtualenvwrapper_conf_lines(),
                virtualenv_conf_end]
                ) + '\n'

        print('---- Appending Virtualenv config to {}.'.format(
                shell_conf_path))
        with EncodedFile(shell_conf_path, 'a') as shell_conf_file:
            shell_conf_file.write(virtualenv_conf)


def add_virtualenvironment_environment_variables(virtualenv_name, variables):
    """Add environment variable exporting/unsetting to the virtualenv
    postactivate/preactivate hook scripts."""
    virtualenv_name = to_unicode(virtualenv_name)

    # Write an export line for each variable in the postactivate script.
    postactivate_path = join(workon_home, virtualenv_name, 'bin',
            'postactivate')
    with EncodedFile(postactivate_path, 'w') as postactivate:
        for var, value in iteritems(variables):
            postactivate.write("export {}='{}'\n".format(to_unicode(var),
                    to_unicode(value)))

    # Write an unset line for each variable in the predeactivate script.
    predeactivate_path = join(workon_home, virtualenv_name, 'bin',
            'predeactivate')
    with EncodedFile(predeactivate_path, 'w') as predeactivate:
        for var, value in iteritems(variables):
            predeactivate.write("unset {}\n".format(to_unicode(var)))


def validate_project_does_not_exists(project_name):
    """Ensures that a given project name does not already exist as a directory
    or as a virtualenvironment."""
    if isdir(project_name):
        raise Exception("'{}' already exists in current directory.".format(
                project_name))
    if isdir(join(getenv('HOME'), '.virtualenvs', project_name,)):
        raise Exception("'{}' virtualenv already exists.".format(
                project_name))

def get_next_step_instructions(project_name):
    """Gets the 'Next step' instructions that apply to all types of project.
    These will be displayed before project-specific other next step
    instructions."""
    
    return [
            "Run 'source {shell_config}'".format(shell_config=shell_conf_path)
            ]

def get_further_config_instructions(project_name):
    """Gets the 'Further configuration' instructions that apply to all types of
    project. These will be displayed before project-specific other further
    configuration instructions."""
    
    return [
            ("Add configuration settings outside of version control in "
            "~/.virtualenvs/{site}/postactivate").format(site=project_name),
            ("Run 'workon {site}' each time you edit "
            "~/.virtualenvs/{site}/postactivate").format(site=project_name)
            ]
