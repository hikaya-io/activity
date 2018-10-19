from django import forms
from django.utils.safestring import mark_safe


class GoogleMapsWidget(forms.HiddenInput):
    """
    Widget for Google Maps object to be displayed
    inline in a form
    """

    def render(self, name, value,country=None, attrs=None, choices=()):

        self.attrs['base_latitude'] = self.attrs.get('base_latitude', u'34.5333')
        self.attrs['base_longitude'] = self.attrs.get('base_longitude', u'69.1667')
        self.attrs['width'] = self.attrs.get('width', 700)
        self.attrs['height'] = self.attrs.get('height', 400)
        self.attrs['country'] = self.attrs.get('country', country)


        maps_html = u"""
            <script type="text/javascript" src="https://maps.google.com/maps/api/js?v=3&key=AIzaSyAc76ZfKuHCvwXAEAiR2vINQPgNRenCf_8&sensor=false"></script>
            <script type="text/javascript">

                $(document).ready(function(){
                    // Base lat and long are set to django defaults from above
                    var base_lat = %(base_latitude)s
                    var base_long = %(base_longitude)s

                    // If the lat and long fields have values use those to center the map
                    function initialize() {
                        if($('#id_%(latitude)s').val()!=''){
                            center = new google.maps.LatLng($('#id_%(latitude)s').val(), $('#id_%(longitude)s').val());
                        }else{
                            center = new google.maps.LatLng(%(base_latitude)s,%(base_longitude)s);
                            $('#id_%(latitude)s').val(base_lat);
                            $('#id_%(longitude)s').val(base_long);
                        }
                        var myOptions = {
                            zoom: 15,
                            center: center,
                            mapTypeId: google.maps.MapTypeId.ROADMAP
                        };
                        map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);
                        geocoder = new google.maps.Geocoder();
                        my_point = new google.maps.Marker({
                            position: center,
                            map: map,
                            draggable: true,
                        })

                         // If someone drags the map pointer reset the lat & long in the form
                        google.maps.event.addListener(my_point, 'dragend', function(event){
                            $('#id_%(latitude)s').val(event.latLng.lat());
                            $('#id_%(longitude)s').val(event.latLng.lng());
                        });
                        $('#%(longitude)s').parent().parent().hide();

                        google.maps.event.trigger(map, 'resize');

                    }

                    google.maps.event.addDomListener(window, 'load', initialize);

                    $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
                        console.log("map resize");
                        initialize();

                    })


                });


                // Called from form to geocode address to get lat long for an address (city, country)
                function codeAddress(){
                    google.maps.event.trigger(map, 'resize');
                    var address = $('#city_country').val();
                    geocoder.geocode( { 'address': address}, function(results, status) {
                        if (status == google.maps.GeocoderStatus.OK) {
                            results_len = results.length
                            var results_table = new Array();
                            for(i=0; i<results_len; i++){
                                address_location = results[i].geometry.location
                                if(i==0){
                                    set_center(address_location.lat(), address_location.lng());
                                    $('#id_%(latitude)s').val(address_location.lat());
                                    $('#id_%(longitude)s').val(address_location.lng());
                                }
                                results_table[i] = '<div style="cursor: pointer" onclick="set_center(' +
                                    address_location.lat() + ', ' +
                                    address_location.lng() + ')">' +
                                    results[i].formatted_address +
                                    '</div>';
                            }
                            $('#search_results').html(results_table.join(''));
                        } else {
                            alert("Geocode was not successful for the following reason: " + status);
                        }
                    });
                }

                // Called from codeAddress set the center to the coded address lat and long
                function set_center(lat, lng){
                    google.maps.event.trigger(map, 'resize');
                    latlng = new google.maps.LatLng(lat, lng);
                    my_point.setPosition(latlng)
                    map.setCenter(latlng);
                }


            </script>

            <br stlye="clear: both" />
            <div style="width: 400px; margin-bottom: 25px; margin-left: 100px">
                <div id="search">
                <label for="city_county">City, Country:</label>
                <input id="city_country" type="text" value="%(country)s" class="input-medium search-query"/>
                <input class="btn" type="button" value="Find" onclick="codeAddress()" />
                </div>
                <div id="search_results"><br/>
                </div>

                <div id="map_canvas" style="width: %(width)ipx; height: %(height)ipx;"></div>
            </div>




            """ % {'latitude': self.attrs['latitude'], 'longitude': self.attrs['longitude'], 'base_longitude': self.attrs['base_longitude'],
                   'base_latitude': self.attrs['base_latitude'], 'width': self.attrs['width'], 'height': self.attrs['height'], 'country': self.attrs['country']}

        rendered = super(GoogleMapsWidget, self).render(name, value, attrs)
        return rendered + mark_safe(maps_html)
