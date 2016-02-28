<?php
//------ DATABASE CONNECTION --------//
mysql_connect('localhost','root','')
or die ("Unable to connect to database");

mysql_select_db('viceprice')
or die ("Unable to select database");


$sql = "SELECT * FROM vp_location";
$result = mysql_query($sql);

$number = mysql_numrows($result);

$i = 0;

if ($number == 0)
	print "Error - No records found";
elseif ($number > 0)
	{
	print"<script type='text/javascript'>var listResults = [";

	while ($i < $number)
		{
		$name = mysql_result($result, 24, "name");
		$website = mysql_result($result, $i, "website");
		$phone = mysql_result($result, $i, "formattedPhoneNumber");
		$lat = mysql_result($result, $i, "latitude");
		$long = mysql_result($result, $i, "longitude");

		print"{name:'$name',";
	    print"website:'$website',";
	    print"phone:'$phone',";
	    print"valueLat: '$lat',";
	    print"valueLong: '$long'},";
		$i++;
		}
		print"];</script>";
	}

mysql_free_result($result);
mysql_close();
?>

<html>
<head>
<meta name='viewport' content='initial-scale=1,maximum-scale=1,user-scalable=no' />
 <link rel="stylesheet" type="text/css" href="css/component.css" />
 <link href='https://api.mapbox.com/mapbox.js/v2.3.0/mapbox.css' rel='stylesheet' />
 <link rel="stylesheet" type="text/css" href="https://fonts.googleapis.com/css?family=Montserrat">
     <!-- JS -->
<script src='https://api.mapbox.com/mapbox.js/v2.3.0/mapbox.js'></script>
<script src='cluster.js'></script>
<style>
  body { margin:0; padding:0; }
  #map { position:absolute; top:0; bottom:0; width:100%; }
  .pin {
  width: 35px;
  height: 35px;
  border-radius: 50% 50% 50% 10%;
  border:solid white 3.5px;
  background: #89849b;
  position: absolute;
  transform: rotateY(30deg);
  left: 50%;
  top: 50%;
  margin: -20px 0 0 -20px;
  }
</style>
</head>
<body>
<div id='map'></div>
<script>
L.mapbox.accessToken = 'pk.eyJ1Ijoic2FsbWFuYWVlIiwiYSI6ImNpa2ZsdXdweTAwMXl0d20yMWVlY3g4a24ifQ._0c3U-A8Lv6C7Sm3ceeiHw';

var geoJsonData = [];
var southWest = L.latLng(38.820993,-76.875833),
    northEast = L.latLng(39.004460,-77.158084),
    bounds = L.latLngBounds(southWest, northEast);
    
    var map = L.mapbox.map('map');

//loop through the listResults to build individual geoJson features
for (var i = 0; i < listResults.length; i++) {
    var result = listResults[i];
    geoJsonData.push(
        {
         "type": "Feature",
         "geometry": {
         "type": "Point",
         "coordinates": [result.valueLong, result.valueLat]
         },
         "properties": {
         "name": result.name,
         "website": result.website, 
         "phone": result.phone,
         "icon": {
	        "className": "pin", // class name to style
	        "iconSize": null // size of icon, use null to set the size in CSS
      		}
         }
        }
    );

}

    L.mapbox.styleLayer('mapbox://styles/mapbox/dark-v8').addTo(map);
    map.setView([38.907557, -77.009014], 13)
    .setMaxBounds(bounds);

    var clusterGroup = new L.MarkerClusterGroup({polygonOptions: {
            fillColor: 'white',
            color: 'white',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.3
        }
     });//end of cluster

    var goeJsonlayer=L.geoJson(geoJsonData,{
      onEachFeature: function (feature, layer) {
        layer.setIcon(L.divIcon(feature.properties.icon));
         var content = '<div class="tooltip"><h1>'+ feature.properties.name +'<\/h1>' +
        '<p>' + feature.properties.phone + '<br \/>' +
         feature.properties.website + '<\/p> <\/div>';
        layer.bindPopup(content);
      }
    });
 	
 	clusterGroup.addLayer(goeJsonlayer);
 	map.addLayer(clusterGroup);


</script>
</body>
</html>