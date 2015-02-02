var url = '/api/place/all';

//UI variables
var map;
var markers;
var popup;
var previousZoom;

var iconStyleGreen = new ol.style.Style({
            image: new ol.style.Icon(/** @type {olx.style.IconOptions} */ ({
                anchor: [0.5, 0.5], //the point of the marker is off center due to shadow
                anchorXUnits: 'fraction',
                anchorYUnits: 'fraction',
                opacity: 1,
                scale: 0.008,
                src: '/static/img/Round-Marker-Green.svg'
            }))
        });

function ui_show_all_places() {
    $.ajax(url, {
        context: document.body
    }).done(function(msg) {
        if (msg.status != 'OK') {
            alert(msg.status);
            return;
        }        
        var features = [];
        var coordinates = []; //to set Extent

        for (var i=0; i< msg.places.length; i++) {
            var datapoint = msg.places[i];
            var geometry = new ol.geom.Point([datapoint.lng, datapoint.lat]);
            coordinates.push([datapoint.lng, datapoint.lat]);
            geometry.transform('EPSG:4326', 'EPSG:3857');
            var iconFeature = new ol.Feature({
                geometry: geometry,
                name: datapoint.name,
                pointcode_old: datapoint.pointcode_old,
                pointcode_new: datapoint.pointcode_new,
                lng: datapoint.lng,
                lat: datapoint.lat,
            });
            iconFeature.setStyle(iconStyleGreen);
            features.push(iconFeature);
        }

        markers.setSource(new ol.source.Vector({features: features}));
        if (features.length === 0) {
            map.getView().setCenter(ol.proj.transform([22, 56], 'EPSG:4326', 'EPSG:3857'));
            map.getView().setZoom(4);
        } else {
            var geom = new ol.geom.MultiPoint(coordinates);
            geom.transform('EPSG:4326', 'EPSG:3857');
            map.getView().fitGeometry(geom, [1200,800], {padding: [40, 20, 10, 20] });
        }
    }).fail(function(jqXHR, textStatus, errorThrown) {
        alert('The request failed. Reason given: "' + errorThrown + '"' );
    });
    
}

$(document).ready(function(){
    markers = new ol.layer.Vector();
    map = new ol.Map({
        target: document.getElementById('map'),
        layers: [
            new ol.layer.Tile({
                source: new ol.source.MapQuest({layer: 'osm'})
            }),
            markers
        ],
        view: new ol.View({
          center: ol.proj.transform([22, 56], 'EPSG:4326', 'EPSG:3857'),
          zoom: 4
        }),
        controls: ol.control.defaults().extend([
            new ol.control.ScaleLine()
        ]),
      });
    
    var popup_div = document.getElementById('map-popup');
    $(popup_div).tooltip({
        placement: 'top',
        html: true,
        trigger: 'manual',
        animation: false
    });
    popup = new ol.Overlay({
        element: popup_div,
        positioning: 'bottom-center',
        stopEvent: false
    });
    map.addOverlay(popup);

    ui_show_all_places();

    map.getView().on('change:resolution', function(event) {
        var zoom = map.getView().getZoom();
        if (zoom !== previousZoom) {
            previousZoom = zoom;
            console.log(zoom);
            var scale;
            if (zoom < 6) {
                scale = 0.008;
            } else if (zoom == 6) {
                scale = 0.011;
            } else {
                scale = 0.015;
            }

            var iconStyleGreen = new ol.style.Style({
                image: new ol.style.Icon(/** @type {olx.style.IconOptions} */ ({
                    anchor: [0.5, 0.5], //the point of the marker is off center due to shadow
                    anchorXUnits: 'fraction',
                    anchorYUnits: 'fraction',
                    opacity: 1,
                    scale: scale,
                    src: '/static/img/Round-Marker-Red.svg'
                }))
            });

            markers.getSource().forEachFeature( function(feature) {
                feature.setStyle(iconStyleGreen);
            });
        }
    });

    //change mouse cursor when over marker, open popup
    $(map.getViewport()).on('mousemove', function(e) {
        if (e.buttons ) return;
        var pixel = map.getEventPixel(e.originalEvent);
        var feature = map.forEachFeatureAtPixel(pixel, function(feature, layer) {
            return feature;
        });
        if (feature) {
            map.getTarget().style.cursor = 'pointer';
            var geometry = feature.getGeometry();
            var coord = geometry.getCoordinates();
            popup.setPosition(coord);
            content = feature.get('name') + '<br>' + 
                feature.get('pointcode_old') + '<br>' + 
                feature.get('pointcode_new');
            $(popup_div).tooltip({content: content}).tooltip('open');
        } else {
            map.getTarget().style.cursor = '';
            $(popup_div).tooltip('close');
        }
    });

    $(map.getViewport()).on('mouseleave', function(e) {
        $(popup_div).tooltip('close');
    });

});
