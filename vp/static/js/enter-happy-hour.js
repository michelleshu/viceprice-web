var isMouseDown = false;
var dealTemplateHTML = "";


var setHighlightingInteraction = function() {
    $(".day-of-week-buttons button")
    .mousedown(function() {
        isMouseDown = true;
        $(this).toggleClass("button-primary");
        return false;
    })
    .mouseover(function() {
        if (isMouseDown) {
            $(this).toggleClass("button-primary");
        }
    });

    $(document)
    .mouseup(function() {
        isMouseDown = false;
    });
};

var setTilCloseInteraction = function() {
    $(".until-close")
    .change(function() {
        if (this.checked) {
            $(this).prev().prop("disabled", true).val("");
        } else {
            $(this).prev().prop("disabled", false).val("00:00");
        }
    });
};

var setAddTimePeriodInteraction = function() {
    $(".add-time-period-link")
    .click(function() {
        $(this).parent().parent().find(".second-time-period").removeClass("hidden");
        $(this).addClass("hidden");
    });

    $(".delete-time-period-link")
    .click(function() {
        $(this).parent().parent().find(".add-time-period-link").removeClass("hidden");
        $(this).parent().addClass("hidden");
    })
};

var setInteractions = function() {
    setHighlightingInteraction();
    setTilCloseInteraction();
    setAddTimePeriodInteraction();
}

$(document).ready(function() {
    dealTemplateHTML = $(".deal-section").html();
    setInteractions();
});