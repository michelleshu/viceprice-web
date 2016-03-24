		/*****MapBox*****/
  L.mapbox.accessToken = 'pk.eyJ1Ijoic2FsbWFuYWVlIiwiYSI6ImNpa2ZsdXdweTAwMXl0d20yMWVlY3g4a24ifQ._0c3U-A8Lv6C7Sm3ceeiHw';
  var southWest = L.latLng(38.820993, -76.875833), 
      northEast = L.latLng(39.004460, -77.158084), 
      bounds = L.latLngBounds(southWest, northEast);
  
  var map = L.map('map',{
    center: [38.907557, -77.028130],
    minZoom: 13,
    zoom: 13,
    zoomControl: false
    });

  L.mapbox.styleLayer('mapbox://styles/salmanaee/cikoa5qxo00gf9vm0s5cut4aa').addTo(map);
  map.setMaxBounds(bounds);
    
  /*************************/
  var clusterGroup = new L.MarkerClusterGroup({polygonOptions: {
            fillColor: 'white',
            color: 'white',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.3
          }
        });//end of cluster
          
  var myLayer = L.mapbox.featureLayer().addTo(map);

  myLayer.on('layeradd', function(e) {
    var marker = e.layer,
        feature = marker.feature;

    // Create custom popup content
    var popupContent =  '<div class="tooltip"><h1>' + feature.properties.name + '<\/h1>' + '<p>' + feature.properties.phone + '<br \/>' + feature.properties.website + '<\/p> <\/div>';

    marker.bindPopup(popupContent,{
        closeButton: false,
        minWidth: 320
    });
});

//markers data
var geoJsonData;
  $.get("../fetch/", function(data) {
          geoJsonData = data.json;
        });   

    /***DC Neighborhoods***/
        var dcnLayer = L.geoJson(dcn,  {
            style: getStyle,
            onEachFeature: onEachFeature
          }).addTo(map);

        var lastLayer,lastLabel;

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
            //add neighborhood names to each polygon 
            var label = L.marker(labelLocation(layer,feature),{
              icon: L.divIcon({
                className: 'label',
                html: getHTML(feature.id,feature.properties.name),
                iconSize: [100, 35]
                })}).addTo(map);
            
            //neighborhood/polygons related events (onClick, Hover etc.) 
            layer.on({
                  mousemove: mousemove,
                  mouseout: mouseout,
                  click: click
                });

            label.on('mouseover',function(e){
              document.getElementById(layer.feature.id).style.color="rgb(35, 40, 43)";
              layer.setStyle({
                  weight: 3,
                  opacity: 0.5,
                  fillColor:'#c8a45e',
                  fillOpacity: 0.8,
              });});
              
            label.on('mouseout',function(e){
                layer.fireEvent("mouseout");
            });


            label.on('click',function(e){
                layer.fireEvent("click");
             });
          };
             
        function click(e) {
           var css,id,neighborhood;
           css=document.getElementsByClassName("label");
           
        if(lastLayer === undefined){}//do nothign
        else
            {   
                dcnLayer.resetStyle(lastLayer);
                lastLayer.on({mousemove:mousemove, mouseout:mouseout});
                document.getElementById(lastLayer.feature.id).style.color="#c8a45e";
                id=parseInt(lastLayer.feature.id)-1;
                css[id].style.display="block";
            }    
        //Onclick: disable hover effect, remove label
        e.target.off({mousemove:false, mouseout:false});
        e.target.setStyle({fillOpacity: 0});
        id=parseInt(e.target.feature.id)-1;
        css[id].style.display="none";
        
        lastLayer=e.target;
        neighborhood=e.target.feature.properties.name;
        
        //OnClick: zoom into Polygon and show related markers
        map.fitBounds(e.target.getBounds());
        myLayer.setGeoJSON(geoJsonData);
        myLayer.setFilter(function(f) {
            return f.properties["neighborhood"] === neighborhood;
        });
        return false;
        } 

        function mousemove(e) {
          var layer = e.target;
          document.getElementById(layer.feature.id).style.color="rgb(35, 40, 43)";
          
          //Highlight the neighborhood when mouse moves in the polygon 
          layer.setStyle({
                  weight: 3,
                  opacity: 0.5,
                  fillColor:'#c8a45e',
                  fillOpacity: 0.8,
            });

          if (!L.Browser.ie && !L.Browser.opera) {
                layer.bringToFront();
              }
          }

          function mouseout(e) {
            dcnLayer.resetStyle(e.target);
            document.getElementById(e.target.feature.id).style.color="#c8a45e";
          }

          function labelLocation (l,f){
            //had to manually adjust the label location of few polygons
           return f.id == 13 ? L.latLng(38.909684,-77.031951): 
                  f.id == 15 ? L.latLng(38.872020, -77.012171): 
                  f.id == 16 ? L.latLng(38.858346, -76.996716):
                  l.getBounds().getCenter();
          }
        
        //label css (customized to each neighborhood based on the polgon size, location etc)
    function getHTML(e,d) {
    return e == 1 ? "<div class='map_labels' style='font-size:18px;margin-top:30%; '>" + d +"<div class='bar_num_labels' id='01'>( 16 ) <div/></div>" : //north DC
           e == 2  ?"<div class='map_labels' style='font-size:18px;margin-left:30%;'>" + d +"<div class='bar_num_labels' id='02'>( 5 ) <div/></div>" :  //west dc
           e == 3  ? "<div class='map_labels' style='font-size:16px;'>" + d +"<div class='bar_num_labels' id='03'>( 33 ) <div/></div>" :  //Friendship Heights
            e == 4  ? "<div class='map_labels' style='font-size:14px;'>" + d +"<div class='bar_num_labels' id='04'>( 44 ) <div/></div>" :  //Adams Morgan
            e == 5  ?"<div class='map_labels' style='font-size:18px;margin-right:30%;'>" + d +"<div class='bar_num_labels' id='05'>( 24 ) <div/></div>" :  //East dc
            e == 6  ? "<div class='map_labels' style='font-size:16px;'>" + d +"<div class='bar_num_labels' id='06'>( 18 )<div/></div>" :  //shaw
            e == 7  ? "<div class='map_labels' style='font-size:16px;'>" + d +"<div class='bar_num_labels' id='07'>( 38 )<div/></div>" :  //Capitol Hill
            e == 8 ? "<div class='map_labels' style='font-size:16px;margin-top:15%;'>" + d +"<div class='bar_num_labels' id='08'>( 115 )<div/></div>" :  //downtown
            e == 9 ? "<div class='map_labels' style='font-size:14px;'>" + d +"<div class='bar_num_labels' id='09'>( 20 )<div/></div>" :  //Columbia Heights
            e == 10 ? "<div class='map_labels' style='font-size:14px;width:50px;margin-left:30%;margin-top:10%;'>" + d +"<div class='bar_num_labels' id='10'>( 76 )<div/></div>" :  //Dupont Circle
            e == 11 ? "<div class='map_labels' style='font-size:16px;'>" + d +"<div class='bar_num_labels' id='11'>( 40 )<div/></div>" :  //foggy bottom
            e == 12 ? "<div class='map_labels' style='font-size:16px;'>" + d +"<div class='bar_num_labels' id='12'>( 28 )<div/></div>" :  //georgetown
            e == 13 ? "<div class='map_labels' style='font-size:12px;width:50px;margin-top:0;margin-left:30%;'>" + d +"<div class='bar_num_labels' id='13'>( 21 )<div/></div>" :  //Logan Circle
            e == 14 ? "<div class='map_labels' style='font-size:14px;margin-top:10%;'>" + d +"<div class='bar_num_labels' id='14'>( 40 )<div/></div>" :  //u street
            e == 15 ? "<div class='map_labels' style='font-size:14px;margin-rigth:50%;'>" + d +"<div class='bar_num_labels' id='15'>( 10 )<div/></div>" : //Waterfront
            e == 16 ? "<div class='map_labels' style='font-size:18px;text-align:left;'>" + d +"<div class='bar_num_labels' id='16'>( 2 )<div/></div>" : //South east
                    "<div class='map_labels' style='font-size:13px;margin-top:2%;'>" + d +"<div class='bar_num_labels' id='17'>( 27 )<div/></div>"; //h street 
            }
