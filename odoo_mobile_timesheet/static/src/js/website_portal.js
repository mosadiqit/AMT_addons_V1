odoo.define('website_portal', function(require) {
    'use strict';
    require('website.website');
    
//    $(".input-search input.myInputsearch").on("change", function () {
//          var input, filter, table, tr, td, i, date, name, project;
//          input = document.getElementById("myInput");
//          var vals = this.value;
//          filter = input.value.toUpperCase();
//          table = document.getElementById("timesheet_table");
//          tr = table.getElementsByTagName("tr");
//          for (i = 0; i < tr.length; i++) {
//            name = tr[i].getElementsByTagName("td")[1];
//            if (name) {
//              if (name.innerHTML.toUpperCase().indexOf(filter) > -1) {
//                tr[i].style.display = "";
//              } 
//              else {
//                tr[i].style.display = "none";
//              }
//            }
//          }   
//        });


    $(document).ready(function(e){
        if ($("#portal_timesheet").html() == "True"){
            $("#footer").hide()
//            $("div.navbar-static-top")[0]['style']['backgroundColor'] = "#875A7B"
            $("nav.navbar-expand-md").removeClass('navbar-light bg-light');
            $("nav.navbar-expand-md").css({'background-color': "#875A7B"})
            var nav_length = $(".navbar-nav > li > a").length
            $("button.navbar-toggler").find("span.navbar-toggler-icon").html('<i class="fa fa-navicon"></i>').css({'color':"white"})
            for (var i=0; i<nav_length; i++){
                $(".navbar-nav > li > a")[i]['style']['color'] = "white"
//                $(".navbar-default .navbar-nav > li > a")[i]['style']['color'] = "white"
            }
            var textarea_length = $("textarea").length
            for (var i=0; i<textarea_length; i++){
                $("textarea")[i]['style']['borderColor'] = "#27BB64"
            }
            $("textarea").focus(function(){
                $(this)[0]['style']['borderColor'] = ""
            });
            $("textarea").focusout(function(){
                $(this)[0]['style']['borderColor'] = "#27BB64"
            });

            var select_length = $("select").length
            for (var i=0; i<select_length; i++){
                $("select")[i]['style']['borderColor'] = "#27BB64"
            }
            $("select").focus(function(){
                $(this)[0]['style']['borderColor'] = ""
            });
            $("select").focusout(function(){
                $(this)[0]['style']['borderColor'] = "#27BB64"
            });
            var input_length = $("input").length
            for (var i=0; i<input_length; i++){
                $("input")[i]['style']['borderColor'] = "#27BB64"
            }
            $("input").focus(function(){
                $(this)[0]['style']['borderColor'] = ""
            });
            $("input").focusout(function(){
                $(this)[0]['style']['borderColor'] = "#27BB64"
            });
//            $("div.navbar-static-top")[0]['style']['color'] = "red"
        }

        var state_options = $("select[name='task_id']:enabled option:not(:first)");
        $('.o_website_portal_details').on('change', "select[name='project_id']", function () {
            var select = $("select[name='task_id']");
            state_options.detach();
            var displayed_state = state_options.filter("[data-project_id="+($(this).val() || 0)+"]");
            var nb = displayed_state.appendTo(select).show().size();
            select.parent().toggle(nb>=0);
        });
        $('.o_website_portal_details').find("select[name='project_id']").change();
        });
        $(".input-search input.myInputsearch").on("change", function () {
          var input, filter, table, tr, td, i, date, name, project;
          input = document.getElementById("myInput");
          var vals = this.value;
          filter = input.value.toUpperCase();
          table = document.getElementById("timesheet_table");
          tr = table.getElementsByTagName("tr");
          for (i = 0; i < tr.length; i++) {
            date = tr[i].getElementsByTagName("td")[0];
            name = tr[i].getElementsByTagName("td")[1];
            if (date) {
              if (date.innerHTML.toUpperCase().indexOf(filter) > -1) {
                tr[i].style.display = "";
              } else if (name) {
                  if (name.innerHTML.toUpperCase().indexOf(filter) > -1) {
                    tr[i].style.display = "";
                  } else {
                    tr[i].style.display = "none";
                  }
            }
          }   
        }
    });

    if(!$('.o_website_portal_details').length) {
        return $.Deferred().reject("DOM doesn't contain '.o_website_portal_details'");
    }

    
});
