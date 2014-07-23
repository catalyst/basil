#!/usr/bin/python3
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

"""
name -- a machine name. E.g. 'django'

title -- means a human-readable name. E.g. 'Django'

templates are used to make projects.

templates are folders containing files including some config for basil and then
some vagrant content to make the vagrant file for.

templates are all stored in a standard location (/etc/?) somewhere. Currently
testing with a local path.

Once a template has made a project, it has no further connection to that
project.
"""

from collections import namedtuple
import fileinput
import importlib
import json
import os
from os.path import join
import re
import shutil
import subprocess

import actions
import keys
import settings
import validation

templates_dir = settings.templates_dir
projects_dir = settings.projects_dir

TemplateInfo = namedtuple('TemplateInfo', ('name', 'title', 'description',
    'template_version'))

Field = namedtuple('Field', ('name', 'type', 'title', 'description', 'default',
    'validators'))
# http://docs.vagrantup.com/v2/cli/machine-readable.html
ProjectStatus = namedtuple('ProjectStatus', ('project_name', 'template_name',
    'template_version', 'state', 'state_human_short', 'state_human_long'))

# Project directory is an absolute path. We only want to store template_name
ProjectInfo = namedtuple('ProjectInfo', ('project_name', 'template_name',
    'template_version'))

default_fields = [
    Field('project_name', 'text', 'Project name', 'The name of this project',
        '', [ 'directory' ]),
]

basil_tag_start = '{{__basil__.'
basil_tag_end = '}}'

def template_load_lib(template_name):
    try:
        loader = importlib.machinery.SourceFileLoader(template_name + '.lib',
            os.path.join(templates_dir, template_name, 'lib.py'))
        template_lib = loader.load_module()
    except:
        template_lib = None
    return template_lib

def template_load_config(template_name):
    return load_config(join(templates_dir, template_name, keys.TEMPLATE_CONFIG))

def project_load_config(project_name):
    return load_config(join(projects_dir, project_name,
        keys.BASIL_INTERNAL_CONFIG))

def load_config(config_path):
    config = {}
    with open(config_path, 'r') as f:
        try:
            config = json.load(f)
        except Exception as e:
            raise Exception("Unable to get config. Problem reading "
                "JSON in \"{}\". Original error: {}".format(config_path, e))
    return config

def install_template(template_path):
    """
    Copies the template from template_path into templates_directory.
    @LATER: Should also accept .tar.gz/.zip/.bz2/etc.
    """
    template_name = os.path.split(template_path)[-1]
    dest_path = join(templates_dir, template_name)
    try:
        shutil.copy(template_path, dest_path)
    except Exception as e:
        raise Exception("Unable to install template \"{}\". "
            "Original error: {}".format(template_name, e))

def get_templates():
    """
    Templates are folders. They must contain a config.json file and optionally
    lib.py.

    Returns a list of TemplateInfos; one for each template in
    templates_directory. E.g. [ TemplateInfo('django', 'Django',
        'A basic Django development installation.') ]
    """
    template_infos = []
    template_names = [x for x in os.listdir(templates_dir)
        if os.path.isdir(join(templates_dir, x))]
    for template_name in template_names:
        template_config = template_load_config(template_name)
        template_infos.append(TemplateInfo(
            template_name,
            template_config[keys.TEMPLATE_CONFIG_TITLE],
            template_config[keys.TEMPLATE_CONFIG_DESCRIPTION],
            template_config[keys.TEMPLATE_CONFIG_TEMPLATE_VERSION]))
    return template_infos

def get_fields(template_name):
    """
    Given the machine name of a template, returns a list of Field tuples that
    are defined for that template.

    Always includes the fields in default_fields, but allow overriding of those
    from templates.
    """
    config = template_load_config(template_name)
    fields = list(default_fields)
    for field_name, field in config[keys.TEMPLATE_CONFIG_FIELDS].items():
        fields.append(Field(field_name,
            field[keys.TEMPLATE_FIELD_TYPE],
            field[keys.TEMPLATE_FIELD_TITLE],
            field[keys.TEMPLATE_FIELD_DESCRIPTION],
            field[keys.TEMPLATE_FIELD_DEFAULT],
            field[keys.TEMPLATE_FIELD_VALIDATORS]))
    return fields

def get_default_field_validators(field_name):
    """
    Raises exception if can't find in default fields.
    """
    field_name2validators = {x.name: x.validators for x in default_fields}
    return field_name2validators[field_name]

def validate_field(template_name, field_name, value):
    """
    Call each validator defined for the field in the template with the given
    value.

    Note - validators are not defined in the config.json file if they are
    default fields.

    If any validator returns False, return False, otherwise, return True.

    For each validator named x, look for the function validator_x, first in the
    template's lib.py, then in basil's validators.py.
    """
    config = template_load_config(template_name)
    try:
        validators = get_default_field_validators(field_name)
    except Exception:
        try:
            validators = (config[keys.TEMPLATE_CONFIG_FIELDS][field_name]
                [keys.TEMPLATE_FIELD_VALIDATORS])
        except KeyError:
            raise Exception("Unable to locate validator details for \"{}\""
                .format(field_name))
    template_lib = template_load_lib(template_name)
    for validator_name in ['validate_' + validator for validator in validators]:
        if template_lib:
            validate_func = template_lib.__dict__.get(validator_name)
            if validate_func:
                if not validate_func(value):
                    return False
                continue
        validate_func = validation.__dict__.get(validator_name)
        if validate_func:
            if not validate_func(value):
                return False
    return True

def process_rewrite(path, values):
    with fileinput.input(files=(path), inplace=True) as f:
        for line in f:
            for field_name, value in values.items():
                line = line.replace(
                    basil_tag_start + field_name + basil_tag_end, value)
            print(line, end='')

def process_rename(path, values):
    directory, name = os.path.split(path)
    orig_name = name
    for field_name, value in values.items():
        name = name.replace(basil_tag_start + field_name + basil_tag_end, value)
    if name != orig_name:
        os.rename(join(directory, orig_name), join(directory, name))

def create_project_config(template_name, values, project_directory):
    """
    Create internal basil config file (.basil)
    """
    template_config = template_load_config(template_name)
    template_version = template_config[keys.TEMPLATE_CONFIG_TEMPLATE_VERSION]
    project_config = {
        keys.PROJECT_TEMPLATE_NAME: template_name,
        keys.PROJECT_TEMPLATE_VERSION: template_version,
        keys.PROJECT_VALUES: values}
    # @Later -- check json for required structure
    with open(join(project_directory, keys.BASIL_INTERNAL_CONFIG), 'w') as f:
        json.dump(project_config, f)    

def create(template_name, values):
    """
    Values should be a dictionary, mapping field names to string values. E.g. { 'project_name': 'My New Project' }
    This function:
    * Performs final validation on all of the field values.
    * Performs any post-processing of field values defined by the template.
      * Look for process(values) in the template's lib.py.
    * Copies the "vagrant template" *inside* templates_directory/template_name to projects_directory
    * "Fill in the blanks" of the new project directory with values.
    * Place a '.basil' json file in the project, containing values, the template name, and an initial state?
    * Runs the "up" action on the new project
    """
    # testing
    skip_creation = False
    if skip_creation:
        import time
        time.sleep(2)
        print("*"*20 + " Skipping creation for test purposes. Set skip_creation"
            "to False later!!! " + "*"*20)
        return
    # Validation
    for field_name, value in values.items():
        if not validate_field(template_name, field_name, value):
            raise Exception("Validation problem for \"{}\" field"
                .format(field_name))
    # Post-processing
    template_lib = template_load_lib(template_name)
    if template_lib:
        process_func = template_lib.__dict__.get(keys.TEMPLATE_CONFIG_PROCESS)
        if process_func:
            process_func(values)
    project_name = values[keys.PROJECT_NAME]
    # Copy vagrant template
    project_directory = join(projects_dir, project_name)
    if os.path.exists(project_directory):
        raise Exception("The \"{}\" project already exists so either "
            "\"Destroy Project\" or choose another name".format(project_name))
    try:
        shutil.copytree(join(templates_dir, template_name, keys.PROJECT_BASE),
            project_directory)
    except Exception as e:
        raise Exception("Unable to create project from template \"{}\". "
            "Original error: {}".format(template_name, e))
    # Rewrite/rename files (replacing basil tags).
    to_process_rewrite = []
    to_process_rename = []
    # Topdown false, so that we will work on subdirectories first, which we need
    # in order to rename effectively.
    for root, dirs, files in os.walk(project_directory, topdown=False):
        for path in [ join(root, name) for name in files ]:
            process_rewrite(path, values)
        for path in  [ join(root, name) for name in files + dirs ]:
            process_rename(path, values)
    # Create internal basil config file (.basil)
    try:
        create_project_config(template_name, values, project_directory)
    except Exception:
        shutil.rmtree(project_directory)
        raise Exception("Unable to create project configuration file ({}) "
            "so project not created.".format(keys.BASIL_INTERNAL_CONFIG))

def get_projects():
    """
    Returns a list of ProjectInfos for each project in projects_directory.
    When listing actions, always include the actions in default_actions.
    """
    project_infos = []
    project_names = [x for x in os.listdir(projects_dir)
        if os.path.isdir(join(projects_dir, x))]
    for project_name in project_names:
        try:
            project_config = project_load_config(project_name)
            template_name = project_config[keys.PROJECT_TEMPLATE_NAME]
            template_version = project_config[keys.PROJECT_TEMPLATE_VERSION]
            template_config = template_load_config(template_name)
            project_infos.append(ProjectInfo(project_name, template_name,
                template_version)) # @Later - ensure anything expected ends up in the schema for testing config.json
        except Exception as e:
            raise Exception("Unable to get project details for \"{}\" "
                "project. {}".format(project_name, e))
    return project_infos

def get_project_statuses():
    """
    Get project statuses.
    """
    project_infos = get_projects()
    project_statuses = []
    for project_info in project_infos:
        project_statuses.append(get_project_status(project_info.project_name,
            project_info.template_name, project_info.template_version))
    return project_statuses

def get_project_status_via_std_vagrant(project_name, project_directory,
        template_name, template_version):
    """
    http://docs.vagrantup.com/v2/cli/machine-readable.html
    Note - API not stabilised yet
    """
    output = str(subprocess.check_output(["vagrant", "status",
        "--machine-readable"], cwd=project_directory), "utf-8")
    status_dict = {}
    for line in output.split("\n"):
        try:
            timestamp, target, msg_type, data = line.split(",")
        except ValueError:
            continue
        data = data.replace(keys.VAGRANT_COMMA, ",").replace("\\n", "<br>")
        if msg_type == keys.VAGRANT_STATUS_STATE:
            status_dict[keys.VAGRANT_STATUS_STATE] = data
        elif msg_type == keys.VAGRANT_STATUS_STATE_HUMAN_SHORT:
            status_dict[keys.VAGRANT_STATUS_STATE_HUMAN_SHORT] = data
        elif msg_type == keys.VAGRANT_STATUS_STATE_HUMAN_LONG:
            status_dict[keys.VAGRANT_STATUS_STATE_HUMAN_LONG] = data
    try:
        project_status = ProjectStatus(project_name, template_name,
            template_version,
            status_dict[keys.VAGRANT_STATUS_STATE],
            status_dict[keys.VAGRANT_STATUS_STATE_HUMAN_SHORT],
            status_dict[keys.VAGRANT_STATUS_STATE_HUMAN_LONG])
    except KeyError as e:
        raise Exception("Unable to get project status for \"{}\"."
            "\nOriginal error: {}".format(project_directory, e))
    return project_status

def get_project_status(project_name, template_name, template_version):
    """
    Uses lib.py version if available, otherwise default approach using vagrant.
    """
    template_lib = template_load_lib(template_name)
    project_status_func = None
    if template_lib:
        project_status_func = (template_lib.__dict__
            .get(keys.PROJECT_STATUS_FUNCNAME))
    if not project_status_func:
        project_status_func = get_project_status_via_std_vagrant
    project_directory = join(projects_dir, project_name)
    return project_status_func(project_name, project_directory,
        template_name, template_version)

def get_port_forwarded_collision_msg(cmd, error):
    forwarded_collision_result_pattern = (r"The forwarded port to (\d{4,5}) "
        r"is already in use on the host machine")
    port_forwarded_collision_result = re.search(
        forwarded_collision_result_pattern, error.replace("\n", " ")) # put on one line before searching
    try:
        port_forwarded = port_forwarded_collision_result.group(1)
    except Exception:
        port_forwarded = False
    if port_forwarded:
        msg = ("Try again after stopping any other projects that are open."
        "\nUnable to start project because it wants to share content "
        "with you over a port ({}) that is already in use - perhaps by "
        "another project.".format(port_forwarded))
    else:
        msg = None
    return msg

def run_vagrant_cmd(command_list, project_directory):
    """
    command_list -- must be a list ready for subprocess to use.

    Don't include lines breaks in exception - only the first line is sent via
    the header. Will be be displaying messages to user in html so use <br>
    instead. OK to use other html markup as well - it does no real harm if
    displaying in terminal.

    error_transforms -- functions taking cmd string and error string as input
    and returning a complete message if the error is of the correct sort. If
    not the right sort of error returns None.

    If no transformations of the error message occur we use the cmd and the
    raw error to form a basic error message.
    """
    p = subprocess.Popen(command_list, cwd=project_directory,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    unused, stderr = p.communicate()
    if stderr:
        cmd = " ".join(command_list)
        error = str(stderr, "utf-8")
        msg = None
        error_transforms = [get_port_forwarded_collision_msg, ]
        for error_transform in error_transforms:
            transformed_msg = error_transform(cmd, error)
            if transformed_msg:
                msg = transformed_msg
                break
        if not msg:
            msg = "Command \"{}\" failed. Reason: {}".format(cmd, error)
        raise Exception(msg.replace("\n", "<br><br>"))
    
def start_project(project_directory):
    """
    Open project - vagrant up.
    """
    run_vagrant_cmd(command_list=["vagrant", "up"],
        project_directory=project_directory)

def view_project(project_directory):
    """
    View output from project e.g. Home Page.
    """
    pass

def stop_project(project_directory):
    """
    Stop project - vagrant halt.
    """
    run_vagrant_cmd(command_list=["vagrant", "halt"],
        project_directory=project_directory)
    
def destroy_project(project_directory):
    """
    Destroy project - vagrant destroy. Note - it is assumed that you have
    already checked with the user that this is what they really want to do.
    Too late if you get to here ;-).
    """
    run_vagrant_cmd(command_list=["vagrant", "destroy", "--force"],
        project_directory=project_directory)
    shutil.rmtree(project_directory)
    
