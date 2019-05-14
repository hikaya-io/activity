var mappingFunction = function(data, countries, getOverlayGroups, getSiteProfile, getSiteProfileIndicator, country_geojson_url){

    var country=[],country_lat=[],country_long=[], narrativeTitle=[], narrativeTXT=[], overlay=[];

    //read country GPS data into arrays
    {% for item in countries %}
        country[{{forloop.counter}}] = "{{ item.country }}";
        country_lat[{{forloop.counter}}] = "{{ item.latitude }}";
        country_long[{{forloop.counter}}] = "{{ item.longitude }}";
    {% endfor %}

     //overlay groups
     {% for group in getOverlayGroups %}
        var {{ group.overlay_group }} = new L.LayerGroup();
     {% endfor %}

            //define icons for overlay markers
    var projectIcon = L.divIcon({
      className: 'map-marker',
      html:'<div class="map-marker project"></div>',
      iconSize: [50,50]
    });
    var indicatorIcon = L.divIcon({
      className: 'marker-indicator',
      html:'<div class="marker-indicator"></div>',
      iconSize: [50,50]
    });
    var greenIcon = new L.Icon({
        iconUrl: '{{ STATIC_URL }}js/images/marker-icon-green.png',
        iconRetinaUrl: '{{ STATIC_URL }}js/images/marker-icon-2x-green.png',
        iconSize:    [25, 41],
        iconAnchor:  [12, 41],
        popupAnchor: [1, -34],
        shadowUrl: '{{ STATIC_URL }}js/images/marker-shadow.png',
        shadowSize:  [41, 41]
            });
    //partner markers
    {% for item in getSiteProfile %}
        L.marker([{{ item.latitude }}, {{ item.longitude }}], {icon: projectIcon})
            .addTo(partners)
            .bindPopup("<b>{{ item.country }}</b>
                        <br/>Project Site:
                        <br/><a href='/workflow/siteprofile_update/{{ item.id }}'>{{ item.name }}</a>
                        <br/>ADM1: {{ item.province }}
                        <br/>ADM2: {{ item.district }}
                        <br/>ADM3: {{ item.village }}
                        <br/>SiteProfile{{ item.name }}
                        <br/> "
                       );
    {% endfor %}

    {% if getSiteProfileIndicator %}
        //indicator markers
        {% for item in getSiteProfileIndicator %}
            L.marker([{{ item.latitude }}, {{ item.longitude }}], {icon: indicatorIcon})
                    .addTo(indicators)
                    .bindPopup("" + "<b>{{ item.country }}</b>
                                <br/>Collected Indicator Data Site:
                                <br/><a href='/workflow/siteprofile_update/{{ item.id }}'>{{ item.name }}</a>
                                <br/>ADM1: {{ item.province }}
                                <br/>ADM2: {{ item.district }}
                                <br/>ADM3: {{ item.village }}
                                <br/>SiteProfile{{ item.name }}
                                <br/> "
                               );
        {% endfor %}
    {% endif %}

    var mbAttr = 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, ' +
                '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
                'Imagery &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, &copy; <a href="http://cartodb.com/attributions">CartoDB</a>',

    //basemaps from mapbox URL and leaflet-providers.js
    mbUrl = 'http://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png';
    var baseMap = L.tileLayer.provider('OpenStreetMap.Mapnik');

    var baseMap = L.tileLayer.provider('OpenStreetMap.Mapnik'),
        grayscale = L.tileLayer(mbUrl, {id: 'mapbox.light', attribution: mbAttr}),
        opentopomap = L.tileLayer.provider('OpenTopoMap');

    var map = L.map('map',
               {
                center: [country_lat[1], country_long[1]],
                zoom: 5,
                dragging: false,
                touchZoom: false,
                scrollWheelZoom: false,
                //preselected layers
                layers: [baseMap, projects, indicators]
                });

    var baseLayers = {"OpenStreet": baseMap,
                      "GrayScale": grayscale,
                      "Topography": opentopomap,
                      };

    var overlays = { {% for narrative in getOverlayNarrative %}
                        "{{narrative.overlay_title}}": {{narrative.overlay_group.overlay_group}},
                     {% endfor %} };

    L.control.layers(baseLayers, overlays).addTo(map);
    var sidebar = L.control.sidebar('sidebar').addTo(map);

    //AFG country boundary geoJSON
    var AFGLayer = L.geoJson().addTo(map);

    $.getJSON("{{ STATIC_URL }}publicdashboard/js/AFG.geo.json", function(json) {
    AFGLayer.addData(json);
    });

    //invest_khandahar.geoJSON data (from http://earthquake.usgs.gov) - TODO - prepare INVEST-in-Khandahar geoJSON
   function addDataToMap(data, map){
       L.geoJson(data, {
            pointToLayer: function(feature, latlng) {
            return L.marker(latlng, {
              icon: greenIcon
                    });
                },
            onEachFeature: function(feature, layer) {
                var popupText = "Magnitude: " + feature.properties.mag + "<br>Location: " + feature.properties.place + "<br><a href='" + feature.properties.url + "'>More info</a>";
                layer.bindPopup(popupText);
            }
       }).addTo(projects);
    }
    
    $.getJSON("{{ STATIC_URL }}publicdashboard/js/invest_khandahar.geojson", function(data){ addDataToMap(data, map); });

        //narrative placeholders
        {% for text in getOverlayNarrative %}
            narrativeTitle[{{forloop.counter}}] = "{{text.narrative_title}}";
            narrativeTXT[{{forloop.counter}}] = "{{text.narrative}}";
            overlay[{{forloop.counter}}] = "{{text.overlay_title}}";
        {% endfor %}

        var testNarrative = L.control({position: 'bottomleft'}),
            dashNarrative = L.control({position: 'bottomleft'});

        dashNarrative.onAdd = function (map) {
        var div = L.DomUtil.create('div', 'info narrative');
            div.innerHTML +=
            "<strong>"+narrativeTitle[1]+":</strong><br/>" + narrativeTXT[1];
            return div;
            };

        testNarrative.onAdd = function (map) {
        var div = L.DomUtil.create('div', 'info narrative');
            div.innerHTML +=
            "<strong>"+narrativeTitle[2]+":</strong><br/>" + narrativeTXT[2];
            return div;
            };

        dashNarrative.addTo(map);

        map.on('overlayadd', function (eventLayer) {
            if (eventLayer.name === overlay[2]) {
                this.removeControl(dashNarrative);
                testNarrative.addTo(this);
            }
        });
        map.on('overlayremove', function (eventLayer) {
            if (eventLayer.name === overlay[2]) {
                this.removeControl(testNarrative);
                dashNarrative.addTo(this);
            }
        });

        var photoLayer = L.photo.cluster().on('click', function (evt) {
	        var photo = evt.layer.photo,
		        template = '<a><img src="{url}"/></a><p>{caption}</p>';

	        if (photo.video && (!!document.createElement('video').canPlayType('video/mp4; codecs=avc1.42E01E,mp4a.40.2'))) {
		        template = '<video autoplay controls poster="{url}"><source src="{video}" type="video/mp4"/></video>';
	            };

	    evt.layer.bindPopup(L.Util.template(template, photo), {
		    className: 'leaflet-popup-photo',
		    minWidth: 400
	        }).openPopup();
        });

        reqwest({
	        url: 'https://picasaweb.google.com/data/feed/api/user/114670224825998987940/albumid/6277837931786391457?alt=json-in-script',
	        type: 'jsonp',
	        success: function (data) {
		        var photos = [];
		        data = data.feed.entry;
		            for (var i = 0; i < data.length; i++) {
			            var photo = data[i];
			            if (photo['georss$where']) {
				            var pos = photo['georss$where']['gml$Point']['gml$pos']['$t'].split(' ');
				            photos.push({
					                lat: pos[0],
					                lng: pos[1],
					                url: photo['media$group']['media$content'][0].url,
					                caption: photo['media$group']['media$description']['$t'],
					                thumbnail: photo['media$group']['media$thumbnail'][0].url,
					                video: (photo['media$group']['media$content'][1] ? photo['media$group']['media$content'][1].url : null)
				                    });
			            };
		}
		photoLayer.add(photos).addTo(VTC);
		map.fitBounds(photoLayer.getBounds());
	}
	});
 }