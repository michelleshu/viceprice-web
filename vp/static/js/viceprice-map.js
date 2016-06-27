// MAPBOX
L.mapbox.accessToken = 'pk.eyJ1Ijoic2FsbWFuYWVlIiwiYSI6ImNpa2ZsdXdweTAwMXl0d20yMWVlY3g4a24ifQ._0c3U-A8Lv6C7Sm3ceeiHw';
var map;
var neighborhoodPolygonLayer;
var markerLayer;
var hiddenNeighborhoodLayer;

// TIME FILTERS
var selectedDay = null;
var selectedTime = null;

// INITIALIZATION
var init = function() {
	loadMap();
	loadRegionalView();
};
init();

// LOAD MAP
function loadMap() {
	if (!map) {
		map = L.map('map', {
			center : [ 38.907557, -77.028130 ], //Initial geographical center of the map
			minZoom : 13, //Minimum zoom level of the map
			zoom : 13, //Initial map zoom
			attributionControl: false//remove attribution from map (added in the left menu instead)
		});
		
		//The map restricts the view to the given geographical bounds, bouncing the user back when he tries to pan outside the view
		var southWest = L.latLng(38.820993, -76.875833),
			northEast = L.latLng(39.004460, -77.158084),
			bounds = L.latLngBounds(southWest, northEast);
		map.setMaxBounds(bounds);
		
		// Use styleLayer to add a Mapbox style created in Mapbox Studio
		L.mapbox.styleLayer('mapbox://styles/salmanaee/cikoa5qxo00gf9vm0s5cut4aa')
			.addTo(map);
		
		markerLayer = L.mapbox.featureLayer().addTo(map);
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
		
		if (selectedTime) {
			queryString += "&time=" + selectedTime;
		}
	}
	$.get("/fetch_location_counts_by_neighborhood" + queryString, function(data) {
		var counts = JSON.parse(data["result"]);
		
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
		// e.target.off({ mousemove: false, mouseout: false, click: false});
		//     e.target.setStyle({fillOpacity: 0}); // remove polygon style
		//     id=parseInt(e.target.feature.id)-1;
		//     css[id].style.display="none"; //remove label
		//     lastLayer=e.target;
		//     neighborhood=e.target.feature.properties.name; 
		//     map.fitBounds(getBounds(e.target));//zoom into Polygon
		//  	cluster.clearLayers(); //clear any previous markr stored in the cluster group 
		//     updateNeighborhoodData(); //load related markers and metro stations 
		loadSingleNeighborhoodView(feature.properties.name);
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
	if (selectedDay) {
		queryString += "&day=" + selectedDay;
		
		if (selectedTime) {
			queryString += "&time=" + selectedTime;
		}
	}

	$.get("/fetch_filtered_deals" + queryString, function(data) {
		markerLayer.setGeoJSON(JSON.parse(data["result"]));
	});
}
// Custom Markers
var restaurant_marker = L.icon({
    iconUrl: '../static/img/restaurant-marker.png',
    iconSize:     [37, 42], // size of the icon in pixels
    iconAnchor:   [17, 42], //The coordinates of the "tip" of the icon (relative to its top left corner). 
    						//The icon will be aligned so that this point is at the marker's geographical location
    popupAnchor:  [3, -42]	//The coordinates of the point from which popups will "open", relative to the icon anchor.

});

var restaurant_marker_clicked = L.icon({
    iconUrl: '../static/img/restaurant-marker-clicked.png',
    iconSize:     [37, 42], 
    iconAnchor:   [17, 42],
    popupAnchor:  [3, -42]

});

var bar_marker = L.icon({
    iconUrl: '../static/img/bar-marker.png',
    iconSize:     [37, 42], 
    iconAnchor:   [17, 42],
    popupAnchor:  [3, -42]

});

var bar_marker_clicked = L.icon({
    iconUrl: '../static/img/bar-marker-clicked.png',
    iconSize:     [37, 42], 
    iconAnchor:   [17, 42],
    popupAnchor:  [3, -42]
});

/******Markers and Clusters********/
var myLayer = L.mapbox.featureLayer(); //markers layer (the actual data is not loaded yet)
//Create an empty cluster group (no markers are added yet)
var cluster = new L.MarkerClusterGroup({ polygonOptions: {
        //set opacity and fill opacity to zero to disable the L.Polygon (highlight)
        opacity: 0, 
        fillOpacity: 0
      }});
var lastMarker,//used for reseting the style of the previously clicked marker 
 	geoJsonData,neighborhoods,deals;


/*Once this layer is loaded do the following:
1)Create a custom popup that contains venues' info (name, subcategory, happhour time and best deals)
2)Bind each popup to its corresponding marker and show it on mouse hover
3)Set the marker's icon to either a bar or restaurant icon
4)Define marker-onClick function */
markerLayer.on('layeradd', function(e) {
    var marker = e.layer,
        feature = marker.feature;
		
	marker.setIcon(bar_marker);

    // //happy hour start and end time 
    // var startTime = moment(deals[feature.properties.locationid].hours.start,'HH:mm').format("hh:mm A"),
    // 	endTime = deals[feature.properties.locationid].hours.end
	// 	? moment(deals[feature.properties.locationid].hours.end,'HH:mm').format("hh:mm A") : "CLOSE";
	// 
	// //populate popup content (refer to the dealsPrices function for more info)
    // var popupContent = dealsPrices(deals[feature.properties.locationid].details,feature.properties,startTime,endTime);
	// 
    // //bin popup content to marker 
    // marker.bindPopup(popupContent,{
    //     closeButton: false,  //Controls the presence of a close button in the popup
    //     minWidth: 340
    // });
	// 
    // marker.on('mouseover', function() {
    // marker.openPopup();
    // });
	// 
    // marker.on('mouseout', function() {
    // marker.closePopup();
    // });
	// 
    // //set up marker icon based on venue type (either bar or restaurant)
    // if(feature.properties.super_category == "Bar")
    // marker.setIcon(bar_marker);
	// else
    // marker.setIcon(restaurant_marker);

    /*If a marker is clicked do the following:
	1) Highlight the marker to indicate that it's clicked
	2) Reset the style of the previously clicked marker 
	3) Show the right nav menu
	4) populate that menu with venue info 
    */
    marker.on('click', function() {
    	//highlight marker on click
        if(feature.properties.super_category == "Bar")
    		marker.setIcon(bar_marker_clicked);
		else
    	    marker.setIcon(restaurant_marker_clicked);

        //reset the style of the previously clicked marker
        if(lastMarker != undefined){
    		if(lastMarker.feature.properties.super_category == "Bar")
    			lastMarker.setIcon(bar_marker);
    		else
    			lastMarker.setIcon(restaurant_marker);
    	}
    	lastMarker=marker;

    	//Show the right menu
        $(".slider-arrow").attr("src", "../static/img/right-arrow.png"); // change the arrow direction to indicate that it could be clicked to hide the menu 
        $(".right-side-bar").show("slide", { direction: "right" }, 700); //Slide the menu out (direction: right, duration: 700 milisec) 
        $(".sliding").animate({ right: "25%"} , 700);// slide the gold bar to the right 
        $menu_visible=true

        //populate the menu with venue info 
        var locationProperties = this.feature.properties,
        	subCategories = locationProperties["subCategories"],
        	startTime = moment(deals[locationProperties["locationid"]].hours.start,'HH:mm').format("hh:mm A"),
			endTime = deals[locationProperties["locationid"]].hours.end
			? moment(deals[locationProperties["locationid"]].hours.end,'HH:mm').format("hh:mm A") : "CLOSE";

        // Reset margins for cover photo
		$("#location-cover-photo").css("-webkit-clip-path", "inset(0px 0px)");
		$("#location-cover-photo").css("margin-top", "0px");
		$("#location-cover-photo").css("margin-bottom", "0px");
		$("#location-cover-photo").removeAttr("src");
		$("#location-cover-photo").attr("data-x-offset", locationProperties["coverPhotoXOffset"]);
		$("#location-cover-photo").attr("data-y-offset", locationProperties["coverPhotoYOffset"]);

		// Add cover photo if applicable
		if (locationProperties["coverPhotoSource"]) {
			$("#location-cover-photo").attr("src", locationProperties["coverPhotoSource"]);
		}

		//Add venue name and Category
        $("#location-name").html(locationProperties["name"]); 
		$("#location-categories").html("");
		//Sub categories will be displayed in this order : Sub-Cat 1 | Sub-Cat 2 | Sub-Cat 3 etc.
		for (var i = 0; i < subCategories.length; i++) {
			if(i == 0) //add a left margin for the first element
				$("#location-categories").append("<div class='category' style='margin-left:1rem;'>" + subCategories[i] + "</div>");
			else
				$("#location-categories").append("<div class='category'>" + subCategories[i] + "</div>");
			
			if(i != (subCategories.length-1)) //Don't add '|' at the end of the last element
				$("#location-categories").append(" | ");
		}

        $("#location-address").html(locationProperties["abbreviatedAddress"]);
        $("#location-phone-number").html(locationProperties["phone"]);
        
        ///--This is to show users where we got our data from-->
        
        if (locationProperties["happyHourWebsite"]){
            $("#location-website").html("Source of Info");
            $("#location-website").attr("href", locationProperties["happyHourWebsite"]);  
        }
        else { 
            $("#location-website").html("Website");
            $("#location-website").attr("href", locationProperties["website"]);
            
        }
        
		$(".rev-hr").css("display","block");
		$(".icon-globe").css("display","inline");
		$(".icon-phone").css("display","inline");
		$(".icon-home").css("display","inline");
		// Populate deal info
        $("#specials-time-frame").html(startTime + " - " + endTime);
        $(".specials-div").append(populateDeals(deals[locationProperties["locationid"]].details));
        $("#yelp_log").attr("src","../static/img/yelp-logo-small.png");
        $(".rev").html("Reviews");
        //Yelp Reviews 
        $.get("/yelpReviews/?loc_id="+locationProperties["locationid"],function(data){
        	yelp_api_response=data.response; // refer to yelpReview on views.py for more details
        	$("#rating_img").attr("src",yelp_api_response.overall_rating_img); //overall rating
        	$("#review_count").html(yelp_api_response.review_count + " reviews");// number of reviews 
        	$("#name").html(yelp_api_response.username); //username
        	$("#profile_img").css("display","inline-block");
        	$("#profile_img").attr("src",yelp_api_response.user_img);
        	$("#excerpt").html("\" "+yelp_api_response.excerpt+" \"");
        	$("#readMore").html(parseInt(yelp_api_response.review_count)-1 + " more reviews ..."); //number of remaining reviews
        	$("#readMore").attr("href",yelp_api_response.url); //venue's page on yelp 
        });
    })
});

function populateDeals(item){
	items = $.extend(true, {}, item);
	$('div').remove('.dealDetails')
	var ulElement = "<div style='list-style: none;' class=dealDetails> "
	for (item in items){
		var type = item[0].toUpperCase() + item.slice(1)
			var image;
			if (items[item].length != 0) {
				if(item == "beer") image = "<span><img src='../static/img/beer.png'/>"
				if(item == "wine") image = "<span><img src='../static/img/wine.png'/>"
				if(item == "liquor") image =  "<span><img src='../static/img/liquor.png'/><p id='drink_type'> Cocktails/"
				ulElement = ulElement + image  +  "<p id='drink_type'>" + type + ": </p><ul  style=padding-left:10px; >" 
			}

			items[item].sort(function(a, b){
			    return a.value - b.value;
			});
			var group = groupByType(items[item])
			for(g in group){
				var dealDetails  =	groupByValue(group[g])
				for(details in dealDetails){
					var detailType;
					if (dealDetails[details]['detailType'] == 1) detailType = "$"+ dealDetails[details]['value'] + " ";
					if (dealDetails[details]['detailType'] == 2) detailType = dealDetails[details]['value'] + "% off "
					if (dealDetails[details]['detailType'] == 3) detailType = "$"+ dealDetails[details]['value']+ " off "
					ulElement = ulElement + "<li><p>" +  detailType + dealDetails[details]['drinkName'] + "</p></li>"
					}
			}
		ulElement = ulElement + "</ul></span>"
	}
	ulElement = ulElement + "</div>"
	return ulElement;
}

function groupByValue(item){
	var stack = item;
	var dealDetails ={};
	var e;
	while(stack.length > 0){
		e = stack.pop();
		if(!dealDetails[e.value]){
			dealDetails[e.value] = e;
			}
		else{
			dealDetails[e.value].drinkName = dealDetails[e.value].drinkName + ", "+ e.drinkName
			}
		}
	return dealDetails
}

function groupByType(item){
	var stack = item;
	var dealDetails ={};
	var e;
	while(stack.length > 0){
		e = stack.pop();
		if(!dealDetails[e.detailType]) dealDetails[e.detailType] = []
			dealDetails[e.detailType].push(e)
			}
	   return dealDetails
}

/*This function returns the popup content:
 1) The venue anme
 2) Venue sub category
 3) Happy Hour start and end time 
 4) The cheapest deals (for wine, liquor and beer)*/  
function dealsPrices(allDeals,properties,startTime,endTime){
	var ulElement = '<ul class="tooltip-info"> <li> <h1>' + properties.name + '</h1></li><li id="subCategories">';
		//if a venue contains one or more subcategories display one of them
		if(properties.subCategories[0] != undefined)  
			ulElement = ulElement + '<h2>' + properties.subCategories[0] + '</h2>';
		
		ulElement = ulElement + '<h3>' + startTime + ' - ' + endTime  + '</h3> </li><li class="cheapest_price"> Best Deal: ';
  	
  	//Display the cheapest deals for wine, beer and liquor (if such data exists)
    for(deal in allDeals){
	    if(deal == "beer" && allDeals["beer"].length != 0)
	    	ulElement = ulElement + '<img src="../static/img/beer.png"/><p>'+lowestPrice(allDeals,deal)+'</p>';
		if(deal == "wine" && allDeals["wine"].length != 0)
	    	ulElement = ulElement +	'<img src="../static/img/wine.png"/><p>'+lowestPrice(allDeals,deal)+'</p>';
		if(deal == "liquor" && allDeals["liquor"].length != 0)
	    	ulElement = ulElement +	'<img src="../static/img/liquor.png"/><p>'+lowestPrice(allDeals,deal)+'</p>';
	}

    ulElement = ulElement + '</li></ul>';
    return ulElement;
}

function lowestPrice(allDeals,deal){
	var lowestPrice;
	var prices=[]; //$
    var prices_off=[]; //$ off
    var percent_off=[]; //% off
	for(index in allDeals[deal]){ //look at all the items of type (beer,wine or liquor)
				if(allDeals[deal][index]["detailType"] == 1)//$
					prices.push(parseFloat(allDeals[deal][index]["value"]));
				if(allDeals[deal][index]["detailType"] == 2)//% off
					percent_off.push(parseFloat(allDeals[deal][index]["value"]));
				if(allDeals[deal][index]["detailType"] == 3)//$ off
					prices_off.push(parseFloat(allDeals[deal][index]["value"]));
			}

			/*When choosing a minimum price for each deal:
			- the priority is: 
			- actual price in $
			- then the $ off 
			- then % off */
			if(prices.length !=0){ 
				lowest_price="$"+Math.min.apply(Math, prices); // find minimum $
			}
			else if(prices_off.length !=0){
				lowest_price="$"+Math.max.apply(Math, prices_off)+" off"; // find minimum $ off
			}
			else if(percent_off.length !=0){
				lowest_price=Math.max.apply(Math, percent_off)+"% off"; // find minimum % off
			}
	return lowest_price;
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

/***DC Neighborhoods***/
// var dcnLayer = L.geoJson(dcn, { //dcn is defined in dcn.js
// 	style : getStyle,
// 	onEachFeature : onEachFeature
// }).addTo(map);
// 
// var lastLayer, lastLabel, //those 2 are used to reset the previously selected neighborhood
// 	css, id, neighborhood; 
// 


// /*On Polygon/label click do the following:
// 1) if the right menu is shown, hide it
// 2) reset the style of any previously selected neighborhood
// 3) remove all css related style from the newly selected neighborhood and disable its related events 
// 4) zoom into the newly selected neighborhood
// 5) load markers and metro stations related to the selected neighborhood*/
// function click(e) {
//      $(".slider-arrow").attr("src", "../static/img/left-arrow.png");
//      $(".right-side-bar").hide("slide", { direction: "right" }, 700);
//      $(".sliding").animate({ right: "0"} , 700);
//      $menu_visible=false;
// 
//     css=document.getElementsByClassName("label");
// 
//     /*if anohter neighborhood is already selected:
//     - reset its polygon style 
//     - enable its events (mouseover,mouseout and click
//     - reset its label's style (color, show the label)*/
//     if(lastLayer != undefined){
//             dcnLayer.resetStyle(lastLayer);
//             lastLayer.on({mousemove:mousemove, mouseout:mouseout,click:click});
//             document.getElementById(lastLayer.feature.id).style.color="#c8a45e";
//             id=parseInt(lastLayer.feature.id)-1;
//             css[id].style.display="block";
//         }
// 
//     //Onclick: disable all events
//     e.target.off({mousemove:false, mouseout:false,click:false});
//     e.target.setStyle({fillOpacity: 0}); // remove polygon style
//     id=parseInt(e.target.feature.id)-1;
//     css[id].style.display="none"; //remove label
//     lastLayer=e.target;
//     neighborhood=e.target.feature.properties.name; 
//     map.fitBounds(getBounds(e.target));//zoom into Polygon
//  	cluster.clearLayers(); //clear any previous markr stored in the cluster group 
//     updateNeighborhoodData(); //load related markers and metro stations 
// 	}
// 
// 	function updateNeighborhoodData(){
// 	myLayer.setGeoJSON(geoJsonData); //load markers data to myLayer
// 	metroLayer.setGeoJSON(metro); //load metro station data to metroLayer (//metro is defined in dc-metro.js)
//     if(neighborhood_on){
//     myLayer.setFilter(function(f) { //filter this layer so it only contains the markers within a specfic neighborhood
//         return f.properties["neighborhood"] === neighborhood;});
//     metroLayer.setFilter(function(f) {//filter this layer so it only contains the stations within a specfic neighborhood
//     	return f.properties["NEIGHBORHOOD"] === neighborhood;});
// 	}
//     else{
//     	clearNeighborhood();
//     }
// }
// 
// 
// //clear neighborhood
// var neighborhood_on=true;
// function clearNeighborhood(){
// 	map.removeLayer(dcnLayer);
// 	$(".map_labels").hide();
// 	$(".bar_num_labels").hide();
// 
//     myLayer.setFilter(function() { 
//         return true;
//     });
//     cluster.clearLayers();
//     cluster.addLayer(myLayer).addTo(map);
//     neighborhood_on=false;	
// }
// 
// //add neighborhood
// function addNeighborhood(){
// 	map.setView([38.907557, -77.028130],13,{zoom:{animate:true}});
// 	cluster.clearLayers();
//     myLayer.setFilter(function(f) {
//             return false;
//         });
//     metroLayer.setFilter(function(f) {
//             return false;
//         });
// 	map.addLayer(dcnLayer);
// 	$(".map_labels").show();
// 	$(".bar_num_labels").show();
//     neighborhood_on=true;
// }

/****Zoom in/Zoom out and Neighborhood Zoom functions ****/
var zoom;
/*If the neighborhood button is clicked, do the following:
1) if the right menu is shown, hide it
2) reset the style of any previously selected neighborhood
3) zoom out to DC level
4) remove markers,metro stations and clusters*/
$("#neighboor-zoom").click(function() {
     $(".slider-arrow").attr("src", "../static/img/left-arrow.png");
     $(".right-side-bar").hide("slide", { direction: "right" }, 700);
     $(".sliding").animate({ right: "0"} , 700);
     $menu_visible=false;

     if(neighborhood_on){
    //reset polygon style
    dcnLayer.resetStyle(lastLayer);
    lastLayer.on({mousemove:mousemove, mouseout:mouseout,click:click});
    document.getElementById(lastLayer.feature.id).style.color="#c8a45e";
    id=parseInt(lastLayer.feature.id)-1;
    css[id].style.display="block";
    //remove all markers
    cluster.clearLayers();
     myLayer.setFilter(function(f) {
            return false;
        });
     metroLayer.setFilter(function(f) {
            return false;
        });
	}
    //zoom out to dc level
    map.setView([38.907557, -77.028130],13,{zoom:{animate:true}});
    
});

$("#zoom-in").click(function() {
	zoom = map.getZoom();
	map.setZoom(zoom + 1);
});

$("#zoom-out").click(function() {
   zoom=map.getZoom();
  map.setZoom(zoom-1);
});

/*If the zoom level of the map changes, do the following:
- if the zoom level is 13, hide the right menu
- if the zoom level is 17 or 18, disable the cluster feature and show unclustered markers
- if the zoom level is 13-16, cluster feature kicks in
*/
// map.on('move', function() {
//     zoom = map.getZoom();
//     if (zoom == 13) {
//      $(".slider-arrow").attr("src", "../static/img/left-arrow.png");
//      $(".right-side-bar").hide("slide", { direction: "right" }, 700);
//      $(".sliding").animate({ right: "0"} , 700);
//      $menu_visible=false;
//  	}
// 
//  	if(!neighborhood_on){
//  		if(zoom ==13)
//     		metroLayer.setFilter(function(f) {return false;});
// 		else
//     	metroLayer.setFilter(function() {return true;});
//     }
// 
//     if((zoom == 17) || (zoom ==18))
//     {
//     	cluster.clearLayers();
//     	map.addLayer(myLayer);
//     }
//     else
//     {
//     	map.removeLayer(myLayer);
//     	cluster.addLayer(myLayer);
//     	map.addLayer(cluster);
//     }
// });