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
  <script type="text/javascript"
          src="//cdn.datatables.net/plug-ins/380cb78f450/integration/jqueryui/dataTables.jqueryui.js"></script>
  <script src="http://openlayers.org/en/v3.1.1/build/ol.js" type="text/javascript"></script>
  <script type="text/javascript" src="/static/places.js"></script>
</%block>
<div>
<div class="wrapper-shown-place">
  <table id="table-shown-place" class='table-shown-place'>
    <thead style="display: none">
      <tr><th>Old Id</th><th>New Id</th><th>Name</th><th>#Candidates</th></tr>
    </thead>	
    <tbody id="body-shown-place">
      <tr><td>No place selected</td><td></td><td></td><td></td></tr>
    </tbody>
  </table>
  <button id="show-prev">Previous Place of Inquiry</button>
  <button id="show-next">Next Place of Inquiry</button>
</div>

</div>
<div class="places-map-wrapper">
  <div id="map" class="places-map"></div>
  <div class="cd-panel from-left">
    <div class="cd-panel-container">
      <div class="cd-panel-content">
        <table id="table-places" class="display">
          <thead>
            <tr><th>Old Id</th><th>New Id</th><th>Name</th><th>#Candidates</th></tr>
          </thead>
          <tbody>
% for r in places:
            <tr class='place-row' dbid=${r.id}><td>${r.pointcode_old}</td><td>${r.pointcode_new}</td><td>${r.name}</td><td>${r.count}</td></tr>
% endfor
          </tbody>
        </table>
     </div>
    </div>
  </div>
  <div class="places-trigger">Places</div>
</div>

<div id="place-form" title="Modify Place of Inquiry" style='display: none'>
<form>
<fieldset>
<input type="hidden" name="id" id="place-id" value="">

<label for="name">Name</label>
<input type="text" name="name" id="place-name" value="" class="text ui-widget-content ui-corner-all">

<label for="lat">Latitude</label>
<input type="text" name="lat" id="place-lat" value="" class="text ui-widget-content ui-corner-all">

<label for="lng">Longitude</label>
<input type="text" name="lng" id="place-lng" value="" class="text ui-widget-content ui-corner-all">

<!-- Allow form submission with keyboard without duplicating the dialog button -->
<input type="submit" tabindex="-1" style="position:absolute; top:-1000px">
</fieldset>
</form>
</div>
