/*
Basil: Build A System Instant-Like
Copyright (C) 2014 Catalyst IT Ltd

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
*/

function make_el(el_type, classes, fn_or_val){
    /*
    Make an html element e.g. select, option. Apply classes to element.
    Provide the element with a value or otherwise modify the element e.g
    create child elements. If a nested element, will be supplying another
    make_el as the fn_or_val. Not all functions are for making sub-elements -
    may also be altering the element in some other way.

    el_type -- e.g. select, option.

    classes -- classes to apply to element (if supplied).

    fn_or_val -- value or function to, for example, create sub-elements or
    alter element.
    */
    var el = document.createElement(el_type);
    if (!classes){
        classes = [];
    }
    try{
        classes.forEach(function(myclass){
            $(el).addClass(myclass);
        });
    }catch(ex){
        console.log('make_el', 'exception when trying to add classes to element: '
            + classes);
    }
    if(typeof(fn_or_val) === 'function'){
        var mod_el_fn = fn_or_val;
        try{
            mod_el_fn(el);
        }catch(ex){
            console.log('make_el', 'exception while applying function to '
                + el_type, ex);
        }
    } else {
        var el_val = fn_or_val;
        try{
            $(el).text(el_val);
        }catch(ex){
            console.log('make_el', 'exception while setting value of ' + el_val
                + ' for ' + el_type, ex);
        }
    };
    return el;
};

// http://stackoverflow.com/questions/1184624/convert-form-data-to-js-object-with-jquery
$.fn.serializeObject = function()
{
    var o = {};
    var a = this.serializeArray();
    $.each(a, function() {
        if (o[this.name] !== undefined) {
            if (!o[this.name].push) {
                o[this.name] = [o[this.name]];
            }
            o[this.name].push(this.value || '');
        } else {
            o[this.name] = this.value || '';
        }
    });
    return o;
};

function starts_with(str, startstr){
    return str.lastIndexOf(startstr, 0) === 0;
}

function setup_template_form(){
    $(function(){
        $("#templates-dropdown").trigger('change');
    });
    $("#templates-dropdown").change(function(){
        var template_name = $(this).val();
        var option = $(this).find("option[value='" + template_name + "']");
        var template_title = option.attr("data-title");
        var template_description = option.attr("data-description");
        $("#template-description").html(template_title
            + ": " + template_description);
    });
    $("#apply-button").attr({
        "title": "Create project based on template"}
    ).click(function(){
        open_create_project();
    });
}

function create_project(){
    // Clear errors.
    $('#create-form input, #create-form label').removeClass('error');
    $('#create-form .errors').html('');

    var template_name = $("#templates-dropdown").find('option:selected').val();
    var create_data = $("#create-form").serializeObject();
    create_data["template_name"] = template_name;
    $.ajax({type: "POST",
            url: "create-project",
            dataType: "json",
            data: create_data
        })
        .done(function(response){
            ok_dialog("Success", "Successfully made \""
                + create_data.project_name + "\"");
            get_project_statuses();
        })
        .fail(function(jqXHR, textStatus, errorThrown){
            // sort errors so Project Name first, then rest by title
            // so separate out error extraction from sorting from creating list items
            var result = JSON.parse(jqXHR.responseText);
            var project_name_errors = [];
            var other_field_errors = [];
            var other_errors = [];
            if (typeof result === 'object') {
                // If the error response is an object, then it is a mapping of
                // fields to error messages.
                var errors = result;
                for (var field in errors) {
                    if (errors.hasOwnProperty(field)) {
                        // Add error classes to the field.
                        $('#create-form input#' + field).addClass('error');
                        $('#create-form label[for=' + field + ']').addClass('error');
                        // Add an error message to the list of errors.
                        var label = $('#create-form label[for=' + field + ']').text();
                        var field_error = label + ' ' + errors[field];
                        if (starts_with(label, "Project name")){
                            project_name_errors.push(field_error);
                        } else {
                            other_field_errors.push(field_error);
                        }
                    }
                }
            }
            else {
                // If result is not an object, then it is simply an error
                // message to add to the list of errors.
                other_errors.push(result);
            }
            // Sort field_errors.
            other_field_errors.sort();
            var field_errors = project_name_errors.concat(other_field_errors);
            _.each(field_errors, function(field_error){
                $('#create-form .errors').append(make_el('li', [], function(li) {
                    $(li).text(field_error);
                }));
            })
            _.each(other_errors, function(other_error){
                $('#create-form .errors').append(make_el('li', [], function(li) {
                    $(li).text(other_error);
                }));
            })
        });
};

function build_create_dialog(template_name, response){
    /*
    TODO - handle validation side of things from user point of view and stopping submission of faulty data
    (client side is enough - the user can feel free to destroy their own system through hacking ;-))
    */
    dialog_div = $("#gen-dialog");
    dialog_div.html(""); // clear it first
    var i = 0;
    dialog_div.append(make_el("form", [], function(form){
        $(form).attr("id", "create-form");
    }));
    var form = $("#create-form");
    form.append(make_el("p", ["instructions"], function(p){
        $(p).html("Configure your <span class='tpl-name'>" + template_name
            + "</span> project by answering the following questions:");
    }));
    form.append(make_el("ul", ["errors"], function(ul){
        $(ul).html("");
    }));
    fieldnames = [];
    for (var fieldname in response){ // see https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/for...in
        if (response.hasOwnProperty(fieldname) && (fieldname != "project_name")) {
            fieldnames.push(fieldname);
        }
    };
    fieldnames.sort();
    fieldnames.unshift("project_name");
    //console.log(fieldnames);
    _.each(fieldnames, function(fieldname){ // see https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/for...in
        var field_det = response[fieldname];
        var title = field_det.title;
        var description = field_det.description;
        var type = field_det.type;
        var field_default = field_det.default;
        var validators = field_det.validators; // TODO wire up front-end validation - see http://jqueryui.com/dialog/#modal-form
        form.append(make_el("label", ["dialog-label"], function(label){
            $(label).text(title + ":");
            $(label).attr("for", fieldname)
        }));
        form.append(make_el("input", ['dialog-input', 'text', 'ui-widget-content', 'ui-corner-all'], function(text){
            $(text).attr({"id": fieldname, "name": fieldname, "value": field_default}) // must define name so serialize will work
        }));
    });
    form.append(make_el("span", [], function(time_span){
        $(time_span).text("Note: building your project and applying the configuration "
            + "may take anything from a few minutes to 20 minutes. It depends on "
            + "whether you already have a particular (vagrant) file downloaded "
            + "already or not.");
        $(time_span).attr("id", "time-warning");
    }));
    dialog_div.dialog({
        title: "Create Project",
        autoOpen: false,
        height: "auto",
        width: 450,
        modal: true,
        dialogClass: "no-close",
        buttons: {
            "Create project": create_project,
            Cancel: function() {
                dialog_div.dialog("close");
        }
    },
    close: function() {
            form.remove();
        }
    });
    return dialog_div;
};

function open_create_project(){
    var template_name = $("#templates-dropdown").find('option:selected').val();
    $.ajax({type: "GET",
            url: "get-fields",
            dataType: "json",
            data: {"template_name": template_name}
        })
        .done(function(response){
            dialog_div = build_create_dialog(template_name, response);
            dialog_div.dialog("open");
        })
        .fail(function(jqXHR, error, ex){
            var title = "Problem getting field details for template";
            var msg = "Problem getting field details for \"" + template_name
                + "\" template.<br><br>" + ex;
            ok_dialog(title, msg);
        });
};

function project_action(project_directory, project_name, url,
        action_lbl_do, action_lbl_doing, success_handler, fail_handler){
    /*
    The success and fail handlers may themselves be AJAX so we had best
    leave switching the hourglass off to them in all cases.
    */
    $("body").css("cursor", "progress");
    $.ajax({type: "POST",
            url: url,
            dataType: "json",
            data: {
                "project_directory": project_directory
            }
        })
        .done(function(response){
            if(success_handler){
                success_handler();
            }
        })
        .fail(function(jqXHR, error, ex){
            if(success_handler){
                fail_handler();
            };
            var title = "Problem " + action_lbl_doing + " \"" + project_name
                + "\"";
            var msg = "Unable to " + action_lbl_do + " \"" + project_name
                + "\" project.<br><br>" + ex;
            ok_dialog(title, msg);
        });
};

function update_details(html){
    $("#progress-details").html(html
        ).scrollTop(100000000000000000);
};

function cleanup_progress(){
    $("#progress").slideUp(600, "swing",
        function(){
            setTimeout(
                function(){
                    $("#progress").html("");
                    $("#progress").show();
                },
                500);
    });
}

function show_progress(project_name, n_expected_msgs, action_lbl_doing,
        action_lbl_doing_cap, callback){
    $("#progress").html(
        "<p id='progress-heading'>Progress " + action_lbl_doing + " "
        + project_name + "</p>"
        + "<div id='progress-bar'></div>"
        + "<div id='progress-summary'>" + action_lbl_doing_cap + " ...</div>"
        + "<div id='details-block'>"
            + "<img id='details-arrow' src='static/images/show_arrow.png'>"
            + "<div id='details-lbl'>Details</div>"
            + "<div class='clear-both'></div>"
        + "</div>"
        + "<div id='progress-details'>Waiting for progress details ...</div>");
    $("#progress-bar").progressbar({value: 0});
    $("#progress-details").hide();
    var show = true;
    $("#details-arrow").click(function(){
        if(show){
            $("#progress-details").show();
            $("#details-arrow").attr("src", "static/images/hide_arrow.png");
        } else {
            $("#progress-details").hide();
            $("#details-arrow").attr("src", "static/images/show_arrow.png");
        }
        show = !show;
    });    /* poll recursively with pauses at client end. Warning - alternative approach
    of instant recursion at client prevented Chromium from updating the DOM till
    function returned (even though server added pauses).*/
    var prev_response_str = "";
    var command_progress_states = {
        ACTIVE: 1,
        FINISHED: 2,
        ERROR: 3,
    }
    function command_end() {
        // handle cleanup e.g. remove progress bar
        $("#progress-bar").progressbar({value: 100});
        setTimeout(cleanup_progress, 2000);
        if (callback){
            callback();
        };
    }
    function get_progress() {
        $.ajax({type: "GET",
                dataType: "json",
                async: false,
                url: "get-command-progress"
            })
            .done(function(response){
                //console.log(response);
                if(response == ""){
                    var response_str = response;
                } else {
                    var response_str = JSON.stringify(response);
                    if (response.state == command_progress_states.FINISHED) {
                        $("#progress-summary").text("Finished");
                        command_end();
                    }
                    else if (response.state == command_progress_states.ERROR) {
                        var msg = "Error occurred: "
                            + response.error.replace(/(\r\n|\n|\r)/gm, "<br>");
                        var error_len = 120;
                        if (msg.length > error_len){
                            var error2display = msg.substring(0, error_len) + " ...";
                        } else {
                            var error2display = msg;
                        }
                        $("#progress-summary").text(error2display);
                        update_details(msg);
                        command_end();
                        var title = "Problem " + action_lbl_doing + " "
                            + project_name;
                        ok_dialog(title, msg);
                    }
                    else {
                        //display progress e.g. messages (if change)
                        var changed = (prev_response_str != response_str);
                        if(changed){ // hammer the html refreshing less
                            //console.log("Changed");
                            prev_response_str = response_str;
                            var percent = (response.progress*100)/n_expected_msgs;
                            $("#progress-bar").progressbar({value: percent});
                            $("#progress-summary").text(response.summary);
                            if(response.details != ""){
                                update_details(response.details.replace(/(\r\n|\n|\r)/gm, "<br>"));
                            };
                        };
                        setTimeout(get_progress, 500);
                    };
                }
            })
            .fail(function(jqXHR, error, ex){
                var title = "Problem " + action_lbl_doing + " "
                    + project_name;
                var msg = "Original error: " + ex;
                ok_dialog(title, msg);
            });
    };
    get_progress();
}

function project_start(project_directory, project_name){
    project_action(project_directory, project_name,
        "project-start", "start", "starting");
    function update(){
        get_project_statuses();
        enable_all_btns();
    };
    show_progress(project_name, 25, "starting", "Starting", update);
};

function project_stop(project_directory, project_name){
    project_action(project_directory, project_name,
        "project-stop", "stop", "stopping",
        get_project_statuses, enable_all_btns);
};

function project_reset(project_directory, project_name){
    project_action(project_directory, project_name,
        "project-reset", "reset", "resetting",
        get_project_statuses, enable_all_btns);
    show_progress(project_name, 10, "resetting", "Resetting");
};

function confirm_destroy(project_directory, project_name) {
    var dialog_div = $("#gen-dialog");
    dialog_div.html("<p>Destroying your project is irreversible. "
        + "Do you really want to destroy it?</p>");
    dialog_div.dialog({
        title: "Destroy " + project_name + " project?",
        autoOpen: false,
        width: 400,
        modal: true,
        dialogClass: "no-close",
        buttons: [
	        {
		        text: "Oops - No",
		        click: function() {
			        $( this ).dialog("close");
                    enable_all_btns();
		        }
	        },
	        {
		        text: "Yes - Destroy!",
		        click: function() {
			        $( this ).dialog("close");
                    project_action(project_directory, project_name,
                        "project-destroy", "destroy", "destroying",
                        get_project_statuses, enable_all_btns)
		        }
	        }
        ]
    });
    dialog_div.dialog("open");
};

function project_destroy(project_directory, project_name){
    confirm_destroy(project_directory, project_name);
};

function ok_dialog(title, msg){
    var dialog_div = $("#gen-dialog");
    dialog_div.html("<p>" + msg + "</p>");
    if (msg.length < 200){
        var width = 400;
        var height = 200;
    } else {
        var width = 700;
        var height = "auto";
    };
    dialog_div.dialog({
        title: title,
        autoOpen: false,
        width: width,
        height: height,
        modal: true,
        dialogClass: "no-close",
        buttons: [
	        {
		        text: "OK",
		        click: function() {
			        $( this ).dialog("close");
			        dialog_div.html("");
		        }
	        }
        ]
    });
    dialog_div.dialog("open");
};

function disable_all_btns(){
    $("input.action_button[type=button]").attr("disabled", "disabled");
};

function enable_all_btns(){
    /* As a common success/fail handler good to guarantee hourglass off */
    $("input.action_button[type=button]").removeAttr("disabled");
    $("body").css("cursor", "default");
};

function open_code(project_directory){
    $.ajax({type: "POST",
            url: "open-code",
            data: {
                "project_directory": project_directory
            }
        })
        .fail(function(jqXHR, error, ex){
            alert(ex);
        });
};

function open_shell(project_directory){
    $.ajax({type: "POST",
            url: "open-shell",
            data: {
                "project_directory": project_directory
            }
        })
        .fail(function(jqXHR, error, ex){
            alert(ex);
        });
};

function add_std_button(td, id, classes, value, action_func, status){
    $(td).append(make_el("input", classes, function(btn){
        $(btn).attr({"id": "btn_" + id,
            "name": "btn_" + id,
            "type": "button",
            "value": value});
        $(btn).click(function(){
            disable_all_btns();
            action_func(status["project_directory"],
                status["project_name"]);
        });
    }));
};

function display_project_statuses(response){
    $("#loading-projects").text("");
    $("#project-statuses > table").remove();
    var projs = $("#project-statuses");
    projs.append(make_el("table", [], function(table){
        $(table).append(make_el("thead", [], function(thead){
             $(thead).append(make_el("tr", [], function(tr){
                $(tr).append(make_el("th", [], function(th){
                    $(th).text("Project");
                }));
                $(tr).append(make_el("th", [], function(th){
                    $(th).text("Status");
                }));
                $(tr).append(make_el("th", [], function(th){
                    $(th).text("Actions");
                }));
            }));
        }));
        $(table).append(make_el("tbody", [], function(tbody){
             var id = 0;
             _.each(response, function(status){
                //console.log(status);
                $(tbody).append(make_el("tr", [], function(tr){
                    $(tr).append(make_el("td", ["projs-col"], function(td){
                        $(td).html("<span class='project-name'>"
                            + status["project_name"]
                            + "</span><br><span class='project-template'>"
                            + "(from " + status["template_name"] + " "
                            + status["template_version"] + ")</span>");
                    }));
                    $(tr).append(make_el("td", ["status-col"], function(td){
                        $(td).html("<strong>" + status["project_state"]
                            + "</strong> - " + status["project_state_msg"]);
                    }))
                    $(tr).append(make_el("td", ["actions-col"], function(td){
                        switch(status["project_state"]){
                            case "unknown":
                                break;
                            case "Not Created":
                            case "Aborted":
                            case "Poweroff":
                                // Start, Destroy
                                id++;
                                add_std_button(td, id, ["action_button"], "Start",
                                    project_start, status);
                                if (status["allow_destroy"]){
                                    id++;
                                    add_std_button(td, id, ["float-right", "action_button"],
                                        "Destroy", project_destroy, status);
                                }
                                break;
                            case "Running":
                                // View, Code, Command, Stop, Reset, Destroy
                                $(td).append(make_el("input", ["action_button"], function(btn){
                                    $(btn).attr({
                                        "id": "btn_" + ++id,
                                        "name": "btn_" + id,
                                        "type": "button",
                                        "value": "View"}
                                    );
                                    var view_url = "'http://localhost:"
                                        + status["webserver_port"] + "'";
                                    var view_cmd = "window.open(" + view_url + ")";
                                    $(btn).attr({
                                        "onClick": view_cmd,
                                        "title": "Open \"" + status["project_name"]
                                            + "\" (on " + view_url + ")"}
                                    );
                                }));
                                $(td).append(make_el("input", ["action_button"], function(btn){
                                    $(btn).attr({
                                        "id": "btn_" + ++id,
                                        "name": "btn_" + id,
                                        "type": "button",
                                        "value": "Code"}
                                    ).click(function(){
                                        open_code(status["project_directory"]);
                                    });
                                }));
                                $(td).append(make_el("input", ["action_button"], function(btn){
                                    $(btn).attr({
                                        "id": "btn_" + ++id,
                                        "name": "btn_" + id,
                                        "type": "button",
                                        "value": "Run Command"}
                                    ).click(function(){
                                        open_shell(status["project_directory"]);
                                    });
                                }));
                                id++;
                                add_std_button(td, id, ["action_button"], "Stop", project_stop,
                                    status);
                                if (status["allow_destroy"]){
                                    id++;
                                    add_std_button(td, id, ["float-right", "action_button"],
                                        "Destroy", project_destroy, status);
                                }
                                id++;
                                add_std_button(td, id, ["float-right", "action_button"],
                                    "Reset", project_reset, status);
                                break;
                         };
                    }));
                }));
            });
        }));
    }));
};

function get_project_statuses(){
    /*
    Can't accept arguments - otherwise messes up setInterval.
    */
    $("body").css("cursor", "progress");
    $.ajax({type: "GET",
        url: "get-statuses",
        dataType: "json"})
        .done(function(response){
            if(response != ""){
                display_project_statuses(response);
                $("body").css("cursor", "default");
            } else {
                $("#loading-projects").text("You don't have any projects yet.");
                $("#project-statuses > table").remove();
                $("body").css("cursor", "default");
            };
        })
        .fail(function(jqXHR, textStatus, errorThrown){
            ok_dialog("Problem with project data",
                "Unable to access project status data. Original problem: "
                + jqXHR.responseText);
            $("#loading-projects").text("Problem accessing projects information. "
                + jqXHR.responseText);
        });
};
