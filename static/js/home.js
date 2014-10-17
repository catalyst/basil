jQuery(document).ready(function($){
    setup_template_form();
    get_project_statuses();
    var refresh_in_ms = 5*60*1000;
    setInterval(get_project_statuses, refresh_in_ms);
});
