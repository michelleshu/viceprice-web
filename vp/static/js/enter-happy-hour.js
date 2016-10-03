var isMouseDown = false;
var dealTemplateHTML = "";
var dealDetailTemplateHTML = "";
var csrftoken = Cookies.get('csrftoken');

$.ajaxSetup({
     beforeSend: function(xhr, settings) {
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
         if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
             // Only send the token to relative URLs i.e. locally.
             xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
         }
     }
});

$(document).ready(function() {
    dealTemplateHTML = $(".deal-section").html();
    dealDetailTemplateHTML = $(".deal-detail-section").html();

    // Track mouse up for day of week selection
    $(document)
    .mouseup(function() {
        isMouseDown = false;
    });
});

$(document).on("click", ".submit-button", function() {
    var deals = $(".deal-section");
    var dealData = getDealInfo(deals);

    $.ajax({
        type: "POST",
        url: "/add_deal/",
        data: JSON.stringify({
            'deal': dealData,
            'location_id': parseInt($('#location-id').val())
        }),
        success: function() {
            document.location.reload(true);
        },
        error: function() {
            alert("Failed to submit deal");
        }
    });
});

$(document).on("click", ".mark-updated-button", function(event) {
    $.ajax({
        type: "POST",
        url: "/mark_location_updated/",
        data: JSON.stringify({
            'location_id': parseInt($('#location-id').val()),
            'updated_by': $('#first-name').val()
        }),
        success: function() {
            alert("Successfully marked as updated!");
        },
        error: function() {
            alert("Failed to mark as updated");
        }
    });
});

$(document).on("click", ".remove-deal-icon", function(event) {
    var dealDescriptionElement = $(event.target).parent().parent().find('.seven');
    var dealDescriptionText = '';
    dealDescriptionElement.find('div').each(function() {
        $(this).find('span').each(function() {
            dealDescriptionText = dealDescriptionText.concat($(this).text().trim() + ' ');
        });
        dealDescriptionText = dealDescriptionText.concat('\n');
    });
    
    var confirmation = confirm('Are you sure you want to delete this deal, ' + 
        $('#first-name').val() + '?\n\n' + dealDescriptionText);
    
    if (confirmation) {
        var dealId = parseInt($(event.target).attr('data-deal-id'), 10);
        $.ajax({
            type: "POST",
            url: "/delete_deal/",
            data: JSON.stringify({ "id": dealId }),
            success: function() {
                $(".remove-deal-icon[data-deal-id=" + dealId + "]").parent().parent().remove();
            }
        });
    }
});

$(document).on("mousedown", ".day-of-week-buttons button", function() {
    isMouseDown = true;
    $(this).toggleClass("button-primary");
    return false;
});

$(document).on("mouseover", ".day-of-week-buttons button", function() {
    if (isMouseDown) {
        $(this).toggleClass("button-primary");
    }
});

$(document).on("change", ".until-close", function() {
    if (this.checked) {
        $(this).prev().prop("disabled", true).val("");
    } else {
        $(this).prev().prop("disabled", false).val("00:00");
    }
});

$(document).on("click", ".add-time-period-link", function() {
    $(this).parent().parent().find(".second-time-period").removeClass("hidden");
    $(this).addClass("hidden");
});

$(document).on("click", ".delete-time-period-link", function() {
    $(this).parent().parent().find(".add-time-period-link").removeClass("hidden");
    $(this).parent().addClass("hidden");
});

$(document).on("change", ".deal-type", function() {
    if ($(this).val() == "price") {
        $(this).parent().parent().find(".dollar-prefix").removeClass("hidden");
        $(this).parent().parent().find(".percent-off-suffix").addClass("hidden");
        $(this).parent().parent().find(".price-off-suffix").addClass("hidden");
    }
    else if ($(this).val() == "percent-off") {
        $(this).parent().parent().find(".dollar-prefix").addClass("hidden");
        $(this).parent().parent().find(".percent-off-suffix").removeClass("hidden");
        $(this).parent().parent().find(".price-off-suffix").addClass("hidden");
    }
    else if ($(this).val() == "price-off") {
        $(this).parent().parent().find(".dollar-prefix").removeClass("hidden");
        $(this).parent().parent().find(".percent-off-suffix").addClass("hidden");
        $(this).parent().parent().find(".price-off-suffix").removeClass("hidden");
    }
});

$(document).on("click", ".add-deal-detail-link", function() {
    $(this).parent().before("<div class='deal-detail-section'>" + dealDetailTemplateHTML + "</div>");
});

$(document).on("click", ".delete-deal-detail-link", function() {
    if ($(".delete-deal-detail-link").length > 1) {
        $(this).parent().parent().remove();
    }
});

var getDealInfo = function(dealElement) {
    var daysOfWeek = getDaysOfWeek(dealElement.find(".day-of-week-buttons .button-primary"));
    var timePeriods = getTimePeriods(dealElement.find(".time-periods"));
    var dealDetails = getDealDetails(dealElement);

    return {
        "daysOfWeek": daysOfWeek,
        "timePeriods": timePeriods,
        "dealDetails": dealDetails
    }
};

var getTimePeriods = function(timePeriods) {
    var firstTimePeriod = {
        'startTime': timePeriods.find(".first-time-period .start-time").val(),
        'endTime': timePeriods.find(".first-time-period .end-time").val(),
        'untilClose': timePeriods.find(".first-time-period .until-close").is(":checked")
    };
    var timePeriodResults = [firstTimePeriod];

    if (timePeriods.find(".second-time-period").not(".hidden").length == 1) {
        var secondTimePeriod = {
            'startTime': timePeriods.find(".second-time-period .start-time").val(),
            'endTime': timePeriods.find(".second-time-period .end-time").val(),
            'untilClose': timePeriods.find(".second-time-period .until-close").is(":checked")
        };
        timePeriodResults.push(secondTimePeriod);
    }

    return timePeriodResults;
};

var getDealDetails = function(dealElement) {
    var dealDetails = dealElement.find(".deal-detail-section");
    var dealDetailResults = [];

    for (var i = 0; i < dealDetails.length; i++) {
        var detail = $(dealDetails[i]);
        dealDetailResults.push({
            'names': detail.find(".drink-names").val(),
            'category': detail.find(".drink-category").val(),
            'dealType': detail.find(".deal-type").val(),
            'dealValue': parseFloat(detail.find(".deal-value").val())
        });
    }

    return dealDetailResults;
};

var getDaysOfWeek = function(daysOfWeekPrimaryButtons) {
    var days = [];
    for (var i = 0; i < daysOfWeekPrimaryButtons.length; i++) {
        var button = daysOfWeekPrimaryButtons[i];
        if ($(button).hasClass("monday-button")) {
            days.push(1);
            continue;
        }
        if ($(button).hasClass("tuesday-button")) {
            days.push(2);
            continue;
        }
        if ($(button).hasClass("wednesday-button")) {
            days.push(3);
            continue;
        }
        if ($(button).hasClass("thursday-button")) {
            days.push(4);
            continue;
        }
        if ($(button).hasClass("friday-button")) {
            days.push(5);
            continue;
        }
        if ($(button).hasClass("saturday-button")) {
            days.push(6);
            continue;
        }
        if ($(button).hasClass("sunday-button")) {
            days.push(7);
        }
    }
    return days;
};