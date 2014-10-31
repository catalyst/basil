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

BasilManagerHandler.__init__ does url handler config

"""
import json
import os
from os.path import join
import sys

import bottle

import core
import keys
import settings

messages = []

projects_dir = settings.projects_dir

basil_config_file = 'basil.json'
not_open_tpl = """
    Your {} project isn't open. Click on the "Start" button to open it. The
    project must be open before you can see the output (e.g. a Home Page)
    or run commands"""
status2friendly = {
    "not_created": not_open_tpl,
    "poweroff": not_open_tpl,
    "aborted": not_open_tpl + """
        <br><br>Note - This project was abruptly stopped without having been
        closed first.
        Try to avoid this happening by always closing projects before
        turning off your machine.
        Not doing so may cause problems which require the project to be
        destroyed and rebuilt.
        """,
    "running": """
        Your {} project is running which means you can view its output (e.g. a
        Home Page). Don't forget to Close it before turning off your machine.
        """}

command_progress = None

@bottle.route('/')
def home():
    return bottle.template('home_template', title="Basil Project Manager",
        template_dropdown=keys.TEMPLATE,
        template_infos=core.get_templates())

@bottle.route('/static/<filepath:path>')
def server_static(filepath):
    static_path = os.path.split(core.__file__)[0]
    return bottle.static_file(filepath,
        root='{}/static'.format(static_path))

@bottle.get('/get-fields')
def get_template_fields():
    template_name = bottle.request.GET.get(keys.PROJECT_TEMPLATE_NAME)
    fields = core.get_fields(template_name)
    return json.dumps(fields)

@bottle.post('/create-project')
def create_project():
    template_name = bottle.request.forms.get(keys.PROJECT_TEMPLATE_NAME)
    values = {item: bottle.request.forms[item] for item in bottle.request.forms}
    del values[keys.PROJECT_TEMPLATE_NAME]
    try:
        core.create(template_name, values)
    except Exception as e:
        errors = json.dumps(e.args[0])
        return bottle.HTTPError(status=500, exception=errors)
    return json.dumps("Successfully created project \"{}\""
        .format(values[keys.PROJECT_NAME]))

@bottle.error(500)
def error500(error): # don't want the default page
    return error.exception

@bottle.route('/get-statuses')
def get_statuses():
    try:
        project_statuses = core.get_project_statuses()
        project_feedback = []
        if project_statuses:
            for project_status in project_statuses:
                project_state_display = (project_status.state.title()
                    .replace("_", " "))
                project_feedback.append({
                    "project_name": project_status.project_name,
                    "project_directory": join(settings.projects_dir,
                        project_status.project_name),
                    "template_name": project_status.template_name,
                    "template_version": project_status.template_version,
                    "project_state": project_state_display,
                    "project_state_msg": status2friendly.get(
                        project_status.state, project_status.state_human_long)
                        .format(project_status.project_name),
                    "webserver_port": project_status.webserver_port,
                    "allow_destroy": project_status.allow_destroy,
                })
        else:
            project_feedback = ""
    except Exception as e:
        msg = str(e)
        if not msg:
            msg = "Unknown error"
        # can grab msg at AJAX jQuery end as jqXHR.responseText
        return bottle.HTTPError(status=500, exception=msg)
    else:
        payload = json.dumps(project_feedback).encode("utf-8")
        return payload

def get_reply_payload(func, args):
    global command_progress
    try:
        command_progress = func(*args) # command_progress is a mutable that is probably yet to be updated (if actual task passed to a thread)
        reply_payload = {"Action state": "submitted successfully"}
    except Exception as e:
        reply_payload = {"Unable to execute action. Error: ": str(e)}
        # ...  AND any progress requests
        command_progress = core.CommandProgress()
        command_progress.state = keys.CommandProgressStates.ERROR
    return json.dumps(reply_payload).encode("utf-8")

@bottle.post('/project-start')
def project_start():
    return get_reply_payload(func=core.start_project,
        args=[bottle.request.forms.get(keys.PROJECT_DIRECTORY)])

@bottle.post('/project-stop')
def project_stop():
    return get_reply_payload(func=core.stop_project,
        args=[bottle.request.forms.get(keys.PROJECT_DIRECTORY)])

@bottle.post('/project-reset')
def project_stop():
    return get_reply_payload(func=core.reset_project,
        args=[bottle.request.forms.get(keys.PROJECT_DIRECTORY)])

@bottle.post('/project-destroy')
def project_stop():
    return get_reply_payload(func=core.destroy_project,
        args=[bottle.request.forms.get(keys.PROJECT_DIRECTORY)])

@bottle.post('/open-code')
def project_stop():
    return get_reply_payload(func=core.open_code,
        args=[bottle.request.forms.get(keys.PROJECT_DIRECTORY)])

@bottle.post('/open-shell')
def project_stop():
    return get_reply_payload(func=core.open_shell,
        args=[bottle.request.forms.get(keys.PROJECT_DIRECTORY)])

@bottle.route('/get-command-progress')
def get_command_progress():
    try:
        payload = command_progress.to_json()
    except Exception as e:
        payload = ("Unable to read progress details from object. "
            "Orig error: {}".format(e))
    return payload

def run_server():
    debug = True
    try:
        core.verify_vagrant_version()
    except Exception as ex:
        print(ex)
        return
    port = 8000
    while True:
        try:
            bottle.run(host='localhost', port=port, debug=debug, reloader=debug)
            break
        except Exception:
            port += 1
    print("\n\n" + "*"*50 + "\n\nClosing down Basil ..."
        "\n\nIf you inadvertantly left any projects open,\nreopen Basil"
        " and close them.\n\n" + "*"*50)
    if debug:
        print("Note - please close again - reloader is currently set to True")

if __name__ == "__main__":
    run_server()
