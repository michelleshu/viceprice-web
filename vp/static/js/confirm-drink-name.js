var dealID;
var itemIDs = [];

$(document).ready(function() {
    get_deal_that_needs_confirmation();

    $("#submit-button").click(function(event) {

        event.preventDefault();
        event.stopPropagation();

        var namesSelected = [];
        for (var i  = 0; i < itemIDs.length; i++) {
            var id = itemIDs[i];
            var name = $("input[type=radio][name='" + id  + "']:checked").val();
            if (name == "custom") {
                name = $("input[type=text][name='" + id  + "']").val();
            }

            namesSelected.push({
                "dealDetailID": id,
                "name": name
            });
        }

        var data = {
            "dealID": dealID,
            "namesSelected": namesSelected
        };

        $.ajax({
            type: "POST",
            url: "/submit_drink_names/",
            data: JSON.stringify(data),
            success: function(data) {
                $(".deal-data").remove();
                get_deal_that_needs_confirmation();
            },
            error: function() {
                alert("Failed to submit names");
            }
        })
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
                    dealHours += "<p>" + moment(data.day, "d").format("dddd ") +
                            moment(data.start, "HH:mm:ss").format("h:mmA - ") +
                            moment(data.end, "HH:mm:ss").format("h:mmA") + "</p>";
                }

                itemIDs = [];
                for (var i = 0; i < dealDetailData.length; i++) {
                    var dealDetailID = dealDetailData[i]["id"];
                    itemIDs.push(dealDetailID);
                    var dealDetailDrinkNames = dealDetailData[i]["drink_names"];
                    var drinkNamesOptions = "";

                    for (var j = 0; j < dealDetailDrinkNames.length; j++) {
                        drinkNamesOptions += "<div class='row'><input type='radio' name='" + dealDetailID +
                            "' value='" + dealDetailDrinkNames[j] + "'/>" +
                            "<span class='drink-name-label'>" + dealDetailDrinkNames[j] + "</span></div>";
                    }

                    $(".confirm-drink-name-container").append("<div class='deal-data'>" + dealHours + drinkNamesOptions +
                        "<div class='row'><input type='radio' name='" + dealDetailID +
                        "' value='custom' selected/><input type='text' name='" + dealDetailID + "'/></row></div><hr/>"
                    );
                }
            }
        },
        error: function(){
            alert("Failed to retrieve deal for confirm");
        }
    });
};