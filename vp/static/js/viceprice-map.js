// MAPBOX
L.mapbox.accessToken = 'pk.eyJ1Ijoic2FsbWFuYWVlIiwiYSI6ImNpa2ZsdXdweTAwMXl0d20yMWVlY3g4a24ifQ._0c3U-A8Lv6C7Sm3ceeiHw';
var map;
var neighborhoodPolygonLayer;
var clusterLayer;
var markerLayer;
var hiddenNeighborhoodLayer;
var selectedMarker;

// CUSTOM MARKER ASSETS
var restaurantMarker = L.icon({
    iconUrl: '../static/img/restaurant-marker.png',
    iconSize:     [37, 42], // size of the icon in pixels
    iconAnchor:   [17, 42], //The coordinates of the "tip" of the icon (relative to its top left corner). 
    						//The icon will be aligned so that this point is at the marker's geographical location
    popupAnchor:  [3, -42]	//The coordinates of the point from which popups will "open", relative to the icon anchor.
});

var restaurantMarkerClicked = L.icon({
    iconUrl: '../static/img/restaurant-marker-clicked.png',
    iconSize:     [37, 42], 
    iconAnchor:   [17, 42],
    popupAnchor:  [3, -42]
});

var barMarker = L.icon({
    iconUrl: '../static/img/bar-marker.png',
    iconSize:     [37, 42], 
    iconAnchor:   [17, 42],
    popupAnchor:  [3, -42]
});

var barMarkerClicked = L.icon({
    iconUrl: '../static/img/bar-marker-clicked.png',
    iconSize:     [37, 42], 
    iconAnchor:   [17, 42],
    popupAnchor:  [3, -42]
});

// NEIGHBORHOOD FILTER
var selectedNeighborhood;

// TIME FILTERS
var selectedDay = null;
var selectedTime = null;
var timeFilterActive = false;

var DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
var HOURS_IN_DAY = 24, MINUTES_IN_HOUR = 60;
var MIN_HOUR = 8, MAX_HOUR = 3 + HOURS_IN_DAY;

// INITIALIZATION
var init = function() {
	initializeDayAndTime();
	loadMap();
	loadRegionalView();
};
init();

// LOAD MAP
function loadMap() {
	if (!map) {
		map = L.map('map', {
			center : [ 38.907557, -77.028130 ], // Initial geographical center of the map
			minZoom : 13, // Minimum zoom level of the map
			zoom : 13, // Initial map zoom
			attributionControl: false // Remove attribution from map (added in the left menu instead)
		});
		
		//The map restricts the view to the given geographical bounds, bouncing the user back when he tries to pan outside the view
		var southWest = L.latLng(38.820993, -76.875833),
			northEast = L.latLng(39.004460, -77.158084),
			bounds = L.latLngBounds(southWest, northEast);
		map.setMaxBounds(bounds);
		
		// Use styleLayer to add a Mapbox style created in Mapbox Studio
		L.mapbox.styleLayer('mapbox://styles/salmanaee/cikoa5qxo00gf9vm0s5cut4aa')
			.addTo(map);
		
		clusterLayer = new L.MarkerClusterGroup({ 
			polygonOptions: {
	    		//set opacity and fill opacity to zero to disable the L.Polygon (highlight)
	    		opacity: 0, 
	    		fillOpacity: 0
	    	}
		});
		
		markerLayer = L.mapbox.featureLayer();
		map.addLayer(clusterLayer);
		
		// Zoom Event Handler 
		map.on('zoomend', function() {			
			// Hide marker detail when zoomed out to full map
			if (this.getZoom() === 13 && hiddenNeighborhoodLayer) {
				selectedNeighborhood = null;
				reloadData();
				markerLayer.setGeoJSON([]);
				clusterLayer.clearLayers();
				neighborhoodPolygonLayer.addLayer(hiddenNeighborhoodLayer);
				$(".neighborhood-label").show();
			}
		});
	}
}

function reloadData() {
	populateLocationCountsByNeighborhood();
	if (selectedNeighborhood) {
		loadSingleNeighborhoodView(selectedNeighborhood);
	}
}

// LOAD REGIONAL (NEIGHBORHOOD OVERVIEW) VIEW
function loadRegionalView() {
	if (!neighborhoodPolygonLayer) {
		$.getJSON("static/json/neighborhood-polygons.json")
			.done(function(data) {
				neighborhoodPolygonLayer = L.geoJson(data, {
					style: getNeighborhoodFeatureStyle,
					onEachFeature: displayNeighborhoodFeature
				}).addTo(map);
				populateLocationCountsByNeighborhood();
			});
	}
}

function populateLocationCountsByNeighborhood() {
	var queryString = "";
	if (selectedDay) {
		queryString += "?day=" + selectedDay;
		
		if (selectedTime && timeFilterActive) {
			queryString += "&time=" + selectedTime;
		}
	}
	$.get("/fetch_location_counts_by_neighborhood" + queryString, function(data) {
		var counts = JSON.parse(data["result"]);
		
		$(".location-count-label").text("(0)");
		
		for (var neighborhood in counts) {
			$("div[data-neighborhood-name='" + neighborhood + "'] .location-count-label")
				.text("(" + counts[neighborhood] + ")");
		}
	});
}

function getNeighborhoodFeatureStyle(feature) {
	return {
		weight : 2,
		color : '#c8a45e',
		fillOpacity : 0.7,
		fillColor : 'rgb(35, 40, 43)'
	};
}

function displayNeighborhoodFeature(feature, layer) {
	// Neighborhood Name Label
	var label = L.marker(getLabelLocation(feature, layer), {
		icon : L.divIcon({
			className : 'label', 
			html : getNeighborhoodLabelHTML(feature.id, feature.properties.name),
			iconSize : [ 100, 35 ]
		})
	}).addTo(map);
	
	// Event Handlers
	layer.on('mouseover', function(e) {
		// Darken neighborhood label color
		$(".neighborhood-label[data-neighborhood-id='" + feature.id + "'] .name-label")[0].style.color = 'rgb(35, 40, 43)';
		$(".neighborhood-label[data-neighborhood-id='" + feature.id + "'] .location-count-label")[0].style.color = 'rgb(35, 40, 43)';
		$(".neighborhood-label[data-neighborhood-id='" + feature.id + "'] .name-label")[0].style.opacity = 1;
		$(".neighborhood-label[data-neighborhood-id='" + feature.id + "'] .location-count-label")[0].style.opacity = 1;
		
		// Lighten background color
		layer.setStyle({
			weight : 3,
			fillColor : 'rgb(200, 164, 94)',
			fillOpacity : 0.85 
		});
	});
	
	layer.on('mouseout', function(e) {
		// Lighten neighborhood label color
		$(".neighborhood-label[data-neighborhood-id='" + feature.id + "'] .name-label")[0].style.color = 'white';
		$(".neighborhood-label[data-neighborhood-id='" + feature.id + "'] .location-count-label")[0].style.color = 'rgb(200, 164, 94)';
		$(".neighborhood-label[data-neighborhood-id='" + feature.id + "'] .name-label")[0].style.opacity = 0.7;
		$(".neighborhood-label[data-neighborhood-id='" + feature.id + "'] .location-count-label")[0].style.opacity = 0.7;
		
		// Darken background color
		layer.setStyle({
			weight : 2,
			fillColor : 'rgb(35, 40, 43)',
			fillOpacity : 0.7
		});
	});
	
	layer.on('click', function(e) {
		if (selectedNeighborhood != feature.properties.name) {
			if (hiddenNeighborhoodLayer) {
				neighborhoodPolygonLayer.addLayer(hiddenNeighborhoodLayer);
			}
			hiddenNeighborhoodLayer = layer;
			
			// Lighten neighborhood label color
			$(".neighborhood-label[data-neighborhood-id='" + feature.id + "'] .name-label")[0].style.color = 'white';
			$(".neighborhood-label[data-neighborhood-id='" + feature.id + "'] .location-count-label")[0].style.color = 'rgb(200, 164, 94)';
			$(".neighborhood-label[data-neighborhood-id='" + feature.id + "'] .name-label")[0].style.opacity = 0.7;
			$(".neighborhood-label[data-neighborhood-id='" + feature.id + "'] .location-count-label")[0].style.opacity = 0.7;
			
			// Darken background color
			layer.setStyle({
				weight : 2,
				fillColor : 'rgb(35, 40, 43)',
				fillOpacity : 0.7
			});
			
			neighborhoodPolygonLayer.removeLayer(layer);
			
			$(".neighborhood-label").show();
			$(".neighborhood-label[data-neighborhood-id='" + e.target.feature.id + "']").hide();
			
			map.fitBounds(e.target.getBounds());

			loadSingleNeighborhoodView(feature.properties.name);
		}
	});
	
	label.on('mouseover',function(e) { layer.fireEvent('mouseover'); });
	label.on('mouseout', function(e) { layer.fireEvent('mouseout'); });
	label.on('click', function(e) { layer.fireEvent('click'); });
}

// Set neighborhood label positions
function getLabelLocation (feature, layer) {
	switch(parseInt(feature.id)) {
		case 2:
			return L.latLng(38.932, -77.095); // West DC
		case 3:
			return L.latLng(38.928, -77.068); // Friendship Heights
		case 4:
			return L.latLng(38.930, -77.043); // Adams Morgan
		case 5:
			return L.latLng(38.932, -76.990); // East DC
		case 9:
			return L.latLng(38.930, -77.030); // Columbia Heights
		case 10:
			return L.latLng(38.911, -77.042); // Dupont Circle
		case 11:
			return L.latLng(38.895, -77.048); // Foggy Bottom
		case 13:
			return L.latLng(38.911, -77.032); // Logan Circle
		case 14:
			return L.latLng(38.917, -77.031); // U Street
		case 15:
			return L.latLng(38.875, -77.010); // Waterfront
		case 16:
			return L.latLng(38.874, -76.960); // South East
		case 17:
			return L.latLng(38.900, -76.986); // H Street
		default:
			return layer.getBounds().getCenter();
	}
}

// Set neighborhood label style
function getNeighborhoodLabelHTML(neighborhoodId, neighborhoodName) {
	var displayName;
	
	switch(parseInt(neighborhoodId)) {
		case 4:
			displayName = "Adams<br/>Morgan";
			break;
		case 9:
			displayName = "Columbia<br/>Heights";
			break;
		case 10:
			displayName = "Dupont<br/>Circle";
			break;
		case 13:
			displayName = "Logan<br/>Circle";
			break;
		default:
			displayName = neighborhoodName;
	}
	
	return "<div class='neighborhood-label' data-neighborhood-name='" + neighborhoodName + 
		"' data-neighborhood-id=" + neighborhoodId + " style='font-size: 0.85rem;'>" + 
		"<div class='name-label'>" + displayName + "</div>" +
		"<div class='location-count-label'></div></div>";
}


// LOAD VIEW FOR SINGLE NEIGHBORHOOD
function loadSingleNeighborhoodView(neighborhood) {
	var queryString = "?neighborhood=" + neighborhood;
	selectedNeighborhood = neighborhood;
	if (selectedDay) {
		queryString += "&day=" + selectedDay;
		
		if (selectedTime && timeFilterActive) {
			queryString += "&time=" + selectedTime;
		}
	}

	$.get("/fetch_filtered_deals" + queryString, function(data) {
		clusterLayer.clearLayers();
		markerLayer.setGeoJSON(JSON.parse(data["result"]));
	});
}

markerLayer.on('layeradd', function(e) {
    var marker = e.layer,
        properties = marker.feature.properties;

	clusterLayer.addLayer(marker);
	
	if (properties.superCategory == "Bar") {
		marker.setIcon(barMarker);
	} else {
		marker.setIcon(restaurantMarker);
	}
	
	// Bind pop up to marker
	marker.bindPopup(getMarkerPopupContent(properties), {
	    closeButton: false,  // Controls the presence of a close button in the popup
	    minWidth: 340
	});
	
	marker.on('mouseover', function() {
		marker.openPopup();
	});
	
	marker.on('mouseout', function() {
		marker.closePopup();
	});
	
	function getMarkerPopupContent(properties){
		// Display preview of first deal only, even if there are multiple ones
		var deal = properties.deals[0];
		var markup = "<ul class='tooltip-info'><li><h1>" + properties.name + "</h1></li>";

		if (properties.subCategories && properties.subCategories.length > 0) {
			markup += "<li><h2>" + properties.subCategories[0] + "</h2>";
		} else {
			markup += "<li>"
		}
		
		var start = moment(deal.start,'HH:mm:ss').format('h:mm A');
		var end = deal.end ? moment(deal.end,'HH:mm:ss').format('h:mm A') : "CLOSE";
		markup += "<h3>" + start + " - " + end  + "</h3></li>";
		
		// Display best deals per category
		var beers = deal.dealDetails.filter(function(detail) { return detail.drinkCategory == 1; });
		var wines = deal.dealDetails.filter(function(detail) { return detail.drinkCategory == 2; });
		var liquors = deal.dealDetails.filter(function(detail) { return detail.drinkCategory == 3; });
		
		if (beers.length > 0) {
			markup += "<img src='../static/img/beer.png'/><p>" + 
				formatDealDetail(beers.reduce(getBestDealDetail)) + "</p>";
		}
		
		if (wines.length > 0) {
			markup += "<img src='../static/img/wine.png'/><p>" + 
				formatDealDetail(wines.reduce(getBestDealDetail)) + "</p>";
		}
  	
		if (liquors.length > 0) {
			markup += "<img src='../static/img/liquor.png'/><p>" + 
				formatDealDetail(liquors.reduce(getBestDealDetail)) + "</p>";
		}

	    return markup + '</li></ul>';
	}
	
	function getBestDealDetail(dealDetailA, dealDetailB) {
		if (dealDetailA.detailType != dealDetailB.detailType) {
			return dealDetailA.detailType < dealDetailB.detailType
				? dealDetailA
				: dealDetailB;
		}
		else if (dealDetailA.detailType === 1) {	// Price
			return dealDetailA.value < dealDetailB.value 
				? dealDetailA
				: dealDetailB;
		} 
		else { // Percent Off or Price Off
			return dealDetailA.value < dealDetailB.value
				? dealDetailB
				: dealDetailA;
		}
	}
	
	function formatDealDetail(dealDetail) {
		if (dealDetail.detailType == 1) {
			return "$" + dealDetail.value;
		}
		else if (dealDetail.detailType == 2) {
			return dealDetail.value + "% off";
		}
		else {
			return "$" + dealDetail.value + " off";
		}
	}
	
	function formatDealDetailWithDescription(dealDetail) {
		return formatDealDetail(dealDetail) + " " + dealDetail.drinkName;
	}
	
	function getDealMarkup(dealDetails) {
		var beers = dealDetails.filter(function(detail) { return detail.drinkCategory == 1; });
		var wines = dealDetails.filter(function(detail) { return detail.drinkCategory == 2; });
		var liquors = dealDetails.filter(function(detail) { return detail.drinkCategory == 3; });
		
		var markup = "<table style='width: 100%;'>";
		if (beers.length > 0) {
			markup += "<tr><td class='drink-category-column'><img src='../static/img/beer.png'/></td>" + 
				"<td class='deal-detail-column'><ul><li>";
			markup += beers.map(formatDealDetailWithDescription).join("</li><li>") + "</li></ul></td></tr>";
		}
		
		if (wines.length > 0) {
			markup += "<tr><td class='drink-category-column'><img src='../static/img/wine.png'/></td>" + 
				"<td class='deal-detail-column'><ul><li>";
			markup += wines.map(formatDealDetailWithDescription).join("</li><li>") + "</li></ul></td></tr>";
		}
		
		if (liquors.length > 0) {
			markup += "<tr><td class='drink-category-column'><img src='../static/img/liquor.png'/></td>" + 
				"<td class='deal-detail-column'><ul><li>";
			markup += liquors.map(formatDealDetailWithDescription).join("</li><li>") + "</li></ul></td></tr>";
		}

		return markup + "</table>";
	}

    marker.on('click', function(e) {
		var properties = this.feature.properties;
		// TODO Add capacity to display multiple deals
		var deal = properties.deals[0];

        if (properties.superCategory == "Bar") {
    		marker.setIcon(barMarkerClicked);
		} else {
    	    marker.setIcon(restaurantMarkerClicked);
		}
		
        if (selectedMarker) {
    		if (selectedMarker.feature.properties.superCategory == "Bar") {
				selectedMarker.setIcon(barMarker);
			} else {
    			selectedMarker.setIcon(restaurantMarker);
			}
    	}
		
		selectedMarker = this;

    	// Show the right menu
        $(".slider-arrow").attr("src", "../static/img/right-arrow.png");
        $(".right-side-bar").show("slide", { direction: "right" }, 700);
        $(".sliding").animate({ right: "25%" } , 700);

        // Reset margins for cover photo
		$("#location-cover-photo").css("-webkit-clip-path", "inset(0px 0px)");
		$("#location-cover-photo").css("margin-top", "0px");
		$("#location-cover-photo").css("margin-bottom", "0px");
		$("#location-cover-photo").removeAttr("src");
		$("#location-cover-photo").attr("data-x-offset", properties["coverXOffset"]);
		$("#location-cover-photo").attr("data-y-offset", properties["coverYOffset"]);

		// Add cover photo if applicable
		if (properties["coverPhotoSource"]) {
			$("#location-cover-photo").attr("src", properties["coverPhotoSource"]);
		}

		// Location information
        $("#location-name").html(properties["name"]); 
		$("#location-categories").html("");

		var subCategories = properties["subCategories"];
		for (var i = 0; i < subCategories.length; i++) {
			if(i == 0) //add a left margin for the first element
				$("#location-categories").append("<div class='category' style='margin-left:1rem;'>" + subCategories[i] + "</div>");
			else
				$("#location-categories").append("<div class='category'>" + subCategories[i] + "</div>");
			
			if(i != (subCategories.length-1)) //Don't add '|' at the end of the last element
				$("#location-categories").append(" | ");
		}

        $("#location-address").html(properties["street"]);
        $("#location-phone-number").html(properties["phoneNumber"]);
        
        if (properties["happyHourWebsite"]){
            $("#location-website").html("Source of Info");
            $("#location-website").attr("href", properties["happyHourWebsite"]);  
        }
        else { 
            $("#location-website").html("Website");
            $("#location-website").attr("href", properties["website"]);
        }
        
		$(".rev-hr").css("display","block");
		$(".icon-globe").css("display","inline");
		$(".icon-phone").css("display","inline");
		$(".icon-home").css("display","inline");
		
		// Deal Info
		var start = moment(deal.start,'HH:mm:ss').format('h:mm A');
		var end = deal.end ? moment(deal.end,'HH:mm:ss').format('h:mm A') : "CLOSE";
        $("#deal-time-frame").html(start + " - " + end);
        $("#deal-details-div").html(getDealMarkup(deal.dealDetails));
		
		// Yelp Reviews
        $("#yelp_log").attr("src","../static/img/yelp-logo-small.png");
        $.get("/yelpReviews/?yelp_id=" + properties["yelpId"],function(data){
        	yelp_api_response = data.response; // refer to yelpReview on views.py for more details
        	$("#rating_img").attr("src",yelp_api_response.overall_rating_img);
        	$("#review_count").html("(" + yelp_api_response.review_count + ")");
        	$("#name").html(yelp_api_response.username); //username
        	$("#profile_img").attr("src",yelp_api_response.user_img);
        	$("#excerpt").html("\" "+yelp_api_response.excerpt+" \"");
        	$(".reviews-div").click(function() {
				window.open(yelp_api_response.url); 
			});
        });
    })
});


// DAY AND TIME FILTERS
function initializeDayAndTime() {
	var now = moment();
	
	// Initialize day
	var dayFilter = $("#day");
	dayFilter.on("input", function(event) {
		selectedDay = dayFilter.val();
		$('#day_output').val(DAYS_OF_WEEK[selectedDay - 1]);
		
		reloadData();
	});
	
	selectedDay = now.day();
	dayFilter.val(selectedDay);
	$('#day_output').val(DAYS_OF_WEEK[selectedDay - 1]);
	
	// Initialize time filter, but don't set time until activated
	$("#filter-by-hours").change(function() {
        if ($(this).is(":checked")) {
            $("#time").show();
			$("#time_output").show();
			timeFilterActive = true;
        } else {
			$("#time").hide();
			$("#time_output").hide();
			timeFilterActive = false;
		}
		
		reloadData();
	});
	
	var timeFilter = $('#time');
	timeFilter.attr('step', MINUTES_IN_HOUR / 2);
	timeFilter.attr('min', MIN_HOUR * MINUTES_IN_HOUR);
	timeFilter.attr('max', MAX_HOUR * MINUTES_IN_HOUR);

	timeFilter.on('input', function(event) {
		var totalMinutes = timeFilter.val();
		var hours = totalMinutes / MINUTES_IN_HOUR;
		if (hours > 24) hours -= 24;
		var minutes = totalMinutes % MINUTES_IN_HOUR;
		var selectedTimeMoment = moment({ hours: hours, minutes: minutes });
		selectedTime = selectedTimeMoment.format("H:mm");
		$("#time_output").text(selectedTimeMoment.format("hh:mm A"));
		
		reloadData();
	});
	
	var nowTotalMinutes = now.hours() * MINUTES_IN_HOUR + now.minutes();
	if (nowTotalMinutes < timeFilter.attr('min')) {
		nowTotalMinutes += HOURS_IN_DAY * MINUTES_IN_HOUR;
	}
	// Round current time
	var hours = now.minutes() > 30 ? now.hours() + 1 : now.hours();
	if (hours > 24) hours -= 24;
	var minutes = now.minutes() > 30 ? 0 : 30;
	var selectedTimeMoment = moment({ hours: hours, minutes: minutes });
	selectedTime = selectedTimeMoment.format("H:mm");
	$('#time_output').text(selectedTimeMoment.format("hh:mm A"));
	timeFilter.val(nowTotalMinutes);
}

/*** DC Metro Stations ***/
var metroLayer = L.mapbox.featureLayer().addTo(map); //create en empty feature layer for the metro stations
													//actual data won't get loaded until a specific neighborhood is clicked

/*Once this layer is loaded to the map do the following:
1)Add an icon for each metro station 
2)Bind a popup to each station that contains: it's name +  train line*/
metroLayer.on('layeradd', function(e) {
  var marker = e.layer,
      feature = e.layer.feature;
  marker.setIcon(L.icon({iconUrl: '../static/img/metro.png',iconSize: [16, 16]}));

  //popup content (name + line colors)
  var metroTooltip = "<div class='metro_info'><p>" + feature.properties.NAME+"</p>";
  var lineColor = feature.properties.LINE.split(","); //in case a station has multiple lines (red, blue, orange)
  for(i in lineColor){ // create a div for each line and assign a color to it
  	metroTooltip=metroTooltip+"<div class='line' style='background-color:"+lineColor[i]+";'></div>";
  }
	metroTooltip=metroTooltip+"</div>";
  
  marker.bindPopup(metroTooltip,{
        closeButton: false,
        minWidth: 90
    });

  marker.on('mouseover', function() {
    marker.openPopup();
    });

    marker.on('mouseout', function() {
    marker.closePopup();
    });
});


// ZOOM FUNCTIONS 

$("#neighboor-zoom").click(function() {
	$(".slider-arrow").attr("src", "../static/img/left-arrow.png");
	$(".right-side-bar").hide("slide", { direction: "right" }, 700);
	$(".sliding").animate({ right: "0"} , 700);
	$menu_visible=false;
	map.setView([38.907557, -77.028130],13,{zoom:{animate:true}});
});

$("#zoom-in").click(function() {
	var zoom = map.getZoom();
	map.setZoom(zoom + 1);
});

$("#zoom-out").click(function() {
	var zoom = map.getZoom();
	map.setZoom(zoom-1);
});