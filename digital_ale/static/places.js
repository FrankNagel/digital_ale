var url = '/api/place_candidates/';

//id and name of currently shown place
var place_id = null;
var place_name = null;

//UI variables
var map;
var markers;
var button_click_targets = {};
var iconStyleRed = new ol.style.Style({
            image: new ol.style.Icon(/** @type {olx.style.IconOptions} */ ({
                anchor: [0.294, 1], //the point of the marker is off center due to shadow
                anchorXUnits: 'fraction',
                anchorYUnits: 'fraction',
                opacity: 1,
                scale: 0.02,
                src: '/static/img/Map-Marker-Red.svg'
            }))
        });

var iconStyleGreen = new ol.style.Style({
            image: new ol.style.Icon(/** @type {olx.style.IconOptions} */ ({
                anchor: [0.294, 1], //the point of the marker is off center due to shadow
                anchorXUnits: 'fraction',
                anchorYUnits: 'fraction',
                opacity: 1,
                scale: 0.02,
                src: '/static/img/Map-Marker-Green.svg'
            }))
        });

function show_candidates_callback(event) {
    var row = event.target.parentElement;
    var id = row.attributes.dbid.value;
    var clone = row.cloneNode(true);
    var tbody = document.getElementById("body-shown-place");

    //initialize global scope variables
    place_id = id;
    place_name = row.children[2].innerHTML;
    
    $(tbody).empty().append(clone);
    $(".table-shown-place").width($("#table-places").width());
    for (var i=0; i< clone.children.length; i++) {
        $(clone.children[i]).width($(row.children[i]).width());
    }
    ui_update_candidates(id);
    
    var prev = document.getElementById('show-prev');
    $(prev).button('option', 'disabled', row.previousElementSibling === null);
    button_click_targets['show-prev'] = row.previousElementSibling;
    prev.place_to_show = row.previousElementSibling;
    var next = document.getElementById('show-next');
    $(next).button('option', 'disabled', row.nextElementSibling === null);
    button_click_targets['show-next'] = row.nextElementSibling;
    next.place_to_show = row.nextElementSibling;
}

function ui_update_candidates(id) {
    $.ajax(url + id, {
        context: document.body
    }).done(function(msg) {
        if (msg.status != 'OK') {
            alert(msg.status);
            return;
        }        
        var features = [];
        var coordinates = []; //to set Extent
        for (var i=0; i< msg.response.length; i++) {
            var datapoint = msg.response[i];
            var geometry = new ol.geom.Point([datapoint.lng, datapoint.lat]);
            coordinates.push([datapoint.lng, datapoint.lat]);
            geometry.transform('EPSG:4326', 'EPSG:3857');
            var iconFeature = new ol.Feature({
                geometry: geometry,
                lng: datapoint.lng,
                lat: datapoint.lat
           });
            iconFeature.setStyle(iconStyleRed);
            features.push(iconFeature);
        }
        //show currently as correct seen coordinates with a green marker
        if (msg.selected.lng !== null && msg.selected.lat !== null) {
            var geometry = new ol.geom.Point([msg.selected.lng, msg.selected.lat]);
            coordinates.push([msg.selected.lng, msg.selected.lat]);
            geometry.transform('EPSG:4326', 'EPSG:3857');
            var iconFeature = new ol.Feature({
                geometry: geometry,
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
            map.getView().fitGeometry(geom, [1200,800], {maxZoom: 13, padding: [40, 20, 10, 20] });
        }
        $('.cd-panel').removeClass('is-visible');
    }).fail(function(jqXHR, textStatus, errorThrown) {
        alert('The request failed. Reason given: "' + errorThrown + '"' );
    });
    
}

function show_sibling(event) {
    var button = event.currentTarget;
    button.place_to_show.children[0].click();
}

function place_save_changes() {
    var id = parseInt($('#place-id').attr('value'));
    var payload = {
        id: $('#place-id').attr('value'),
        name: $('#place-name').attr('value'),
        lng: parseFloat($('#place-lng').attr('value')),
        lat: parseFloat($('#place-lat').attr('value'))
    };
    $.ajax('/api/place/' + id + '/edit', {
        type: 'POST',
        data: payload,
        context: document.body
    }).done(function(data, textStatus, jqXHR) {
        $('#place-form').dialog( "close" );
        ui_update_candidates(id);
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

    //change mouse cursor when over marker
    $(map.getViewport()).on('mousemove', function(e) {
        var pixel = map.getEventPixel(e.originalEvent);
        var hit = map.forEachFeatureAtPixel(pixel, function(feature, layer) {
            return true;
        });
        if (hit) {
            map.getTarget().style.cursor = 'pointer';
        } else {
            map.getTarget().style.cursor = '';
        }
    });

    //open place edit dialog on click
    map.on('click', function(evt) {
        var coordinates, lnglat, lng, lat;
        var feature = map.forEachFeatureAtPixel(evt.pixel,
                                                function(feature, layer) {
                                                    return feature;
                                                });
        if (feature) {
            var geometry = feature.getGeometry();
            coordinates = geometry.getCoordinates();
        } else {
            coordinates = evt.coordinate;            
        }
        lnglat = ol.proj.transform(coordinates, 'EPSG:3857', 'EPSG:4326');
        lng = lnglat[0];
        lat = lnglat[1];

        //initialize dialog
        $('#place-id').attr('value', place_id);
        $('#place-name').attr('value', place_name);
        $('#place-lng').attr('value', lng);
        $('#place-lat').attr('value', lat);
        $('#place-form').dialog({
            buttons: {
                "Save": place_save_changes,
                Cancel: function() {
                    $('#place-form').dialog( "close" );
                }
            }
        });

        //alert([place_id, place_name, lng, lat]);
    });
    
    $('.places-trigger').on('click', function(event){
	event.preventDefault();
	$('.cd-panel').toggleClass('is-visible');
    });
    $('.cd-panel').on('click', function(event){
	if( $(event.target).is('.cd-panel') || $(event.target).is('.cd-panel-close') ) { 
	    $('.cd-panel').removeClass('is-visible');
	    event.preventDefault();
	}
    });
    $('#show-prev').button({ icons: { primary: "ui-icon-circle-triangle-w"}, text: false }).
        on('click', show_sibling);
    
    $('#show-next').button({ icons: { primary: "ui-icon-circle-triangle-e"}, text: false }).
        on('click', show_sibling);

    $('.place-row > td').on('click', show_candidates_callback);
    $('#table-shown-place').DataTable({
        dom: 't',
        paging: false,
        ordering: false, info: false, searching: false, compact: true});
    $('#table-places').DataTable({paging: false});
    $('#table-places > tbody > tr :first').click();
});
