<%page expression_filter="h"/>
<%inherit file='base.mako' />
<%block name="header">
  <link rel="stylesheet"
        href="http://code.jquery.com/ui/1.10.4/themes/smoothness/jquery-ui.css"
        type="text/css">
  <link rel="stylesheet"
        href="//cdn.datatables.net/plug-ins/380cb78f450/integration/jqueryui/dataTables.jqueryui.css"
        type="text/css">
  <link rel="stylesheet" href="http://openlayers.org/en/v3.1.1/css/ol.css" type="text/css">

  <script type="text/javascript" src="http://code.jquery.com/jquery-2.1.1.js"></script>
  <script type="text/javascript" src="http://code.jquery.com/ui/1.10.4/jquery-ui.js"></script>
  <script type="text/javascript" src="//cdn.datatables.net/1.10.3/js/jquery.dataTables.js"></script>
  <script type="text/javascript" src="//cdn.datatables.net/plug-ins/3cfcc339e89/sorting/custom-data-source/dom-checkbox.js"></script>
  <script type="text/javascript"
          src="//cdn.datatables.net/plug-ins/380cb78f450/integration/jqueryui/dataTables.jqueryui.js"></script>
  <script src="http://openlayers.org/en/v3.1.1/build/ol.js" type="text/javascript"></script>
  <script type="text/javascript" src="/static/places_all.js"></script>
</%block>
<div id="map" class="places-all-map">
  <div id='map-popup' title='popup anchor'></div>
</div>

