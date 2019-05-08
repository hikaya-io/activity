    var componentizedLeaflet = function(mapCenter, mapScalingFactor, mapSites){

    var layeredCountries = new L.LayerGroup();
    // Define an icon called cssIcon
    var countryIcon = L.divIcon({
      // Set class name for CSS and marker width/height
      html:'<div class="map-marker"></div>',
      iconSize: [0,0]
    });
    for (site in mapSites){
        L.marker([ site['latitude'], site['longitude']], {icon: countryIcon}).addTo(layeredCountries).bindPopup("");
        // + "<b>{{ site['location_name']}}</b><br>{{ site['site_description']}}<br/> <a href="">{{site['region_name']}}</a><br/>"
    }
    
    var mapCoordinates = mapCenter
    var mapScale = mapScalingFactor
    var mbAttr = 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, ' +
                    '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
                    'Imagery &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, &copy; <a href="http://cartodb.com/attributions">CartoDB</a>',
                    mbUrl = 'http://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png';


    var grayscale   = L.tileLayer(mbUrl, {id: 'mapbox.light', attribution: mbAttr}),
                    streets  = L.tileLayer(mbUrl, {id: 'mapbox.streets',   attribution: mbAttr});
    var map = L.map('map', {
                    center: mapCoordinates,
                    zoom: mapScale,
                    layers: [grayscale, layeredCountries]
                    });

    var baseLayers = { "Grayscale": grayscale,"Streets": streets,};
    var overlays = {"RRIMA Location": layeredCountries, };
    L.control.layers(baseLayers, overlays).addTo(map);

}