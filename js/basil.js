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

function project_action(project_directory, project_name, url,
        action_lbl_do, action_lbl_doing, success_handler, fail_handler){
    /*
    The success and fail handlers may themselves be AJAX so we had best
    leave switching the hourglass off to them in all cases.
    */
    $("body").css("cursor", "progress");
    $.ajax({type: "POST",
            url: url,
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

function project_start(project_directory, project_name){
    project_action(project_directory, project_name,
        "project-start", "start", "starting");
    $("#progress").html(
        "<p id='progress-heading'>Progress starting " + project_name + "</p>"
        + "<div id='progress-bar'></div>"
        + "<div id='progress-summary'>Starting ...</div>"
        + "<div id='details-block'>"
            + "<img id='details-arrow' src='images/show_arrow.png'>"
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
            $("#details-arrow").attr("src", "images/hide_arrow.png");
        } else {
            $("#progress-details").hide();
            $("#details-arrow").attr("src", "images/show_arrow.png");
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
        get_project_statuses();
        enable_all_btns();
    }
    function get_progress() {
        $.ajax({type: "GET",
                async: false,
                url: "get-command-progress"
            })
            .done(function(response){
                //console.log(response);
                var response_str = JSON.stringify(response);
                if (response != ""){
                    if (response.state == command_progress_states.FINISHED) {
                        $("#progress-summary").text("Finished");
                        command_end();
                    }
                    else if (response.state == command_progress_states.ERROR) {
                        $("#progress-summary").text("Error");
                        command_end();
                        alert("Error occurred: " + command_progress.error);
                    }
                    else {
                        //display progress e.g. messages (if change)
                        var changed = (prev_response_str != response_str);
                        if(changed){ // hammer the html refreshing less
                            //console.log("Changed");
                            prev_response_str = response_str;
                            var n_expected_msgs = 20;
                            var percent = (response.progress*100)/n_expected_msgs;
                            $("#progress-bar").progressbar({value: percent});
                            $("#progress-summary").text(response.summary);
                            if(response.details != ""){
                                $("#progress-details").html(
                                    response.details.replace(/(\r\n|\n|\r)/gm, "<br>")
                                );
                                $("#progress-details").scrollTop(100000000000000000);
                            };
                        };
                        setTimeout(get_progress, 500);
                    };
                }
            })
            .fail(function(jqXHR, error, ex){
                var title = "Problem getting progress details";
                var msg = "Original error: " + ex;
                ok_dialog(title, msg);
            });
    };
    get_progress();
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

function project_stop(project_directory, project_name){
    project_action(project_directory, project_name,
        "project-stop", "stop", "stopping",
        get_project_statuses, enable_all_btns);
};

function confirm_destroy(project_directory, project_name) {
    $("#dialog").html("<p>Destroying your project is irreversible. "
        + "Do you really want to destroy it?</p>");
    $("#dialog").dialog({
        title: "Destroy " + project_name + " project?",
        autoOpen: false,
        width: 400,
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
    $("#dialog").dialog("open");
};

function project_destroy(project_directory, project_name){
    confirm_destroy(project_directory, project_name);
};

function ok_dialog(title, msg){
    $("#dialog").html("<p>" + msg + "</p>");
    $("#dialog").dialog({
        title: title,
        autoOpen: false,
        width: 400,
        dialogClass: "no-close",
        buttons: [
	        {
		        text: "OK",
		        click: function() {
			        $( this ).dialog("close");
		        }
	        }
        ]
    });
    $("#dialog").dialog("open");
};

function disable_all_btns(){
    $("input[type=button]").attr("disabled", "disabled");
};

function enable_all_btns(){
    /* As a common success/fail handler good to guarantee hourglass off */
    $("input[type=button]").removeAttr("disabled");
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
        $(btn).attr("id", "btn_" + id);
        $(btn).attr("name", "btn_" + id);
        $(btn).attr("type", "button");
        $(btn).attr("value", value);
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
                    }));
                    $(tr).append(make_el("td", ["actions-col"], function(td){
                        switch(status["project_state"]){
                            case "Not Created":
                            case "Aborted":
                            case "Poweroff":
                                // Start, Destroy
                                id++;
                                add_std_button(td, id, [], "Start",
                                    project_start, status);
                                id++;
                                add_std_button(td, id, ["float-right"],
                                    "Destroy", project_destroy, status);
                                break;
                            case "Running":
                                // View, Code, Command, Stop, Destroy
                                $(td).append(make_el("input", [], function(btn){
                                    $(btn).attr("id", "btn_" + ++id);
                                    $(btn).attr("name", "btn_" + id);
                                    $(btn).attr("type", "button");
                                    $(btn).attr("value", "View");
                                    var view_url = "'http://localhost:"
                                        + status["webserver_port"] + "'";
                                    var view_cmd = "window.open(" + view_url + ")";
                                    $(btn).attr("onClick", view_cmd);
                                    $(btn).attr("title", "Open \""
                                        + status["project_name"] + "\" (on "
                                        + view_url + ")");
                                }));
                                $(td).append(make_el("input", [], function(btn){
                                    $(btn).attr("id", "btn_" + ++id);
                                    $(btn).attr("name", "btn_" + id);
                                    $(btn).attr("type", "button");
                                    $(btn).attr("value", "Code");
                                    $(btn).click(function(){
                                        open_code(status["project_directory"]);
                                    });
                                }));
                                $(td).append(make_el("input", [], function(btn){
                                    $(btn).attr("id", "btn_" + ++id);
                                    $(btn).attr("name", "btn_" + id);
                                    $(btn).attr("type", "button");
                                    $(btn).attr("value", "Run Command");
                                    $(btn).click(function(){
                                        open_shell(status["project_directory"]);
                                    });
                                }));
                                id++;
                                add_std_button(td, id, [], "Stop", project_stop,
                                    status);
                                id++;
                                add_std_button(td, id, ["float-right"],
                                    "Destroy", project_destroy, status);
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
    $.ajax({type: "GET", url: "get-statuses"})
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
        .fail(function(jqXHR, error, ex){
            alert("Unable to access project status data. Please try again.");
        });
};
