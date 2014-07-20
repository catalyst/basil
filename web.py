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

basil_config_file = 'basil.json'


class Page(object):

    def __init__(self, handler):
        self.handler = handler
        self.response = 200
        self.headers = {
            'Content-type': 'text/html'
        }

    def title(self):
        return 'Basil'

    def head(self):
        return """
        <link rel="stylesheet" href="css/main.css">
        <script type="text/javascript" src="js/jquery.min.js"></script>
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
            <a href="\" title="Home page">
                <image id="basil-logo" src="images/basil_logo2.png">
            </a>
            {body}
          </body>
        </html>
        """.format(title=self.title(), head = self.head(), body=self.body())
        return content.encode('utf-8')

    def get_postvars(self):
        """
        Returns dict of where vals are lists (usually of just one item).
        """
        ctype, unused = cgi.parse_header(self.handler.headers.get('content-type'))
        if ctype != 'application/x-www-form-urlencoded':
            raise Exception("Unexpected content type.")
        length = int(self.handler.headers.get('content-length'))
        b_postvars = urllib.parse.parse_qs(self.handler.rfile.read(length),
            keep_blank_values=1)
        postvars = {str(key, "utf-8"): [str(x, "utf-8") for x in val_list]
            for key, val_list in b_postvars.items()}
        return postvars

    def execute(self):
        self.handler.send_response(self.response)
        for key, value in iter(self.headers.items()):
            self.handler.send_header(key, value)
        self.handler.end_headers()
        self.handler.wfile.write(self.render())


class Asset(object):

    def __init__(self, handler):
        self.handler = handler

    def execute(self):
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
            

class HomePage(Page):

    def __init__(self, handler):
        super(HomePage, self).__init__(handler)

    def title(self):
        return 'Basil - Instance Manager'

    def body(self):
        template_infos = core.get_templates()
        options = []
        descs = []
        for template_info in template_infos:
            options.append("""<option value="{}">{}</option>"""
                .format(template_info.name, template_info.title))
            descs.append("""
            case "{name}":
                desc = "{desc}";
                template_title = "{title}";
                break;
            """.format(name=template_info.name, desc=template_info.description,
            title=template_info.title))
        options_html = "\n".join(options)
        template2desc_html = "\n".join(descs)
        project_statuses = core.get_project_statuses()
        project_bits = []
        if project_statuses:
            project_bits.append("""<table>
        <thead>
        <tr><th>Project</th><th>Status</th><th>Actions</th></tr>
        </thead>
        <tbody>
        """)
            buttons_html = """
            <input type="button" value="Open"
                onclick="alert('Open not implemented yet ...')">
            <input type="button" value="Close"
                onclick="alert('Close not implemented yet ...')">
            <input type="button" value="Destroy"
                onclick="alert('Destroy not implemented yet ...')">
            """
        for project_status in project_statuses:
            project_bits.append("""<tr><td class="project-cell">{}</td>
                <td><strong>{}</strong> - {}</td>
                <td>{}</td>
                </tr>""".format(project_status.project_name,
                project_status.state.replace("_", " ").title(),
                project_status.state_human_long, buttons_html))
        if project_statuses:
            project_bits.append("""</tbody>
            </table>""")
        projects_html = ("\n".join(project_bits) if project_statuses
            else "<p class=\"instructions\">No projects to manage yet.</p>")
        html = """
        <h1>Basil projects</h1>
        <h2>Make a new project</h2>
        <p class="instructions">Choose a template to base your new project on.</p>
        <div id="templates-form">
        <form action="/get-values" method="POST">
        <span class="fld-lbl">Available templates:</span>
        <select name="{template_dropdown}" class="dropdown" id="templates-dropdown" on_>
        {options}
        </select>
        <input id="apply-button" type="submit" value="APPLY">
        </form>
        </div>
        <p id="template-description"></p>
        <h2>Manage existing projects</h2>
        {projects}
        <script type='text/javascript'>
            jQuery(document).ready(function($){{
                $(function(){{
                    $("#templates-dropdown").trigger('change');
                }});
                $("#templates-dropdown").change(function(){{
                    var val = $(this).val();
                    var desc = undefined;
                    var template_title = undefined;
                    switch(val){{
                        {template2desc}
                    }}
                    $("#template-description").text(template_title
                        + ": " + desc);
                }});
            }});
        </script>
        """.format(template_dropdown=keys.TEMPLATE, options=options_html,
            projects=projects_html, template2desc=template2desc_html)
        return html


class CreateProject(Page):

    def __init__(self, handler):
        super(CreateProject, self).__init__(handler)

    def title(self):
        return 'Project being built ...'

    def body(self):
        postvars = self.get_postvars()
        template_name = postvars[keys.TEMPLATE][0]
        project_name = postvars[keys.PROJECT_NAME][0]
        values = {key: val[0] for key, val in postvars.items()
            if key != keys.TEMPLATE}
        try:
            core.create(template_name, values)
            body_html = """
            <h1>Success!</h1>

            <p class="instructions">Your "{project_name}" project was successfully built.</p>

            <p>Click <a target='_blank' href='http://localhost:8888/'>
            open {project_name}</a> and see feedback from your project.</p>

            """.format(project_name=project_name)
        except Exception as e:
            body_html = ("Was unable to build project.<br>Original error: {}"
                .format(e))
        return body_html


class GetValues(Page):

    def __init__(self, handler):
        super(GetValues, self).__init__(handler)

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


class BasilManagerHandler(http.server.BaseHTTPRequestHandler):

    def __init__(self, request, client_address, server):
        # More specific urls should be toward the top.
        self.urls = [
            (r'images/|css/|js/', {'GET': Asset,}),
            (r'create-project', {'POST': CreateProject,}),
            (r'get-values', {'POST': GetValues,}),
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
    print('Basil server running on port: {}'.format(port))
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()
