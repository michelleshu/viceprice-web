/** ***MapBox**** */

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

/** *****Creating featureLayer and adding markers data******** */
var myLayer = L.mapbox.featureLayer().addTo(map);

myLayer.on('layeradd', function(e) {
<<<<<<< HEAD
    var marker = e.layer,
        feature = marker.feature;

    // Create custom popup content
    var popupContent =  '<h1>' + feature.properties.name + '<\/h1>';

    marker.bindPopup(popupContent,{
        closeButton: false,
        minWidth: 200
    });

    // Populate sidebar data on marker click
    marker.on('click', function() {
        $(".slider-arrow").attr("src", "../static/img/right-arrow.png");
        $(".right-side-bar").show("slide", { direction: "right" }, 700);
        $(".sliding").animate({ right: "25%"} , 700);
        $menu_visible=true
        var locationProperties = this.feature.properties;
        $("#location-name").html(locationProperties["name"]);
        $("#location-address").html(locationProperties["abbreviatedAddress"]);
        $("#location-phone-number").html(locationProperties["phone"]);
        $("#location-website").html(locationProperties["website"]);
        $("#location-website").attr("href", locationProperties["website"])
    })
=======
	var marker = e.layer, feature = marker.feature;

	// Create custom popup content
	var popupContent = '<h1>' + feature.properties.name + '<\/h1>';

	marker.bindPopup(popupContent, {
		closeButton : false,
		minWidth : 320
	});

	// Populate sidebar data on marker click
	marker.on('click', function() {
		var locationProperties = this.feature.properties;
		$("#location-name").html(locationProperties["name"]);
		$("#location-address").html(locationProperties["abbreviatedAddress"]);
		$("#location-phone-number").html(locationProperties["phone"]);
		$("#location-website").html(locationProperties["website"]);
		$("#location-website").attr("href", locationProperties["website"])
	})
>>>>>>> 321d16a25693b871b27bb9278f06511a8cdf4b77
});

var geoJsonData;
var neighborhoods
function fetchData(time, dayIndex) {
	$.get("/fetch/?time=" + time, { day: dayIndex }, function(data) {
		geoJsonData = data.json;
		neighborhoods = data.neighborhoods;
		updateHappyHours();
	});
}
function updateHappyHours(){
	$(neighborhoods).each(function(index,data){
	    $("div[neighborhood='"+data.neighborhood+"']").text(data.count)
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
	console.log(feature)
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
<<<<<<< HEAD
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
    myLayer.setGeoJSON(geoJsonData);
    myLayer.setFilter(function(f) {
        return f.properties["neighborhood"] === neighborhood;
    });
    return false;
=======
	css = document.getElementsByClassName("label");

	if (lastLayer === undefined) {
	}// do nothign
	else {
		dcnLayer.resetStyle(lastLayer);
		lastLayer.on({
			mousemove : mousemove,
			mouseout : mouseout,
			click : click
		});
		document.getElementById(lastLayer.feature.id).style.color = "#c8a45e";
		id = parseInt(lastLayer.feature.id) - 1;
		css[id].style.display = "block";
	}
	// Onclick: disable hover effect, remove label
	e.target.off({
		mousemove : false,
		mouseout : false,
		click : false
	});
	e.target.setStyle({
		fillOpacity : 0
	});
	id = parseInt(e.target.feature.id) - 1;
	css[id].style.display = "none";

	lastLayer = e.target;
	neighborhood = e.target.feature.properties.name;

	// OnClick: zoom into Polygon and show related markers
	map.fitBounds(getBounds(e.target));
	myLayer.setGeoJSON(geoJsonData);
	myLayer.setFilter(function(f) {
		return f.properties["neighborhood"] === neighborhood;
	});
	return false;
>>>>>>> 321d16a25693b871b27bb9278f06511a8cdf4b77
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

<<<<<<< HEAD
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
=======
function labelLocation(l, f) {
	// had to manually adjust the label location of few polygons
	return f.id == 10 ? L.latLng(38.912624, -77.042739) : f.id == 13 ? L
			.latLng(38.911011, -77.031959) : f.id == 14 ? L.latLng(38.918115,
			-77.030865) : f.id == 15 ? L.latLng(38.872020, -77.012171)
			: f.id == 16 ? L.latLng(38.889849, -76.943152) : f.id == 17 ? L
					.latLng(38.900487, -76.986962) : l.getBounds().getCenter();
>>>>>>> 321d16a25693b871b27bb9278f06511a8cdf4b77
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

<<<<<<< HEAD
//label css (customized to each neighborhood based on the polgon size, location etc)
function getHTML(e,d) {
    return e == 1 ? "<div class='map_labels' style='font-size:18px;'>North DC<div class='bar_num_labels' id='01'>( 16 ) <div/></div>" : //north DC
        e == 2  ?   "<div class='map_labels' style='font-size:18px;'>West DC<div class='bar_num_labels' id='02' >( 5 ) <div/></div>" :  //west dc
        e == 3  ?   "<div class='map_labels' style='font-size:16px;'>Friendship Heights<div class='bar_num_labels' id='03' style='text-align:right;'>( 33 ) </div></div>" :  //Friendship Heights
        e == 4  ?   "<div class='map_labels' style='font-size:12px;'>Adams <br/>Morgan<div class='bar_num_labels' id='04'>( 44 ) <div/></div>" :  //Adams Morgan
        e == 5  ?  "<div class='map_labels' style='font-size:18px;'>East DC<div class='bar_num_labels' id='05'>( 24 ) <div/></div>" :  //East dc
        e == 6  ?  "<div class='map_labels' style='font-size:16px;'>Shaw<div class='bar_num_labels' id='06'>( 18 )<div/></div>" :  //shaw
        e == 7  ?  "<div class='map_labels' style='font-size:16px;'>Capitol Hill<div class='bar_num_labels' id='07'>( 38 )<div/></div>" :  //Capitol Hill
        e == 8 ?  "<div class='map_labels' style='font-size:16px;'>Downtown<div class='bar_num_labels' id='08'>( 115 )<div/></div>" :  //downtown
        e == 9 ?  "<div class='map_labels' style='font-size:14px;'>Columbia <br/>Heights<div class='bar_num_labels' id='09'>( 20 )<div/></div>" :  //Columbia Heights
        e == 10 ? "<div class='map_labels' style='font-size:14px;'>Dupont <br/> Circle<div class='bar_num_labels' id='10'>( 76 )<div/></div>" :  //Dupont Circle
        e == 11 ? "<div class='map_labels' style='font-size:13px;'>Foggy Bottom<div class='bar_num_labels' id='11'>( 40 )<div/></div>" :  //foggy bottom
        e == 12 ? "<div class='map_labels' style='font-size:16px;'>Georgetown<div class='bar_num_labels' id='12'>( 28 )<div/></div>" :  //georgetown
        e == 13 ? "<div class='map_labels' style='font-size:12px;'>Logan <br/> Circle<div class='bar_num_labels' id='13'>( 21 )<div/></div>" :  //Logan Circle
        e == 14 ? "<div class='map_labels' style='font-size:14px;'>U Street<div class='bar_num_labels' id='14'>( 40 )<div/></div>" :  //u street
        e == 15 ? "<div class='map_labels' style='font-size:14px;'>Waterfront<div class='bar_num_labels' id='15'>( 10 )<div/></div>" : //Waterfront
        e == 16 ? "<div class='map_labels' style='font-size:18px;'>East of The River<div class='bar_num_labels' id='16'>( 2 )<div/></div>" : //South east
                  "<div class='map_labels' style='font-size:11px;'>H Street<div class='bar_num_labels' id='17'>( 27 )</div></div>"; //h street
=======
// label css (customized to each neighborhood based on the polgon size, location
// etc)
function getHTML(e, d) {
	return  "<div class='map_labels' style='font-size:18px;margin-top:30%; '>"
			+ d + "<div class='bar_num_labels' data-neighborhood='"+d+"' id='"+e+"'> <div/></div>"
																										// street
>>>>>>> 321d16a25693b871b27bb9278f06511a8cdf4b77
}

/** ****Zoom in / Zoom out and Neighborhood Zoom functions***** */
var zoom;

$("#neighboor-zoom").click(function() {
<<<<<<< HEAD
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
=======
	// zoom out to dc level
	map.setView([ 38.907557, -77.028130 ], 13, {
		zoom : {
			animate : true
		}
	});
	// reset polygon style
	dcnLayer.resetStyle(lastLayer);
	lastLayer.on({
		mousemove : mousemove,
		mouseout : mouseout,
		click : click
	});
	document.getElementById(lastLayer.feature.id).style.color = "#c8a45e";
	id = parseInt(lastLayer.feature.id) - 1;
	css[id].style.display = "block";
	// remove all markers
	myLayer.setFilter(function(f) {
		return false;
	});
>>>>>>> 321d16a25693b871b27bb9278f06511a8cdf4b77
});

$("#zoom-in").click(function() {
	zoom = map.getZoom();
	map.setZoom(zoom + 1);
});

$("#zoom-out").click(function() {
<<<<<<< HEAD
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
=======
	zoom = map.getZoom();
	map.setZoom(zoom - 1);
});

>>>>>>> 321d16a25693b871b27bb9278f06511a8cdf4b77
