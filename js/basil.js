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

jQuery(document).ready(function($){

    $(function(){
        $("#templates-dropdown").trigger('change');
    });
    $("#templates-dropdown").change(function(){
        var template_name = $(this).val();
        var option = $(this).find("option[value='" + template_name + "']");
        var template_title = option.attr("data-title");
        var template_description = option.attr("data-description");
        $("#template-description").text(template_title
            + ": " + template_description);
    });
    
    function project_action(project_directory, url, action_lbl, 
            success_handler, fail_handler){
        $.ajax({type: "POST",
                url: url,
                data: {
                    "project_directory": project_directory
                }
            })
            .done(function(response){
                /*console.log("AJAX call to " + url 
                    + " succeeded. project_directory was " + project_directory)*/
                success_handler();
            })
            .fail(function(jqXHR, error, ex){
                fail_handler();
                alert("Unable to " + action_lbl + " project. Cause: " + ex);
            }); 
    };

    function project_start(project_directory){
        project_action(project_directory, "project-start", "Start", 
            get_project_statuses, enable_all_btns);
    };
    
    function project_stop(project_directory){
        project_action(project_directory, "project-stop", "Stop", 
            get_project_statuses, enable_all_btns);
    };

    function confirm_destroy() {
        $( "#destroy-dialog" ).dialog({
	        autoOpen: false,
	        width: 400,
	        buttons: [
		        {
			        text: "Oops - No",
			        click: function() {
				        $( this ).dialog( "close" );
			        }
		        },
		        {
			        text: "Yes - Destroy!",
			        click: function() {
				        $( this ).dialog( "close" );
			        }
		        }
	        ]
        });
        $( "#destroy-dialog" ).dialog( "open" );
    };

    function project_destroy(project_directory){
        confirm_destroy();
        enable_all_btns();
        /*project_action(project_directory, "project-destroy", "Destroy", 
            get_project_statuses, enable_all_btns);*/
    };

    function disable_all_btns(){
        $("input[type=button]").attr("disabled", "disabled");
    };

    function enable_all_btns(){
        $("input[type=button]").removeAttr("disabled");
    };

    function display_project_statuses(response){
        $("#loading-projects").remove();
        $("#project-statuses > table").remove();
        var projs = $("#project-statuses");
        projs.append(make_el("table", [], function(table){
            $(table).append(make_el("thead", [], function(thead){
                 $(thead).append(make_el("tr", [], function(tr){
                    $(tr).append(make_el("th", [], function(th){
                        $(th).text("Project");
                        $(th).attr("id", "projs-col");
                    }));
                    $(tr).append(make_el("th", [], function(th){
                        $(th).text("Status");
                    }));
                    $(tr).append(make_el("th", [], function(th){
                        $(th).text("Actions");
                        $(th).attr("id", "actions-col");
                    }));
                }));
            }));
            $(table).append(make_el("tbody", [], function(tbody){
                 var id = 0;
                 _.each(response, function(status){
                    $(tbody).append(make_el("tr", [], function(tr){
                        $(tr).append(make_el("td", [], function(td){
                             $(td).html("<span class='project-name'>" 
                                 + status["project_name"]
                                 + "</span><br><span class='project-template'>"
                                 + "(from " + status["template_name"] + " "
                                 + status["template_version"] + ")</span>");
                        }));
                        $(tr).append(make_el("td", [], function(td){
                             $(td).html("<strong>" + status["project_state"]
                                 + "</strong> - " + status["project_state_msg"]);                                    
                        }));
                        $(tr).append(make_el("td", [], function(td){
                            switch(status["project_state"]){
                                case "Not Created":
                                case "Aborted":
                                case "Poweroff":
                                    // Start, Destroy
                                    $(td).append(make_el("input", [], function(btn){
                                        $(btn).attr("id", "btn_" + ++id);
                                        $(btn).attr("name", "btn_" + id);
                                        $(btn).attr("type", "button");
                                        $(btn).attr("value", "Start");
                                        $(btn).click(function(){
                                            disable_all_btns();
                                            project_start(status["project_directory"]);
                                        });
                                    }));
                                    $(td).append(make_el("input", ["float-right"], function(btn){
                                        $(btn).attr("id", "btn_" + ++id);
                                        $(btn).attr("name", "btn_" + id);
                                        $(btn).attr("type", "button");
                                        $(btn).attr("value", "Destroy");
                                        $(btn).click(function(){
                                            disable_all_btns();
                                            project_destroy(status["project_directory"]);
                                        });
                                    }));
                                    break;
                                case "Running":
                                    // View, Command, Stop, Destroy
                                    $(td).append(make_el("input", [], function(btn){
                                        $(btn).attr("id", "btn_" + ++id);
                                        $(btn).attr("name", "btn_" + id);
                                        $(btn).attr("type", "button");
                                        $(btn).attr("value", "View");
                                    }));
                                    $(td).append(make_el("input", [], function(btn){
                                        $(btn).attr("id", "btn_" + ++id);
                                        $(btn).attr("name", "btn_" + id);
                                        $(btn).attr("type", "button");
                                        $(btn).attr("value", "Run Command");
                                    }));
                                    $(td).append(make_el("input", [], function(btn){
                                        $(btn).attr("id", "btn_" + ++id);
                                        $(btn).attr("name", "btn_" + id);
                                        $(btn).attr("type", "button");
                                        $(btn).attr("value", "Stop");
                                        $(btn).click(function(){
                                            disable_all_btns();
                                            project_stop(status["project_directory"]);
                                        });
                                    }));
                                    $(td).append(make_el("input", ["float-right"], function(btn){
                                        $(btn).attr("id", "btn_" + ++id);
                                        $(btn).attr("name", "btn_" + id);
                                        $(btn).attr("type", "button");
                                        $(btn).attr("value", "Destroy");
                                        $(btn).click(function(){
                                            disable_all_btns();
                                            project_destroy(status["project_directory"]);
                                        });
                                    }));
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
        $.ajax({type: "GET", url: "get-statuses"})
            .done(function(response){
                // if no response, Chromium produces unhelpful error about syntax (see http://stackoverflow.com/a/23939381)
                if(response != ""){
                    display_project_statuses(response);
                } else {
                    alert("Got unexpected empty response - please refresh");
                };
            })
            .fail(function(jqXHR, error, ex){
                alert("Unable to access project status data. Please try again.");
            });
    };
    get_project_statuses();
    var refresh_in_ms = 5*60*1000;
    setInterval(get_project_statuses, refresh_in_ms);
});
