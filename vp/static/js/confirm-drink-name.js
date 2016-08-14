var dealID;
var locationID;
var itemIDs = [];

$(document).ready(function() {
    get_deal_that_needs_confirmation();

    $(document).on("click", ".delete-deal-detail", function(e) {
        // Don't allow deletion of last detail
        if ($(".deal-data").length <= 1) {
            alert("Cannot delete last deal detail. Reject the whole deal instead.");
            return;
        }

        var dealDetailId = parseInt($(e.target).attr("data-deal-detail-id"));

        $.ajax({
            type: "POST",
            url: "/delete_deal_detail/",
            data: JSON.stringify({ "id": dealDetailId }),
            success: function() {
                $(".delete-deal-detail[data-deal-detail-id=" + dealDetailId + "]").parent().parent().remove();
            }
        });
    });

    $("#reject-button").click(function(event) {
        event.preventDefault();
        event.stopPropagation();

        $.ajax({
            type: "POST",
            url: "/reject_deal/",
            data: JSON.stringify({ "locationID": locationID }),
            success: function() {
                $(".location-name").remove();
                $(".deal-hours").remove();
                $(".deal-data").remove();
                get_deal_that_needs_confirmation();
            }
        })
    });


    $("#submit-button").click(function(event) {
        event.preventDefault();
        event.stopPropagation();

        var namesSelected = [];
        for (var i  = 0; i < itemIDs.length; i++) {
            var id = itemIDs[i];
            var name = $("input[type=radio][name='" + id  + "']:checked").val();

            if (!name) {
                continue;
            }

            if (name == "custom") {
                name = $("input[type=text][name='" + id  + "']").val();
            }

            namesSelected.push({
                "dealDetailID": id,
                "name": name
            });
        }

        var data = {
            "locationID": locationID,
            "dealID": dealID,
            "namesSelected": namesSelected
        };

        $.ajax({
            type: "POST",
            url: "/submit_drink_names/",
            data: JSON.stringify(data),
            success: function(data) {
                $(".location-name").remove();
                $(".deal-hours").remove();
                $(".deal-data").remove();
                get_deal_that_needs_confirmation();
            },
            error: function() {
                alert("Failed to submit names");
            }
        });
    })
});

$(document).on("focus", "input[type='text']", function() {
    $(this).parent().closest('.deal-data').find("input[type='radio']").prop("checked", false);
    $(this).prev().prop("checked", true);
});

$(document).on("click", ".drink-name-label", function() {
    $(this).parent().closest('.deal-data').find("input[type='radio']").prop("checked", false);
    $(this).prev().prop("checked", true);
});

var get_deal_that_needs_confirmation = function() {
    $.ajax({
        type: "GET",
        url: "/get_deal_that_needs_confirmation",

        success: function(data) {
            locationID = data["location_id"];
            var locationName = data["location_name"];
            var dealHoursData = data["deal_hour_data"];
            var dealDetailData = data["deal_detail_data"];
            dealID = data["deal_id"];
            var dealsCount = data["deals_count"];

            if (dealsCount == 0) {
                $(".remaining-count").html("No Deals Left to Confirm!");
            }
            else {
                $(".remaining-count").html(dealsCount + " Deals Left to Confirm");

                var dealHours = "";
                for (var i = 0; i < dealHoursData.length; i++) {
                    var data = dealHoursData[i];
                    var dealEnd = data.end !== "None" ? moment(data.end, "HH:mm:ss").format("h:mmA") : "close";
                    dealHours += "<p>" + moment(data.day % 7, "d").format("dddd ") +
                            moment(data.start, "HH:mm:ss").format("h:mmA - ") +
                            dealEnd + "</p>";
                }

                $(".confirm-drink-name-container").append("<h5 class='location-name'>" + locationName +
                    "</h5><h6 class='deal-hours'>" + dealHours + "</h6><hr/>");

                itemIDs = [];
                for (var i = 0; i < dealDetailData.length; i++) {
                    var dealDetail = dealDetailData[i];

                    itemIDs.push(dealDetail.id);

                    var drinkCategory = "";
                    if (dealDetail.drink_category === 1) {
                        drinkCategory = "Beer";
                    } else if (dealDetail.drink_category === 2) {
                        drinkCategory = "Wine";
                    } else if (dealDetail.drink_category === 3) {
                        drinkCategory = "Liquor";
                    }

                    var dealValue = "";
                    if (dealDetail.detail_type === 1) {
                        dealValue = "$" + dealDetail.value;
                    } else if (dealDetail.detail_type === 2) {
                        dealValue = dealDetail.value + "% off";
                    } else if (dealDetail.detail_type === 3) {
                        dealValue = "$" + dealDetail.value + " off";
                    }
                    var dealDetailDrinkNames = dealDetail["drink_names"];
                    var drinkNamesOptions = "";

                    for (var j = 0; j < dealDetailDrinkNames.length; j++) {
                        drinkNamesOptions += "<div class='row'><input type='radio' name='" + dealDetail.id +
                            "' value='" + dealDetailDrinkNames[j] + "'/>" +
                            "<span class='drink-name-label'>" + dealDetailDrinkNames[j] + "</span></div>";
                    }

                    $(".confirm-drink-name-container").append("<div class='deal-data'>" +
                        "<h6>" + drinkCategory + " - " + dealValue +
                        "<i class='fa fa-minus-circle delete-deal-detail' data-deal-detail-id='" + dealDetail.id + "'></i></h6>" +
                        drinkNamesOptions +
                        "<div class='row'><input type='radio' name='" + dealDetail.id +
                        "' value='custom' selected/><input type='text' name='" + dealDetail.id + "'/></row></div><hr/>"
                    );
                }
            }
        },
        error: function(){
            alert("Failed to retrieve deal for confirm");
        }
    });
};