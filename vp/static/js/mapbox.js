/*****MapBox*****/
L.mapbox.accessToken = 'pk.eyJ1Ijoic2FsbWFuYWVlIiwiYSI6ImNpa2ZsdXdweTAwMXl0d20yMWVlY3g4a24ifQ._0c3U-A8Lv6C7Sm3ceeiHw';

var southWest = L.latLng(38.820993, -76.875833), northEast = L.latLng(39.004460, -77.158084),
  bounds = L.latLngBounds(southWest, northEast);

var map = L.mapbox.map('map');

L.mapbox.styleLayer('mapbox://styles/salmanaee/cikoa5qxo00gf9vm0s5cut4aa').addTo(map);

map.setView([38.907557, -77.028130]);
map.setMaxBounds(bounds);
map.setZoom(13);

/*************************/
var clusterGroup = new L.MarkerClusterGroup({polygonOptions: {
    fillColor: 'white',
    color: 'white',
    weight: 2,
    opacity: 1,
    fillOpacity: 0.3
  }
});//end of cluster

$.get("../fetch/", function(data) {
  geoJsonData = data.json;
  var goeJsonlayer = L.geoJson(geoJsonData, {
    onEachFeature : function(feature, layer) {
      console.log(feature);
      layer.setIcon(L.divIcon(feature.properties.icon));
      var content = '<div class="tooltip"><h1>' + feature.properties.name + '<\/h1>' + '<p>' + feature.properties.phone + '<br \/>' + feature.properties.website + '<\/p> <\/div>';
      layer.bindPopup(content);
    }
  });
  //map.addLayer(goeJsonlayer);
  //map.addLayer(clusterGroup);
});

  /***DC Neighborhoods***/

var dcnLayer = L.geoJson(dcn,  {
  style: getStyle,
  onEachFeature: onEachFeature
}).addTo(map);

var label,div,currentZoom;

function getStyle(feature) {
  return {
    weight: 2,
    opacity: 0.5,
    color: '#c8a45e',
    fillOpacity: 0.8,
    fillColor: 'rgb(35, 40, 43)',
  };
}

function onEachFeature(feature, layer) {
  layer.on({
    mousemove: mousemove,
    mouseout: mouseout,
  click: zoomToFeature
  });

  label = L.marker(layer.getBounds().getCenter(), {
    icon: L.divIcon({
      className: 'label',
      html: getHTML(feature.id,feature.properties.name),
      iconSize: [100, 35]
    })
  }).addTo(map);
};


/*map.on('zoomend', function() {
currentZoom = map.getZoom();
$('.map_labels').css('font-size', currentZoom/1.5);
});*/

function zoomToFeature(e) {
  map.fitBounds(e.target.getBounds());
}

function mousemove(e) {
  var layer = e.target;
  layer.setStyle({
    weight: 3,
    opacity: 0.5,
    fillColor:'#c8a45e',
    fillOpacity: 0.8
  });
  if (!L.Browser.ie && !L.Browser.opera) {
    layer.bringToFront();
  }
}

function mouseout(e) {
  dcnLayer.resetStyle(e.target);
}

function getHTML(e,d) {
  return e == 1 ? "<div class='map_labels' style='font-size:18px;margin-top:30%;'>" + d +"</div>" : //north DC
          e == 2  ?"<div class='map_labels' style='font-size:18px;margin-left:30%;'>" + d +"</div>" :  //west dc
          e == 3  ? "<div class='map_labels' style='font-size:16px;'>" + d +"</div> " :  //Friendship Heights
          e == 4  ? "<div class='map_labels' style='font-size:14px;'>" + d +"</div>" :  //Adams Morgan
          e == 5  ?"<div class='map_labels' style='font-size:18px;margin-right:30%;'>" + d +"</div>" :  //East dc
          e == 6  ? "<div class='map_labels' style='font-size:16px;'>" + d +"</div>" :  //shaw
          e == 7  ? "<div class='map_labels' style='font-size:16px;'>" + d +"</div>" :  //Capitol Hill
          e == 8 ? "<div class='map_labels' style='font-size:16px;margin-top:15%;'>" + d +"</div>" :  //downtown
          e == 9 ? "<div class='map_labels' style='font-size:14px;'>" + d +"</div>" :  //Columbia Heights
          e == 10 ? "<div class='map_labels' style='font-size:14px;width:50px;margin-left:30%;margin-top:10%;'>" + d +"</div>" :  //Dupont Circle
          e == 11 ? "<div class='map_labels' style='font-size:16px;'>" + d +"</div>" :  //foggy bottom
          e == 12 ? "<div class='map_labels' style='font-size:16px;'>" + d +"</div>" :  //georgetown
          e == 13 ? "<div class='map_labels' style='font-size:14px;width:50px;margin-left:25%;'>" + d +"</div>" :  //Logan Circle
          e == 14 ? "<div class='map_labels' style='font-size:14px;margin-top:10%;'>" + d +"</div>" :  //u street
          e == 15 ? "<div class='map_labels' style='font-size:14px;margin-rigth:50%;'>" + d +"</div>" : //Waterfront
          e == 16 ? "<div class='map_labels' style='font-size:18px;text-align:left;'>" + d +"</div>" : //South east
          "<div class='map_labels' style='font-size:14px;margin-top:10%;'>" + d +"</div>"; //h street
}
