// MAPBOX
L.mapbox.accessToken = 'pk.eyJ1Ijoic2FsbWFuYWVlIiwiYSI6ImNpa2ZsdXdweTAwMXl0d20yMWVlY3g4a24ifQ._0c3U-A8Lv6C7Sm3ceeiHw';
var map;
var loadingIndicator;
var neighborhoodPolygonLayer;
var markerLayer;
var metroLayer;
var metroLayerData;
var hiddenNeighborhoodLayer;
var selectedMarker;

var markersByNeighborhood = {};
var neighborhoodCounts = {};

var mediaScreenWidth = 737;

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
    loadMetroData();
	initializeDayAndTime();
	initializeLoadingIndicator();
	loadMap();
	loadRegionalView();
};
init();

// Returns a function, that, as long as it continues to be invoked, will not
// be triggered. The function will be called after it stops being called for
// N milliseconds. If `immediate` is passed, trigger the function on the
// leading edge, instead of the trailing.
function debounce(func, wait, immediate) {
	var timeout;
	return function() {
		var context = this, args = arguments;
		var later = function() {
			timeout = null;
			if (!immediate) func.apply(context, args);
		};
		var callNow = immediate && !timeout;
		clearTimeout(timeout);
		timeout = setTimeout(later, wait);
		if (callNow) func.apply(context, args);
	};
};

// LOAD MAP
function loadMap() {
      map = L.map('map', {
        center : [ 38.907557, -77.028130 ], // Initial geographical center of the map
        minZoom : 13, // Minimum zoom level of the map
        zoom : 13, // Initial map zoom
      });

		//The map restricts the view to the given geographical bounds, bouncing the user back when he tries to pan outside the view
		var southWest = L.latLng(38.820993, -76.875833),
			northEast = L.latLng(39.004460, -77.158084),
			bounds = L.latLngBounds(southWest, northEast);
		map.setMaxBounds(bounds);

		// Use styleLayer to add a Mapbox style created in Mapbox Studio
		L.mapbox.styleLayer('mapbox://styles/salmanaee/cikoa5qxo00gf9vm0s5cut4aa')
			.addTo(map);

        metroLayer = L.mapbox.featureLayer();
        map.addLayer(metroLayer);

		markerLayer = L.mapbox.featureLayer();
		map.addLayer(markerLayer);

		// Zoom Event Handler
		map.on('zoomend', function() {
			// Hide marker detail when zoomed out to full map
			if (this.getZoom() === 13) {
				// Hide sidebar
				$(".slider-arrow").attr("src", "../static/img/left-arrow.png");
				$(".right-side-bar").hide("slide", { direction: "right" }, 700);
				$(".sliding").animate({ right: "0"} , 700);
			}
		});
}

var reloadData = debounce(function() {
	populateLocationCountsByNeighborhood();
	if (selectedNeighborhood) {
		loadSingleNeighborhoodView(selectedNeighborhood);
	}
}, 200);

// LOAD REGIONAL (NEIGHBORHOOD OVERVIEW) VIEW
function loadRegionalView() {
	$(".loading-indicator-container").show();
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

function loadMetroData() {
    $.getJSON("static/json/dc-metro.json")
        .done(function(data) {
            metroLayerData = data;
        });
}

function populateLocationCountsByNeighborhood() {
    // Try to retrieve data from cache
    var timeValue = timeFilterActive ? selectedTime : "none";
    if (neighborhoodCounts[selectedDay] && neighborhoodCounts[selectedDay][timeValue]) {
        var counts = neighborhoodCounts[selectedDay][timeValue];
        $(".location-count-label").text("(0)");
        for (var neighborhood in counts) {
            $("div[data-neighborhood-name='" + neighborhood + "'] .location-count-label")
                .text("(" + counts[neighborhood] + ")");
        }
        return;
    }

	$(".loading-indicator-container").show();
	var queryString = "";
	if (selectedDay) {
		queryString += "?day=" + selectedDay;

		if (selectedTime && timeFilterActive) {
			queryString += "&time=" + selectedTime;
		}
	}
	$.get("/fetch_location_counts_by_neighborhood" + queryString, function(data) {
		var counts = JSON.parse(data["result"]);
        var timeValue = timeFilterActive ? selectedTime : "none";

        neighborhoodCounts[selectedDay] = neighborhoodCounts[selectedDay] || {};
        neighborhoodCounts[selectedDay][timeValue] = counts;

		$(".location-count-label").text("(0)");
		for (var neighborhood in counts) {
			$("div[data-neighborhood-name='" + neighborhood + "'] .location-count-label")
				.text("(" + counts[neighborhood] + ")");
		}

		$(".loading-indicator-container").hide();
	});
}

function getNeighborhoodFeatureStyle(feature) {
	return {
		weight : 2,
		color : '#c8a45e',
		fillOpacity : 0.85,
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
		$(".neighborhood-label[data-neighborhood-id='" + feature.id + "'] .name-label")[0].style.opacity = 1;
		$(".neighborhood-label[data-neighborhood-id='" + feature.id + "'] .location-count-label")[0].style.opacity = 1;

		// Darken background color
		layer.setStyle({
			weight : 2,
			fillColor : 'rgb(35, 40, 43)',
			fillOpacity : 0.85
		});
	});

	layer.on('click', function(e) {
		if (selectedNeighborhood != feature.properties.name) {  
            ga('send', {
              hitType: 'event',
              eventCategory: 'Neighborhood',
              eventAction: 'click',
              eventLabel: feature.properties.name
            });
            
			if (hiddenNeighborhoodLayer) {
				neighborhoodPolygonLayer.addLayer(hiddenNeighborhoodLayer);
			}
			hiddenNeighborhoodLayer = layer;

			// Lighten neighborhood label color
			$(".neighborhood-label[data-neighborhood-id='" + feature.id + "'] .name-label")[0].style.color = 'white';
			$(".neighborhood-label[data-neighborhood-id='" + feature.id + "'] .location-count-label")[0].style.color = 'rgb(200, 164, 94)';
			$(".neighborhood-label[data-neighborhood-id='" + feature.id + "'] .name-label")[0].style.opacity = 1;
			$(".neighborhood-label[data-neighborhood-id='" + feature.id + "'] .location-count-label")[0].style.opacity = 1;

			// Darken background color
			layer.setStyle({
				weight : 2,
				fillColor : 'rgb(35, 40, 43)',
				fillOpacity : 0.85
			});

			neighborhoodPolygonLayer.removeLayer(layer);

			$(".neighborhood-label").show();
			$(".neighborhood-label[data-neighborhood-id='" + e.target.feature.id + "']").hide();

			map.fitBounds(e.target.getBounds());

			loadSingleNeighborhoodView(feature.properties.name);
		}
	});

	label.on('mouseout', function(e) { layer.fireEvent('mouseout'); });
	label.on('mouseover',function(e) { layer.fireEvent('mouseover'); });
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
    selectedNeighborhood = neighborhood;

    var filteredMetroData = {
        "type": "FeatureCollection",
        "features": metroLayerData.features.filter(function(data) {
            return data.properties.NEIGHBORHOOD == selectedNeighborhood;
        })
    };
    metroLayer.setGeoJSON(filteredMetroData);

    // Try to get deal data for markers from cache
    var timeValue = timeFilterActive ? selectedTime : "none";
    if (markersByNeighborhood[neighborhood] &&
        markersByNeighborhood[neighborhood][selectedDay] &&
        markersByNeighborhood[neighborhood][selectedDay][timeValue]) {

        var markers = markersByNeighborhood[neighborhood][selectedDay][timeValue];
        markerLayer.setGeoJSON(markers);
        return;
    }

	$(".loading-indicator-container").show();

	var queryString = "?neighborhood=" + neighborhood;
	if (selectedDay) {
		queryString += "&day=" + selectedDay;

		if (selectedTime && timeFilterActive) {
			queryString += "&time=" + selectedTime;
		}
	}

	$.get("/fetch_filtered_deals" + queryString, function(data) {
		markerLayer.setGeoJSON(JSON.parse(data["result"]));

        var timeValue = timeFilterActive ? selectedTime : "none";
        markersByNeighborhood[neighborhood] = markersByNeighborhood[neighborhood] || {};
        markersByNeighborhood[neighborhood][selectedDay] = 
            markersByNeighborhood[neighborhood][selectedDay] || {};
        markersByNeighborhood[neighborhood][selectedDay][timeValue] = JSON.parse(data["result"]);
        
		$(".loading-indicator-container").hide();
	});
}

markerLayer.on('layeradd', function(e) {
    var marker = e.layer,
        properties = marker.feature.properties;

	if (properties.superCategory == "Bar") {
		marker.setIcon(barMarker);
	} else {
		marker.setIcon(restaurantMarker);
	}
    
	// Bind pop up to marker
  if ($(window).width() > mediaScreenWidth) {
	  marker.bindPopup(getMarkerPopupContent(properties), {
	      closeButton: false,  // Controls the presence of a close button in the popup
	      minWidth: 340
	  });
      
    Tipped.create(marker._icon, 'Click for more details', { position: 'bottom' });
    
    marker.on('add', function() {
        Tipped.create(marker._icon, 'Click for more details', { position: 'bottom' });
    });
  }
    
    marker.on('mouseover', function() {
        if ($(window).width() > mediaScreenWidth) { marker.openPopup(); }
	});

	marker.on('mouseout', function() {
		if ($(window).width() > mediaScreenWidth) { marker.closePopup(); }
	});

  function getMobileItemDetails(properties) {
    var markup = "<img src=" + properties.coverPhotoSource + ">";
    markup += "<div class='mobile-item-details-sign'>Happy Hour Specials</div>";
    markup += "<div class='mobile-item-details-deals'>" + getDealMobileMarkup(properties.deals[0].dealDetails) + "</div><hr>";


    //yelp_api_response = {
    //  review_count: 149,
    //  username: "Bharat P.",
    //  overall_rating_img: "https://s3-media1.fl.yelpcdn.com/assets/2/www/img/5ef3eb3cb162/ico/stars/v1/stars_3_half.png",
    //  url: "http://www.yelp.com/biz/nanny-o-briens-irish-pub-washington?utm_campaign=yelp_api&utm_medium=api_v2_business&utm_source=Piz41a8pB1aBdsTg5jkZDw",
    //  user_img: "http://s3-media1.fl.yelpcdn.com/photo/NdAva2yfUt5uC57vfxUfUg/ms.jpg",
    //  excerpt: "I regularly meet up with friends at Nanny O' Briens to play board games, and I enjoy this place Pros - Service is usually really good. The bartender is..."
    //}

    //markup += "<div class='mobile-item-review'><img src=" + yelp_api_response.user_img + " width='40' height='40' style='float: left'>"
    //markup += "<p><span>"+ yelp_api_response.username + " - </span>" + yelp_api_response.excerpt + "</div>"
    //markup += "<div class='mobile-item-readmore'><a href=" + yelp_api_response.url + ">Read More</a></div></div></div>"

    $.get("/yelpReviews/?yelp_id=" + properties["yelpId"],function(data){
      yelp_api_response = data.response;

      markup += "<div class='mobile-item-details-reviews'><h3>Reviews</h3>";
      markup += "<div class='mobile-item-review'><img src=" + yelp_api_response.user_img + " width='40' height='40' style='float: left'>"
      markup += "<p><span>"+ yelp_api_response.username + " - </span>" + yelp_api_response.excerpt + "</div>"
      markup += "<div class='mobile-item-readmore'><a href=" + yelp_api_response.url + ">Read More</a></div></div>"
      markup += "</div><hr>"
      return markup;
    });

    markup += "<div class='mobile-item-metadata'><ul>";
    markup += "<li><a href='tel:" + properties["phoneNumber"]+"'>" + properties["phoneNumber"] + "</a></li>";
    markup += "<li><a href='https://www.google.com/maps/dir/Current+Location/" + properties["latitude"] +"," + properties["longitude"]+"'>" + properties["street"] + "</a></li>";
    markup += "<li><u><a href='" + properties["website"] + "' target='_blank'>" + properties["website"] + "</a></u></li></ul></div>";
    markup += "<div class='mobile-item-close image-rotate'><img src='static/img/downarrow.svg' width='28' height='28'></div>"

    return markup;
  }

  function getMarkerMobileContent(properties) {
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

		var beers = deal.dealDetails.filter(function(detail) { return detail.drinkCategory == 1; });
		var wines = deal.dealDetails.filter(function(detail) { return detail.drinkCategory == 2; });
		var liquors = deal.dealDetails.filter(function(detail) { return detail.drinkCategory == 3; });

	  markup += "<li class='mobile-item-deals-price'><ul>"


		if (beers.length > 0) {
			markup += "<li style='text-align: left'><img src='../static/img/beer.svg' width='20' height='20' /><p>" +
				formatDealDetail(beers.reduce(getBestDealDetail)) + "</p></li>";
		}

		if (wines.length > 0) {
			markup += "<li style='text-align: left'><img src='../static/img/wine.svg' width='20' height='20'/><p>" +
				formatDealDetail(wines.reduce(getBestDealDetail)) + "</p></li>";
		}

		if (liquors.length > 0) {
			markup += "<li style='text-align: left'><img src='../static/img/liquor.svg' width='20' height='20'/><p>" +
				formatDealDetail(liquors.reduce(getBestDealDetail)) + "</p></li>";
		}

	  return markup + '</ul></li></ul>';
  }

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
        
        if (deal.end && moment(deal.end,'HH:mm:ss') < moment(deal.start,'HH:mm:ss') && moment(selectedTime, "H:mm") < moment(deal.start,'HH:mm:ss')) {
            // Display previous day for deals crossing midnight
            yesterday = selectedDay > 1 ? selectedDay - 1 : 7;
            markup += "<h3>" + DAYS_OF_WEEK[yesterday - 1] + " " + start + " - " + end  + "</h3></li>";
        } else {
            markup += "<h3>" + DAYS_OF_WEEK[selectedDay - 1] + " " + start + " - " + end  + "</h3></li>";
        }

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

  function getDealMobileMarkup(dealDetails) {
    markup = "";
    
    dealDetails = dealDetails.sort(sortDealDetail);

	var beers = dealDetails.filter(function(detail) { return detail.drinkCategory == 1; });
	var wines = dealDetails.filter(function(detail) { return detail.drinkCategory == 2; });
	var liquors = dealDetails.filter(function(detail) { return detail.drinkCategory == 3; });

	if (beers.length > 0) {
      markup += "<ul><li>Beers</li><li>"
      $.map(beers, function(b, i) { markup += "<span>" + formatDealDetail(b) + " " + b.drinkName + "</span>"; });
      markup += "</li></ul>"
    }

	if (wines.length > 0) {
      markup += "<ul><li>Wines</li><li>"
      $.map(wines, function(b, i) { markup += "<span>" + formatDealDetail(b) + " " + b.drinkName + "</span>"; });
      markup += "</li></ul>"
    }

		if (liquors.length > 0) {
      markup += "<ul><li>Liquors</li><li>"
      $.map(liquors, function(b, i) { markup += "<span>" + formatDealDetail(b) + " " + b.drinkName + "</span>"; });
      markup += "</li></ul>"
    }

    return markup;
  }

  function mobileItemFull() {
    $('#mobile-item-showfull').hide();
    $("#mobile-item-short").find("p, img").hide();
    $(".mobile-item-deals-price").hide();

    $('#mobile-item-details').html(getMobileItemDetails(properties));
    $('#mobile-item-details').slideDown("slow");

    $('#mobile-item-details .mobile-item-close').swipe({
      swipe: function() {
        $('#mobile-item-details').hide();
        $('#mobile-item-info').slideUp("fast");
      }
    });
  }
  
  function sortDealDetail(a, b) {
      if (a.detailType !== b.detailType) {
          return a.detailType - b.detailType;
      } else if (a.detailType === 1) {
          return a.value - b.value;
      } else {
          return b.value - a.value;
      }
  }

	function getDealMarkup(dealDetails) {
        dealDetails = dealDetails.sort(sortDealDetail);
        
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

        ga('send', {
          hitType: 'event',
          eventCategory: 'Venues',
          eventAction: 'click',
          eventLabel: properties.name
        });
        
        
      // TODO Add capacity to display multiple deals
      var deal = properties.deals[0];

      var start = moment(deal.start,'HH:mm:ss').format('h:mm A');
      var end = deal.end ? moment(deal.end,'HH:mm:ss').format('h:mm A') : "CLOSE";

      if ($(window).width() < mediaScreenWidth) {
        $(".mobile-logo").hide();

        $("#mobile-item-info").show();
        $("#mobile-item-showfull").show();

        $("#mobile-item-short").html(getMarkerMobileContent(properties));

        $('#mobile-item-showfull').on('click', function() {
          mobileItemFull();
        });

        $("#mobile-item-short").swipe({
          swipeUp:function(event, direction, distance, duration, fingerCount, fingerData) {
            $('#mobile-item-info').slideUp("fast");
          },
          swipeDown:function(event, direction, distance, duration, fingerCount, fingerData) {
            mobileItemFull();
          }
        });

      } else {

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
		    $(".sliding").show();
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
            $("#location-address").attr("href", "https://www.google.com/maps/dir/Current+Location/" + properties["latitude"] +"," + properties["longitude"]);
          
            $("#location-phone-number").html(properties["phoneNumber"]);

            if (properties["happyHourWebsite"]){
                $("#location-website").html("Info Source");
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
            if (deal.end && moment(deal.end,'HH:mm:ss') < moment(deal.start,'HH:mm:ss') && moment(selectedTime, "H:mm") < moment(deal.start,'HH:mm:ss')) {  
                // Display previous day if past midnight
                var yesterday = selectedDay > 1 ? selectedDay - 1 : 7;
                $("#deal-time-frame").html(DAYS_OF_WEEK[yesterday - 1] + " " + start + " - " + end);
            } else {
                $("#deal-time-frame").html(DAYS_OF_WEEK[selectedDay - 1] + " " + start + " - " + end);
            }
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
      }
    })
});


metroLayer.on('layeradd', function(e) {
    var marker = e.layer,
        feature = e.layer.feature;

    marker.setIcon(L.icon({
        iconUrl: '../static/img/metro.png',
        iconSize: [16, 16]
    }));

    //popup content (name + line colors)
    var metroTooltip = "<div class='metro_info'><p>" + feature.properties.NAME + "</p>";
    var lineColor = feature.properties.LINE.split(","); //in case a station has multiple lines (red, blue, orange)
    for (i in lineColor) { // create a div for each line and assign a color to it
        metroTooltip = metroTooltip + "<div class='line' style='background-color:" + lineColor[i] + ";'></div>";
    }
    metroTooltip = metroTooltip + "</div>";

    marker.bindPopup(metroTooltip, {
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

// DAY AND TIME FILTERS
function initializeDayAndTime() {
	var now = moment();

	// Initialize day
	var dayFilter = $(".day");
	dayFilter.on("input", function(event) {
		selectedDay = $(this).val();
		$('.day_output').val(DAYS_OF_WEEK[selectedDay - 1]);

		reloadData();
	});

	selectedDay = now.day();
    if (selectedDay === 0) { 
        // Handle Sunday
        selectedDay = 7;
    }
    
	dayFilter.val(selectedDay);
	$('.day_output').val(DAYS_OF_WEEK[selectedDay - 1]);

	// Initialize time filter, but don't set time until activated

  $("#filter-by-hours, #filter-by-hours-desktop").on('change', function() {
    var time = $(this).parent().find('.time');
    var time_output = $(this).parent().find('.time_output');

    if ($(this).is(":checked")) {
      $(time).show();
		  $(time_output).show();
		  timeFilterActive = true;
    } else {
		  $(time).hide();
		  $(time_output).hide();
		  timeFilterActive = false;
		}

		reloadData();
	});


	var timeFilter = $('.time');
	//var timeFilter = $('.time:visible');
	timeFilter.attr('step', MINUTES_IN_HOUR / 2);
	timeFilter.attr('min', MIN_HOUR * MINUTES_IN_HOUR);
	timeFilter.attr('max', MAX_HOUR * MINUTES_IN_HOUR);

	//$(document).on('input', timeFilter, function(event) {
  timeFilter.on('input', function(event) {
		var totalMinutes = $(this).val();
		var hours = totalMinutes / MINUTES_IN_HOUR;
		if (hours > 24) hours -= 24;
		var minutes = totalMinutes % MINUTES_IN_HOUR;
		var selectedTimeMoment = moment({ hours: hours, minutes: minutes });
		selectedTime = selectedTimeMoment.format("H:mm");
		$('.time_output').text(selectedTimeMoment.format("hh:mm A"));

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
  $('.time_output').text(selectedTimeMoment.format("hh:mm A"));
	timeFilter.val(nowTotalMinutes);
}

// LOADING INDICATOR
function initializeLoadingIndicator() {
	var container = $(".loading-indicator-container")[0];
	loadingIndicator = new Spinner({
		color: "#FFFFFF",
		lines: 11,
		length: 41,
		width: 10,
		radius: 32,
		scale: 0.3
	}).spin(container);
}

// ZOOM FUNCTIONS

$("#overview-zoom, #mobile-overview-zoom").click(function() {
	$(".slider-arrow").attr("src", "../static/img/left-arrow.png");
	$(".right-side-bar").hide("slide", { direction: "right" }, 700);
	$(".sliding").animate({ right: "0"} , 700);
    
    $("#mobile-item-info").hide();
    $("#mobile-item-showfull").hide();
    $("#mobile-item-details").hide();
    
  if ($(window).width() < mediaScreenWidth) {
	  map.setView([38.907557, -77.028130],11,{zoom:{animate:true}});
  } else {
	  map.setView([38.907557, -77.028130],13,{zoom:{animate:true}});
  }

    if (hiddenNeighborhoodLayer) {
        selectedNeighborhood = null;
        reloadData();
        markerLayer.setGeoJSON([]);
        metroLayer.setGeoJSON([]);
        neighborhoodPolygonLayer.addLayer(hiddenNeighborhoodLayer);
        $(".neighborhood-label").show();

        // Hide sidebar
        $(".slider-arrow").attr("src", "../static/img/left-arrow.png");
        $(".right-side-bar").hide("slide", { direction: "right" }, 700);
        $(".sliding").animate({ right: "0"} , 700);
    }
});

// get current location in mobile mode
$('#current-location').on('click', function(){
  map.locate({setView: true, maxZoom: 15});
});

$('#mobile-settings').on('click', function(){
  $('#mobile-filters').slideDown("fast");
});

$('#mobile-filters .mobile-filters-close').on('click', function() {
  $(this).closest('#mobile-filters').slideUp("fast");
});

$(document).on('click', '#mobile-item-details .mobile-item-close', function() {
  $('#mobile-item-details').hide();
  $('#mobile-item-info').slideUp("fast");
});

$("#zoom-in").click(function() {
	var zoom = map.getZoom();
	map.setZoom(zoom + 1);
});

$("#zoom-out").click(function() {
	var zoom = map.getZoom();
	map.setZoom(zoom-1);
});
