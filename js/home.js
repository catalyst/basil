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
    get_project_statuses();
    var refresh_in_ms = 5*60*1000;
    setInterval(get_project_statuses, refresh_in_ms);
});
