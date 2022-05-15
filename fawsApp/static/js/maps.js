(function ($) {
    if ($(".cordinate").length > 0) {
        var building_log = '';
        var building_lat = '';
        var building_data = '';
        var map_cod = '[';
        $(".cordinate").each(function () {
            building_log = $(this).attr('data-long');
            building_lat = $(this).attr('data-lat');
            building_data = $(this).attr('data-img');
            if (building_log != "" && building_lat != "") {
                map_cod = map_cod + '{"type":"Feature", "properties":{"marker-color":"#000", "marker-symbol":"rocket", "description":"' + building_data + '"}, "geometry":{"type": "Point","coordinates": [' + building_log + ', ' + building_lat + ']}},';
            }
        });
        if (building_log != "" && building_lat != "") {
            map_cod = map_cod.substr(0, (map_cod.length - 1))
            map_cod = map_cod + ']';
            map_cod = JSON.parse(map_cod);
            if ($(".map_zoom_leval").length > 0) {
                var zoom = $(".map_zoom_leval").attr('zoom_leval');
            } else {
                var zoom = 11;
            }
            if ($(".building-detail").length > 0) {
                var zoom = 10;
                var log = building_log;
                var lat = building_lat - 0.070;
            } else if ($(".center_cordinate").length > 0) {
                var zoom = zoom;
                var log = building_log;
                var lat = building_lat;
            } else {
                var zoom = zoom;
                var log = building_log;
                var lat = building_lat;
            }
            mapboxgl.accessToken = 'pk.eyJ1Ijoid2V3b3JraW5kaWEiLCJhIjoiY2pnNmV6OHp4N3cwYzMzczJuZGxhNmY2cSJ9.EtcSdXo6G18Cb3IWTHpHlA';
            if (!mapboxgl.supported()) {
                alert('Your browser does not support Mapbox GL');
            } else {
                var map = new mapboxgl.Map({
                    container: 'mapww',
                    style: 'mapbox://styles/mapbox/light-v10',
                    //center: [-19.0760, 72.8777],
                    center: [log, lat],
                    zoom: zoom
                });
                var size = 50;
                var pulsingDot = {
                    width: size,
                    height: size,
                    data: new Uint8Array(size * size * 4),
                    onAdd: function () {
                        var canvas = document.createElement('canvas');
                        canvas.width = this.width;
                        canvas.height = this.height;
                        this.context = canvas.getContext('2d');
                    },
                    render: function () {
                        var duration = 1000;
                        var t = (performance.now() % duration) / duration;
                        var radius = size / 2 * 0.3;
                        var outerRadius = size / 2 * 0.7 * t + radius;
                        var context = this.context;
                        // draw outer circle
                        context.clearRect(0, 0, this.width, this.height);
                        context.beginPath();
                        context.arc(this.width / 2, this.height / 2, outerRadius, 0, Math.PI * 2);
                        context.fillStyle = 'rgba(102, 122, 98,' + (1 - t) + ')';
                        context.fill();
                        // draw inner circle
                        context.beginPath();
                        context.arc(this.width / 2, this.height / 2, radius, 0, Math.PI * 2);
                        context.fillStyle = '#4397bc';
                        context.strokeStyle = 'white';
                        context.lineWidth = 2 + 4 * (1 - t);
                        context.fill();
                        context.stroke();
                        // update this image's data with data from the canvas
                        this.data = context.getImageData(0, 0, this.width, this.height).data;
                        // keep the map repainting
                        map.triggerRepaint();
                        // return `true` to let the map know that the image was updated
                        return true;
                    }
                };
                map.on('load', function () {
                    map.scrollZoom.disable(); // Disable scroll
                    // Display map navigation controls
                    var nav = new mapboxgl.NavigationControl();
                    map.addControl(nav, 'top-left');
                    map.setPaintProperty('water', 'fill-color', '#D6EBFF'); // Change water color
                    map.addImage('pulsing-dot', pulsingDot, {
                        pixelRatio: 2
                    }); // Add blink dot
                    // Add a layer showing the places.
                    map.addLayer({
                        "id": "places",
                        "type": "symbol",
                        "source": {
                            "type": "geojson",
                            "data": {
                                "type": "FeatureCollection",
                                "features": map_cod
                            }
                        },
                        "layout": {
                            "icon-image": "pulsing-dot"
                            //                        "icon-allow-overlap": true
                        }
                    });
                    /* for highlight current building: START */
                    if ($(".building-detail").length > 0) {
                        new mapboxgl.Popup().setLngLat([building_log, building_lat]).setHTML(building_data).addTo(map);
                    }
                    /* for highlight current building: END */
                    // When a click event occurs on a feature in the places layer, open a popup at the
                    // location of the feature, with description HTML from its properties.
                    map.on('click', 'places', function (e) {
                        var coordinates = e.features[0].geometry.coordinates.slice();
                        var description = e.features[0].properties.description;
                        // Ensure that if the map is zoomed out such that multiple
                        // copies of the feature are visible, the popup appears
                        // over the copy being pointed to.
                        while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
                            coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
                        }
                        new mapboxgl.Popup().setLngLat(coordinates).setHTML(description).addTo(map);
                        // Center the map on the coordinates of any clicked symbol from the 'symbols' layer.
                        var lat_log = e.features[0].geometry.coordinates;
                        if ($(".building-detail").length > 0) {
                            lat_log[1] = lat_log[1] - 0.070;
                        }
                        map.flyTo({
                            center: lat_log
                        });
                    });
                    // Change the cursor to a pointer when the mouse is over the places layer.
                    map.on('mouseenter', 'places', function () {
                        map.getCanvas().style.cursor = 'pointer';
                    });
                    // Change it back to a pointer when it leaves.
                    map.on('mouseleave', 'places', function () {
                        map.getCanvas().style.cursor = '';
                    });
                });
            }
        }
    }
})(jQuery);;
