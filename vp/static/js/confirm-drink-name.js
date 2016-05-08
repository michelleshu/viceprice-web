$(document).ready(function() {
    get_deal_that_needs_confirmation();
});

var get_deal_that_needs_confirmation = function() {
    $.ajax({
        type: "GET",
        url: "/get_deal_that_needs_confirmation",

        success: function(data){
            var dealDetailData = data["deal_detail_data"];

            for (var i = 0; i < dealDetailData.length; i++) {
                var dealDetailID = dealDetailData[i]["id"];
                var dealDetailDrinkNames = dealDetailData[i]["drink_names"];
                var drinkNamesOptions = "";

                for (var j = 0; j < dealDetailDrinkNames.length; j++) {
                    drinkNamesOptions += "<div class='row'><input type='radio' name='" + dealDetailID +
                        "' value='" + dealDetailDrinkNames[j] + "'/>" + dealDetailDrinkNames[j] + "</div>";
                }

                $(".confirm-drink-name-container").append(drinkNamesOptions +
                    "<div class='row'><input type='radio' name='" + dealDetailID + "' value='custom'/><input type='text'/></row><hr/>"
                );
            }
        },
        error: function(){
            alert("Failed to retrieve deal for confirm");
        }
    });
};