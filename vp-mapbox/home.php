<!DOCTYPE html>
<html>
<head>
  <meta charset=utf-8 />
 <title> VicePrice </title>
 <meta name='viewport' content='initial-scale=1,maximum-scale=1,user-scalable=no' />
    <!-- css -->
  
    <link rel="stylesheet" type="text/css" href="css/component.css" />
    <link href='https://api.mapbox.com/mapbox.js/v2.3.0/mapbox.css' rel='stylesheet' />
    <link rel="stylesheet" type="text/css" href="https://fonts.googleapis.com/css?family=Montserrat">
     <!-- JS -->
    <script src='https://api.mapbox.com/mapbox.js/v2.3.0/mapbox.js'></script>
    <script src='cluster.js'></script>
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
  <style>
    body { font-family:'Montserrat'; margin:0; padding:0; }
    .map { position:absolute; top:0; bottom:0; width:100%; }
  </style>
</head>
<body>
    <div class='grid'>
        <div id='map' class='map' style='position:fixed;'></div>

        <div class='left-side-bar'>
            <div class='search-div'>
                <p> SEARCH </p> 
                <form method="get" action="/search" id="search">
                <input name="q" type="text" size="40" />
                </form>
            </div>
            <div class='hours-div'>
                <p> HOURS </p>  
            </div>
            <div class='location-div'>
                <p> LOCATION: </p>
                  
            </div>
            <div class='venues-div'>
                <p> VENUES: </p>  

                <input type="checkbox" id="dive">
                <label for="dive"><i class="v-icon"></i>
                <span class="label">Dive Bar</span></label>

                <input type="checkbox" id="gay">
                <label for="gay"><i class="v-icon"></i>
                <span class="label">Gay Bar</span></label>

                <input type="checkbox" id="hotel">
                <label for="hotel"><i class="v-icon"></i>
                <span class="label">Hotel</span></label>

                <input type="checkbox" id="general">
                <label for="general"><i class="v-icon"></i>
                <span class="label">General</span></label>
                
                <input type="checkbox" id="fancy">
                <label for="fancy"><i class="v-icon"></i>
                <span class="label">Fancy</span></label>

                <input type="checkbox" id="sports">
                <label for="sports"><i class="v-icon"></i>
                <span class="label">Sports</span></label>
                
                <input type="checkbox" id="pub">
                <label for="pub"><i class="v-icon"></i>
                <span class="label">Pub</span></label>
                
                <input type="checkbox" id="nightclub">
                <label for="nightclub"><i class="v-icon"></i>
                <span class="label">Nightclub</span></label>
                
                <input type="checkbox" id="piano" value="Hi">
                <label for="piano"><i class="v-icon"></i>
                <span class="label">Piano</span></label>
                
                <input type="checkbox" id="hookah">
                <label for="hookah"><i class="v-icon"></i>
                <span class="label">Hookah</span></label>

            </div>
            <div class="about-contact-us"> 
                <a href="url">About</a> 
                <a href="url">Contact Us</a> 
                <a href="url">Owner?</a> 
            </div>
        </div>

        <div class='right-side-bar'> 
            <img src="img/sushi.jpg" width="300" height="170px"/>
            <div class="bar-info-div">  
                <h1> Hanate Sushi Bar</h1>
                <h3> Facny Bar | </h3> <h4>3:00 PM to 5:30 PM </h4> 
            </div>
            <div class="specials-div">
                <h2> Happy Hour Specials </h2>  
                <p> $5 Drink Specials </p>
                <ul> 
                    <li> Beer </li>
                    <ul> 
                        <li> $2 off all drafts </li> 
                    </ul>
                    <li> Wine </li>
                    <ul> 
                        <li> $5 House Wines </li> 
                    </ul>
                    <li> Cocktails &amp; Sprits </li>
                    <ul> 
                        <li> $1 off all rails </li> 
                        <li> $2 off all cocktails </li>
                        <li> $9 Boiler Maker </li>
                        <li> $1 off all rails </li> 
                        <li> $2 off all cocktails </li>
                        <li> $1 off all rails </li> 
                        <li> $2 off all cocktails </li>
                    </ul>
                </ul>
            </div>
            <div class="reviews-div">
                <div style="overflow:hidden;">
                <h2> Reviews </h2>
                <img src="img/facebook_icon.png" style="display:block;float:right;width:20%; height:20%; padding-bottom:5%"/> 
                </div>
                <ul>
                    <li><img src="img/icon-profile.png" style="vertical-align:middle; padding-right:5%;"/> it's like a Moroccan oasis in the middle of ....</li>
                    <hr class="review-hr">
                    <li> <img src="img/icon-profile.png" style="vertical-align:middle; padding-right:5%;"/> try getting a table by window ... </li>
                    <hr class="review-hr">
                    <li> <img src="img/icon-profile.png" style="vertical-align:middle; padding-right:5%;"/> seared scallops along .. </li> 
                    <hr class="review-hr">
                    <li> <img src="img/icon-profile.png" style="vertical-align:middle; padding-right:5%;"/> seared scallops along .. </li> 
                    <hr class="review-hr">
                </ul>
                <a href="url"> Read more ... </a>
            </div>
        </div> 
    </div>

<script>
   $("input:checkbox").change(function() {
                    var ischecked= $(this).is(':checked');
                    if(!ischecked)
                       hoverEnabled = false;
                }); 


   /*****MapBox*****/
    L.mapbox.accessToken = 'pk.eyJ1Ijoic2FsbWFuYWVlIiwiYSI6ImNpa2ZsdXdweTAwMXl0d20yMWVlY3g4a24ifQ._0c3U-A8Lv6C7Sm3ceeiHw';
    
    var southWest = L.latLng(38.820993,-76.875833),
    northEast = L.latLng(39.004460,-77.158084),
    bounds = L.latLngBounds(southWest, northEast);
    
    var map = L.mapbox.map('map');

    L.mapbox.styleLayer('mapbox://styles/mapbox/dark-v8').addTo(map);

    map.setView([38.907557, -77.009014], 13); 
    map.setMaxBounds(bounds);
    
    
    /*************************/
    L.mapbox.featureLayer('salmanaee.p703d8fb')
    .on('ready', function(e) {
        var clusterGroup = new L.MarkerClusterGroup({polygonOptions: {
            fillColor: 'white',
            color: 'white',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.3
        }
     });//end of cluster
        e.target.eachLayer(function(layer) {
            clusterGroup.addLayer(layer);
      });
      map.addLayer(clusterGroup);
    });//end of function

</script>
</body>
</html>