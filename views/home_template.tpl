<html>
    <head>
        <meta charset="UTF-8">
        <title>{{title}}</title>
        <link rel="icon" href="static/images/favicon.png">
        <link rel="stylesheet" href="static/css/jquery-ui.min.css">
        <link rel="stylesheet" href="static/css/main.css">
        <script type="text/javascript" src="static/js/jquery.min.js"></script>
        <script type="text/javascript" src="static/js/underscore-min.js"></script>
        <script type="text/javascript" src="static/js/jquery-ui.min.js"></script>
        <script type="text/javascript" src="static/js/basil.js"></script>
        <script type="text/javascript" src="static/js/home.js"></script>
    </head>
    <body>
        <a href="/" title="Home page">
            <image id="basil-logo" src="static/images/basil_logo.png">
        </a>
        <h1>Basil projects</h1>
        <h2>Make a new project</h2>
        <p class="instructions">Choose a template to base your new
            project on.</p>
        <div id="templates-form">
            <form action="/get-values" method="POST">
                <span class="fld-lbl">Available templates:</span>
                <select name="{{template_dropdown}}" class="dropdown"
                    id="templates-dropdown">
                    %for template_info in template_infos:
                        <option value="{{template_info.name}}"
                            data-title="{{template_info.title}}"
                            data-description="{{template_info.description}}">
                                {{template_info.title}}
                        </option>
                    %end
                </select>
                <input id="apply-button" value="CREATE" type=button>
            </form>
        </div>
        <p id="template-description"></p>
        <h2>Manage existing projects</h2>
        <div id="progress"></div>
        <div id="project-statuses">
        <p id="loading-projects" class=\"instructions\">
        Loading projects status details ...</p>
        </div>
        <div id="gen-dialog" title="General dialog" style="display: none;"></div>
    </body>
</html>
