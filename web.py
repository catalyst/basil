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

import cgi
from collections import namedtuple
import http.server
import json
from mimetypes import types_map
import os
from os.path import join
import re
import sys
import urllib

import core
import keys
import settings

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

def get_postvars(handler):
    """
    Returns dict of post variables. The vals are lists (usually of just
    one item).
    """
    ctype, unused = cgi.parse_header(handler.headers.get('content-type'))
    if ctype != 'application/x-www-form-urlencoded':
        raise Exception("Unexpected content type.")
    length = int(handler.headers.get('content-length'))
    b_postvars = urllib.parse.parse_qs(handler.rfile.read(length),
        keep_blank_values=1)
    postvars = {str(key, "utf-8"): [str(x, "utf-8") for x in val_list]
        for key, val_list in b_postvars.items()}
    return postvars


class Request(object):

    def __init__(self, handler):
        self.handler = handler
        self.response = 200
        self.response_msg = ""
        self.headers = {}

    def execute(self):
        """
        Must send a response and end headers otherwise the HTTPServer retries
        the request.
        """
        response_args = [self.response,]
        if self.response_msg:
            response_args.append(self.response_msg)
        self.handler.send_response(*response_args)
        for key, value in iter(self.headers.items()):
            self.handler.send_header(key, value)
        self.handler.end_headers()


class Page(Request):

    def __init__(self, handler):
        super(Page, self).__init__(handler)
        self.headers['Content-type'] = 'text/html'

    def title(self):
        return 'Basil'

    def head(self):
        """
        Add other css before main.css so main overrides others.
        Add other js after jquery core so they can use it.
        """
        return """
        <link rel="stylesheet" href="css/main.css">
        <script type="text/javascript" src="js/jquery.min.js"></script>
        <script type="text/javascript" src="js/underscore-min.js"></script>
        """

    def body(self):
        return ''

    def render(self):
        content = """
        <html>
          <head>
            <meta charset="UTF-8">
            <title>{title}</title>
            {head}
          </head>
          <body>
            <a href="/" title="Home page">
                <image id="basil-logo" src="images/basil_logo.png">
            </a>
            {body}
          </body>
        </html>
        """.format(title=self.title(), head = self.head(), body=self.body())
        return content.encode('utf-8')

    def get_postvars(self):
        return get_postvars(self.handler)

    def execute(self):
        super(Page, self).execute()
        self.handler.wfile.write(self.render())


class GetStatuses(Request):

    def __init__(self, handler):
        super(GetStatuses, self).__init__(handler)
        self.headers['Content-type'] = 'application/json'
        self.headers['Accept'] = 'text/plain'

    def execute(self):
        super(GetStatuses, self).execute()
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
                })
        else:
            project_feedback = ""
        payload = json.dumps(project_feedback).encode("utf-8")
        self.handler.wfile.write(payload)


class Action(Request):

    def __init__(self, handler):
        super(Action, self).__init__(handler)
        try:
            postvars = get_postvars(self.handler)
            self.project_directory = postvars[keys.PROJECT_DIRECTORY][0]
        except Exception as e:
            raise Exception("Unable to carry out page action. "
                "Original error: {}".format(e))

    def execute(self, func, args):
        try:
            func(*args)
        except Exception as e:
            self.response = 500
            self.response_msg = e
            print(e)
        super(Action, self).execute()


class ProjectStart(Action):

    def execute(self):
        super(ProjectStart, self).execute(func=core.start_project,
            args=[self.project_directory,])


class ProjectStop(Action):

    def execute(self):
        super(ProjectStop, self).execute(func=core.stop_project,
            args=[self.project_directory,])


class ProjectDestroy(Action):

    def execute(self):
        super(ProjectDestroy, self).execute(func=core.destroy_project,
            args=[self.project_directory,])


class OpenCode(Action):
    
    def execute(self):
        super(OpenCode, self).execute(func=core.open_code,
            args=[self.project_directory,])


class OpenShell(Action):
    
    def execute(self):
        super(OpenShell, self).execute(func=core.open_shell,
            args=[self.project_directory,])
        

class HomePage(Page):

    def title(self):
        return "Basil Project Manager"

    def head(self):
        head = """<link rel="stylesheet" href="css/jquery-ui.min.css">"""
        head += super(HomePage, self).head() # we want main.css to override other css
        head += """
        <script type="text/javascript" src="js/jquery-ui.min.js"></script>
        <script type="text/javascript" src="js/basil.js"></script>
        """
        return head

    def body(self):
        template_infos = core.get_templates()
        options = []
        for template_info in template_infos:
            options.append("""<option value="{}" data-title="{}"
            data-description="{}">{}</option>""".format(template_info.name,
            template_info.title, template_info.description,
            template_info.title))
        options_html = "\n".join(options)
        html = """
        <h1>Basil projects</h1>
        <h2>Make a new project</h2>
        <p class="instructions">Choose a template to base your new
            project on.</p>
        <div id="templates-form">
        <form action="/get-values" method="POST">
        <span class="fld-lbl">Available templates:</span>
        <select name="{template_dropdown}" class="dropdown"
            id="templates-dropdown">
        {options}
        </select>
        <input id="apply-button" type="submit" value="APPLY">
        </form>
        </div>
        <p id="template-description"></p>
        <h2>Manage existing projects</h2>
        <div id="project-statuses">
        <p id="loading-projects" class=\"instructions\">
        Loading projects status details ...</p>
        </div>
        <div id="dialog" title="Destroy Project" style="display: none;">
        </div>""".format(template_dropdown=keys.TEMPLATE, options=options_html)
        return html


class CreateProject(Page):

    def title(self):
        return 'Project being built ...'

    def body(self):
        postvars = self.get_postvars()
        template_name = postvars[keys.TEMPLATE][0]
        if template_name != "basil_django":
            return """
        <h1>Coming soon - not implemented yet</h1>
        <p class="instructions">
        Support for <span class="project-name">{}</span> template coming soon. Sorry! 
        <a href="/" title="Back to home page">Back</a>
        </p>
        """.format(template_name)
        project_name = postvars[keys.PROJECT_NAME][0]
        project_directory = join(projects_dir, project_name)
        values = {key: val[0] for key, val in postvars.items()
            if key != keys.TEMPLATE}
        try:
            core.create(template_name, values)
        except Exception as e:
            return ("Was unable to create \"{}\" project.<br>"
                "Original error: {}".format(project_name, e))
        try:
            core.start_project(project_directory)
        except Exception as e:
            return ("\"{}\" project successfully created but was unable to "
                "start it.<br>Original error: {}".format(project_name, e))
        try:
            core.view_project(project_directory)
        except Exception as e:
            return ("\"{}\" project successfully created and started but was "
                "unable to view it.<br>Original error: {}".format(project_name,
                e))
        # assumes the port we want has been tagged "webserver_port" - @Later make a proper requirement
        project_config = core.project_load_config(project_name)
        port2open = project_config[keys.PROJECT_PORTS].get(
            keys.TEMPLATE_CONFIG_WEBSERVER_PORT, 8888)
        return """
            <h1>Success!</h1>

            <p class="instructions">Your "{project_name}" project was
            successfully built.</p>

            <p>Click <a target='_blank' href='http://localhost:{port2open}/'>
            open {project_name}</a> and see feedback from your project.</p>
            """.format(project_name=project_name, port2open=port2open)


class GetValues(Page):

    def title(self):
        return 'Configure Project'

    def get_template_name(self):
        postvars = self.get_postvars()
        try:
            template_name = postvars.get(keys.TEMPLATE)[0]
        except Exception as e:
            template_name = None
        return template_name

    def body(self):
        template_name = self.get_template_name()
        if not template_name:
            body_html = ("Oops! Unable to identify template to build project "
                "from.")
        else:
            fields = core.get_fields(template_name)
            form_bits = ["""<form id="settings-form" action="create-project"
            method="POST">"""]
            for field in fields:
                form_bits.append("""
                <span class="fld-lbl">{lbl}:</span>
                <input class="txt-input" type="text" name="{name}" id="{name}"
                value="{default}" title="{desc}">
                """.format(desc=field.description, lbl=field.title,
                name=field.name, default=field.default))
            form_bits.append("""<input type="hidden" name="{}" value="{}">"""
                .format(keys.TEMPLATE, template_name))
            form_bits.append("""<span id="time-warning">Note: building your
            project and applying the configuration may take anything from a few
            minutes to 20 minutes. It depends on whether you already have a
            particular (vagrant) file downloaded already or not.</span>
            <input id="apply-template" class="submit" type="submit"
            value="APPLY">
            </form>""")
            form_html = "\n".join(form_bits)
            body_html = """
            <h1>Configure your project</h1>
            <p class="instructions">Configure your <span class='tpl-name'>
            {template_name}</span> project by answering the following
            questions:</p>
            {form_html}
            <script type='text/javascript'>
            $("#project_name").focus();
            </script>""".format(template_name=template_name,
            form_html=form_html)
        return body_html


class NotFoundPage(Page):

    def __init__(self, handler):
        super(NotFoundPage, self).__init__(handler)
        self.response = 404

    def title(self):
        return 'Basil - Page not found'

    def body(self):
        return 'Sorry, page does not exist.'


class Asset(object):

    def __init__(self, handler):
        self.handler = handler

    def execute(self):
        """
        Note - by sending a response and ending the header we don't break
        HTTPServer.
        """
        try:
            unused, ext = os.path.splitext(self.handler.path)
            if ext in (".js", ".css", ".png"):
                ctype = types_map[ext]
                curdir = os.path.split(core.__file__)[0]
                resource_path = os.path.join(curdir, self.handler.path.strip("/"))
                #print("resource_path: {}".format(resource_path))
                text = (ext in (".js", ".css"))
                mode = "rt" if text else "rb"
                with open(resource_path, mode) as f:
                    self.handler.send_response(200)
                    self.handler.send_header('Content-type', ctype)
                    self.handler.end_headers()
                    asset_content = f.read()
                    if text:
                        asset_content = asset_content.encode("utf-8")
                    self.handler.wfile.write(asset_content)
        except IOError:
            self.handler.send_error(404)


class BasilManagerHandler(http.server.BaseHTTPRequestHandler):

    def __init__(self, request, client_address, server):
        # More specific urls should be toward the top.
        self.urls = [
            (r'images/|css/|js/', {'GET': Asset,}),
            (r'create-project', {'POST': CreateProject,}),
            (r'get-values', {'POST': GetValues,}),
            (r'get-statuses', {'GET': GetStatuses,}),
            (r'project-start', {'POST': ProjectStart,}),
            (r'project-stop', {'POST': ProjectStop,}),
            (r'project-destroy', {'POST': ProjectDestroy,}),
            (r'open-code', {'POST': OpenCode,}),
            (r'open-shell', {'POST': OpenShell,}),
            (r'', {'GET': HomePage,}),
        ]
        super(BasilManagerHandler, self).__init__(
            request, client_address, server)

    def do_METHOD(self, method):
        path = self.path.strip('/')
        for url, methods in self.urls:
            if re.match(url, path):
                pageClass = methods.get(method)
                #print("Using class {} for {}".format(pageClass, path))
                if pageClass:
                    break
        else:
            pageClass = NotFoundPage
        page = pageClass(self)
        page.execute()

    def do_GET(self):
        self.do_METHOD('GET')

    def do_POST(self):
        self.do_METHOD('POST')


def run_server():
    port = 8000
    httpd = None
    while not httpd:
        try:
            httpd = http.server.HTTPServer(('', port), BasilManagerHandler)
        except:
            port += 1
    print("Basil server running on port: {}".format(port))
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()
