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
from functools import partial
import importlib.machinery
import json
import os
from os.path import join
import re
import shutil
import subprocess
import sys
from threading import Thread
import tkinter
from tkinter import filedialog
import webbrowser

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
    'template_version', 'state', 'state_human_short', 'state_human_long',
    'webserver_port'))

# Project directory is an absolute path. We only want to store template_name
ProjectInfo = namedtuple('ProjectInfo', ('project_name', 'template_name',
    'template_version', 'ports'))

default_fields = [
    Field('project_name', 'text', 'Project name', 'The name of this project',
        '', [ 'directory' ]),
]

OpenCommand = namedtuple("OpenCommand", ("cmd_bits", "lbl"))

basil_tag_start = "{{__basil__."
basil_tag_end = "}}"
basil_bash_start = "#basil_bash_start #####" # using # instead of, for eg, * otherwise regex treats as multiple repeats ;-)
basil_bash_end = "#basil_bash_end #####"

port_range_start = 45600

my_platform = "my_platform"
LINUX = "Linux"
WINDOWS = "Windows"
MAC = "Mac OSX"
UNKNOWN_PLATFORM = "Unknown platform"
if sys.platform.startswith("darwin"):
    my_platform = MAC
elif os.name == "nt":
    my_platform = WINDOWS
elif os.name == "posix":
    my_platform = LINUX
else:
    my_platform = UNKNOWN_PLATFORM

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
    fields = { field.name: field for field in default_fields }
    for field_name, field in config[keys.TEMPLATE_CONFIG_FIELDS].items():
        fields[field_name] = (Field(field_name,
            field[keys.TEMPLATE_FIELD_TYPE],
            field[keys.TEMPLATE_FIELD_TITLE],
            field[keys.TEMPLATE_FIELD_DESCRIPTION],
            field[keys.TEMPLATE_FIELD_DEFAULT],
            field[keys.TEMPLATE_FIELD_VALIDATORS]))
    return list(fields.values())

def get_default_field_validators(field_name):
    """
    Raises exception if can't find in default fields.
    """
    field_name2validators = {x.name: x.validators for x in default_fields}
    return field_name2validators[field_name]

def get_ports(template_name):
    """
    We want to be able to assign ports to the projects to avoid potential
    collisions. Some templates will need to use the same port in multiple
    places e.g. a webserver port. E.g.

    Inside project:

       config_somewhere: .... webserver_port
       other_config: ... ssh_port
       other_config: ... webserver_port

    we want basil to do something like:

       config_somewhere: .... 8080
       other_config: ... 8022
       other_config: ... 8080

    Returns a dictionary that maps each "port tag" in the template to an
    available port that isn't in use by any other projects.
    """
    assigned_ports = {}
    config = template_load_config(template_name)
    if keys.TEMPLATE_CONFIG_PORTS in config:
        port_tags = config[keys.TEMPLATE_CONFIG_PORTS]
        used_ports = []
        for project in get_projects():
            used_ports += project.ports.values()
        current_port = port_range_start
        for port_tag in port_tags:
            while current_port in used_ports:
                current_port += 1
            assigned_ports[port_tag] = current_port
            current_port += 1
    return assigned_ports

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
    if field_name in config[keys.TEMPLATE_CONFIG_FIELDS]:
        try:
            validators = (config[keys.TEMPLATE_CONFIG_FIELDS][field_name]
                [keys.TEMPLATE_FIELD_VALIDATORS])
        except KeyError:
            raise Exception("Unable to locate validator details for \"{}\""
                .format(field_name))
    else:
        validators = get_default_field_validators(field_name)
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
        else:
            raise Exception('Validation function not found: {}'.format(
                validator_name))
    return True

def process_rewrite(path, values):
    """
    values dict -- may have numbers (e.g. port) as vals
    """
    with fileinput.input(files=(path), inplace=True) as f:
        for line in f:
            for field_name, value in values.items():
                orig = basil_tag_start + field_name + basil_tag_end
                line = line.replace(orig, str(value))
            print(line, end="")

def process_rename(path, values):
    """
    values dict -- may have numbers (e.g. port) as vals
    """
    directory, name = os.path.split(path)
    orig_name = name
    for field_name, value in values.items():
        orig = basil_tag_start + field_name + basil_tag_end
        name = name.replace(orig, str(value))
    if name != orig_name:
        os.rename(join(directory, orig_name), join(directory, name))

def populate_templates(project_directory, values):
    # Rewrite/rename files (replacing basil tags).
    to_process_rewrite = []
    to_process_rename = []
    # Topdown false, so that we will work on subdirectories first, which we need
    # in order to rename effectively.
    for root, dirs, files in os.walk(project_directory, topdown=False):
        for path in [ join(root, name) for name in files ]:
            try:
                process_rewrite(path, values)
            except Exception as e:
                raise Exception("Problem rewriting \"{}\" with values: {}"
                    .format(path, values))
        for path in  [ join(root, name) for name in files + dirs ]:
            try:
                process_rename(path, values)
            except Exception as e:
                raise Exception("Problem renaming \"{}\" with values: {}"
                    .format(path, values))

def create_project_config(template_name, values, ports, project_directory):
    """
    Create internal basil config file (.basil)
    """
    template_config = template_load_config(template_name)
    template_version = template_config[keys.TEMPLATE_CONFIG_TEMPLATE_VERSION]
    project_config = {
        keys.PROJECT_TEMPLATE_NAME: template_name,
        keys.PROJECT_TEMPLATE_VERSION: template_version,
        keys.PROJECT_VALUES: values,
        keys.PROJECT_PORTS: ports,
    }
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
    # Get ports
    ports = get_ports(template_name)
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
    rewrite_values = values.copy()
    rewrite_values.update(ports)
    populate_templates(project_directory, rewrite_values)
    # Create internal basil config file (.basil)
    try:
        create_project_config(template_name, values, ports, project_directory)
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
            ports = project_config[keys.PROJECT_PORTS]
            template_config = template_load_config(template_name)
            project_infos.append(ProjectInfo(project_name, template_name,
                template_version, ports)) # @Later - ensure anything expected ends up in the schema for testing config.json
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
        project_statuses.append(get_project_status(
            project_info.project_name,
            project_info.template_name,
            project_info.template_version))
    return project_statuses

def get_project_status_via_vagrant(project_name, template_name,
        template_version):
    """
    http://docs.vagrantup.com/v2/cli/machine-readable.html
    Note - API not stabilised yet
    """
    project_directory = join(projects_dir, project_name)
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
    project_config = project_load_config(project_name)
    webserver_port = project_config[keys.PROJECT_PORTS].get(
        keys.TEMPLATE_CONFIG_WEBSERVER_PORT, 8888)
    try:
        project_status = ProjectStatus(project_name, template_name,
            template_version,
            status_dict[keys.VAGRANT_STATUS_STATE],
            status_dict[keys.VAGRANT_STATUS_STATE_HUMAN_SHORT],
            status_dict[keys.VAGRANT_STATUS_STATE_HUMAN_LONG],
            webserver_port)
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
        project_status_func = get_project_status_via_vagrant
    return project_status_func(project_name, template_name,
        template_version)

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

def execute_blocking_vagrant_cmd(command_list, project_directory,
        command_progress, msg_transformer=None, callback=None):
    """
    command_list -- must be a list ready for subprocess to use.

    command_progress -- mutable which allows us to communicate progress simply
    by updating it.

    msg_transformer -- function to turn message string to friendlier version

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
    progress = 0
    while True:
        if p.poll() == None:
            while True:
                progress += 1
                command_progress[keys.PROGRESS_PROGRESS] = progress;
                msg = str(p.stdout.readline(), "utf-8").strip()
                if not msg:
                    break
                if msg_transformer:
                    summary, details = msg_transformer(msg)
                else:
                    summary, details = None, msg
                if not summary:
                    summary = command_progress[keys.PROGRESS_SUMMARY]
                if not details:
                    details = command_progress[keys.PROGRESS_DETAILS]
                command_progress[keys.PROGRESS_SUMMARY] = summary;
                command_progress[keys.PROGRESS_DETAILS] += details + "\n"
            error = str(p.stderr.read(), "utf-8").strip()
            if error:
                cmd = " ".join(command_list)
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
        else:
            break
    command_progress[keys.PROGRESS_FINISHED] = True
    if callback:
        callback()

def run_vagrant_cmd(command_list, project_directory, blocking=False,
        msg_transformer=None, callback=None):
    """
    command_list -- must be a list ready for subprocess to use.
    """
    command_progress = {
        keys.PROGRESS_FINISHED: False,
        keys.PROGRESS_PROGRESS: 0,
        keys.PROGRESS_SUMMARY: "In progress",
        keys.PROGRESS_DETAILS: "",
    }
    cmd = partial(execute_blocking_vagrant_cmd, command_list,
        project_directory, command_progress, msg_transformer, callback)
    if blocking:
        cmd()
    else:
        t = Thread(target=cmd)
        t.start()
    return command_progress

def start_msg_transformer(text):
    bringing_up = "Bringing machine up"
    booting = "Booting Virtual Machine (may take a few minutes)"
    transformers = [
        (r"Bringing machine.+up",(bringing_up, text)),
        (r"Clearing any previously set forwarded ports",(bringing_up, text)),
        (r"Fixed port collision",(bringing_up, text)),
        (r"previously set network interfaces",(bringing_up, text)),
        (r"Preparing network interfaces",(bringing_up, text)),
        (r"Forwarding ports",(bringing_up, text)),
        (r"Booting VM",(booting, text)),
        (r"Waiting for machine to boot",(booting, text)),
        (r"Machine booted",("Successfully booted", text)),
        (r"previously set network interfaces",(bringing_up, text)),
        (r"previously set network interfaces",(bringing_up, text)),
        (r"previously set network interfaces",(bringing_up, text)),
        (r"previously set network interfaces",(bringing_up, text)),
        (r"previously set network interfaces",(bringing_up, text)),
        (r"previously set network interfaces",(bringing_up, text)),
    ]
    summary = None
    details = text
    for pattern, response in transformers:
        if re.search(pattern, text):
            summary, details = response
            break
    return summary, details

# @TODO: Should we be passing the project_name instead?
def start_project(project_directory):
    """
    Open project - vagrant up.
    """
    command_progress = run_vagrant_cmd(command_list=["vagrant", "up"],
        project_directory=project_directory, blocking=False,
        msg_transformer=start_msg_transformer)
    return command_progress

def open_code(project_directory):
    """
    Open file browser in folder where the code is. Then open the file selected
    using the default text editor for that file type (unless html, in which
    case, use the first text editor you can get working).

    See http://stackoverflow.com/questions/434597/open-document-with-default-application-in-python
    """
    try:
        root = tkinter.Tk()
        root.withdraw()
        filepath = filedialog.askopenfilename(initialdir=project_directory)
    except Exception as e:
        raise Exception("Unable to identify a file in \"{}\""
            .format(project_directory))
    if not filepath: # don't bother them with a message
        return
    shell = False
    is_html = filepath.endswith((".htm", ".html", ".xhtm", ".xhtml"))
    if my_platform == MAC:
        if is_html:
            editor_cmds_to_try = [
                OpenCommand(["open", "-a", "TextEdit"], "TextEdit"),
            ] # anything needed other than TextEdit?
        else:
            editor_cmds_to_try = [
                OpenCommand(["open"], "default"),
            ]
    elif my_platform == WINDOWS:
        if is_html:
            editor_cmds_to_try = [ # surely Windows users deserve a chance to use something decent
                OpenCommand(["Notepad++"], "Notepad++"),
                OpenCommand(["notepad"], "Notepad"),
                OpenCommand(["wordpad"], "Wordpad"),
            ]
        else:
            editor_cmds_to_try = [
                OpenCommand(["start"], "default"),
            ]
            shell = True
    elif my_platform == LINUX:
        if is_html: # the order of these could be controversial ;-)
            editor_cmds_to_try = [
                OpenCommand(["gedit"], "gedit"),
                OpenCommand(["vim"], "vim"),
                OpenCommand(["emacs"], "emacs"),
                OpenCommand(["nano"], "nano"),
                OpenCommand(["pico"], "pico"),
            ]
        else:
            editor_cmds_to_try = [
                OpenCommand(["xdg-open"], "default"),
            ]
    last_error = None
    editors_tried = []
    for editor_cmd in editor_cmds_to_try:
        editor_lbl = editor_cmd.lbl
        editors_tried.append(editor_lbl)
        cmd_bits = editor_cmd.cmd_bits
        cmd_bits += [filepath,]
        command = " ".join(cmd_bits)
        try:
            if shell:
                retcode = subprocess.call(command, shell=True)
            else:
                retcode = subprocess.call(cmd_bits, shell=False)
            if retcode < 0:
                continue
            else:
                return # success!
        except OSError as e:
            last_error = e
            continue
    # Something went wrong if you are here :-). Report on the last problem.
    # Only ever multiple if was trying to open html.
    multiple_attempts = (len(editors_tried) > 1)
    msg_bits = ["Unable to open code file \"{}\".".format(filepath)]
    if multiple_attempts:
        msg_bits.append("None of the following text editors worked: {}"
            .format(", ".join(editors_tried)))
    else:
        msg_bits.append("Running the command \"{}\" failed to open the {} text "
            "editor".format(command, editor_lbl))
    if last_error:
        msg_bits.append("Original error: {}".format(last_error))
    raise Exception("\n".join(msg_bits))

def open_shell(project_directory):
    """
    Open a terminal with the ssh command already run.

    Works very nicely in Linux using bash.
    See http://stackoverflow.com/questions/3512055/avoid-gnome-terminal-close-after-script-execution

    Not added Windows implementation yet. Not checked Mac implementation
    although probably Linux approach will work.
    """
    if my_platform in (LINUX, MAC):
        rcfile_path = join(project_directory, "rcfile")
        with open(rcfile_path, "w") as f:
            cmd = """cd "{}" && vagrant ssh""".format(project_directory)
            f.write("{}\n{}\n{}".format(basil_bash_start, cmd, basil_bash_end))
            f.close()
        subprocess.check_output(["gnome-terminal", "-e", "bash --rcfile \"{}\""
            .format(rcfile_path)])
    elif my_platform == WINDOWS:
        raise Exception("Open SSH not implemented yet for Windows")
    else:
        raise Exception("Unexpected platform when trying to open ssh")

def stop_project(project_directory):
    """
    Stop project - vagrant halt.
    """
    command_progress = run_vagrant_cmd(command_list=["vagrant", "halt"],
        project_directory=project_directory, blocking=True)
    return command_progress

def destroy_project(project_directory):
    """
    Destroy project - vagrant destroy. Note - it is assumed that you have
    already checked with the user that this is what they really want to do.
    Too late if you get to here ;-).
    """
    callback = partial(shutil.rmtree, project_directory)
    command_progress = run_vagrant_cmd(command_list=["vagrant", "destroy", "--force"],
        project_directory=project_directory, blocking=True, callback=callback)
    return command_progress
