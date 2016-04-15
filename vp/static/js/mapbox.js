/*****MapBox*****/
L.mapbox.accessToken = 'pk.eyJ1Ijoic2FsbWFuYWVlIiwiYSI6ImNpa2ZsdXdweTAwMXl0d20yMWVlY3g4a24ifQ._0c3U-A8Lv6C7Sm3ceeiHw';
var southWest = L.latLng(38.820993, -76.875833), northEast = L.latLng(
		39.004460, -77.158084), bounds = L.latLngBounds(southWest, northEast);

var map = L.map('map', {
	center : [ 38.907557, -77.028130 ],
	minZoom : 13,
	zoom : 13,
	zoomControl : false
});

L.mapbox.styleLayer('mapbox://styles/salmanaee/cikoa5qxo00gf9vm0s5cut4aa')
		.addTo(map);
map.setMaxBounds(bounds);

/*********create a custom marker ***********/
var restaurant_marker = L.icon({
    iconUrl: '../static/img/restaurant-marker.png',
    iconSize:     [44, 49], // size of the icon
    iconAnchor:   [20, 49],
    popupAnchor:  [3, -49]

});

var restaurant_marker_clicked = L.icon({
    iconUrl: '../static/img/restaurant-marker-clicked.png',
    iconSize:     [44, 49], // size of the icon
    iconAnchor:   [20, 49],
    popupAnchor:  [3, -49]

});

var bar_marker = L.icon({
    iconUrl: '../static/img/bar-marker.png',
    iconSize:     [44, 49], // size of the icon
    iconAnchor:   [20, 49],
    popupAnchor:  [3, -49]

});

var bar_marker_clicked = L.icon({
    iconUrl: '../static/img/bar-marker-clicked.png',
    iconSize:     [44, 49], // size of the icon
    iconAnchor:   [20, 49],
    popupAnchor:  [3, -49]

});

/******Creating featureLayer and adding markers data********/
var myLayer = L.mapbox.featureLayer().addTo(map);
var lastMarker;
myLayer.on('layeradd', function(e) {
    var marker = e.layer,
        feature = marker.feature;

    // Create custom popup content'
    var startTime = moment(deals[feature.properties.locationid].hours.start,'HH:mm').format("hh:mm A");
	var endTime = deals[feature.properties.locationid].hours.end
		? moment(deals[feature.properties.locationid].hours.end,'HH:mm').format("hh:mm A") : "CLOSE";
    var popupContent = dealsPrices(deals[feature.properties.locationid].details,feature.properties,startTime,endTime);

    marker.bindPopup(popupContent,{
        closeButton: false,
        minWidth: 290
    });

    marker.on('mouseover', function() {
    marker.openPopup();
    });

    marker.on('mouseout', function() {
    marker.closePopup();
    });

    if(feature.properties.super_category == "Bar")
    marker.setIcon(bar_marker);
	else
    marker.setIcon(restaurant_marker);

    // Populate sidebar data on marker click
        marker.on('click', function() {
        //highlight marker on onclick
        if(feature.properties.super_category == "Bar")
    		marker.setIcon(bar_marker_clicked);
		else
    	    marker.setIcon(restaurant_marker_clicked);
        //reset previous marker
        if(lastMarker === undefined){} // do nothing
    	else
        {
    	if(lastMarker.feature.properties.super_category == "Bar")
    		lastMarker.setIcon(bar_marker);
    	else
    		lastMarker.setIcon(restaurant_marker);
    	}
    	lastMarker=marker;
        $(".slider-arrow").attr("src", "../static/img/right-arrow.png");
        $(".right-side-bar").show("slide", { direction: "right" }, 700);
        $(".sliding").animate({ right: "25%"} , 700);
        $menu_visible=true

        var locationProperties = this.feature.properties;
        $("#location-name").html(locationProperties["name"]);

		var subCategories = locationProperties["subCategories"];
		$("#location-categories").html("");
		for (var i = 0; i < subCategories.length; i++) {
			$("#location-categories").append("<div class='category'>" + subCategories[i] + "</div>");
		}

        $("#location-address").html(locationProperties["abbreviatedAddress"]);
        $("#location-phone-number").html(locationProperties["phone"]);
        $("#location-website").html(locationProperties["website"]);
        $("#location-website").attr("href", locationProperties["website"]);
		// Populate deal info
		var startTime = moment(deals[locationProperties["locationid"]].hours.start,'HH:mm').format("hh:mm A");
		var endTime = deals[locationProperties["locationid"]].hours.end
			? moment(deals[locationProperties["locationid"]].hours.end,'HH:mm').format("hh:mm A") : "CLOSE";

        $("#specials-time-frame").html(startTime + " - " + endTime);
        $(".specials-div").append(populateDeals(deals[locationProperties["locationid"]].details));

        //Yelp Reviews 
        $.get("/yelpReviews/?loc_id="+locationProperties["locationid"],function(data){
        	yelp_api_response=data.response;
        	$("#name").html(yelp_api_response.username);
        	$("#profile_img").attr("src",yelp_api_response.user_img);
        	$("#rating_img").attr("src",yelp_api_response.overall_rating_img);
        	$("#user_rating_img").attr("src",yelp_api_response.user_rating_img);
        	$("#review_count").html(yelp_api_response.review_count + " reviews");
        	$("#excerpt").html("\" "+yelp_api_response.excerpt+" \"");
        	$("#readMore").html(parseInt(yelp_api_response.review_count)-1 + " more reviews ...");
        	$("#readMore").attr("href",yelp_api_response.url);
        });

		// Reset margins for cover photo
		$("#location-cover-photo").css("-webkit-clip-path", "inset(0px 0px)");
		$("#location-cover-photo").css("margin-top", "0px");
		$("#location-cover-photo").css("margin-bottom", "0px");
		$("#location-cover-photo").removeAttr("src");
	
		// Add cover photo if applicable
		if (locationProperties["coverPhotoSource"]) {

			$("#location-cover-photo").attr("src", locationProperties["coverPhotoSource"]);

			$("#location-cover-photo").load(function(){
				// Resize according to offset and Facebook cover photo proportions
				var originalWidth = $("#location-cover-photo").width();
				var originalHeight = $("#location-cover-photo").height();

				var clipTop = (locationProperties["coverPhotoYOffset"] * 0.01) * originalHeight;
				var clipLeft = (locationProperties["coverPhotoXOffset"] * 0.01) * originalWidth;
				var clipBottom = (originalHeight - clipTop) - 0.37 * (originalWidth - clipLeft);

				if (clipBottom < 0) {
					clipTop += clipBottom;
					clipBottom = 0;
				}

				$("#location-cover-photo").css("-webkit-clip-path", "inset(" + clipTop + "px 0px "  + clipBottom + "px "  + clipLeft + "px)");
				$("#location-cover-photo").css("margin-top", "-" + clipTop + "px");
				$("#location-cover-photo").css("margin-bottom", "-" + clipBottom + "px");
    		});
		}
    })
});

function populateDeals(items){
	$('div').remove('.dealDetails')
	var ulElement = "<div style='list-style: none;' class=dealDetails> "
	for (item in items){
		var type = item[0].toUpperCase() + item.slice(1)
			var image;
			if(item == "beer") image = "<span><img src='../static/img/beer.png'/>"
			if(item == "wine") image = "<span><img src='../static/img/wine.png'/>"
			if(item == "liqour") image =  "<span><img src='../static/img/drink.png'/>"
			ulElement = ulElement + image  +  type + "<ul  style=padding-left:10px; >"

			for(details in items[item]){
				var detailType;
				if (items[item][details]['detailType'] == 1) detailType = "$"+items[item][details]['value'] + " ";
				if (items[item][details]['detailType'] == 2) detailType = items[item][details]['value'] + "% off " 
				if (items[item][details]['detailType'] == 3) detailType = "$"+items[item][details]['value']+ " off "
				ulElement = ulElement + "<li><p>" +  detailType + items[item][details]['drinkName'] + "</p></li>"
			}
		ulElement = ulElement + "</ul></span>"
	}
	ulElement = ulElement + "</div>"
	return ulElement;
}

function dealsPrices(allDeals,properties,startTime,endTime){
	var ulElement = '<ul class="tooltip-info"> <li> <h1>' + properties.name + '</h1></li>'
					+'<li style="margin-bottom: 0.4rem;"> <h2>' + properties.subCategories + '</h2> <h3>' + startTime + ' - ' + endTime  + '</h3> </li><li>';
  
    for(deal in allDeals){
	    if(deal == "beer" && allDeals["beer"].length != 0)
	    	ulElement = ulElement + '<img src="../static/img/beer.png"/><p>'+lowestPrice(allDeals,deal)+'</p>';
		if(deal == "wine" && allDeals["wine"].length != 0)
	    	ulElement = ulElement +	'<img src="../static/img/wine.png"/><p>'+lowestPrice(allDeals,deal)+'</p>';
		if(deal == "liqour" && allDeals["liqour"].length != 0)
	    	ulElement = ulElement +	'<img src="../static/img/drink.png"/><p>'+lowestPrice(allDeals,deal)+'</p>';
	}

    ulElement = ulElement + '</li></ul>';
    return ulElement;
}

function lowestPrice(allDeals,deal){
	var lowestPrice;
	var prices=[];
    var prices_off=[];
    var percent_off=[];
	for(index in allDeals[deal]){ //look at all the items of type beer
				if(allDeals[deal][index]["detailType"] == 1) 
					prices.push(parseFloat(allDeals[deal][index]["value"]));
				if(allDeals[deal][index]["detailType"] == 3)//price off (2nd highest priority)
					prices_off.push(parseFloat(allDeals[deal][index]["value"]));
				if(allDeals[deal][index]["detailType"] == 2)//% off	
					percent_off.push(parseFloat(allDeals[deal][index]["value"]));
			}
			if(prices.length !=0){//price (highest priority) ==> find minumum price
				lowest_price="$"+Math.min.apply(Math, prices);
			}
			else if(prices_off.length !=0){
				lowest_price="$"+Math.max.apply(Math, prices_off)+" off";
			}
			else if(percent_off.length !=0){
				lowest_price=Math.max.apply(Math, percent_off)+"% off";
			}
	return lowest_price;
}

var geoJsonData;
var neighborhoods;
var deals;
function fetchData(time, dayIndex) {
	$.get("/fetch/?time=" + time, { day: dayIndex }, function(data) {
		geoJsonData = data.json;
		neighborhoods = data.neighborhoods;
		deals = data.deals;
		updateHappyHours();
		updateNeighborhoodData();
	});
}
function updateHappyHours(){
	$('.bar_num_labels').empty();
	$(neighborhoods).each(function(index,data){
	    $("div[data-neighborhood='"+data.neighborhood+"']").text("(" + data.count + ")")
	});
}
/** *DC Neighborhoods** */
var dcnLayer = L.geoJson(dcn, {
	style : getStyle,
	onEachFeature : onEachFeature
}).addTo(map);

var lastLayer, lastLabel, css, id, neighborhood;

function getStyle(feature) {
	return {
		weight : 2,
		opacity : 0.5,
		color : '#c8a45e',
		fillOpacity : 0.8,
		fillColor : 'rgb(35, 40, 43)',
	};
}

function onEachFeature(feature, layer) {
	// add neighborhood names to each polygon
	var label = L.marker(labelLocation(layer, feature), {
		icon : L.divIcon({
			className : 'label',
			html : getHTML(feature.id, feature.properties.name),
			iconSize : [ 100, 35 ]
		})
	}).addTo(map);

	// neighborhood/polygons related events (onClick, Hover etc.)
	layer.on({
		mousemove : mousemove,
		mouseout : mouseout,
		click : click
	});

	label
			.on(
					'mouseover',
					function(e) {
						document.getElementById(layer.feature.id).style.color = "rgb(35, 40, 43)";
						layer.setStyle({
							weight : 3,
							opacity : 0.5,
							fillColor : '#c8a45e',
							fillOpacity : 0.8,
						});
					});

	label.on('mouseout', function(e) {
		layer.fireEvent("mouseout");
	});

	label.on('click', function(e) {
		layer.fireEvent("click");
	});
}

function click(e) {
     $(".slider-arrow").attr("src", "../static/img/left-arrow.png");
     $(".right-side-bar").hide("slide", { direction: "right" }, 700);
     $(".sliding").animate({ right: "0"} , 700);
     $menu_visible=false;
    css=document.getElementsByClassName("label");

    if(lastLayer === undefined){}//do nothign
    else
        {
            dcnLayer.resetStyle(lastLayer);
            lastLayer.on({mousemove:mousemove, mouseout:mouseout,click:click});
            document.getElementById(lastLayer.feature.id).style.color="#c8a45e";
            id=parseInt(lastLayer.feature.id)-1;
            css[id].style.display="block";
        }
    //Onclick: disable hover effect, remove label
    e.target.off({mousemove:false, mouseout:false,click:false});
    e.target.setStyle({fillOpacity: 0});
    id=parseInt(e.target.feature.id)-1;
    css[id].style.display="none";

    lastLayer=e.target;
    neighborhood=e.target.feature.properties.name;

    //OnClick: zoom into Polygon and show related markers
     map.fitBounds(getBounds(e.target));
    updateNeighborhoodData()
    return false;
	}

	function updateNeighborhoodData(){
	myLayer.setGeoJSON(geoJsonData);
    myLayer.setFilter(function(f) {
        return f.properties["neighborhood"] === neighborhood;
    });
	}

function mousemove(e) {
	var layer = e.target;
	document.getElementById(layer.feature.id).style.color = "rgb(35, 40, 43)";

	// Highlight the neighborhood when mouse moves in the polygon
	layer.setStyle({
		weight : 3,
		opacity : 0.5,
		fillColor : '#c8a45e',
		fillOpacity : 0.8,
	});

	if (!L.Browser.ie && !L.Browser.opera) {
		layer.bringToFront();
	}
}

function mouseout(e) {
	dcnLayer.resetStyle(e.target);
	document.getElementById(e.target.feature.id).style.color = "#c8a45e";
}

function labelLocation (l,f){
    //had to manually adjust the label location of few polygons
    return f.id == 3 ? L.latLng(38.927526, -77.070867): //Freindship Heights
         f.id == 2 ? L.latLng(38.930150, -77.093441): //East DC
         f.id == 10 ? L.latLng(38.910328, -77.042245): //Dupont Circle
         f.id == 13 ? L.latLng(38.911111, -77.031433): //Logan Circle
         f.id == 14 ? L.latLng(38.916820, -77.030761): //u street
         f.id == 15 ? L.latLng(38.872020, -77.012171): //Waterfront
         f.id == 16 ? L.latLng(38.874071, -76.960545): //South east
         f.id == 17 ? L.latLng(38.900487, -76.986962):  //h street
          l.getBounds().getCenter();
}

function getBounds(e) {
	return e.feature.id == 1 ? L.latLngBounds([ 38.927309, -77.109718 ], [
			38.985176, -77.003803 ]) : e.feature.id == 3 ? L.latLngBounds([
			38.913442, -77.090021 ], [ 38.938577, -77.044096 ])
			: e.feature.id == 5 ? L.latLngBounds([ 38.902295, -77.046826 ], [
					38.960317, -76.939709 ]) : e.feature.id == 11 ? L
					.latLngBounds([ 38.894218, -77.060449 ], [ 38.907131,
							-77.036954 ]) : e.feature.id == 17 ? L
					.latLngBounds([ 38.886004, -77.018576 ], [ 38.914693,
							-76.965533 ]) : e.getBounds();
}


//label css (customized to each neighborhood based on the polygon size, location etc)
//some neghoborhoods has a customized css style (is there a better way to write this function)
function getHTML(e,d) {
	    return (e == 1) || (e==2) || (e==5) || (e==16) ? "<div class='map_labels' style='font-size:18px;'>"+d+"<div class='bar_num_labels' data-neighborhood='"+d+"' id='"+e+"'><div/></div>" : //north DC(16), west dc(5),east dc(24) and east of the river(2)
        (e == 3) || (e == 6) || (e == 7) || (e == 8) || (e == 12) ? "<div class='map_labels' style='font-size:16px;'>"+d+"<div class='bar_num_labels' data-neighborhood='"+d+"' id='"+e+"'><div/></div>" :  //Friendship Heights(33),shaw(18),Capitol hill (38), downtown(155), georgetown(28)
        e == 9 ?  "<div class='map_labels' style='font-size:14px;'>Columbia <br/>Heights<div class='bar_num_labels' data-neighborhood='"+d+"' id='"+e+"'><div/></div>" :  //Columbia Heights
        e == 10 ? "<div class='map_labels' style='font-size:14px;'>Dupont <br/> Circle<div class='bar_num_labels' data-neighborhood='"+d+"' id='"+e+"'><div/></div>":  //Dupont Circle
        e == 4  ? "<div class='map_labels' style='font-size:13px;'>Adams <br/>Morgan<div class='bar_num_labels' data-neighborhood='"+d+"' id='"+e+"'><div/></div>" :  //Adams Morgan
        e == 13 ? "<div class='map_labels' style='font-size:13px;'>Logan <br/> Circle<div class='bar_num_labels' data-neighborhood='"+d+"' id='"+e+"'><div/></div>" :  //Logan Circle
        (e == 14) || (e==15) ? "<div class='map_labels' style='font-size:14px;'>"+d+"<div class='bar_num_labels' data-neighborhood='"+d+"' id='"+e+"'><div/></div>":  //u street(40), Waterfront(10)
        "<div class='map_labels' style='font-size:13px;'>"+d+"<div class='bar_num_labels' data-neighborhood='"+d+"' id='"+e+"'><div/></div>" //foggy bottom(40) and h street (27)
        }

/*
function getHTML(e, d) {
	return  "<div class='map_labels' style='font-size:18px;margin-top:30%; '>"
			+ d + "<div class='bar_num_labels' data-neighborhood='"+d+"' id='"+e+"'> <div/></div>"
}*/

/****Zoom in / Zoom out and Neighborhood Zoom functions***** */
var zoom;

$("#neighboor-zoom").click(function() {
     $(".slider-arrow").attr("src", "../static/img/left-arrow.png");
     $(".right-side-bar").hide("slide", { direction: "right" }, 700);
     $(".sliding").animate({ right: "0"} , 700);
     $menu_visible=false;
  //zoom out to dc level
    map.setView([38.907557, -77.028130],13,{zoom:{animate:true}});
    //reset polygon style
    dcnLayer.resetStyle(lastLayer);
    lastLayer.on({mousemove:mousemove, mouseout:mouseout,click:click});
    document.getElementById(lastLayer.feature.id).style.color="#c8a45e";
    id=parseInt(lastLayer.feature.id)-1;
    css[id].style.display="block";
    //remove all markers
     myLayer.setFilter(function(f) {
            return false;
        });
});

$("#zoom-in").click(function() {
	zoom = map.getZoom();
	map.setZoom(zoom + 1);
});

$("#zoom-out").click(function() {
   zoom=map.getZoom();
  map.setZoom(zoom-1);
});

map.on('move', function() {
    zoom = map.getZoom();

    if (zoom == 13) {
      $(".slider-arrow").attr("src", "../static/img/left-arrow.png");
     $(".right-side-bar").hide("slide", { direction: "right" }, 700);
     $(".sliding").animate({ right: "0"} , 700);
     $menu_visible=false;
    }
});

