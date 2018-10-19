//Bootstrap remember tab
// Javascript to enable link to tab

/*
 * A global ajaxComplete method that shows you any messages that are set in Django's view
 */
$( document )
    .ajaxStart( function() {
        $('#ajaxloading').show();
    })
    .ajaxStop( function() {
         $('#ajaxloading').hide();
    });

if (!Date.prototype.toISODate) {
  Date.prototype.toISODate = function() {
    return this.getFullYear() + '-' +
           ('0'+ (this.getMonth()+1)).slice(-2) + '-' +
           ('0'+ this.getDate()).slice(-2);
  }
}
function isDate(dateVal) {
    /*
    var pattern = /^(\d{4})-(\d{2})-(\d{2})$/;
    var dateArray = dateVal.match(pattern);
    if (dateArray == null) return false;

    var currentYear = (new Date).getFullYear();
    var year = dateArray[1];
    var month = dateArray[2];
    var day = dateArray[3];
    if (year < 2010 || year > (currentYear+3)) return false;
    if (month < 1 || month > 12) return false;
    if (day < 1 || day > 31) return false;
    return new Date(dateVal) === 'Invalid Date' ? false : true;
    */
    var date = new Date(dateVal);
    if (date == 'Invalid Date') {
        return false;
    }
    var currentYear = (new Date).getFullYear();
    if (date.getFullYear() > currentYear + 100 || date.getFullYear() < 1980 ) {
        return false;
    }
    return true;
}

function formatDate(dateString, day=0) {
    var months = new Array();
    months[1] = "Jan";
    months[2] = "Feb";
    months[3] = "Mar";
    months[4] = "Apr";
    months[5] = "May";
    months[6] = "Jun";
    months[7] = "Jul";
    months[8] = "Aug";
    months[9] = "Sep";
    months[10] = "Oct";
    months[11] = "Nov";
    months[12] = "Dec";

    if (dateString == null || dateString == undefined || dateString.length == 0 || dateString == 'undefined' || dateString == 'null' ) {
        return '';
    }
    try {
        var dateval = new Date(dateString);
        tz = dateval.getTimezoneOffset();
        hrs = dateval.getHours();
        if (hrs > 0) {
            // alert("offsetting timezone tz=" + tz + " hrs = " + hrs);
            dateval.setMinutes(dateval.getMinutes() + tz);
        }
        var month = months[(dateval.getMonth() + 1)];
        var ret = month.concat(' ').concat(day == 0 ? dateval.getDate() : day).concat(', ').concat(dateval.getFullYear());
        return ret;
    } catch (err) {
        console.log(err);
        try {
            var dateArray = dateString.split('-');
            var month = months[parseInt(dateArray[1])]
            return month.concat(' ').concat(day == 0 ? dateArray[2] : day).concat(', ').concat(dateArray[0]);
        }
        catch (err) {
            return dateString == null ? '' : dateString;
        }
    }
}


$(function() {
     // Javascript to enable link to tab
    var hash = document.location.hash;
    if (hash) {
    $('.nav-tabs a[href='+hash+']').tab('show');
    }

    // Change hash for page-reload
    $('a[data-toggle="tab"]').on('show.bs.tab', function (e) {
    window.location.hash = e.target.hash;
    });
});

//
function submitClose(){
    opener.location.reload(true);
    self.close();
}

//App specific JavaScript
$(function () {
  $('[data-toggle="tooltip"]').tooltip()
})

//custom jquery to trigger date picker, info pop-over and print category text
$(document).ready(function() {
    $('.datepicker').datepicker({dateFormat: "yy-mm-dd"});
});


/*
 * Create and show a Bootstrap alert.
 */
function createAlert (type, message, fade, whereToAppend) {
    if (whereToAppend == undefined ){
        whereToAppend = "#messages";
    }
    $(whereToAppend).append(
        $(
            "<div class='alert alert-" + type + " dynamic-alert alert-dismissable' style='margin-top:0;'>" +
            "<button type='button' class='close' data-dismiss='alert' aria-hidden='true'>&times;</button>" +
            "<p>" + message + "</p>" +
            "</div>"
        )
    );
    if (fade == true) {
        // Remove the alert after 5 seconds if the user does not close it.
        $(".dynamic-alert").delay(5000).fadeOut("slow", function () { $(this).remove(); });
    }
}

/*
* Save the task checkbox state
*/
function tasklistChange(pk,type,value){
    // send true or false back to the update and set the checkbox class
    if ($('#' + type + '_' + pk ).hasClass( "glyphicon glyphicon-check") == true ) {
        $.get('/workflow/checklist_update_link/' + pk + '/' + type + '/0/', function(data){
            $('#' + type + '_' + pk ).removeClass("glyphicon glyphicon-check").addClass("glyphicon glyphicon-unchecked");
        });
    }else{
        $.get('/workflow/checklist_update_link/' + pk + '/' + type + '/1/', function(data){
            $('#' + type + '_' + pk ).removeClass("glyphicon glyphicon-unchecked").addClass("glyphicon glyphicon-check");
        });
    }

}

// using jQuery
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

/*
 * Set the csrf header before sending the actual ajax request
 * while protecting csrf token from being sent to other domains
 */
$.ajaxSetup({
    crossDomain: false, // obviates need for sameOrigin test
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    }
});

/*
* Save the bookmark
*/
function newBookmark(bookmark_url){


     $.ajax({ url: "/workflow/new_bookmark/",
                     data: {
                        url: bookmark_url ,
                        csrfmiddlewaretoken: getCookie('csrftoken'),
                     },
                     type: 'POST',
                     success: function(data) {
                         $('#bookmarks').load(location.href + " #bookmarks>*", "");
                     },
    });

}



$(document).ready(function() {
    $(document).on('hidden.bs.modal', '.modal', function () {
        $('.modal:visible').length && $(document.body).addClass('modal-open');
    });
    /*
    *  Reload page if country dropdown changes on main dashboard
    */
    $('#something').click(function() {
        load(url, data, loadComplete);
    });

     /*
     * Handle change in the indicator services drop-down; updates the indicator drop-down accordingly.
     */
    $("#services").change(function() {
        var selected_service = $(this).val();
        if (selected_service == undefined || selected_service == -1 || selected_service == '') {
            $("#serivce").html("<option>--Service--</option>");
        } else {
            var url = "/indicators/service/" + selected_service + "/service_json/";
            $.getJSON(url, function(service) {

                var options = '<option value="0">--Indicator--</option>';
                for (var i = 0; i < service.length; i++) {
                    options += '<option value="' + service[i].nid + '">' + service[i].type + ' - ' + service[i].level + ' - ' + service[i].title + '</option>';
                }

                $("#service_indicator").html(options);
                $("#service_indicator_option:first").attr('selected', 'selected');
            });
        }

        // page-specific-action call if a page has implemented the 'country_dropdwon_has_changed' function
        if(typeof services_dropdwon_has_changed != 'undefined') services_dropdwon_has_changed(selected_service);
    });


    /*
     * Handle change in the country drop-down; updates the province drop-down accordingly.
     */
    $("select#id_country").change(function() {
        var selected_country = $(this).val();
        if (selected_country == undefined || selected_country == -1 || selected_country == '') {
            $("select#id_country").html("<option>--Country--</option>");
        } else {
            var url = "/workflow/country/" + selected_country + "/country_json/";
            $.getJSON(url, function(province) {
                var options = '<option value="">--Level 1--</option>';
                for (var i = 0; i < province.length; i++) {
                    options += '<option value="' + province[i].pk + '">' + province[i].fields['name'] + '</option>';
                }

                $("select#id_province").html(options);
                $("select#id_province_option:first").attr('selected', 'selected');
            });
        }

        // page-specific-action call if a page has implemented the 'country_dropdwon_has_changed' function
        if(typeof country_dropdown_has_changed != 'undefined') country_dropdown_has_changed(selected_country);
    });


    /*
     * Handle change in the province drop-down; updates the district drop-down accordingly.
     */
    $("select#id_province").change(function() {
        var selected_province = $(this).val();
        if (selected_province == undefined || selected_province == -1 || selected_province == '') {
            $("select#id_province").html("<option>--Level 1--</option>");
        } else {
            var url = "/workflow/province/" + selected_province + "/province_json/";
            $.getJSON(url, function(district) {
                var options = '<option value="">--Level 2--</option>';
                for (var i = 0; i < district.length; i++) {
                    options += '<option value="' + district[i].pk + '">' + district[i].fields['name'] + '</option>';
                }

                $("select#id_district").html(options);
                $("select#id_district option:first").attr('selected', 'selected');
            });
        }

        // page-specific-action call if a page has implemented the 'country_dropdwon_has_changed' function
        if(typeof country_dropdown_has_changed != 'undefined') country_dropdown_has_changed(selected_country);
    });


    /*
     * Handle change in the province drop-down; updates the district drop-down accordingly.
     */
    $("select#id_district").change(function() {
        var selected_district = $(this).val();
        if (selected_district == undefined || selected_district == -1 || selected_district == '') {
            $("select#id_district").html("<option>--Level 2--</option>");
        } else {
            var url = "/workflow/district/" + selected_district + "/district_json/";
            $.getJSON(url, function(adminthree) {
                var options = '<option value="">--Level 3--</option>';
                for (var i = 0; i < adminthree.length; i++) {
                    options += '<option value="' + adminthree[i].pk + '">' + adminthree[i].fields['name'] + '</option>';
                }

                $("select#id_admin_level_three").html(options);
                $("select#id_admin_level_three option:first").attr('selected', 'selected');
            });
        }

        // page-specific-action call if a page has implemented the 'country_dropdwon_has_changed' function
        if(typeof country_dropdown_has_changed != 'undefined') country_dropdown_has_changed(selected_country);
    });


    /*
     * Handle change in office drop-down
     */
    $("select#id_district").change(function(vent) {
        var selected_distirct = $(this).val();
        if (selected_distirct == -1) {
            return;
        }

        // page-specific-action call if a page has implemented the 'office_dropdown_has_changed' function
        if(typeof district_dropdown_has_changed != 'undefined') distirct_dropdown_has_changed(district_office);
    });

/*
* CUSTOM DASHBOARD
*/

    // on change to Step 2, selector, save change to db
    // on change to Step 3, selector, save change to db


    /*
     * UPDATE BUDGET TOTAL
    */
    function updateBudget()
    {
        var mc_budget = parseFloat($("#mc_budget").val());
        var other_bidget = parseFloat($("#other_budget").val());
        var total = mc_budget + other_budget;
        var total = total.toFixed(2);
        $("#total_budget").val(total);
    }
    $(document).on("change, keyup", "#mc_budget", updateBudget);
    $(document).on("change, keyup", "#other_budget", updateBudget);

    /*
     * Calculate Total Indirect Beneficiaries
    */
    function updateBens()
    {
        var direct_bens = parseFloat($("#id_estimated_num_direct_beneficiaries").val());
        var avg_houshold_size = parseFloat($("#id_average_household_size").val());
        var total = direct_bens * avg_houshold_size;
        var total = total.toFixed(2);
        $("#id_estimated_num_indirect_beneficiaries").val(total);
    }
    $(document).on("change, keyup", "#id_estimated_num_direct_beneficiaries", updateBens);
    $(document).on("change, keyup", "#id_average_household_size", updateBens);

    /*
     * Trained TOTAL
    */
    function updateTrained()
    {
        var male = parseFloat($("#id_estimate_male_trained").val());
        var female = parseFloat($("#id_estimate_female_trained").val());
        var total = male + female;
        var total = total.toFixed(0);
        $("#id_estimate_total_trained").val(total);
    }
    $(document).on("change, keyup", "#id_estimate_male_trained", updateTrained);
    $(document).on("change, keyup", "#id_estimate_female_trained", updateTrained);

    /*
     * CFW Workers TOTAL
    */
    function updateCFW()
    {
        var male = parseFloat($("#id_cfw_estimate_male").val());
        var female = parseFloat($("#id_cfw_estimate_female").val());
        var total = male + female;
        var total = total.toFixed(0);
        $("#id_cfw_estimate_total").val(total);
    }
    $(document).on("change, keyup", "#id_cfw_estimate_male", updateCFW);
    $(document).on("change, keyup", "#id_cfw_estimate_female", updateCFW);

    $('.dropdown-menu a').on('click', function(){
        $(this).parent().parent().prev().html($(this).html() + '<span class="caret"></span>');
    })

    /*
    * Expand accordion down to location hash and then load collected data
    */
    if(location.hash != null && location.hash != ""){
        $('.collapse').removeClass('in');
        $(location.hash + '.collapse').collapse('show');
        indicator_id = location.hash.split('-')
        console.log(indicator_id)
        //loadIndicators(indicator_id[1])
    }
});

/*
* Pop-up window for help docs and guidance on forms
*/

function newPopup(url, windowName) {
    return window.open(url,windowName,'height=768,width=1366,left=1200,top=10,titlebar=no,toolbar=no,menubar=no,location=no,directories=no,status=no');
}

// EXAMPLE: <a onclick="newPopup('https://docs.google.com/document/d/1tDwo3m1ychefNiAMr-8hCZnhEugQlt36AOyUYHlPbVo/edit?usp=sharing','Form Help/Guidance'); return false;" href="#" class="btn btn-sm btn-info">Form Help/Guidance</a>

$('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
  e.target // activated tab
  e.relatedTarget // previous tab
})

/*
* Confirm Change of Short form to Long
*/
function confirmshort() {
      if (document.getElementById('id_short').checked == true) {
        return false;
      } else {
       var box= confirm("Warning: The short form is recommended for all cases except COMPLEX programs.  Are you sure you want to do this?");
        if (box==true)
            return true;
        else
           document.getElementById('id_short').checked = true;

      }
    }