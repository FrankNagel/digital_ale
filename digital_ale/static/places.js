var url = '/api/place_candidates/';

var current_place = null;

//UI variables
var map;
var markers;
var popup;
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

function place_sync_state(id) {
    $.ajax('/api/place/' + id, {
        type: 'GET',
        context: document.body
    }).done(function(data, textStatus, jqXHR) {
        current_place = data;
        $('tr[dbid=' + id + ']').each(function(index, value) {
            value.childNodes[2].innerHTML = data.name;
            value.childNodes[3].innerHTML = data.candidate_count;
            value.children[4].children[0].checked = (current_place.lat !== null && current_place.lng !== null);
            value.children[5].children[0].checked = current_place.coordinates_validated;
        });
        var checkbox =$('#validate');
        checkbox.prop('checked', data.coordinates_validated);
        checkbox.button('refresh');
        checkbox.button('option', { disabled: (current_place.lat === null && current_place.lng === null) } );
    }).fail(function(jqXHR, textStatus, errorThrown) {
        alert('Access of current Place of Inquiry on the server failed. Reason given: "' + errorThrown + '"' );
        current_place = null;
    });
}

function show_candidates_callback(event) {
    var row = event.target.parentElement;
    var id = row.attributes.dbid.value;
    var clone = row.cloneNode(true);
    var tbody = document.getElementById("body-shown-place");

    $(tbody).empty().append(clone);
    $(".table-shown-place").width($("#table-places").width());
    for (var i=0; i< clone.children.length; i++) {
        $(clone.children[i]).width($(row.children[i]).width());
    }
    place_sync_state(id);
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
        for (var i=0; i< msg.candidates.length; i++) {
            var datapoint = msg.candidates[i];
            var geometry = new ol.geom.Point([datapoint.lng, datapoint.lat]);
            coordinates.push([datapoint.lng, datapoint.lat]);
            geometry.transform('EPSG:4326', 'EPSG:3857');
            var iconFeature = new ol.Feature({
                geometry: geometry,
                name: datapoint.name,
                source: datapoint.source,
                feature_code: datapoint.feature_code,
                lng: datapoint.lng,
                lat: datapoint.lat,
                candidate_id: datapoint.id,
                selected : datapoint.selected
            });
            if (datapoint.selected) {
                iconFeature.setStyle(iconStyleGreen);
            } else {
                iconFeature.setStyle(iconStyleRed);
            }
            features.push(iconFeature);
        }

        markers.setSource(new ol.source.Vector({features: features}));
        if (features.length === 0) {
            map.getView().setCenter(ol.proj.transform([22, 56], 'EPSG:4326', 'EPSG:3857'));
            map.getView().setZoom(4);
        } else {
            var geom = new ol.geom.MultiPoint(coordinates);
            var maxZoom = coordinates.length == 1 ? 11 : 13;
            geom.transform('EPSG:4326', 'EPSG:3857');
            map.getView().fitGeometry(geom, [1200,800], {maxZoom: maxZoom, padding: [40, 20, 10, 20] });
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

function toggle_validated(event) {
    var button = event.currentTarget;
    var id = current_place.id;
    var payload = {
        coordinates_validated: button.checked
    };
    $.ajax('/api/place/' + id + '/edit', {
        type: 'POST',
        data: payload,
        context: document.body
    }).done(function(data, textStatus, jqXHR) {
        place_sync_state(id);
    }).fail(function(jqXHR, textStatus, errorThrown) {
        alert('Failed to save the changed validation status. Reason given: "' + errorThrown + '"' );
        place_sync_state(id);
    });
}

function place_save_from_candidate() {
    var id = parseInt($('#place-id').prop('value'));
    var payload = {
        name: $('#place-name').prop('value'),
        lng: $('#place-lng').prop('value'),
        lat: $('#place-lat').prop('value'),
        remarks: $('#place-remarks').prop('value')
    };
    $.ajax('/api/place/' + id + '/edit', {
        type: 'POST',
        data: payload,
        context: document.body
    }).done(function(data, textStatus, jqXHR) {
        $('#place-form').dialog( "close" );
        place_sync_state(id);
        ui_update_candidates(id);
    }).fail(function(jqXHR, textStatus, errorThrown) {
        place_sync_state(id);
        ui_update_candidates(id);
        alert('The request failed. Reason given: "' + errorThrown + '"' );
    });
}

function place_save_from_map() {
    var id = parseInt($('#place-id').prop('value'));
    var payload = {
        place_id: id,
        name: $('#place-name').prop('value').trim(),
        lng: $('#place-lng').prop('value').trim(),
        lat: $('#place-lat').prop('value').trim()
    };
    if (! (payload.lng.length && payload.lat.length)) {
        //don't create a candidate without coordinates
        //only save name and remark
        place_save_from_candidate();
        return;
    }
    $.ajax('/api/place_candidate/add', {
        type: 'POST',
        data: payload,
        context: document.body
    }).done(function(data, textStatus, jqXHR) {
        place_save_from_candidate();
    }).fail(function(jqXHR, textStatus, errorThrown) {
        ui_update_candidates(id);
        alert('The request failed. Reason given: "' + errorThrown + '"' );
    });    
}

function candidate_delete() {
    var id = parseInt($('#place-id').prop('value'));
    var candidate_id = $('#candidate-id').prop('value');
    $.ajax('/api/place_candidate/' + candidate_id, {
        type: 'DELETE',
        context: document.body
    }).done(function(data, textStatus, jqXHR) {
        $('#place-form').dialog( "close" );
        place_sync_state(id);
        ui_update_candidates(id);
    }).fail(function(jqXHR, textStatus, errorThrown) {
        alert('The request failed. Reason given: "' + errorThrown + '"' );
    });
}

function open_dialog(lat, lng, from_candidate, candidate_id) {
    //initialize dialog
    $('#place-id').prop('value', current_place.id);
    $('#place-name').prop('value', current_place.name);
    $('#place-remarks').prop('value', current_place.remarks);
    $('#candidate-id').prop('value', candidate_id);
    $('#place-lng').prop('value', lng).prop('disabled', from_candidate);
    $('#place-lat').prop('value', lat).prop('disabled', from_candidate);
  
    if (from_candidate){
        var buttons = {};
        if (candidate_id) {
            buttons.Delete = candidate_delete;
        }
        buttons.Save = place_save_from_candidate;
        buttons.Cancel= function() {
            $('#place-form').dialog( "close" );
        };
        $('#place-form').dialog({
            width: 700,
            title: 'Set Place of Inquiry from Candidate',
            buttons: buttons
        });
    } else {
        $('#place-form').dialog({
            width: 700,
            title: 'Set Place of Inquiry',
            buttons: {
                "Save": place_save_from_map,
                Cancel: function() {
                    $('#place-form').dialog( "close" );
                }
            }
        });
    }
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

    //change mouse cursor when over marker, open popup
    $(map.getViewport()).on('mousemove', function(e) {
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
                feature.get('source');
            if (feature.get('feature_code') !== null) {
                content += '<br>' + feature.get('feature_code');
            }
            $(popup_div).tooltip({content: content}).tooltip('open');
        } else {
            map.getTarget().style.cursor = '';
            $(popup_div).tooltip('close');
        }
    });

    $(map.getViewport()).on('mouseleave', function(e) {
        $(popup_div).tooltip('close');
    });

    //open place edit dialog on click
    map.on('click', function(evt) {
        var coordinates, lnglat, lng, lat;
        var candidate_id = null;
        var feature = map.forEachFeatureAtPixel(evt.pixel,
                                                function(feature, layer) {
                                                    return feature;
                                                });
        if (feature) {
            var geometry = feature.getGeometry();
            coordinates = geometry.getCoordinates();
            candidate_id = feature.get('candidate_id');
        } else {
            coordinates = evt.coordinate;
        }
        lnglat = ol.proj.transform(coordinates, 'EPSG:3857', 'EPSG:4326');
        lng = lnglat[0];
        lat = lnglat[1];
        open_dialog(lat, lng, Boolean(feature), candidate_id);
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

    $('#validate').button().on('click', toggle_validated);

    $('.place-row > td').on('click', show_candidates_callback);
    $('#table-shown-place').DataTable({
        dom: 't',
        paging: false,
        ordering: false, info: false, searching: false, compact: true});
    $('#table-places').DataTable({
        paging: false,
        columns: [
            { "orderDataType": "dom-text", type: 'string' },
            { "orderDataType": "dom-text", type: 'string' },
            { "orderDataType": "dom-text", type: 'string' },
            { "orderDataType": "dom-text-numeric" },
            { "orderDataType": "dom-checkbox" },
            { "orderDataType": "dom-checkbox" }
        ]});
    $('#table-places > tbody > tr :first').click();
});
