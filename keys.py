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
ACTION_OPEN = "open" # vagrant up + open start page
ACTION_EDIT = "edit" # files in shared folder
ACTION_SSH = "ssh"
ACTION_HALT = "halt"
ACTION_DESTROY = "destroy"
ACTIONS = [ACTION_OPEN, ACTION_EDIT, ACTION_SSH, ACTION_HALT, ACTION_DESTROY]

TEMPLATE = "template"

# POST vars
PROJECT_NAME = "project_name"
PROJECT_DIRECTORY = "project_directory"

PROJECT_TEMPLATE_NAME = "template_name"
PROJECT_TEMPLATE_VERSION = "template_version"
PROJECT_VALUES = "values"
PROJECT_PORTS = "ports"

PROJECT_BASE = "project_base"

BASIL_INTERNAL_CONFIG = ".basil"
TEMPLATE_CONFIG = "config.json"

TEMPLATE_CONFIG_FIELDS = "fields"
TEMPLATE_CONFIG_TITLE = "title"
TEMPLATE_CONFIG_DESCRIPTION = "description"
TEMPLATE_CONFIG_TEMPLATE_VERSION = "template_version"
TEMPLATE_CONFIG_PROCESS = "process"
TEMPLATE_CONFIG_PORTS = "port_tags"
TEMPLATE_CONFIG_WEBSERVER_PORT = "webserver_port"

TEMPLATE_FIELD_TITLE = "title"
TEMPLATE_FIELD_DESCRIPTION = "description"
TEMPLATE_FIELD_TYPE = "type"
TEMPLATE_FIELD_DEFAULT = "default"
TEMPLATE_FIELD_VALIDATORS = "validators"

# to override method for getting project status this function must be in lib.py
PROJECT_STATUS_FUNCNAME = "get_project_status"

VAGRANT_STATUS_STATE = "state"
VAGRANT_STATUS_STATE_HUMAN_SHORT = "state-human-short"
VAGRANT_STATUS_STATE_HUMAN_LONG = "state-human-long"
VAGRANT_COMMA = "%!(VAGRANT_COMMA)"

VAGRANT_STATUS_STATE_UNKNOWN = "unknown"

PROGRESS_STATE = "state"
PROGRESS_PROGRESS = "progress"
PROGRESS_SUMMARY = "summary"
PROGRESS_DETAILS = "details"
PROGRESS_ERROR = "error"

from enum import Enum

class CommandProgressStates(Enum):
    ACTIVE = 1
    FINISHED = 2
    ERROR = 3
