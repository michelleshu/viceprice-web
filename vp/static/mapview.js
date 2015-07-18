var COPY_TYPE = {
    AllDays: 1,
    Weekdays: 2,
    Weekend: 3
};

function initialize() {
    var markers = [];
    var arlington = new google.maps.LatLng(38.8803, -77.1083);

    var mapOptions = {
        center: arlington,
        zoom: 13
    };

    var map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);

    // Create the search box and link it to the UI element
    var input = document.getElementById('pac-input');
    map.controls[google.maps.ControlPosition.TOP_LEFT].push(input);
    var searchBox = new google.maps.places.SearchBox(input);

    // Listen for the event fired when the user selects an item from the pick list.
    // Retrieve the matching places for that item.
    google.maps.event.addListener(searchBox, 'places_changed', function() {
        var places = searchBox.getPlaces();

        if (places.length == 0) {
            return;
        }
        for (var i = 0, marker; marker = markers[i]; i++) {
            marker.setMap(null);
        }

        // For each place, get the icon, place name and location
        markers = [];
        var bounds = new google.maps.LatLngBounds();
        for (var i = 0, place; place = places[i]; i++) {
            var image = {
                url: place.icon,
                size: new google.maps.Size(71, 71),
                origin: new google.maps.Point(0, 0),
                anchor: new google.maps.Point(17, 34),
                scaledSize: new google.maps.Size(25, 25)
            };

            // Create a marker for each place
            var marker = new google.maps.Marker({
                map: map,
                icon: image,
                title: place.place_id,
                position: place.geometry.location
            });
            markers.push(marker);

            // Create an info window for each marker
            var contentString = getInfoWindowContentString(place);

            var infowindow = new google.maps.InfoWindow({
                content: contentString
            });

            google.maps.event.addListener(marker, 'click', function() {
                infowindow.open(map, marker);
                activateInfoWindow(marker.title);
            });

            bounds.extend(place.geometry.location);
        }

        map.fitBounds(bounds);
    });

    // Bias the search results towards places that are within the bounds of the current map's viewport
    google.maps.event.addListener(map, 'bounds_changed', function() {
        var bounds = map.getBounds();
        searchBox.setBounds(bounds);
    });
}

function getInfoWindowContentString(place) {
    var contentString = "<form method='POST' class='infowindow-form' id='place-info-form'>" +
        "<div class='info-window-line'><span id='place-name-" + place.place_id + "'>" + place.name + "</span></div>" +
        "<div class='info-window-line'><span id='info-window-title'>Address:</span>" +
            "<span class='place-address-" + place.place_id + "'>" + place.formatted_address + "</span></div>" +
        "<div class='info-window-line'><span class='info-window-title'>Phone Number:</span>" +
            "<span class='place-phone-number-" + place.place_id + "'>" + place.formatted_phone_number + "</span></div>" +
        "<div class='info-window-line'><span class='info-window-title'>Website:</span>" +
            "<a href='" + place.website + "' id='place-website-" + place.place_id + " target='_blank'>" + place.website + "</a></div>" +
        "<div class='info-window-line'><span class='info-window-title'>Business Hours:</span>" +
            "<a href='#' id='copy-business-hours-all-link-" + place.place_id + "'>Copy All </a>" +
            "<a href='#' id='copy-business-hours-weekdays-link-" + place.place_id + "'>Weekdays </a>" +
            "<a href='#' id='copy-business-hours-weekend-link-" + place.place_id + "'>Weekend </a>" +
            "<a href='#' id='clear-business-hours-link-" + place.place_id + "'>Clear</a>" +
            "<table class='business-hour-table'>" +
                "<tr><td>Monday</td><td><input class='time-input' type='time' autocomplete='on' id='monday-opening-" + place.place_id + "'></input> to " +
                    "<input class='time-input' type='time' autocomplete='on' id='monday-closing-" + place.place_id + "'></input></td></tr>" +
                "<tr><td>Tuesday</td><td><input class='time-input' type='time' autocomplete='on' id='tuesday-opening-" + place.place_id + "'></input> to " +
                    "<input class='time-input' type='time' autocomplete='on' id='tuesday-closing-" + place.place_id + "'></input></td></tr>" +
                "<tr><td>Wednesday</td><td><input class='time-input' type='time' autocomplete='on' id='wednesday-opening-" + place.place_id + "'></input> to " +
                    "<input class='time-input' type='time' autocomplete='on' id='wednesday-closing-" + place.place_id + "'></input></td></tr>" +
                "<tr><td>Thursday</td><td><input class='time-input' type='time' autocomplete='on' id='thursday-opening-" + place.place_id + "'></input> to " +
                    "<input class='time-input' type='time' autocomplete='on' id='thursday-closing-" + place.place_id + "'></input></td></tr>" +
                "<tr><td>Friday</td><td><input class='time-input' type='time' autocomplete='on' id='friday-opening-" + place.place_id + "'></input> to " +
                    "<input class='time-input' type='time' autocomplete='on' id='friday-closing-" + place.place_id + "'></input></td></tr>" +
                "<tr><td>Saturday</td><td><input class='time-input' type='time' autocomplete='on' id='saturday-opening-" + place.place_id + "'></input> to " +
                    "<input class='time-input' type='time' autocomxplete='on' id='saturday-closing-" + place.place_id + "'></input></td></tr>" +
                "<tr><td>Sunday</td><td><input class='time-input' type='time' autocomplete='on' id='sunday-opening-" + place.place_id + "'></input> to " +
                    "<input class='time-input' type='time' autocomplete='on' id='sunday-closing-" + place.place_id + "'></input></td></tr>" +
            "</table></div>" +
        "<div class='info-window-line'><span class='info-window-title'>Product Categories:</span>" +
            "<select class='product-categories-selector' id='product-categories-selector-" + place.place_id + "' multiple='multiple'>" +
                "<option value='1'>Cigarettes</option>" +
                "<option value='2'>Cigars</option>" +
                "<option value='3'>Beer</option>" +
                "<option value='4'>Wine</option>" +
                "<option value='5'>Liquor</option>" +
                "<option value='6'>Marijuana</option>" +
            "</select></div>" +
        "<input type='submit'></input>" +
        "<div class='place-latitude hidden' id='place-latitude-" + place.place_id + "'>" + place.geometry.location.A + "</div><div class='place-longitude hidden' id='place-longitude-" + place.place_id + "'>" + place.geometry.location.F + "</div><div class='place-google-id hidden'>" + place.place_id + "</div>" +
        "</form>";

    return contentString;
}

function activateInfoWindow(place_id) {
    // Set copy business hours links
    $('#copy-business-hours-all-link-' + place_id).click(
        {
            place_id: place_id,
            copy_type: COPY_TYPE.AllDays
        },
        copyBusinessHours
    );

    $('#copy-business-hours-weekdays-link-' + place_id).click(
        {
            place_id: place_id,
            copy_type: COPY_TYPE.Weekdays
        },
        copyBusinessHours
    );

    $('#copy-business-hours-weekend-link-' + place_id).click(
        {
            place_id: place_id,
            copy_type: COPY_TYPE.Weekend
        },
        copyBusinessHours
    );

    $('#clear-business-hours-link-' + place_id).click(
        {
            place_id: place_id
        },
        clearBusinessHours
    );

    $('#product-categories-selector-' + place_id).select2();

    $('#place-info-form').submit(
        {
            place_id: place_id
        },
        submitPlaceInfo
    );
}

function copyBusinessHours(e) {
    var place_id = e.data.place_id;
    var copy_type = e.data.copy_type;

    var weekday_opening_value = $('#monday-opening-' + place_id).val();
    var weekday_closing_value = $('#monday-closing-' + place_id).val();
    var weekend_opening_value = $('#saturday-opening-' + place_id).val();
    var weekend_closing_value = $('#saturday-closing-' + place_id).val();

    if (copy_type === COPY_TYPE.AllDays || copy_type === COPY_TYPE.Weekdays) {
        $('#tuesday-opening-' + place_id).val(weekday_opening_value);
        $('#wednesday-opening-' + place_id).val(weekday_opening_value);
        $('#thursday-opening-' + place_id).val(weekday_opening_value);
        $('#friday-opening-' + place_id).val(weekday_opening_value);

        $('#tuesday-closing-' + place_id).val(weekday_closing_value);
        $('#wednesday-closing-' + place_id).val(weekday_closing_value);
        $('#thursday-closing-' + place_id).val(weekday_closing_value);
        $('#friday-closing-' + place_id).val(weekday_closing_value);
    }

    if (copy_type == COPY_TYPE.AllDays) {
        $('#saturday-opening-' + place_id).val(weekday_opening_value);
        $('#sunday-opening-' + place_id).val(weekday_opening_value);

        $('#saturday-closing-' + place_id).val(weekday_closing_value);
        $('#sunday-closing-' + place_id).val(weekday_closing_value);
    }

    if (copy_type == COPY_TYPE.Weekend) {
        $('#saturday-opening-' + place_id).val(weekend_opening_value);
        $('#sunday-opening-' + place_id).val(weekend_opening_value);

        $('#saturday-closing-' + place_id).val(weekend_closing_value);
        $('#sunday-closing-' + place_id).val(weekend_closing_value);
    }
}

function clearBusinessHours(e) {
    var place_id = e.data.place_id;

    $('#monday-opening-' + place_id).val('');
    $('#tuesday-opening-' + place_id).val('');
    $('#wednesday-opening-' + place_id).val('');
    $('#thursday-opening-' + place_id).val('');
    $('#friday-opening-' + place_id).val('');
    $('#saturday-opening-' + place_id).val('');
    $('#sunday-opening-' + place_id).val('');

    $('#monday-closing-' + place_id).val('');
    $('#tuesday-closing-' + place_id).val('');
    $('#wednesday-closing-' + place_id).val('');
    $('#thursday-closing-' + place_id).val('');
    $('#friday-closing-' + place_id).val('');
    $('#saturday-closing-' + place_id).val('');
    $('#sunday-closing-' + place_id).val('');
}

function savePlaceInfo(e) {
    var place_id = e.data.place_id;

    $.ajax({
        url: "save_place_info/",
        type: "POST",
        data: {
            place_id: place_id,
            place_name: $('#place-name-' + place_id).val(),
            address: $('#place-address-' + place_id).val(),
            phone_number: $('#place-phone-number-' + place_id).val(),
            website: $('#place-website-' + place_id).val(),
            business_hours: {
                monday_opening: $('#monday-opening-' + place_id).val(),
                tuesday_opening: $('#tuesday-opening-' + place_id).val(),
                wednesday_opening: $('#wednesday-opening-' + place_id).val(),
                thursday_opening: $('#thursday-opening-' + place_id).val(),
                friday_opening: $('#friday-opening-' + place_id).val(),
                saturday_opening: $('#saturday-opening-' + place_id).val(),
                sunday_opening: $('#sunday-opening-' + place_id).val(),
                monday_closing: $('#monday-closing-' + place_id).val(),
                tuesday_closing: $('#tuesday-closing-' + place_id).val(),
                wednesday_closing: $('#wednesday-closing-' + place_id).val(),
                thursday_closing: $('#thursday-closing-' + place_id).val(),
                friday_closing: $('#friday-closing-' + place_id).val(),
                saturday_closing: $('#saturday-closing-' + place_id).val(),
                sunday_closing: $('#sunday-closing-' + place_id).val()
            },
            product_categories: $('#product-categories-selector-' + place_id).val(),
            latitude: $('#place-latitude-' + place_id).val(),
            longitude: $('#place-longitude-' + place_id).val()
        }
    });

}

google.maps.event.addDomListener(window, 'load', initialize);
